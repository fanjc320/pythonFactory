import matplotlib
from svg.path import parse_path
from svg.path.path import Line, CubicBezier, QuadraticBezier, Arc
import numpy as np
from skimage.draw import polygon
import matplotlib.pyplot as plt
from matplotlib import pyplot as plt

matplotlib.rc("font",family='MicroSoft YaHei',weight="bold")

def path_to_polygon(path_string, npoints=100):
    path = parse_path(path_string)
    points = []
    # We'll sample the path at npoints equally spaced in terms of parameter t (from 0 to 1)
    for i in range(npoints):
        t = i / (npoints - 1.0)
        pos = path.point(t)
        points.append((pos.real, pos.imag))
    return points


try:
    from svg.path import parse_path
    from svg.path.path import Move, Line, Arc, CubicBezier, QuadraticBezier
except ImportError:
    raise ImportError("Required library 'svg.path' is missing. Install with 'pip install svg.path'")


def svg_path_to_polygons(path_string, samples_per_curve=10):
    """
    Converts an SVG path string to multiple polygons (list of vertices).
    Handles multiple subpaths separated by 'M' (move) commands.

    Args:
        path_string (str): SVG path 'd' attribute
        samples_per_curve (int): Points to sample on curved segments

    Returns:
        list: List of polygons, each being [(x1, y1), (x2, y2), ...]
    """
    path = parse_path(path_string)
    polygons = []  # Stores all polygons
    current_poly = []  # Current polygon being built

    for segment in path:
        if isinstance(segment, Move):
            # Finalize previous polygon if it has points
            if current_poly:
                polygons.append(current_poly)
                current_poly = []
            # Start new polygon at move destination
            current_poly.append((segment.end.real, segment.end.imag))
        else:
            # Add segment start if it's the first segment
            if not current_poly:
                current_poly.append((segment.start.real, segment.start.imag))

            # Handle different segment types
            if isinstance(segment, Line):
                current_poly.append((segment.end.real, segment.end.imag))
            elif isinstance(segment, (Arc, CubicBezier, QuadraticBezier)):
                for j in range(1, samples_per_curve + 1):
                    t = j / samples_per_curve
                    point = segment.point(t)
                    current_poly.append((point.real, point.imag))

    # Add last polygon if it exists
    if current_poly:
        polygons.append(current_poly)

    return polygons


def extract_svg_paths(svg_filename):
    """
    Extracts all path data ('d' attributes) from an SVG file

    Args:
        svg_filename (str): Path to SVG file

    Returns:
        list: SVG path strings found in the file
    """
    import xml.etree.ElementTree as ET

    # Parse XML and register SVG namespace
    tree = ET.parse(svg_filename)
    root = tree.getroot()
    # # ns = {'svg': 'http://www.w3.org/2000/svg'}
    # ns = {'svg': ''}
    # # Find all path elements
    # paths = []
    # # for elem in root.findall('.//svg:path', ns):
    # for elem in root.findall('.//svg:path'):
    #     print("elem:", elem)
    #     if 'd' in elem.attrib:
    #         paths.append(elem.attrib['d'])
    # return paths

    paths = []
    if root.tag.startswith('{http://www.w3.org/2000/svg}'):
        # SVG uses XML namespace
        namespace = {'svg': 'http://www.w3.org/2000/svg'}
        paths = root.findall('.//svg:path', namespace)
    else:
        # No namespace
        paths = root.findall('.//path')

    # Extract the 'd' attribute from each path
    path_data = [path.get('d') for path in paths if path.get('d') is not None]

    return path_data

def getPolygonFromPath(filePath):
    path_strings = extract_svg_paths(filePath)
    print("path_strings len:", len(path_strings))
    # 2. Convert each path to polygons
    all_polygons = []
    for path_str in path_strings:
        polygons = svg_path_to_polygons(path_str, samples_per_curve=20)
        all_polygons.extend(polygons)
    # 3. Output results
    # print(f"Found {len(all_polygons)} polygons in {filePath}")
    return all_polygons

def getPolygonGrayImgFromPath(svg_filename):
    path_strings = extract_svg_paths(svg_filename)
    print("path_strings len:", len(path_strings))
    # 2. Convert each path to polygons
    all_polygons = []
    for path_str in path_strings:
        polygons = svg_path_to_polygons(path_str, samples_per_curve=20)
        all_polygons.extend(polygons)
    # 3. Output results
    print(f"Found {len(all_polygons)} polygons in {svg_filename}")
    print("all_polygons[0]:", all_polygons[0])
    # print("all_polygons.shape:", all_polygons[0].shape)'list' object has no attribute 'shape'

    x_coords = [point[0] for point in all_polygons[0]]
    y_coords = [point[1] for point in all_polygons[0]]

    # Create a binary image with the polygon filled
    img = np.zeros((1200, 1200), dtype=np.uint8)
    rr, cc = polygon(x_coords, y_coords, img.shape)
    img[rr, cc] = 255
    return img


def plot_polygon(points):
    """可视化多边形及其拐点"""
    x, y = zip(*points)
    plt.figure()
    plt.plot(x + (x[0],), y + (y[0],), 'b-')  # 闭合多边形
    plt.plot(x, y, 'ro')  # 标记拐点
    for i, (xi, yi) in enumerate(points):
        plt.text(xi, yi, f'{i}', color='green')
    plt.axis('equal')
    plt.show()


def check_concave_convex(polygon_points):
    """检测多边形拐点的凹凸性"""
    n = len(polygon_points)
    if n < 3:
        return []

    results = []
    for i in range(n):
        p0 = polygon_points[(i - 1) % n]
        p1 = polygon_points[i]
        p2 = polygon_points[(i + 1) % n]

        # 计算叉积
        cross = (p1[0] - p0[0]) * (p2[1] - p0[1]) - (p1[1] - p0[1]) * (p2[0] - p0[0])

        if cross < 0:
            results.append((p1, "凸点"))
        elif cross > 0:
            results.append((p1, "凹点"))
        else:
            results.append((p1, "共线"))

    return results

# Usage Example
if __name__ == "__main__":
    # 1. Extract paths from SVG file
    # svg_filename = "input.svg"
    svg_filename = "test_polygon1.svg"
    # svg_filename = "./testSVG/test_polygon2.svg"
    # path_strings = extract_svg_paths(svg_filename)
    # print("path_strings len:", len(path_strings))
    # # 2. Convert each path to polygons
    # all_polygons = []
    # for path_str in path_strings:
    #     polygons = svg_path_to_polygons(path_str, samples_per_curve=20)
    #     all_polygons.extend(polygons)

    all_polygons = getPolygonFromPath(svg_filename)

    # 3. Output results
    print(f"Found {len(all_polygons)} polygons in {svg_filename}")
    for i, polygon in enumerate(all_polygons):
        print(f"\nPolygon {i + 1} with {len(polygon)} vertices:")
        for vertex in polygon:
            print(f"  ({vertex[0]:.2f}, {vertex[1]:.2f})")