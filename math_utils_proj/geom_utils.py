import numpy as np

def keep_vertices(f, keep_list):
    trans = dict((v, i) for i, v in enumerate(keep_list))
    trans_f = np.array([trans[v] if v in trans else -1 for row in f for v in row], dtype=np.uint32).reshape(-1, len(f[0]))

    res_f = trans_f[(trans_f != np.uint32(-1)).all(axis=1)]
    return res_f



def get_adj_matrix(vertex_count, faces):
    edges = get_edges_from_elements(faces)

    adj_matrix = np.zeros((vertex_count, vertex_count)).astype(np.int)
    adj_matrix[edges[:, 0], edges[:, 1]] = 1
    adj_matrix[edges[:, 1], edges[:, 0]] = 1
    return adj_matrix


def get_edges_from_faces(faces):
    edges1 = np.array([faces[:, 0], faces[:, 1]]).transpose()
    edges2 = np.array([faces[:, 1], faces[:, 2]]).transpose()
    edges3 = np.array([faces[:, 2], faces[:, 0]]).transpose()
    edges = np.concatenate((edges1, edges2, edges3))
    return edges

def get_mesh_faces_from_tetra_elems(elems):
    faces = get_faces_from_tetra_elements(np.array(elems))
    sorted_faces = np.sort(faces, axis=1)
    unique_faces, idxs, inv_idxs, counts = np.unique(sorted_faces, axis=0,
                                                     return_inverse=True, return_counts=True,
                                                     return_index=True)
    f_idxs = np.where(counts == 1)[0]


    return faces[idxs][f_idxs]

def get_faces_from_tetra_elements(elems):
    faces_list = []
    for (dim1, dim2, dim3) in ((2, 1, 0), (1, 3, 0), (3, 2, 0), (2, 3, 1)):

        local_faces = np.array([elems[:, dim1], elems[:, dim2], elems[:, dim3]]).T
        faces_list.append(local_faces)

    faces = np.concatenate(faces_list)
    return faces


def get_edges_from_elements(elems):
    edges_list = []
    dim = len(elems[0])
    for i in np.arange(dim):
        for j in np.arange(i + 1, dim):
            local_edges = np.array([elems[:, i], elems[:, j]]).T
            edges_list.append(local_edges)
    edges = np.concatenate(edges_list)
    return edges
