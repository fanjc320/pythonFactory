import numpy as np
from shapely.geometry import Polygon, LineString, MultiLineString
from shapely.affinity import rotate


def get_oriented_bounding_box(polygon):
    """Get the oriented bounding box of a polygon"""
    # Get the minimum area rectangle (oriented bounding box)
    obb = polygon.minimum_rotated_rectangle

    # Get coordinates of OBB
    x, y = obb.exterior.coords.xy

    # Get the four corners of the OBB
    corners = list(zip(x[:-1], y[:-1]))

    return corners


def get_rotation_angle(corners):
    """Calculate rotation angle from OBB corners"""
    # Get first edge vector
    edge_vector = np.array(corners[1]) - np.array(corners[0])

    # Calculate angle with x-axis
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

    # Determine which edge is shorter
    if edge1 < edge2:
        # Lines should be parallel to edge1 (no rotation needed)
        pass
    else:
        # Lines should be parallel to edge2 (rotate 90 degrees)
        angle += 90

    # Rotate polygon to align splitting lines with x-axis
    rotated_poly = rotate(polygon, -angle, origin='centroid', use_radians=False)

    # Get bounds of rotated polygon
    minx, miny, maxx, maxy = rotated_poly.bounds

    # Generate parallel lines (now horizontal after rotation)
    lines = []
    y = miny
    while y <= maxy:
        line = LineString([(minx, y), (maxx, y)])
        lines.append(line)
        y += spacing

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
        rotated_back = rotate(line, angle, origin='centroid', use_radians=False)
        final_lines.append(rotated_back)

    return MultiLineString(final_lines)


# Example usage
if __name__ == "__main__":
    # Create a sample polygon
    poly = Polygon([(0, 0), (2, 1), (3, 3), (1, 4), (-1, 2)])

    # Split the polygon with lines parallel to short OBB edge
    lines = split_polygon_with_lines(poly, spacing=0.5)

    # Visualize (requires matplotlib)
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    x, y = poly.exterior.xy
    ax.plot(x, y, 'b-', label='Polygon')

    for line in lines.geoms:
        x, y = line.xy
        ax.plot(x, y, 'r-')

    plt.axis('equal')
    plt.legend()
    plt.show()