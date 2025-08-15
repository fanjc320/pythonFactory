import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

# 两条断开的曲线
x1 = np.linspace(0, 2, 10)
y1 = np.sin(x1)

x2 = np.linspace(3, 5, 10)
y2 = np.cos(x2)

# 曲线1的终点 (P0) 和曲线2的起点 (P3)
P0 = np.array([x1[-1], y1[-1]])
P3 = np.array([x2[0], y2[0]])

# 控制点 P1 和 P2（沿切线方向延伸）
P1 = P0 + 0.5 * np.array([1, 1])  # 沿曲线1的切线方向
P2 = P3 - 0.5 * np.array([1, -1]) # 沿曲线2的切线方向

# 生成贝塞尔曲线（三次）
t = np.linspace(0, 1, 100)
x_bezier = (1-t)**3 * P0[0] + 3*(1-t)**2*t * P1[0] + 3*(1-t)*t**2 * P2[0] + t**3 * P3[0]
y_bezier = (1-t)**3 * P0[1] + 3*(1-t)**2*t * P1[1] + 3*(1-t)*t**2 * P2[1] + t**3 * P3[1]

# 绘图
plt.figure(figsize=(8, 4))
plt.plot(x1, y1, 'r-', label='Curve 1')
plt.plot(x2, y2, 'b-', label='Curve 2')
plt.plot(x_bezier, y_bezier, 'g--', label='Bezier Bridge')
plt.scatter([P0[0], P3[0]], [P0[1], P3[1]], c='black', s=50, label='Endpoints')
plt.scatter([P1[0], P2[0]], [P1[1], P2[1]], c='orange', s=50, label='Control Points')
plt.legend()
plt.title("Smooth Connection with Bezier Curve (C1 Continuity)")
plt.show()


from scipy.interpolate import make_interp_spline

# 合并两条曲线的点（中间插入过渡点）
points = np.vstack([
    np.column_stack([x1, y1]),
    np.column_stack([x_bridge, y_bridge]),  # 过渡点
    np.column_stack([x2, y2])
])

# 参数化（按累积弦长）
t = np.arange(len(points))

# 构建 B 样条
spline = make_interp_spline(t, points, k=3)  # 三次样条
t_smooth = np.linspace(0, t[-1], 200)
points_smooth = spline(t_smooth)

# 绘图
plt.plot(points[:, 0], points[:, 1], 'ro', label='Control Points')
plt.plot(points_smooth[:, 0], points_smooth[:, 1], 'b-', label='B-Spline Bridge')
plt.legend()
plt.title("B-Spline Smooth Transition")
plt.show()