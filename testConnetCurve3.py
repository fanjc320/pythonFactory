import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

# 两条断开的曲线
x1 = np.linspace(0, 2, 10)
y1 = np.sin(x1)

x2 = np.linspace(3, 5, 10)  # 与 x1 无交集
y2 = np.cos(x2)

# 定义过渡点：从曲线1的终点到曲线2的起点线性插值
x_bridge = np.linspace(x1[-1], x2[0], 3)  # 在 x1[-1] 和 x2[0] 之间插值3个点
y_bridge = np.linspace(y1[-1], y2[0], 3)  # 在 y1[-1] 和 y2[0] 之间插值3个点

# 合并所有点
x_combined = np.concatenate([x1, x_bridge, x2])
y_combined = np.concatenate([y1, y_bridge, y2])

# 使用 CubicSpline 平滑连接
cs = CubicSpline(x_combined, y_combined, bc_type='natural')
x_smooth = np.linspace(0, 5, 200)
y_smooth = cs(x_smooth)

# 绘图
plt.figure(figsize=(8, 4))
plt.plot(x1, y1, 'ro', label='Curve 1')
plt.plot(x2, y2, 'bo', label='Curve 2')
plt.plot(x_smooth, y_smooth, 'g-', label='Smooth Bridge')
plt.legend()
plt.title("Smoothly Bridging Disconnected Curves (Cubic Spline)")
plt.show()