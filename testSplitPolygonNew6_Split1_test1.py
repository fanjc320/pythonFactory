import math
from common.polygon_plot_index import draw_polygon_with_labels
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon
# from shapely.plotting import plot_polygon
from common.Polygon_Compare import *
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection
import numpy as np
import random
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

def recursive_split_direct_global(part_global_indices, threshold=2.6, current_decomposition=None, depth=0, max_depth=10,
                                  visited_states=None):
    """
    递归拆分多边形，直接使用全局索引
    """
    global global_polygon

    if visited_states is None:
        visited_states = set()

    if current_decomposition is None:
        current_decomposition = [part_global_indices]

    # 生成当前状态的唯一标识（基于全局索引）
    state_key = tuple(tuple(sorted(indices)) for indices in current_decomposition)
    if state_key in visited_states:
        return [current_decomposition]

    visited_states.add(state_key)

    # 检查终止条件
    if depth > max_depth:
        return [current_decomposition]

    # 检查所有子多边形是否满足条件（凹顶点数 <= 1）
    all_valid = True
    for global_indices in current_decomposition:
        poly = [global_polygon[i] for i in global_indices]
        if len(find_concave_vertices(poly, threshold)) > 1:
            all_valid = False
            break

    if all_valid:
        return [current_decomposition]

    decompositions = []

    # 遍历每个需要拆分的子多边形
    for idx, global_indices in enumerate(current_decomposition):
        # 从全局索引获取多边形
        poly = [global_polygon[i] for i in global_indices]

        # 查找凹顶点（返回局部索引）
        local_concave_verts = find_concave_vertices(poly, threshold)

        if len(local_concave_verts) <= 1:
            continue

        print(f"\n深度 {depth}: 处理子多边形")
        print(f"全局索引: {global_indices}")
        print(f"凹顶点局部索引: {local_concave_verts}")
        print(f"凹顶点全局索引: {[global_indices[i] for i in local_concave_verts]}")

        # 生成拆分线（使用局部索引）
        splits = generate_promising_splits_direct(poly, local_concave_verts, threshold, global_indices)

        if not splits:
            print("没有生成有效的拆分线")
            continue

        for local_i, local_j in splits:
            try:
                print(
                    f"尝试拆分: 局部索引({local_i}, {local_j}) -> 全局索引({global_indices[local_i]}, {global_indices[local_j]})")

                # 拆分多边形（使用局部索引）
                new_poly1, new_poly2 = split_polygon(poly, local_i, local_j)

                if len(new_poly1) < 3 or len(new_poly2) < 3:
                    continue

                # 直接将局部索引映射回全局索引
                global_i, global_j = global_indices[local_i], global_indices[local_j]

                # 确定拆分路径（使用全局索引）
                if local_i < local_j:
                    # 路径1: i -> j
                    new_global_indices1 = global_indices[local_i:local_j + 1]
                    # 路径2: j -> end + start -> i
                    new_global_indices2 = global_indices[local_j:] + global_indices[:local_i + 1]
                else:
                    # 路径1: i -> end + start -> j
                    new_global_indices1 = global_indices[local_i:] + global_indices[:local_j + 1]
                    # 路径2: j -> i
                    new_global_indices2 = global_indices[local_j:local_i + 1]

                # 验证拆分结果
                if not validate_global_split(global_indices, new_global_indices1, new_global_indices2):
                    print("拆分验证失败")
                    continue

                print(f"拆分成功:")
                print(f"  子多边形1全局索引: {new_global_indices1}")
                print(f"  子多边形2全局索引: {new_global_indices2}")

                # 创建新的分解（直接使用全局索引）
                new_decomposition = (
                        current_decomposition[:idx] +
                        [new_global_indices1, new_global_indices2] +
                        current_decomposition[idx + 1:]
                )

                # 递归处理
                new_decomps = recursive_split_direct_global(
                    part_global_indices, threshold, new_decomposition,
                    depth + 1, max_depth, visited_states
                )

                decompositions.extend(new_decomps)

            except Exception as e:
                print(f"拆分过程中出错: {e}")
                continue

        if decompositions:
            break

    return decompositions if decompositions else [current_decomposition]


def generate_promising_splits_direct(poly, local_concave_verts, threshold, global_indices):
    """生成拆分线，直接使用全局索引信息"""
    splits = []
    n = len(poly)

    print(f"\n生成拆分线:")
    print(f"多边形顶点数: {n}")
    print(f"凹顶点局部索引: {local_concave_verts}")
    print(f"凹顶点全局索引: {[global_indices[i] for i in local_concave_verts]}")
    print(f"所有顶点全局索引: {global_indices}")

    for i in range(len(local_concave_verts)):
        for j in range(i + 1, len(local_concave_verts)):
            local_i = local_concave_verts[i]
            local_j = local_concave_verts[j]

            if not is_valid_split(poly, local_i, local_j):
                continue

            splits.append((local_i, local_j))
            print(
                f"有效拆分线: 局部({local_i}, {local_j}) -> 全局({global_indices[local_i]}, {global_indices[local_j]})")

    print(f"总共生成 {len(splits)} 条有效拆分线")
    return splits


def validate_global_split(original_global_indices, new_global_indices1, new_global_indices2):
    """验证全局索引拆分是否正确"""
    # 检查顶点数
    if len(new_global_indices1) < 3 or len(new_global_indices2) < 3:
        return False

    # 检查所有原始顶点都被包含
    original_set = set(original_global_indices)
    new_set = set(new_global_indices1 + new_global_indices2)

    if original_set != new_set:
        print(f"顶点不匹配: 原始{original_set} vs 拆分后{new_set}")
        return False

    # 检查没有重复顶点
    if len(new_global_indices1) != len(set(new_global_indices1)) or \
            len(new_global_indices2) != len(set(new_global_indices2)):
        print("有重复顶点")
        return False

    return True

# 辅助函数
def get_polygon_from_global_indices(global_indices):
    """从全局索引获取多边形"""
    global global_polygon
    return [global_polygon[i] for i in global_indices]

def recursive_split_direct_global(part_global_indices, threshold=2.6, current_decomposition=None,
                                  depth=0, max_depth=10, visited_states=None, split_history=None):
    """
    递归拆分多边形，直接使用全局索引，返回分解方案和拆分历史
    返回格式: [(decomposition, split_history), ...]
    """
    global global_polygon

    if visited_states is None:
        visited_states = set()

    if current_decomposition is None:
        current_decomposition = [part_global_indices]

    if split_history is None:
        split_history = []

    # 生成当前状态的唯一标识（基于全局索引）
    state_key = tuple(tuple(sorted(indices)) for indices in current_decomposition)
    if state_key in visited_states:
        return [(current_decomposition, split_history)]

    visited_states.add(state_key)

    # 检查终止条件
    if depth > max_depth:
        return [(current_decomposition, split_history)]

    # 检查所有子多边形是否满足条件（凹顶点数 <= 1）
    all_valid = True
    for global_indices in current_decomposition:
        poly = [global_polygon[i] for i in global_indices]
        if len(find_concave_vertices(poly, threshold)) > 1:
            all_valid = False
            break

    if all_valid:
        return [(current_decomposition, split_history)]

    results = []  # 存储所有结果 (decomposition, split_history)

    # 遍历每个需要拆分的子多边形
    for idx, global_indices in enumerate(current_decomposition):
        # 从全局索引获取多边形
        poly = [global_polygon[i] for i in global_indices]

        # 查找凹顶点（返回局部索引）
        local_concave_verts = find_concave_vertices(poly, threshold)

        if len(local_concave_verts) <= 1:
            continue

        # 生成拆分线（使用局部索引）
        splits = generate_promising_splits_direct(poly, local_concave_verts, threshold, global_indices)

        if not splits:
            continue

        for local_i, local_j in splits:
            try:
                # 获取对应的全局索引
                global_i, global_j = global_indices[local_i], global_indices[local_j]

                # 记录本次拆分信息
                current_split_info = {
                    'depth': depth,
                    'parent_polygon': global_indices,
                    'split_points': (global_i, global_j),
                    'local_indices': (local_i, local_j),
                    'concave_vertices': [global_indices[i] for i in local_concave_verts]
                }

                # 拆分多边形（使用局部索引）
                new_poly1, new_poly2 = split_polygon(poly, local_i, local_j)

                if len(new_poly1) < 3 or len(new_poly2) < 3:
                    continue

                # 确定拆分路径（使用全局索引）
                if local_i < local_j:
                    new_global_indices1 = global_indices[local_i:local_j + 1]
                    new_global_indices2 = global_indices[local_j:] + global_indices[:local_i + 1]
                else:
                    new_global_indices1 = global_indices[local_i:] + global_indices[:local_j + 1]
                    new_global_indices2 = global_indices[local_j:local_i + 1]

                # 验证拆分结果
                if not validate_global_split(global_indices, new_global_indices1, new_global_indices2):
                    continue

                # 创建新的分解和拆分历史
                new_decomposition = (
                        current_decomposition[:idx] +
                        [new_global_indices1, new_global_indices2] +
                        current_decomposition[idx + 1:]
                )

                new_split_history = split_history + [current_split_info]

                # 递归处理
                sub_results = recursive_split_direct_global(
                    part_global_indices, threshold, new_decomposition,
                    depth + 1, max_depth, visited_states, new_split_history
                )

                results.extend(sub_results)

            except Exception as e:
                print(f"拆分过程中出错: {e}")
                continue

        if results:
            break

    # 如果没有找到新的分解，返回当前状态
    if not results:
        return [(current_decomposition, split_history)]

    return results


# 添加去重函数
def remove_duplicate_decompositions(results):
    """移除重复的分解结果"""
    unique_results = []
    seen = set()

    for decomposition, split_history in results:
        # 生成唯一标识：对每个子多边形的索引进行排序，然后对整个分解进行排序
        decomposition_key = tuple(sorted(tuple(sorted(indices)) for indices in decomposition))

        if decomposition_key not in seen:
            seen.add(decomposition_key)
            unique_results.append((decomposition, split_history))

    return unique_results

# 辅助函数：打印拆分历史
def print_split_history(split_history):
    """打印拆分历史信息"""
    print("\n=== 拆分历史 ===")
    for i, split_info in enumerate(split_history):
        print(f"步骤 {i + 1} (深度 {split_info['depth']}):")
        print(f"  父多边形: {split_info['parent_polygon']}")
        print(f"  拆分点: {split_info['split_points']} (全局索引)")
        print(f"  拆分点: {split_info['local_indices']} (局部索引)")
        print(f"  凹顶点: {split_info['concave_vertices']}")
    print("================\n")


# 辅助函数：可视化带拆分历史的分解
def visualize_decomposition_with_history(decomposition, split_history,
                                         title="Polygon Decomposition with Split History"):
    """可视化分解结果并显示拆分历史"""
    global global_polygon

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    # 左图：显示分解结果
    original_poly = np.array(global_polygon)
    original_patch = patches.Polygon(original_poly, alpha=0.2, edgecolor='black',
                                     facecolor='lightgray', linestyle='--', label='Original')
    ax1.add_patch(original_patch)

    # 绘制每个子多边形
    for i, global_indices in enumerate(decomposition):
        poly_vertices = [global_polygon[idx] for idx in global_indices]
        color = (random.random() * 0.7 + 0.3, random.random() * 0.7 + 0.3, random.random() * 0.7 + 0.3)

        patch = patches.Polygon(poly_vertices, alpha=0.6, edgecolor='black',
                                facecolor=color, linewidth=2)
        ax1.add_patch(patch)

        # 标记顶点编号
        for idx in global_indices:
            x, y = global_polygon[idx]
            ax1.text(x, y, f'{idx}', fontsize=8, ha='center', va='center',
                     bbox=dict(boxstyle="circle,pad=0.2", facecolor='white', alpha=0.8))

    # 右图：显示拆分过程
    ax2.add_patch(patches.Polygon(original_poly, alpha=0.3, edgecolor='black',
                                  facecolor='lightgray', label='Original'))

    # 绘制所有拆分线
    colors = ['red', 'blue', 'green', 'orange', 'purple']
    for i, split_info in enumerate(split_history):
        global_i, global_j = split_info['split_points']
        point1 = global_polygon[global_i]
        point2 = global_polygon[global_j]

        color = colors[i % len(colors)]
        ax2.plot([point1[0], point2[0]], [point1[1], point2[1]],
                 color=color, linewidth=2, marker='o', label=f'Split {i + 1}')

    # 设置图形属性
    all_points = np.array(global_polygon)
    x_min, y_min = all_points.min(axis=0) - 1
    x_max, y_max = all_points.max(axis=0) + 1

    for ax in [ax1, ax2]:
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)

    ax1.set_title('Final Decomposition', fontweight='bold')
    ax2.set_title('Split Process', fontweight='bold')
    ax2.legend()

    plt.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()

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
    plt.gca().invert_yaxis()
    plt.show()

#######################################################################
threashold_set = 150 / 180.0 * math.pi  # 弧度角
# global_polygon0 = [(0, 0), (0.5, 0.5), (1.0, 0),(1.5, 0.5), (2.0, 0.5), (2.5, 0.2), (3, 0), (3, 1), (2, 1), (2, 2), (1, 2), (1, 1), (0, 1)]
global_polygon2 = [(0, 0), (0.5, 0.5), (1.5, 0), (2.5, 0.2), (3, 0), (3, 1), (2, 1), (2, 2), (1, 2), (1, 1), (0, 1)]
global_polygon1 = [(0, 0), (0.5, 0.2), (1.5, 0.5), (2.5, 0.2), (3, 0), (3, 1), (2, 1), (2, 2), (1, 2), (1, 1), (0, 1)]
global_polygon = [(337.7, 585.1), (338.5, 581.7), (339.2, 578.3), (339.8, 574.8), (340.3, 571.3), (340.9, 567.8),
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


def main_with_split_history(polygon):
    # 初始全局索引
    global threashold_set
    global global_polygon
    global_polygon = polygon
    initial_global_indices = list(range(len(global_polygon)))

    print("开始递归拆分...")
    results = recursive_split_direct_global(initial_global_indices, threshold=2.6)

    # 移除重复的分解结果
    unique_results = remove_duplicate_decompositions(results)

    print(f"\n找到 {len(results)} 种分解方案，其中 {len(unique_results)} 种唯一方案")

    score_sort = []
    for i, (decomposition, split_history) in enumerate(unique_results):
        print(f"\n=== 唯一方案 {i + 1} ===")
        print(f"拆分步骤数: {len(split_history)}")
        print(f"子多边形数量: {len(decomposition)}")

        # 打印拆分历史
        print_split_history(split_history)

        # 打印最终分解
        print("最终分解:")
        for j, global_indices in enumerate(decomposition):
            poly = get_polygon_from_global_indices(global_indices)
            # area = polygon_area(poly)
            concave_count = len(find_concave_vertices(poly, threashold_set))
            convex_status = "凸" if concave_count == 0 else "凹"
            # print(f"  子多边形{j + 1}: {convex_status}, {len(global_indices)}顶点, {concave_count}凹点, 面积{area:.2f}")
            print(f"  子多边形{j + 1}: {convex_status}, {len(global_indices)}顶点, {concave_count}凹点")
            print(f"    顶点索引: {global_indices}")

        # 可视化
        # visualize_decomposition_with_history(decomposition, split_history,
        #                                      title=f"Unique Decomposition {i + 1}")


        polygons = [ [global_polygon[i] for i in indices] for indices in decomposition]
        polygons = [Polygon(poly) for poly in polygons]
        print(f"main_with_split_history polygons:{polygons} decomp:{decomposition}")
        #
        score_overall = get_aggregate_regularity(polygons)
        print(f"方案 {i + 1}: {len(decomposition)} 个子多边形 综合评分:{score_overall} ")
        print(f"decomposition:{decomposition}") # decomposition:[[3, 4, 5, 6, 7, 8, 9], [9, 10, 0, 1, 2, 3]]
        score_sort.append({
            "polygon_index": i,
            "overall_score": score_overall
        })

    # 按综合评分排序
    score_sort.sort(key=lambda x: x["overall_score"], reverse=True)
    for score in score_sort:
        print(f"score:{score}")
    index_best = score_sort[0]['polygon_index']
    decomp, history = unique_results[index_best]
    print("index_best:", index_best)
    visualize_decomposition_with_history(decomp, history)


# 使用示例
if __name__ == "__main__":
    # global global_polygon
    main_with_split_history(global_polygon)