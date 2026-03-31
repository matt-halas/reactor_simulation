from settings import GUI_SCALE, NEUTRON_SOURCE_ENERGY

import numpy as np
from neutron import Neutron


class NeutronSource:
    # A neutron source that will release neutrons from a given position at a given velocity
    # Direction of neutron release is random, intensity is likelihood of release every step
    def __init__(self, x_pos, y_pos, vel, intensity):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.vel = vel
        self.intensity = intensity
        self.emit_active = False

    def decide_emit(self, neutrons):
        if self.emit_active:
            if self.intensity > np.random.random():
                self.emit(neutrons)

    def emit(self, neutrons):
        theta = np.random.random() * 2 * np.pi
        neutrons.append(Neutron(self.x_pos, self.y_pos, NEUTRON_SOURCE_ENERGY, theta))

    def draw(self, canvas):
        size = 10
        canvas.create_oval(
            self.x_pos * GUI_SCALE - size / 2,
            self.y_pos * GUI_SCALE - size / 2,
            self.x_pos * GUI_SCALE + size / 2,
            self.y_pos * GUI_SCALE + size / 2,
            fill="red",
        )
