from pyvista import examples
import pyvista as pv
import numpy as np
from scipy.sparse.csgraph import connected_components

from common_utils import read_obj, get_edges_from_faces, get_adj_matrix
from pyvista_utils import plot_v_e

input_file = r'D:\Truss\input\obj\tea_pot.obj'

vertices, faces = read_obj(input_file)

edges = get_edges_from_faces(faces)

adj_matrix = get_adj_matrix(len(vertices), faces)
cc_data = connected_components(adj_matrix, directed=False)

colors = np.array([[255, 0, 0]] * len(vertices))
vert_idxs0 = np.where(cc_data[1] == 0)[0]
vert_idxs1 = np.where(cc_data[1] == 1)[0]
vert_idxs2 = np.where(cc_data[1] == 2)[0]
vert_idxs3 = np.where(cc_data[1] == 3)[0]
colors[vert_idxs0, :] = [0, 255, 0]
colors[vert_idxs1, :] = [0, 0, 255]
colors[vert_idxs2, :] = [0, 255, 255]
colors[vert_idxs3, :] = [255, 255, 0]

colors = np.array([[255, 0, 0]] * len(edges))
edges0 = np.where(np.sum(np.isin(edges, vert_idxs0), axis = 1) > 0)[0]
edges1 = np.where(np.sum(np.isin(edges, vert_idxs1), axis = 1) > 0)[0]
edges2 = np.where(np.sum(np.isin(edges, vert_idxs2), axis = 1) > 0)[0]
edges3 = np.where(np.sum(np.isin(edges, vert_idxs3), axis = 1) > 0)[0]
colors[edges0, :] = [0, 255, 0]
colors[edges1, :] = [0, 0, 255]
colors[edges2, :] = [0, 255, 255]
colors[edges3, :] = [255, 255, 0]

plot_v_e(vertices, edges, colors)

