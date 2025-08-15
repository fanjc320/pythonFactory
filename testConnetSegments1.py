import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev

# 定义两条线段
line1 = np.array([[0, 0], [1, 2]])  # 第一条线段
line2 = np.array([[3, 3], [4, 1]])  # 第二条线段

# 创建连接点集（包括线段端点和中间控制点）
points = np.vstack([line1[-1:],
                   [line1[-1] + (line2[0] - line1[-1])/3],  # 中间控制点1
                   [line1[-1] + 2*(line2[0] - line1[-1])/3], # 中间控制点2
                   line2[:1]])

# 参数化样条曲线
tck, u = splprep(points.T, u=None, s=0.0, k=3)
u_new = np.linspace(u.min(), u.max(), 100)
x_new, y_new = splev(u_new, tck, der=0)

# 绘制结果
plt.figure(figsize=(8, 6))
plt.plot(line1[:, 0], line1[:, 1], 'b-o', label='Line 1')
plt.plot(line2[:, 0], line2[:, 1], 'g-o', label='Line 2')
plt.plot(x_new, y_new, 'r-', label='Spline Curve')
plt.scatter(points[1:-1, 0], points[1:-1, 1], c='k', marker='x', label='Control Points')
plt.legend()
plt.grid(True)
plt.title('Spline Curve Connection')
plt.show()