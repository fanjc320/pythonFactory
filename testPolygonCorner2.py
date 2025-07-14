import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from testSVG.polygon import getPolygonFromPath
matplotlib.rc("font",family='MicroSoft YaHei',weight="bold")

def calculate_curvature_and_convexity(points, k=3):
    """
    计算多边形顶点曲率并判断凹凸性
    参数:
        points: 多边形顶点坐标列表 [(x1,y1), (x2,y2), ...]
        k: 计算曲率时使用的邻域窗口半宽
    返回:
        curvatures: 各顶点曲率值数组
        convexities: 各顶点凹凸性列表 ('convex', 'concave', 'flat')
        turning_angles: 各顶点转向角(弧度)
    """
    n = len(points)
    curvatures = np.zeros(n)
    turning_angles = np.zeros(n)
    convexities = ['flat'] * n

    for i in range(n):
        # 获取当前点及其前后k个点
        window = []
        for j in range(-k, k + 1):
            idx = (i + j) % n
            window.append(points[idx])

        x = [p[0] for p in window]
        y = [p[1] for p in window]

        # 计算一阶和二阶导数
        dx = np.gradient(x)
        dy = np.gradient(y)
        ddx = np.gradient(dx)
        ddy = np.gradient(dy)

        # 计算曲率
        denominator = (dx[-1] ** 2 + dy[-1] ** 2) ** 1.5
        if denominator > 1e-6:  # 避免除以零
            curvature = (dx[-1] * ddy[-1] - dy[-1] * ddx[-1]) / denominator
            curvatures[i] = np.abs(curvature)
        else:
            curvatures[i] = 0

        # 计算转向角判断凹凸性
        prev_idx = (i - 1) % n
        next_idx = (i + 1) % n
        v1 = np.array(points[i]) - np.array(points[prev_idx])
        v2 = np.array(points[next_idx]) - np.array(points[i])

        # 计算叉积和转向角
        cross = np.cross(v1, v2)
        dot = np.dot(v1, v2)
        turning_angle = np.arctan2(np.linalg.norm(cross), dot)
        turning_angles[i] = turning_angle

        # 判断凹凸性
        if cross > 1e-6:  # 凸点(左转)
            convexities[i] = 'convex'
        elif cross < -1e-6:  # 凹点(右转)
            convexities[i] = 'concave'
        else:  # 平直或共线
            convexities[i] = 'flat'

    return curvatures, convexities, turning_angles


def find_curvature_peaks(curvatures, convexities, threshold=0.1, min_dist=1):
    """
    寻找曲率极值点，并返回其索引和属性
    """
    peaks = []
    n = len(curvatures)

    for i in range(1, n - 1):
        if (curvatures[i] > curvatures[i - 1] and
                curvatures[i] > curvatures[i + 1] and
                curvatures[i] > threshold and
                convexities[i] != 'flat'):
            # 检查最小距离
            # if not any(abs(i - p) <= min_dist for p in peaks):
            if (p[i]['index'] is None or not any(abs(i - p[i]['index'])  <= min_dist) for p in peaks):
                peaks.append({
                    'index': i,
                    'curvature': curvatures[i],
                    'convexity': convexities[i],
                    'angle': turning_angles[i] if 'turning_angles' in locals() else None
                })
                # peaks.append(i)

    # 按曲率值排序
    peaks.sort(key=lambda x: x['curvature'], reverse=True)
    return peaks


# 示例多边形 (包含凸点和凹点)
points = np.array([
    [0, 0], [1, 0], [2, 0.2], [3, 0], [4, 0],  # 底部边缘
    [4, 1], [3.5, 1.5], [3, 1.2], [2.5, 1.5],  # 右侧凹部
    [2, 1], [1.5, 1.5], [1, 1], [0.5, 1.3], [0, 1]  # 顶部波浪
])

all_polygons = getPolygonFromPath("./testSVG/test_polygon2.svg")
polygon_np = all_polygons[0]
print("before polygon_np:", polygon_np)
# polygon_np = [list(t) for t in polygon_np]
polygon_np = np.array(polygon_np)
points = polygon_np

# 计算曲率和凹凸性
curvatures, convexities, turning_angles = calculate_curvature_and_convexity(points)
peaks = find_curvature_peaks(curvatures, convexities, threshold=0.3)

# 可视化结果
plt.figure(figsize=(14, 6))

# 绘制多边形和顶点
plt.subplot(121)
plt.plot(*zip(*np.vstack([points, points[0]])), 'b-', label='多边形轮廓')
plt.plot(points[:, 0], points[:, 1], 'ko', label='所有顶点')

# 标记凹凸性
for i, (x, y) in enumerate(points):
    color = 'g' if convexities[i] == 'convex' else 'r' if convexities[i] == 'concave' else 'k'
    marker = '^' if convexities[i] == 'convex' else 'v' if convexities[i] == 'concave' else 'o'
    plt.plot(x, y, marker=marker, color=color)
    plt.text(x, y + 0.05, f'{i}', color='blue', fontsize=8)

# 标记曲率极值点
for peak in peaks:
    i = peak['index']
    plt.plot(points[i, 0], points[i, 1], 'yo', markersize=10, markeredgecolor='k')
    plt.text(points[i, 0], points[i, 1] - 0.1,
             f"C:{peak['curvature']:.2f}\n{peak['convexity']}",
             ha='center', va='top', bbox=dict(facecolor='white', alpha=0.8))

plt.title('多边形顶点曲率与凹凸性')
plt.axis('equal')
plt.legend()

# 绘制曲率图
plt.subplot(122)
plt.plot(curvatures, 'g-', label='曲率值')
plt.plot(turning_angles, 'b--', label='转向角(弧度)')

# 标记极值点
for peak in peaks:
    i = peak['index']
    plt.plot(i, curvatures[i], 'ro')
    plt.text(i, curvatures[i], f"{i}\n{peak['convexity']}", ha='right')

plt.xlabel('顶点索引')
plt.ylabel('值')
plt.title('顶点曲率和转向角')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

# 输出结果
print("顶点曲率和凹凸性分析:")
for i, (point, curvature, convexity) in enumerate(zip(points, curvatures, convexities)):
    print(f"顶点 {i}: 坐标 {point}, 曲率 {curvature:.4f}, 凹凸性 {convexity}")

print("\n检测到的曲率极值点:")
for peak in peaks:
    i = peak['index']
    print(f"顶点 {i}: 坐标 {points[i]}, 曲率 {peak['curvature']:.4f}, " +
          f"凹凸性 {peak['convexity']}, 转向角 {turning_angles[i]:.4f} rad")