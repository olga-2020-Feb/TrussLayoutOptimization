import os

import numpy as np

from geom_utils import get_edges_from_elements, get_edges_from_faces, get_mesh_faces_from_tetra_elems
from io_utils.nastran_utils import read_nastran
from proc_res.export_utils import save_width_2_csv
from proc_res.vis_utils import plot_n_save_animation, pyvistaPlot
from pyvista_graph import plot_graph
from pyvista_utils import plot_v_e
from solver import solveLoop
from sample_gen import prepareStructure, prepare_input_data


def trussOptOneTime(input_file_path, output_csv_file_path,
                    output_animation_file_path, output_graph_file_path):
    Nd, PML, dof, f, initials = prepareStructure(input_file_path)

    init_Nd, init_PML, Cns, Nds, volumes, a_s, qs, us, PMLs = \
        solveLoop(Nd, PML, dof, f, initials)


    if output_csv_file_path is not None:
        save_width_2_csv(output_csv_file_path, Nd, Cns[-1][:, [0, 1]].astype(int), a_s[-1])

    if output_graph_file_path is not None:
        plot_graph(np.arange(len(volumes)), volumes, 'Iteration', 'Volume', output_graph_file_path)

    if output_animation_file_path is not None:
        threshold = np.min([np.max(a) for a in a_s]) * 1e-3
        plot_n_save_animation(init_Nd, init_PML, Cns, Nds, volumes, a_s, qs, us, PMLs, dof, f, threshold,
                              output_animation_file_path)



def trussOptOneIteration(vertices, elems, dof, f, ground_str_edges = None, init_edges = None):
    initials = [1, 1, 1]
    Nd, PML, dof, f = prepare_input_data(vertices, elems, dof, f, ground_str_edges, init_edges)

    init_Nd, init_PML, Cns, Nds, volumes, a_s, qs, us, PMLs = \
        solveLoop(Nd, PML, dof, f, initials)

    return init_Nd, init_PML, Cns, Nds, volumes, a_s, qs, us, PMLs

def update_data_example_cb(iter, dof, f, initials,
                           init_Nd, init_PML, Cns, Nds, volumes, a_s, qs, us, PMLs, user_data):
    Nd = Nds[-1]
    PML = PMLs[-1]


    return Nd, PML, dof, f, initials

def preproc_data_example_cb(Nd, PML, dof, f, initials, user_data):

    return Nd, PML, dof, f, initials

def postproc_data_example_cb(all_Nds, all_PMLs, all_dof, all_f, all_initials,
                             all_a_s, all_q_s, all_us, all_volumes, all_Cns, postproc_user_data):
    do_something = 4


def trussOptRun(vertices, elems, dof, f, iter_count,
                preproc_data_cb = None, update_data_cb = None, postproc_data_cb = None,
                preproc_user_data = None, update_user_data = None, postproc_user_data = None,
                ground_str_edges = None, init_edges = None):
    initials = [1, 1, 1]
    Nd, PML, dof, f = prepare_input_data(vertices, elems, dof, f, ground_str_edges, init_edges)

    if preproc_data_cb is not None:
        Nd, PML, dof, f, initials = preproc_data_cb(Nd, PML, dof, f, initials, preproc_user_data)

    curr_a = None
    all_a_s = []
    all_q_s = []
    all_us = []
    all_PMLs = []
    all_volumes = []
    all_Nds = []
    all_f = []
    all_dof = []
    all_initials = []
    all_Cns = []

    for i in np.arange(iter_count):
        init_Nd, init_PML, Cns, Nds, volumes, a_s, qs, us, PMLs = \
            solveLoop(Nd, PML, dof, f, initials)

        curr_a = a_s[-1]
        all_a_s.append(a_s)
        all_q_s.append(qs)
        all_us.append(us)
        all_PMLs.append(PMLs)
        all_volumes.append(volumes)
        all_Nds.append(Nd)
        all_f.append(f)
        all_dof.append(dof)
        all_initials.append(initials)
        all_Cns.append(Cns)


        if update_data_cb is not None:
            Nd, PML, dof, f, initials = update_data_cb(i, dof, f, initials,
                                                       init_Nd, init_PML, Cns, Nds, volumes, a_s, qs, us, PMLs,
                                                       update_user_data)

    if postproc_data_cb is not None:
        postproc_data_cb(all_Nds, all_PMLs, all_dof, all_f, all_initials,
                         all_a_s, all_q_s, all_us, all_volumes, all_Cns, postproc_user_data)


def update_data_movie_cb(iter, dof, f, initials,
                           init_Nd, init_PML, Cns, Nds, volumes, a_s, qs, us, PMLs, user_data):
    Nd = Nds[-1]
    PML = PMLs[-1]

    file_path = None
    if len(user_data) > 1 and user_data[1] is not None:
        path_parts = os.path.splitext(user_data[1])
        file_path = '{}_{}_{}'.format(path_parts[0], iter, path_parts[1])
    chunk_count = 10
    edge_scale_needed = True

    if len(user_data) > 2 and user_data[2] is not None:
        plot_graph(np.arange(len(volumes)), volumes, 'Iteration', 'Volume', user_data[2])


    if len(user_data) > 3:
        chunk_count = user_data[3]

    if len(user_data) > 4:
        edge_scale_needed = user_data[4]

    threshold = None

    if len(user_data) > 5 and user_data[5] is not None:
        threshold = float(user_data[5])

    if threshold is None:
        threshold = np.min([np.max(a) for a in a_s]) * 1e-6
        #threshold = 0.0


    pyvistaPlot(Nds[-1], Cns[-1][:, [0, 1, 3]].tolist(), a_s[-1], qs[-1], str, threshold, dof, f)

    if file_path is not None:
        plot_n_save_animation(init_Nd, init_PML, Cns, Nds, volumes, a_s, qs, us, PMLs, dof, f, threshold,
                              file_path, chunk_count = chunk_count, edge_scale_needed=edge_scale_needed)

    return Nd, PML, dof, f, initials

def preproc_data_visualize_cb(Nd, PML, dof, f, initials, user_data):
    vertices = Nd
    edges = PML[:, :2].astype(int)
    colors = np.array([[200, 200, 200]] * len(PML))
    colors[PML[:, 4] > 0] = [255, 0, 0]

    dof_idxs = np.where(np.sum(dof.reshape((-1, 3)), axis=1) == 0)[0]
    f_idxs = np.where(np.abs(np.sum(np.array(f).flatten().reshape((-1, 3)), axis=1)) > 0)[0]

    plot_v_e(vertices, edges, line_widths=np.ones(len(edges)),
             colors = colors, sphere_idxs= dof_idxs, sphere_colors= np.zeros((len(dof_idxs), 3)),
             arrow_idxs= f_idxs,arrow_dirs= np.array(f).reshape((-1, 3))[f_idxs],
             arrow_colors= np.ones((len(f_idxs), 3)).astype(np.int) * [0, 255, 0])
    return Nd, PML, dof, f, initials

def postproc_data_movie_cb(all_Nds, all_PMLs, all_dof, all_f, all_initials,
                           all_a_s, all_q_s, all_us, all_volumes, all_Cns, postproc_user_data):
    path_parts = os.path.splitext(postproc_user_data[0])
    print('postproc_data_movie_cb')
    for i, a_s in enumerate(all_a_s):
        if not os.path.exists(path_parts[0]):
            os.makedirs(path_parts[0])
        file_path = '{}_{}_{}'.format(path_parts[0], i, path_parts[1])

        save_width_2_csv(file_path, all_Nds[i], all_Cns[i][-1][:, [0, 1]].astype(int), a_s[-1])


def trussOptRunVisNastran(input_file_path, output_csv_file_path,
                          output_animation_file_path, output_graph_file_path):
    vertices, elems, dof, f = read_nastran(input_file_path)
    vertices = np.array(vertices)
    gr_str_edges = None
    init_gues_edges = get_edges_from_elements(elems)

    trussOptRun(vertices, elems, dof, f, 3,
                preproc_data_cb = preproc_data_visualize_cb,
                update_data_cb = update_data_movie_cb,
                postproc_data_cb = postproc_data_movie_cb,
                preproc_user_data = None, update_user_data = [output_csv_file_path, output_animation_file_path, output_graph_file_path],
                postproc_user_data = [output_csv_file_path, output_animation_file_path, output_graph_file_path],
                ground_str_edges = gr_str_edges, init_edges = init_gues_edges)