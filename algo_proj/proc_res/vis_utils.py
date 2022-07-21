import numpy as np

from proc_res.vis_mathplotlib import mathplotlibPlot
from proc_res.vis_pyvista import prepareAnimationConsts
from pyvista_animation import animation_v_e
from pyvista_utils import plot_v_e

def plot_n_save_animation(init_Nd, init_PML, Cns, Nds, volumes, a_s, qs, us, PMLs, dof, f, threshold, output_file_path):
    animation_edges, animation_colors, animation_widths, \
    all_animation_edges, all_animation_colors, all_animation_widths = \
        collect_animation_data(init_Nd, init_PML, Cns, Nds, volumes, a_s, qs, us, PMLs, threshold)
    plotTrussAnimation(init_Nd, animation_colors, animation_edges, animation_widths, dof, f, output_file_path)


def plotTrussAnimation(Nd, animation_colors, animation_edges, animation_widths,
                       dof, f,
                       output_file_path = r"output/Animation.mp4"):
    dof_0_idxs, sphere_colors, _, arrow_idx, arrow_dirs, arrow_colors, _ = \
        prepareAnimationConsts(dof, f)
    ver = [[Nd]] * len(animation_edges)
    dof_0_idxs_list = [dof_0_idxs] * len(animation_edges)
    sphere_colors_list = [sphere_colors] * len(animation_edges)
    arrow_idxs_list = [arrow_idx] * len(animation_edges)
    arrow_dirs_list = [arrow_dirs] * len(animation_edges)
    arrow_colors_list = [arrow_colors] * len(animation_edges)
    animation_v_e(ver, animation_edges,
                  edge_colors_list=animation_colors, line_width_list=animation_widths,
                  sphere_idxs_list=dof_0_idxs_list, sphere_colors_list=sphere_colors_list,
                  arrow_idxs_list=arrow_idxs_list, arrow_dirs_list=arrow_dirs_list, arrow_colors_list=arrow_colors_list,
                  file_2_save=output_file_path)



def pyvistaPlot(vertices,edges, a, q, str, threshold, dof=[], f=[]):

    iter_line_widths = []

    iter_colors, iter_edges = [], []
    f = np.array(f)
    f = f.reshape(int(f.size/3), -1)
    dof = np.array(dof)
    dof = dof.reshape(int(dof.size / 3), -1)
    _, _, _, iter_colors, iter_edges, iter_line_widths = \
        get_edges_from_data(np.array(edges)[:, :2], a, q, threshold)

    dof_0_idxs = np.where(np.sum(dof, axis=1) == 0)[0]
    f_idxs = np.where(np.sum(f, axis=1) != 0)[0]
    if len(f_idxs) > 0:
        arrow_idx = f_idxs
        arrow_dirs = f[f_idxs]

    plot_v_e(vertices, np.array(iter_edges).astype(np.int),
                  colors = np.array(iter_colors), line_widths=iter_line_widths,sphere_idxs= dof_0_idxs, sphere_colors= np.zeros((len(dof_0_idxs), 3)),
                  arrow_idxs= arrow_idx,arrow_dirs= arrow_dirs,arrow_colors= np.ones((len(arrow_idx), 3)).astype(np.int) * [0, 255, 0])




    # edges = np.array(edges+edges)       #3D Plot bug in here
    # vplt.plot_v_e(vertices, np.array(edges.astype(np.int)))


def collect_animation_data(init_Nd, init_PML, Cns, Nds, volumes, a_s, qs, us, PMLs, threshold):
    animation_edges=[]
    animation_colors=[]
    animation_widths = []
    all_animation_edges=[]
    all_animation_colors=[]
    all_animation_widths=[]

    for i, (Cn, a, q) in enumerate(zip(Cns, a_s, qs)):
        all_iter_colors, all_iter_edges, all_iter_widths, iter_colors, iter_edges, iter_widths = \
            get_edges_from_data(Cn, a, q, threshold)

        animation_colors.append(np.array(iter_colors))
        animation_edges.append(np.array(iter_edges))
        animation_widths.append(iter_widths)
        all_animation_colors.append(np.array(all_iter_colors))
        all_animation_edges.append(np.array(all_iter_edges))
        all_animation_widths.append(all_iter_widths)

    return animation_edges, animation_colors, animation_widths, \
           all_animation_edges, all_animation_colors, all_animation_widths




def plotTruss(Nd, Cn, a, q, threshold, str,dof, f, update = True,
              show = "mathplotlib",
              animation_edges=[],animation_colors=[], animation_widths = [],
              all_animation_edges=[], all_animation_colors=[], all_animation_widths=[],
              ITER_PLOT = True, ITER_ANIMATION = True):
    if show == 'pyvista':
        if(ITER_PLOT):
            pyvistaPlot(Nd, Cn[:, [0, 1, 4]].tolist(), a, q, str, threshold, update, dof, f)
        if (ITER_ANIMATION):
            all_iter_colors, all_iter_edges, all_iter_widths, iter_colors, iter_edges, iter_widths = \
                get_edges_from_data(Cn, a, q, threshold)

            animation_colors.append(np.array(iter_colors))
            animation_edges.append(np.array(iter_edges))
            animation_widths.append(iter_widths)
            all_animation_colors.append(np.array(all_iter_colors))
            all_animation_edges.append(np.array(all_iter_edges))
            all_animation_widths.append(all_iter_widths)

    else:
        mathplotlibPlot(Cn, Nd, a, q, str, threshold, update)


def get_edges_from_data(Cn, a, q, threshold):
    iter_colors, iter_edges, iter_widths = [], [], []
    all_iter_colors, all_iter_edges, all_iter_widths = [], [], []

    for i in range(len(a)):
        radius = (a[i] / np.pi) ** .5
        all_iter_edges.append([int(Cn[i][0]), int(Cn[i][1])])
        all_iter_widths.append(radius)
        if all([q[lc][i] >= 0 for lc in range(len(q))]):
            all_iter_colors.append(np.array([255, 0, 0]))  # red
        elif all([q[lc][i] <= 0 for lc in range(len(q))]):
            all_iter_colors.append(np.array([0, 0, 255]))  # blue
        else:
            all_iter_colors.append(np.array([200, 200, 200]))  # gray
        if a[i] >= threshold:
            iter_edges.append([int(Cn[i][0]), int(Cn[i][1])])
            iter_widths.append(radius)
            if all([q[lc][i] >= 0 for lc in range(len(q))]):
                iter_colors.append(np.array([255, 0, 0]))  # red
            elif all([q[lc][i] <= 0 for lc in range(len(q))]):
                iter_colors.append(np.array([0, 0, 255]))  # blue
    return all_iter_colors, all_iter_edges, all_iter_widths, iter_colors, iter_edges, iter_widths