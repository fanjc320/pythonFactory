import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations


def is_concave(polygon, i):
    """检查第i个顶点是否是凹点"""
    n = len(polygon)
    p0 = polygon[(i - 1) % n]
    p1 = polygon[i]
    p2 = polygon[(i + 1) % n]

    # 计算向量
    v1 = np.array(p0) - np.array(p1)
    v2 = np.array(p2) - np.array(p1)

    # 计算叉积
    cross = np.cross(v1, v2)

    # 在标准坐标系中，叉积为正表示凹点
    return cross > 0


def find_concave_vertices(polygon):
    """找出所有凹点"""
    return [i for i in range(len(polygon)) if is_concave(polygon, i)]


def is_valid_diagonal(polygon, i, j):
    """检查i和j之间的对角线是否有效"""
    # 确保i和j不相邻
    n = len(polygon)
    if abs(i - j) % n == 1 or abs(j - i) % n == 1:
        return False

    # 检查对角线是否完全在多边形内部
    # 这里简化处理，实际需要更复杂的几何判断
    return True


def split_polygon(polygon, i, j):
    """沿i-j对角线拆分多边形"""
    if i > j:
        i, j = j, i
    poly1 = polygon[i:j + 1]
    poly2 = polygon[j:] + polygon[:i + 1]
    return poly1, poly2


def generate_all_splits(polygon):
    """生成所有可能的拆分方式"""
    concave_verts = find_concave_vertices(polygon)
    splits = []

    # 生成所有凹点对组合
    for i, j in combinations(concave_verts, 2):
        if is_valid_diagonal(polygon, i, j):
            splits.append((i, j))

    return splits


def recursive_split(polygon, current_decomposition=None):
    """递归拆分多边形"""
    if current_decomposition is None:
        current_decomposition = [polygon]

    concave_counts = [len(find_concave_vertices(p)) for p in current_decomposition]
    if all(cnt <= 1 for cnt in concave_counts):
        return [current_decomposition]

    decompositions = []

    for idx, subpoly in enumerate(current_decomposition):
        concave_verts = find_concave_vertices(subpoly)
        if len(concave_verts) <= 1:
            continue

        splits = generate_all_splits(subpoly)
        for i, j in splits:
            new_poly1, new_poly2 = split_polygon(subpoly, i, j)
            new_decomposition = current_decomposition[:idx] + [new_poly1, new_poly2] + current_decomposition[idx + 1:]
            decompositions += recursive_split(polygon, new_decomposition)

    return decompositions if decompositions else [current_decomposition]


def plot_polygon_decomposition(decomposition):
    """绘制多边形分解结果"""
    plt.figure()
    colors = plt.cm.tab10.colors

    for i, polygon in enumerate(decomposition):
        closed_poly = polygon + [polygon[0]]
        x, y = zip(*closed_poly)
        plt.plot(x, y, color=colors[i % len(colors)], linewidth=2)
        plt.fill(x, y, color=colors[i % len(colors)], alpha=0.3)

    plt.axis('equal')
    plt.title(f"分解为{len(decomposition)}个子多边形")
    plt.show()


# 示例多边形
polygon = [(0, 0), (3, 0), (3, 1), (2, 1), (2, 2), (1, 2), (1, 1), (0, 1)]

# 找出所有可能的分解
all_decompositions = recursive_split(polygon)

# 绘制每种分解方式
for i, decomposition in enumerate(all_decompositions):
    print(f"分解方案 {i + 1}:")
    plot_polygon_decomposition(decomposition)