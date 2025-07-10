import numpy as np
import matplotlib.pyplot as plt
from scipy.special import comb

def bernstein_poly(i, n, t):
    """伯恩斯坦多项式"""
    return comb(n, i) * (t**i) * ((1 - t)**(n - i))

def bezier_curve(points, n_times=1000):
    """生成贝塞尔曲线点"""
    n = len(points) - 1
    t = np.linspace(0, 1, n_times)
    curve = np.zeros((n_times, 2))
    for i in range(n + 1):
        curve += np.outer(bernstein_poly(i, n, t), points[i])
    return curve

# 假设我们有一段不完整的曲线，需要补全两个部分
# 已知部分1
section1 = np.array([(0, 0), (1, 2), (2, 3)])
# 已知部分2
section2 = np.array([(5, 1), (6, -1), (7, 0)])

# 为了保持曲率连续性，我们需要在连接处匹配一阶和二阶导数
# 这里简化处理，添加控制点来平滑连接
control_point1 = section1[-1] + (section1[-1] - section1[-2]) * 0.5
control_point2 = section2[0] - (section2[1] - section2[0]) * 0.5

# 创建补全的贝塞尔曲线控制点
bezier_points = np.vstack([
    section1[-1],
    control_point1,
    control_point2,
    section2[0]
])

# 生成贝塞尔曲线
bezier_segment = bezier_curve(bezier_points)

# 绘制结果
plt.figure(figsize=(8, 6))
plt.plot(section1[:, 0], section1[:, 1], 'ro-', label='已知部分1')
plt.plot(section2[:, 0], section2[:, 1], 'go-', label='已知部分2')
plt.plot(bezier_segment[:, 0], bezier_segment[:, 1], 'b-', label='贝塞尔补全')
plt.plot(bezier_points[:, 0], bezier_points[:, 1], 'c--', label='控制多边形')
plt.scatter(bezier_points[:, 0], bezier_points[:, 1], c='cyan', marker='x')
plt.legend()
plt.title('使用贝塞尔曲线补全多边形（保持曲率连续性）')
plt.grid(True)
plt.axis('equal')
plt.show()