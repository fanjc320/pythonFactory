import math
from common.polygon_plot_index import draw_polygon_with_labels
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon
# from shapely.plotting import plot_polygon
from common.Polygon_Compare import *
import matplotlib
matplotlib.use('Qt5Agg')
def find_concave_vertices(polygon, threshold=160):
    """
    查找多边形的凹顶点
    基于角度阈值判断顶点是否为凹顶点
    """
    concave_vertices = []
    n = len(polygon)

    for i in range(n):
        # 获取前一个、当前和后一个顶点
        index_p = (i - 1) % n
        index_c = i
        index_n = (i + 1) % n
        prev = polygon[index_p]
        curr = polygon[index_c]
        next_ = polygon[index_n]
        # print(f"polygon:{polygon}")
        # print(f"find_concave_vertices i:{i} ip:{index_p} ic:{index_c} in:{index_n} p:{prev} c:{curr} n:{next_}")

        # 计算向量
        v1 = (prev[0] - curr[0], prev[1] - curr[1])
        v2 = (next_[0] - curr[0], next_[1] - curr[1])

        # 计算角度
        angle = calculate_internal_angle(v1, v2)
        # print(f"find_concave_vertices xxxx i:{i} angle:{angle} threshold:{threshold}")

        # if angle > threshold:  # 角度大于阈值，认为是凹顶点
        #     concave_vertices.append(i)
        if angle < threshold:  # 角度大于阈值，认为是凹顶点
            concave_vertices.append(i)
    return concave_vertices


def find_concave_vertices_with_indices(indices, threshold=2.6):
    """查找凹顶点（使用索引），返回全局索引"""
    global global_polygon
    poly = [global_polygon[i] for i in indices]
    local_concave_verts = find_concave_vertices(poly, threshold)

    # 将局部索引转换为全局索引
    global_concave_verts = [indices[i] for i in local_concave_verts]
    return global_concave_verts


# 或者如果需要同时返回局部和全局索引，可以这样：
def find_concave_vertices_with_indices_detailed(indices, threshold=2.6):
    """查找凹顶点（使用索引），返回局部索引和全局索引"""
    global global_polygon
    poly = [global_polygon[i] for i in indices]
    local_concave_verts = find_concave_vertices(poly, threshold)

    # 将局部索引转换为全局索引
    global_concave_verts = [indices[i] for i in local_concave_verts]
    return local_concave_verts, global_concave_verts

#有bug,可能不是内角的角度
def calculate_angle(v1, v2):
    """
    计算两个向量之间的角度（0-180度）
    """
    dot_product = v1[0] * v2[0] + v1[1] * v2[1]
    mag_v1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
    mag_v2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)

    if mag_v1 * mag_v2 == 0:
        return 0

    cos_angle = dot_product / (mag_v1 * mag_v2)
    cos_angle = max(-1, min(1, cos_angle))  # 确保在有效范围内
    angle_rad = math.acos(cos_angle)
    angle_deg = math.degrees(angle_rad)

    return angle_deg

def calculate_internal_angle(vec1, vec2):
    # # 计算两个向量
    # vec1 = (prev[0] - current[0], prev[1] - current[1])
    # vec2 = (next_v[0] - current[0], next_v[1] - current[1])
    # 计算点积
    dot = vec1[0] * vec2[0] + vec1[1] * vec2[1]
    # 计算向量模长
    mag1 = math.sqrt(vec1[0] ** 2 + vec1[1] ** 2)
    mag2 = math.sqrt(vec2[0] ** 2 + vec2[1] ** 2)
    if mag1 * mag2 == 0:
        # print(f"calculate_internal_angles 共线 vec1:{vec1} vec2:{vec2}")
        return math.pi
    # 计算夹角
    cos_theta = dot / (mag1 * mag2)
    cos_theta = max(min(cos_theta, 1.0), -1.0)
    theta = math.acos(cos_theta)
    # 计算叉积判断方向
    cross = vec1[0] * vec2[1] - vec1[1] * vec2[0]
    # 确定内角
    # internal_angle = 0
    if cross >= 0:
        internal_angle = theta
    else:
        internal_angle = 2 * math.pi - theta
    # print(f"calculate_internal_angles internal_angle:{internal_angle} vec1:{vec1} vec2:{vec2} dot:{dot} cos_theta:{cos_theta}:theta:{theta}")
    return internal_angle

def split_polygon(polygon, i, j):
    """
    在多边形的顶点i和j之间进行拆分
    返回两个新的多边形
    """
    n = len(polygon)

    # 确保 i < j
    if i > j:
        i, j = j, i

    # 创建第一个多边形 (i 到 j)
    poly1 = polygon[i:j + 1]

    # 创建第二个多边形 (j 到 end 和 0 到 i)
    poly2 = polygon[j:] + polygon[:i + 1]

    # 确保多边形是闭合的（首尾顶点相同）
    if poly1[0] != poly1[-1]:
        poly1.append(poly1[0])
    if poly2[0] != poly2[-1]:
        poly2.append(poly2[0])

    return poly1, poly2


def is_valid_split(polygon, i, j):
    """
    检查从顶点i到顶点j的拆分线是否有效

    参数:
    polygon: 多边形顶点列表
    i, j: 要连接的顶点索引

    返回:
    bool: 拆分线是否有效
    """
    n = len(polygon)

    # 1. 检查是否是相邻顶点（边）
    if abs(i - j) == 1 or abs(i - j) == n - 1:
        print(f"is_valid_split 000 ij:{i,j}")
        return False

    # 2. 检查拆分线是否在多边形内部
    if not is_diagonal_inside_polygon(polygon, i, j):
        print(f"is_valid_split 111 ij:{i, j} poly:{polygon}")
        return False

    # 3. 检查拆分线是否与多边形的其他边相交
    if does_split_intersect_edges(polygon, i, j):
        print(f"is_valid_split 222 ij:{i, j}")
        return False

    return True


def is_diagonal_inside_polygon(polygon, i, j):
    # """
    # 检查对角线是否在多边形内部
    # 使用叉积法判断对角线是否在多边形内部
    # """
    # n = len(polygon)
    #
    # # 获取顶点
    # a = polygon[(i - 1) % n]
    # b = polygon[i]
    # c = polygon[(i + 1) % n]
    # d = polygon[j]
    #
    # # 计算向量
    # ab = (b[0] - a[0], b[1] - a[1])
    # bc = (c[0] - b[0], c[1] - b[1])
    # bd = (d[0] - b[0], d[1] - b[1])
    #
    # # 计算叉积
    # cross_abc = ab[0] * bc[1] - ab[1] * bc[0]  # ab × bc
    # cross_abd = ab[0] * bd[1] - ab[1] * bd[0]  # ab × bd
    #
    # # 如果两个叉积同号，说明对角线在多边形内部
    # return cross_abc * cross_abd > 0

    mid_point = ((polygon[i][0] + polygon[j][0]) / 2,
                 (polygon[i][1] + polygon[j][1]) / 2)
    # print(f"is_diagonal_inside_polygon mid:{mid_point} poly:{polygon} res:{is_point_in_polygon(mid_point, polygon)}")
    if not is_point_in_polygon(mid_point, polygon):
        return False
    return True


def does_split_intersect_edges(polygon, i, j):
    """
    检查拆分线是否与多边形的其他边相交
    """
    n = len(polygon)
    line1 = (polygon[i], polygon[j])

    # 检查与所有非相邻边的相交情况
    for k in range(n):
        # 跳过相邻边（包括拆分线本身）
        if k == i or k == j or (k + 1) % n == i or (k + 1) % n == j:
            continue

        line2 = (polygon[k], polygon[(k + 1) % n])

        if do_lines_intersect(line1, line2):
            return True

    return False


def do_lines_intersect(line1, line2):
    """
    检查两条线段是否相交
    使用快速排斥实验和跨立实验
    """
    a, b = line1
    c, d = line2

    # 快速排斥实验
    if (max(a[0], b[0]) < min(c[0], d[0]) or
            max(c[0], d[0]) < min(a[0], b[0]) or
            max(a[1], b[1]) < min(c[1], d[1]) or
            max(c[1], d[1]) < min(a[1], b[1])):
        return False

    # 跨立实验
    def cross_product(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    # 检查点c,d是否在线段ab的两侧
    cross1 = cross_product(a, b, c)
    cross2 = cross_product(a, b, d)

    # 检查点a,b是否在线段cd的两侧
    cross3 = cross_product(c, d, a)
    cross4 = cross_product(c, d, b)

    # 如果两条线段相交，那么跨立实验的结果应该异号
    return (cross1 * cross2 <= 0) and (cross3 * cross4 <= 0)


# 简化版本（如果上面的实现太复杂，可以使用这个简化版本）
def is_valid_split_simple(polygon, i, j):
    """
    简化版本的拆分线有效性检查
    """
    n = len(polygon)

    # 1. 不能是相邻顶点
    if abs(i - j) == 1 or abs(i - j) == n - 1:
        return False

    # 2. 检查拆分线是否完全在多边形内部（简化检查）
    # 这里可以使用更简单的方法，比如检查中点是否在多边形内部
    mid_point = ((polygon[i][0] + polygon[j][0]) / 2,
                 (polygon[i][1] + polygon[j][1]) / 2)

    if not is_point_in_polygon(mid_point, polygon):
        return False

    return True


def is_point_in_polygon(point, polygon):
    """
    判断点是否在多边形内部（射线法）
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
def generate_promising_splits(poly, concave_verts, threshold=2.6):
    """生成有希望的拆分线，并打印全局索引信息"""
    global global_polygon

    splits = []
    n = len(poly)

    # 打印输入信息
    print(f"\n=== 生成拆分线 ===")
    print(f"多边形顶点数: {n}")
    print(f"凹顶点局部索引: {concave_verts}")

    # 获取全局索引信息（如果可能）
    try:
        # 假设 poly 是从 global_polygon 提取的
        global_indices = []
        for vertex in poly:
            if vertex in global_polygon:
                global_indices.append(global_polygon.index(vertex))
            else:
                global_indices.append(-1)  # 无法找到对应的全局索引

        print(f"多边形全局索引: {global_indices}")
        print(f"凹顶点全局索引: {[global_indices[i] for i in concave_verts if i < len(global_indices)]}")
    except:
        print("无法确定全局索引信息")

    # 生成所有可能的凹顶点对拆分线
    for i in range(len(concave_verts)):
        for j in range(i + 1, len(concave_verts)):
            idx1 = concave_verts[i]
            idx2 = concave_verts[j]
            print(f"-----可能的拆分线: ({global_indices[idx1]}, {global_indices[idx2]})")
            # 检查拆分线是否有效（不能是相邻顶点）
            if abs(idx1 - idx2) == 1 or abs(idx1 - idx2) == n - 1:
                print(f"-----可能的拆分线 continue : ({global_indices[idx1]}, {global_indices[idx2]})")
                continue

            # 检查拆分线是否在多边形内部
            if is_valid_split(poly, idx1, idx2):
                splits.append((idx1, idx2))

                # 打印拆分线信息
                try:
                    global_idx1 = global_indices[idx1] if idx1 < len(global_indices) else -1
                    global_idx2 = global_indices[idx2] if idx2 < len(global_indices) else -1
                    print(f"拆分线: 局部({idx1}, {idx2}) -> 全局({global_idx1}, {global_idx2})")
                except:
                    print(f"拆分线: 局部({idx1}, {idx2})")
            else:
                print(f"-----可能的拆分线 not valid: ({global_indices[idx1]}, {global_indices[idx2]})")


    print(f"总共生成 {len(splits)} 条拆分线")
    print("==================\n")

    return splits


# 修改 recursive_split 函数中的调用部分
def recursive_split(part_indices, threshold=2.6, current_decomposition=None, depth=0, max_depth=10,
                    visited_states=None):
    """递归拆分多边形（使用索引表示部分），添加状态跟踪防止死循环"""
    global global_polygon

    if visited_states is None:
        visited_states = set()

    if current_decomposition is None:
        current_decomposition = [part_indices]

    # 生成当前状态的唯一标识
    state_key = tuple(
        tuple(indices) for indices in sorted(current_decomposition, key=lambda x: (len(x), x[0] if x else 0)))
    if state_key in visited_states:
        return [current_decomposition]

    visited_states.add(state_key)

    # 检查终止条件
    if depth > max_depth:
        return [current_decomposition]

    # 检查所有子多边形是否满足条件
    all_valid = True
    for indices in current_decomposition:
        if len(find_concave_vertices_with_indices(indices, threshold)) > 1:
            all_valid = False
            break

    if all_valid:
        return [current_decomposition]

    decompositions = []

    # 遍历每个需要拆分的子多边形
    for idx, indices in enumerate(current_decomposition):
        # 获取凹顶点（全局索引）
        global_concave_verts = find_concave_vertices_with_indices(indices, threshold)

        if len(global_concave_verts) <= 1:
            continue

        # 从全局多边形中提取当前部分的多边形
        poly = [global_polygon[i] for i in indices]

        # 将全局凹顶点索引转换为局部索引
        local_concave_verts = []
        for global_idx in global_concave_verts:
            if global_idx in indices:
                local_concave_verts.append(indices.index(global_idx))

        print(f"\n深度 {depth}: 处理子多边形 {idx}")
        print(f"全局索引: {indices}")
        print(f"凹顶点全局索引: {global_concave_verts}")
        print(f"凹顶点局部索引: {local_concave_verts}")

        # 生成拆分线（使用局部索引）
        splits = generate_promising_splits(poly, local_concave_verts, threshold)
        print(f"所有拆分对 splits: {splits}")
        # 修复：添加对 splits 是否为空的检查
        if not splits:
            print("没有生成有效的拆分线")
            continue

        for split_pair in splits:
            try:
                # 确保 split_pair 包含两个索引
                if len(split_pair) != 2:
                    continue

                i, j = split_pair

                print(
                    f"尝试拆分: 局部索引({i}, {j}) -> 全局索引({indices[i] if i < len(indices) else 'N/A'}, {indices[j] if j < len(indices) else 'N/A'})")

                # 拆分多边形（使用局部索引）
                new_poly1, new_poly2 = split_polygon(poly, i, j)

                # 检查拆分后多边形是否有效
                if len(new_poly1) < 3 or len(new_poly2) < 3:
                    print("拆分后多边形顶点数不足")
                    continue

                # 将局部索引转换回全局索引
                if i in range(len(poly)) and j in range(len(poly)):
                    # 确定拆分路径
                    if i < j:
                        path1 = indices[i:j + 1]
                        path2 = indices[j:] + indices[:i + 1]
                    else:
                        path1 = indices[i:] + indices[:j + 1]
                        path2 = indices[j:i + 1]

                    # 创建两个新的索引序列
                    indices1 = path1
                    indices2 = path2

                    # 检查索引序列是否有效（至少3个顶点）
                    if len(indices1) < 3 or len(indices2) < 3:
                        print(f"拆分后索引序列无效: {len(indices1)}, {len(indices2)}")
                        continue

                    print(f"拆分成功: 子多边形1索引 {indices1}")
                    print(f"拆分成功: 子多边形2索引 {indices2}")

                    # 创建新的分解
                    new_decomposition = (
                            current_decomposition[:idx] +
                            [indices1, indices2] +
                            current_decomposition[idx + 1:]
                    )

                    # 递归处理新分解
                    new_decomps = recursive_split(
                        part_indices, threshold, new_decomposition,
                        depth + 1, max_depth, visited_states
                    )

                    for decomp in new_decomps:
                        decompositions.append(decomp)

            except Exception as e:
                print(f"拆分过程中出错: {e}")
                import traceback
                traceback.print_exc()
                continue

        # 每个子多边形只尝试一次拆分
        if decompositions:
            break

    # 如果没有找到分解，返回当前状态
    if not decompositions:
        return [current_decomposition]

    return decompositions
def is_valid_split_line(polygon, i, j, threshold=160):
    """完整检查拆分线是否有效"""
    n = len(polygon)

    # 1. 检查是否是多边形的边
    if abs(i - j) % n == 1 or abs(i - j) % n == n - 1:
        return False

    # 2. 检查拆分线是否在多边形内部
    if not is_line_inside_polygon(polygon, polygon[i], polygon[j]):
        return False

    # 3. 检查是否与其他边相交
    if does_line_intersect_other_edges(polygon, i, j):
        return False

    # 4. 检查拆分后是否产生有效多边形
    if not produces_valid_polygons(polygon, i, j):
        return False

    return True


def is_line_inside_polygon(polygon, point1, point2):
    """检查线段是否完全在多边形内部"""
    # 检查端点
    if not is_point_in_polygon(point1, polygon) or not is_point_in_polygon(point2, polygon):
        return False

    # 检查线段上的中间点
    num_samples = 3
    for k in range(1, num_samples):
        t = k / num_samples
        sample_point = (
            point1[0] + t * (point2[0] - point1[0]),
            point1[1] + t * (point2[1] - point1[1])
        )
        if not is_point_in_polygon(sample_point, polygon):
            return False

    return True


def does_line_intersect_other_edges(polygon, i, j):
    """检查拆分线是否与多边形的其他非相邻边相交"""
    n = len(polygon)
    line_start = polygon[i]
    line_end = polygon[j]

    for k in range(n):
        next_k = (k + 1) % n
        if k == i or k == j or next_k == i or next_k == j:
            continue

        edge_start = polygon[k]
        edge_end = polygon[next_k]

        if do_segments_intersect(line_start, line_end, edge_start, edge_end):
            return True

    return False


def produces_valid_polygons(polygon, i, j):
    """检查拆分后是否产生有效的多边形"""
    try:
        poly1, poly2 = split_polygon(polygon, i, j)
        return len(poly1) >= 3 and len(poly2) >= 3
    except:
        return False


def do_segments_intersect(a, b, c, d):
    """检查两条线段是否相交"""

    def cross_product(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    o1 = cross_product(a, b, c)
    o2 = cross_product(a, b, d)
    o3 = cross_product(c, d, a)
    o4 = cross_product(c, d, b)

    if o1 * o2 < 0 and o3 * o4 < 0:
        return True

    return False


def is_point_in_polygon(point, polygon):
    """判断点是否在多边形内（使用射线法）"""
    x, y = point
    n = len(polygon)
    inside = False

    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
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


def iterative_split(polygon, threshold=160, max_iterations=20):
    """迭代版本的多边形拆分，避免递归死循环"""
    decompositions = [[polygon]]
    visited_states = set()

    for iteration in range(max_iterations):
        new_decompositions = []
        any_improvement = False

        for decomp in decompositions:
            if is_decomposition_complete(decomp, threshold):
                new_decompositions.append(decomp)
                continue

            improved = try_improve_decomposition(decomp, threshold, visited_states)
            if improved:
                new_decompositions.extend(improved)
                any_improvement = True
            else:
                new_decompositions.append(decomp)

        if not any_improvement:
            break

        decompositions = new_decompositions

    return decompositions


def is_decomposition_complete(decomposition, threshold):
    """检查分解是否已完成"""
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

        splits = generate_promising_splits(poly, concave_verts, threshold)

        for i, j in splits:
            try:
                poly1, poly2 = split_polygon(poly, i, j)
                if len(poly1) < 3 or len(poly2) < 3:
                    continue

                new_decomp = decomposition[:idx] + [poly1, poly2] + decomposition[idx + 1:]

                state_key = tuple(tuple(tuple(vertex) for vertex in poly) for poly in
                                  sorted(new_decomp, key=lambda x: (len(x), tuple(x[0]) if x else (0, 0))))
                if state_key in visited_states:
                    continue

                visited_states.add(state_key)
                improved_decomps.append(new_decomp)
                break

            except:
                continue

    return improved_decomps


def visualize_decomposition(polygon, decomposition):
    """可视化分解结果"""
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches

        fig, ax = plt.subplots(figsize=(10, 8))
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown']

        # 绘制原始多边形
        x = [p[0] for p in polygon] + [polygon[0][0]]
        y = [p[1] for p in polygon] + [polygon[0][1]]
        ax.plot(x, y, 'k-', linewidth=2, label='Original')

        # 绘制分解后的子多边形
        for i, poly in enumerate(decomposition):
            color = colors[i % len(colors)]
            poly_x = [p[0] for p in poly] + [poly[0][0]]
            poly_y = [p[1] for p in poly] + [poly[0][1]]
            ax.fill(poly_x, poly_y, alpha=0.3, color=color)
            ax.plot(poly_x, poly_y, '-', color=color, linewidth=2, label=f'Part {i + 1}')

        ax.axis('equal')
        ax.legend()
        plt.title(f'Polygon Decomposition ({len(decomposition)} parts)')
        plt.show()

    except ImportError:
        print("Matplotlib not available for visualization")


def recursive_split(global_polygon, part_indices, threshold=2.6, current_decomposition=None, depth=0, max_depth=10,
                    visited_states=None):
    """递归拆分多边形（使用索引表示部分），添加状态跟踪防止死循环"""
    if visited_states is None:
        visited_states = set()

    if current_decomposition is None:
        current_decomposition = [part_indices]

    # 生成当前状态的唯一标识
    state_key = tuple(
        tuple(indices) for indices in sorted(current_decomposition, key=lambda x: (len(x), x[0] if x else 0)))
    if state_key in visited_states:
        return [current_decomposition]

    visited_states.add(state_key)

    # 检查终止条件
    if depth > max_depth:
        return [current_decomposition]

    # 检查所有子多边形是否满足条件
    all_valid = True
    for indices in current_decomposition:
        # 从全局多边形中提取当前部分的多边形
        poly = [global_polygon[i] for i in indices]
        if len(find_concave_vertices(poly, threshold)) > 1:
            all_valid = False
            break

    if all_valid:
        return [current_decomposition]

    decompositions = []

    # 遍历每个需要拆分的子多边形
    for idx, indices in enumerate(current_decomposition):
        # 从全局多边形中提取当前部分的多边形
        poly = [global_polygon[i] for i in indices]
        concave_verts = find_concave_vertices(poly, threshold)

        if len(concave_verts) <= 1:
            continue

        # 生成拆分线（使用局部索引）
        splits = generate_promising_splits(poly, concave_verts, threshold)

        for i, j in splits:
            try:
                # 拆分多边形（使用局部索引）
                new_poly1, new_poly2 = split_polygon(poly, i, j)

                # 检查拆分后多边形是否有效
                if len(new_poly1) < 3 or len(new_poly2) < 3:
                    continue

                # 将局部索引转换回全局索引
                # 注意：这里需要根据拆分后的顶点重新映射到全局索引
                # 由于拆分会产生新顶点，我们需要特殊处理这种情况

                # 方法1：如果拆分不产生新顶点（对角线拆分）
                if i in range(len(poly)) and j in range(len(poly)):
                    # 对角线拆分，不产生新顶点
                    # 将局部索引转换回全局索引
                    indices1 = []
                    indices2 = []

                    # 确定拆分路径
                    if i < j:
                        path1 = indices[i:j + 1]
                        path2 = indices[j:] + indices[:i + 1]
                    else:
                        path1 = indices[i:] + indices[:j + 1]
                        path2 = indices[j:i + 1]

                    # 创建两个新的索引序列
                    indices1 = path1
                    indices2 = path2

                    # 创建新的分解
                    new_decomposition = (
                            current_decomposition[:idx] +
                            [indices1, indices2] +
                            current_decomposition[idx + 1:]
                    )

                    # 递归处理新分解
                    new_decomps = recursive_split(
                        global_polygon, part_indices, new_decomposition,
                        depth + 1, max_depth, visited_states
                    )

                    for decomp in new_decomps:
                        decompositions.append(decomp)

                # 方法2：如果拆分产生新顶点（需要特殊处理）
                # 这里需要根据您的 split_polygon 实现来调整

            except Exception as e:
                continue

        # 每个子多边形只尝试一次拆分
        if decompositions:
            break

    # 如果没有找到分解，返回当前状态
    if not decompositions:
        return [current_decomposition]

    return decompositions


# 辅助函数：从索引序列获取多边形
def get_polygon_from_indices(global_polygon, indices):
    """从全局多边形和索引序列中提取多边形"""
    return [global_polygon[i] for i in indices]


# 修改后的 find_concave_vertices 函数（接受索引）
# def find_concave_vertices_with_indices(global_polygon, indices, threshold=2.6):
#     """查找凹顶点（使用索引）"""
#     poly = [global_polygon[i] for i in indices]
#     return find_concave_vertices(poly, threshold)


def find_concave_vertices_with_indices(indices, threshold=2.6):
    """查找凹顶点（使用索引）"""
    global global_polygon
    poly = [global_polygon[i] for i in indices]
    return find_concave_vertices(poly, threshold)

# 修改后的 generate_promising_splits 函数（接受索引）
def generate_promising_splits_with_indices(global_polygon, indices, concave_verts, threshold=2.6):
    """生成有希望的拆分线（使用索引）"""
    poly = [global_polygon[i] for i in indices]
    return generate_promising_splits(poly, concave_verts, threshold)
def draw_polygon_with_concave(vertices, concave_verts, color='blue', alpha=0.5, label_offset=0.1):
    """
    绘制多边形并标注顶点索引

    参数:
    - vertices: 顶点坐标列表，格式为 [(x1,y1), (x2,y2), ...]
    - color: 多边形填充颜色
    - alpha: 多边形透明度
    - label_offset: 顶点标签偏移量
    """
    # 创建图形
    fig, ax = plt.subplots()

    # 将顶点列表转换为NumPy数组以便处理
    vertices = np.array(vertices)

    # 绘制多边形
    polygon = plt.Polygon(vertices, color=color, alpha=alpha)
    ax.add_patch(polygon)

    # 绘制顶点并标注索引
    for i, (x, y) in enumerate(vertices):
        # 绘制顶点
        ax.plot(x, y, 'ro')

        # 计算标签位置（稍微偏移以避免重叠）
        offset_x = label_offset if x >= 0 else -label_offset
        offset_y = label_offset if y >= 0 else -label_offset

        # 标注索引
        ax.text(x + offset_x, y + offset_y, str(i),
                fontsize=12, color='black', weight='bold')

    # 突出显示凹顶点（红色）
    if concave_verts:
        # concave_array = np.array(concave_verts)
        # ax.plot(concave_array[:, 0], concave_array[:, 1], 's', color='red',
        #          markersize=12, markerfacecolor='none', markeredgewidth=3, label='凹顶点')
        # 标记凹顶点索引
        for i in concave_verts:
            vertex = vertices[i]
            ax.text(vertex[0] + 0.15, vertex[1] + 0.15, str(i), fontsize=14,
                     fontweight='bold', color='red',
                     bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.8))

    # 设置坐标轴范围
    min_x, min_y = np.min(vertices, axis=0)
    max_x, max_y = np.max(vertices, axis=0)
    ax.set_xlim(min_x - 1, max_x + 1)
    ax.set_ylim(min_y - 1, max_y + 1)

    # 设置图形标题
    ax.set_title('Polygon with Vertex Indices')

    # 显示图形
    plt.grid(True)
    plt.axis('equal')  # 保持纵横比一致
    plt.show()


def enhanced_evaluate_split_quality(self, split_polygons):
    """
    增强的拆分质量评估，包含形状规则性分析
    """
    if len(split_polygons) < 2:
        return {"valid": False, "message": "未成功拆分"}

    areas = [poly.area for poly in split_polygons]
    total_area = sum(areas)

    # 基础评估
    area_ratio = min(areas) / max(areas) if max(areas) > 0 else 0
    area_loss = abs(total_area - self.original_area) / self.original_area

    # 形状规则性评估
    shape_scores = []
    shape_details = []

    for poly in split_polygons:
        regularity = calculate_shape_regularity(poly)
        shape_scores.append(regularity.get("overall_score", 0))
        shape_details.append(regularity)

    avg_shape_score = np.mean(shape_scores)
    min_shape_score = min(shape_scores)

    # 综合评分
    composite_score = (area_ratio * 0.4 + avg_shape_score * 0.4 +
                       (1 - area_loss) * 0.2)

    return {
        "valid": area_loss < 0.01,
        "area_ratio": area_ratio,
        "avg_shape_score": avg_shape_score,
        "min_shape_score": min_shape_score,
        "area_loss": area_loss,
        "num_parts": len(split_polygons),
        "composite_score": composite_score,
        "shape_details": shape_details,
        "areas": areas
    }

#######################################################################
# global_polygon0 = [(0, 0), (0.5, 0.5), (1.0, 0),(1.5, 0.5), (2.0, 0.5), (2.5, 0.2), (3, 0), (3, 1), (2, 1), (2, 2), (1, 2), (1, 1), (0, 1)]
global_polygon = [(0, 0), (0.5, 0.5), (1.5, 0), (2.5, 0.2), (3, 0), (3, 1), (2, 1), (2, 2), (1, 2), (1, 1), (0, 1)]
global_polygon1 = [(0, 0), (0.5, 0.2), (1.5, 0.5), (2.5, 0.2), (3, 0), (3, 1), (2, 1), (2, 2), (1, 2), (1, 1), (0, 1)]
global_polygon2 = [(337.7, 585.1), (338.5, 581.7), (339.2, 578.3), (339.8, 574.8), (340.3, 571.3), (340.9, 567.8),
                  (341.4, 564.2), (341.9, 560.7), (342.4, 557.3), (343.0, 553.8), (344.9, 543.2), (346.8, 532.4),
                  (348.9, 521.5), (351.1, 510.7), (353.6, 499.9), (356.4, 489.1), (359.6, 478.6), (363.1, 468.3),
                  (367.1, 458.2), (367.2, 461.9), (367.2, 465.6), (367.1, 469.3), (366.9, 473.0), (366.6, 476.8),
                  (366.3, 480.5), (365.9, 484.2), (365.6, 487.9), (365.4, 491.6), (364.9, 500.6), (364.4, 510.5),
                  (364.1, 521.0), (363.9, 531.9), (363.9, 542.9), (364.2, 553.7), (364.9, 564.1), (365.9, 573.8),
                  (367.4, 582.6), (371.9, 582.4), (376.3, 582.3), (380.8, 582.1), (385.3, 581.9), (389.8, 581.7),
                  (394.3, 581.5), (398.8, 581.2), (403.2, 580.9), (407.7, 580.6), (414.7, 580.6), (421.7, 580.5),
                  (428.7, 580.3), (435.7, 580.1), (442.8, 580.0), (449.8, 579.8), (456.8, 579.6), (463.8, 579.5),

                  (659.1, 1019.1), (658.1, 1021.1), (658.0, 1021.2), (657.9, 1021.2), (657.8, 1021.3),
                  (657.7, 1021.3), (657.7, 1021.4), (657.6, 1021.4), (657.5, 1021.5), (657.4, 1021.5),
                  (657.3, 1021.6), (650.1, 1023.1), (642.9, 1024.5), (635.6, 1025.9), (628.4, 1027.3),
                  (621.2, 1028.7), (613.9, 1030.0), (606.7, 1031.3), (599.4, 1032.6), (592.2, 1033.9),

                  (279.0, 1025.1), (277.9, 1022.5), (276.9, 1019.5), (276.0, 1016.3), (275.2, 1012.9),
                  (274.5, 1009.4), (273.8, 1006.0), (273.2, 1002.6), (272.6, 999.5), (272.0, 996.6), (269.1, 983.4),

                  (268.3, 593.2), (278.1, 591.7), (288.1, 590.4), (298.0, 589.2), (308.0, 588.1), (318.0, 587.1),
                  (327.9, 586.1)]


def recursive_split(part_indices, threshold=2.6, current_decomposition=None, depth=0, max_depth=10,
                    visited_states=None):
    """递归拆分多边形（使用索引表示部分），添加状态跟踪防止死循环"""
    global global_polygon

    if visited_states is None:
        visited_states = set()

    if current_decomposition is None:
        current_decomposition = [part_indices]

    # 生成当前状态的唯一标识
    state_key = tuple(
        tuple(indices) for indices in sorted(current_decomposition, key=lambda x: (len(x), x[0] if x else 0)))
    if state_key in visited_states:
        return [current_decomposition]

    visited_states.add(state_key)

    # 检查终止条件
    if depth > max_depth:
        return [current_decomposition]

    # 检查所有子多边形是否满足条件
    all_valid = True
    for indices in current_decomposition:
        if len(find_concave_vertices_with_indices(indices, threshold)) > 1:
            all_valid = False
            break

    if all_valid:
        return [current_decomposition]

    decompositions = []

    # 遍历每个需要拆分的子多边形
    for idx, indices in enumerate(current_decomposition):
        # 获取凹顶点（全局索引）
        global_concave_verts = find_concave_vertices_with_indices(indices, threshold)

        if len(global_concave_verts) <= 1:
            continue

        # 从全局多边形中提取当前部分的多边形
        poly = [global_polygon[i] for i in indices]

        # 将全局凹顶点索引转换为局部索引
        local_concave_verts = []
        for global_idx in global_concave_verts:
            if global_idx in indices:
                local_concave_verts.append(indices.index(global_idx))

        # 生成拆分线（使用局部索引）
        splits = generate_promising_splits(poly, local_concave_verts, threshold)

        for i, j in splits:
            try:
                # 拆分多边形（使用局部索引）
                new_poly1, new_poly2 = split_polygon(poly, i, j)

                # 检查拆分后多边形是否有效
                if len(new_poly1) < 3 or len(new_poly2) < 3:
                    continue

                # 将局部索引转换回全局索引
                if i in range(len(poly)) and j in range(len(poly)):
                    # 确定拆分路径
                    if i < j:
                        path1 = indices[i:j + 1]
                        path2 = indices[j:] + indices[:i + 1]
                    else:
                        path1 = indices[i:] + indices[:j + 1]
                        path2 = indices[j:i + 1]

                    # 创建两个新的索引序列
                    indices1 = path1
                    indices2 = path2

                    # 检查索引序列是否有效（至少3个顶点）
                    if len(indices1) < 3 or len(indices2) < 3:
                        continue

                    # 创建新的分解
                    new_decomposition = (
                            current_decomposition[:idx] +
                            [indices1, indices2] +
                            current_decomposition[idx + 1:]
                    )
                    print(f"recursive_split new_decomposition:{new_decomposition}")
                    # 递归处理新分解
                    new_decomps = recursive_split(
                        part_indices, threshold, new_decomposition,
                        depth + 1, max_depth, visited_states
                    )

                    for decomp in new_decomps:
                        decompositions.append(decomp)

            except Exception as e:
                print(f"拆分过程中出错: {e}")
                continue

        # 每个子多边形只尝试一次拆分
        if decompositions:
            break

    # 如果没有找到分解，返回当前状态
    if not decompositions:
        return [current_decomposition]

    return decompositions
def get_polygon_from_indices(indices):
    """从全局多边形和索引序列中提取多边形"""
    global global_polygon
    return [global_polygon[i] for i in indices]


# # 辅助函数：计算多边形的面积（使用索引）
# def polygon_area_from_indices(indices):
#     """计算多边形的面积（使用索引）"""
#     global global_polygon
#     poly = [global_polygon[i] for i in indices]
#     return polygon_area(poly)

# 辅助函数：检查多边形是否凸（使用索引）
def is_convex_from_indices(indices, threshold=2.6):
    """检查多边形是否凸（使用索引）"""
    global global_polygon
    poly = [global_polygon[i] for i in indices]
    return len(find_concave_vertices(poly, threshold)) == 0


# 使用示例
def main1():
    global global_polygon
    # 初始部分包含所有顶点的索引
    initial_indices = list(range(len(global_polygon)))

    # 执行递归拆分
    decompositions = recursive_split(initial_indices, threshold=2.6)

    # 输出结果
    for i, decomp in enumerate(decompositions):
        print(f"分解方案 {i + 1}:")
        for j, indices in enumerate(decomp):
            poly = get_polygon_from_indices(indices)
            print(f"  子多边形 {j + 1}: {poly}")
        print()

# 使用示例
def main():
    # test_polygon = [(0, 0), (0.5, 0.2), (1.5, 0.5), (2.5, 0.2), (3, 0), (3, 1), (2, 1), (2, 2), (1, 2), (1, 1), (0, 1)]
    test_polygon1 = [(833.0, 1600.2), (833.2, 1600.2), (833.4, 1600.2), (833.6, 1600.1), (833.8, 1600.1),
                    (834.0, 1600.1), (834.3, 1600.0), (834.5, 1600.0), (834.7, 1599.9), (834.9, 1599.9),
                    (834.9, 1599.9), (835.2, 1600.1), (835.6, 1600.3), (835.9, 1600.5), (836.2, 1600.6),
                    (836.5, 1600.7), (836.9, 1600.8), (837.2, 1600.9), (837.6, 1601.0), (838.0, 1601.1),
                    (838.0, 1601.1), (838.4, 1601.1), (838.8, 1601.2), (839.1, 1601.3), (839.5, 1601.4),
                    (839.9, 1601.5), (840.3, 1601.6), (840.6, 1601.7), (841.0, 1601.8), (841.4, 1601.9),
                    (841.4, 1601.9), (841.4, 1602.0), (841.4, 1602.2), (841.4, 1602.3), (841.3, 1602.4),
                    (841.3, 1602.5), (841.3, 1602.7), (841.3, 1602.8), (841.3, 1602.9), (841.3, 1603.0),
                    (841.3, 1603.0), (840.9, 1603.1), (840.5, 1603.3), (840.1, 1603.4), (839.7, 1603.5),
                    (839.3, 1603.6), (838.9, 1603.7), (838.5, 1603.8), (838.1, 1604.0), (837.7, 1604.1),
                    (837.7, 1604.1), (837.8, 1605.0), (838.1, 1605.8), (838.5, 1606.5), (839.0, 1607.1),
                    (839.6, 1607.8), (840.1, 1608.4), (840.6, 1609.1), (841.0, 1609.9), (841.3, 1610.8),
                    (841.3, 1610.8), (841.0, 1610.8), (840.7, 1610.8), (840.5, 1610.9), (840.2, 1610.9),
                    (840.0, 1611.0), (839.7, 1611.0), (839.4, 1611.0), (839.2, 1611.1), (838.9, 1611.1),
                    (837.8, 1610.0), (837.6, 1609.8), (837.4, 1609.5), (837.1, 1609.3), (836.9, 1609.1),
                    (838.9, 1611.1), (838.7, 1610.9), (838.5, 1610.7), (838.2, 1610.4), (838.0, 1610.2),
                    (836.9, 1609.1), (836.9, 1609.2), (836.8, 1609.3), (836.7, 1609.4), (836.6, 1609.5),
                    (836.5, 1609.6), (836.5, 1609.7), (836.4, 1609.8), (836.3, 1609.9), (836.2, 1610.0),
                    (836.2, 1610.0), (836.2, 1610.1), (836.1, 1610.1), (836.0, 1610.2), (836.0, 1610.2),
                    (835.9, 1610.3), (835.8, 1610.3), (835.7, 1610.4), (835.7, 1610.4), (835.6, 1610.5)]
    # test_polygon = [(337.7, 585.1), (338.5, 581.7), (339.2, 578.3), (339.8, 574.8), (340.3, 571.3), (340.9, 567.8), (341.4, 564.2), (341.9, 560.7), (342.4, 557.3), (343.0, 553.8), (344.9, 543.2), (346.8, 532.4), (348.9, 521.5), (351.1, 510.7), (353.6, 499.9), (356.4, 489.1), (359.6, 478.6), (363.1, 468.3), (367.1, 458.2), (367.2, 461.9), (367.2, 465.6), (367.1, 469.3), (366.9, 473.0), (366.6, 476.8), (366.3, 480.5), (365.9, 484.2), (365.6, 487.9), (365.4, 491.6), (364.9, 500.6), (364.4, 510.5), (364.1, 521.0), (363.9, 531.9), (363.9, 542.9), (364.2, 553.7), (364.9, 564.1), (365.9, 573.8), (367.4, 582.6), (371.9, 582.4), (376.3, 582.3), (380.8, 582.1), (385.3, 581.9), (389.8, 581.7), (394.3, 581.5), (398.8, 581.2), (403.2, 580.9), (407.7, 580.6), (414.7, 580.6), (421.7, 580.5), (428.7, 580.3), (435.7, 580.1), (442.8, 580.0), (449.8, 579.8), (456.8, 579.6), (463.8, 579.5), (470.8, 579.5), (475.7, 579.5), (480.6, 579.6), (485.6, 579.7), (490.5, 579.8), (495.4, 579.9), (500.3, 580.0), (505.3, 580.0), (510.2, 580.0), (515.1, 579.9), (516.1, 579.9), (517.2, 579.8), (518.3, 579.8), (519.5, 579.7), (520.7, 579.6), (521.9, 579.4), (522.9, 579.1), (523.9, 578.8), (524.7, 578.3), (526.2, 574.7), (527.5, 570.4), (528.5, 565.6), (529.3, 560.5), (529.9, 555.3), (530.4, 550.2), (530.8, 545.2), (531.2, 540.5), (531.5, 536.4), (532.2, 535.0), (532.7, 533.4), (533.0, 531.9), (533.3, 530.3), (533.5, 528.6), (533.8, 527.0), (534.2, 525.5), (534.8, 523.9), (535.6, 522.5), (535.9, 522.0), (536.2, 521.6), (536.4, 521.4), (536.7, 521.1), (537.0, 521.0), (537.3, 520.9), (537.7, 520.8), (538.2, 520.7), (538.7, 520.6), (539.9, 521.2), (540.8, 521.8), (541.7, 522.5), (542.4, 523.3), (543.0, 524.2), (543.6, 525.1), (544.1, 526.1), (544.6, 527.2), (545.2, 528.3), (545.6, 532.2), (546.2, 537.9), (546.9, 544.8), (547.7, 552.4), (548.6, 560.2), (549.7, 567.5), (550.8, 573.8), (552.0, 578.6), (553.2, 581.2), (555.4, 581.9), (557.7, 582.3), (560.2, 582.6), (562.6, 582.8), (565.2, 582.9), (567.7, 582.9), (570.2, 582.9), (572.6, 583.0), (574.9, 583.1), (580.0, 583.5), (585.2, 584.0), (590.3, 584.4), (595.4, 584.9), (600.6, 585.4), (605.7, 585.8), (610.8, 586.3), (616.0, 586.8), (621.1, 587.3), (628.2, 588.1), (635.3, 589.0), (642.4, 589.9), (649.4, 590.9), (656.5, 592.0), (663.6, 593.1), (670.6, 594.2), (677.7, 595.4), (684.7, 596.7), (685.6, 601.9), (686.3, 607.1), (686.9, 612.4), (687.5, 617.7), (687.9, 623.1), (688.3, 628.4), (688.7, 633.7), (689.0, 639.0), (689.4, 644.3), (690.5, 659.4), (691.4, 674.6), (692.1, 689.7), (692.7, 704.8), (693.1, 720.0), (693.3, 735.1), (693.4, 750.3), (693.3, 765.4), (693.0, 780.6), (692.9, 783.9), (692.8, 787.1), (692.6, 790.3), (692.4, 793.6), (692.1, 796.8), (691.8, 800.0), (691.5, 803.2), (691.2, 806.5), (690.8, 809.7), (690.5, 811.7), (690.2, 813.8), (689.8, 816.0), (689.4, 818.2), (689.0, 820.5), (688.7, 822.8), (688.4, 824.9), (688.4, 827.0), (688.5, 828.9), (687.8, 831.8), (687.2, 834.7), (686.5, 837.6), (685.8, 840.5), (685.1, 843.4), (684.4, 846.2), (683.6, 849.1), (682.8, 852.0), (682.0, 854.8), (682.6, 854.9), (683.3, 854.9), (683.9, 855.0), (684.6, 855.1), (685.2, 855.1), (685.9, 855.2), (686.5, 855.3), (687.2, 855.3), (687.8, 855.4), (686.1, 871.6), (684.3, 887.7), (682.1, 903.9), (679.8, 919.9), (677.1, 936.0), (674.3, 952.0), (671.2, 967.9), (667.8, 983.8), (664.2, 999.7), (663.7, 1001.9), (663.2, 1004.3), (662.7, 1006.8), (662.1, 1009.4), (661.5, 1012.0), (660.8, 1014.5), (660.0, 1016.9), (659.1, 1019.1), (658.1, 1021.1), (658.0, 1021.2), (657.9, 1021.2), (657.8, 1021.3), (657.7, 1021.3), (657.7, 1021.4), (657.6, 1021.4), (657.5, 1021.5), (657.4, 1021.5), (657.3, 1021.6), (650.1, 1023.1), (642.9, 1024.5), (635.6, 1025.9), (628.4, 1027.3), (621.2, 1028.7), (613.9, 1030.0), (606.7, 1031.3), (599.4, 1032.6), (592.2, 1033.9), (591.8, 1031.0), (591.5, 1028.1), (591.2, 1025.2), (590.8, 1022.2), (590.5, 1019.3), (590.2, 1016.4), (589.9, 1013.5), (589.7, 1010.5), (589.4, 1007.6), (568.3, 1027.7), (546.6, 1046.3), (524.4, 1063.4), (501.4, 1078.9), (477.5, 1092.7), (452.6, 1104.8), (426.6, 1115.2), (399.3, 1123.8), (370.7, 1130.6), (369.7, 1120.5), (368.7, 1110.3), (367.8, 1100.2), (366.9, 1090.1), (366.0, 1079.9), (365.1, 1069.8), (364.2, 1059.7), (363.2, 1049.5), (362.2, 1039.4), (352.9, 1038.0), (343.6, 1036.5), (334.4, 1034.9), (325.1, 1033.3), (315.9, 1031.6), (306.7, 1030.0), (297.5, 1028.3), (288.2, 1026.7), (279.0, 1025.1), (277.9, 1022.5), (276.9, 1019.5), (276.0, 1016.3), (275.2, 1012.9), (274.5, 1009.4), (273.8, 1006.0), (273.2, 1002.6), (272.6, 999.5), (272.0, 996.6), (269.1, 983.4), (266.3, 970.1), (263.7, 956.8), (261.2, 943.5), (258.9, 930.2), (256.7, 916.8), (254.6, 903.4), (252.7, 890.0), (250.9, 876.6), (250.1, 870.5), (249.3, 864.3), (248.5, 858.1), (247.8, 852.0), (247.1, 845.8), (246.5, 839.6), (246.1, 833.4), (245.7, 827.2), (245.5, 821.0), (243.8, 803.5), (242.6, 785.9), (241.9, 768.2), (241.5, 750.5), (241.5, 732.8), (241.8, 715.1), (242.4, 697.5), (243.2, 679.8), (244.2, 662.3), (244.7, 655.0), (245.2, 647.8), (245.8, 640.5), (246.4, 633.3), (247.0, 626.0), (247.6, 618.8), (248.1, 611.5), (248.5, 604.3), (248.9, 597.0), (258.5, 595.0), (268.3, 593.2), (278.1, 591.7), (288.1, 590.4), (298.0, 589.2), (308.0, 588.1), (318.0, 587.1), (327.9, 586.1)]
    test_polygon = global_polygon
    print("原始多边形顶点:", test_polygon)

    threashold_set = 150/180.0 * math.pi # 弧度角
    # 查找凹顶点
    # concave_verts = find_concave_vertices(test_polygon, threshold=math.pi)#ok
    concave_verts = find_concave_vertices(test_polygon, threshold=threashold_set)#外∠更凹，外∠越小，越凹，angle就越小
    print("凹顶点索引:", concave_verts)
    print("凹顶点坐标:", [test_polygon[i] for i in concave_verts])
    draw_polygon_with_concave(test_polygon, concave_verts, color='skyblue', alpha=0.7)
    # return 0
    print("-------------------------------------------------------------------------")
    # 使用迭代版本进行拆分（更安全）
    # decompositions = iterative_split(test_polygon, threshold=threashold_set)
    decompositions = recursive_split(test_polygon, threshold=threashold_set)#容易死循环
    score_sort = []
    print(f"\n找到 {len(decompositions)} 种分解方案")
    for i, decomp in enumerate(decompositions):
        # print(f"decomp:{decomp}")
        polygons = [Polygon(coords) for coords in decomp]
        score_overall = get_aggregate_regularity(polygons)
        print(f"方案 {i + 1}: {len(decomp)} 个子多边形 综合评分:{score_overall}")
        score_sort.append({
            "polygon_index": i,
            "overall_score": score_overall
        })
        for j, poly in enumerate(decomp):
            concave_count = len(find_concave_vertices(poly, threshold=threashold_set))
            print(f"  子多边形 {j + 1}: {len(poly)} 顶点, {concave_count} 凹顶点")
    # 按综合评分排序
    score_sort.sort(key=lambda x: x["overall_score"], reverse=True)
    # print(f"score_sort:{score_sort}")
    for score in score_sort:
        print(f"score:{score}")

    # 可视化第一个分解方案
    if decompositions:
        # visualize_decomposition(test_polygon, decompositions[26])
        visualize_decomposition(test_polygon, decompositions[score_sort[0].get("polygon_index")])
        # for i, decomp in enumerate(decompositions):
        #     visualize_decomposition(test_polygon, decomp)


if __name__ == "__main__":
    # main()
    main1()