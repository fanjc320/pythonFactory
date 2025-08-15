import numpy as np
import matplotlib.pyplot as plt
import bezier
import numpy as np

# 第一条贝塞尔曲线（3个控制点）
nodes1 = np.array([
    [0.0, 1.0, 2.0],  # x
    [0.0, 2.0, 1.0]   # y
])
curve1 = bezier.Curve(nodes1, degree=2)

# 第二条贝塞尔曲线（确保起点与 curve1 终点重合）
nodes2 = np.array([
    [2.0, 3.0, 4.0],  # x (起点=curve1终点)
    [1.0, 0.0, 1.0]   # y
])
curve2 = bezier.Curve(nodes2, degree=2)

# 检查是否 C1 连续（切线方向相同）
tangent1 = curve1.evaluate_hodograph(1.0)  # 终点导数
tangent2 = curve2.evaluate_hodograph(0.0)  # 起点导数
print("Tangent at connection:", tangent1, tangent2)

# 绘制曲线
ax = curve1.plot(num_pts=50, color='blue')
curve2.plot(num_pts=50, color='red', ax=ax)
ax.set_title("Bezier Curve Connection (C1 Continuity)")
plt.show()