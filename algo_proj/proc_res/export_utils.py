import numpy as np

from io_utils.csv_utils import write_csv


def save_width_2_csv(csv_file_path, vertices, edges, widths):
    labels = [str(v) for v in vertices]
    res_table = np.zeros((len(vertices), len(vertices)))
    res_table[edges[:, 0], edges[:, 1]] = widths
    res_table[edges[:, 1], edges[:, 0]] = widths
    write_csv(csv_file_path, res_table, labels, labels)
