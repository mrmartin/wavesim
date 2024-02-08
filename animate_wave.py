import sys
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore
from scipy.signal import convolve

class WaveSimulator2D:
    """
    Simulates the 2D wave equation on CPU using NumPy.
    The system assumes units, where the wave speed is 1.0 pixel/timestep.
    """
    def __init__(self, w, h):
        self.global_dampening = 1.0
        self.source_opacity = 0.9
        self.c = np.ones((h, w), dtype=np.float32)
        self.d = np.ones((h, w), dtype=np.float32)
        self.u = np.zeros((h, w), dtype=np.float32)
        self.u_prev = np.zeros((h, w), dtype=np.float32)
        self.set_dampening_field(None, 32)
        self.laplacian_kernel = np.array([
            [0.05, 0.2, 0.05],
            [0.2, -1.0, 0.2],
            [0.05, 0.2, 0.05]
        ])
        self.t = 0
        self.dt = 1.0
        self.sources = np.zeros([0, 5])

    def reset_time(self):
        self.t = 0.0

    def update_field(self):
        laplacian = convolve(self.u, self.laplacian_kernel, mode='same', method='fft')
        v = (self.u - self.u_prev) * self.d
        r = (self.u + v + laplacian * (self.c * self.dt)**2)
        self.u_prev[:] = self.u
        self.u[:] = r
        self.t += self.dt
        # Add/remove source every ten frames
        if self.t % 10 == 0:
            self.add_and_remove_source()

    def get_field(self):
        return self.u

    def set_dampening_field(self, d, pml_thickness):
        if d is not None:
            assert(d.shape == self.d.shape)
            self.d = np.clip(np.array(d), 0.0, self.global_dampening)
        else:
            self.d[:] = self.global_dampening
        w = self.d.shape[1]
        h = self.d.shape[0]
        for i in range(pml_thickness):
            v = (i / pml_thickness) ** 0.5
            self.d[i, i:w - i] = v
            self.d[-(1 + i), i:w - i] = v
            self.d[i:h - i, i] = v
            self.d[i:h - i, -(1 + i)] = v

    def set_refractive_index_field(self, r):
        assert(r.shape == self.c.shape)
        self.c = 1.0/np.clip(np.array(r), 1.0, 10.0)

    def set_sources(self, sources):
        assert sources.shape[1] == 5, 'sources must have shape Nx5'
        self.sources = np.array(sources).astype(np.float32)

    def update_sources(self):
        v = np.sin(self.sources[:, 2]+self.sources[:, 4]*self.t)*self.sources[:, 3]
        coords = self.sources[:, 0:2].astype(np.int32)
        t = self.source_opacity
        self.u[coords[:, 1], coords[:, 0]] = self.u[coords[:, 1], coords[:, 0]]*t + v*(1.0-t)

    def add_and_remove_source(self):
        # Define circle parameters
        center_x, center_y, radius = 400, 600, 100
        amplitude, frequency = 100, 2*np.pi/30  # Keep consistent with your setup

        # Generate a new source
        r = np.sqrt(np.random.rand()) * radius  # Uniform distribution within the circle
        theta = np.random.rand() * 2 * np.pi
        x = center_x + r * np.cos(theta)
        y = center_y + r * np.sin(theta)
        phase = np.random.rand() * 2 * np.pi
        new_source = np.array([[x, y, phase, amplitude, frequency]])

        # Add the new source
        self.sources = np.append(self.sources, new_source, axis=0)

        # Remove a random source if any exist
        if len(self.sources) > 0:
            remove_index = np.random.randint(len(self.sources))
            self.sources = np.delete(self.sources, remove_index, axis=0)

def generate_random_points_in_circle(center_x, center_y, radius, num_points):
    points = np.zeros((num_points, 2))

    # Generate points in polar coordinates, then convert to Cartesian
    for i in range(num_points):
        r = np.sqrt(np.random.rand()) * radius  # sqrt for uniform distribution
        theta = np.random.rand() * 2 * np.pi
        x = center_x + r * np.cos(theta)
        y = center_y + r * np.sin(theta)
        points[i, :] = [x, y]

    return points

def create_sources_from_points(points, amplitude, frequency):
    num_points = points.shape[0]
    sources = np.zeros((num_points, 5))

    for i in range(num_points):
        phase = np.random.rand() * 2 * np.pi
        sources[i, :] = [points[i, 0], points[i, 1], phase, amplitude, frequency]

    return sources

width, height = 1200, 800
# Initialize the simulator with a grid size and two wave sources
simulator = WaveSimulator2D(w=height, h=width)
center_x, center_y, radius, num_points = int(height/2), int(width/2), int((width+height)/10), 1500
points = generate_random_points_in_circle(center_x, center_y, radius, num_points)
amplitude, frequency = 100, 2*np.pi/30  # Example amplitude and frequency
sources = create_sources_from_points(points, amplitude, frequency)

simulator.set_sources(sources)

max_value = 0

def update():
    global max_value
    simulator.update_sources()
    simulator.update_field()
    max_value = max(max_value, np.max(simulator.get_field()))
    imgItem.setImage(simulator.get_field(), autoLevels=False, levels=(0, max_value))

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = pg.GraphicsLayoutWidget(show=True, title="Wave Simulator 2D")
    win.resize(width, height)
    imgItem = pg.ImageItem()
    view = win.addViewBox()
    view.addItem(imgItem)
    view.setAspectLocked(True)
    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(50)
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()