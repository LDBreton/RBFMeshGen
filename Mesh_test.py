import numpy as np
from RBFMeshGen import RandomMesh, plot_points, Border

def circle_parametric_function(radius, t):
    return radius * np.cos(t), radius * np.sin(t)

outer_radius = 1.0
inner_radius = 0.5

border_outer1 = Border(parametric_function=lambda t: circle_parametric_function(outer_radius, t), label=1, t_start=0, t_end=np.pi)
border_outer2 = Border(parametric_function=lambda t: circle_parametric_function(outer_radius, t), label=1, t_start=np.pi, t_end=2 * np.pi)
border_inner1 = Border(parametric_function=lambda t: circle_parametric_function(inner_radius, t), label=1, t_start=0, t_end=2 * np.pi)


random_mesh = RandomMesh(border_outer1(100),border_outer2(200), border_inner1(-100))

num_points = 10000
points = random_mesh.generate_points(num_points)
plot_points(points)
