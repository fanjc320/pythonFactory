import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline, make_interp_spline

# 假设有两条曲线段 (x1, y1) 和 (x2, y2)
x1 = np.linspace(0, 2, 10)
y1 = np.sin(x1)

x2 = np.linspace(2, 4, 10)  # 确保 x2[0] = x1[-1] 才能连接
y2 = np.cos(x2)

# 合并曲线并确保平滑连接
x_combined = np.concatenate([x1, x2[1:]])  # 避免重复点
y_combined = np.concatenate([y1, y2[1:]])

# 使用 CubicSpline 自动保证 C² 连续
cs = CubicSpline(x_combined, y_combined, bc_type='natural')  # 'natural' 或 'clamped'

# 生成更密集的点用于绘图
x_smooth = np.linspace(0, 4, 100)
y_smooth = cs(x_smooth)

# 绘制结果
plt.figure(figsize=(8, 4))
plt.plot(x1, y1, 'ro', label='Curve 1')
plt.plot(x2, y2, 'bo', label='Curve 2')
plt.plot(x_smooth, y_smooth, 'g-', label='Smoothed Connection')
plt.legend()
plt.title("Smooth Connection using Cubic Spline")
plt.show()