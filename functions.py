import numpy as np

from cell import Cell
from neutron import Neutron
from neutronsource import NeutronSource
from settings import (
    CELL_SIZE,
    DEFAULT_FUEL_ENRICHMENT,
    FUEL_ROD_PITCH,
    FUEL_ROD_SIZE,
    GUI_SCALE,
    N_FUEL_RODS,
    N_X,
    N_Y,
    NEUTRONS_PER_FISSION,
)


def step_neutrons(reactor, neutrons, cells, time_step, fuel_cs, fuel_alpha):
    # Steps all neutrons forward. Tracks which neutrons undergo fission and absorption, handles the adding of new prompt neutrons and removal of the fissioned and absorbed neutrons
    fissions = []
    # Track neutrons that fission or are absorbed
    neutrons_to_remove = []
    for i in range(len(neutrons)):
        neutron = neutrons[i]
        neutron.step(cells, time_step, fuel_cs, fuel_alpha, reactor.reactor_size)
        if neutron.fission:
            x_loc = neutron.x_pos
            y_loc = neutron.y_pos
            fissions.append([x_loc, y_loc])
        if neutron.absorb or neutron.fission:
            neutrons_to_remove.append(i)
    for fission in fissions:
        if (NEUTRONS_PER_FISSION % 1) > np.random.random():
            neutrons_to_add = np.ceil(NEUTRONS_PER_FISSION)
        else:
            neutrons_to_add = np.floor(NEUTRONS_PER_FISSION)
        for i in range(int(neutrons_to_add)):
            neutrons.append(
                Neutron(
                    x_pos=fission[0],
                    y_pos=fission[1],
                    energy=10,
                    theta=np.random.random() * 2 * np.pi,
                )
            )
    for i in reversed(neutrons_to_remove):
        if not i >= len(neutrons):
            neutrons.pop(i)

    return neutrons


def draw_cells(reactor):
    # draws the rod(s) and moderator onto the canvas
    reactor.canvas.delete("all")
    reactor.canvas.create_rectangle(
        0,
        0,
        reactor.reactor_size * GUI_SCALE,
        reactor.reactor_size * GUI_SCALE,
        fill="blue",
        outline="",
    )  # creates the background, i.e. the moderator
    rod_spacing = FUEL_ROD_PITCH - FUEL_ROD_SIZE
    for i in range(N_FUEL_RODS):
        for j in range(N_FUEL_RODS):
            if [
                i,
                j,
            ] in reactor.control_rod_locations and reactor.control_rods_inserted:
                color = "grey"
            else:
                color = "yellow"
            reactor.canvas.create_rectangle(
                (rod_spacing + (i * FUEL_ROD_PITCH)) * GUI_SCALE * CELL_SIZE,
                (rod_spacing + (j * FUEL_ROD_PITCH)) * GUI_SCALE * CELL_SIZE,
                (rod_spacing + FUEL_ROD_SIZE + (i * FUEL_ROD_PITCH))
                * GUI_SCALE
                * CELL_SIZE,
                (rod_spacing + FUEL_ROD_SIZE + (j * FUEL_ROD_PITCH))
                * GUI_SCALE
                * CELL_SIZE,
                fill=color,
                outline="",
            )


def initialize_reactor_components(reactor):
    reactor.cells = generate_fuel_rod_bundle(
        N_FUEL_RODS, FUEL_ROD_SIZE, FUEL_ROD_PITCH, CELL_SIZE
    )
    reactor.step_number = 0
    reactor.neutrons = []
    reactor.neutron_count = 0
    reactor.average_neutron_energy = calculate_average_energy(reactor.neutrons)
    reactor.time_elapsed = 0
    reactor.enrichment = DEFAULT_FUEL_ENRICHMENT / 100
    # Position of source in cm
    reactor.neutron_source = NeutronSource(
        0.2 * N_X * CELL_SIZE, 0.2 * N_Y * CELL_SIZE, 1, 1
    )
    reactor.is_running = False
    reactor.control_rods_inserted = False
    reactor.control_rod_locations = []
    for i in range(0, N_FUEL_RODS, 2):
        for j in range(0, N_FUEL_RODS, 2):
            reactor.control_rod_locations.append([i, j])


def generate_single_fuel_rod(N_X, N_Y, CELL_SIZE):
    # generate instances of the cell class
    cells = []
    # starting from 0, to N_X-1, initialize cells by defining their corners (nodes)
    for i in range(N_X):
        for j in range(N_Y):
            nodes = [
                [i * CELL_SIZE, j * CELL_SIZE],
                [(i + 1) * CELL_SIZE, j * CELL_SIZE],
                [i * CELL_SIZE, (j + 1) * CELL_SIZE],
                [(i + 1) * CELL_SIZE, (j + 1) * CELL_SIZE],
            ]
            if i > 1 and j > 1 and i < 8 and j < 8:
                cell_type = "Fuel"
            else:
                cell_type = "Moderator"
            cells.append(Cell(nodes, cell_type))
    return cells


def generate_fuel_rod_bundle(n_rods, rod_size, pitch, CELL_SIZE):
    # Generates cells, one mm in size.
    cells = []
    spacing = pitch - rod_size
    for i in range(n_rods * pitch + spacing):
        for j in range(n_rods * pitch + spacing):
            nodes = [
                [i * CELL_SIZE, j * CELL_SIZE],
                [(i + 1) * CELL_SIZE, j * CELL_SIZE],
                [i * CELL_SIZE, (j + 1) * CELL_SIZE],
                [(i + 1) * CELL_SIZE, (j + 1) * CELL_SIZE],
            ]
            if i % pitch < spacing or j % pitch < spacing:
                cell_type = "Moderator"
            else:
                cell_type = "Fuel"
            cells.append(Cell(nodes, cell_type))
    return cells


def generate_control_rods(
    n_rods, rod_size, pitch, CELL_SIZE, control_rod_locations, cells
):
    """Generates the physical representation of control rods to be used by sim when calculating neutron interactions. Changes cell types to control rods based on an input of control rod locations.
    control rod location is the coordinate of the fuel rod to be replaced by a control rod, i.e. for an 8x8 fuel rod bundle, 0,0 is the top left"""
    spacing = pitch - rod_size
    reactor_size = (len(cells)) ** (1 / 2)  # Gets width of reactor in number of cells
    for location in control_rod_locations:
        x, y = location
        # Capture the physical location (mmX mmY) of the control rod
        for i in range(spacing + pitch * x, spacing + pitch * x + rod_size):
            for j in range(spacing + pitch * y, spacing + pitch * y + rod_size):
                # CELLS IS 1D ARRAY NEED TO CALCULATE CELL LOCATION
                cells[int(i * reactor_size + j)].cell_type = "ControlRod"
                cells[int(i * reactor_size + j)].color = "grey"
    return cells


def calculate_average_energy(neutrons):
    total_energy = 0
    for neutron in neutrons:
        total_energy += neutron.energy
    if len(neutrons) != 0:
        return total_energy / len(neutrons)
    else:
        return 0


def calculate_fuel_params(enrichment):
    """ACTUALLY CALCULATES CROSS SECTION AND ALPHA (ABSORPTION RATIO)"""
    # microscopic absorption cross sections for uranium
    u235_mic_abs_cs = 684e-24
    u238_mic_abs_cs = 2.7e-24
    # fission to absorption ratio for u235
    u235_alpha = 0.8556
    # density of uo2 fuel is 10.97 g/cm^3, molar mass of 270.03 g/mol
    # 6.022e23 atoms per mol, 2.446e22 atoms/cm^3
    n_fuel = 2.446e22
    u235_mac_abs_cs = u235_mic_abs_cs * n_fuel * enrichment
    u238_mac_abs_cs = u238_mic_abs_cs * n_fuel * (1 - enrichment)
    fuel_mac_abs_cs = u235_mac_abs_cs + u238_mac_abs_cs
    # fission to absorption ratio for natural uranium
    fuel_alpha = (u235_alpha * u235_mac_abs_cs) / (u235_mac_abs_cs + u238_mac_abs_cs)
    return fuel_mac_abs_cs, fuel_alpha
