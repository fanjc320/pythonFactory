# DeepSeek python,  split polygon into many parallel line segments, direction is parallel with the short edge of OrientedboundingBox of polygon
# the image result show lines not fulfill polygon
# use method parallels is clipped, abandon rotation
import numpy as np
from shapely.geometry import Polygon, LineString, MultiLineString
from shapely.ops import clip_by_rect


def get_obb_short_edge_direction(polygon):
    """Get the direction vector of the short edge of the OBB"""
    obb = polygon.minimum_rotated_rectangle
    coords = np.array(obb.exterior.coords)

    # Get all edge vectors
    edges = coords[1:] - coords[:-1]
    edge_lengths = np.linalg.norm(edges, axis=1)

    # Find the shortest edge
    short_edge_idx = np.argmin(edge_lengths[:4])  # Only check first 4 edges
    direction = edges[short_edge_idx]
    return direction / np.linalg.norm(direction)  # Return unit vector


def generate_parallel_lines(polygon, direction, spacing=1.0):
    """
    Generate parallel lines in given direction that cover the polygon

    Args:
        polygon: Shapely Polygon
        direction: Unit vector for line direction
        spacing: Distance between lines

    Returns:
        MultiLineString of clipped lines
    """
    # Get perpendicular direction for line spacing
    perp_direction = np.array([-direction[1], direction[0]])

    # Get bounds and calculate coverage needed
    bounds = polygon.bounds
    minx, miny, maxx, maxy = bounds

    # Calculate projection of bounds corners onto perpendicular direction
    corners = np.array([[minx, miny], [minx, maxy], [maxx, miny], [maxx, maxy]])
    projs = np.dot(corners, perp_direction)
    min_proj, max_proj = np.min(projs), np.max(projs)

    # Generate lines
    lines = []
    current_proj = min_proj
    while current_proj <= max_proj:
        # Calculate point on line
        point = perp_direction * current_proj

        # Create line through point in direction
        # Make line long enough to cover polygon (100x bounds size)
        scale = max(maxx - minx, maxy - miny) * 100
        p1 = point - direction * scale
        p2 = point + direction * scale
        line = LineString([p1, p2])

        # Clip line to polygon bounds first (optimization)
        clipped = clip_by_rect(line, minx, miny, maxx, maxy)
        if not clipped.is_empty:
            # Then clip to actual polygon
            final_clip = polygon.intersection(clipped)
            if not final_clip.is_empty:
                if final_clip.geom_type == 'LineString':
                    lines.append(final_clip)
                elif final_clip.geom_type == 'MultiLineString':
                    lines.extend(list(final_clip.geoms))

        current_proj += spacing

    return MultiLineString(lines)


def split_polygon_parallel_to_short_edge(polygon, spacing=1.0):
    """Main function to split polygon with parallel lines along OBB short edge"""
    direction = get_obb_short_edge_direction(polygon)
    return generate_parallel_lines(polygon, direction, spacing)


# Example usage and visualization
if __name__ == "__main__":
    from shapely.geometry import Polygon
    import matplotlib.pyplot as plt

    # Create a sample polygon
    poly = Polygon([(0, 0), (2, 0.5), (2.5, 3), (1, 5), (-1, 4), (-1, 2)])

    # Split the polygon
    lines = split_polygon_parallel_to_short_edge(poly, spacing=0.3)

    # Visualization
    fig, ax = plt.subplots(figsize=(10, 8))

    # Plot polygon
    x, y = poly.exterior.xy
    ax.plot(x, y, 'b-', linewidth=2, label='Polygon')
    ax.fill(x, y, 'b', alpha=0.1)

    # Plot split lines
    for line in lines.geoms:
        x, y = line.xy
        ax.plot(x, y, 'r-', linewidth=0.8)

    # Plot OBB for reference
    obb = poly.minimum_rotated_rectangle
    x, y = obb.exterior.xy
    ax.plot(x, y, 'g--', linewidth=1, label='OBB')

    plt.axis('equal')
    plt.legend()
    plt.title('Polygon Split by Parallel Lines (No Rotation Method)')
    plt.show()