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


def recursive_split(polygon, threshold=2.6, current_decomposition=None, depth=0, max_depth=10, visited_states=None):
    """递归拆分多边形，添加状态跟踪防止死循环"""
    if visited_states is None:
        visited_states = set()

    if current_decomposition is None:
        current_decomposition = [polygon]

    # 生成当前状态的唯一标识
    state_key = tuple(tuple(tuple(vertex) for vertex in poly) for poly in
                      sorted(current_decomposition, key=lambda x: (len(x), tuple(x[0]) if x else (0, 0))))
    if state_key in visited_states:
        return [current_decomposition]

    visited_states.add(state_key)

    # 检查终止条件
    if depth > max_depth:
        return [current_decomposition]

    # 检查所有子多边形是否满足条件
    all_valid = True
    for poly in current_decomposition:
        if len(find_concave_vertices(poly, threshold)) > 1:
            all_valid = False
            break

    if all_valid:
        return [current_decomposition]

    decompositions = []

    # 遍历每个需要拆分的子多边形
    for idx, poly in enumerate(current_decomposition):
        concave_verts = find_concave_vertices(poly, threshold)

        if len(concave_verts) <= 1:
            continue

        # 生成拆分线
        splits = generate_promising_splits(poly, concave_verts, threshold)

        for i, j in splits:
            try:
                new_poly1, new_poly2 = split_polygon(poly, i, j)

                # 检查拆分后多边形是否有效
                if len(new_poly1) < 3 or len(new_poly2) < 3:
                    continue

                # 创建新的分解
                new_decomposition = (
                        current_decomposition[:idx] +
                        [new_poly1, new_poly2] +
                        current_decomposition[idx + 1:]
                )

                # 递归处理新分解
                new_decomps = recursive_split(
                    polygon, threshold, new_decomposition,
                    depth + 1, max_depth, visited_states
                )

                for decomp in new_decomps:
                    decompositions.append(decomp)

            except Exception as e:
                continue

        # 每个子多边形只尝试一次拆分
        if decompositions:
            break

    # 如果没有找到分解，返回当前状态
    if not decompositions:
        return [current_decomposition]

    return decompositions


def generate_promising_splits(polygon, concave_vertices, threshold=160):
    """生成真正有效的拆分线，确保在多边形内部"""
    splits = []
    n = len(polygon)
    # convex_vertices = [i for i in range(n) if i not in concave_vertices]
    #
    # # 策略1: 凹顶点与可见凸顶点的连接
    # for concave_idx in concave_vertices:
    #     for convex_idx in convex_vertices:
    #         if is_valid_split_line(polygon, concave_idx, convex_idx, threshold):
    #             splits.append((concave_idx, convex_idx))

    # 策略2: 凹顶点之间的连接
    for i in range(len(concave_vertices)):
        for j in range(i + 1, len(concave_vertices)):
            idx_i = concave_vertices[i]
            idx_j = concave_vertices[j]
            if is_valid_split_line(polygon, idx_i, idx_j, threshold):
                splits.append((idx_i, idx_j))

    return splits[:10]  # 限制返回数量


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

# 使用示例
def main():
    # 创建一个测试多边形（凹多边形）
    # test_polygon = [
    #     (0, 0), (10, 0), (10, 5), (8, 8), (5, 10),
    #     (2, 8), (0, 5), (0, 0)  # 闭合多边形
    # ]
    # test_polygon = [(0, 0), (0.5, 0.2), (1.5, 0.5), (2.5, 0.2), (3, 0), (3, 1), (2, 1), (2, 2), (1, 2), (1, 1), (0, 1)]
    test_polygon = [(833.0, 1600.2), (833.2, 1600.2), (833.4, 1600.2), (833.6, 1600.1), (833.8, 1600.1),
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
    main()