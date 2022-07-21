import os.path

import numpy as np

from common_utils import create_base_3d_grid_edges,  create_base_3d_grid
from pyvista_utils import plot_v_e


cut_y = 4
cut_x_from = 3
cut_x_to = 6

vertices, edges = create_base_3d_grid(9, 6, 3)
plot_v_e(vertices, edges)


