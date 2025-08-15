from svgpathtools import svg2paths
import numpy as np
#deepseek python, svg file to polygons
# visualize


def svg_to_polygons(svg_file, tolerance=0.1):
    """
    Convert SVG paths to polygons with a given tolerance for approximation.

    Args:
        svg_file (str): Path to SVG file
        tolerance (float): Maximum allowed error when approximating curves with line segments

    Returns:
        list: List of polygons, where each polygon is a list of (x, y) coordinate tuples
    """
    # Load paths and attributes from SVG file
    paths, attributes = svg2paths(svg_file)

    polygons = []

    for path in paths:
        # Approximate the path with line segments
        polyline = []
        for segment in path:
            if segment.length() == 0:
                continue

            # Number of line segments to approximate this curve segment
            n_segments = max(2, int(segment.length() / tolerance))

            # Sample points along the segment
            for t in np.linspace(0, 1, n_segments):
                point = segment.point(t)
                polyline.append((point.real, point.imag))

        if polyline:
            polygons.append(polyline)

    return polygons


import matplotlib.pyplot as plt


def plot_polygons(polygons, title="SVG Polygons"):
    """Plot polygons using matplotlib"""
    plt.figure(figsize=(8, 8))
    plt.title(title)

    for i, polygon in enumerate(polygons):
        # Unzip x and y coordinates
        x, y = zip(*polygon)
        plt.plot(x + (x[0],), y + (y[0],), label=f"Polygon {i + 1}")

    plt.axis('equal')
    plt.gca().invert_yaxis()
    plt.legend()
    plt.grid(True)
    plt.show()


# Example usage (after extracting polygons)
# Example usage
# polygons = svg_to_polygons('input.svg')
polygons = svg_to_polygons('testSVG/jimeng-little-girl.svg')
plot_polygons(polygons)
for i, polygon in enumerate(polygons):
    print(f"Polygon {i + 1} has {len(polygon)} points")