import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize


def curvature_matching_connect(line1, line2):
    """
    通过优化实现曲率匹配的连接

    参数:
        line1: 第一条线段
        line2: 第二条线段

    返回:
        曲线上的点
    """
    p0 = np.array(line1[-1])
    p3 = np.array(line2[0])

    # 计算切线方向
    if len(line1) >= 2:
        tangent1 = p0 - np.array(line1[-2])
    else:
        tangent1 = np.array([1, 0])

    if len(line2) >= 2:
        tangent2 = np.array(line2[1]) - p3
    else:
        tangent2 = np.array([1, 0])

    tangent1 = tangent1 / np.linalg.norm(tangent1)
    tangent2 = tangent2 / np.linalg.norm(tangent2)

    # 初始控制点猜测
    distance = np.linalg.norm(p3 - p0)
    initial_guess = np.concatenate([
        p0 + 0.3 * distance * tangent1,  # p1
        p3 - 0.3 * distance * tangent2  # p2
    ])

    # 优化目标函数
    def objective(control_points):
        p1 = control_points[:2]
        p2 = control_points[2:]

        # 计算连接点处的曲率
        # 贝塞尔曲线在t=0处的曲率
        k1 = 2 * np.cross(p1 - p0, p2 - 2 * p1 + p0) / (np.linalg.norm(p1 - p0) ** 3)

        # 计算第一条线段在终点的曲率
        if len(line1) >= 3:
            a = np.array(line1[-3])
            b = np.array(line1[-2])
            c = p0
            k_line1 = 2 * np.cross(b - a, c - 2 * b + a) / (np.linalg.norm(b - a) ** 3)
        else:
            k_line1 = 0

        # 计算第二条线段在起点的曲率
        if len(line2) >= 3:
            a = p3
            b = np.array(line2[1])
            c = np.array(line2[2])
            k_line2 = 2 * np.cross(b - a, c - 2 * b + a) / (np.linalg.norm(b - a) ** 3)
        else:
            k_line2 = 0

        # 目标是最小化曲率差异
        return (k1 - k_line1) ** 2 + (k1 - k_line2) ** 2

    # 优化
    result = minimize(objective, initial_guess, method='L-BFGS-B')
    p1 = result.x[:2]
    p2 = result.x[2:]

    # 生成三次贝塞尔曲线
    t = np.linspace(0, 1, 100)
    curve = np.outer((1 - t) ** 3, p0) + \
            np.outer(3 * (1 - t) ** 2 * t, p1) + \
            np.outer(3 * (1 - t) * t ** 2, p2) + \
            np.outer(t ** 3, p3)

    return curve


# 示例使用
line1 = [[0, 0], [1, 2], [2, 1.5]]
line2 = [[3, 3], [4, 1], [5, 2]]

curve = curvature_matching_connect(line1, line2)

plt.figure(figsize=(10, 6))
plt.plot(np.array(line1)[:, 0], np.array(line1)[:, 1], 'b-o', label='Line 1')
plt.plot(np.array(line2)[:, 0], np.array(line2)[:, 1], 'g-o', label='Line 2')
plt.plot(curve[:, 0], curve[:, 1], 'r-', linewidth=2, label='Optimized Connection')
plt.axis('equal')
plt.legend()
plt.grid(True)
plt.title('Curvature-Matched Connection')
plt.show()