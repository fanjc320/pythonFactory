import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from itertools import combinations
import math
from testSVGtoPolygon3 import extract_polygons_with_colors
from common.Polygon_Simplify1 import rdp_simplify
from common.typeInfoDetail import recursive_type_compact
matplotlib.rc("font",family='MicroSoft YaHei',weight="bold")
matplotlib.use('Qt5Agg')
def calculate_angle(p0, p1, p2):
    """计算三个点形成的角度（0-180度）"""
    v1 = np.array(p0) - np.array(p1)
    v2 = np.array(p2) - np.array(p1)

    # 计算向量长度
    len1 = np.linalg.norm(v1)
    len2 = np.linalg.norm(v2)

    # 计算点积和角度（弧度）
    dot_product = np.dot(v1, v2)
    if abs(len1 * len2) < 0.01:
        # print("calculate_angle p0:", p0, " p1:", p1, " p2:", p2)
        return 0, False
    # print("calculate_angle len1:", len1, " len2:", len2, " dot_product:", dot_product)
    angle_rad = np.arccos(dot_product / (len1 * len2))

    # 转换为角度
    angle_deg = np.degrees(angle_rad)
    # print("calculate_angle p0:", p0, " p1:", p1, " p2:", p2, " v1:", v1, "v2:", v2)
    # 计算叉积确定方向
    cross = np.cross(v1, v2)
    # cross = np.cross(-105, -105)
    # cross = np.cross(105, 105)

    return angle_deg, cross > 0


def is_concave(polygon, i, threshold=160):
    """检查第i个顶点是否是凹点（角度小于threshold度）"""
    n = len(polygon)
    p0 = polygon[(i - 1) % n]
    p1 = polygon[i]
    p2 = polygon[(i + 1) % n]

    angle, is_reflex = calculate_angle(p0, p1, p2)

    # 凹点条件：是反射角（内角大于180度）且角度小于阈值
    return is_reflex and angle < threshold

def find_concave_vertices(polygon, threshold=160):
    """找出所有凹点（角度小于threshold度）"""
    return [i for i in range(len(polygon)) if is_concave(polygon, i, threshold)]


def segments_intersect(seg1, seg2):
    """判断两条线段是否相交（不包括端点接触）"""
    (x1, y1), (x2, y2) = seg1
    (x3, y3), (x4, y4) = seg2

    # 计算方向向量
    dx1 = x2 - x1
    dy1 = y2 - y1
    dx2 = x4 - x3
    dy2 = y4 - y3

    # 计算分母
    denominator = dy2 * dx1 - dx2 * dy1

    # 如果分母为0，表示线段平行或共线
    if denominator == 0:
        # 检查是否共线且有重叠
        if (x2 - x1) * (y3 - y1) == (y2 - y1) * (x3 - x1):  # 共线
            # 检查投影是否有重叠
            def overlap(a1, a2, b1, b2):
                return max(a1, a2) >= min(b1, b2) and min(a1, a2) <= max(b1, b2)

            x_overlap = overlap(x1, x2, x3, x4)
            y_overlap = overlap(y1, y2, y3, y4)
            return x_overlap and y_overlap
        return False

    # 计算参数u和v
    u = (dx2 * (y1 - y3) - dy2 * (x1 - x3)) / denominator
    v = (dx1 * (y1 - y3) - dy1 * (x1 - x3)) / denominator

    # 检查交点是否在两个线段上
    return (u > 0 and u < 1 and v > 0 and v < 1)


def is_point_in_polygon(point, polygon):
    """使用射线法判断点是否在多边形内部"""
    x, y = point
    n = len(polygon)
    inside = False

    for i in range(n):
        (x1, y1), (x2, y2) = polygon[i], polygon[(i + 1) % n]

        # 检查点是否在顶点上
        if (x == x1 and y == y1) or (x == x2 and y == y2):
            return True

        # 检查点是否在水平边上
        if y1 == y2 == y and min(x1, x2) <= x <= max(x1, x2):
            return True

        # 检查射线相交
        if min(y1, y2) < y <= max(y1, y2):
            x_intersect = (y - y1) * (x2 - x1) / (y2 - y1) + x1
            if x <= x_intersect:
                inside = not inside

    return inside


def is_valid_diagonal(polygon, i, j):
    """检查i和j之间的对角线是否有效"""
    n = len(polygon)
    if abs(i - j) % n == 1 or abs(j - i) % n == 1:
        return False  # 相邻顶点

    # 检查对角线是否与任何边相交
    diagonal = (polygon[i], polygon[j])
    for k in range(n):
        edge = (polygon[k], polygon[(k + 1) % n])
        # 跳过与对角线共享顶点的边
        if k != i and k != j and (k + 1) % n != i and (k + 1) % n != j:
            if segments_intersect(diagonal, edge):
                return False

    # 检查对角线的中点是否在多边形内部
    mid_point = ((polygon[i][0] + polygon[j][0]) / 2, (polygon[i][1] + polygon[j][1]) / 2)
    if not is_point_in_polygon(mid_point, polygon):
        return False

    return True


def split_polygon(polygon, i, j):
    """沿i-j对角线拆分多边形"""
    if i > j:
        i, j = j, i
    poly1 = polygon[i:j + 1]
    poly2 = polygon[j:] + polygon[:i + 1]
    return poly1, poly2


def generate_all_splits(polygon, threshold=160):
    """生成所有可能的拆分方式"""
    concave_verts = find_concave_vertices(polygon, threshold)
    splits = []

    # 生成所有凹点对组合
    for i, j in combinations(concave_verts, 2):
        if is_valid_diagonal(polygon, i, j):
            splits.append((i, j))

    return splits


# def recursive_split(polygon, threshold=160, current_decomposition=None, depth=0, max_depth=10):
#     """递归拆分多边形，添加深度限制防止无限递归"""
#     if depth > max_depth:
#         print("depth > max_depth     !!!!!!!!!!!!!!!!!!")
#         return [current_decomposition]
#
#     if current_decomposition is None:
#         # print("recursive_split current_decomposition is None")
#         current_decomposition = [polygon]
#
#     concave_counts = [len(find_concave_vertices(p, threshold)) for p in current_decomposition]
#     print("recursive_split len concave_counts:", len(concave_counts), " depth:", depth, " len(polygon):", len(polygon))
#     if all(cnt <= 1 for cnt in concave_counts):
#         # print("recursive_split cnt <= 1", " concave_counts:", concave_counts)
#         return [current_decomposition]
#
#     decompositions = []
#
#     for idx, subpoly in enumerate(current_decomposition):
#         concave_verts = find_concave_vertices(subpoly, threshold)
#         if len(concave_verts) <= 1:
#             # print("recursive_split len(concave_verts) <= 1:", len(concave_verts) <= 1)
#             continue
#
#         splits = generate_all_splits(subpoly, threshold)
#         for i, j in splits:
#             new_poly1, new_poly2 = split_polygon(subpoly, i, j)
#             new_decomposition = current_decomposition[:idx] + [new_poly1, new_poly2] + current_decomposition[idx + 1:]
#             # print("recursive_split len poly1:", len(new_poly1), " poly2:", len(new_poly2), " len(new_decomposition):",
#             #       len(new_decomposition))
#             # 递归处理新分解
#             new_decomps = recursive_split(polygon, threshold, new_decomposition, depth + 1, max_depth)
#             for decomp in new_decomps:
#                 # 检查是否已经存在相同的分解
#                 if not any(all(p in prev_decomp for p in decomp) for prev_decomp in decompositions):
#                     # print("---")
#                     decompositions.append(decomp)
#
#     return decompositions if decompositions else [current_decomposition]


def recursive_split_new(polygon, threshold=160, current_decomposition=None, depth=0, max_depth=10, memo=None):
    """递归拆分多边形，添加记忆化和深度限制"""
    if memo is None:
        memo = {}

    # 生成当前状态的哈希键（基于多边形顶点）
    state_key = tuple(tuple(p) for p in (current_decomposition or [polygon]))
    if state_key in memo:
        return memo[state_key]

    if depth > max_depth:
        result = [current_decomposition or [polygon]]
        memo[state_key] = result
        return result

    if current_decomposition is None:
        current_decomposition = [polygon]

    # 预计算凹顶点数，避免重复计算
    concave_info = []
    for p in current_decomposition:
        concave_verts = find_concave_vertices(p, threshold)
        concave_info.append((len(concave_verts), concave_verts))

    if all(cnt <= 1 for cnt, _ in concave_info):
        result = [current_decomposition]
        memo[state_key] = result
        return result

    decompositions = []
    visited_decomps = set()  # 用于去重

    for idx, (subpoly, (concave_cnt, concave_verts)) in enumerate(zip(current_decomposition, concave_info)):
        if concave_cnt <= 1:
            continue

        # 只生成有希望的拆分线（连接凹顶点）
        splits = generate_promising_splits(subpoly, concave_verts, threshold)

        for i, j in splits:
            try:
                new_poly1, new_poly2 = split_polygon(subpoly, i, j)
                if len(new_poly1) < 3 or len(new_poly2) < 3:  # 跳过无效拆分
                    continue

                new_decomposition = (current_decomposition[:idx] +
                                     [new_poly1, new_poly2] +
                                     current_decomposition[idx + 1:])

                # 使用规范化表示去重
                normalized_decomp = tuple(sorted(tuple(tuple(vertex) for poly in new_decomposition for vertex in poly)))
                if normalized_decomp in visited_decomps:
                    continue
                visited_decomps.add(normalized_decomp)

                # 递归处理
                new_decomps = recursive_split_new(polygon, threshold, new_decomposition, depth + 1, max_depth, memo)

                for decomp in new_decomps:
                    decompositions.append(decomp)

            except Exception as e:
                print(f"Split failed: {e}")
                continue

    result = decompositions if decompositions else [current_decomposition]
    memo[state_key] = result
    return result

# 修改 recursive_split_new 添加调试信息
def recursive_split_new1(polygon, threshold=160, current_decomposition=None, depth=0, max_depth=10, memo=None):
    """递归拆分多边形，添加详细的调试信息"""
    if memo is None:
        memo = {}

    if current_decomposition is None:
        current_decomposition = [polygon]
        print(f"初始多边形: {len(polygon)} 个顶点")

    # 预计算凹顶点信息
    concave_info = []
    for p in current_decomposition:
        concave_verts = find_concave_vertices(p, threshold)
        concave_info.append((len(concave_verts), concave_verts))
        print(f"子多边形 {len(p)} 顶点: {len(concave_verts)} 个凹顶点")

    # 检查是否所有子多边形都满足条件
    if all(cnt <= 1 for cnt, _ in concave_info):
        print(f"深度 {depth}: 所有子多边形满足条件 (≤1 凹顶点)")
        return [current_decomposition]

    if depth > max_depth:
        print(f"深度 {depth}: 达到最大深度限制")
        return [current_decomposition]

    decompositions = []

    for idx, (subpoly, (concave_cnt, concave_verts)) in enumerate(zip(current_decomposition, concave_info)):
        if concave_cnt <= 1:
            continue

        print(f"深度 {depth}: 处理子多边形 {idx} (有 {concave_cnt} 个凹顶点)")

        splits = generate_promising_splits1(subpoly, concave_verts, threshold)
        print(f"找到 {len(splits)} 个拆分线")

        for split_idx, (i, j) in enumerate(splits):
            print(f"尝试拆分线 {split_idx + 1}: ({i}, {j})")

            try:
                new_poly1, new_poly2 = split_polygon(subpoly, i, j)
                print(f"拆分成功: {len(new_poly1)} 和 {len(new_poly2)} 个顶点")

                new_decomposition = (current_decomposition[:idx] +
                                     [new_poly1, new_poly2] +
                                     current_decomposition[idx + 1:])

                # 递归处理
                new_decomps = recursive_split_new1(polygon, threshold, new_decomposition, depth + 1, max_depth, memo)

                for decomp in new_decomps:
                    decompositions.append(decomp)

            except Exception as e:
                print(f"拆分失败: {e}")
                continue

    if not decompositions:
        print(f"深度 {depth}: 没有找到有效拆分，返回当前分解")
        return [current_decomposition]

    return decompositions

def generate_promising_splits(polygon, concave_vertices, threshold=160):
    """
    生成有希望的多边形拆分线，只考虑连接凹顶点的拆分

    参数:
    - polygon: 输入多边形
    - concave_vertices: 凹顶点索引列表
    - threshold: 凹度阈值

    返回:
    - 拆分线列表 [(i, j), ...]，其中 i, j 是顶点索引
    """
    splits = []
    n = len(polygon)

    # 如果没有凹顶点或只有一个，返回空列表
    if len(concave_vertices) <= 1:
        return splits

    # 只考虑凹顶点之间的连接
    for i_idx in range(len(concave_vertices)):
        for j_idx in range(i_idx + 1, len(concave_vertices)):
            i = concave_vertices[i_idx]
            j = concave_vertices[j_idx]

            # 确保索引有效
            if i >= n or j >= n:
                continue

            # 检查拆分线是否有效（不自相交、在多边形内部等）
            if is_valid_split_line(polygon, i, j, threshold):
                splits.append((i, j))

    # 也可以考虑凹顶点与凸顶点的连接（在某些情况下可能更好）
    convex_vertices = [idx for idx in range(n) if idx not in concave_vertices]

    for concave_idx in concave_vertices:
        for convex_idx in convex_vertices:
            # 确保顶点不相邻
            if abs(concave_idx - convex_idx) % n <= 1:
                continue

            if is_valid_split_line(polygon, concave_idx, convex_idx, threshold):
                splits.append((concave_idx, convex_idx))

    return splits

# # 调试版本的 generate_promising_splits
def generate_promising_splits1(polygon, concave_vertices, threshold=160):
    """
    调试版本：生成所有可能的拆分线用于测试
    """
    splits = []
    n = len(polygon)

    print(f"生成拆分线: 多边形有 {n} 个顶点, {len(concave_vertices)} 个凹顶点")

    # 方法1: 凹顶点之间的连接
    for i in range(len(concave_vertices)):
        for j in range(i + 1, len(concave_vertices)):
            idx_i = concave_vertices[i]
            idx_j = concave_vertices[j]
            if is_valid_split_line1(polygon, idx_i, idx_j, threshold):
                splits.append((idx_i, idx_j))
                print(f"凹-凹拆分: ({idx_i}, {idx_j})")

    # 方法2: 如果凹-凹拆分不够，尝试凹-凸拆分
    if len(splits) == 0:
        convex_vertices = [i for i in range(n) if i not in concave_vertices]
        for concave_idx in concave_vertices:
            for convex_idx in convex_vertices:
                if is_valid_split_line1(polygon, concave_idx, convex_idx, threshold):
                    splits.append((concave_idx, convex_idx))
                    print(f"凹-凸拆分: ({concave_idx}, {convex_idx})")

    # 方法3: 如果还是没有拆分线，尝试所有顶点对（调试用）
    if len(splits) == 0:
        print("尝试所有可能的顶点对...")
        for i in range(n):
            for j in range(i + 2, n):  # 跳过相邻顶点
                if abs(i - j) % n > 1 and is_valid_split_line1(polygon, i, j, threshold):
                    splits.append((i, j))
                    print(f"全连接拆分: ({i}, {j})")

    print(f"找到 {len(splits)} 个有效拆分线")
    return splits

# 拆分线有效性检查严格版本
def is_valid_split_line(polygon, i, j, threshold=160):
    """
    检查拆分线是否有效

    条件:
    1. 拆分线不能是多边形的边
    2. 拆分线必须在多边形内部
    3. 拆分线不能与其他边相交
    4. 拆分线不能导致过于细长的子多边形
    """
    n = len(polygon)

    # 条件1: 不能是多边形的边（相邻顶点）
    if abs(i - j) % n == 1 or abs(i - j) % n == n - 1:
        return False

    # 条件2: 拆分线必须在多边形内部
    if not is_line_inside_polygon(polygon, polygon[i], polygon[j]):
        return False

    # 条件3: 拆分线不能与其他边相交（除了端点）
    if does_line_intersect_edges(polygon, i, j):
        return False

    # 条件4: 避免过于细长的子多边形（可选）
    if would_create_sliver_polygons(polygon, i, j, threshold):
        return False

    return True

def is_valid_split_line1(polygon, i, j, threshold=160):
    """
    简化有效性检查，先确保基本拆分可行
    """
    n = len(polygon)

    # 基本检查：不能是相邻顶点
    if abs(i - j) % n <= 1 or abs(i - j) % n == n - 1:
        return False

    # 先尝试拆分，如果成功则认为有效
    try:
        poly1, poly2 = split_polygon(polygon, i, j)
        # 确保拆分后的多边形至少有3个顶点
        if len(poly1) >= 3 and len(poly2) >= 3:
            return True
    except:
        pass

    return False

def is_line_inside_polygon(polygon, point1, point2):
    """
    检查线段是否完全在多边形内部
    """
    # 简单实现：检查线段中点是否在多边形内
    mid_point = ((point1[0] + point2[0]) / 2, (point1[1] + point2[1]) / 2)
    return is_point_in_polygon(mid_point, polygon)


def does_line_intersect_edges(polygon, i, j):
    """
    检查拆分线是否与多边形的其他边相交
    """
    n = len(polygon)
    line_start = polygon[i]
    line_end = polygon[j]

    for k in range(n):
        # 跳过相邻边（共享顶点的边）
        if k == i or k == j or (k + 1) % n == i or (k + 1) % n == j:
            continue

        edge_start = polygon[k]
        edge_end = polygon[(k + 1) % n]

        if do_lines_intersect(line_start, line_end, edge_start, edge_end):
            return True

    return False


def would_create_sliver_polygons(polygon, i, j, min_area_ratio=0.1):
    """
    检查拆分是否会创建过于细长的子多边形
    """
    try:
        poly1, poly2 = split_polygon(polygon, i, j)

        # 计算面积比
        area_total = polygon_area(polygon)
        area1 = polygon_area(poly1)
        area2 = polygon_area(poly2)

        min_area = min(area1, area2)
        ratio = min_area / area_total if area_total > 0 else 0

        # 如果较小的子多边形面积占比太小，认为是细长多边形
        return ratio < min_area_ratio

    except:
        return True  # 如果拆分失败，认为会创建无效多边形


def polygon_area(polygon):
    """
    计算多边形面积（使用鞋带公式）
    """
    n = len(polygon)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += polygon[i][0] * polygon[j][1]
        area -= polygon[j][0] * polygon[i][1]
    return abs(area) / 2.0


# 辅助函数（需要根据你的具体实现调整）
def is_point_in_polygon(point, polygon):
    """
    判断点是否在多边形内（使用射线法）
    """
    x, y = point
    n = len(polygon)
    inside = False

    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


def do_lines_intersect(a, b, c, d):
    """
    检查两条线段是否相交
    """

    def ccw(A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

    return ccw(a, c, d) != ccw(b, c, d) and ccw(a, b, c) != ccw(a, b, d)

def plot_polygon_decomposition(decomposition, threshold=160):
    """绘制多边形分解结果"""
    plt.figure(figsize=(8, 6))
    colors = plt.cm.tab10.colors

    for i, polygon in enumerate(decomposition):
        closed_poly = polygon + [polygon[0]]
        x, y = zip(*closed_poly)
        plt.plot(x, y, color=colors[i % len(colors)], linewidth=2)
        plt.fill(x, y, color=colors[i % len(colors)], alpha=0.3)

        # 标注顶点和角度
        for j in range(len(polygon)):
            px, py = polygon[j]
            p0 = polygon[(j - 1) % len(polygon)]
            p1 = polygon[j]
            p2 = polygon[(j + 1) % len(polygon)]
            angle, _ = calculate_angle(p0, p1, p2)

            # plt.text(px, py, f"{j}\n{angle:.1f}°", ha='center', va='center',
            #          bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))

    plt.axis('equal')
    plt.title(f"凹角阈值={threshold}° 分解为{len(decomposition)}个子多边形")
    plt.show()

####################################################################################################################################################

def recursive_split(polygon, threshold=160, current_decomposition=None, depth=0, max_depth=10, visited_states=None):
    """递归拆分多边形，添加状态跟踪防止死循环"""
    if visited_states is None:
        visited_states = set()

    if current_decomposition is None:
        current_decomposition = [polygon]

    # 生成当前状态的唯一标识（防止重复处理相同状态）
    state_key = tuple(tuple(tuple(vertex) for vertex in poly) for poly in sorted(current_decomposition, key=len))
    if state_key in visited_states:
        print(f"深度 {depth}: 状态已处理过，跳过")
        return [current_decomposition]

    visited_states.add(state_key)

    print(f"深度 {depth}: 处理 {len(current_decomposition)} 个子多边形")

    # 检查终止条件
    if depth > max_depth:
        print(f"深度 {depth}: 达到最大深度限制")
        return [current_decomposition]

    # 检查所有子多边形是否满足条件
    all_valid = True
    concave_counts = []
    for poly in current_decomposition:
        concave_count = len(find_concave_vertices(poly, threshold))
        concave_counts.append(concave_count)
        if concave_count > 1:
            all_valid = False

    print(f"凹顶点计数: {concave_counts}")

    if all_valid:
        print(f"深度 {depth}: 所有子多边形满足条件")
        return [current_decomposition]

    decompositions = []

    # 遍历每个需要拆分的子多边形
    for idx, poly in enumerate(current_decomposition):
        concave_verts = find_concave_vertices(poly, threshold)

        if len(concave_verts) <= 1:
            continue

        print(f"拆分子多边形 {idx} (有 {len(concave_verts)} 个凹顶点)")

        # 生成拆分线（限制数量防止组合爆炸）
        splits = generate_limited_splits(poly, concave_verts, threshold, max_splits=5)

        for i, j in splits:
            try:
                print(f"尝试拆分线: ({i}, {j})")
                new_poly1, new_poly2 = split_polygon(poly, i, j)

                # 检查拆分后多边形是否有效
                if len(new_poly1) < 3 or len(new_poly2) < 3:
                    print("拆分产生无效多边形，跳过")
                    continue

                # 创建新的分解
                new_decomposition = (
                        current_decomposition[:idx] +
                        [new_poly1, new_poly2] +
                        current_decomposition[idx + 1:]
                )

                # 检查新状态是否真的有改进
                if not has_improvement(current_decomposition, new_decomposition, threshold):
                    print("拆分没有改进，跳过")
                    continue

                # 递归处理新分解
                new_decomps = recursive_split(
                    polygon, threshold, new_decomposition,
                    depth + 1, max_depth, visited_states
                )

                for decomp in new_decomps:
                    decompositions.append(decomp)

            except Exception as e:
                print(f"拆分失败: {e}")
                continue

        # 每个子多边形只尝试有限次拆分
        break

    # 如果没有找到分解，返回当前状态
    if not decompositions:
        print(f"深度 {depth}: 没有找到有效拆分")
        return [current_decomposition]

    return decompositions


def generate_limited_splits(polygon, concave_vertices, threshold, max_splits=5):
    """生成有限数量的拆分线，防止组合爆炸"""
    splits = []
    n = len(polygon)

    # 优先尝试凹顶点之间的连接
    for i in range(min(len(concave_vertices), 3)):  # 限制尝试的凹顶点数量
        for j in range(i + 1, min(len(concave_vertices), i + 4)):  # 限制连接数量
            idx_i = concave_vertices[i]
            idx_j = concave_vertices[j]

            if is_valid_split_line(polygon, idx_i, idx_j, threshold):
                splits.append((idx_i, idx_j))
                if len(splits) >= max_splits:
                    return splits

    # 如果还不够，尝试凹-凸连接
    if len(splits) < max_splits:
        convex_vertices = [i for i in range(n) if i not in concave_vertices]
        for concave_idx in concave_vertices[:2]:  # 只尝试前2个凹顶点
            for convex_idx in convex_vertices[:5]:  # 只尝试前5个凸顶点
                if is_valid_split_line(polygon, concave_idx, convex_idx, threshold):
                    splits.append((concave_idx, convex_idx))
                    if len(splits) >= max_splits:
                        return splits

    return splits


def has_improvement(old_decomp, new_decomp, threshold):
    """检查新分解是否比旧分解有改进"""
    old_concave_total = sum(len(find_concave_vertices(poly, threshold)) for poly in old_decomp)
    new_concave_total = sum(len(find_concave_vertices(poly, threshold)) for poly in new_decomp)

    # 如果凹顶点总数减少，或者子多边形数量增加但凹顶点数没变差
    return (new_concave_total < old_concave_total or
            (len(new_decomp) > len(old_decomp) and new_concave_total <= old_concave_total))


def is_valid_split_line(polygon, i, j, threshold):
    """简化的有效性检查"""
    n = len(polygon)

    # 基本检查：不能是相邻顶点
    if abs(i - j) % n <= 1 or abs(i - j) % n == n - 1:
        return False

    # 尝试拆分来检查有效性
    try:
        poly1, poly2 = split_polygon(polygon, i, j)
        return len(poly1) >= 3 and len(poly2) >= 3
    except:
        return False
def iterative_split(polygon, threshold=160, max_iterations=20):
    """迭代版本的多边形拆分，避免递归死循环"""
    decompositions = [[polygon]]
    visited_states = set()

    for iteration in range(max_iterations):
        print(f"迭代 {iteration + 1}")
        new_decompositions = []
        any_improvement = False

        for decomp in decompositions:
            # 检查当前分解是否已完成
            if is_decomposition_complete(decomp, threshold):
                new_decompositions.append(decomp)
                continue

            # 尝试改进当前分解
            improved = try_improve_decomposition(decomp, threshold, visited_states)
            if improved:
                new_decompositions.extend(improved)
                any_improvement = True
            else:
                new_decompositions.append(decomp)

        if not any_improvement:
            print("没有进一步改进，终止迭代")
            break

        decompositions = new_decompositions

    return decompositions


def is_decomposition_complete(decomposition, threshold):
    """检查分解是否已完成（所有子多边形≤1个凹顶点）"""
    for poly in decomposition:
        if len(find_concave_vertices(poly, threshold)) > 1:
            return False
    return True


def try_improve_decomposition(decomposition, threshold, visited_states):
    """尝试改进分解"""
    improved_decomps = []

    for idx, poly in enumerate(decomposition):
        concave_verts = find_concave_vertices(poly, threshold)
        if len(concave_verts) <= 1:
            continue

        # 尝试有限数量的拆分
        splits = generate_limited_splits(poly, concave_verts, threshold, max_splits=3)

        for i, j in splits:
            try:
                poly1, poly2 = split_polygon(poly, i, j)
                if len(poly1) < 3 or len(poly2) < 3:
                    continue

                new_decomp = decomposition[:idx] + [poly1, poly2] + decomposition[idx + 1:]

                # 检查状态是否已访问
                state_key = tuple(tuple(tuple(vertex) for vertex in poly) for poly in sorted(new_decomp, key=len))
                if state_key in visited_states:
                    continue

                visited_states.add(state_key)

                if has_improvement(decomposition, new_decomp, threshold):
                    improved_decomps.append(new_decomp)
                    break  # 每个多边形只尝试一次成功拆分

            except Exception as e:
                print(f"拆分尝试失败: {e}")
                continue

    return improved_decomps
def visualize_with_similar_colors(svg_file):
    """
    Process SVG and visualize with original colors replaced by similar palette colors
    """
    angle_threshold = 160
    # Extract polygons with original colors
    # simplified = [(0, 0), (0.5, 0.2), (1.5, 0.5), (2.5, 0.2), (3, 0), (3, 1), (2, 1), (2, 2), (1, 2), (1, 1), (0, 1)]
    simplified = [(833.0, 1600.2), (833.2, 1600.2), (833.4, 1600.2), (833.6, 1600.1), (833.8, 1600.1), (834.0, 1600.1), (834.3, 1600.0), (834.5, 1600.0), (834.7, 1599.9), (834.9, 1599.9), (834.9, 1599.9), (835.2, 1600.1), (835.6, 1600.3), (835.9, 1600.5), (836.2, 1600.6), (836.5, 1600.7), (836.9, 1600.8), (837.2, 1600.9), (837.6, 1601.0), (838.0, 1601.1), (838.0, 1601.1), (838.4, 1601.1), (838.8, 1601.2), (839.1, 1601.3), (839.5, 1601.4), (839.9, 1601.5), (840.3, 1601.6), (840.6, 1601.7), (841.0, 1601.8), (841.4, 1601.9), (841.4, 1601.9), (841.4, 1602.0), (841.4, 1602.2), (841.4, 1602.3), (841.3, 1602.4), (841.3, 1602.5), (841.3, 1602.7), (841.3, 1602.8), (841.3, 1602.9), (841.3, 1603.0), (841.3, 1603.0), (840.9, 1603.1), (840.5, 1603.3), (840.1, 1603.4), (839.7, 1603.5), (839.3, 1603.6), (838.9, 1603.7), (838.5, 1603.8), (838.1, 1604.0), (837.7, 1604.1), (837.7, 1604.1), (837.8, 1605.0), (838.1, 1605.8), (838.5, 1606.5), (839.0, 1607.1), (839.6, 1607.8), (840.1, 1608.4), (840.6, 1609.1), (841.0, 1609.9), (841.3, 1610.8), (841.3, 1610.8), (841.0, 1610.8), (840.7, 1610.8), (840.5, 1610.9), (840.2, 1610.9), (840.0, 1611.0), (839.7, 1611.0), (839.4, 1611.0), (839.2, 1611.1), (838.9, 1611.1), (838.9, 1611.1), (838.7, 1610.9), (838.5, 1610.7), (838.2, 1610.4), (838.0, 1610.2), (837.8, 1610.0), (837.6, 1609.8), (837.4, 1609.5), (837.1, 1609.3), (836.9, 1609.1), (836.9, 1609.1), (836.9, 1609.2), (836.8, 1609.3), (836.7, 1609.4), (836.6, 1609.5), (836.5, 1609.6), (836.5, 1609.7), (836.4, 1609.8), (836.3, 1609.9), (836.2, 1610.0), (836.2, 1610.0), (836.2, 1610.1), (836.1, 1610.1), (836.0, 1610.2), (836.0, 1610.2), (835.9, 1610.3), (835.8, 1610.3), (835.7, 1610.4), (835.7, 1610.4), (835.6, 1610.5), (835.6, 1610.5), (835.1, 1610.8), (834.6, 1611.1), (834.2, 1611.4), (833.8, 1611.6), (833.4, 1611.8), (833.0, 1611.9), (832.5, 1611.9), (832.0, 1611.9), (831.4, 1611.8), (831.4, 1611.8), (831.1, 1611.4), (830.9, 1611.0), (830.7, 1610.6), (830.4, 1610.3), (830.2, 1609.9), (829.9, 1609.6), (829.6, 1609.3), (829.3, 1609.0), (828.9, 1608.7), (828.9, 1608.7), (828.6, 1608.9), (828.3, 1609.1), (828.0, 1609.2), (827.7, 1609.4), (827.5, 1609.6), (827.2, 1609.8), (826.9, 1610.0), (826.6, 1610.1), (826.3, 1610.3), (826.3, 1610.3), (826.3, 1610.2), (826.2, 1610.2), (826.1, 1610.1), (826.0, 1610.0), (826.0, 1609.9), (825.9, 1609.9), (825.8, 1609.8), (825.8, 1609.7), (825.7, 1609.6), (825.7, 1609.6), (826.0, 1609.1), (826.3, 1608.5), (826.7, 1607.9), (827.0, 1607.4), (827.3, 1606.8), (827.6, 1606.2), (827.9, 1605.6), (828.2, 1605.0), (828.5, 1604.4), (828.5, 1604.4), (828.1, 1604.3), (827.7, 1604.2), (827.3, 1604.0), (826.9, 1603.9), (826.6, 1603.7), (826.3, 1603.5), (826.0, 1603.3), (825.6, 1603.0), (825.3, 1602.7), (825.3, 1602.7), (825.7, 1602.3), (826.3, 1601.9), (827.1, 1601.6), (828.0, 1601.4), (828.9, 1601.2), (829.9, 1601.0), (830.8, 1600.8), (831.6, 1600.6), (832.3, 1600.4), (832.3, 1600.4), (832.4, 1600.4), (832.5, 1600.4), (832.6, 1600.4), (832.6, 1600.3), (832.7, 1600.3), (832.8, 1600.3), (832.8, 1600.3), (832.9, 1600.3), (833.0, 1600.2)]
    all_decompositions = iterative_split(simplified, angle_threshold)#ok
    # all_decompositions = recursive_split(simplified, threshold=160, max_depth=5)#死循环
    print("visualize_with_similar_colors len all_decompositions:", len(all_decompositions))
    for i, decomposition in enumerate(all_decompositions):
        print(f"分解方案 {i + 1}:")
        plot_polygon_decomposition(decomposition, angle_threshold)

###############################################################################
import math


def find_concave_vertices(polygon, threshold=160):
    """
    查找多边形中的所有凹顶点
    """
    n = len(polygon)
    concave_vertices = []

    for i in range(n):
        prev_point = polygon[(i - 1) % n]
        current_point = polygon[i]
        next_point = polygon[(i + 1) % n]

        if is_concave(prev_point, current_point, next_point, threshold):
            concave_vertices.append(i)

    return concave_vertices


def is_concave(prev_point, current_point, next_point, threshold=160):
    """
    判断一个顶点是否是凹顶点
    """
    angle, is_reflex = calculate_angle(prev_point, current_point, next_point)

    # 如果是凹角且角度小于阈值，认为是凹顶点
    return is_reflex and angle < threshold


def calculate_angle(p0, p1, p2):
    """
    计算三个点形成的角度和凹凸性
    返回: (角度, 是否是凹角)
    """
    # 向量 v1 = p1->p0, v2 = p1->p2
    v1 = (p0[0] - p1[0], p0[1] - p1[1])
    v2 = (p2[0] - p1[0], p2[1] - p1[1])

    # 计算叉积判断凹凸性
    cross = v1[0] * v2[1] - v1[1] * v2[0]
    is_reflex = cross < 0  # 在右手坐标系中，负叉积表示凹角

    # 计算角度
    dot = v1[0] * v2[0] + v1[1] * v2[1]
    mag1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
    mag2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)

    if mag1 * mag2 == 0:
        return 180, is_reflex

    cos_angle = dot / (mag1 * mag2)
    # 防止浮点误差导致超出 [-1, 1] 范围
    cos_angle = max(-1, min(1, cos_angle))
    angle = math.degrees(math.acos(cos_angle))

    return angle, is_reflex


def analyze_polygon_angles(polygon, threshold=160):
    """
    分析多边形所有顶点的角度信息
    """
    n = len(polygon)
    print("顶点角度分析:")
    print("索引 | 坐标 | 角度 | 是否凹顶点")
    print("-" * 50)

    for i in range(n):
        prev_point = polygon[(i - 1) % n]
        current_point = polygon[i]
        next_point = polygon[(i + 1) % n]

        angle, is_reflex = calculate_angle(prev_point, current_point, next_point)
        is_concave_vertex = is_reflex and angle < threshold

        print(f"{i:3d} | {current_point} | {angle:6.1f}° | {is_concave_vertex}")

    concave_verts = find_concave_vertices(polygon, threshold)
    print(f"\n凹顶点总数: {len(concave_verts)}")
    print(f"凹顶点索引: {concave_verts}")

    return concave_verts


if __name__ == "__main__":
    # visualize_with_similar_colors("testSVG/jimeng-little-girl.svg")

    # 测试你的多边形
    your_polygon = [(833.0, 1600.2), (833.2, 1600.2), (833.4, 1600.2), (833.6, 1600.1), (833.8, 1600.1), (834.0, 1600.1), (834.3, 1600.0), (834.5, 1600.0), (834.7, 1599.9), (834.9, 1599.9), (834.9, 1599.9), (835.2, 1600.1), (835.6, 1600.3), (835.9, 1600.5), (836.2, 1600.6), (836.5, 1600.7), (836.9, 1600.8), (837.2, 1600.9), (837.6, 1601.0), (838.0, 1601.1), (838.0, 1601.1), (838.4, 1601.1), (838.8, 1601.2), (839.1, 1601.3), (839.5, 1601.4), (839.9, 1601.5), (840.3, 1601.6), (840.6, 1601.7), (841.0, 1601.8), (841.4, 1601.9), (841.4, 1601.9), (841.4, 1602.0), (841.4, 1602.2), (841.4, 1602.3), (841.3, 1602.4), (841.3, 1602.5), (841.3, 1602.7), (841.3, 1602.8), (841.3, 1602.9), (841.3, 1603.0), (841.3, 1603.0), (840.9, 1603.1), (840.5, 1603.3), (840.1, 1603.4), (839.7, 1603.5), (839.3, 1603.6), (838.9, 1603.7), (838.5, 1603.8), (838.1, 1604.0), (837.7, 1604.1), (837.7, 1604.1), (837.8, 1605.0), (838.1, 1605.8), (838.5, 1606.5), (839.0, 1607.1), (839.6, 1607.8), (840.1, 1608.4), (840.6, 1609.1), (841.0, 1609.9), (841.3, 1610.8), (841.3, 1610.8), (841.0, 1610.8), (840.7, 1610.8), (840.5, 1610.9), (840.2, 1610.9), (840.0, 1611.0), (839.7, 1611.0), (839.4, 1611.0), (839.2, 1611.1), (838.9, 1611.1), (838.9, 1611.1), (838.7, 1610.9), (838.5, 1610.7), (838.2, 1610.4), (838.0, 1610.2), (837.8, 1610.0), (837.6, 1609.8), (837.4, 1609.5), (837.1, 1609.3), (836.9, 1609.1), (836.9, 1609.1), (836.9, 1609.2), (836.8, 1609.3), (836.7, 1609.4), (836.6, 1609.5), (836.5, 1609.6), (836.5, 1609.7), (836.4, 1609.8), (836.3, 1609.9), (836.2, 1610.0), (836.2, 1610.0), (836.2, 1610.1), (836.1, 1610.1), (836.0, 1610.2), (836.0, 1610.2), (835.9, 1610.3), (835.8, 1610.3), (835.7, 1610.4), (835.7, 1610.4), (835.6, 1610.5), (835.6, 1610.5), (835.1, 1610.8), (834.6, 1611.1), (834.2, 1611.4), (833.8, 1611.6), (833.4, 1611.8), (833.0, 1611.9), (832.5, 1611.9), (832.0, 1611.9), (831.4, 1611.8), (831.4, 1611.8), (831.1, 1611.4), (830.9, 1611.0), (830.7, 1610.6), (830.4, 1610.3), (830.2, 1609.9), (829.9, 1609.6), (829.6, 1609.3), (829.3, 1609.0), (828.9, 1608.7), (828.9, 1608.7), (828.6, 1608.9), (828.3, 1609.1), (828.0, 1609.2), (827.7, 1609.4), (827.5, 1609.6), (827.2, 1609.8), (826.9, 1610.0), (826.6, 1610.1), (826.3, 1610.3), (826.3, 1610.3), (826.3, 1610.2), (826.2, 1610.2), (826.1, 1610.1), (826.0, 1610.0), (826.0, 1609.9), (825.9, 1609.9), (825.8, 1609.8), (825.8, 1609.7), (825.7, 1609.6), (825.7, 1609.6), (826.0, 1609.1), (826.3, 1608.5), (826.7, 1607.9), (827.0, 1607.4), (827.3, 1606.8), (827.6, 1606.2), (827.9, 1605.6), (828.2, 1605.0), (828.5, 1604.4), (828.5, 1604.4), (828.1, 1604.3), (827.7, 1604.2), (827.3, 1604.0), (826.9, 1603.9), (826.6, 1603.7), (826.3, 1603.5), (826.0, 1603.3), (825.6, 1603.0), (825.3, 1602.7), (825.3, 1602.7), (825.7, 1602.3), (826.3, 1601.9), (827.1, 1601.6), (828.0, 1601.4), (828.9, 1601.2), (829.9, 1601.0), (830.8, 1600.8), (831.6, 1600.6), (832.3, 1600.4), (832.3, 1600.4), (832.4, 1600.4), (832.5, 1600.4), (832.6, 1600.4), (832.6, 1600.3), (832.7, 1600.3), (832.8, 1600.3), (832.8, 1600.3), (832.9, 1600.3), (833.0, 1600.2)]
    print("=== 多边形分析 ===")
    concave_verts = analyze_polygon_angles(your_polygon)