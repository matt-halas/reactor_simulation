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

    def step(self, cells, time_step, fuel_cs, fuel_alpha, reactor_size):
        self.energy = 1 / 2 * 1.66e-27 * (self.x_vel**2 + self.y_vel**2) / 1.6e-19
        dx = self.x_vel * time_step
        dy = self.y_vel * time_step
        if dx > reactor_size or dy > reactor_size:
            print("too fast!")
        # Wall collisions changed to periodicity instead of a reflection
        if self.x_pos + dx > reactor_size or self.x_pos + dx < 0:
            self.x_pos = (self.x_pos + dx) % (reactor_size)
        else:
            self.x_pos += dx

        if self.y_pos + dy > reactor_size or self.y_pos + dy < 0:
            self.y_pos = (self.y_pos + dy) % (reactor_size)
        else:
            self.y_pos += dy

        # Determine the medium of the neutron (fuel or moderator)
        self.find_medium(cells)
        # If the medium is moderator, determine the likelihood of a collision in a path that the neutron is travelling
        # Determine the step path length in cm (m/s*100*dt)
        step_path_length = np.sqrt((self.x_vel**2 + self.y_vel**2)) * 100 * time_step
        if self.medium == "Moderator":
            # Probability formula on page 59 - neutron makes it to x WITHOUT a collision
            scatter_probability = 1 - np.exp(-MOD_MAC_SCT_CS * step_path_length)
            if scatter_probability > np.random.random():
                self.moderator_collision()
            absorb_probability = 1 - np.exp(
                -MOD_MAC_ABS_CS * 0.0253 / self.energy * step_path_length
            )
            if absorb_probability > np.random.random():
                self.absorb = True

        elif self.medium == "Fuel":
            cross_section = fuel_cs * np.sqrt(0.0253 / self.energy)
            collision_probability = 1 - np.exp(-cross_section * step_path_length)
            if collision_probability > np.random.random():
                self.fuel_collision(fuel_alpha)

    def moderator_collision(self):
        # phi is collision angle
        phi = np.random.random() * 2 * np.pi
        theta = np.atan2(self.y_vel, self.x_vel)
        theta2 = np.random.random() * 2 * np.pi
        vel = np.sqrt(self.x_vel**2 + self.y_vel**2)
        self.x_vel = (
            vel * np.cos(theta - phi) * (1 - M_MOD)
            + 2 * M_MOD * MODERATOR_RMS * np.cos(theta2 - phi)
        ) * np.cos(phi) / (1 + M_MOD) + vel * np.sin(theta - phi) * np.cos(
            phi + np.pi / 2
        )
        self.y_vel = (
            vel * np.cos(theta - phi) * (1 - M_MOD)
            + 2 * M_MOD * MODERATOR_RMS * np.cos(theta2 - phi)
        ) * np.sin(phi) / (1 + M_MOD) + vel * np.sin(theta - phi) * np.sin(
            phi + np.pi / 2
        )

    def fuel_collision(self, fuel_alpha):
        if not self.fission and not self.absorb:
            fission = np.random.random() < fuel_alpha
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
            tags="neutron",
        )
