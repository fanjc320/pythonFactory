import math
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import ConvexHull


def sort_vertices_counterclockwise(vertices):
    """
    将多边形顶点按逆时针顺序排序
    """
    if len(vertices) < 3:
        return vertices

    # 计算多边形中心点
    center_x = sum(x for x, y in vertices) / len(vertices)
    center_y = sum(y for x, y in vertices) / len(vertices)
    center = (center_x, center_y)

    # 按相对于中心点的极角排序
    def angle_from_center(point):
        dx = point[0] - center_x
        dy = point[1] - center_y
        return math.atan2(dy, dx)

    # 排序并确保是逆时针方向
    sorted_vertices = sorted(vertices, key=angle_from_center)

    # 使用凸包算法确保正确的逆时针顺序
    try:
        hull = ConvexHull(sorted_vertices)
        # 凸包的顶点按逆时针顺序排列
        hull_vertices = [sorted_vertices[i] for i in hull.vertices]
        return hull_vertices
    except:
        return sorted_vertices


def calculate_internal_angles(vertices):
    """
    计算多边形每个顶点的内角（度数）
    """
    n = len(vertices)
    angles = []

    for i in range(n):
        # 获取当前顶点和相邻顶点
        prev_idx = (i - 1) % n
        next_idx = (i + 1) % n

        current = vertices[i]
        prev = vertices[prev_idx]
        next_v = vertices[next_idx]

        # 计算两个向量
        vec1 = (prev[0] - current[0], prev[1] - current[1])
        vec2 = (next_v[0] - current[0], next_v[1] - current[1])

        # 计算点积
        dot = vec1[0] * vec2[0] + vec1[1] * vec2[1]

        # 计算向量模长
        mag1 = math.sqrt(vec1[0] ** 2 + vec1[1] ** 2)
        mag2 = math.sqrt(vec2[0] ** 2 + vec2[1] ** 2)

        if mag1 * mag2 == 0:
            angles.append(0)
            continue

        # 计算夹角
        cos_theta = dot / (mag1 * mag2)
        cos_theta = max(min(cos_theta, 1.0), -1.0)
        theta = math.acos(cos_theta)

        # 计算叉积判断方向
        cross = vec1[0] * vec2[1] - vec1[1] * vec2[0]

        # 确定内角
        if cross >= 0:
            internal_angle = theta
        else:
            internal_angle = 2 * math.pi - theta

        angles.append(math.degrees(internal_angle))

    return angles


def find_vertices_with_large_angles(vertices, threshold=200):
    """
    找出内角大于阈值的顶点
    """
    angles = calculate_internal_angles(vertices)
    large_angle_vertices = []

    for i, angle in enumerate(angles):
        if angle > threshold:
            large_angle_vertices.append({
                'vertex_index': i,
                'vertex_coord': vertices[i],
                'angle': angle
            })

    return large_angle_vertices, angles


def visualize_polygon_with_large_angles(vertices, large_vertices, angles, title="多边形内角分析"):
    """
    可视化多边形，特别标注内角大于200度的顶点
    """
    n = len(vertices)

    # 创建图形
    fig, ax = plt.subplots(figsize=(12, 10))

    # 绘制多边形
    polygon = plt.Polygon(vertices, alpha=0.2, edgecolor='blue', facecolor='lightblue', linewidth=2)
    ax.add_patch(polygon)

    # 绘制顶点和边
    x_coords, y_coords = zip(*vertices)
    ax.plot(x_coords + (x_coords[0],), y_coords + (y_coords[0],), 'bo-', linewidth=2, markersize=8)

    # 标注所有顶点和内角
    for i, (x, y) in enumerate(vertices):
        # 标注顶点编号
        ax.annotate(f'V{i + 1}', (x, y), xytext=(8, 8), textcoords='offset points',
                    fontsize=10, fontweight='bold', color='black')

        # 标注内角
        angle_text = f'{angles[i]:.1f}°'
        color = 'red' if angles[i] > 200 else 'green'

        ax.annotate(angle_text, (x, y), xytext=(0, -15), textcoords='offset points',
                    fontsize=9, fontweight='bold', color=color,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

    # 特别标注内角大于200度的顶点
    for vertex_info in large_vertices:
        i = vertex_info['vertex_index']
        x, y = vertex_info['vertex_coord']
        angle = vertex_info['angle']

        # 绘制红色圆圈标记
        circle = plt.Circle((x, y), 0.15, color='red', fill=False, linewidth=3)
        ax.add_patch(circle)

        # 添加特殊标注
        ax.annotate(f'大角度: {angle:.1f}°', (x, y), xytext=(20, 20),
                    textcoords='offset points', fontsize=12, fontweight='bold',
                    color='red', arrowprops=dict(arrowstyle='->', color='red'))

    # 设置图形属性
    ax.set_xlabel('X坐标')
    ax.set_ylabel('Y坐标')
    ax.set_title(f'{title}\n(红色圆圈标记内角 > 200° 的顶点)')
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')

    # 自动调整坐标轴范围
    margin = 0.8
    ax.set_xlim(min(x_coords) - margin, max(x_coords) + margin)
    ax.set_ylim(min(y_coords) - margin, max(y_coords) + margin)

    plt.tight_layout()
    plt.show()

def create_regular_polygon(n_sides, radius=1, center=(0, 0)):
    """
    创建正多边形
    """
    angles = np.linspace(0, 2*np.pi, n_sides, endpoint=False)
    x = center[0] + radius * np.cos(angles)
    y = center[1] + radius * np.sin(angles)
    return list(zip(x, y))

###########################################################################

import math
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import ConvexHull


def sort_vertices_counterclockwise(vertices):
    """
    将多边形顶点按逆时针顺序排序
    """
    if len(vertices) < 3:
        return vertices

    # 计算多边形中心点
    center_x = sum(x for x, y in vertices) / len(vertices)
    center_y = sum(y for x, y in vertices) / len(vertices)
    center = (center_x, center_y)

    # 按相对于中心点的极角排序
    def angle_from_center(point):
        dx = point[0] - center_x
        dy = point[1] - center_y
        return math.atan2(dy, dx)

    # 排序并确保是逆时针方向
    sorted_vertices = sorted(vertices, key=angle_from_center)

    # 使用凸包算法确保正确的逆时针顺序
    try:
        hull = ConvexHull(sorted_vertices)
        # 凸包的顶点按逆时针顺序排列
        hull_vertices = [sorted_vertices[i] for i in hull.vertices]
        return hull_vertices
    except:
        return sorted_vertices


def calculate_internal_angles(vertices):
    """
    计算多边形每个顶点的内角（度数）
    """
    n = len(vertices)
    angles = []

    for i in range(n):
        # 获取当前顶点和相邻顶点
        prev_idx = (i - 1) % n
        next_idx = (i + 1) % n

        current = vertices[i]
        prev = vertices[prev_idx]
        next_v = vertices[next_idx]

        # 计算两个向量
        vec1 = (prev[0] - current[0], prev[1] - current[1])
        vec2 = (next_v[0] - current[0], next_v[1] - current[1])

        # 计算点积
        dot = vec1[0] * vec2[0] + vec1[1] * vec2[1]

        # 计算向量模长
        mag1 = math.sqrt(vec1[0] ** 2 + vec1[1] ** 2)
        mag2 = math.sqrt(vec2[0] ** 2 + vec2[1] ** 2)

        if mag1 * mag2 == 0:
            angles.append(0)
            continue

        # 计算夹角
        cos_theta = dot / (mag1 * mag2)
        cos_theta = max(min(cos_theta, 1.0), -1.0)
        theta = math.acos(cos_theta)

        # 计算叉积判断方向
        cross = vec1[0] * vec2[1] - vec1[1] * vec2[0]

        # 确定内角
        if cross >= 0:
            internal_angle = theta
        else:
            internal_angle = 2 * math.pi - theta

        angles.append(math.degrees(internal_angle))

    return angles


def find_vertices_with_large_angles(vertices, threshold=200):
    """
    找出内角大于阈值的顶点
    """
    angles = calculate_internal_angles(vertices)
    large_angle_vertices = []

    for i, angle in enumerate(angles):
        if angle > threshold:
            large_angle_vertices.append({
                'vertex_index': i,
                'vertex_coord': vertices[i],
                'angle': angle
            })

    return large_angle_vertices, angles


def visualize_comparison(original_vertices, sorted_vertices, large_vertices, sorted_angles, title="多边形对比分析"):
    """
    可视化对比原始多边形和排序后的多边形，都显示内角角度
    """
    # 计算原始多边形的内角（基于原始顺序）
    original_angles = calculate_internal_angles(original_vertices)

    n = len(sorted_vertices)

    # 创建对比图形
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

    # 左侧：原始多边形（带内角显示）
    x_orig, y_orig = zip(*original_vertices)

    # 绘制原始多边形
    polygon_orig = plt.Polygon(original_vertices, alpha=0.2, edgecolor='red', facecolor='lightcoral', linewidth=2)
    ax1.add_patch(polygon_orig)
    ax1.plot(x_orig + (x_orig[0],), y_orig + (y_orig[0],), 'ro-', linewidth=2, markersize=8, label='原始多边形')

    # 标注原始顶点顺序和内角
    for i, (x, y) in enumerate(original_vertices):
        # 标注顶点编号
        ax1.annotate(f'V{i + 1}', (x, y), xytext=(8, 8), textcoords='offset points',
                     fontsize=10, fontweight='bold', color='darkred')

        # 标注内角（原始顺序计算的角度）
        angle_text = f'{original_angles[i]:.1f}°'
        color = 'red' if original_angles[i] > 200 else 'green'

        ax1.annotate(angle_text, (x, y), xytext=(0, -15), textcoords='offset points',
                     fontsize=9, fontweight='bold', color=color,
                     bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

    # 标记原始多边形中的大角度顶点
    original_large_vertices = []
    for i, angle in enumerate(original_angles):
        if angle > 200:
            original_large_vertices.append({
                'vertex_index': i,
                'vertex_coord': original_vertices[i],
                'angle': angle
            })

    for vertex_info in original_large_vertices:
        i = vertex_info['vertex_index']
        x, y = vertex_info['vertex_coord']
        angle = vertex_info['angle']

        # 绘制橙色圆圈标记原始多边形中的大角度顶点
        circle = plt.Circle((x, y), 0.15, color='orange', fill=False, linewidth=3)
        ax1.add_patch(circle)

        # 添加特殊标注
        ax1.annotate(f'大角度: {angle:.1f}°', (x, y), xytext=(20, 20),
                     textcoords='offset points', fontsize=11, fontweight='bold',
                     color='orange', arrowprops=dict(arrowstyle='->', color='orange'))

    ax1.set_xlabel('X坐标')
    ax1.set_ylabel('Y坐标')
    ax1.set_title('原始多边形 + 内角分析\n(橙色圆圈标记内角 > 200° 的顶点)')
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal')
    ax1.legend()

    # 右侧：排序后的多边形
    x_sorted, y_sorted = zip(*sorted_vertices)
    polygon_sorted = plt.Polygon(sorted_vertices, alpha=0.2, edgecolor='blue', facecolor='lightblue', linewidth=2)
    ax2.add_patch(polygon_sorted)
    ax2.plot(x_sorted + (x_sorted[0],), y_sorted + (y_sorted[0],), 'bo-', linewidth=2, markersize=8,
             label='逆时针排序后')

    # 标注所有顶点和内角
    for i, (x, y) in enumerate(sorted_vertices):
        # 标注顶点编号
        ax2.annotate(f'V{i + 1}', (x, y), xytext=(8, 8), textcoords='offset points',
                     fontsize=10, fontweight='bold', color='darkblue')

        # 标注内角
        angle_text = f'{sorted_angles[i]:.1f}°'
        color = 'red' if sorted_angles[i] > 200 else 'green'

        ax2.annotate(angle_text, (x, y), xytext=(0, -15), textcoords='offset points',
                     fontsize=9, fontweight='bold', color=color,
                     bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

    # 特别标注内角大于200度的顶点
    for vertex_info in large_vertices:
        i = vertex_info['vertex_index']
        x, y = vertex_info['vertex_coord']
        angle = vertex_info['angle']

        # 绘制红色圆圈标记
        circle = plt.Circle((x, y), 0.15, color='red', fill=False, linewidth=3)
        ax2.add_patch(circle)

        # 添加特殊标注
        ax2.annotate(f'大角度: {angle:.1f}°', (x, y), xytext=(20, 20),
                     textcoords='offset points', fontsize=11, fontweight='bold',
                     color='red', arrowprops=dict(arrowstyle='->', color='red'))

    ax2.set_xlabel('X坐标')
    ax2.set_ylabel('Y坐标')
    ax2.set_title('逆时针排序后 + 内角分析\n(红色圆圈标记内角 > 200° 的顶点)')
    ax2.grid(True, alpha=0.3)
    ax2.set_aspect('equal')
    ax2.legend()

    # 自动调整坐标轴范围（统一两个子图）
    margin = 0.8
    all_x = x_orig + x_sorted
    all_y = y_orig + y_sorted
    ax1.set_xlim(min(all_x) - margin, max(all_x) + margin)
    ax1.set_ylim(min(all_y) - margin, max(all_y) + margin)
    ax2.set_xlim(min(all_x) - margin, max(all_x) + margin)
    ax2.set_ylim(min(all_y) - margin, max(all_y) + margin)

    plt.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()

    return original_angles


def print_detailed_comparison(original_vertices, sorted_vertices, original_angles, sorted_angles, large_vertices):
    """
    打印详细的对比信息，包括原始和排序后的内角
    """
    print("=" * 100)
    print("多边形顶点顺序和内角对比分析")
    print("=" * 100)

    print("\n原始顶点顺序和内角:")
    print("-" * 50)
    for i, ((x, y), angle) in enumerate(zip(original_vertices, original_angles)):
        status = ">200° ⚠️" if angle > 200 else "正常"
        print(f"V{i + 1}: ({x:.2f}, {y:.2f}) -> {angle:6.1f}°  {status}")

    print("\n逆时针排序后的顶点顺序和内角:")
    print("-" * 50)
    for i, ((x, y), angle) in enumerate(zip(sorted_vertices, sorted_angles)):
        status = ">200° ⚠️" if angle > 200 else "正常"
        print(f"V{i + 1}: ({x:.2f}, {y:.2f}) -> {angle:6.1f}°  {status}")

    print(f"\n原始内角和: {sum(original_angles):.1f}°")
    print(f"排序后内角和: {sum(sorted_angles):.1f}°")
    print(f"理论值: {(len(sorted_vertices) - 2) * 180}°")

    # 找出原始多边形中的大角度顶点
    original_large = [i for i, angle in enumerate(original_angles) if angle > 200]
    if original_large:
        print(f"\n原始多边形中内角大于200度的顶点:")
        print("-" * 50)
        for i in original_large:
            print(f"V{i + 1}: {original_angles[i]:.1f}°")

    if large_vertices:
        print(f"\n排序后多边形中内角大于200度的顶点:")
        print("-" * 50)
        for vertex in large_vertices:
            print(f"V{vertex['vertex_index'] + 1}: {vertex['angle']:.1f}°")
    else:
        print("\n排序后多边形中没有内角大于200度的顶点")


# 示例演示
if __name__ == "__main__":
    # 测试用例1：随机顺序的多边形
    test_polygon1 = [
        (2, 1), (4, 3), (1, 4), (0, 2), (3, 0), (2, 2)
    ]

    # 测试用例2：明显的凹多边形（会有大角度）
    test_polygon2 = [
        (0, 0), (5, 0), (4, 2), (5, 4), (0, 4), (1, 2)
    ]

    # 测试用例3：星形多边形（多个大角度）
    test_polygon3 = [
        (2, 0), (4, 2), (2, 4), (0, 2), (3, 2), (2, 3), (1, 2), (2, 1)
    ]

    test_cases = [test_polygon1, test_polygon2, test_polygon3]

    for i, original_vertices in enumerate(test_cases, 1):
        print(f"\n{'=' * 100}")
        print(f"测试用例 {i}")
        print(f"{'=' * 100}")

        # 1. 将顶点按逆时针顺序排序
        sorted_vertices = sort_vertices_counterclockwise(original_vertices)

        # 2. 计算内角并找出大于200度的顶点
        large_angle_vertices, sorted_angles = find_vertices_with_large_angles(sorted_vertices, threshold=200)

        # 3. 计算原始多边形的内角
        original_angles = calculate_internal_angles(original_vertices)

        # 4. 打印详细对比信息
        print_detailed_comparison(original_vertices, sorted_vertices, original_angles, sorted_angles,
                                  large_angle_vertices)

        # 5. 可视化对比（现在返回原始多边形的内角）
        original_angles = visualize_comparison(original_vertices, sorted_vertices, large_angle_vertices, sorted_angles,
                                               f"测试用例 {i} - 多边形对比分析")

        print(f"\n测试用例 {i} 分析完成")
        print(f"{'=' * 100}\n")