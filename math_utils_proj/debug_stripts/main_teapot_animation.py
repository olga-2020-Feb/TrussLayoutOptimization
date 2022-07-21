import numpy as np

import pyvista as pv
from scipy.sparse.csgraph import connected_components

from common_utils import read_obj, get_adj_matrix, get_edges_from_faces, keep_vertices
from pyvista_utils import v_e_2_pyvista_mesh
from pyvista_animation import animation_v_e


def animation_1(vertices, faces, cc_data, output_file_path):
    edge_list = []
    vert_list = []
    colors_list = []

    nice_colors = [[255, 255, 0], [255, 0, 255], [0, 255, 255],
                   [0, 0, 255], [0, 255, 0], [255, 0, 0]]

    for i in np.arange(cc_data[0]):
        vert_idxs = np.where(cc_data[1] == i)[0]
        local_faces = keep_vertices(faces, vert_idxs)
        local_edges = get_edges_from_faces(local_faces)
        edge_list.append(local_edges)
        vert_list.append([vertices[vert_idxs]] * 25)
        colors_list.append(np.array([nice_colors[i]] * (len(local_edges) // 2) +
                                    [nice_colors[i + 1]] * (len(local_edges) - len(local_edges) // 2)))
    animation_v_e(vert_list, edge_list, colors_list=colors_list, file_2_save=output_file_path)


def animation_2(vertices, faces, cc_data, output_file_path):
    colors = cc_data[1]
    y_means = [np.mean(vertices[np.where(cc_data[1] == i)[0], 1]) for i in np.arange(cc_data[0])]
    x_means = [np.mean(vertices[np.where(cc_data[1] == i)[0], 0]) for i in np.arange(cc_data[0])]
    y_means_sort = np.argsort(y_means)
    x_means_sort = np.argsort(x_means)
    lid_idxs = np.where(cc_data[1] == y_means_sort[-2])[0]
    lid_handle_idxs = np.where(cc_data[1] == y_means_sort[-1])[0]
    tube_idxs = np.where(cc_data[1] == x_means_sort[-1])[0]
    main_idxs = np.where(cc_data[1] == x_means_sort[0])[0]

    edges = get_edges_from_faces(faces)

    step_size = 15
    move_unit = .1
    v_list = []
    curr_v = np.array(vertices)
    for i in np.arange(4):
        curr_move_unit = move_unit
        if i % 2 > 0:
            curr_move_unit = -move_unit
        for _ in np.arange(step_size):
            v_list.append(np.array(curr_v))
            curr_v[lid_idxs, 1] = curr_v[lid_idxs, 1] + curr_move_unit / 2
            curr_v[lid_handle_idxs, 1] = curr_v[lid_handle_idxs, 1] + curr_move_unit
    for i in np.arange(4):
        curr_move_unit = move_unit
        if i % 2 > 0:
            curr_move_unit = -move_unit
        for _ in np.arange(step_size):
            v_list.append(np.array(curr_v))
            curr_v[tube_idxs, 0] = curr_v[tube_idxs, 0] + curr_move_unit
            curr_v[main_idxs, 0] = curr_v[main_idxs, 0] - curr_move_unit
            curr_v[main_idxs, 1] = curr_v[main_idxs, 1] - curr_move_unit


    animation_v_e([v_list], [edges], colors_list=[colors], file_2_save=output_file_path)


output_file1_path = r"output\tea_pot1.mp4"
output_file2_path = r"output\tea_pot2.mp4"
input_file = r'input\obj\tea_pot.obj'

vertices, faces = read_obj(input_file)

adj_matrix = get_adj_matrix(len(vertices), faces)
cc_data = connected_components(adj_matrix, directed=False)

animation_1(vertices, faces, cc_data, output_file1_path)
animation_2(vertices, faces, cc_data, output_file2_path)


