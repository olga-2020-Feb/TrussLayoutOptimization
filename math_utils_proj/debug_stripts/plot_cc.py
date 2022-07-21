import numpy as np

from scipy.sparse.csgraph import connected_components

from geom_utils import get_adj_matrix, keep_vertices

import matplotlib.pyplot as plt

from io_utils.obj_utils import read_obj


def plot_connected_comps(vertices, faces):
    xs=vertices[:, 0]
    ys=vertices[:, 1]
    fig1, ax1 = plt.subplots()
    ax1.triplot(xs, ys, faces , 'go-', lw=1.0 )
    plt.show()

    adj_matrix = get_adj_matrix(len(vertices), faces)
    cc_data = connected_components(adj_matrix, directed=False)
    for i in np.arange(cc_data[0]):
        cc_vertex_indices = np.where(cc_data[1] == i)[0]
        cc_faces = keep_vertices(faces, cc_vertex_indices)
        xs = vertices[cc_vertex_indices, 0]
        ys = vertices[cc_vertex_indices, 1]
        fig1, ax1 = plt.subplots()
        ax1.triplot(xs, ys, cc_faces, 'go-', lw=1.0)
        plt.show()


input_file = r'D:\Truss\input\obj\tea_pot.obj'

vertices, faces = read_obj(input_file)

xs = vertices[:, 0]
ys = vertices[:, 1]

plt.plot(xs, ys, 'o', color='black')
plt.show()


fig2, ax2 = plt.subplots()
ax2.triplot(xs, ys, faces, 'go-', lw=1.0)
plt.show()

plot_connected_comps(vertices, faces)