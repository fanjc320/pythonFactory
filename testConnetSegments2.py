import numpy as np
import matplotlib.pyplot as plt


def smooth_connect_lines(line1, line2, tension=0.5):
    """使用三次贝塞尔曲线平滑连接两条线段

    参数:
        line1: 第一条线段的点集 (至少两个点)
        line2: 第二条线段的点集 (至少两个点)
        tension: 控制曲线紧密度 (0-1)

    返回:
        曲线上的点集
    """
    p0 = line1[-1]  # 第一条线段的终点
    p3 = line2[0]  # 第二条线段的起点

    # 计算第一条线段在终点的方向向量
    dir1 = p0 - line1[-2] if len(line1) > 1 else np.array([1, 0])
    # 计算第二条线段在起点的方向向量
    dir2 = line2[1] - p3 if len(line2) > 1 else np.array([1, 0])

    # 计算控制点
    dist = np.linalg.norm(p3 - p0)
    p1 = p0 + tension * dist * 0.3 * dir1 / np.linalg.norm(dir1)
    p2 = p3 - tension * dist * 0.3 * dir2 / np.linalg.norm(dir2)

    # 生成贝塞尔曲线
    t = np.linspace(0, 1, 100)
    curve = np.outer((1 - t) ** 3, p0) + \
            np.outer(3 * (1 - t) ** 2 * t, p1) + \
            np.outer(3 * (1 - t) * t ** 2, p2) + \
            np.outer(t ** 3, p3)

    return curve


# 示例使用
line1 = np.array([[0, 0], [1, 2], [2, 1]])
line2 = np.array([[3, 3], [4, 1], [5, 2]])

curve = smooth_connect_lines(line1, line2, tension=0.7)

plt.figure(figsize=(8, 6))
plt.plot(line1[:, 0], line1[:, 1], 'b-o', label='Line 1')
plt.plot(line2[:, 0], line2[:, 1], 'g-o', label='Line 2')
plt.plot(curve[:, 0], curve[:, 1], 'r-', label='Connection Curve')
plt.legend()
plt.grid(True)
plt.title('Automated Bezier Connection')
plt.show()