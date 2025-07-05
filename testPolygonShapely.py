import numpy as np
from shapely.geometry import LinearRing, Polygon
import matplotlib.pyplot as plt
from  testSVG.test0 import extract_svg_paths, svg_path_to_polygons, getPolygonFromPath

# distance    = 0.2
# cap_style   = 2  # 1 (round), 2 (flat), 3 (square)
# join_style  = 2  # 1 (round), 2 (mitre), and 3 (bevel)
# mitre_limit = 5  # 默认是 5
#
# polygon_np = np.array([
#     [0, 0],
#     [0.5, 0],
#     [0.5, 0.5],
#     [1, 0.5],
#     [1, 1],
#     [0, 1],
# ])  # 这里没有闭环，可以直接输入 shapely 的 LinearRing
# print("init polygon_np:", polygon_np, " type:", type(polygon_np), " polygon_np[:,0]:" ,polygon_np[:,0])

distance    = 20
cap_style   = 20  # 1 (round), 2 (flat), 3 (square)
join_style  = 20  # 1 (round), 2 (mitre), and 3 (bevel)
mitre_limit = 50  # 默认是 5
all_polygons = getPolygonFromPath("./testSVG/test_polygon2.svg")
polygon_np = all_polygons[0]
print("before polygon_np:", polygon_np)
# polygon_np = [list(t) for t in polygon_np]
polygon_np = np.array(polygon_np)
print("after type(polygon_np):", type(polygon_np), "polygon_np:", polygon_np)
print("after polygon_np[:,0]:", polygon_np[:,0])

polygon_shapely = Polygon(LinearRing(polygon_np))
# buffer 后得到的是闭环的结果，即第一个点和最后一个点相同
polygon_dilated_np = np.array(polygon_shapely.buffer(
    distance, cap_style=cap_style, join_style=join_style, mitre_limit=mitre_limit).exterior.coords)
polygon_shrunk_np = np.array(polygon_shapely.buffer(
    -distance, cap_style=cap_style, join_style=join_style, mitre_limit=mitre_limit).exterior.coords)

# 以下用于绘图
fig, ax = plt.subplots(figsize=(8, 6), dpi=80)
ax.plot(
    np.append(polygon_np[:,0], polygon_np[0,0]),
    np.append(polygon_np[:,1], polygon_np[0,1]),
    '.-', color='b', label='original', lw=3, ms=8, mew=3)
ax.plot(
    polygon_dilated_np[:,0],
    polygon_dilated_np[:,1],
    '.-', color='orange', label=' buffer (dilated)', lw=3, ms=8, mew=3)
ax.plot(
    polygon_shrunk_np[:,0],
    polygon_shrunk_np[:,1],
    '.-', color='r', label='buffer (shrunk)', lw=3, ms=8, mew=3)
ax.axis('equal')
ax.legend(loc='lower right', fontsize=14)
plt.tight_layout()
plt.show()
