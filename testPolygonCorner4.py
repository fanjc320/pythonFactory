# deepseek python, concave polygon decomposition
from shapely.geometry import Polygon
from shapely.ops import triangulate
from testSVG.polygon import getPolygonFromPath, plot_polygon
import matplotlib.pyplot as plt
def decompose_concave_to_convex(polygon):
    """
    Decompose a concave polygon into convex parts using triangulation.
    Returns a list of convex polygons (triangles in this case).
    """
    triangles = triangulate(polygon)
    return [tri for tri in triangles if tri.area > 0]

# Example usage
points = [(0, 0), (2, 0), (1, 1), (2, 2), (0, 2)]  # Concave polygon (diamond with dent)
poly = Polygon(points)
convex_parts = decompose_concave_to_convex(poly)

for i, part in enumerate(convex_parts):
    print(f"Convex part {i+1}: {list(part.exterior.coords)}")

plt.figure(figsize=(10, 5))
plt.subplot(121)
plot_polygon(Polygon(points), color='blue')
plt.title("Original Concave Polygon")

plt.subplot(122)
colors = ['red', 'green', 'yellow', 'purple', 'blue', 'orange']
for i, part in enumerate(convex_parts):
    plot_polygon(Polygon(part), color=colors[i % len(colors)])
plt.title("Convex Decomposition")

plt.tight_layout()
plt.show()