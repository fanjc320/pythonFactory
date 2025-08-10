from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from common.polygon import getPolygonFromPath


def inner_offset_to_line(polygon, distance):
    # Negative buffer (inner offset)
    offset = polygon.buffer(-distance)

    if offset.is_empty:
        # If the offset disappears, extract the skeleton (simplified)
        boundary = polygon.boundary
        return boundary  # or use a more robust skeletonization method

    # If it becomes a LineString (e.g., for thin rectangles)
    if offset.geom_type == 'LineString':
        return offset

    # If it's still a polygon, return its boundary (not ideal, but works for some cases)
    return offset.boundary


# Example usage
polygon = Polygon([(0, 0), (0, 10), (2, 10), (2, 0)])

all_polygons = getPolygonFromPath("./testSVG/test_polygon2.svg")
# all_polygons = getPolygonFromPath("./testSVG/jimeng-little-girl.svg")
polygon_np = all_polygons[0]
print("before polygon_np:", polygon_np)
polygon = Polygon(polygon_np)

distance = 150  # Larger than half the width (causes collapse)
centerline = inner_offset_to_line(polygon, distance)
print(centerline)  # Output: LINESTRING (0.5 0, 0.5 10)

def plot_polygon(polygon, color='blue', alpha=0.5):
    """Plot a polygon with given color and transparency."""
    x, y = polygon.exterior.xy#https://geek-docs.com/python/python-ask-answer/738_python_extract_pointscoordinates_from_a_polygon_in_shapely.html
    plt.fill(x, y, color=color, alpha=alpha)
    # plt.plot(x, y, color='black')
    plt.plot(x, y, color='cyan')

plt.figure(figsize=(10, 5))
# plt.subplot(121)
# plot_polygon(Polygon(points), color='blue')
plot_polygon(polygon, color='blue')########
plt.title("Original Polygon")

# plt.subplot(122)
x, y = centerline.xy
print("x,y",x,y)
plt.plot(x, y, color='red')########

plt.tight_layout()
plt.show()