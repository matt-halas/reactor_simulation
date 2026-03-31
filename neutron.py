from settings import *
import numpy as np


class Neutron:
    def __init__(self, x_pos, y_pos, energy, theta):
        self.x_pos = x_pos
        self.y_pos = y_pos
        # Energy of neutron
        self.energy = energy
        self.theta = theta
        # Calculates absolute speed of the neutron in m/s
        abs_speed = np.sqrt(2 * self.energy * 1.6e-19 / 1.66e-27)
        # Converting m/s to cm/s
        self.x_vel = np.cos(theta) * abs_speed
        self.y_vel = np.sin(theta) * abs_speed
        self.collision = False
        self.size = 5
        self.color = "black"
        self.fission = False
        self.absorb = False

    def step(self, cells):
        self.energy = 1 / 2 * 1.66e-27 * (self.x_vel**2 + self.y_vel**2) / 1.6e-19
        dx = self.x_vel * TIME_STEP
        dy = self.y_vel * TIME_STEP
        if dx > N_X * CELL_SIZE or dy > N_Y * CELL_SIZE:
            print("too fast!")
        # Wall collisions changed to periodicity instead of a reflection
        if self.x_pos + dx > N_X * CELL_SIZE or self.x_pos + dx < 0:
            self.x_pos = (self.x_pos + dx) % (N_X * CELL_SIZE)
        else:
            self.x_pos += dx

        if self.y_pos + dy > N_Y * CELL_SIZE or self.y_pos + dy < 0:
            self.y_pos = (self.y_pos + dy) % (N_Y * CELL_SIZE)
        else:
            self.y_pos += dy

        # Determine the medium of the neutron (fuel or moderator)
        self.find_medium(cells)
        # If the medium is moderator, determine the likelihood of a collision in a path that the neutron is travelling
        # Determine the step path length in cm (m/s*100*dt)
        step_path_length = np.sqrt((self.x_vel**2 + self.y_vel**2)) * 100 * TIME_STEP
        if self.medium == "Moderator":
            # Probability formula on page 59 - neutron makes it to x WITHOUT a collision
            collision_probability = 1 - np.exp(-CROSS_SECTION * step_path_length)
            if collision_probability > np.random.random():
                self.moderator_collision()
        elif self.medium == "Fuel":
            cross_section = CROSS_SECTION * np.sqrt(0.0253 / self.energy)
            collision_probability = 1 - np.exp(-cross_section * step_path_length)
            if collision_probability > np.random.random():
                self.fuel_collision()

    def moderator_collision(self):
        # phi is collision angle
        phi = (np.random.random() - 0.5) * np.pi
        theta = np.atan2(self.y_vel, self.x_vel)
        vel = np.sqrt(self.x_vel**2 + self.y_vel**2)
        self.x_vel = vel * np.cos(theta - phi) * (1 - M_MOD) * np.cos(phi) / (
            1 + M_MOD
        ) + vel * np.sin(theta - phi) * np.cos(phi + np.pi / 2)
        self.y_vel = vel * np.cos(theta - phi) * (1 - M_MOD) * np.sin(phi) / (
            1 + M_MOD
        ) + vel * np.sin(theta - phi) * np.sin(phi + np.pi / 2)

    def fuel_collision(self):
        if not self.fission and not self.absorb:
            fission = np.random.random() < FUEL_ALPHA
            if fission:
                self.fission = True
            else:
                self.absorb = True

    def find_medium(self, cells):
        cell_idx = int(self.x_pos // CELL_SIZE * 10 + self.y_pos // CELL_SIZE)
        self.medium = cells[cell_idx].cell_type

    def draw(self, canvas):
        canvas.create_oval(
            self.x_pos * GUI_SCALE - self.size / 2,
            self.y_pos * GUI_SCALE - self.size / 2,
            self.x_pos * GUI_SCALE + self.size / 2,
            self.y_pos * GUI_SCALE + self.size / 2,
            fill=self.color,
        )
