import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection
from typing import List, Tuple, Union
import numpy as np


def plot_polygons(
        polygons: Union[List[List[Tuple[float, float]]], List[Tuple[float, float]]],
        fill: bool = True,
        color: Union[str, List[str]] = 'blue',
        edgecolor: Union[str, List[str]] = 'black',
        linewidth: Union[float, List[float]] = 1.0,
        alpha: float = 0.5,
        show_vertices: bool = False,
        vertex_color: str = 'red',
        vertex_size: float = 30,
        labels: Union[str, List[str], None] = None,
        title: str = 'Polygon Visualization',
        ax=None
) -> None:
    """
    Visualize one or more polygons using matplotlib.

    Parameters:
    -----------
    polygons : List of polygons, where each polygon is a list of (x, y) tuples.
               Example: [[(0,0), (1,0), (1,1), (0,1)], [(2,2), (3,2), (3,3)]]
               or a single polygon: [(0,0), (1,0), (1,1), (0,1)].
    fill : bool, whether to fill the polygons (default: True).
    color : str or list of str, fill color(s) (default: 'blue').
    edgecolor : str or list of str, border color(s) (default: 'black').
    linewidth : float or list of float, border width(s) (default: 1.0).
    alpha : float, transparency (0-1) (default: 0.5).
    show_vertices : bool, whether to mark vertices (default: False).
    vertex_color : str, color of vertex markers (default: 'red').
    vertex_size : float, size of vertex markers (default: 30).
    labels : str or list of str, labels for each polygon (default: None).
    title : str, title of the plot (default: 'Polygon Visualization').
    ax : matplotlib axis, if None creates a new figure (default: None).
    """
    # Handle single polygon input
    if not isinstance(polygons[0][0], (list, tuple)):
        polygons = [polygons]  # Convert to list of polygons

    # Convert color, edgecolor, linewidth to lists if they are not
    if isinstance(color, str):
        color = [color] * len(polygons)
    if isinstance(edgecolor, str):
        edgecolor = [edgecolor] * len(polygons)
    if isinstance(linewidth, (int, float)):
        linewidth = [linewidth] * len(polygons)

    # Create figure if ax is None
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))

    # Prepare patches for each polygon
    patches = []
    for poly in polygons:
        polygon_patch = MplPolygon(poly, closed=True)
        patches.append(polygon_patch)

    # Add patches to the axis
    collection = PatchCollection(
        patches,
        facecolor=color if fill else 'none',
        edgecolor=edgecolor,
        linewidth=linewidth,
        alpha=alpha
    )
    ax.add_collection(collection)

    # Show vertices if enabled
    if show_vertices:
        for poly in polygons:
            x, y = zip(*poly)
            ax.scatter(x, y, color=vertex_color, s=vertex_size, zorder=3)

    # Add labels if provided
    if labels is not None:
        if isinstance(labels, str):
            labels = [labels] * len(polygons)
        for poly, label in zip(polygons, labels):
            # Calculate centroid for label position
            x, y = zip(*poly)
            centroid = (sum(x) / len(x), sum(y) / len(y))
            ax.text(centroid[0], centroid[1], label, ha='center', va='center')

    # Auto-adjust axis limits
    all_points = [point for poly in polygons for point in poly]
    x, y = zip(*all_points)
    ax.set_xlim(min(x) - 0.5, max(x) + 0.5)
    ax.set_ylim(min(y) - 0.5, max(y) + 0.5)

    # Set title and equal aspect ratio
    ax.set_title(title)
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.7)

    if ax is None:
        plt.show()


# Example usage
if __name__ == "__main__":
    # Example 1: Single polygon
    # square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    square = [(0, 0), (0.5, 0.2), (1.5, 0.5), (2.5, 0.2), (3, 0), (3, 1), (2, 1), (2, 2), (1, 2), (1, 1), (0, 1)]
    plot_polygons(square, fill=True, color='skyblue', title='Single Polygon')

    # Example 2: Multiple polygons with labels
    triangle = [(2, 2), (3, 2), (2.5, 3)]
    pentagon = [(4, 1), (5, 1), (5.5, 2), (5, 3), (4, 3)]
    plot_polygons(
        [square, triangle, pentagon],
        fill=True,
        color=['skyblue', 'lightgreen', 'salmon'],
        edgecolor=['blue', 'green', 'red'],
        linewidth=[1, 2, 1.5],
        labels=['Square', 'Triangle', 'Pentagon'],
        title='Multiple Polygons'
    )

    # Example 3: Show vertices and no fill
    hexagon = [(1, 4), (2, 4.5), (3, 4), (3, 3), (2, 2.5), (1, 3)]
    plot_polygons(
        hexagon,
        fill=False,
        edgecolor='purple',
        linewidth=2,
        show_vertices=True,
        vertex_color='orange',
        title='Hexagon with Vertices'
    )

    plt.show()