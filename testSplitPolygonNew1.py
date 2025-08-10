import matplotlib.pyplot as plt
import numpy as np


def plot_a_type_polygon(points, title):
    points = np.array(points)
    # 闭合多边形
    closed_points = np.vstack([points, points[0]])

    plt.figure()
    plt.plot(closed_points[:, 0], closed_points[:, 1], 'b-')
    plt.fill(closed_points[:, 0], closed_points[:, 1], 'b', alpha=0.3)
    plt.title(title)
    plt.axis('equal')
    plt.show()


# 凸四边形（0个凹点）
convex_quad = [(0, 0), (2, 0), (2, 2), (0, 2)]
plot_a_type_polygon(convex_quad, "凸四边形（0个凹点）")

# 有一个凹点的五边形
concave_pentagon = [(0, 0), (2, 0), (2, 1), (1, 0.5), (0, 1)]
plot_a_type_polygon(concave_pentagon, "有一个凹点的五边形")

# 有一个凹点的六边形
concave_hexagon = [(0, 0), (2, 0), (2, 1), (1.5, 0.5), (1, 1), (0, 1)]
plot_a_type_polygon(concave_hexagon, "有一个凹点的六边形")