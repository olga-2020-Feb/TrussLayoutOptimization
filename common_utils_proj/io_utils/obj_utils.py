import numpy as np

def write_obj(out_file_path, vertices, faces):

    v_lines = ['v {} {} {}\n'.format(v[0], v[1], v[2]) for v in vertices]
    f_lines = []
    if len(faces) > 0:
        f_lines = ['f {} {} {}\n'.format(f[0], f[1], f[2]) for f in (faces + 1)]
    lines = ['\n'] + v_lines + ['\n'] + f_lines + ['\n']
    with open(out_file_path, 'w') as file:
        file.writelines(lines)


def read_obj(in_file):

    with open(in_file) as file:
        lines = file.readlines()
    vert_lines = [line for line in lines if line.startswith('v ')]
    face_lines = [line for line in lines if line.startswith('f ')]
    face_idxs_lines = [line.split()[1:] for line in face_lines]

    xs = [float(line.split()[1]) for line in vert_lines]
    ys = [float(line.split()[2]) for line in vert_lines]
    zs = [float(line.split()[3]) for line in vert_lines]

    faces = np.array([[int(substr) for substr in lines] for lines in face_idxs_lines])
    faces = faces - 1

    vertices = np.array([xs, ys, zs]).transpose()

    return vertices, faces