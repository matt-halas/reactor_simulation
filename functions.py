from cell import Cell


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


def draw_fuel_rod_bundle(canvas, n_rods, rod_size, pitch, CELL_SIZE):
    spacing = pitch - rod_size
    reactor_size = n_rods * pitch + spacing
    canvas.create_rectangle(0, 0, reactor_size, reactor_size)


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
