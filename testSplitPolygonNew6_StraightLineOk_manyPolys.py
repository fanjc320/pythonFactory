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

    # 计算叉积确定方向
    cross = np.cross(v1, v2)

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


def recursive_split(polygon, threshold=160, current_decomposition=None, depth=0, max_depth=10):
    """递归拆分多边形，添加深度限制防止无限递归"""
    if depth > max_depth:
        return [current_decomposition]

    if current_decomposition is None:
        print("recursive_split current_decomposition is None")
        current_decomposition = [polygon]

    concave_counts = [len(find_concave_vertices(p, threshold)) for p in current_decomposition]
    print("recursive_split len concave_counts:", len(concave_counts), " depth:", depth)
    if all(cnt <= 1 for cnt in concave_counts):
        return [current_decomposition]

    decompositions = []

    for idx, subpoly in enumerate(current_decomposition):
        concave_verts = find_concave_vertices(subpoly, threshold)
        if len(concave_verts) <= 1:
            continue

        splits = generate_all_splits(subpoly, threshold)
        for i, j in splits:
            new_poly1, new_poly2 = split_polygon(subpoly, i, j)
            new_decomposition = current_decomposition[:idx] + [new_poly1, new_poly2] + current_decomposition[idx + 1:]

            # 递归处理新分解
            new_decomps = recursive_split(polygon, threshold, new_decomposition, depth + 1, max_depth)
            for decomp in new_decomps:
                # 检查是否已经存在相同的分解
                if not any(all(p in prev_decomp for p in decomp) for prev_decomp in decompositions):
                    decompositions.append(decomp)

    return decompositions if decompositions else [current_decomposition]


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


# # 示例多边形
# polygon = [(0, 0), (0.5, 0.2), (1.5, 0.5), (2.5, 0.2), (3, 0), (3, 1), (2, 1), (2, 2), (1, 2), (1, 1), (0, 1)]
#
# 设置凹角阈值（度）
angle_threshold = 160
#
# # 找出所有可能的分解
# all_decompositions = recursive_split(polygon, angle_threshold)
#
# # 绘制每种分解方式
# for i, decomposition in enumerate(all_decompositions):
#     print(f"分解方案 {i + 1}:")
#     plot_polygon_decomposition(decomposition, angle_threshold)

# Custom color palette
custom_palette = [
    '#FF0000', '#FF7F00', '#FFFF00', '#7FFF00', '#00FF00',
    '#00FF7F', '#00FFFF', '#007FFF', '#0000FF', '#7F00FF',
    '#FF00FF', '#FF007F', '#FF5733', '#33FF57', '#3357FF',
    '#F033FF', '#FF33F0', '#33FFF0', '#FFD700', '#9400D3'
]
def visualize_with_similar_colors(svg_file, custom_palette):
    """
    Process SVG and visualize with original colors replaced by similar palette colors
    """
    # Extract polygons with original colors
    # colored_polygons = extract_polygons_with_colors(svg_file, 1)
    colored_polygons = extract_polygons_with_colors(svg_file, 10)
    print("visualize_with_similar_colors colored_polygons type:", type(colored_polygons), " len:", len(colored_polygons))
    print("----------------------------------colored_polygons:", colored_polygons[:2])
    count =0
    for polygon in colored_polygons:
        if count > 3:
            break
        print("visualize_with_similar_colors polygon type:", type(polygon[0]), " len:", len(polygon[0]), type(polygon[0][0]))
        # simplified, count, tol = rdp_simplify(complex_coords, 0.01, max_points=150)
        # recursive_type_compact(polygon[0])
        print("----------------------------------polygon[0]:", polygon[0][:20]) # [(0.0, 0.0), (0.10001068490223315, 0.0), (0.200021
        # print("----------------------------------polygon[1]:", polygon[1][:20]) # #A043CE
        # print("----------------------------------polygon[2]:", polygon[2][:20])#越界了
        simplified, count, tol = rdp_simplify(polygon[0], 0.01, max_points=150)
        print("visualize_with_similar_colors simplified type:", type(simplified), " len:", len(simplified), " count:", count)
        # print("visualize_with_similar_colors polygon:", polygon)
        all_decompositions = recursive_split(simplified, angle_threshold)
        # print("visualize_with_similar_colors all_decompositions:", all_decompositions)
        print("visualize_with_similar_colors len all_decompositions:", len(all_decompositions))
        for i, decomposition in enumerate(all_decompositions):
            print(f"分解方案 {i + 1}:")
            plot_polygon_decomposition(decomposition, angle_threshold)
        ++count

if __name__ == "__main__":
    visualize_with_similar_colors("testSVG/jimeng-little-girl.svg", custom_palette)