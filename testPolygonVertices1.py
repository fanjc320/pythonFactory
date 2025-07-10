from shapely.geometry import Polygon
import numpy as np
import matplotlib.pyplot as plt
from testSVG.polygon import getPolygonFromPath, plot_polygon


# 测试
poly_points = [(0, 0), (2, 0), (2, 1), (1, 1), (1, 2), (0, 2)]
plot_polygon(poly_points)

all_polygons = getPolygonFromPath("./testSVG/test_polygon2.svg")
polygon_np = all_polygons[0]
print("before polygon_np:", polygon_np)
# polygon_np = [list(t) for t in polygon_np]
polygon_np = np.array(polygon_np)
# print("after type(polygon_np):", type(polygon_np), "polygon_np:", polygon_np)
# print("after polygon_np[:,0]:", polygon_np[:,0])
plot_polygon(polygon_np)

# 定义一个多边形
polygon = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])

# 获取所有拐点坐标
print("多边形拐点坐标:", list(polygon.exterior.coords))

# 获取拐点数量
print("拐点数量:", len(polygon.exterior.coords) - 1)  # 减去重复的起点

####################
# 测试
print("拐点凹凸性:", check_concave_convex(poly_points))
print("拐点凹凸性:", check_concave_convex(polygon_np))