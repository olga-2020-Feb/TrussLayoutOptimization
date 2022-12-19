import numpy as np
import pyvista as pv
import vtk
from pyvista import PolyData


def numpy_to_pyvista(v,f=None):
    if f is None:
        return pv.PolyData(v)
    else:
        pyvista_faces = np.concatenate((np.full((f.shape[0], 1), 3), f), 1)
        # Pyvista supports not only triangular faces, but any general polyhedrons. As such, it needs some way to
        # differentiate between different cell types. Here we concatenated the cell qualifier (a number 3) to each
        # face in the faces array, to assert pyvista knows we are handling *triangular* faces and not anything else.
        # If we don't do this, pyvista thinks the first number in each row is the cell qualifier, and this creates
        # a segmentation fault.
        return pv.PolyData(v,pyvista_faces)

def add_arrows_copy(cent, direction,
                    length_factor = 1,
                    tip_length = None, tip_radius = None,
                    shaft_radius = None):
    """Add arrows to plotting object."""
    direction = direction.copy()
    if cent.ndim != 2:
        cent = cent.reshape((-1, 3))

    if direction.ndim != 2:
        direction = direction.reshape((-1, 3))

    direction[:,0] *= length_factor
    direction[:,1] *= length_factor
    direction[:,2] *= length_factor

    if tip_length is None:
        tip_length =  .2
    if shaft_radius is None:
        shaft_radius = .1
    if tip_radius is None:
        tip_radius = .2

    shaft_resolution = 8

    pdata = pv.vector_poly_data(cent, direction)
    # Create arrow object
    arrow = vtk.vtkArrowSource()
    arrow.SetTipLength(tip_length)
    arrow.SetTipRadius(tip_radius)
    #arrow.SetTipResolution(tip_resolution)
    arrow.SetShaftRadius(shaft_radius)
    arrow.SetShaftResolution(shaft_resolution)
    arrow.Update()
    glyph3D = vtk.vtkGlyph3D()
    glyph3D.SetSourceData(arrow.GetOutput())
    glyph3D.SetInputData(pdata)
    glyph3D.SetVectorModeToUseVector()
    glyph3D.Update()

    arrows = pv.wrap(glyph3D.GetOutput())

    return arrows

def get_tube_meshes(start, end, radii = None, speed_up_chunk_part = 0):
    mesh_list = []
    if radii is None:
        radii = [1] * len(start)

    chunk_indices = np.arange(len(radii)).reshape((-1, 1)).tolist()

    if speed_up_chunk_part > 0:
        min_radius = np.min(radii)
        max_radius = np.max(radii)
        if ((max_radius - min_radius) / speed_up_chunk_part) > 0:
            intervals = np.array(np.arange(min_radius, max_radius, (max_radius - min_radius) / speed_up_chunk_part))
        else:
            intervals = np.array([0] + [max_radius] * (speed_up_chunk_part - 1))

        sorted_radii = np.sort(radii)

        idxs_list = [np.where(sorted_radii >= intervals[i])[0][0]
                     for i in np.arange(speed_up_chunk_part)
                     if len(np.where(sorted_radii > intervals[i])[0]) > 0]

        idxs = np.unique(idxs_list)

        chunk_indices = np.split(np.argsort(radii), idxs)
        chunk_indices = [chunk for chunk in chunk_indices if len(chunk) > 0]

    for i, chunk in enumerate(chunk_indices):
        start_chunk = start[chunk]
        end_chunk = end[chunk]
        edges = np.vstack((np.array([2] * len(chunk)), np.arange(len(chunk)), np.arange(len(chunk), 2 * len(chunk)))).T
        mesh = pv.PolyData(np.vstack([start_chunk, end_chunk]), edges)
        mesh_list.append(mesh)

    # for i, (v0, v1, radius) in enumerate(zip(start, end, radii)):
    #     mesh = pv.PolyData(np.vstack([v0, v1]), np.array([2, 0, 1]))
    #     mesh_list.append(mesh)
    return mesh_list, chunk_indices

def add_tubes(p, start, end, radii = None, colors = None):

    if colors is None:
        colors = np.arange(start.shape[0])

    if radii is None:
        radii = [1] * len(start)


    rgb = len(colors.shape) > 1

    mesh_list, chunk_indices = get_tube_meshes(start, end, radii, 10)

    for i, mesh in enumerate(mesh_list):
        #edge_colors = np.tile([colors[i]], (len(mesh.points), 1))
        radius = np.mean(np.array(radii)[chunk_indices[i]])
        edge_colors = np.tile(colors[chunk_indices[i]], (len(mesh.points) // len(chunk_indices[i]), 1))
        p.add_mesh(mesh, scalars=edge_colors, rgb=rgb, render_lines_as_tubes=True,
                   style='wireframe', line_width=radius * 2)

    return p

def plot_v_f(v, f, colors = None):
    p = pv.Plotter()
    p.add_axes()
    p.set_background('white')
    pyvista_mesh = numpy_to_pyvista(v, f)
    if colors is None:
        colors = np.arange(v.shape[0])
    p.add_mesh(pyvista_mesh, scalars=colors, show_edges=True)#, style='wireframe')

    p.show(interactive = True, auto_close=False)

def plot_v_e(v, e,
             colors = None,
             line_width = None, line_widths = None,
             sphere_idxs = None, sphere_colors = None, sphere_size = None,
             arrow_idxs = None, arrow_dirs = None, arrow_colors = None, arrow_scale = None):

    p = pv.Plotter()
    p.set_background('white')

    if colors is None:
        colors = np.arange(e.shape[0])

    dists = np.sqrt(np.sum((v[e[:, 0]] - v[e[:, 1]])**2, axis=1))

    if line_widths is None:
        if line_width is None:
            line_width = calc_line_width(v, e)
        line_widths = np.repeat(line_width, len(e))

    p = add_tubes(p, v[e[:, 0]], v[e[:, 1]], line_widths / 2., colors)

    if sphere_idxs is not None:
        points_mesh = numpy_to_pyvista(v[sphere_idxs])
        if sphere_colors is None:
            sphere_colors = np.arange(sphere_idxs.shape[0])
        if sphere_size is None:
            #sphere_size = np.min(dists) // 2
            sphere_size = np.mean(dists) // 40
            if sphere_size == 0:
                sphere_size = 1
        rgb = len(sphere_colors.shape) > 1
        p.add_mesh(points_mesh, style='points', point_size=sphere_size,
                   render_points_as_spheres = True, scalars = sphere_colors, rgb=rgb)

    if arrow_idxs is not None:
        if arrow_scale is None:
            arrow_scale = calc_arrows_scale(v, arrow_dirs)
        if arrow_colors is None:
            arrow_colors = np.arange(len(arrow_idxs))
        rgb = len(arrow_colors.shape) > 1
        arrows = add_arrows_copy(v[arrow_idxs] - arrow_dirs * arrow_scale, arrow_dirs,
                                 length_factor = arrow_scale)
        arrow_colors = arrow_colors.repeat(len(arrows.vectors) // len(arrow_idxs), axis=0)
        p.add_mesh(arrows, scalars=arrow_colors, rgb=rgb)

    set_camera_settings(p, v)
    p.show(interactive = True, auto_close=False)


def calc_arrows_scale(v, arrow_dirs):
    arrow_dir_dists = np.sqrt(np.sum(arrow_dirs ** 2, axis=1))
    arrow_dir_dists_max = np.max(arrow_dir_dists)
    dists = np.max(v, axis=0) - np.min(v, axis=0)
    arrow_scale = np.min(dists) / arrow_dir_dists_max
    return arrow_scale


def calc_line_width(v, e):
    dists = np.sqrt(np.sum((v[e[:, 0]] - v[e[:, 1]]) ** 2, axis=1))
    line_width = np.min(dists) / 10.
    return line_width


def set_camera_settings(p, v):
    p.camera.position = (np.mean(v[:, 0]), np.mean(v[:, 1]),
                         np.mean(v[:, 2]) + np.max(np.sqrt(np.sum((v - np.mean(v, axis=0)) ** 2, axis=1))) * 4)
    p.camera.focal_point = np.mean(v, axis=0)
    p.camera.up = (0.0, 1.0, 0.0)
    p.camera.zoom(1.)
    p.add_axes()


def v_e_2_pyvista_mesh(v, e):
    padding = np.empty(e.shape[0], int) * 2
    padding[:] = 2
    edges_w_padding = np.vstack((padding, e.T)).T
    mesh = pv.PolyData(v, edges_w_padding)
    return mesh


