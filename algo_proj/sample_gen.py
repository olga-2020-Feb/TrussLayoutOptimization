
import numpy as np
import itertools

import scipy

from geom_utils import get_mesh_faces_from_tetra_elems, get_edges_from_faces, get_edges_from_elements
from io_utils.nastran_utils import read_nastran


#Nastran input file

def prepareNastran(input_file):
    initials = [1, 1, 1]
    vertices, elems, dof, f = read_nastran(input_file)
    vertices = np.array(vertices)
    gr_str_edges = get_edges_from_elements(elems)
    init_gues_edges = get_edges_from_faces(get_mesh_faces_from_tetra_elems(elems))
    Nd, PML, dof, f = prepare_input_data(vertices, elems, dof, f, gr_str_edges, init_gues_edges)

    return Nd, dof, f, PML, initials


def prepare_input_data(vertices, elems, dof, f, ground_str_edges = None, init_edges = None):
    Nd = vertices

    if ground_str_edges is None:
        i_s = np.repeat(np.arange(len(vertices)), len(vertices)).flatten()
        j_s = np.tile(np.arange(len(vertices)), len(vertices)).flatten()
        edges = np.array([i_s, j_s]).T
        ground_str_edges = np.delete(edges, i_s <= j_s, axis=0)

    if init_edges is None:
        init_edges = get_edges_from_elements(elems)
        connected_vert_mask = np.isin(np.arange(len(vertices)), np.unique(init_edges))
        non_connected_vert_idxs = np.where(connected_vert_mask == False)[0]
        connected_vert_idxs = np.where(connected_vert_mask)[0]
        cdists = scipy.spatial.distance.cdist(vertices[non_connected_vert_idxs], vertices[connected_vert_idxs])
        nearast_idxs = np.argsort(cdists, axis=1)[:, :3]
        new_edges = np.stack((np.repeat(non_connected_vert_idxs, 3), connected_vert_idxs[nearast_idxs.flatten()])).T
        init_edges = np.concatenate((np.unique(init_edges, axis=0), new_edges))


    # Load and support conditions (derived from file)
    # Create the 'ground structure' from the first guess
    if ground_str_edges is not None and init_edges is not None:
        ground_str_edges = np.unique(np.sort(ground_str_edges, axis=1), axis=0)
        init_edges = np.unique(np.sort(init_edges, axis=1), axis=0)
        PML = create_PML(vertices, ground_str_edges, init_edges)
    else:
        PML = create_PML_from_elems(vertices, elems)
    dof, f = np.array(dof).flatten(), [np.array(f).flatten().tolist()]
    print('Nodes: %d Members: %d' % (len(Nd), len(PML)))
    return Nd, PML, dof, f


def create_PML(vertices, ground_str_edges = None, init_edges = None):

    cdists = scipy.spatial.distance.cdist(vertices, vertices)

    l = cdists[ground_str_edges[:, 0]].take(ground_str_edges[:, 1])

    init_guess_mask = (np.sum((init_edges[:, None, :] == ground_str_edges).all(axis=2), axis=0) > 0)

    PML = np.array([ground_str_edges[:, 0], ground_str_edges[:, 1], l]).T
    PML = np.hstack((PML, np.array([init_guess_mask, init_guess_mask]).T))
    return PML


def create_PML_from_elems(vertices, elems):
    edges = get_edges_from_elements(np.array(elems))

    # Load and support conditions (derived from file)
    # Create the 'ground structure' from the first guess
    cdists = scipy.spatial.distance.cdist(vertices, vertices)
    i_s = np.repeat(np.arange(len(vertices)), len(vertices))
    j_s = np.tile(np.arange(len(vertices)), len(vertices))
    # First guess will be the given edges
    init_guess_matrix = np.zeros_like(cdists)
    init_guess_matrix[edges[:, 0], edges[:, 1]] = True
    init_guess_matrix[edges[:, 1], edges[:, 0]] = True
    init_guess = init_guess_matrix.flatten()
    PML = np.array([i_s, j_s, cdists.flatten()]).T
    PML = np.delete(PML, np.where(i_s >= j_s)[0], axis=0)
    init_guess = np.delete(init_guess, np.where(i_s >= j_s)[0], axis=0)
    PML = np.hstack((PML, np.array([init_guess, init_guess]).T))
    return PML


def prepareStructure(file_path):

    Nd, dof, f, PML, initials = prepareNastran(file_path)

    return Nd, PML, dof, f, initials