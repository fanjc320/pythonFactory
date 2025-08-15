import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
import math
from scipy.interpolate import splprep, splev


def calculate_angle(p0, p1, p2):
    """计算三个点形成的角度（0-180度）"""
    v1 = np.array(p0) - np.array(p1)
    v2 = np.array(p2) - np.array(p1)
    len1 = np.linalg.norm(v1)
    len2 = np.linalg.norm(v2)
    dot_product = np.dot(v1, v2)
    angle_rad = np.arccos(dot_product / (len1 * len2))
    angle_deg = np.degrees(angle_rad)
    cross = np.cross(v1, v2)
    return angle_deg, cross > 0


def is_concave(polygon, i, threshold=160):
    """检查第i个顶点是否是凹点（角度小于threshold度）"""
    n = len(polygon)
    p0 = polygon[(i - 1) % n]
    p1 = polygon[i]
    p2 = polygon[(i + 1) % n]
    angle, is_reflex = calculate_angle(p0, p1, p2)
    return is_reflex and angle < threshold


def find_concave_vertices(polygon, threshold=160):
    """找出所有凹点（角度小于threshold度）"""
    return [i for i in range(len(polygon)) if is_concave(polygon, i, threshold)]


def quadratic_bezier(p0, p1, p2, t):
    """二次贝塞尔曲线"""
    return (1 - t) ** 2 * np.array(p0) + 2 * (1 - t) * t * np.array(p1) + t ** 2 * np.array(p2)


def cubic_bezier(p0, p1, p2, p3, t):
    """三次贝塞尔曲线"""
    return (1 - t) ** 3 * np.array(p0) + 3 * (1 - t) ** 2 * t * np.array(p1) + 3 * (1 - t) * t ** 2 * np.array(
        p2) + t ** 3 * np.array(p3)


def generate_smooth_connection(p1, p2, polygon, resolution=20):
    """
    生成两点间的平滑连接曲线
    参数:
        p1, p2: 要连接的两个点索引
        polygon: 原始多边形
        resolution: 曲线分辨率
    返回:
        曲线上的点列表
    """
    n = len(polygon)
    prev1 = polygon[(p1 - 1) % n]
    next1 = polygon[(p1 + 1) % n]
    prev2 = polygon[(p2 - 1) % n]
    next2 = polygon[(p2 + 1) % n]

    # 计算控制点 - 这里使用简单的启发式方法
    # 可以调整这些系数来改变曲线形状
    ctrl1 = np.array(polygon[p1]) + 0.3 * (np.array(next1) - np.array(prev1))
    ctrl2 = np.array(polygon[p2]) + 0.3 * (np.array(next2) - np.array(prev2))

    # 生成三次贝塞尔曲线
    curve_points = []
    for t in np.linspace(0, 1, resolution):
        point = cubic_bezier(polygon[p1], ctrl1, ctrl2, polygon[p2], t)
        curve_points.append(point)

    return curve_points


def split_with_smooth_connection(polygon, i, j, resolution=20):
    """用平滑曲线连接i和j点来拆分多边形"""
    if i > j:
        i, j = j, i

    # 生成平滑连接曲线
    curve = generate_smooth_connection(i, j, polygon, resolution)

    # 创建两个子多边形
    poly1 = polygon[i:j + 1] + curve[::-1]  # 逆序曲线点
    poly2 = polygon[j:] + polygon[:i + 1] + curve

    return poly1, poly2


def plot_polygon_with_splits(polygon, splits=None, threshold=160):
    """绘制多边形和可能的拆分曲线"""
    plt.figure(figsize=(10, 8))

    # 绘制原始多边形
    closed_poly = polygon + [polygon[0]]
    x, y = zip(*closed_poly)
    plt.plot(x, y, 'b-', linewidth=2, label='原始多边形')
    plt.fill(x, y, 'b', alpha=0.1)

    # 标记凹点
    concave_verts = find_concave_vertices(polygon, threshold)
    for i in concave_verts:
        px, py = polygon[i]
        plt.plot(px, py, 'ro', markersize=8)
        plt.text(px, py, f"{i}", ha='center', va='center',
                 bbox=dict(facecolor='white', edgecolor='none'))

    # 绘制所有可能的平滑拆分曲线
    if splits:
        for i, j in splits:
            curve = generate_smooth_connection(i, j, polygon)
            cx, cy = zip(*curve)
            plt.plot(cx, cy, 'g--', linewidth=1.5, alpha=0.7)
            plt.text(np.mean(cx), np.mean(cy), f"{i}-{j}",
                     ha='center', va='center', color='green')

    plt.axis('equal')
    plt.legend()
    plt.title(f"凹角阈值={threshold}° 多边形与可能的平滑拆分曲线")
    plt.show()


# 示例多边形
polygon = [(0, 0), (0.5, 0.2), (1.5, 0.5), (2.5, 0.2), (3, 0),
           (3, 1), (2, 1), (2, 2), (1, 2), (1, 1), (0, 1)]

# 设置凹角阈值（度）
angle_threshold = 160

# 找出所有凹点
concave_verts = find_concave_vertices(polygon, angle_threshold)

# 生成所有可能的拆分组合
possible_splits = list(combinations(concave_verts, 2))

# 绘制多边形和可能的拆分曲线
plot_polygon_with_splits(polygon, possible_splits, angle_threshold)

# 示例：选择一个拆分方案并展示结果
if len(concave_verts) >= 2:
    # 选择第一个拆分方案
    split_i, split_j = possible_splits[0]

    # 执行拆分
    poly1, poly2 = split_with_smooth_connection(polygon, split_i, split_j)

    # 绘制结果
    plt.figure(figsize=(10, 8))

    # 绘制第一个子多边形
    closed_poly1 = poly1 + [poly1[0]]
    x1, y1 = zip(*closed_poly1)
    plt.plot(x1, y1, 'r-', linewidth=2, label='子多边形1')
    plt.fill(x1, y1, 'r', alpha=0.1)

    # 绘制第二个子多边形
    closed_poly2 = poly2 + [poly2[0]]
    x2, y2 = zip(*closed_poly2)
    plt.plot(x2, y2, 'g-', linewidth=2, label='子多边形2')
    plt.fill(x2, y2, 'g', alpha=0.1)

    # 标记原始凹点
    for i in concave_verts:
        px, py = polygon[i]
        plt.plot(px, py, 'bo', markersize=8)

    plt.axis('equal')
    plt.legend()
    plt.title(f"使用平滑曲线拆分的子多边形 (连接点 {split_i}-{split_j})")
    plt.show()