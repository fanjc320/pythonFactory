import numpy as np
import matplotlib.pyplot as plt


def smooth_bezier_connect(line1, line2, alpha=0.5):
    """
    使用三次贝塞尔曲线平滑连接两条线段，强制切线连续

    参数:
        line1: 第一条线段 [(x1, y1), (x2, y2), ...]
        line2: 第二条线段 [(x1, y1), (x2, y2), ...]
        alpha: 控制曲线紧度的参数 (0 < alpha < 1)

    返回:
        curve_points: 曲线上的点
    """
    p0 = np.array(line1[-1])  # 第一条线段的终点
    p3 = np.array(line2[0])  # 第二条线段的起点

    # 计算第一条线段在终点的切线方向
    if len(line1) >= 2:
        tangent1 = p0 - np.array(line1[-2])
    else:
        tangent1 = np.array([1, 0])  # 默认水平方向

    # 计算第二条线段在起点的切线方向
    if len(line2) >= 2:
        tangent2 = np.array(line2[1]) - p3
    else:
        tangent2 = np.array([1, 0])  # 默认水平方向

    # 归一化切线向量
    tangent1 = tangent1 / np.linalg.norm(tangent1)
    tangent2 = tangent2 / np.linalg.norm(tangent2)

    # 计算控制点位置
    distance = np.linalg.norm(p3 - p0)
    p1 = p0 + alpha * distance * tangent1  # 第一个控制点沿第一条线段切线方向
    p2 = p3 - alpha * distance * tangent2  # 第二个控制点沿第二条线段切线方向

    # 三次贝塞尔曲线公式
    t = np.linspace(0, 1, 100)
    curve_points = []
    for ti in t:
        point = (1 - ti) ** 3 * p0 + 3 * (1 - ti) ** 2 * ti * p1 + 3 * (1 - ti) * ti ** 2 * p2 + ti ** 3 * p3
        curve_points.append(point)

    return np.array(curve_points)


# 示例使用
line1 = [[0, 0], [1, 2], [2, 1.5]]  # 第一条线段
line2 = [[3, 3], [4, 1], [5, 2]]  # 第二条线段

curve = smooth_bezier_connect(line1, line2, alpha=0.3)

# 绘制结果
plt.figure(figsize=(10, 6))
plt.plot(np.array(line1)[:, 0], np.array(line1)[:, 1], 'b-o', label='Line 1')
plt.plot(np.array(line2)[:, 0], np.array(line2)[:, 1], 'g-o', label='Line 2')
plt.plot(curve[:, 0], curve[:, 1], 'r-', linewidth=2, label='Smooth Connection')
plt.axis('equal')
plt.legend()
plt.grid(True)
plt.title('G1 Continuous Bezier Connection')
plt.show()