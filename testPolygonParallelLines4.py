# DeepSeek python,  split polygon into many parallel line segments, direction is parallel with the short edge of OrientedboundingBox of polygon
# the image result show lines not fulfill polygon
# use method parallels is clipped, abandon rotation
# the polygon can be ringlike
# fulfill polygon like paint brush
import numpy as np
from shapely.geometry import Polygon, LineString, MultiLineString, MultiPolygon
from shapely.affinity import rotate
import matplotlib.pyplot as plt


def paintbrush_fill(polygon, spacing=0.5, wiggle_amplitude=0.2, wiggle_frequency=0.5):
    """
    Create paintbrush-like strokes to fill a polygon, following its OBB orientation.

    Args:
        polygon: Shapely Polygon to fill
        spacing: Distance between stroke paths
        wiggle_amplitude: Magnitude of brush stroke variation
        wiggle_frequency: Frequency of brush stroke variation

    Returns:
        MultiLineString of paintbrush strokes
    """
    # Get oriented bounding box properties
    obb = polygon.minimum_rotated_rectangle
    coords = np.array(obb.exterior.coords)
    edges = coords[1:] - coords[:-1]
    edge_lengths = np.linalg.norm(edges, axis=1)
    short_edge_idx = np.argmin(edge_lengths[:4])
    direction = edges[short_edge_idx]
    direction = direction / np.linalg.norm(direction)

    # Calculate rotation angle to align strokes horizontally
    angle = np.degrees(np.arctan2(direction[1], direction[0]))
    rotated_poly = rotate(polygon, -angle, origin='centroid')

    # Get bounds of rotated polygon
    minx, miny, maxx, maxy = rotated_poly.bounds
    width = maxx - minx
    height = maxy - miny

    # Generate wiggly stroke paths
    strokes = []
    y = miny
    while y <= maxy:
        # Create base line
        x_points = np.linspace(minx - width * 0.2, maxx + width * 0.2, int(width * 2))

        # Add sinusoidal variation for natural brush effect
        wiggle = wiggle_amplitude * np.sin(y * wiggle_frequency * 2 * np.pi / height)
        y_points = y + wiggle * np.sin(x_points * wiggle_frequency * 2 * np.pi / width)

        # Create wiggly line
        stroke = LineString(np.column_stack([x_points, y_points]))

        # Clip to polygon
        clipped = rotated_poly.intersection(stroke)
        if not clipped.is_empty:
            if clipped.geom_type == 'LineString':
                strokes.append(clipped)
            elif clipped.geom_type == 'MultiLineString':
                strokes.extend(list(clipped.geoms))

        y += spacing

    # Rotate strokes back to original orientation
    final_strokes = []
    for stroke in strokes:
        rotated_back = rotate(stroke, angle, origin=polygon.centroid)
        final_strokes.append(rotated_back)

    return MultiLineString(final_strokes)


# Example usage with visualization
if __name__ == "__main__":
    # Create a sample polygon (could be ring-like)
    exterior = [(0, 0), (5, 1), (6, 5), (2, 6), (-1, 4)]
    interior = [(2, 2), (4, 2), (4, 4), (2, 4)]
    poly = Polygon(exterior, [interior])

    # Generate paintbrush strokes
    strokes = paintbrush_fill(poly, spacing=0.3, wiggle_amplitude=0.15, wiggle_frequency=0.8)

    # Visualization
    fig, ax = plt.subplots(figsize=(10, 8))

    # Plot polygon
    x, y = poly.exterior.xy
    ax.plot(x, y, 'k-', linewidth=2, label='Boundary')
    if poly.interiors:
        for interior in poly.interiors:
            xi, yi = interior.xy
            ax.plot(xi, yi, 'k-', linewidth=2)

    # Plot paintbrush strokes with varying transparency
    for i, stroke in enumerate(strokes.geoms):
        xs, ys = stroke.xy
        alpha = 0.3 + 0.5 * (i % 3) / 3  # Vary transparency for artistic effect
        ax.plot(xs, ys, '-', color='sienna', linewidth=1.5, alpha=alpha)

    # Add OBB for reference
    obb = poly.minimum_rotated_rectangle
    x, y = obb.exterior.xy
    ax.plot(x, y, 'b--', linewidth=1, label='OBB')

    plt.axis('equal')
    plt.legend()
    plt.title('Paintbrush-Style Polygon Filling')
    plt.show()