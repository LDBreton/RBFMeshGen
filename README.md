# RBFMeshGen

RBFMeshGen is a Python package designed for the generation and visualization of random mesh points within specified geometric boundaries using Radial Basis Functions (RBF) and other mesh generation techniques. The package provides tools to create, manipulate, and visualize complex mesh structures effectively in Python.

## Features

- **Geometric Boundary Definitions**: Define complex boundaries using parametric functions.
- **Mesh Generation**: Generate meshes based on defined geometric borders, ensuring points adhere to specified orientations and distributions.
- **Visualization Tools**: Visualize meshes and geometric borders, supporting both individual and collective plot displays.
- **Utility Functions**: Includes utility functions to calculate mesh orientations and handle geometric calculations.

## Installation

To install RBFMeshGen, simply clone this repository and use the setup file to install the package:

```bash
pip install RBFMeshGen
```


## Usage

```python
import numpy as np
from RBFMeshGen import RandomMesh, plot_mesh, Border


# Define a parametric function for a circle
def circle_parametric_function(radius, t):
    return radius * np.cos(t), radius * np.sin(t)


# Define the borders of the mesh
outer_radius = 1.0
inner_radius = 0.5

border_outer1 = Border(parametric_function=lambda t: circle_parametric_function(outer_radius, t), label=1, t_start=0,
                       t_end=np.pi)
border_outer2 = Border(parametric_function=lambda t: circle_parametric_function(outer_radius, t), label=1,
                       t_start=np.pi, t_end=2 * np.pi)
border_inner1 = Border(parametric_function=lambda t: circle_parametric_function(inner_radius, t), label=1, t_start=0,
                       t_end=2 * np.pi)

# Generate a random mesh
random_mesh = RandomMesh(border_outer1(100), border_outer2(200), border_inner1(-100))

# Generate points
num_points = 10000
random_mesh.generate_points(num_points)

# Plot the points
plot_mesh(random_mesh)
```

![Output Mesh Visualization](docs/images/Example_1.png)

## Contributing

Contributions to RBFMeshGen are welcome! Please feel free to fork the repository, make changes, and submit pull requests. You can also open issues to discuss potential changes or report bugs.

## License
RBFMeshGen is released under the MIT License. See the LICENSE file in the repository for full details.


