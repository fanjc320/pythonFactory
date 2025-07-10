import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev

# 假设我们有一些不完整的多边形顶点（缺失部分用None表示）
incomplete_polygon = [
    (0, 0), (1, 2), (2, 3), None, None, (5, 1), (6, -1), (7, 0), None, (0, 0)
]

# 提取已知点
known_points = [p for p in incomplete_polygon if p is not None]
x, y = zip(*known_points)

# 参数化样条曲线
tck, u = splprep([x, y], s=0, per=True)  # per=True表示闭合曲线

# 生成更多的点来补全曲线
u_new = np.linspace(0, 1, 1000)
x_new, y_new = splev(u_new, tck)

# 绘制结果
plt.figure(figsize=(8, 6))
plt.plot(x, y, 'ro', label='已知点')
plt.plot(x_new, y_new, 'b-', label='样条补全')
plt.legend()
plt.title('使用样条曲线补全多边形')
plt.grid(True)
plt.axis('equal')
plt.show()