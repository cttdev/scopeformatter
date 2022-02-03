from matplotlib import pyplot as plt
from matplotlib import transforms
import numpy as np

class DraggableBoundingBox:
    lock = None
    def __init__(self, rectangle):
        self.rectangle = rectangle
        
        self.xy = self.rectangle.get_xy()
        self.width = self.rectangle.get_width()
        self.height = self.rectangle.get_height()

        self.dragging = None
        self.connect()

        self.press = None

    def connect(self):
        self.cidpress = self.rectangle.figure.canvas.mpl_connect(
            "button_press_event", self.on_press
        )
        # self.cidrelease = self.rectangle.figure.canvas.mpl_connect(
        #     "button_release_event", self.on_release
        # )
        self.cidmotion = self.rectangle.figure.canvas.mpl_connect(
            "motion_notify_event", self.on_motion
        )

    def disconnect(self):
        self.rectangle.figure.canvas.mpl_disconnect(self.cidpress)
        self.rectangle.figure.canvas.mpl_disconnect(self.cidrelease)
        self.rectangle.figure.canvas.mpl_disconnect(self.cidmotion)

    def on_press(self, event):
        if event.inaxes != self.rectangle.axes:
            return

        point_threshold = 0.1

        xs, ys = self.get_corner_coords()
        # Find nearest point to cursor
        min_distance = float("inf")
        for i, point in enumerate(zip(xs, ys)):
            x, y = point
            distance = np.sqrt((event.xdata - x) ** 2 + (event.ydata - y) ** 2)
            if distance < min_distance:
                min_distance = distance
                closest_index = i

        if event.button == 1:
            if min_distance < point_threshold:
                self.dragging = closest_index
        
        print(self.get_corner_coords())

    def on_motion(self, event):
        if self.dragging is None:
            return

        if event.inaxes != self.rectangle.axes:
            return

        self.transfrom_rectangle_coordinates(event.xdata, event.ydata)
            

        # self.xs[self.dragging] = self.xs[self.dragging] - event.xdata
        # self.ys[self.dragging] = self.ys[self.dragging] - event.ydata



        # self.line.set_data(self.xs, self.ys)
        # self.line.figure.canvas.draw()

        # if

        # xdx = [i+dx for i,_ in self.geometry]
        # ydy = [i+dy for _,i in self.geometry]

        # self.geometry = [[x, y] for x, y in zip(xdx, ydy)]
        # self.poly.set_xy(self.geometry)
        self.rectangle.figure.canvas.draw()

