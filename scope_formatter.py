import os
import random
import sys
from matplotlib.widgets import RectangleSelector
import mplcursors


import numpy as np
import matplotlib.pyplot as plt

from PyQt5 import QtCore

import qtmodern.styles
import qtmodern.windows
from PyQt5.QtWidgets import QApplication, QGroupBox, QHBoxLayout, QMessageBox, QPushButton, QSlider, \
    QVBoxLayout, QWidget, QFileDialog, QListWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from data_loader import DataLoader
from data_processor import DataProcessor

from helpers import DraculaAccents, DraculaColors, process_raw_data_lines


class App(QWidget):
    def __init__(self):
        super().__init__()
        # Window
        self.setWindowTitle("Scope Formatter")

        self.width, self.height = 900, 600
        self.setMinimumSize(self.width, self.height)

        self.data_loader = None
        self.data_processor = DataProcessor(None)

        # Styling
        plt.style.use("./dracula.mplstyle")
        self.canvas_series_color = random.choice(list(DraculaAccents))
        self.processed_canvas_series_color = random.choice([i for i in list(DraculaAccents) if i != self.canvas_series_color])

        # Canvas and Toolbar
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.canvas.axes.grid(color=DraculaColors.current_line.value)
        self.canvas.axes.set_axisbelow(True)

        self.toolbar = NavigationToolbar(self.canvas, self)

        self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.canvas.setFocus()

        props = dict(facecolor=self.processed_canvas_series_color.value, alpha=0.1)
        self.selector = RectangleSelector(self.canvas.axes, self.bounding_box_select,
                                       useblit=True,
                                       button=[1, 3],  # don't use middle button
                                       minspanx=0, minspany=0,
                                       spancoords='data',
                                       drag_from_anywhere=True,
                                       interactive=True,
                                       props=props)

        self.processed_figure = plt.figure()
        self.processed_canvas = FigureCanvas(self.processed_figure)
        self.processed_canvas.axes = self.processed_canvas.figure.add_subplot(111)
        self.processed_canvas.axes.grid(color=DraculaColors.current_line.value)
        self.processed_canvas.axes.set_axisbelow(True)

        self.processed_toolbar = NavigationToolbar(self.processed_canvas, self)

        self.processed_canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.processed_canvas.setFocus()

        self.processed_canvas_series = None
        self.processed_canvas_cursor = None

        # Buttons
        file_button = QPushButton("Load TXT")
        file_button.clicked.connect(self.loadFile)

        self.plot_button = QPushButton("Plot Data")
        self.plot_button.setEnabled(False)
        self.plot_button.clicked.connect(self.plotData)

        self.zero_offset_button = QPushButton("Zero Offset")
        self.zero_offset_button.setCheckable(True)
        self.zero_offset_button.setChecked(False)
        self.zero_offset_button.setEnabled(False)
        self.zero_offset_button.clicked.connect(self.zero_offset_signal)

        self.export_button = QPushButton("Export CSV")
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self.export_processed_data_as_csv)


        file_button.setMinimumSize(100, 50)
        self.plot_button.setMinimumSize(100, 50)
        self.zero_offset_button.setMinimumSize(100, 50)
        self.export_button.setMinimumSize(100, 50)

        #-Choosers
        self.x_chooser = QListWidget()
        self.x_chooser.itemClicked.connect(self.update_x_values)
    

        # Slider
        self.decimation_slider = QSlider()
        self.decimation_slider.setEnabled(False)
        self.decimation_slider.setOrientation(QtCore.Qt.Horizontal)
        self.decimation_slider.setMinimum(1)
        self.decimation_slider.setMaximum(10)
        self.decimation_slider.setValue(1)
        self.decimation_slider.setTickPosition(QSlider.TicksBelow)
        self.decimation_slider.valueChanged.connect(self.change_decimation)

        # Layout
        main_layout = QHBoxLayout()

        plot_layout = QVBoxLayout()
        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.canvas)

        processed_plot_layout = QVBoxLayout()
        processed_plot_layout.addWidget(self.processed_toolbar)
        processed_plot_layout.addWidget(self.processed_canvas)

        settings_layout = QVBoxLayout()
        settings_layout.addWidget(file_button)
        settings_layout.addWidget(self.plot_button)
        settings_layout.addWidget(self.zero_offset_button)
        settings_layout.addWidget(self.export_button)

        slider_layout = QVBoxLayout()
        slider_layout.addWidget(self.decimation_slider)

        slider_group = QGroupBox("Decimation")
        slider_group.setMaximumSize(300, 100)
        slider_group.setLayout(slider_layout)

        settings_layout.addWidget(slider_group)

        main_layout.addLayout(settings_layout)
        main_layout.addLayout(plot_layout)
        main_layout.addLayout(processed_plot_layout)

        self.setLayout(main_layout)

        self.show()


    def loadFile(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "TXT Files (*.txt)")

        msg = QMessageBox()

        try:
            self.data_loader = DataLoader(file_name)
            self.data_processor.set_raw_data(self.data_loader.get_data())
            
            for i in range(len(self.data_loader.get_data()[0])):
                self.x_chooser.addItem(str(i))

            msg.setIcon(QMessageBox.Information)
            msg.setText("Successfully loaded {}.".format(os.path.basename(file_name)))
            msg.setWindowTitle("Success!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

            self.canvas.axes.clear()
            self.processed_canvas.axes.clear()

            self.plot_button.setEnabled(True)
        except:
            self.plot_button.setEnabled(False)
            self.zero_offset_button.setEnabled(False)
            self.export_button.setEnabled(False)
            self.decimation_slider.setEnabled(False)

            msg.setIcon(QMessageBox.Critical)
            if file_name == "":
                msg.setText("No file selected! Try Again.")
            else:
                msg.setText("Could not load {}.".format(os.path.basename(file_name)))

            msg.setWindowTitle("Error!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()


    def plotData(self):
        raw_data = self.data_processor.get_raw_data()

        self.canvas_series = self.canvas.axes.scatter(raw_data[:, 0], raw_data[:, 1], color=self.canvas_series_color.value)
        self.canvas.axes.grid(color=DraculaColors.current_line.value)

        data, extents = self.data_processor.update_data()

        self.processed_canvas_series = self.processed_canvas.axes.scatter(data[:, 0], data[:, 1], color=self.processed_canvas_series_color.value)
        self.processed_canvas.axes.grid(color=DraculaColors.current_line.value)

        self.data_processor.set_extents(self.processed_canvas.axes.get_xlim(), self.processed_canvas.axes.get_ylim())

        self.add_processed_canvas_cursor()

        self.canvas.draw()
        self.processed_canvas.draw()

        self.zero_offset_button.setEnabled(True)
        self.export_button.setEnabled(True)
        self.decimation_slider.setEnabled(True)


    def update_x_values(self, item):
        print(item)


    def bounding_box_select(self, eclick, erelease):
        extents = self.selector.extents

        if extents[0] == extents[1] and extents[2] == extents[3]:
            self.data_processor.set_extents(self.canvas.axes.get_xlim(), self.canvas.axes.get_ylim())
        else:
            self.data_processor.set_extents(extents[0:2], extents[2:4])

        self.update_canvas()


    def export_processed_data_as_csv(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "CSV Files (*.csv)")

        msg = QMessageBox()

        try:
            mod_file_name = (file_name.split(".")[0] + "_" + self.date.replace("/", "-") + "_" + self.start_time.strftime("%H%M%S")) + ".csv"

            np.savetxt(mod_file_name, self.processed_data, delimiter=",")

            msg.setIcon(QMessageBox.Information)
            msg.setText("Successfully Saved {}.".format(os.path.basename(file_name)))
            msg.setWindowTitle("Success!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        except:
            msg.setIcon(QMessageBox.Critical)
            if file_name == "":
                msg.setText("No file selected! Try Again.")
            else:
                msg.setText("Could not save {}.".format(os.path.basename(file_name)))

            msg.setWindowTitle("Error!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()


    def change_decimation(self, value):
        self.data_processor.set_decimation(value)
        self.update_canvas()


    def zero_offset_signal(self):
        self.data_processor.set_zero_offset(self.zero_offset_button.isChecked())
        self.update_canvas()


    def update_canvas(self):
        data, extents = self.data_processor.process_data()

        self.processed_canvas.axes.set_xlim(extents[0:2])
        self.processed_canvas.axes.set_ylim(extents[2:4])

        if self.processed_canvas_series is not None:
            self.processed_canvas_series.remove()
            self.processed_canvas_cursor.remove()

            self.processed_canvas_series = self.processed_canvas.axes.scatter(data[:, 0], data[:, 1], color=self.processed_canvas_series_color.value)
            self.add_processed_canvas_cursor()

        self.processed_canvas.axes.grid(color=DraculaColors.current_line.value)

        self.processed_canvas.draw()


    def add_processed_canvas_cursor(self):
        self.processed_canvas_cursor = mplcursors.cursor(self.processed_canvas_series, hover=True)
        @self.processed_canvas_cursor.connect("add")
        def _(sel):
            sel.annotation.get_bbox_patch().set(fc=DraculaColors.foreground.value)
            sel.annotation.arrow_patch.set(arrowstyle="simple", fc=DraculaColors.foreground.value, alpha=.75)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    qtmodern.styles.dark(app)

    main = App()

    sys.exit(app.exec_())
