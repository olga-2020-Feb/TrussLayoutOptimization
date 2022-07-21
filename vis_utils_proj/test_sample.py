import numpy as np
import pyvista
nodes = (np.array([
    [0, 0, 0],
    [0, 0, 1],
    [0, 1, 1],
    [0, 1, 0],
])).astype(float)
edges = np.array([
    [2, 0, 1],
    [2, 1, 2],
    [2, 2, 3],
    [2, 0, 2],
])
radii = (np.array([1, 2, 3, 4])).astype(float)
num_edges = 4

plotter = pyvista.Plotter()
mesh = pyvista.PolyData(nodes, edges)
plotter.add_mesh(mesh,
                 scalars=range(num_edges),
                 render_lines_as_tubes=True,
                 style='wireframe',
                 line_width=radii,
                 cmap='viridis',
                 show_scalar_bar=False,
                 )
plotter.show()