import numpy as np
from shapely.geometry import Polygon, LineString, MultiLineString
from shapely.ops import unary_union
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev
from typing import List

def generate_organic_stroke(polygon, max_width=0.5, min_length=3, variability=0.3):
    """
    Generate a single organic brush stroke within the polygon.

    Args:
        polygon: Shapely Polygon to fill
        max_width: Maximum width of the brush stroke
        min_length: Minimum length of the stroke
        variability: How much the stroke meanders (0-1)

    Returns:
        LineString representing the brush stroke
    """
    # Get polygon bounds and random starting point
    minx, miny, maxx, maxy = polygon.bounds
    start_point = [np.random.uniform(minx, maxx), np.random.uniform(miny, maxy)]

    # Generate control points for a smooth, organic stroke
    # num_points = int(min_length * (1 + np.random.rand()))
    num_points = int(min_length * (1 + np.random.rand())) + 1
    angles = np.cumsum(variability * np.random.randn(num_points))
    lengths = max_width * (0.5 + 0.5 * np.random.rand(num_points))

    points = [start_point]
    for i in range(1, num_points):
        dx = lengths[i] * np.cos(angles[i])
        dy = lengths[i] * np.sin(angles[i])
        points.append([points[-1][0] + dx, points[-1][1] + dy])

    # Create smooth spline through points
    points = np.array(points).T
    print("generate_organic_stroke points:", points)
    tck, u = splprep(points, u=None, s=0.0, per=0)
    u_new = np.linspace(u.min(), u.max(), 100)
    x_new, y_new = splev(u_new, tck, der=0)

    stroke = LineString(np.column_stack([x_new, y_new]))
    print("stroke:", stroke)
    return stroke


def multilinestring_to_linestrings(multi_line: MultiLineString) -> List[LineString]:
    """
    Convert a MultiLineString to a list of LineStrings.

    Args:
        multi_line: A MultiLineString geometry

    Returns:
        List of LineString objects contained in the MultiLineString
    """
    if not isinstance(multi_line, MultiLineString):
        raise TypeError("Input must be a MultiLineString")

    return list(multi_line.geoms)
def paintbrush_fill_freeform(polygon, max_width=0.5, density=1.0, max_iter=1000):
    """
    Fill polygon with organic brush strokes of controlled width.

    Args:
        polygon: Shapely Polygon to fill
        max_width: Maximum width of each brush stroke
        density: Coverage density (0-1)
        max_iter: Maximum iterations to attempt filling

    Returns:
        MultiLineString of all brush strokes
    """
    remaining_area = polygon
    strokes = []
    coverage = 0
    iterations = 0

    while coverage < density and iterations < max_iter:
        # Generate a new organic stroke
        stroke = generate_organic_stroke(polygon, max_width)

        # Create buffer around stroke to represent painted area
        stroke_area = stroke.buffer(max_width / 2, cap_style=2, join_style=2)

        # Clip to polygon and check if valid
        valid_stroke = remaining_area.intersection(stroke)
        if valid_stroke.length > max_width:  # Only keep meaningful strokes
            strokes.append(valid_stroke)
            # Subtract painted area from remaining
            remaining_area = remaining_area.difference(stroke_area)
            coverage = 1 - (remaining_area.area / polygon.area)

        iterations += 1
    # print("paintbrush_fill_freeform strokes:", strokes) # strokes 包含了multistring,会报错
    # strokes: [ < shapely.geometry.linestring.LineString
    # object
    # at
    # 0x000001AC253E7700 >, < shapely.geometry.linestring.LineString
    # object
    # at...
    # ]

    # return MultiLineString(strokes), coverage
    new_strokes = []
    for geometry in strokes:
        if geometry.geom_type == 'LineString':
            new_strokes.append(geometry)
        elif geometry.geom_type == 'MultiLineString':
            lineList = multilinestring_to_linestrings(geometry)
            new_strokes.append(lineList)
    print("paintbrush_fill_freeform new_strokes:", new_strokes)
    return MultiLineString(new_strokes), coverage
# Example usage
if __name__ == "__main__":
    # Create a sample polygon (could be ring-like)
    # exterior = [(0, 0),(2,0.5), (4,0.5), (5, 1),(6,2), (6, 5), (4, 5), (2, 6),(0,5), (-1, 4),(-1,2)]
    # interior = [(2, 2), (4, 2),(5,3), (4, 4),(3,5), (2, 4),(1,3)]
    exterior = [(0, 0), (5, 1), (6, 5), (2, 6), (-1, 4)]
    interior = [(2, 2), (4, 2), (4, 4), (2, 4)]
    # poly = Polygon(exterior, [interior])
    poly = Polygon(exterior)

    # Generate paintbrush strokes
    strokes, coverage = paintbrush_fill_freeform(
        poly,
        max_width=0.4,
        density=0.95,  # Aim for 95% coverage
        max_iter=2000
    )

    print(f"Achieved {coverage * 100:.1f}% coverage")

    # Visualization
    fig, ax = plt.subplots(figsize=(10, 8))

    # Plot polygon
    x, y = poly.exterior.xy
    ax.plot(x, y, 'k-', linewidth=2)
    if poly.interiors:
        for interior in poly.interiors:
            xi, yi = interior.xy
            ax.plot(xi, yi, 'k-', linewidth=2)

    # Plot paintbrush strokes with random colors
    colors = plt.cm.tab20(np.linspace(0, 1, len(strokes.geoms)))
    for i, stroke in enumerate(strokes.geoms):
        xs, ys = stroke.xy
        ax.plot(xs, ys, '-', color=colors[i], linewidth=1.5, alpha=0.7)

    plt.axis('equal')
    plt.title(f"Organic Paintbrush Filling (Width ≤ {0.4} units)")
    plt.show()