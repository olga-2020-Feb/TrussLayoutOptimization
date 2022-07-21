import numpy as np


def create_base_3d_grid_edges(xs, ys, zs):
    edges_x_start = np.tile(np.tile(np.arange(len(xs) - 1), len(ys)).reshape((len(ys), -1)) +
                            (np.arange(len(ys)).reshape((-1, 1)) * len(xs)), (len(zs), 1, 1)) + \
                    (np.arange(len(zs)).reshape((-1, 1, 1)) * len(xs) * len(ys))
    edges_x_end = np.tile(np.tile(np.arange(1, len(xs)), len(ys)).reshape((len(ys), -1)) +
                          (np.arange(len(ys)).reshape((-1, 1)) * len(xs)), (len(zs), 1, 1)) + \
                  (np.arange(len(zs)).reshape((-1, 1, 1)) * len(xs) * len(ys))
    edges_y_start = np.tile(np.tile(np.arange(len(xs)), len(ys) - 1).reshape((len(ys) - 1, -1)) +
                            (np.arange(len(ys) - 1).reshape((-1, 1)) * len(xs)), (len(zs), 1, 1)) + \
                    (np.arange(len(zs)).reshape((-1, 1, 1)) * len(xs) * len(ys))
    edges_y_end = np.tile(np.tile(np.arange(len(xs)), len(ys) - 1).reshape((len(ys) - 1, -1)) +
                          (np.arange(1, len(ys)).reshape((-1, 1)) * len(xs)), (len(zs), 1, 1)) + \
                  (np.arange(len(zs)).reshape((-1, 1, 1)) * len(xs) * len(ys))
    edges_z_start = np.tile(np.tile(np.arange(len(xs)), len(ys)).reshape((len(ys), -1)) +
                            (np.arange(len(ys)).reshape((-1, 1)) * len(xs)), (len(zs) - 1, 1, 1)) + \
                    (np.arange(len(zs) - 1).reshape((-1, 1, 1)) * len(xs) * len(ys))
    edges_z_end = np.tile(np.tile(np.arange(len(xs)), len(ys)).reshape((len(ys), -1)) +
                          (np.arange(len(ys)).reshape((-1, 1)) * len(xs)), (len(zs) - 1, 1, 1)) + \
                  (np.arange(1, len(zs)).reshape((-1, 1, 1)) * len(xs) * len(ys))
    edges_diag_start = np.tile(np.tile(np.arange(len(xs) - 1), len(ys) - 1).reshape((len(ys) - 1, -1)) +
                               (np.arange(len(ys) - 1).reshape((-1, 1)) * len(xs)), (len(zs) - 1, 1, 1)) + \
                       (np.arange(len(zs) - 1).reshape((-1, 1, 1)) * len(xs) * len(ys))
    edges_diag_end = np.tile(np.tile(np.arange(1, len(xs)), len(ys) - 1).reshape((len(ys) - 1, -1)) +
                             (np.arange(1, len(ys)).reshape((-1, 1)) * len(xs)), (len(zs) - 1, 1, 1)) + \
                     (np.arange(1, len(zs)).reshape((-1, 1, 1)) * len(xs) * len(ys))

    edges_x = np.vstack((edges_x_start.flatten(), edges_x_end.flatten())).T
    edges_y = np.vstack((edges_y_start.flatten(), edges_y_end.flatten())).T
    edges_z = np.vstack((edges_z_start.flatten(), edges_z_end.flatten())).T
    edges_diag = np.vstack((edges_diag_start.flatten(), edges_diag_end.flatten())).T
    edges = np.concatenate((edges_x, edges_y, edges_z, edges_diag))
    return edges

def create_base_3d_grid(x_count, y_count, z_count):
    xs = np.arange(x_count)
    ys = np.arange(y_count)
    zs = np.arange(z_count)

    xs_matrix = np.tile(xs, (len(zs), len(ys), 1))
    ys_matrix = np.tile(ys.reshape((-1, 1)), (len(zs), 1, len(xs)))
    zs_matrix = np.tile(zs.reshape((-1, 1, 1)), (1, len(ys), len(xs)))

    vertices = np.array([xs_matrix.flatten(), ys_matrix.flatten(), zs_matrix.flatten()]).T
    edges = create_base_3d_grid_edges(xs, ys, zs)

    edges_start = np.tile(np.arange(len(vertices)), len(vertices))
    edges_end = np.repeat(np.arange(len(vertices)), len(vertices))
    edges = np.vstack((edges_start, edges_end)).T
    zero_len_idxs = np.where(edges[:, 0] == edges[:, 1])[0]
    edges = np.delete(edges, zero_len_idxs, axis=0)

    return vertices.astype(np.float), edges