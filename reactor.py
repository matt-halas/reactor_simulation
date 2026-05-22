import tkinter as tk
import numpy as np

from functions import (
    # generate_single_fuel_rod,
    calculate_average_energy,
    calculate_fuel_params,
    generate_fuel_rod_bundle,
)
from reactorAux import (
    initialize_controls,
    initialize_graphs,
    update_graphs,
    pack_widgets,
)

from neutronsource import NeutronSource
from neutron import Neutron

from settings import *


class Reactor:
    def __init__(self, root):
        self.root = root
        root.bind("<Key>", self.handle_keypress)
        self.plot_frame = tk.Frame(root)
        # self.canvas = tk.Canvas(root)
        # width=N_X * CELL_SIZE * GUI_SCALE,
        # height=N_Y * CELL_SIZE * GUI_SCALE,
        # self.cells = generate_single_fuel_rod(N_X, N_Y, CELL_SIZE)
        self.cells = generate_fuel_rod_bundle(8, 9, 12, CELL_SIZE)
        self.reactor_size = np.sqrt(len(self.cells)) * CELL_SIZE
        self.step_number = 0
        self.canvas = tk.Canvas(
            root,
            width=self.reactor_size * GUI_SCALE,
            height=self.reactor_size * GUI_SCALE,
        )
        self.neutrons = []
        self.neutron_count = len(self.neutrons)
        self.average_neutron_energy = calculate_average_energy(self.neutrons)
        self.time_elapsed = 0
        self.enrichment = DEFAULT_FUEL_ENRICHMENT / 100
        # Position of source in cm
        self.neutron_source = NeutronSource(
            0.2 * N_X * CELL_SIZE, 0.2 * N_Y * CELL_SIZE, 1, 1
        )
        self.is_running = False

        initialize_controls(self, root)
        initialize_graphs(self)
        self.update_graphs_loop()
        pack_widgets(self)
        self.initial_draw()

        self.draw_reactor()
        self.update_reactor()

    def update_graphs_loop(self):
        """Updates time, neutron count, and neutron energy data, then updates the graphs accordingly"""
        update_graphs(self)
        self.root.after(100, self.update_graphs_loop)

    def initial_draw(self):
        self.canvas.delete("all")
        for cell in self.cells:
            cell.draw(self.canvas)

    def draw_reactor(self):
        self.canvas.delete("neutron")
        self.canvas.delete("source")
        for neutron in self.neutrons:
            neutron.draw(self.canvas)
        self.neutron_source.draw(self.canvas)
        self.root.update()

    def step_reactor(self):
        self.fuel_mac_abs_cs, self.fuel_alpha = calculate_fuel_params(self.enrichment)
        self.neutrons = self.step_neutrons(
            self.neutrons,
            self.cells,
            self.time_step,
            self.fuel_mac_abs_cs,
            self.fuel_alpha,
        )
        self.neutron_source.decide_emit(self.neutrons)
        self.neutron_count = len(self.neutrons)
        self.average_neutron_energy = calculate_average_energy(self.neutrons)
        self.time_elapsed += self.time_step
        self.step_number += 1

    def update_reactor(self):
        # Function to step all reactor elements, then draw the updated elements onto the canvas
        while self.is_running:
            self.step_reactor()
            self.draw_reactor()

    def step_neutrons(self, neutrons, cells, time_step, fuel_cs, fuel_alpha):
        # Steps all neutrons forward. Tracks which neutrons undergo fission and absorption, handles the adding of new prompt neutrons and removal of the fissioned and absorbed neutrons
        fissions = []
        # Track neutrons that fission or are absorbed
        neutrons_to_remove = []
        for i in range(len(neutrons)):
            neutron = neutrons[i]
            neutron.step(cells, time_step, fuel_cs, fuel_alpha, self.reactor_size)
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

    def change_enrichment(self):
        self.enrichment = (
            self.enrichment_entry_var.get() / 100
        )  # converts the percent enrichment to decimal fraction

    def on_slider_move(self, event=None):
        # gets the slider value, performs transform, and updates the time step and display
        self.time_step = 1e-10 * 10 ** (self.time_step_slider.get() / 33)
        self.time_step_display_label.config(text=f"dt: {self.time_step:.2e}")

    def pause_reactor(self):
        self.is_running = False

    def run_reactor(self):
        self.is_running = True
        self.update_reactor()

    def reset_reactor(self):
        for neutron in self.neutrons:
            del neutron
        self.neutrons = []
        self.time_data, self.neutron_count_data, self.neutron_energy_data = [], [], []
        self.time_elapsed = 0
        self.step_reactor()
        self.draw_reactor()

    def toggle_source(self):
        if not self.neutron_source.emit_active:
            self.neutron_source.emit_active = True
        elif self.neutron_source.emit_active:
            self.neutron_source.emit_active = False

    def emit_neutron(self):
        self.neutron_source.emit(self.neutrons)

    def handle_keypress(self, event):
        if event.keysym:
            # Close the window if the esc key is pressed
            if event.keysym == "Escape":
                self.reset_reactor()
                root.destroy()

    def toggle_controlrod(self):
        print("toggled!")


if __name__ == "__main__":
    # Run the window
    root = tk.Tk()
    reactor = Reactor(root)
    root.mainloop()
