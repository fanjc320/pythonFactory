#deepseek simplify polygons with less vertices less than 100
from svgpathtools import svg2paths
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import matplotlib
from rdp import rdp
matplotlib.use('Qt5Agg')
from testSplitPolygonNew6_StraightLineOk_manyPolys import *
def simplify_polygon(polygon, max_vertices=100, tolerance=0.1):
    """
    Simplify polygon using Douglas-Peucker algorithm and smoothing
    to reduce vertices while preserving shape.

    Args:
        polygon: List of (x,y) points
        max_vertices: Maximum allowed vertices (default: 100)
        tolerance: Simplification tolerance (higher = more simplification)

    Returns:
        Simplified polygon as list of (x,y) points
    """
    if len(polygon) <= max_vertices:
        return polygon

    # First apply smoothing to reduce noise
    x, y = zip(*polygon)
    window_size = max(3, len(polygon) // 20)  # Adaptive window size
    if window_size % 2 == 0: window_size += 1  # Ensure odd

    # Apply Savitzky-Golay smoothing
    x_smooth = signal.savgol_filter(x, window_size, 2)
    y_smooth = signal.savgol_filter(y, window_size, 2)
    smoothed = list(zip(x_smooth, y_smooth))

    # Apply Douglas-Peucker algorithm
    # from rdp import rdp
    simplified = rdp(smoothed, epsilon=tolerance)

    # If still too many points, increase tolerance and try again
    while len(simplified) > max_vertices and tolerance < 10:
        tolerance *= 1.5
        simplified = rdp(smoothed, epsilon=tolerance)

    return simplified


def process_svg(svg_file, max_vertices=100):
    """
    Process SVG file and return simplified polygons
    """
    paths, _ = svg2paths(svg_file)
    simplified_polygons = []
    print("process_svg paths numb:", len(paths))
    for path in paths:
        # Convert path to polygon
        polyline = []
        for segment in path:
            if segment.length() == 0:
                continue
            # print("process_svg path numb:", len(path), " segment.length():", segment.length())
            # for t in np.linspace(0, 1, max(2, int(segment.length() / 0.1))):
            for t in np.linspace(0, 1, max(2, int(segment.length()))):
                point = segment.point(t)
                polyline.append((point.real, point.imag))

        if polyline:
            simplified = simplify_polygon(polyline, max_vertices)
            simplified_polygons.append(simplified)

    return simplified_polygons


def visualize_polygons(polygons, title="Simplified Polygons"):
    """Visualize polygons with vertex count labels"""
    plt.figure(figsize=(10, 10))
    plt.title(title)

    for i, polygon in enumerate(polygons):
        x, y = zip(*polygon)
        plt.plot(x + (x[0],), y + (y[0],), label=f"Polygon {i + 1} ({len(polygon)} vertices)")

    plt.axis('equal')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.gca().invert_yaxis()
    # plt.show()
    plt.show(block=True)


# Install required packages:
# pip install scipy rdp

if __name__ == "__main__":
    plt.close('all')
    # Example usage
    svg_file = "testSVG/jimeng-little-girl.svg"
    simplified_polygons = process_svg(svg_file, max_vertices=100)
    print(f"Reduced to {len(simplified_polygons)} polygons")
    for i, poly in enumerate(simplified_polygons):
        print(f"Polygon {i + 1}: {len(poly)} vertices")

    visualize_polygons(simplified_polygons)

    # count = 0
    # for polygon in simplified_polygons:
    #     if count == 0:
    #         continue
    #     if count > 1:
    #         break
    #     print("visualize_with_similar_colors polygon type:", type(polygon[0]), " len:", len(polygon[0]), type(polygon[0][0]))
    #     # simplified, count, tol = rdp_simplify(complex_coords, 0.01, max_points=150)
    #     # recursive_type_compact(polygon[0])
    #     print("----------------------------------polygon[0]:", polygon[0][:5]) # [(0.0, 0.0), (0.10001068490223315, 0.0), (0.200021
    #     print("----------------------------------polygon[1]:", polygon[1][:20]) # #A043CE
    #     # print("----------------------------------polygon[2]:", polygon[2][:20])#越界了
    #     all_decompositions = recursive_split(polygon[0], angle_threshold)
    #     # print("visualize_with_similar_colors all_decompositions:", all_decompositions)
    #     print("visualize_with_similar_colors len all_decompositions:", len(all_decompositions))
    #     for i, decomposition in enumerate(all_decompositions):
    #         print(f"分解方案 {i + 1}:")
    #         plot_polygon_decomposition(decomposition, angle_threshold)
    #     ++count

