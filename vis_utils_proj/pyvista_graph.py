
import numpy as np
import pyvista as pv


def plot_graph(xs, ys, x_label, y_label, output_file_path = None):

    chart = pv.Chart2D()
    chart.line(xs, ys)
    chart.x_label = x_label
    chart.y_label = y_label
    if output_file_path is None:
        chart.show()
    else:
        chart.show(screenshot = output_file_path)
