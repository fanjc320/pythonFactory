#DeepSeek
# polygon, split vertices into two sections as a and b equally, keeping initial order of vertices. reverse the order of vertices in b, connect vertices pairing up, so we get several line segments.
# python code
# visualize
# if the segments is longer than a fixed number, truncate it , get the new points,  they can form new edge , the new edge split the polygon into two new polygons, get them

from common.polygon import getPolygonFromPath,getFirstPolygonFromPath2
from common.InterplatePolygon import interpolate_polygon_uniformly_noscipy
from common.MyPolygon import *

def connect_polygon_vertices(vertices):
    """
    Split polygon vertices into two equal sections, reverse the second section,
    then connect corresponding vertices to form line segments.

    Args:
        vertices: List of polygon vertices in order (e.g., [(x1, y1), (x2, y2), ...])

    Returns:
        List of line segments as tuples of connected vertices
    """
    n = len(vertices)
    if n % 2 != 0:
        raise ValueError("Number of vertices must be even for equal splitting")

    # Split into two equal sections
    split_idx = n // 2
    A = vertices[:split_idx]
    B = vertices[split_idx:]

    # Reverse the second section
    B_reversed = B[::-1]

    # Pair up vertices and create line segments
    line_segments = [(A[i], B_reversed[i]) for i in range(split_idx)]

    return line_segments


def plot_polygon_and_segments(vertices, segments):
    """
    Plot the polygon and the generated line segments.

    Args:
        vertices: List of polygon vertices in order.
        segments: List of line segments as tuples of vertices.
    """
    # Extract x and y coordinates for the polygon
    polygon_x = [v[0] for v in vertices] + [vertices[0][0]]  # Close the polygon
    polygon_y = [v[1] for v in vertices] + [vertices[0][1]]

    # Create the plot
    plt.figure(figsize=(8, 8))

    # Plot the polygon
    plt.plot(polygon_x, polygon_y, 'b-o', label='Polygon Edges', linewidth=2, markersize=8)

    # Plot the vertices with labels
    for i, (x, y) in enumerate(vertices):
        plt.text(x, y, f'v{i + 1}', fontsize=12, ha='right', va='bottom')

    # Plot the line segments
    colors = ['r', 'g', 'm', 'c']  # Different colors for segments
    for i, (start, end) in enumerate(segments):
        plt.plot([start[0], end[0]], [start[1], end[1]],
                 f'{colors[i % len(colors)]}--',
                 linewidth=2,
                 label=f'Segment {i + 1}')

    # Set plot title and labels
    plt.title('Polygon with Generated Line Segments', fontsize=14)
    plt.xlabel('X-axis', fontsize=12)
    plt.ylabel('Y-axis', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=10)
    plt.axis('equal')  # Ensure equal aspect ratio

    plt.show()


# Example usage:
def test_connect_polygon_vertices():
    # Example with a hexagon (regular for simplicity)
    # n = 40
    # angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    # hexagon_vertices = [(np.cos(a), np.sin(a)) for a in angles]
    # print("hexagon_vertices:", hexagon_vertices)

    all_polygons = getPolygonFromPath("./testSVG/polygon_simple.svg")
    polygon_np = all_polygons[0]
    polygon_np.append(polygon_np[0])# make length even #[()]
    print("before polygon_np:", polygon_np, " len:", len(polygon_np))
    polygon_np_converted = [list(inner_tuple) for inner_tuple in polygon_np]# [[]]
    polygon_np_converted = np.array(polygon_np_converted)
    # print("before polygon_np_converted:", polygon_np_converted, " len:", len(polygon_np_converted))
    polygon_np_interpolate = interpolate_polygon_uniformly_noscipy(polygon_np_converted, 40)
    polygon_np_interpolate_conterback = [tuple(x) for x in polygon_np_interpolate]
    # print("before polygon_np_interpolate_conterback:", polygon_np_interpolate_conterback, " len:", len(polygon_np_interpolate_conterback))
    # polygon_np = [list(t) for t in polygon_np]
    # polygon_np = np.array(polygon_np)
    # hexagon_vertices = polygon_np
    hexagon_vertices = polygon_np_interpolate_conterback

    segments = connect_polygon_vertices(hexagon_vertices)
    # print("Hexagon line segments:")
    # for i, seg in enumerate(segments):
    #     print(f"Segment {i + 1}: {seg[0]} -- {seg[1]}")

    plot_polygon_and_segments(hexagon_vertices, segments)

    # Example with a square
    n = 4
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    square_vertices = [(np.cos(a), np.sin(a)) for a in angles]

    segments = connect_polygon_vertices(square_vertices)
    print("\nSquare line segments:")
    for i, seg in enumerate(segments):
        print(f"Segment {i + 1}: {seg[0]} -- {seg[1]}")

    plot_polygon_and_segments(square_vertices, segments)


def distance(p1, p2):
    """Calculate Euclidean distance between two points"""
    return sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def truncate_segment(p1, p2, max_length):
    """Return a new point that truncates the segment to max_length"""
    seg_length = distance(p1, p2)
    if seg_length <= max_length:
        return None

    ratio = max_length / seg_length
    new_x = p1[0] + ratio * (p2[0] - p1[0])
    new_y = p1[1] + ratio * (p2[1] - p1[1])
    return (new_x, new_y)


def split_polygon(vertices, segments, max_length):
    """Split polygon if any segment exceeds max_length"""
    new_polygons = []
    modified_vertices = vertices.copy()

    for seg in segments:
        p1, p2 = seg
        new_point = truncate_segment(p1, p2, max_length)
        if new_point:
            # Find insertion index
            idx1 = modified_vertices.index(p1)
            idx2 = modified_vertices.index(p2)

            # Determine proper insertion order
            if abs(idx1 - idx2) == 1:
                insert_idx = max(idx1, idx2)
            else:
                # Handle wrap-around case
                insert_idx = len(modified_vertices) if min(idx1, idx2) == 0 else max(idx1, idx2)

            modified_vertices.insert(insert_idx, new_point)

    if len(modified_vertices) == len(vertices):
        return [vertices]  # No splits occurred

    # Split into two polygons at the first new point
    split_idx = next(i for i, v in enumerate(modified_vertices)
                     if v not in vertices)

    poly1 = modified_vertices[split_idx:] + modified_vertices[:split_idx]
    poly2 = list(reversed(poly1))  # Other side of the split

    # Ensure polygons are closed
    if poly1[0] != poly1[-1]:
        poly1.append(poly1[0])
    if poly2[0] != poly2[-1]:
        poly2.append(poly2[0])

    return [poly1, poly2]


def visualize_polygons(polygons):
    """Visualize multiple polygons"""
    plt.figure(figsize=(8, 8))
    colors = ['b', 'r', 'g', 'm', 'c']
    print("visualize_polygons polygons:", polygons)
    for i, poly in enumerate(polygons):
        x = [p[0] for p in poly]
        y = [p[1] for p in poly]
        plt.plot(x, y, f'{colors[i % len(colors)]}-o', label=f'Polygon {i + 1}', linewidth=2)

        # Label vertices
        for j, (px, py) in enumerate(poly[:-1]):  # Skip closing point
            plt.text(px, py, f'v{j + 1}', fontsize=10, ha='right')

    plt.title('_visualize_polygons', fontsize=14)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend("fjc")
    plt.axis('equal')
    plt.show()

def visualize_polygon(poly, color='r'):##接受不闭合的，自动闭合
    """Visualize multiple polygons"""
    plt.figure(figsize=(8, 8))
    # colors = ['b', 'r', 'g', 'm', 'c']
    poly.append(poly[0])
    # for i, poly in enumerate(polygons):
    x = [p[0] for p in poly]
    y = [p[1] for p in poly]
    plt.plot(x, y, linewidth=2,color = color)
    # x = [p[0] for p in poly]
        # plt.plot(x, y, f'{colors[i % len(colors)]}-o', label=f'Polygon {i + 1}', linewidth=2)

        # Label vertices
    for j, (px, py) in enumerate(poly[:-1]):  # Skip closing point
        plt.text(px, py, f'v{j + 1}', fontsize=10, ha='right')

    plt.title('visualize_polygon', fontsize=14)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.axis('equal')
    plt.show()

# Example usage
def TestSplitPolygon_notFulfill():
    # Create a large rectangle
    vertices = [(0, 0), (4, 0), (4, 2), (0, 2)]
    polygon = getFirstPolygonFromPath2("./testSVG/polygon_simple.svg", True)
    print("polygon:", polygon)
    # segments = connect_polygon_vertices(vertices)
    segments = connect_polygon_vertices(polygon)

    print("Original segments:")
    for seg in segments:
        print(f"{seg[0]} to {seg[1]} (length: {distance(*seg):.2f})")

    max_length = 100  # Maximum allowed segment length
    # result_polygons = split_polygon(vertices, segments, max_length)
    result_polygons = split_polygon(polygon, segments, max_length)

    print(f"\nSplit into {len(result_polygons)} polygons:")
    for i, poly in enumerate(result_polygons):
        print(f"Polygon {i + 1}: {poly}")

    visualize_polygons(result_polygons)

##################################################
#######################################################
import matplotlib.pyplot as plt
import numpy as np
from math import sqrt


def connect_polygon_vertices(verticesss, max_length=None):
    """
    Split polygon vertices and connect segments, optionally truncating long segments.

    Args:
        vertices: List of polygon vertices as (x,y) tuples
        max_length: Maximum allowed segment length (None for no truncation)

    Returns:
        segments: List of line segments
        new_points: List of new points created from truncation
        new_polygons: List of new polygons formed by splitting
    """
    poly = Polygon(verticesss)
    n = len(poly.vertices)
    if n % 2 != 0:
        raise ValueError("Number of vertices must be even for equal splitting")

    split_idx = n // 2


    A = poly.vertices[:split_idx]
    B = poly.vertices[split_idx:][::-1]  # Reversed
    print("connect_polygon_vertices split_idx:", split_idx)
    segments = []
    new_points = []


    # for a, b in zip(A, B):
    mat = []
    for i, pair in enumerate(zip(A, B)):
        a = pair[0]
        b = pair[1]
        print("connect_polygon_vertices i:", i, " pair:", pair, " a:", a, " b:", b)
        dx = b[0] - a[0]
        dy = b[1] - a[1]
        length = sqrt(dx ** 2 + dy ** 2)

        if max_length and length > max_length:
            # Truncate the segment
            ratio = max_length / length
            new_point = (a[0] + dx * ratio, a[1] + dy * ratio)
            new_points.append(new_point)
            segments.append((a, new_point))
            print("connect_polygon_vertices ")
        else:
            segments.append((a, b))

    # Split original polygon if we have new points
    new_polygons = []
    if new_points:
        # Find insertion points in original vertex list
        insert_indices = []
        # for i, v in enumerate(vertices):
        #     print("connect_polygon_vertices test vertices i:", i, " vertice:", v)
        for np in new_points:
            print("connect_polygon_vertices np:", np)
            for i, (v1, v2) in enumerate(zip(vertices, vertices[1:] + [vertices[0]])):
                print("connect_polygon_vertices v1:", v1, " v2:", v2)
                if point_on_segment(np, v1, v2):# 截断出来的新点，是否在老的顶点v1和v2组成的线段上。如果在，就
                    print("connect_polygon_vertices point_on_segment i:", i, " np:", np, " v1:", v1, " v2:", v2)
                    insert_indices.append(i + 1)
                    break

        # Create new polygons
        if len(insert_indices) == 2:
            idx1, idx2 = sorted(insert_indices)
            print("connect_polygon_vertices idx1:", idx1, " idx2:", idx2)
            poly1 = vertices[:idx1] + [new_points[0]] + vertices[idx2:]
            poly2 = vertices[idx1:idx2] + [new_points[1]]
            new_polygons = [poly1, poly2]

    return segments, new_points, new_polygons


def point_on_segment(p, a, b):
    """Check if point p lies on segment a-b"""
    cross = (p[1] - a[1]) * (b[0] - a[0]) - (p[0] - a[0]) * (b[1] - a[1])
    if abs(cross) > 1e-12:
        return False

    dot = (p[0] - a[0]) * (b[0] - a[0]) + (p[1] - a[1]) * (b[1] - a[1])
    if dot < 0:
        return False

    squared_len = (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2
    if (p[0] - a[0]) ** 2 + (p[1] - a[1]) ** 2 > squared_len:
        return False

    return True


def plot_polygons(original, segments, new_points, new_polygons):
    plt.figure(figsize=(10, 10))

    # Plot original polygon
    x, y = zip(*original)
    plt.plot(x + (x[0],), y + (y[0],), 'b-o', label='Original Polygon', linewidth=2)

    # Plot vertices with labels
    for i, (xi, yi) in enumerate(original):
        plt.text(xi, yi, f'v{i + 1}', fontsize=12, ha='right', va='bottom')

    # Plot segments
    colors = ['r', 'g', 'm', 'c', 'y']
    for i, (a, b) in enumerate(segments):
        plt.plot([a[0], b[0]], [a[1], b[1]],
                 f'{colors[i % len(colors)]}--',
                 linewidth=2,
                 label=f'Segment {i + 1}')

    # Plot new points
    if new_points:
        for i, (xi, yi) in enumerate(new_points):
            plt.plot(xi, yi, 'ko', markersize=8)
            plt.text(xi, yi, f'np{i + 1}', fontsize=12, ha='left', va='top')

    # Plot new polygons
    for i, poly in enumerate(new_polygons):
        x, y = zip(*poly)
        plt.plot(x + (x[0],), y + (y[0],),
                 linestyle=[':', '-.'][i % 2],
                 linewidth=3,
                 label=f'New Polygon {i + 1}')

    plt.title('Polygon Segmentation _plot_polygons', fontsize=14)
    plt.xlabel('X-axis', fontsize=12)
    plt.ylabel('Y-axis', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=10)
    plt.axis('equal')
    plt.show()


# Example usage
if __name__ == "__main__":
    # Create a sample polygon (rectangle)
    vertices = [(0, 0), (2, 0), (2, 3), (0, 3), (0.5, 1.5)]
    colors = ['b', 'r', 'g', 'm', 'c']
    visualize_polygon(vertices)
    polygon = getFirstPolygonFromPath2("./testSVG/polygon_simple.svg", True)
    # vertices = polygon
    print("polygon:", polygon)
    # Process with max_length = 2.5
    # segments, new_points, new_polygons = connect_polygon_vertices(vertices, max_length=2.5)
    segments, new_points, new_polygons = connect_polygon_vertices(vertices, max_length=1.0)

    print("Original vertices:", vertices)
    print("Segments:")
    for i, seg in enumerate(segments):
        print(f"  {i + 1}: {seg[0]} → {seg[1]}")
    print("New points:", new_points)
    print("New polygons:",new_polygons)
    polygons_split = []
    for i, poly in enumerate(new_polygons):
        print(f"aaaa  Polygon {i + 1}: {poly}")
        # visualize_polygon(poly, f'{colors[i % len(colors)]}--')
        polygons_split.append(poly)
        # visualize_polygon(poly, colors[i % len(colors)])
    visualize_polygons(polygons_split)
    plot_polygons(vertices, segments, new_points, new_polygons)