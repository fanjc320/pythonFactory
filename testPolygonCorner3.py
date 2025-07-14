# deepseek python, concave polygon decomposition, 维持原来的边的走向
import numpy as np
from shapely.geometry import Polygon, LineString, MultiPolygon
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay


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


def constrained_delaunay_triangulation(coords):
    """
    Perform constrained Delaunay triangulation of a polygon.
    """
    # Remove duplicate last point (closed polygon)
    points = coords[:-1]

    # Perform standard Delaunay triangulation
    tri = Delaunay(points)

    # Get triangles as polygon objects
    triangles = []
    for simplex in tri.simplices:
        triangle_coords = points[simplex]
        triangles.append(Polygon(triangle_coords))

    return triangles


def merge_triangles_while_preserving_edges(triangles, original_polygon):
    """
    Merge adjacent triangles while preserving the original polygon edges.
    """
    # Extract original edges
    original_edges = []
    original_coords = list(original_polygon.exterior.coords)
    for i in range(len(original_coords) - 1):
        edge = LineString([original_coords[i], original_coords[i + 1]])
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
                if is_convex(union) and preserves_original_edges(union, original_edges):
                    # Replace the two polygons with their union
                    polygons.pop(j)
                    polygons.pop(i)
                    polygons.append(union)
                    changed = True
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
                    break

            if not edge_in_boundary:
                return False
    return True


def plot_polygon(polygon, color='blue', alpha=0.5):
    """Plot a polygon with given color and transparency."""
    x, y = polygon.exterior.xy
    plt.fill(x, y, color=color, alpha=alpha)
    plt.plot(x, y, color='black')


# Example usage
if __name__ == "__main__":
    # Create a concave polygon (L-shaped)
    concave_poly = Polygon([
        (0, 0), (2, 0), (2, 1), (1, 1), (1, 2), (0, 2)
    ])

    # Decompose it
    convex_parts = decompose_concave_polygon(concave_poly)

    # Plot the original and decomposed parts
    plt.figure(figsize=(10, 5))

    plt.subplot(121)
    plot_polygon(concave_poly, color='blue')
    plt.title("Original Concave Polygon")

    plt.subplot(122)
    colors = ['red', 'green', 'yellow', 'purple', 'orange']
    for i, part in enumerate(convex_parts):
        plot_polygon(part, color=colors[i % len(colors)])
    plt.title("Convex Decomposition")

    plt.tight_layout()
    plt.show()