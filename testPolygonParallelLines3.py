# DeepSeek python,  split polygon into many parallel line segments, direction is parallel with the short edge of OrientedboundingBox of polygon
# the image result show lines not fulfill polygon
# use method parallels is clipped, abandon rotation
# the polygon can be ringlike
import numpy as np
from shapely.geometry import Polygon, LineString, MultiLineString
from shapely.ops import unary_union

def get_obb_short_edge_direction(polygon):
    """Get the direction vector of the short edge of the OBB"""
    obb = polygon.minimum_rotated_rectangle
    coords = np.array(obb.exterior.coords)

    edges = coords[1:] - coords[:-1]
    edge_lengths = np.linalg.norm(edges, axis=1)
    short_edge_idx = np.argmin(edge_lengths[:4])
    direction = edges[short_edge_idx]
    return direction / np.linalg.norm(direction)


def generate_parallel_lines(polygon, direction, spacing=1.0):
    """
    Generate parallel lines in given direction that properly handle ring-like polygons

    Args:
        polygon: Shapely Polygon (can have holes)
        direction: Unit vector for line direction
        spacing: Distance between lines

    Returns:
        MultiLineString of clipped lines
    """
    perp_direction = np.array([-direction[1], direction[0]])

    # Get the exterior and all interiors
    exterior = polygon.exterior
    interiors = polygon.interiors

    # Create negative space polygons for holes
    hole_polygons = [Polygon(interior) for interior in interiors]

    # Calculate bounds using exterior only
    bounds = exterior.bounds
    minx, miny, maxx, maxy = bounds

    # Calculate projection range
    corners = np.array([[minx, miny], [minx, maxy], [maxx, miny], [maxx, maxy]])
    projs = np.dot(corners, perp_direction)
    min_proj, max_proj = np.min(projs), np.max(projs)

    lines = []
    current_proj = min_proj
    while current_proj <= max_proj:
        point = perp_direction * current_proj
        scale = max(maxx - minx, maxy - miny) * 100
        p1 = point - direction * scale
        p2 = point + direction * scale
        line = LineString([p1, p2])

        # First clip to exterior
        exterior_clip = line.intersection(Polygon(exterior))
        if not exterior_clip.is_empty:
            # Then subtract all holes
            final_clip = exterior_clip
            for hole in hole_polygons:
                final_clip = final_clip.difference(hole)
                if final_clip.is_empty:
                    break

            if not final_clip.is_empty:
                if final_clip.geom_type == 'LineString':
                    lines.append(final_clip)
                elif final_clip.geom_type == 'MultiLineString':
                    lines.extend(list(final_clip.geoms))

        current_proj += spacing

    return MultiLineString(lines)


def split_polygon_with_holes(polygon, spacing=1.0):
    """Main function to split polygon (with holes) with parallel lines"""
    direction = get_obb_short_edge_direction(polygon)
    return generate_parallel_lines(polygon, direction, spacing)


# Example with ring-like polygon
if __name__ == "__main__":
    from shapely.geometry import Polygon
    import matplotlib.pyplot as plt

    # Create a ring-like polygon (donut shape)
    # exterior = [(0, 0), (5, 0), (5, 5), (0, 5)]
    # interior = [(1, 1), (4, 1), (4, 4), (1, 4)]
    exterior = [(0, 0), (2, 0.5), (2.5, 3), (1, 5), (-1, 4), (-1, 2)]
    # interior = [(1, 1), (4, 1), (4, 4), (1, 4)]
    interior = [(0, 1), (2, 1), (2, 3), (0, 4)]
    ring_poly = Polygon(exterior, [interior])

    # Split the polygon
    lines = split_polygon_with_holes(ring_poly, spacing=0.4)

    # Visualization
    fig, ax = plt.subplots(figsize=(10, 8))

    # Plot polygon
    x, y = ring_poly.exterior.xy
    ax.plot(x, y, 'b-', linewidth=2, label='Exterior')
    ax.fill(x, y, 'b', alpha=0.1)

    x, y = ring_poly.interiors[0].xy
    ax.plot(x, y, 'b-', linewidth=2, label='Interior')
    ax.fill(x, y, 'w')

    # Plot split lines
    for line in lines.geoms:
        x, y = line.xy
        ax.plot(x, y, 'r-', linewidth=0.8)

    plt.axis('equal')
    plt.legend()
    plt.title('Ring-like Polygon Split by Parallel Lines')
    plt.show()