import tkinter as tk
import numpy as np

from functions import (
    # generate_single_fuel_rod,
    calculate_average_energy,
    calculate_fuel_params,
    generate_fuel_rod_bundle,
    initialize_reactor_components,
    draw_cells,
    draw_cells_cellwise,
    step_neutrons,
    generate_control_rods,
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

        # create the cells, neutrons, and reactor stats/parameters. Required for width and height of canvas
        initialize_reactor_components(self)

        self.reactor_size = np.sqrt(len(self.cells)) * CELL_SIZE
        self.canvas = tk.Canvas(
            root,
            width=self.reactor_size * GUI_SCALE,
            height=self.reactor_size * GUI_SCALE,
        )

        initialize_controls(self, root)
        initialize_graphs(self)
        self.update_graphs_loop()
        pack_widgets(self)
        draw_cells(self)

        self.draw_reactor()
        self.update_reactor()

    def update_graphs_loop(self):
        """Updates time, neutron count, and neutron energy data, then updates the graphs accordingly"""
        update_graphs(self)
        self.root.after(100, self.update_graphs_loop)

    def draw_reactor(self):
        self.canvas.delete("neutron")
        for neutron in self.neutrons:
            neutron.draw(self.canvas)
        self.root.update()

    def step_reactor(self):
        self.fuel_mac_abs_cs, self.fuel_alpha = calculate_fuel_params(self.enrichment)
        self.neutrons = step_neutrons(
            self,
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
        self.cells = generate_fuel_rod_bundle(
            N_FUEL_RODS, FUEL_ROD_SIZE, FUEL_ROD_PITCH, CELL_SIZE
        )
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
        if self.control_rods_inserted:
            self.control_rods_inserted = False
            self.cells = generate_fuel_rod_bundle(
                N_FUEL_RODS, FUEL_ROD_SIZE, FUEL_ROD_PITCH, CELL_SIZE
            )
            draw_cells(self)
            self.draw_reactor()
        elif not self.control_rods_inserted:
            self.control_rods_inserted = True
            self.cells = generate_control_rods(
                N_FUEL_RODS,
                FUEL_ROD_SIZE,
                FUEL_ROD_PITCH,
                CELL_SIZE,
                [[0, 0]],
                self.cells,
            )
            draw_cells_cellwise(self)
            self.draw_reactor()


if __name__ == "__main__":
    # Run the window
    root = tk.Tk()
    reactor = Reactor(root)
    root.mainloop()
