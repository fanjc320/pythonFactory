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

def extract_polygons_with_colors(svg_file, max_vertices=500, sampling_density=10):
    """
    Extract polygons with their colors from SVG
    """
    try:
        paths, attributes = svg2paths(svg_file)
        colored_polygons = []

        for i, (path, attr) in enumerate(zip(paths, attributes)):
            # Get fill color with fallback to stroke then default
            fill_color = attr.get('fill', attr.get('stroke', '#000000'))
            path_name = attr.get('id', f'path_{i}')
            if 'id' not in attr:
                print(f"Path {i} has no ID, using generated name: {path_name}")
                # path_name = attr.get('class')
            hex_color = parse_svg_color(fill_color)

            # Convert path to polygon
            polyline = []
            for segment in path:
                if segment.length() == 0:
                    continue
                # Sample points based on segment length and desired density
                num_samples  = max(2, int(segment.length() * sampling_density))
                # print("extract_polygons_with_colors path:", path_name, " segment.length():", segment.length(), " n_segments:", n_segments," path_len:",path_len)
                num_samples  = 10# 从test_polygon6.svg 三条线的对比得出的经验性结论
                for t in np.linspace(0, 1, num_samples ):
                    point = segment.point(t)
                    # print("---- segment.point:", point)
                    x = round(point.real, 1)
                    y = round(point.imag, 1)
                    polyline.append((x, y))

            if polyline and len(polyline) > 2 and hex_color:
                colored_polygons.append((polyline, hex_color, path_name))
                #简化太严重，不平滑，暂时注释掉
                # try:
                #     simplified = simplify_polygon(polyline, max_vertices)
                #     if len(simplified) >= 3:  # Ensure it's a valid polygon
                #         colored_polygons.append((simplified, hex_color, path_name))
                #         print(f"Path {i} {len(polyline)} → {len(simplified)} vertices")
                # except Exception as e:
                #     # print(f"Error simplifying path {i}: {e}")
                #     # Fallback: use original polyline if simplification fails
                #     colored_polygons.append((polyline, hex_color, path_name))
        return colored_polygons
    except Exception as e:
        print(f"Error processing SVG file: {e}")
        return []


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

    for i, (polygon, orig_color, path_name) in enumerate(colored_polygons):
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


def simplify_polygon(polyline, max_vertices):
    """
    Simplify polygon using Douglas-Peucker algorithm or sampling
    """
    if len(polyline) <= max_vertices:
        return polyline

    # Method 1: Simple uniform sampling (fast)
    if len(polyline) > max_vertices * 2:
        # Use uniform sampling for very dense polylines
        indices = np.linspace(0, len(polyline) - 1, max_vertices, dtype=int)
        return [polyline[i] for i in indices]

    # Method 2: Douglas-Peucker algorithm (more accurate)
    try:
        from rdp import rdp
        epsilon = calculate_epsilon(polyline, max_vertices)
        return rdp(polyline, epsilon=epsilon)
    except ImportError:
        # Fallback: uniform sampling if RDP not available
        indices = np.linspace(0, len(polyline) - 1, max_vertices, dtype=int)
        return [polyline[i] for i in indices]


def calculate_epsilon(polyline, target_vertices):
    """
    Calculate appropriate epsilon for Douglas-Peucker algorithm
    """
    # Calculate bounding box dimensions
    x_coords = [p[0] for p in polyline]
    y_coords = [p[1] for p in polyline]
    bbox_width = max(x_coords) - min(x_coords)
    bbox_height = max(y_coords) - min(y_coords)

    # Use a fraction of the bounding box size
    return max(bbox_width, bbox_height) * 0.01

# Example usage
if __name__ == "__main__":
    svg_file = "testSVG/jimeng-little-girl.svg"
    # svg_file = "testSVG/test_polygon6.svg"
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