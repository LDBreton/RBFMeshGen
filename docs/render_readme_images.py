"""Render the geometry gallery used by the project README."""
from pathlib import Path
import math

import matplotlib.pyplot as plt
import numpy as np

from RBFMeshGen import Border, RBFMesh


OUTPUT = Path(__file__).with_name("images")
BLUE = "#2563eb"
INK = "#111827"
ACCENT = "#f97316"
MINT = "#10b981"


def circle(radius, center=(0.0, 0.0), label="boundary"):
    cx, cy = center
    return Border(
        lambda t: (cx + radius * math.cos(t), cy + radius * math.sin(t)),
        label=label,
        t_start=0,
        t_end=2 * math.pi,
    )


def save_mesh(mesh, filename, title, boundary_colors=None, limits=None):
    fig, ax = plt.subplots(figsize=(6, 4.5), layout="constrained")
    ax.set_facecolor("#f8fafc")
    ax.scatter(
        [point.x for point in mesh.Points],
        [point.y for point in mesh.Points],
        s=4,
        color=BLUE,
        alpha=0.72,
        linewidths=0,
    )
    boundary_colors = boundary_colors or {}
    for label in dict.fromkeys(point.label for point in mesh.Boundary_Points):
        points = [point for point in mesh.Boundary_Points if point.label == label]
        ax.scatter(
            [point.x for point in points],
            [point.y for point in points],
            s=10,
            color=boundary_colors.get(label, INK),
            linewidths=0,
            label=str(label),
            zorder=3,
        )
    ax.set_title(title, fontsize=15, weight="semibold", pad=12)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color("#cbd5e1")
    if limits:
        ax.set_xlim(limits[0])
        ax.set_ylim(limits[1])
    fig.savefig(OUTPUT / filename, dpi=180, facecolor="white")
    plt.close(fig)


def render_airfoil():
    def upper(t):
        y = 0.17735 * np.sqrt(t) - 0.075597 * t - 0.212836 * t**2 + 0.17363 * t**3 - 0.06254 * t**4
        return t, y

    def lower(t):
        x, y = upper(t)
        return x, -y

    mesh = RBFMesh(
        circle(0.8, (0.5, 0), "outer")(260),
        Border(upper, "airfoil", 0, 1)(220),
        Border(lower, "airfoil", 1, 0)(220),
    )
    mesh.generate_points(2400, method="halton", seed=42)
    save_mesh(mesh, "airfoil_domain.png", "Airfoil inside a circular domain",
              {"outer": INK, "airfoil": ACCENT}, ((-0.35, 1.35), (-0.88, 0.88)))


def render_overlaps():
    mesh = RBFMesh(
        circle(1, (0, 0), "A")(180),
        circle(1, (1, 0), "B")(180),
        circle(1, (0, 1), "C")(180),
    )
    mesh.generate_points(2600, method="sobol", seed=42)
    save_mesh(mesh, "overlapping_regions.png", "Overlapping regions",
              {"A": INK, "B": ACCENT, "C": MINT}, ((-1.1, 2.1), (-1.1, 2.1)))


def render_interfaces():
    mesh = RBFMesh(
        circle(1, label="outer")(180),
        circle(0.72, label="interface")(360),
        circle(0.28, label="hole")(-100),
    )
    mesh.generate_points(2400, method="halton", seed=42)
    save_mesh(mesh, "internal_interfaces.png", "Internal interface and hole",
              {"outer": INK, "interface": MINT, "hole": ACCENT},
              ((-1.08, 1.08), (-1.08, 1.08)))


if __name__ == "__main__":
    OUTPUT.mkdir(exist_ok=True)
    render_airfoil()
    render_overlaps()
    render_interfaces()
