import re

import numpy as np


def read_nastran(input_file_path):

    with open(input_file_path, 'r') as file:
        file_lines = file.readlines()
    complete_lines = file_lines#[]

    #grid_lines = [line for line in complete_lines if line.startswith('GRID')]

    grid_data_list = [(idx, line) for idx, line in enumerate(complete_lines) if  line.startswith('GRID')]
    grid_lines = [line for i, (idx, line) in enumerate(grid_data_list)]
    grid_line_idxs = [idx for i, (idx, line) in enumerate(grid_data_list)]


    elem_lines = [line for line in complete_lines if line.startswith('CTETRA')]
    quad4_lines = [line for line in complete_lines if line.startswith('CQUAD4')]
    spc_lines = [line for line in complete_lines if line.startswith('SPC,')]
    force_lines = [line for line in complete_lines if line.startswith('FORCE,')]

    format_data_list = [(idx, line) for idx, line in enumerate(complete_lines) if '><' in line]
    format_lines = [line for i, (idx, line) in enumerate(format_data_list)]
    format_line_idxs = [idx for i, (idx, line) in enumerate(format_data_list)]

    if len(format_line_idxs) > 0:
        min_xyz_idx = grid_line_idxs[0]
        min_format_idx = [i for i, idx in enumerate(format_line_idxs) if idx < min_xyz_idx][-1]
        format_line = format_lines[min_format_idx]
        token_idxs = np.array([_.start() for _ in re.finditer('><', format_line)])
        xyz_idx_lines = [line[token_idxs[0] + 1: token_idxs[1] + 1] for line in grid_lines]
        xyz_idxs = [int(str) for str in xyz_idx_lines]
        xyz_idxs_dict = dict(zip(xyz_idxs, np.arange(len(grid_line_idxs))))
        xyz_bad_format_lines = \
            [[line[token_idxs[i] + 1: token_idxs[i + 1] + 1] for i in np.arange(2, 5)] for line in grid_lines]
        quad_lines = \
            [[line[token_idxs[i] + 1: token_idxs[i + 1] + 1] for i in np.arange(2, 6)] for line in quad4_lines]
        quads = np.array([[(xyz_idxs_dict[int(str)]) for str in lines] for lines in quad_lines])
        xyz_lines = [[re.sub(r'(\d|\.)(\-|\+)(\d)', r'\1e\2\3', bad_line)
                      for bad_line in bad_lines]
                     for bad_lines in xyz_bad_format_lines]
    else:
        xyz_lines = [str(line).split(',')[3:6] if ',' in line else str(line).split()[2:] for line in grid_lines]
        quad_lines = [str(line.strip()).split()[-4:] for line in quad4_lines]
        quads = np.array([[(int(str) - 1) for str in lines] for lines in quad_lines])

    tetra_lines = [str(line.strip()).split(',')[-4:] for line in elem_lines]

    dof_lines = [str(line).split(',')[2:] for line in spc_lines]
    f_lines = [str(line).split(',')[2:] for line in force_lines]

    vertices = np.array([[float(str) for str in lines] for lines in xyz_lines])
    elems = np.array([[(int(str) - 1) for str in lines] for lines in tetra_lines])


    output_elems_list = []
    if len(elems) > 0:
        output_elems_list.append(elems)
    if len(quads) > 0:
        output_elems_list.append(quads)
    output_elems = np.concatenate(output_elems_list)


    dof_idxs = [(int(lines[0]) - 1) for lines in dof_lines]
    dof_dim_idxs =  [(int(lines[1]) - 1) for lines in dof_lines]
    dof_val =  [float(lines[2]) for lines in dof_lines]

    f_idxs = [(int(lines[0]) - 1) for lines in f_lines]
    f_vals =  np.array([[float(str) for str in lines[3:6]] for lines in f_lines])

    dof = np.ones_like(vertices)
    dof[dof_idxs, dof_dim_idxs] = dof_val

    f = np.zeros_like(vertices)
    if len(f_idxs) > 0:
        f[f_idxs, :] = f_vals


    return vertices, output_elems, dof, f

