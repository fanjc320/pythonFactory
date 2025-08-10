import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
from shapely.geometry import Polygon, LineString, MultiPolygon
from shapely.ops import polygonize, unary_union
from common.polygon_plot import *

def is_concave(polygon, index):
    """检查给定索引的点是否是凹点"""
    points = list(polygon.exterior.coords)[:-1]
    n = len(points)
    p1 = points[(index - 1) % n]
    p2 = points[index]
    p3 = points[(index + 1) % n]

    # 计算叉积
    cross = (p2[0] - p1[0]) * (p3[1] - p2[1]) - (p2[1] - p1[1]) * (p3[0] - p2[0])
    return cross > 0  # 在逆时针多边形中，叉积为正表示凹点


def find_concave_points(polygon):
    """找到多边形中所有的凹点"""
    concave_indices = []
    points = list(polygon.exterior.coords)[:-1]
    for i in range(len(points)):
        if is_concave(polygon, i):
            concave_indices.append(i)
    return concave_indices


def generate_diagonals(polygon, concave_indices):
    """生成所有可能的分割线（对角线）"""
    diagonals = []
    points = list(polygon.exterior.coords)[:-1]
    n = len(points)

    for i in concave_indices:
        for j in range(n):
            # 确保不是相邻点且不是同一个点
            if j != i and abs(j - i) > 1 and (j + 1) % n != i and (i + 1) % n != j:
                line = LineString([points[i], points[j]])
                if polygon.contains(line):
                    diagonals.append((i, j))

    return diagonals


def split_polygon(polygon, split_lines):
    """使用分割线分割多边形"""
    # 创建分割线集合
    lines = []
    points = list(polygon.exterior.coords)[:-1]
    for i, j in split_lines:
        lines.append(LineString([points[i], points[j]]))

    # 合并所有分割线
    splitter = unary_union(lines)

    # 分割多边形
    result = polygon.difference(splitter)

    # 如果结果是MultiPolygon，则分割成功
    if isinstance(result, MultiPolygon):
        return list(result.geoms)
    return []


def decompose_polygon(polygon):
    """拆解多边形"""
    concave_indices = find_concave_points(polygon)
    diagonals = generate_diagonals(polygon, concave_indices)

    # 存储所有可能的拆解方案
    decompositions = []

    # 尝试所有可能的分割线组合（限制最大分割线数量）
    max_splits = min(3, len(diagonals))  # 避免组合爆炸
    for r in range(1, max_splits + 1):
        for combo in combinations(diagonals, r):
            # 尝试分割多边形
            sub_polygons = split_polygon(polygon, combo)

            # 检查分割结果是否有效
            if len(sub_polygons) > 1:
                valid = True
                for poly in sub_polygons:
                    if not poly.is_valid or poly.area < 1e-6:
                        valid = False
                        break
                if valid:
                    decompositions.append(combo)

    return decompositions, diagonals


def plot_decomposition(polygon, decomposition, diagonals):
    """可视化拆解结果"""
    fig, ax = plt.subplots(figsize=(10, 10))

    # 绘制原始多边形
    x, y = polygon.exterior.xy
    ax.plot(x, y, 'b-', linewidth=2)
    ax.fill(x, y, 'b', alpha=0.1)

    # 绘制所有可能的分割线
    points = list(polygon.exterior.coords)[:-1]
    for (i, j) in diagonals:
        ax.plot([points[i][0], points[j][0]],
                [points[i][1], points[j][1]],
                'g--', alpha=0.3)

    # 绘制当前拆解方案的分割线
    for (i, j) in decomposition:
        ax.plot([points[i][0], points[j][0]],
                [points[i][1], points[j][1]],
                'r-', linewidth=2)

    # 标记凹点
    concave_indices = find_concave_points(polygon)
    for i in concave_indices:
        ax.plot(points[i][0], points[i][1], 'ro', markersize=8)

    ax.set_aspect('equal')
    plt.title(f"拆解方案: {len(decomposition)}条分割线")
    plt.show()


# 示例多边形
polygon = [(0, 0), (3, 0), (3, 1), (2, 1), (2, 2), (1, 2), (1, 1), (0, 1)]
plot_polygons(polygon, fill=True, color='skyblue', title='Single Polygon')
plt.show()
polygon = Polygon(polygon)
# 找到所有拆解方案
decompositions, diagonals = decompose_polygon(polygon)

# 打印所有可能的拆解方案
print(f"找到 {len(decompositions)} 种拆解方案:")
for i, decomp in enumerate(decompositions, 1):
    print(f"方案 {i}: 使用分割线 {decomp}")

# 可视化所有拆解方案
for decomp in decompositions:
    plot_decomposition(polygon, decomp, diagonals)