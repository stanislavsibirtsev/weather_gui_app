from PyQt6.QtWidgets import QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates

class PlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(8, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.ax = self.figure.add_subplot(111)

    def clear(self):
        self.ax.clear()
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        self.figure.tight_layout()
        self.canvas.draw()

    def add_plot(self, timestamps, values, label):
        datetimes = [datetime.fromtimestamp(ts) for ts in timestamps]
        self.ax.plot(datetimes, values, label=label)
        self.ax.legend()
        self.figure.autofmt_xdate()
        self.canvas.draw()
