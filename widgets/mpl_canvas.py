from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# explicitly set the backend for PyInstaller
matplotlib.use('Qt5Agg')

# Force hidden imports for PyInstaller
import _ctypes
import pkg_resources.py2_warn

class MplCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure(figsize=(5, 4))
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
