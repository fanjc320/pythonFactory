import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline


def bspline_connect(line1, line2, smoothness=0.1):
    """
    使用B样条曲线实现高阶连续性连接

    参数:
        line1: 第一条线段
        line2: 第二条线段
        smoothness: 平滑系数

    返回:
        曲线上的点
    """
    # 提取连接点附近的点
    if len(line1) > 2:
        prev_points = line1[-3:]
    else:
        prev_points = line1[-2:] if len(line1) > 1 else [line1[-1], line1[-1] + [1, 0]]

    if len(line2) > 2:
        next_points = line2[:3]
    else:
        next_points = line2[:2] if len(line2) > 1 else [line2[0], line2[0] + [1, 0]]

    # 创建控制点集
    control_points = np.vstack([prev_points, next_points])

    # 创建参数化值
    u = np.linspace(0, 1, len(control_points))

    # 创建B样条 - 使用3次样条（奇数阶）
    spline = make_interp_spline(u, control_points, k=3)  # 改为k=3

    # 生成曲线点
    u_new = np.linspace(u[0], u[-1], 100)
    curve = spline(u_new)

    # 只保留连接部分
    start_idx = len(prev_points) - 1
    end_idx = start_idx + 1
    u_connect = np.linspace(u[start_idx], u[end_idx], 100)
    curve_connect = spline(u_connect)

    return curve_connect


# 示例使用
line1 = np.array([[0, 0], [1, 2], [2, 1.5]])
line2 = np.array([[3, 3], [4, 1], [5, 2]])

curve = bspline_connect(line1, line2, smoothness=0.2)

plt.figure(figsize=(10, 6))
plt.plot(line1[:, 0], line1[:, 1], 'b-o', label='Line 1')
plt.plot(line2[:, 0], line2[:, 1], 'g-o', label='Line 2')
plt.plot(curve[:, 0], curve[:, 1], 'r-', linewidth=2, label='B-spline Connection')
plt.axis('equal')
plt.legend()
plt.grid(True)
plt.title('B-spline Curve (C2 Continuous)')
plt.show()