# deepseek python, concave polygon decomposition, 维持原来的边的走向
import numpy as np
from shapely.geometry import Polygon, LineString, MultiPolygon
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay
from testSVG.polygon import getPolygonFromPath
from common.SegmentsIntersect import segments_intersect
from common.Polygon_Segment import is_line_inside_polygon

def decompose_concave_polygon(polygon):
    """
    Decompose a concave polygon into convex parts while maintaining original edge directions.

    Args:
        polygon: A Shapely Polygon object representing the concave polygon

    Returns:
        A list of Shapely Polygon objects representing the convex decomposition
    """
    # Extract coordinates
    coords = np.array(polygon.exterior.coords)

    # Perform constrained Delaunay triangulation
    triangles = constrained_delaunay_triangulation(coords)

    # Merge triangles while preserving original edges
    convex_parts = merge_triangles_while_preserving_edges(triangles, polygon)

    return convex_parts


# def segments_intersect(a1, a2, b1, b2):
#     """判断线段a1a2和b1b2是否相交"""
#
#     def ccw(A, B, C):
#         return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
#
#     return ccw(a1, b1, b2) != ccw(a2, b1, b2) and ccw(a1, a2, b1) != ccw(a1, a2, b2)


# def triangle_in_polygon(triangle, polygon):#triangle type [(2, 2), (5, 2), (3, 5)]
#     """判断三角形是否完全在多边形内"""
#     # 检查所有顶点是否都在多边形内
#     # for point in triangle:
#     #     if not point_in_polygon(point, polygon):
#     #         return False
#
#     # 检查三角形的边是否与多边形的边相交
#     tri_edges = [(triangle[0], triangle[1]),
#                  (triangle[1], triangle[2]),
#                  (triangle[2], triangle[0])]
#
#     n = len(polygon)
#     poly_edges = [(polygon[i], polygon[(i + 1) % n]) for i in range(n)]
#
#     for tri_edge in tri_edges:
#         for poly_edge in poly_edges:
#             a = tri_edge[0]
#             b = tri_edge[1]
#             c = poly_edge[0]
#             d = poly_edge[1]
#             # print("triangle_in_polygon a:", a, "b:", b, "c:", c, "d:", d)#triangle_in_polygon a: [4. 0.] b: [2. 2.] c: [0. 0.] d: [4. 0.]
#             seg1 = (tuple(a), tuple(b))
#             seg2 = (tuple(c), tuple(d))
#
#             # if segments_intersect(a, b, c, d):
#             print('triangle_in_polygon before segments_intersect a{} b{} c{} d{}'.format(a, b, c, d))
#             if segments_intersect(seg1, seg2):
#                 print('triangle_in_polygon after segments_intersect a{} b{} c{} d{}'.format(a, b, c, d))
#                 return False
#
#     # # 可选：检查多边形是否有顶点在三角形内（针对有洞的情况）
#     # for point in polygon:
#     #     if point_in_polygon(point, triangle):
#     #         return False
#
#     return True

def triangle_in_polygon(triangle, polygon):#triangle type [(2, 2), (5, 2), (3, 5)]
    """判断三角形是否完全在多边形内"""
    # 检查所有顶点是否都在多边形内
    # for point in triangle:
    #     if not point_in_polygon(point, polygon):
    #         return False

    # 检查三角形的边是否与多边形的边相交
    tri_edges = [(triangle[0], triangle[1]),
                 (triangle[1], triangle[2]),
                 (triangle[2], triangle[0])]

    n = len(polygon)
    poly_edges = [(polygon[i], polygon[(i + 1) % n]) for i in range(n)]


    for tri_edge in tri_edges:
        print("triangle_in_polygon before tri_edge:{} polygon:{}".format(tri_edge, polygon))
        tri_edge = LineString(tri_edge)
        polygon1 = [tuple(pair) for pair in polygon]
        polygon2 = Polygon(polygon1)
        print("triangle_in_polygon after tri_edge:{} polygon:{}".format(tri_edge, polygon2))
        if not is_line_inside_polygon(tri_edge,polygon2):
            return False

    # # 可选：检查多边形是否有顶点在三角形内（针对有洞的情况）
    # for point in polygon:
    #     if point_in_polygon(point, triangle):
    #         return False

    return True

def constrained_delaunay_triangulation(coords):
    """
    Perform constrained Delaunay triangulation of a polygon.
    """
    # Remove duplicate last point (closed polygon)
    points = coords[:-1]

    # Perform standard Delaunay triangulation
    tri = Delaunay(points)

    # plt.figure(figsize=(8, 6))
    # fig, axes = plt.subplots(3, 3, sharex=True, sharey=True, figsize=(10, 8))
    fig, axes = plt.subplots(figsize=(10, 8))
    # Get triangles as polygon objects
    triangles = []
    i = 0
    for simplex in tri.simplices: # 三角形中顶点的索引 https://blog.csdn.net/ztf312/article/details/89189817
        triangle_coords = points[simplex]

        # if triangle_in_polygon(triangle_coords, points):
        if triangle_in_polygon(triangle_coords, points):
            triangles.append(Polygon(triangle_coords))

            # print("simplex:", simplex)
            print("triangle_coords:", triangle_coords)
            # print("triangles:", Polygon(triangle_coords))
            # triangles: POLYGON((4 0, 2 2, 0 0, 4 0))
            # print("triangles1:", plt.Polygon(triangle_coords))#plt.Polygon和Polygon和内容一样,都是构成三角形的三个顶点
            # triangles1: Polygon4((4, 0)...)
            # plt.gca().add_patch(plt.Polygon(triangle_coords))
            # axes[0, 0].plot(triangle_coords[:,0], triangle_coords[:,1], 'r-', label='tri')
            colors = ['red', 'green', 'yellow', 'purple', 'blue', 'orange']
            axes.plot(triangle_coords[:,0], triangle_coords[:,1], colors[i%len(colors)], label='tri')
            i=i+1

    plt.title("triangles")
    plt.show()

    return triangles


def merge_triangles_while_preserving_edges(triangles, original_polygon):
    """
    Merge adjacent triangles while preserving the original polygon edges.
    """
    # Extract original edges
    original_edges = []
    original_coords = list(original_polygon.exterior.coords)# 提取多边形中的点 https://geek-docs.com/python/python-ask-answer/738_python_extract_pointscoordinates_from_a_polygon_in_shapely.html
    for i in range(len(original_coords) - 1):
        edge = LineString([original_coords[i], original_coords[i + 1]])#https://shapely.readthedocs.io/en/stable/reference/shapely.LineString.html
        original_edges.append(edge)

    # Start with all triangles
    polygons = triangles.copy()

    # Try to merge adjacent polygons if the union is convex and doesn't violate original edges
    changed = True
    while changed:
        changed = False
        for i in range(len(polygons)):
            for j in range(i + 1, len(polygons)):
                poly1 = polygons[i]
                poly2 = polygons[j]

                # Check if polygons are adjacent
                if not poly1.touches(poly2):
                    continue

                # Try union
                union = poly1.union(poly2)

                # Handle case where union is a MultiPolygon (shouldn't happen with adjacent polys)
                if isinstance(union, MultiPolygon):
                    continue

                # Check if convex and preserves original edges
                # if is_convex(union) and preserves_original_edges(union, original_edges):
                if is_convex(union):
                    # Replace the two polygons with their union
                    polygons.pop(j)
                    polygons.pop(i)
                    polygons.append(union)
                    changed = True
                    print("is_convex preserves_original_edges true union:", union)
                    break
            if changed:
                break

    return polygons


def is_convex(polygon):
    """
    Check if a polygon is convex.
    """
    # A polygon is convex if all interior angles are less than 180 degrees
    coords = np.array(polygon.exterior.coords)
    vectors = np.diff(coords, axis=0)
    angles = []
    for i in range(len(vectors)):
        v1 = vectors[i - 1]
        v2 = vectors[i]
        cross = np.cross(v1, v2)
        angles.append(cross)

    # All crosses should have same sign for convex polygon
    if all(a >= 0 for a in angles) or all(a <= 0 for a in angles):
        return True
    return False

#fjc避免只因为边的顶点顺序不同，而产生新的边，即ab=ba
def preserves_original_edges(polygon, original_edges):
    """
    Check if the polygon preserves all original edges that it contains.
    """
    for edge in original_edges:
        if polygon.contains(edge) or polygon.covers(edge):
            # Check if this edge is in the polygon's boundary
            edge_in_boundary = False
            poly_coords = list(polygon.exterior.coords)
            for i in range(len(poly_coords) - 1):
                poly_edge = LineString([poly_coords[i], poly_coords[i + 1]])
                if poly_edge.equals(edge):
                    edge_in_boundary = True
                    print("poly_edge.equals(edge)   poly_edge:", poly_edge)
                    print("poly_edge.equals(edge)   edge:", edge)
                    break

            if not edge_in_boundary:
                return False
    return True


def plot_polygon(polygon, color='blue', alpha=0.5):
    """Plot a polygon with given color and transparency."""
    x, y = polygon.exterior.xy#https://geek-docs.com/python/python-ask-answer/738_python_extract_pointscoordinates_from_a_polygon_in_shapely.html
    plt.fill(x, y, color=color, alpha=alpha)
    # plt.plot(x, y, color='black')
    plt.plot(x, y, color='cyan')


# Example usage
if __name__ == "__main__":
    # Create a concave polygon (L-shaped)
    concave_poly = Polygon([
        # (0, 0), (2, 0), (2, 1), (1, 1), (1, 2), (0, 2)
        # (0, 0), (4, 0), (4, 1), (2, 2), (1, 4), (0, 4)
        # (0, 0), (4, 0), (4, 1), (2, 2), (1, 4), (0, 3)
        (0, 0), (4, 0), (4, 1), (2, 2), (1, 4), (0, 2)
    ])

    all_polygons = getPolygonFromPath("./testSVG/test_polygon2.svg")
    polygon_np = all_polygons[0]
    print("before polygon_np:", polygon_np)
    # concave_poly = Polygon(polygon_np)
    print("after polygon_np:", polygon_np)

    # Decompose it
    convex_parts = decompose_concave_polygon(concave_poly)

    # Plot the original and decomposed parts
    plt.figure(figsize=(10, 5))

    plt.subplot(121)
    plot_polygon(concave_poly, color='blue')
    plt.title("Original Concave Polygon")

    plt.subplot(122)
    colors = ['red', 'green', 'yellow', 'purple', 'blue', 'orange']
    for i, part in enumerate(convex_parts):
        plot_polygon(part, color=colors[i % len(colors)])
    plt.title("Convex Decomposition")

    plt.tight_layout()
    plt.show()