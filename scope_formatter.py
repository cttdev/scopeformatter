import os
import random
import sys
from matplotlib.widgets import RectangleSelector
import mplcursors


import numpy as np
import matplotlib.pyplot as plt

from PyQt5 import QtCore, QtGui

import qtmodern.styles
import qtmodern.windows
from PyQt5.QtWidgets import QApplication, QGroupBox, QHBoxLayout, QLineEdit, QMessageBox, QPushButton, QSlider, QTabWidget, \
    QVBoxLayout, QWidget, QFileDialog, QListWidget, QLabel, QSplashScreen
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from data_loader import DataLoader
from data_processor import DataProcessor

from helpers import DraculaAccents, DraculaColors, InterpolationTypes


class App(QWidget):
    def __init__(self):
        super().__init__()
        # Window
        self.setWindowTitle("Scope Formatter")

        self.width, self.height = 900, 600
        self.setMinimumSize(self.width, self.height)

        self.data_loader = None
        self.data_processor = DataProcessor(np.array([]))

        # Styling
        plt.style.use("./dracula.mplstyle")
        self.canvas_series_color = random.choice(list(DraculaAccents))
        self.processed_canvas_series_color = random.choice([i for i in list(DraculaAccents) if not i in [self.canvas_series_color]])
        self.interpolated_series_color = random.choice([i for i in list(DraculaAccents) if not i in [self.canvas_series_color, self.processed_canvas_series_color]])

        # Canvas and Toolbar
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.canvas.axes.grid(color=DraculaColors.current_line.value)
        self.canvas.axes.set_axisbelow(True)

        self.toolbar = NavigationToolbar(self.canvas, self)

        self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.canvas.setFocus()

        self.canvas_series = None

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
        self.interpolated_series = None
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

        self.interpolate_button = QPushButton("Interpolate")
        self.interpolate_button.setCheckable(True)
        self.interpolate_button.setChecked(False)
        self.interpolate_button.clicked.connect(self.update_processed_canvas)

        file_button.setMinimumSize(100, 50)
        self.plot_button.setMinimumSize(100, 50)
        self.zero_offset_button.setMinimumSize(100, 50)
        self.export_button.setMinimumSize(100, 50)

        #-Choosers
        self.x_chooser = QListWidget()
        self.x_chooser.itemClicked.connect(self.update_series_values)

        self.y_chooser = QListWidget()
        self.y_chooser.itemClicked.connect(self.update_series_values)

        self.interpolation_chooser = QListWidget()
        self.interpolation_chooser.addItems({i.name: i.value for i in InterpolationTypes})
        self.interpolation_chooser.setCurrentRow(0)
        self.interpolation_chooser.itemClicked.connect(self.update_processed_canvas)

        # Entry
        self.x_divisor_entry = QLineEdit()
        self.x_divisor_entry.setValidator(QtGui.QDoubleValidator())
        self.x_divisor_entry.setText("1")
        self.x_divisor_entry.textChanged.connect(self.change_x_divisor)

        self.y_divisor_entry = QLineEdit()
        self.y_divisor_entry.setValidator(QtGui.QDoubleValidator())
        self.y_divisor_entry.setText("1")
        self.y_divisor_entry.textChanged.connect(self.change_y_divisor)

        # Label
        self.interpolate_equation = QLabel()

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

        # Plots
        plot_layout = QVBoxLayout()
        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.canvas)

        processed_plot_layout = QVBoxLayout()
        processed_plot_layout.addWidget(self.processed_toolbar)
        processed_plot_layout.addWidget(self.processed_canvas)

        # Settings
        settings_tabs = QTabWidget()

        # Main Settings
        main_settings_tab = QWidget()

        main_settings_tab.layout = QVBoxLayout(main_settings_tab)
        main_settings_tab.layout.addWidget(file_button)
        main_settings_tab.layout.addWidget(self.x_chooser)
        main_settings_tab.layout.addWidget(self.plot_button)
        main_settings_tab.layout.addWidget(self.zero_offset_button)
        main_settings_tab.layout.addWidget(self.export_button)

        slider_layout = QVBoxLayout()
        slider_layout.addWidget(self.decimation_slider)

        slider_group = QGroupBox("Decimation")
        slider_group.setMaximumSize(300, 100)
        slider_group.setLayout(slider_layout)

        main_settings_tab.layout.addWidget(slider_group)

        main_settings_tab.setLayout(main_settings_tab.layout)
        settings_tabs.addTab(main_settings_tab, "Main")

        # Series Settings
        self.series_settings_tab = QWidget()

        self.series_settings_tab.layout = QVBoxLayout(self.series_settings_tab)

        # X-Series
        self.series_settings_tab.layout.addWidget(self.x_chooser)

        x_divisor_layout = QVBoxLayout()
        x_divisor_layout.addWidget(self.x_divisor_entry)

        x_divisor_group = QGroupBox("X Divisor")
        x_divisor_group.setMaximumSize(300, 100)
        x_divisor_group.setLayout(x_divisor_layout)

        self.series_settings_tab.layout.addWidget(x_divisor_group)

        # Y-Series
        self.series_settings_tab.layout.addWidget(self.y_chooser)

        y_divisor_layout = QVBoxLayout()
        y_divisor_layout.addWidget(self.y_divisor_entry)

        y_divisor_group = QGroupBox("Y Divisor")
        y_divisor_group.setMaximumSize(300, 100)
        y_divisor_group.setLayout(y_divisor_layout)

        self.series_settings_tab.layout.addWidget(y_divisor_group)

        self.series_settings_tab.setLayout(self.series_settings_tab.layout)
        settings_tabs.addTab(self.series_settings_tab, "Series")

        self.series_settings_tab.setEnabled(False)

        # Interpolation Settings
        self.interpolation_settings_tab = QWidget()

        self.interpolation_settings_tab.layout = QVBoxLayout()

        self.interpolation_settings_tab.layout.addWidget(self.interpolation_chooser)
        self.interpolation_settings_tab.layout.addWidget(self.interpolate_button)

        interpolate_equation_layout = QVBoxLayout()
        interpolate_equation_layout.addWidget(self.interpolate_equation)

        interpolate_equation_group = QGroupBox("Equation")
        interpolate_equation_group.setMaximumSize(300, 100)
        interpolate_equation_group.setLayout(interpolate_equation_layout)

        self.interpolation_settings_tab.layout.addWidget(interpolate_equation_group)

        self.interpolation_settings_tab.setLayout(self.interpolation_settings_tab.layout)
        settings_tabs.addTab(self.interpolation_settings_tab, "Interpolation")

        self.interpolation_settings_tab.setEnabled(False)

        # Main Layout 
        main_layout.addWidget(settings_tabs)
        main_layout.addLayout(plot_layout)
        main_layout.addLayout(processed_plot_layout)

        self.setLayout(main_layout)


    def loadFile(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "TXT Files (*.txt)")

        msg = QMessageBox()

        try:
            self.data_loader = DataLoader(file_name)

            series_names = list(self.data_loader.get_series_dict())

            self.x_chooser.clear()
            self.y_chooser.clear()

            # Enable choosers
            self.x_chooser.addItems(series_names)
            self.x_chooser.setCurrentRow(DataLoader.DataColums.Time.value)

            self.y_chooser.addItems(series_names)
            self.y_chooser.setCurrentRow(DataLoader.DataColums.Voltage.value)

            self.data_processor.set_raw_data(self.get_choosen_data())

            msg.setIcon(QMessageBox.Information)
            msg.setText("Successfully loaded {}.".format(os.path.basename(file_name)))
            msg.setWindowTitle("Success!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

            self.plot_button.setEnabled(True)

        except:
            self.x_chooser.clear()
            self.y_chooser.clear()

            self.plot_button.setEnabled(False)
            self.zero_offset_button.setEnabled(False)
            self.export_button.setEnabled(False)
            self.decimation_slider.setEnabled(False)
            self.series_settings_tab.setEnabled(False)
            self.interpolation_settings_tab.setEnabled(False)

            msg.setIcon(QMessageBox.Critical)
            if file_name == "":
                msg.setText("No file selected! Try Again.")
            else:
                msg.setText("Could not load {}.".format(os.path.basename(file_name)))

            msg.setWindowTitle("Error!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

        self.canvas.axes.clear()
        self.processed_canvas.axes.clear()

        if self.canvas_series is not None:
            self.canvas_series.remove()
            self.canvas_series = None

        if self.processed_canvas_series is not None:
            self.processed_canvas_series.remove()
            self.processed_canvas_cursor.remove()
            self.processed_canvas_series = None

        self.canvas.axes.grid(color=DraculaColors.current_line.value)
        self.processed_canvas.axes.grid(color=DraculaColors.current_line.value)

        self.canvas.draw()
        self.processed_canvas.draw()


    def plotData(self):
        raw_data = self.data_processor.get_raw_data()

        # Canvas
        if self.canvas_series is not None:
            self.canvas_series.remove()

        self.canvas_series = self.canvas.axes.scatter(raw_data[:, 0], raw_data[:, 1], color=self.canvas_series_color.value)
        self.canvas.axes.grid(color=DraculaColors.current_line.value)
        
        self.update_canvas_bounds(self.canvas, self.canvas_series)
        self.canvas.draw()

        # Processed Canvas
        self.data_processor.set_extents(self.canvas.axes.get_xlim(), self.canvas.axes.get_ylim())
        data, extents = self.data_processor.process_data()

        self.processed_canvas.axes.set_xlim(extents[0:2])
        self.processed_canvas.axes.set_ylim(extents[2:4])

        if self.processed_canvas_series is not None:
            self.processed_canvas_series.remove()
            self.processed_canvas_cursor.remove()

        self.processed_canvas_series = self.processed_canvas.axes.scatter(data[:, 0], data[:, 1], color=self.processed_canvas_series_color.value)
        self.processed_canvas.axes.grid(color=DraculaColors.current_line.value)

        self.interpolate()
        self.add_processed_canvas_cursor()
        self.processed_canvas.draw()

        self.zero_offset_button.setEnabled(True)
        self.export_button.setEnabled(True)
        self.decimation_slider.setEnabled(True)
        self.series_settings_tab.setEnabled(True)
        self.interpolation_settings_tab.setEnabled(True)


    def update_series_values(self, item):
        self.data_processor.set_raw_data(self.get_choosen_data())
        self.plotData()


    def bounding_box_select(self, eclick, erelease):
        extents = self.selector.extents

        if extents[0] == extents[1] and extents[2] == extents[3]:
            self.data_processor.set_extents(self.canvas.axes.get_xlim(), self.canvas.axes.get_ylim())
        else:
            self.data_processor.set_extents(extents[0:2], extents[2:4])

        self.update_processed_canvas()


    def export_processed_data_as_csv(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "CSV Files (*.csv)")

        msg = QMessageBox()

        try:
            mod_file_name = (file_name.split(".")[0] + "_" + self.data_loader.get_dates()[0].replace("/", "-") + "_" + self.data_loader.get_start_times()[0].strftime("%H%M%S")) + ".csv"

            np.savetxt(mod_file_name, self.data_processor.process_data()[0], delimiter=",")

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


    def change_x_divisor(self, text):
        try:
            if float(text) == 0:
                return
            self.data_processor.set_x_divisor(float(text))
            self.update_processed_canvas()
        except:
            return


    def change_y_divisor(self, text):
        try:
            if float(text) == 0:
                return
            self.data_processor.set_y_divisor(float(text))
            self.update_processed_canvas()
        except:
            return


    def change_decimation(self, value):
        self.data_processor.set_decimation(value)
        self.update_processed_canvas()


    def zero_offset_signal(self):
        self.data_processor.set_zero_offset(self.zero_offset_button.isChecked())
        self.update_processed_canvas()


    def interpolate(self):
        if self.interpolate_button.isChecked():
            if self.interpolated_series is not None:
                self.processed_canvas.axes.lines.pop(0)

            interpolation_dict = {i.name: i.value for i in InterpolationTypes}
            chosen_interpolation = interpolation_dict[self.interpolation_chooser.currentItem().text()]

            data, extents = self.data_processor.process_data()
            x = data[:, 0]
            y = data[:, 1]

            model = np.poly1d(np.polyfit(x, y, chosen_interpolation))
            fit_y = model(x)

            self.interpolated_series = self.processed_canvas.axes.plot(x, fit_y, color=self.interpolated_series_color.value, linewidth=2, dash_capstyle='round')

            self.interpolate_equation.setText(str(model).strip())
        elif not len(self.processed_canvas.axes.lines) == 0:
            self.interpolated_series = None
            self.processed_canvas.axes.lines.pop(0)
            self.interpolate_equation.setText("")


    def update_processed_canvas(self):
        data, extents = self.data_processor.process_data()

        self.processed_canvas.axes.set_xlim(extents[0:2])
        self.processed_canvas.axes.set_ylim(extents[2:4])

        if self.processed_canvas_series is not None:
            self.processed_canvas_series.remove()
            self.processed_canvas_cursor.remove()

            self.processed_canvas_series = self.processed_canvas.axes.scatter(data[:, 0], data[:, 1], color=self.processed_canvas_series_color.value)
            self.add_processed_canvas_cursor()

        self.processed_canvas.axes.grid(color=DraculaColors.current_line.value)

        self.interpolate()

        self.processed_canvas.draw()


    def get_choosen_data(self):
        series_dict = self.data_loader.get_series_dict()

        chosen_x = series_dict[self.x_chooser.currentItem().text()]
        chosen_y = series_dict[self.y_chooser.currentItem().text()]

        raw_data = self.data_loader.get_data()
        return np.column_stack((raw_data[:, chosen_x], raw_data[:, chosen_y]))


    def add_processed_canvas_cursor(self):
        self.processed_canvas_cursor = mplcursors.cursor(self.processed_canvas_series, hover=True)
        @self.processed_canvas_cursor.connect("add")
        def _(sel):
            sel.annotation.get_bbox_patch().set(fc=DraculaColors.foreground.value)
            sel.annotation.arrow_patch.set(arrowstyle="simple", fc=DraculaColors.foreground.value, alpha=.75)


    @staticmethod
    def update_canvas_bounds(canvas, series):
        canvas.axes.ignore_existing_data_limits = True
        canvas.axes.update_datalim(series.get_datalim(canvas.axes.transData))
        canvas.axes.autoscale_view()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    qtmodern.styles.dark(app)

    splash = QSplashScreen(
        QtGui.QPixmap("resources/logo.png").scaledToHeight(
            400, QtCore.Qt.TransformationMode.SmoothTransformation
        )
    )
    
    splash.setWindowFlags(
        QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint
    )

    splash.show()

    main = App()

    def showWindow():
        splash.close()
        main.show()

    QtCore.QTimer.singleShot(1000, showWindow)

    sys.exit(app.exec_())
