import tkinter as tk

from cell import Cell
from neutronsource import NeutronSource

from settings import *


class Reactor:
    def __init__(self, parent):
        self.parent = parent
        self.canvas = tk.Canvas(
            parent,
            width=N_X * CELL_SIZE * GUI_SCALE,
            height=N_Y * CELL_SIZE * GUI_SCALE,
        )
        self.canvas.pack()
        self.cells = generate_cells(N_X, N_Y, CELL_SIZE)
        self.neutrons = []
        self.neutron_count = len(self.neutrons)
        self.neutron_count_text = tk.Label(
            parent, text="Neutron count:" + str(self.neutron_count)
        )
        self.neutron_count_text.pack()
        # Position of source in cm
        self.neutron_source = NeutronSource(2, 2, 1, 0.1)
        self.is_running = False
        run_button = tk.Button(parent, text="Run", command=self.run_reactor)
        run_button.pack()
        pause_button = tk.Button(parent, text="Pause", command=self.pause_reactor)
        pause_button.pack()
        reset_button = tk.Button(parent, text="Reset", command=self.reset_reactor)
        reset_button.pack()
        toggle_source_button = tk.Button(
            parent, text="Toggle neutron source", command=self.toggle_source
        )
        toggle_source_button.pack()
        emit_neutron_button = tk.Button(
            parent, text="Emit neutron", command=self.emit_neutron
        )
        emit_neutron_button.pack()
        self.draw_reactor()
        self.update_reactor()

    def draw_reactor(self):
        self.canvas.delete("all")
        for cell in self.cells:
            cell.draw(self.canvas)
        for neutron in self.neutrons:
            neutron.draw(self.canvas)
        self.neutron_source.draw(self.canvas)
        self.parent.update()

    def step_reactor(self):
        for i in range(len(self.neutrons) - 1, -1, -1):
            neutron = self.neutrons[i]
            neutron.step(self.cells)
            if neutron.collision:
                """if np.random.random() < 0.25:
                    self.neutrons.pop(i)"""
                pass
        self.neutron_source.decide_emit(self.neutrons)
        self.neutron_count = len(self.neutrons)
        self.neutron_count_text.config(text="Neutron count: " + str(self.neutron_count))

    def update_reactor(self):
        # Function to step all reactor elements, then draw the updated elements onto the canvas
        self.step_reactor()
        self.draw_reactor()
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
                cell_type = "Air"
            cells.append(Cell(nodes, cell_type))
    return cells


if __name__ == "__main__":
    # Run the window
    root = tk.Tk()
    reactor = Reactor(root)
    root.mainloop()
