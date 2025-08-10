import numpy as np
from skimage.morphology import skeletonize
from skimage import draw
import matplotlib.pyplot as plt
from common.polygon import getPolygonFromPath


def polygon_to_mask(polygon, shape=(100, 100)):
    """Convert polygon coordinates to binary mask"""
    mask = np.zeros(shape, dtype=np.uint8)
    coords = np.array(polygon.exterior.coords)
    # Scale coordinates to fit mask
    coords = (coords - coords.min(axis=0)) / (coords.max(axis=0) - coords.min(axis=0)) * np.array(shape)
    rr, cc = draw.polygon(coords[:, 1], coords[:, 0], shape=mask.shape)
    mask[rr, cc] = 1
    return mask

def skeleton_to_lines(skeleton):
    """Convert skeleton image to line segments"""
    from skimage.measure import find_contours
    contours = find_contours(skeleton, 0.5)
    return [contour[:, ::-1] for contour in contours]  # Convert to (x,y) format

# Example usage with Shapely polygon
from shapely.geometry import Polygon, LineString

polygon = Polygon([(0,0), (0,2), (1,2), (1,0)])  # Thin rectangle

##############################
all_polygons = getPolygonFromPath("./testSVG/test_polygon2.svg")
polygon_np = all_polygons[0]
print("before polygon_np:", polygon_np)
polygon = Polygon(polygon_np)
#############################

mask = polygon_to_mask(polygon)
skeleton = skeletonize(mask)
lines = skeleton_to_lines(skeleton)

# Convert to Shapely LineString
centerline = LineString(lines[0]) if lines else None

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
print("centerline x,y",x,y)
plt.plot(x, y, color='red')########

plt.tight_layout()
plt.show()