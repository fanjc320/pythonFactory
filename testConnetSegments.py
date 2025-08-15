import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev

# 定义两条线段
line1 = np.array([[0, 0], [1, 2]])  # 第一条线段
line2 = np.array([[3, 3], [4, 1]])   # 第二条线段

# 提取连接点
p0 = line1[-1]  # 第一条线段的终点
p3 = line2[0]   # 第二条线段的起点

# 计算控制点
p1 = p0 + np.array([0.5, 0.5])  # 第一个控制点
p2 = p3 - np.array([0.5, 0.5])  # 第二个控制点

# 定义贝塞尔曲线函数
def cubic_bezier(p0, p1, p2, p3, t):
    return (1-t)**3 * p0 + 3*(1-t)**2*t * p1 + 3*(1-t)*t**2 * p2 + t**3*p3

# 生成曲线点
t = np.linspace(0, 1, 100)
curve_points = np.array([cubic_bezier(p0, p1, p2, p3, ti) for ti in t])

# 绘制结果
plt.figure(figsize=(8, 6))
plt.plot(line1[:, 0], line1[:, 1], 'b-o', label='Line 1')
plt.plot(line2[:, 0], line2[:, 1], 'g-o', label='Line 2')
plt.plot(curve_points[:, 0], curve_points[:, 1], 'r-', label='Bezier Curve')
plt.scatter([p1[0], p2[0]], [p1[1], p2[1]], c='k', marker='x', label='Control Points')
plt.legend()
plt.grid(True)
plt.title('Bezier Curve Connection')
plt.show()