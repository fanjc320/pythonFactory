# deepseek
# fill polygon with colors [
#             '#FF0000', '#FF7F00', '#FFFF00', '#7FFF00', '#00FF00',
#             '#00FF7F', '#00FFFF', '#007FFF', '#0000FF', '#7F00FF',
#             '#FF00FF', '#FF007F', '#FF5733', '#33FF57', '#3357FF',
#             '#F033FF', '#FF33F0', '#33FFF0', '#FFD700', '#9400D3'
#         ] , approximate original color from svg file

from svgpathtools import svg2paths
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import re
# import cssutils

# def parse_svg_color(color_str):
#     """
#     Parse SVG color string into hex format
#     Supports: hex, rgb(), rgba(), named colors, and none/currentColor
#     """
#     if not color_str or color_str.lower() in ['none', 'transparent', 'currentcolor']:
#         return None
#
#     # If already in hex format
#     if re.match(r'^#([a-f0-9]{3}|[a-f0-9]{6})$', color_str, re.IGNORECASE):
#         return color_str.upper()
#
#     # Handle rgb/rgba format
#     if color_str.startswith(('rgb(', 'rgba(')):
#         try:
#             # Use cssutils to parse complex color values
#             color = cssutils.css.Color(color_str)
#             return "#%02X%02X%02X" % (color.red, color.green, color.blue)
#         except:
#             return None
#
#     # Handle named colors (basic set)
#     named_colors = {
#         'black': '#000000',
#         'white': '#FFFFFF',
#         'red': '#FF0000',
#         'green': '#00FF00',
#         'blue': '#0000FF',
#         'yellow': '#FFFF00',
#         'cyan': '#00FFFF',
#         'magenta': '#FF00FF',
#         'silver': '#C0C0C0',
#         'gray': '#808080',
#         'maroon': '#800000',
#         'olive': '#808000',
#         'purple': '#800080',
#         'teal': '#008080',
#         'navy': '#000080'
#     }
#     return named_colors.get(color_str.lower(), None)


def extract_polygons_with_colors(svg_file, tolerance=0.1):
    """
    Extract polygons with their colors from SVG
    """
    paths, attributes = svg2paths(svg_file)
    colored_polygons = []

    for path, attr in zip(paths, attributes):
        # Get fill color with fallback to stroke then default
        fill_color = attr.get('fill', attr.get('stroke', '#000000'))
        hex_color = parse_svg_color(fill_color)

        # Convert path to polygon
        polyline = []
        for segment in path:
            if segment.length() == 0:
                continue

            n_segments = max(2, int(segment.length() / tolerance))
            for t in np.linspace(0, 1, n_segments):
                point = segment.point(t)
                polyline.append((point.real, point.imag))

        if polyline and hex_color:
            colored_polygons.append((polyline, hex_color))

    return colored_polygons


def visualize_colored_polygons(colored_polygons, palette=None, title="SVG Polygons"):
    """Visualize polygons with colors"""
    plt.figure(figsize=(10, 10))
    plt.title(title)
    ax = plt.gca()

    color_palette = [
        '#FF0000', '#FF7F00', '#FFFF00', '#7FFF00', '#00FF00',
        '#00FF7F', '#00FFFF', '#007FFF', '#0000FF', '#7F00FF',
        '#FF00FF', '#FF007F', '#FF5733', '#33FF57', '#3357FF',
        '#F033FF', '#FF33F0', '#33FFF0', '#FFD700', '#9400D3'
    ] if palette is None else palette

    color_usage = defaultdict(int)

    for i, (polygon, orig_color) in enumerate(colored_polygons):
        fill_color = color_palette[i % len(color_palette)] if palette else orig_color
        color_usage[fill_color] += 1
        label = f"Polygon {i + 1} ({fill_color})"

        x, y = zip(*polygon)
        plt.fill(x + (x[0],), y + (y[0],),
                 fill_color,
                 edgecolor='black',
                 linewidth=0.5,
                 label=label)

    plt.axis('equal')
    if len(color_usage) <= 20:
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.gca().invert_yaxis()
    plt.show()


def parse_svg_color(color_str):
    """Simplified color parser without cssutils"""
    if not color_str or color_str.lower() in ['none', 'transparent']:
        return None

    # Hex colors
    if re.match(r'^#(?:[0-9a-f]{3}){1,2}$', color_str, re.IGNORECASE):
        return color_str.upper()

    # rgb() colors
    rgb_match = re.match(r'rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', color_str)
    if rgb_match:
        r, g, b = map(int, rgb_match.groups())
        return "#%02X%02X%02X" % (r, g, b)

    # Named colors (basic set)
    named_colors = {
        'black': '#000000', 'white': '#FFFFFF', 'red': '#FF0000',
        'green': '#00FF00', 'blue': '#0000FF', 'yellow': '#FFFF00',
        'cyan': '#00FFFF', 'magenta': '#FF00FF', 'silver': '#C0C0C0',
        'gray': '#808080', 'maroon': '#800000', 'olive': '#808000',
        'purple': '#800080', 'teal': '#008080', 'navy': '#000080'
    }
    return named_colors.get(color_str.lower(), '#000000')

# Install required package if needed
# pip install cssutils

# Example usage
svg_file = "testSVG/jimeng-little-girl.svg"
# colored_polygons = extract_polygons_with_colors(svg_file, 1)
# colored_polygons = extract_polygons_with_colors(svg_file, 10)
# colored_polygons = extract_polygons_with_colors(svg_file, 20)
# colored_polygons = extract_polygons_with_colors(svg_file, 200)
colored_polygons = extract_polygons_with_colors(svg_file, 20)
print("colored_polygons type:", type(colored_polygons), " len:", len(colored_polygons))#type: <class 'list'>  len: 51
# print("colored_polygons:", colored_polygons[0][0])
#extract_polygons_with_colors tolerence->len 1->5197,10->515,20->256, 200->28 变形了
print("colored_polygons  00 len:", len(colored_polygons[0][0]))

visualize_colored_polygons(colored_polygons)  # Original colors

visualize_colored_polygons(colored_polygons, palette=[
    '#FF0000', '#FF7F00', '#FFFF00', '#7FFF00', '#00FF00',
    '#00FF7F', '#00FFFF', '#007FFF', '#0000FF', '#7F00FF'
])  # Custom palette