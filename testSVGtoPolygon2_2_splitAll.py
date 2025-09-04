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
from svgpathtools import svg2paths
import re
import math
from testSplitPolygonNew6_Split1_test1 import find_concave_vertices,draw_polygon_with_concave,main_with_split_history,threashold_set


def get_colors_from_css(svg_file):
    with open(svg_file, 'r') as f:
        svg_content = f.read()

    # 提取<style>部分
    style_match = re.search(r'<style[^>]*>(.*?)</style>', svg_content, re.DOTALL)
    if not style_match:
        return {}

    style_content = style_match.group(1)
    color_rules = {}

    # 解析CSS规则
    for rule in re.finditer(r'\.([^{]+)\s*\{\s*([^}]+)\s*\}', style_content):
        class_name = rule.group(1).strip()
        properties = rule.group(2)

        # 提取填充颜色
        fill_match = re.search(r'fill:\s*([^;]+)', properties)
        if fill_match:
            color_rules[class_name] = fill_match.group(1).strip()

    return color_rules


def get_path_classes(svg_file):
    with open(svg_file, 'r') as f:
        svg_content = f.read()

    # 提取路径及其class属性
    path_classes = {}
    for match in re.finditer(r'<path[^>]*class="([^"]+)"[^>]*>', svg_content):
        path_id = match.group(0).split('id="')[1].split('"')[0] if 'id="' in match.group(0) else None
        classes = match.group(1).split()
        path_classes[path_id or f"path_{len(path_classes)}"] = classes

    return path_classes

def extract_polygons_with_colors(svg_file, max_vertices=500, sampling_density=10):
    """
    Extract polygons with their colors from SVG
    """
    try:
        paths, attributes = svg2paths(svg_file)

        color_rules = get_colors_from_css(svg_file)
        path_classes = get_path_classes(svg_file)

        colored_polygons = []

        for i, (path, attr) in enumerate(zip(paths, attributes)):
            # Get fill color with fallback to stroke then default
            # fill_color = attr.get('fill', attr.get('stroke', '#000000'))
            path_name = attr.get('id', f'path_{i}')
            if 'id' not in attr:
                print(f"Path {i} has no ID, using generated name: {path_name}")

            cls = attr.get('class')
            # if cls is None:
            #     print(f"no class color path:{path_name}")
            #     fill_color = "#000000"
            # else:
            #     fill_color = color_rules[cls]
            fill_color = color_rules.get(cls, '#000000')
            hex_color = parse_svg_color(fill_color)
            # Convert path to polygon
            polyline = []
            for segment in path:
                # print(f"extract_polygons_with_colors segment:{segment}")
                if segment.length() == 0:
                    continue
                # Sample points based on segment length and desired density
                num_samples  = max(2, int(segment.length() * sampling_density))
                # print("extract_polygons_with_colors path:", path_name, " segment.length():", segment.length(), " n_segments:", n_segments," path_len:",path_len)
                num_samples  = 10# 从test_polygon6.svg 三条线的对比得出的经验性结论
                for t in np.linspace(0, 1, num_samples ):
                    point = segment.point(t)
                    x = round(point.real, 1)
                    y = round(point.imag, 1)
                    polyline.append((x, y))
                    # print("---- segment.point:", point, " polyline:", polyline)
            unique_polyline = []
            seen_points = set()
            for point in polyline:
                if point not in seen_points:
                    unique_polyline.append(point)
                    seen_points.add(point)
            if unique_polyline and len(unique_polyline) > 2 and hex_color:
                colored_polygons.append((unique_polyline, hex_color, path_name))
        # print(f"extract_polygons_with_colors colored_polygons:{colored_polygons}")
        return colored_polygons
    except Exception as e:
        print(f"Error processing SVG file: {e}")
        return []

def visualize_colored_polygons(colored_polygons, palette=None, title="SVG Polygons", showName = False, highlight_index = None):
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

        # 设置多边形样式
        if highlight_index is not None and i == highlight_index:
            print(f"visualize_colored_polygons highlight_index:{highlight_index} polygon:{polygon}")
            # 突出显示的多边形
            edgecolor = 'red'
            linewidth = 3
            alpha = 1.0
            # fill_color = '#FFFF00'  # 黄色突出显示
            fill_color = '#00FFFF'  # cyan突出显示
            label = f"★ HIGHLIGHT: {path_name} ({fill_color})"
        else:
            # 普通多边形
            edgecolor = 'black'
            linewidth = 0.5
            alpha = 0.7
            label = f"Polygon {i} ({fill_color})"

        x, y = zip(*polygon)
        plt.fill(x + (x[0],), y + (y[0],),
                 fill_color,
                 edgecolor=edgecolor,
                 linewidth=linewidth,
                 alpha=alpha,
                 label=label)

        if showName:
            # 在多边形中心位置显示 path_name
            center_x = sum(x) / len(x)
            center_y = sum(y) / len(y)
            plt.text(center_x, center_y, path_name,
                     fontsize=8, ha='center', va='center',
                     bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7))

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
def show_extract_svg():
    svg_file = "testSVG/jimeng-little-girl.svg"
    # svg_file = "testSVG/jimeng-little-girl_simplify2.svg"
    # svg_file = "testSVG/test_polygon6.svg"
    # colored_polygons = extract_polygons_with_colors(svg_file, 1)
    # colored_polygons = extract_polygons_with_colors(svg_file, 10)
    # colored_polygons = extract_polygons_with_colors(svg_file, 20)
    # colored_polygons = extract_polygons_with_colors(svg_file, 200)
    colored_polygons = extract_polygons_with_colors(svg_file, 20)
    print("colored_polygons type:", type(colored_polygons), " len:", len(colored_polygons))#type: <class 'list'>  len: 51
    print("colored_polygons:", colored_polygons[0][0])
    index = 5
    print("colored_polygons  00 len:", len(colored_polygons[index][0]))
    threashold_set = 150 / 180.0 * math.pi  # 弧度角
    concave_verts = find_concave_vertices(colored_polygons[index][0], threshold=threashold_set)  # 外∠更凹，外∠越小，越凹，angle就越小
    print("凹顶点索引:", concave_verts)
    print("凹顶点坐标:", [colored_polygons[index][0][i] for i in concave_verts])
    draw_polygon_with_concave(colored_polygons[index][0], concave_verts, color='skyblue', alpha=0.7)

    visualize_colored_polygons(colored_polygons, palette=[
        '#FF0000', '#FF7F00', '#FFFF00', '#7FFF00', '#00FF00',
        '#00FF7F', '#00FFFF', '#007FFF', '#0000FF', '#7F00FF'
    ], showName=True, highlight_index=4)  # Custom palette



def split_svg_all_polygons():
    global threashold_set
    svg_file = "testSVG/jimeng-little-girl.svg"
    # svg_file = "testSVG/test_polygon6.svg"
    # simplified_polygons = process_svg(svg_file, max_vertices=100)
    simplified_polygons = extract_polygons_with_colors(svg_file, max_vertices=20)
    print(f"Reduced to {len(simplified_polygons)} polygons  type:{type(simplified_polygons)}")
    for i, poly in enumerate(simplified_polygons):
        print(f"Polygon {i + 1}: {len(poly)} vertices")

    for i, (polygon, color, path_name) in enumerate(simplified_polygons):
        if i != 5: # 0-3是大块 4是一条直线 5有小的凹点，需要处理
            continue
        # print("visualize_with_similar_colors polygon type:", type(polygon), " len:", len(polygon), type(polygon[0]))

        concave_verts = find_concave_vertices(polygon, threshold=threashold_set)  # 外∠更凹，外∠越小，越凹，angle就越小
        print(">>>>>>凹顶点索引:", concave_verts)
        print(">>>>>>凹顶点坐标:", [polygon[i] for i in concave_verts])
        draw_polygon_with_concave(polygon, concave_verts, color='skyblue', alpha=0.7)

        # main_with_split_history(polygon)

if __name__ == "__main__":
    show_extract_svg()
    # split_svg_all_polygons()
