from settings import TIME_STEP, N_X, N_Y, CELL_SIZE, M_MOD, CROSS_SECTION, GUI_SCALE
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
        self.x_vel = np.cos(theta) * abs_speed / 100
        self.y_vel = np.sin(theta) * abs_speed / 100
        self.collision = False

    def step(self, cells):
        dx = self.x_vel * TIME_STEP
        dy = self.y_vel * TIME_STEP
        # Wall collisions changed to periodicity instead of a reflection
        if self.x_pos + dx > N_X * CELL_SIZE:
            x_collision = True
            # self.x_pos = 2 * N_X * CELL_SIZE - self.x_pos - dx
            # dx = -dx
            self.x_pos = N_X * CELL_SIZE - self.x_pos + dx
        elif self.x_pos + dx < 0:
            x_collision = True
            # self.x_pos = -self.x_pos - dx
            # dx = -dx
            self.x_pos = N_X * CELL_SIZE + self.x_pos + dx
        else:
            x_collision = False
            self.x_pos += dx

        if self.y_pos + dy > N_Y * CELL_SIZE:
            y_collision = True
            # self.y_pos = 2 * N_Y * CELL_SIZE - self.y_pos - dy
            # dy = -dy
            self.y_pos = N_Y * CELL_SIZE - self.y_pos + dy
        elif self.y_pos + dy < 0:
            y_collision = True
            # self.y_pos = -self.y_pos - dy
            # dy = -dy
            self.y_pos = N_Y * CELL_SIZE + self.y_pos + dy
        else:
            y_collision = False
            self.y_pos += dy

        if x_collision or y_collision:
            self.collision = True
        else:
            self.collision = False
        # Determine the medium of the neutron (fuel or moderator)
        self.find_medium(cells)
        # If the medium is air, determine the likelihood of a collision in a path that the neutron is travelling
        if self.medium == "Air":
            step_path_length = np.sqrt((self.x_vel**2 + self.y_vel**2)) * TIME_STEP
            # Probability formula on page 59 - neutron makes it to x WITHOUT a collision
            collision_probability = 1 - np.exp(-CROSS_SECTION * step_path_length)
            if collision_probability > np.random.random():
                self.moderator_collision()

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

    def find_medium(self, cells):
        cell_idx = int(self.x_pos // CELL_SIZE * 10 + self.y_pos // CELL_SIZE)
        self.medium = cells[cell_idx].cell_type

    def draw(self, canvas):
        size = 5
        canvas.create_oval(
            self.x_pos * GUI_SCALE - size / 2,
            self.y_pos * GUI_SCALE - size / 2,
            self.x_pos * GUI_SCALE + size / 2,
            self.y_pos * GUI_SCALE + size / 2,
            fill="black",
        )
