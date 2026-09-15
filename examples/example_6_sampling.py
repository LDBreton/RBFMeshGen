"""Compare the random, Halton, and Sobol interior sampling methods."""
import argparse
import math

import matplotlib.pyplot as plt

from RBFMeshGen import Border, RBFMesh


def main(save_path=None):
    fig, axes = plt.subplots(1, 3, figsize=(12, 4), layout='constrained')
    meshes = {}
    for ax, method in zip(axes, ('random', 'halton', 'sobol')):
        outer = Border(lambda t: (math.cos(t), math.sin(t)), 'outer', 0, 2 * math.pi)
        hole = Border(lambda t: (0.35 * math.cos(t), 0.35 * math.sin(t)), 'hole', 0, 2 * math.pi)
        mesh = RBFMesh(outer(160), hole(-80))
        mesh.generate_points(1024, method=method, seed=42)
        ax.scatter([p.x for p in mesh.Points], [p.y for p in mesh.Points], s=3, color='#2563eb')
        ax.scatter([p.x for p in mesh.Boundary_Points], [p.y for p in mesh.Boundary_Points],
                   s=5, color='#111827')
        ax.set(title=method.capitalize(), aspect='equal', xlim=(-1.05, 1.05), ylim=(-1.05, 1.05))
        ax.set_xticks([])
        ax.set_yticks([])
        meshes[method] = mesh
    fig.suptitle('1,024 interior points per method | same borders | seed=42')
    if save_path:
        fig.savefig(save_path, dpi=160)
        plt.close(fig)
    else:
        plt.show()
    return meshes


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--save', help='Save a comparison image instead of opening a window')
    main(parser.parse_args().save)
