import argparse

import numpy as np

from common_utils import get_edges_from_elements, read_nastran, \
    get_mesh_faces_from_tetra_elems, get_edges_from_faces, write_obj, get_faces_from_tetra_elements, keep_vertices
from pyvista_utils import plot_v_e, plot_v_f


def parse_argument():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_nastran',
                        default=r'D:\Truss\input\nmesh_creation\Analysis1\Analysis1.nas')

    args = parser.parse_args()
    params = args.__dict__

    return params


def main():
    params = parse_argument()
    input_file = params['input_nastran']

    vertices, elems, dof, f = read_nastran(input_file)

    mesh_faces = get_mesh_faces_from_tetra_elems(elems)

    edges = get_edges_from_elements(np.array(elems))
    mesh_edges = get_edges_from_faces(mesh_faces)

    sorted_edges = np.sort(edges, axis=1)
    sorted_mesh_edges = np.sort(mesh_edges, axis=1)

    mesh_edge_mask = (sorted_edges[:, None] == sorted_mesh_edges).all(-1).any(-1)

    colors = np.ones((len(sorted_edges), 3)).astype(int) * [0, 0, 255]
    colors[mesh_edge_mask] = [255, 0, 255]

    dof_0_idxs = np.where(np.sum(dof, axis=1) == 0)[0]

    arrow_idx = None
    arrow_dirs = None
    f_idxs = np.where(np.sum(f, axis=1) != 0)[0]
    if len(f_idxs) > 0:
        arrow_idx = f_idxs
        arrow_dirs = f[f_idxs]

    line_widths = np.ones(len(sorted_edges)) * 4
    line_widths[mesh_edge_mask] = 2
    plot_v_e(vertices, sorted_edges, colors=colors, line_widths=line_widths,
             sphere_idxs=dof_0_idxs, sphere_colors=np.zeros((len(dof_0_idxs), 3)),
             arrow_idxs=arrow_idx, arrow_dirs=arrow_dirs,
             arrow_colors=np.ones((len(arrow_idx), 3)).astype(int) * [0, 255, 0])

if __name__ == '__main__':
    main()