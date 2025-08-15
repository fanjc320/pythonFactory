import numpy as np
import matplotlib.pyplot as plt


def catmull_rom_spline(p0, p1, p2, p3, num_points=100):
    """
    Catmull-Rom样条曲线 (保证C1连续)
    参数:
        p0, p1, p2, p3: 控制点 (p1和p2是端点)
        num_points: 生成的曲线点数
    返回:
        曲线上的点
    """
    t = np.linspace(0, 1, num_points)
    t2 = t ** 2
    t3 = t ** 3

    # Catmull-Rom矩阵
    M = np.array([
        [-1, 3, -3, 1],
        [2, -5, 4, -1],
        [-1, 0, 1, 0],
        [0, 2, 0, 0]
    ]) / 2.0

    # 几何矩阵
    G = np.vstack([p0, p1, p2, p3])

    # 计算曲线点
    T = np.vstack([t3, t2, t, np.ones_like(t)])
    curve = np.dot(np.dot(T.T, M), G)

    return curve


# 示例使用
line1 = np.array([[0, 0], [1, 2], [2, 1.5]])
line2 = np.array([[3, 3], [4, 1], [5, 2]])

# 需要四个点: [p0, p1, p2, p3]
# p1和p2是端点，p0和p3用于确定切线方向
p0 = line1[-2] if len(line1) > 1 else line1[-1] - np.array([1, 0])
p1 = line1[-1]
p2 = line2[0]
p3 = line2[1] if len(line2) > 1 else line2[0] + np.array([1, 0])

curve = catmull_rom_spline(p0, p1, p2, p3)

plt.figure(figsize=(10, 6))
plt.plot(line1[:, 0], line1[:, 1], 'b-o', label='Line 1')
plt.plot(line2[:, 0], line2[:, 1], 'g-o', label='Line 2')
plt.plot(curve[:, 0], curve[:, 1], 'r-', linewidth=2, label='Catmull-Rom Spline')
plt.axis('equal')
plt.legend()
plt.grid(True)
plt.title('C1 Continuous Catmull-Rom Spline')
plt.show()