import numpy as np


def prepareAnimationConsts(dof, f):
    f = np.array(f)
    f = f.reshape(int(f.size / 3), -1)
    dof = np.array(dof)
    dof = dof.reshape(int(dof.size / 3), -1)
    dof_0_idxs = np.where(np.sum(dof, axis=1) == 0)[0]
    arrow_idx = None
    arrow_dirs = None
    f_idxs = np.where(np.sum(f, axis=1) != 0)[0]
    if len(f_idxs) > 0:
        arrow_idx = f_idxs
        arrow_dirs = f[f_idxs]
    sphere_colors = np.zeros((len(dof_0_idxs), 3))
    arrow_colors = np.ones((len(arrow_idx), 3)).astype(np.int) * [0, 255, 0]
    arrows_and_sphere = [dof_0_idxs, sphere_colors, None, arrow_idx, arrow_dirs, arrow_colors, None]
    return dof_0_idxs, sphere_colors, None, arrow_idx, arrow_dirs, arrow_colors, None