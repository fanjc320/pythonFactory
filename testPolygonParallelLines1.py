import numpy as np
from shapely.geometry import Polygon, LineString, MultiLineString
from shapely.affinity import rotate


def get_oriented_bounding_box(polygon):
    """Get the oriented bounding box of a polygon"""
    obb = polygon.minimum_rotated_rectangle
    x, y = obb.exterior.coords.xy
    corners = list(zip(x[:-1], y[:-1]))
    return corners


def get_rotation_angle(corners):
    """Calculate rotation angle from OBB corners"""
    edge_vector = np.array(corners[1]) - np.array(corners[0])
    angle = np.arctan2(edge_vector[1], edge_vector[0])
    return np.degrees(angle)


def get_obb_edge_lengths(corners):
    """Calculate lengths of OBB edges"""
    edge1 = np.linalg.norm(np.array(corners[1]) - np.array(corners[0]))
    edge2 = np.linalg.norm(np.array(corners[2]) - np.array(corners[1]))
    return edge1, edge2


def split_polygon_with_lines(polygon, spacing=1.0):
    """
    Split polygon with parallel lines along the short edge of OBB

    Args:
        polygon: Shapely Polygon
        spacing: distance between parallel lines

    Returns:
        MultiLineString of all line segments inside the polygon
    """
    # Get OBB and its properties
    obb_corners = get_oriented_bounding_box(polygon)
    angle = get_rotation_angle(obb_corners)
    edge1, edge2 = get_obb_edge_lengths(obb_corners)

    # Determine which edge is shorter and set rotation
    if edge1 < edge2:
        # Lines parallel to edge1 (original orientation)
        rotation_angle = 0
    else:
        # Lines parallel to edge2 (rotate 90 degrees)
        rotation_angle = 90

    # Total rotation needed (original angle + adjustment for short edge)
    total_angle = angle + rotation_angle

    # Rotate polygon to make splitting lines horizontal
    rotated_poly = rotate(polygon, -total_angle, origin='centroid', use_radians=False)

    # Get precise bounds of rotated polygon
    minx, miny, maxx, maxy = rotated_poly.bounds

    # Calculate required number of lines to fully cover the polygon
    height = maxy - miny
    num_lines = int(np.ceil(height / spacing)) + 1

    # Generate parallel lines (now horizontal after rotation)
    lines = []
    for i in range(num_lines):
        y = miny + i * spacing
        line = LineString([(minx - 10, y), (maxx + 10, y)])  # Extend beyond bounds
        lines.append(line)

    # Clip lines to rotated polygon
    clipped_lines = []
    for line in lines:
        intersection = rotated_poly.intersection(line)
        if not intersection.is_empty:
            if intersection.geom_type == 'LineString':
                clipped_lines.append(intersection)
            elif intersection.geom_type == 'MultiLineString':
                clipped_lines.extend(list(intersection.geoms))

    # Rotate lines back to original orientation
    final_lines = []
    for line in clipped_lines:
        rotated_back = rotate(line, total_angle, origin='centroid', use_radians=False)
        final_lines.append(rotated_back)

    return MultiLineString(final_lines)


# Example usage with visualization
if __name__ == "__main__":
    # Create a more complex sample polygon
    poly = Polygon([(0, 0), (2, 0.5), (2.5, 3), (1, 5), (-1, 4), (-1, 2)])

    # Split the polygon with lines parallel to short OBB edge
    lines = split_polygon_with_lines(poly, spacing=0.3)

    # Visualization
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 8))

    # Plot original polygon
    x, y = poly.exterior.xy
    ax.plot(x, y, 'b-', linewidth=2, label='Polygon')
    ax.fill(x, y, 'b', alpha=0.1)

    # Plot all split lines
    for line in lines.geoms:
        x, y = line.xy
        ax.plot(x, y, 'r-', linewidth=0.8)

    # Plot OBB for reference
    obb = poly.minimum_rotated_rectangle
    x, y = obb.exterior.xy
    ax.plot(x, y, 'g--', linewidth=1, label='OBB')

    plt.axis('equal')
    plt.legend()
    plt.title('Polygon Split by Parallel Lines Along OBB Short Edge')
    plt.show()