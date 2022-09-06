import os

import numpy as np
import pyvista as pv

from pyvista_utils import set_camera_settings, get_tube_meshes, add_arrows_copy, numpy_to_pyvista, calc_arrows_scale


def animation_v_e(v_block_list, e_list, edge_colors_list = None,
                  line_width_list = None,
                  sphere_idxs_list = None, sphere_colors_list = None, sphere_size_list = None,
                  arrow_idxs_list = None, arrow_dirs_list = None,
                  arrow_colors_list = None, arrow_scale_list = None,
                  file_2_save = None, chunk_count = 10, scale_needed = True):

    dists = np.sqrt(np.sum((v_block_list[0][0][e_list[0][:, 0]] - v_block_list[0][0][e_list[0][:, 1]]) ** 2, axis=1))

    edge_mesh_list_list, hlp_edge_mesh_list_list_list, \
    edge_chunk_indices_list_list, hlp_edge_chunk_indices_list_list_list = \
        get_mesh_lists(v_block_list, e_list, line_width_list, #1, 10,
                       chunk_count = chunk_count, scale_needed=scale_needed)

    sphere_mesh_list, hlp_sphere_mesh_list_list = get_spere_mesh_lists(v_block_list, sphere_idxs_list)

    arrows_mesh_list, hlp_arrows_mesh_list_list = get_arrow_mesh_lists(v_block_list, dists, arrow_idxs_list,
                                                                       arrow_dirs_list, arrow_scale_list)

    plotter = pv.Plotter()
    plotter.set_background('white')
    # Open a movie file
    if file_2_save is not None:
        parent_folder_path = os.path.split(file_2_save)[0]
        if not os.path.exists(parent_folder_path):
            os.makedirs(parent_folder_path)
        plotter.open_movie(file_2_save)

    actors_list = []

    frame = 0
    set_camera_settings(plotter, v_block_list[0][0])
    # Update scalars on each frame
    for i, (edge_mesh_list, chunk_indices, v_block, hlp_edge_mesh_list_list) in \
            enumerate(zip(edge_mesh_list_list, edge_chunk_indices_list_list, v_block_list, hlp_edge_mesh_list_list_list)):

        for last_actor in actors_list:
            _ = plotter.remove_actor(last_actor)
        actors_list = []

        colors = None
        rgb = False

        if edge_colors_list is not None:
            colors = edge_colors_list[i]
            rgb = len(colors.shape) > 1

        actors_list = add_edges(plotter, edge_mesh_list, chunk_indices,
                                line_width_list[i], actors_list, colors, rgb)

        actors_list = add_spheres(plotter, sphere_idxs_list, actors_list,
                                  sphere_mesh_list, sphere_colors_list, sphere_size_list, dists)

        actors_list = add_arrows(plotter, arrow_idxs_list, actors_list, arrows_mesh_list, arrow_colors_list)

        for j, (v, hlp_edge_mesh_list) in enumerate(zip(v_block, hlp_edge_mesh_list_list)):
            frame = frame + 1
            for k, edge_mesh in enumerate(edge_mesh_list):
                edge_mesh.points[:] = hlp_edge_mesh_list[k].points[:]
            if hlp_sphere_mesh_list_list is not None:
                sphere_mesh_list[i].points = hlp_sphere_mesh_list_list[i][j].points
            # if hlp_arrows_mesh_list_list is not None:
            #     arrows_mesh_list[i].points = hlp_arrows_mesh_list_list[i][j].points
            plotter.add_text(f"Iteration: {frame}", name='time-label', color=[0, 0, 0])
            for i in range(80):
                plotter.write_frame()  # Write this frame

    plotter.store_image = True
    # Be sure to close the plotter when finished
    plotter.close()


def get_mesh_lists(v_block_list, e_list, line_width_list,
                   edge_scale_min = None, edge_scale_max = None, chunk_count = 0, scale_needed = True):

    all_widths =  np.concatenate(line_width_list)
    max_width = np.max(all_widths)
    min_width = np.min(all_widths)
    if edge_scale_min is None:
        edge_scale_min = min_width
    if edge_scale_max is None:
        edge_scale_max = max_width
    edge_scale = 1

    if scale_needed and max_width > min_width:
        edge_scale = (edge_scale_max - edge_scale_min) / (max_width - min_width)

    edge_mesh_list_list = []
    hlp_edge_mesh_list_list_list = []
    edge_chunk_indices_list_list = []
    hlp_edge_chunk_indices_list_list_list = []
    for i, (v_block, edges) in enumerate(zip(v_block_list, e_list)):
        radii = None
        if line_width_list is not None:
            if scale_needed:
                radii = edge_scale_min + (np.array(line_width_list[i]) - min_width) * edge_scale
            else:
                radii = np.array(line_width_list[i])
        tube_meshes, chunk_indices = get_tube_meshes(v_block[0][edges[:, 0]], v_block[0][edges[:, 1]], radii, chunk_count)
        hlp_edge_mesh_list_list = []
        hlp_edge_chunk_indices_list_list = []
        for j, v in enumerate(v_block):
            hlp_tube_meshes, hlp_chunk_indices = get_tube_meshes(v[edges[:, 0]], v[edges[:, 1]], radii, chunk_count)
            hlp_edge_mesh_list_list.append(hlp_tube_meshes)
            hlp_edge_chunk_indices_list_list.append(hlp_chunk_indices)
        edge_mesh_list_list.append(tube_meshes)
        edge_chunk_indices_list_list.append(chunk_indices)
        hlp_edge_mesh_list_list_list.append(hlp_edge_mesh_list_list)
        hlp_edge_chunk_indices_list_list_list.append(hlp_edge_chunk_indices_list_list)

    return edge_mesh_list_list, hlp_edge_mesh_list_list_list, \
           edge_chunk_indices_list_list, hlp_edge_chunk_indices_list_list_list


def get_arrow_mesh_lists(v_block_list, dists, arrow_idxs_list = None,
                         arrow_dirs_list = None, arrow_scale_list = None):
    arrows_mesh_list = None
    hlp_arrows_mesh_list_list = None
    if arrow_idxs_list is not None:
        arrows_mesh_list = []
        hlp_arrows_mesh_list_list = []
        for i, (arrow_idxs, arrow_dirs, v_block) in \
                enumerate(zip(arrow_idxs_list, arrow_dirs_list, v_block_list)):
            if arrow_scale_list is None:
                arrow_scale = calc_arrows_scale(dists, arrow_dirs)
            else:
                arrow_scale = arrow_scale_list[i]
            arrows_mesh = add_arrows_copy(v_block[0][arrow_idxs] - arrow_dirs * arrow_scale, arrow_dirs,
                                     length_factor = arrow_scale)

            arrows_mesh_list.append(arrows_mesh)
            hlp_arrows_mesh_list = []
            for j, v in enumerate(v_block):
                hlp_arrows_mesh = add_arrows_copy(v[arrow_idxs] - arrow_dirs * arrow_scale, arrow_dirs,
                                                  length_factor = arrow_scale)
                hlp_arrows_mesh_list.append(hlp_arrows_mesh)
            hlp_arrows_mesh_list_list.append(hlp_arrows_mesh_list)

    return arrows_mesh_list, hlp_arrows_mesh_list_list


def get_spere_mesh_lists(v_block_list, sphere_idxs_list):
    sphere_mesh_list = None
    hlp_sphere_mesh_list_list = None
    if sphere_idxs_list is not None:
        sphere_mesh_list = []
        hlp_sphere_mesh_list_list = []
        for i, (sphere_idxs, v_block) in enumerate(zip(sphere_idxs_list, v_block_list)):
            points_mesh = numpy_to_pyvista(v_block[0][sphere_idxs])
            hlp_sphere_mesh_list = []
            for j, v in enumerate(v_block):
                hlp_points_mesh = numpy_to_pyvista(v[sphere_idxs])
                hlp_sphere_mesh_list.append(hlp_points_mesh)
            sphere_mesh_list.append(points_mesh)
            hlp_sphere_mesh_list_list.append(hlp_sphere_mesh_list)
    return sphere_mesh_list, hlp_sphere_mesh_list_list


def add_spheres(plotter, sphere_idxs_list, actors_list, sphere_mesh_list, sphere_colors_list, sphere_size_list, dists):
    if sphere_idxs_list is not None:
        for i, (sphere_mesh, sphere_idxs) in enumerate(zip(sphere_mesh_list, sphere_idxs_list)):
            if sphere_colors_list is not None:
                sphere_colors = sphere_colors_list[i]
            else:
                sphere_colors = np.arange(sphere_idxs.shape[0])
            if sphere_size_list is not None:
                sphere_size = sphere_size_list[i]
            else:
                sphere_size = np.min(dists) // 2
            rgb = len(sphere_colors.shape) > 1

            last_actor = plotter.add_mesh(sphere_mesh, style='points', point_size=sphere_size,
                                          render_points_as_spheres=True, scalars=sphere_colors, rgb=rgb)
            actors_list.append(last_actor)
    return actors_list


def add_arrows(plotter, arrows_idxs_list, actors_list, arrow_mesh_list, arrow_colors_list):
    if arrows_idxs_list is not None:
        for i, (arrow_mesh, arrow_idxs) in enumerate(zip(arrow_mesh_list, arrows_idxs_list)):
            if arrow_colors_list is not None:
                arrow_colors = arrow_colors_list[i]
            else:
                arrow_colors = np.arange(arrow_idxs.shape[0])
            rgb = len(arrow_colors.shape) > 1

            local_arrow_colors = arrow_colors.repeat(len(arrow_mesh.vectors) // len(arrow_idxs), axis=0)
            last_actor = plotter.add_mesh(arrow_mesh, scalars=local_arrow_colors, rgb=rgb)
            actors_list.append(last_actor)

    return actors_list


def add_edges_old(plotter, edge_mesh_list, actors_list, colors, rgb):
    for j, edge_mesh in enumerate(edge_mesh_list):
        if colors is None:
            edge_colors = np.tile([0], (len(edge_mesh.points), 1))
        else:
            edge_colors = np.tile([colors[j]], (len(edge_mesh.points), 1))
        last_actor = plotter.add_mesh(edge_mesh, scalars=edge_colors, rgb=rgb)
        actors_list.append(last_actor)
    return actors_list


def add_edges(plotter, edge_mesh_list, chunk_indices, areas_list, actors_list, colors, rgb):
    for j, edge_mesh in enumerate(edge_mesh_list):
        if colors is None:
            edge_colors = np.tile([0], (len(edge_mesh.points), 1))
        else:
            edge_colors = colors[chunk_indices[j]]#np.tile(colors[chunk_indices[j]], (len(edge_mesh.points), 1))
        area = np.mean(np.array(areas_list)[chunk_indices[j]])
        line_width = 2 * ((area / np.pi) ** .5)
        if line_width < 1:
            line_width = 1
        last_actor = plotter.add_mesh(edge_mesh, scalars=edge_colors, rgb=rgb,
                                      render_lines_as_tubes=True, line_width = line_width,
                                      style='wireframe')
        actors_list.append(last_actor)
    return actors_list