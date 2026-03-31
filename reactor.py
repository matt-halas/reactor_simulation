import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from cell import Cell
from neutronsource import NeutronSource
from neutron import Neutron

from settings import *


class Reactor:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(
            root,
            width=N_X * CELL_SIZE * GUI_SCALE,
            height=N_Y * CELL_SIZE * GUI_SCALE,
        )
        self.canvas.pack()
        self.cells = generate_cells(N_X, N_Y, CELL_SIZE)
        self.neutrons = []
        self.neutron_count = len(self.neutrons)
        self.neutron_count_text = tk.Label(
            root, text="Neutron count: " + str(self.neutron_count)
        )
        self.neutron_count_text.pack()
        self.average_neutron_energy = self.calculate_average_energy()
        self.average_neutron_energy_text = tk.Label(
            root, text="Neutron count: " + str(self.average_neutron_energy)
        )
        self.average_neutron_energy_text.pack()
        self.time_elapsed = 0
        self.time_elapsed_text = tk.Label(
            root, text="Time elapsed: " + str(self.time_elapsed)
        )
        # Position of source in cm
        self.neutron_source = NeutronSource(
            0.2 * N_X * CELL_SIZE, 0.2 * N_Y * CELL_SIZE, 1, 0.1
        )
        self.is_running = False
        run_button = tk.Button(root, text="Run", command=self.run_reactor)
        run_button.pack()
        pause_button = tk.Button(root, text="Pause", command=self.pause_reactor)
        pause_button.pack()
        reset_button = tk.Button(root, text="Reset", command=self.reset_reactor)
        reset_button.pack()
        toggle_source_button = tk.Button(
            root, text="Toggle neutron source", command=self.toggle_source
        )
        toggle_source_button.pack()
        emit_neutron_button = tk.Button(
            root, text="Emit neutron", command=self.emit_neutron
        )
        emit_neutron_button.pack()

        self.plot_frame = tk.Frame(root)
        self.plot_frame.pack(fill=tk.BOTH, expand=True)

        self.fig = Figure(figsize=(5, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.figcanvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.figcanvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.x_data, self.y_data = [], []
        self.update_plot()  # Start live updates

        self.draw_reactor()
        self.update_reactor()

    def update_plot(self):

        self.x_data.append(self.time_elapsed)
        self.y_data.append(self.neutron_count)

        self.ax.clear()
        self.ax.plot(self.x_data, self.y_data, color="steelblue")
        self.figcanvas.draw_idle()

        self.root.after(100, self.update_plot)  # Runs alongside your existing loop

    def draw_reactor(self):
        self.canvas.delete("all")
        for cell in self.cells:
            cell.draw(self.canvas)
        for neutron in self.neutrons:
            neutron.draw(self.canvas)
        self.neutron_source.draw(self.canvas)
        self.root.update()

    def step_reactor(self):
        self.step_neutrons()
        self.neutron_source.decide_emit(self.neutrons)
        self.neutron_count = len(self.neutrons)
        self.neutron_count_text.config(text="Neutron count: " + str(self.neutron_count))
        self.average_neutron_energy = self.calculate_average_energy()
        self.average_neutron_energy_text.config(
            text="Neutron energy: " + str(self.average_neutron_energy)
        )
        self.time_elapsed += TIME_STEP
        self.time_elapsed_text.config = tk.Label(
            text="Time elapsed: " + str(self.time_elapsed)
        )

    def step_neutrons(self):
        # Steps all neutrons forward. Tracks which neutrons undergo fission and absorption, handles the adding of new prompt neutrons and removal of the fissioned and absorbed neutrons
        fissions = []
        # Track neutrons that fission or are absorbed
        neutrons_to_remove = []
        for i in range(len(self.neutrons) - 1, -1, -1):
            neutron = self.neutrons[i]
            neutron.step(self.cells)
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
                self.neutrons.append(
                    Neutron(
                        x_pos=fission[0],
                        y_pos=fission[1],
                        energy=10,
                        theta=np.random.random() * 2 * np.pi,
                    )
                )
        for i in reversed(neutrons_to_remove):
            self.neutrons.pop(i)

    def update_reactor(self):
        # Function to step all reactor elements, then draw the updated elements onto the canvas
        while self.is_running:
            self.step_reactor()
            self.draw_reactor()

    def pause_reactor(self):
        self.is_running = False

    def run_reactor(self):
        self.is_running = True
        self.update_reactor()

    def reset_reactor(self):
        for neutron in self.neutrons:
            del neutron
        self.neutrons = []
        self.update_reactor()

    def toggle_source(self):
        if not self.neutron_source.emit_active:
            self.neutron_source.emit_active = True
        elif self.neutron_source.emit_active:
            self.neutron_source.emit_active = False

    def emit_neutron(self):
        self.neutron_source.emit(self.neutrons)

    def calculate_average_energy(self):
        total_energy = 0
        for neutron in self.neutrons:
            total_energy += neutron.energy
        if len(self.neutrons) != 0:
            return total_energy / len(self.neutrons)
        else:
            return 0


def generate_cells(N_X, N_Y, CELL_SIZE):
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
            if i > 2 and j > 2 and i < 7 and j < 7:
                cell_type = "Fuel"
            else:
                cell_type = "Moderator"
            cells.append(Cell(nodes, cell_type))
    return cells


if __name__ == "__main__":
    # Run the window
    root = tk.Tk()
    reactor = Reactor(root)
    root.mainloop()
