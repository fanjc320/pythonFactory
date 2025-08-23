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
    # square = [(0, 0), (0.5, 0.2), (1.5, 0.5), (2.5, 0.2), (3, 0), (3, 1), (2, 1), (2, 2), (1, 2), (1, 1), (0, 1)]
    square = [(833.0, 1600.2), (833.2, 1600.2), (833.4, 1600.2), (833.6, 1600.1), (833.8, 1600.1),
                             (834.0, 1600.1), (834.3, 1600.0), (834.5, 1600.0), (834.7, 1599.9), (834.9, 1599.9),
                             (834.9, 1599.9), (835.2, 1600.1), (835.6, 1600.3), (835.9, 1600.5), (836.2, 1600.6),
                             (836.5, 1600.7), (836.9, 1600.8), (837.2, 1600.9), (837.6, 1601.0), (838.0, 1601.1),
                             (838.0, 1601.1), (838.4, 1601.1), (838.8, 1601.2), (839.1, 1601.3), (839.5, 1601.4),
                             (839.9, 1601.5), (840.3, 1601.6), (840.6, 1601.7), (841.0, 1601.8), (841.4, 1601.9),
                             (841.4, 1601.9), (841.4, 1602.0), (841.4, 1602.2), (841.4, 1602.3), (841.3, 1602.4),
                             (841.3, 1602.5), (841.3, 1602.7), (841.3, 1602.8), (841.3, 1602.9), (841.3, 1603.0),
                             (841.3, 1603.0), (840.9, 1603.1), (840.5, 1603.3), (840.1, 1603.4), (839.7, 1603.5),
                             (839.3, 1603.6), (838.9, 1603.7), (838.5, 1603.8), (838.1, 1604.0), (837.7, 1604.1),
                             (837.7, 1604.1), (837.8, 1605.0), (838.1, 1605.8), (838.5, 1606.5), (839.0, 1607.1),
                             (839.6, 1607.8), (840.1, 1608.4), (840.6, 1609.1), (841.0, 1609.9), (841.3, 1610.8),
                             (841.3, 1610.8), (841.0, 1610.8), (840.7, 1610.8), (840.5, 1610.9), (840.2, 1610.9),
                             (840.0, 1611.0), (839.7, 1611.0), (839.4, 1611.0), (839.2, 1611.1), (838.9, 1611.1),
                             (838.9, 1611.1), (838.7, 1610.9), (838.5, 1610.7), (838.2, 1610.4), (838.0, 1610.2),
                             (837.8, 1610.0), (837.6, 1609.8), (837.4, 1609.5), (837.1, 1609.3), (836.9, 1609.1),
                             (836.9, 1609.1), (836.9, 1609.2), (836.8, 1609.3), (836.7, 1609.4), (836.6, 1609.5),
                             (836.5, 1609.6), (836.5, 1609.7), (836.4, 1609.8), (836.3, 1609.9), (836.2, 1610.0),
                             (836.2, 1610.0), (836.2, 1610.1), (836.1, 1610.1), (836.0, 1610.2), (836.0, 1610.2),
                             (835.9, 1610.3), (835.8, 1610.3), (835.7, 1610.4), (835.7, 1610.4), (835.6, 1610.5),
                             (835.6, 1610.5), (835.1, 1610.8), (834.6, 1611.1), (834.2, 1611.4), (833.8, 1611.6),
                             (833.4, 1611.8), (833.0, 1611.9), (832.5, 1611.9), (832.0, 1611.9), (831.4, 1611.8),
                             (831.4, 1611.8), (831.1, 1611.4), (830.9, 1611.0), (830.7, 1610.6), (830.4, 1610.3),
                             (830.2, 1609.9), (829.9, 1609.6), (829.6, 1609.3), (829.3, 1609.0), (828.9, 1608.7),
                             (828.9, 1608.7), (828.6, 1608.9), (828.3, 1609.1), (828.0, 1609.2), (827.7, 1609.4),
                             (827.5, 1609.6), (827.2, 1609.8), (826.9, 1610.0), (826.6, 1610.1), (826.3, 1610.3),
                             (826.3, 1610.3), (826.3, 1610.2), (826.2, 1610.2), (826.1, 1610.1), (826.0, 1610.0),
                             (826.0, 1609.9), (825.9, 1609.9), (825.8, 1609.8), (825.8, 1609.7), (825.7, 1609.6),
                             (825.7, 1609.6), (826.0, 1609.1), (826.3, 1608.5), (826.7, 1607.9), (827.0, 1607.4),
                             (827.3, 1606.8), (827.6, 1606.2), (827.9, 1605.6), (828.2, 1605.0), (828.5, 1604.4),
                             (828.5, 1604.4), (828.1, 1604.3), (827.7, 1604.2), (827.3, 1604.0), (826.9, 1603.9),
                             (826.6, 1603.7), (826.3, 1603.5), (826.0, 1603.3), (825.6, 1603.0), (825.3, 1602.7),
                             (825.3, 1602.7), (825.7, 1602.3), (826.3, 1601.9), (827.1, 1601.6), (828.0, 1601.4),
                             (828.9, 1601.2), (829.9, 1601.0), (830.8, 1600.8), (831.6, 1600.6), (832.3, 1600.4),
                             (832.3, 1600.4), (832.4, 1600.4), (832.5, 1600.4), (832.6, 1600.4), (832.6, 1600.3),
                             (832.7, 1600.3), (832.8, 1600.3), (832.8, 1600.3), (832.9, 1600.3), (833.0, 1600.2)]

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