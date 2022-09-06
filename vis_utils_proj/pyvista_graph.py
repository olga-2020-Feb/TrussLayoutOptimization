
import numpy as np
import pyvista as pv
import os


def plot_graph(xs, ys, x_label, y_label, output_file_path = None):

    chart = pv.Chart2D()
    chart.line(xs, ys)
    chart.x_label = x_label
    chart.y_label = y_label
    if output_file_path is None:
        chart.show()
    else:
        parent_folder_path = os.path.split(output_file_path)[0]
        if not os.path.exists(parent_folder_path):
            os.makedirs(parent_folder_path)
        chart.show(screenshot = output_file_path)
