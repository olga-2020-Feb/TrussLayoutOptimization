import numpy as np


def read_nastran(input_file_path):

    with open(input_file_path, 'r') as file:
        file_lines = file.readlines()
    complete_lines = file_lines#[]

    grid_lines = [line for line in complete_lines if line.startswith('GRID')]
    elem_lines = [line for line in complete_lines if line.startswith('CTETRA')]
    spc_lines = [line for line in complete_lines if line.startswith('SPC,')]
    force_lines = [line for line in complete_lines if line.startswith('FORCE,')]

    xyz_lines = [str(line).split(',')[3:6] for line in grid_lines]
    tetra_lines = [str(line.strip()).split(',')[-4:] for line in elem_lines]
    dof_lines = [str(line).split(',')[2:] for line in spc_lines]
    f_lines = [str(line).split(',')[2:] for line in force_lines]

    vertices = np.array([[float(str) for str in lines] for lines in xyz_lines])
    elems = np.array([[(int(str) - 1) for str in lines] for lines in tetra_lines])


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


    return vertices, elems, dof, f

