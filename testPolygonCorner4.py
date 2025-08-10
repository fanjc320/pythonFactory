# deepseek python, concave polygon decomposition
from shapely.ops import triangulate
from common.polygon import getPolygonFromPath, plot_polygon
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, LineString
from common.Polygon_Segment import is_line_inside_polygon
def decompose_concave_to_convex(polygon):
    """
    Decompose a concave polygon into convex parts using triangulation.
    Returns a list of convex polygons (triangles in this case).
    """
    triangles = triangulate(polygon)
    # return [tri for tri in triangles if tri.area > 0]

    new_tris = []
    for tri in triangles:
        innterTri = True
        exterior_coords = list(tri.exterior.coords)
        exterior_edges = [(exterior_coords[i], exterior_coords[i + 1])
                          for i in range(len(exterior_coords) - 1)]
        for tri_edge in exterior_edges:
            print("decompose_concave_to_convex before tri_edge:{} polygon:{}".format(tri_edge, polygon))
            tri_edge = LineString(tri_edge)
            if not is_line_inside_polygon(tri_edge, polygon):
                innterTri = False
        if innterTri:
            new_tris.append(tri)


    return new_tris

# Example usage
points = [(0, 0), (2, 0), (1, 1), (2, 2), (0, 2)]  # Concave polygon (diamond with dent)
poly = Polygon(points)

all_polygons = getPolygonFromPath("./testSVG/test_polygon2.svg")
# all_polygons = getPolygonFromPath("./testSVG/jimeng-little-girl.svg")
polygon_np = all_polygons[0]
print("before polygon_np:", polygon_np)
concave_poly = Polygon(polygon_np)  #########
print("after polygon_np:", polygon_np)

# convex_parts = decompose_concave_to_convex(poly)
convex_parts = decompose_concave_to_convex(concave_poly)###########

for i, part in enumerate(convex_parts):
    print(f"Convex part {i+1}: {list(part.exterior.coords)}")

plt.figure(figsize=(10, 5))
plt.subplot(121)
# plot_polygon(Polygon(points), color='blue')
plot_polygon(concave_poly, color='blue')########
plt.title("Original Concave Polygon")

plt.subplot(122)
colors = ['red', 'green', 'yellow', 'purple', 'blue', 'orange']
for i, part in enumerate(convex_parts):
    plot_polygon(Polygon(part), color=colors[i % len(colors)])
plt.title("Convex Decomposition")

plt.tight_layout()
plt.show()