import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
import math


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


def calculate_tangent(polygon, point_idx, alpha=0.3):
    """
    计算多边形在某点的切线方向
    alpha: 控制切线长度的系数 (0-1)
    """
    prev_point = polygon[(point_idx - 1) % len(polygon)]
    next_point = polygon[(point_idx + 1) % len(polygon)]
    tangent = (np.array(next_point) - np.array(prev_point)) * alpha
    return tangent


def cubic_bezier(p0, p1, p2, p3, t):
    """三次贝塞尔曲线计算"""
    return (1 - t) ** 3 * np.array(p0) + 3 * (1 - t) ** 2 * t * np.array(p1) + 3 * (1 - t) * t ** 2 * np.array(
        p2) + t ** 3 * np.array(p3)


def generate_smooth_connection(polygon, i, j, resolution=30):
    """
    生成两点间的平滑连接曲线，考虑边切线方向
    返回曲线上的点列表
    """
    # 获取两点位置
    p1 = np.array(polygon[i])
    p2 = np.array(polygon[j])

    # 计算切线方向
    t1 = calculate_tangent(polygon, i)
    t2 = calculate_tangent(polygon, j)

    # 调整切线方向确保朝向对方
    if np.dot(p2 - p1, t1) < 0:
        t1 = -t1
    if np.dot(p1 - p2, t2) < 0:
        t2 = -t2

    # 创建三次贝塞尔曲线 (两个控制点)
    ctrl1 = p1 + t1
    ctrl2 = p2 + t2

    # 生成曲线点
    curve_points = []
    for t in np.linspace(0, 1, resolution):
        point = cubic_bezier(p1, ctrl1, ctrl2, p2, t)
        curve_points.append(tuple(point))

    return curve_points


def split_with_smooth_connection(polygon, i, j, resolution=30):
    """用平滑曲线连接i和j点来拆分多边形"""
    if i > j:
        i, j = j, i

    # 生成平滑连接曲线
    curve = generate_smooth_connection(polygon, i, j, resolution)

    # 创建两个子多边形
    poly1 = polygon[i:j + 1] + curve[::-1]  # 逆序曲线点
    poly2 = polygon[j:] + polygon[:i + 1] + curve

    return poly1, poly2


def plot_polygon_decomposition(polygon, decompositions, threshold=160):
    """绘制多边形分解结果"""
    plt.figure(figsize=(10, 8))
    colors = plt.cm.tab10.colors

    # 绘制原始多边形
    closed_poly = polygon + [polygon[0]]
    x, y = zip(*closed_poly)
    plt.plot(x, y, 'k--', linewidth=1, alpha=0.5)

    # 绘制所有子多边形
    for i, subpoly in enumerate(decompositions):
        closed_subpoly = subpoly + [subpoly[0]]
        x, y = zip(*closed_subpoly)
        plt.plot(x, y, color=colors[i % len(colors)], linewidth=2)
        plt.fill(x, y, color=colors[i % len(colors)], alpha=0.3)

        # 标注顶点
        for j, (px, py) in enumerate(subpoly):
            plt.text(px, py, f"{j}", ha='center', va='center',
                     bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))

    # 标记原始凹点
    concave_verts = find_concave_vertices(polygon, threshold)
    for i in concave_verts:
        px, py = polygon[i]
        plt.plot(px, py, 'ro', markersize=8)

    plt.axis('equal')
    plt.title(f"凹角阈值={threshold}° 平滑拆分结果 (共{len(decompositions)}个子多边形)")
    plt.show()


def find_optimal_splits(polygon, concave_verts):
    """寻找最优的拆分点对（简化版：选择距离最远的点对）"""
    if len(concave_verts) < 2:
        return []

    # 计算所有凹点对的距离
    distances = []
    for i, j in combinations(concave_verts, 2):
        p1 = np.array(polygon[i])
        p2 = np.array(polygon[j])
        distances.append((np.linalg.norm(p1 - p2), (i, j)))

    # 按距离排序并返回最佳的几个
    distances.sort(reverse=True)
    return [pair for dist, pair in distances[:min(3, len(distances))]]  # 返回前3个最佳


def smooth_polygon_decomposition(polygon, threshold=160):
    """执行平滑多边形分解"""
    concave_verts = find_concave_vertices(polygon, threshold)

    if len(concave_verts) < 2:
        print("凹点不足2个，无需拆分")
        return [polygon]

    # 寻找最优拆分点对
    best_splits = find_optimal_splits(polygon, concave_verts)
    if not best_splits:
        return [polygon]

    # 选择第一个最佳拆分方案
    split_i, split_j = best_splits[0]

    # 执行拆分
    poly1, poly2 = split_with_smooth_connection(polygon, split_i, split_j)

    # 递归处理子多边形
    final_decomposition = []
    for subpoly in [poly1, poly2]:
        sub_concave = find_concave_vertices(subpoly, threshold)
        if len(sub_concave) >= 2:
            final_decomposition += smooth_polygon_decomposition(subpoly, threshold)
        else:
            final_decomposition.append(subpoly)

    return final_decomposition


# 示例多边形
polygon = [
    (0, 0), (0.5, 0.2), (1.5, 0.5), (2.5, 0.2), (3, 0),
    (3, 1), (2, 1), (2, 2), (1, 2), (1, 1), (0, 1)
]

# 设置凹角阈值（度）
angle_threshold = 160

# 执行平滑拆分
decompositions = smooth_polygon_decomposition(polygon, angle_threshold)

# 绘制结果
print(f"将多边形拆分为 {len(decompositions)} 个子多边形")
plot_polygon_decomposition(polygon, decompositions, angle_threshold)

# 显示每个子多边形的顶点
for i, subpoly in enumerate(decompositions):
    print(f"\n子多边形 {i + 1}:")
    for j, point in enumerate(subpoly):
        print(f"  顶点 {j}: {point}")