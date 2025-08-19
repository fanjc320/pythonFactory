from svgpathtools import svg2paths2
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon as MplPolygon
import numpy as np

#fill polygon with colors same to svg
def get_svg_polygons_with_colors(svg_file, tolerance=0.1):
    """
    Extract polygons with their original colors from SVG

    Args:
        svg_file (str): Path to SVG file
        tolerance (float): Approximation tolerance for curves

    Returns:
        list: List of tuples (polygon_points, fill_color, stroke_color, stroke_width)
    """
    # Load paths, attributes, and svg_attributes
    paths, attributes, svg_attributes = svg2paths2(svg_file)

    colored_polygons = []

    for path, attr in zip(paths, attributes):
        # Approximate path with line segments
        polyline = []
        for segment in path:
            if segment.length() == 0:
                continue

            n_segments = max(2, int(segment.length() / tolerance))
            for t in np.linspace(0, 1, n_segments):
                point = segment.point(t)
                polyline.append((point.real, point.imag))

        if not polyline:
            continue

        # Extract style properties
        fill_color = attr.get('fill', '#000000')  # Default black
        stroke_color = attr.get('stroke', 'none')
        stroke_width = float(attr.get('stroke-width', 1))

        # Handle 'none' and default values
        if fill_color.lower() == 'none':
            fill_color = None
        if stroke_color.lower() == 'none':
            stroke_color = None

        colored_polygons.append((polyline, fill_color, stroke_color, stroke_width))

    return colored_polygons


def plot_colored_polygons(colored_polygons, title="SVG Polygons with Original Colors"):
    """Visualize polygons with their original colors using matplotlib"""
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_title(title)

    patches = []
    colors = []

    for polygon, fill_color, stroke_color, stroke_width in colored_polygons:
        # Convert to matplotlib Polygon patch
        mpl_poly = MplPolygon(polygon, closed=True)

        # Set style properties
        if fill_color:
            mpl_poly.set_facecolor(fill_color)
        else:
            mpl_poly.set_facecolor('none')

        if stroke_color:
            mpl_poly.set_edgecolor(stroke_color)
            mpl_poly.set_linewidth(stroke_width)
        else:
            mpl_poly.set_edgecolor('none')

        patches.append(mpl_poly)

    # Add all patches at once for better performance
    ax.add_collection(PatchCollection(patches, match_original=True))

    # Set axis limits based on polygon extents
    all_points = [point for poly in colored_polygons for point in poly[0]]
    xs, ys = zip(*all_points)
    ax.set_xlim(min(xs), max(xs))
    ax.set_ylim(min(ys), max(ys))
    ax.set_aspect('equal')
    plt.gca().invert_yaxis()
    plt.show()


# Example usage
# colored_polygons = get_svg_polygons_with_colors('input.svg')
colored_polygons = get_svg_polygons_with_colors('testSVG/jimeng-little-girl.svg')
plot_colored_polygons(colored_polygons)