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


# 示例演示
if __name__ == "__main__":
    print("多边形顶点逆时针排序并找出内角大于200度的顶点")
    print("=" * 60)

    # 示例多边形（可能不是逆时针顺序）
    test_polygon = [
        (2, 1), (4, 3), (1, 4), (0, 2), (3, 0), (2, 2)
    ]

    print("原始顶点顺序:")
    for i, (x, y) in enumerate(test_polygon):
        print(f"V{i + 1}: ({x}, {y})")

    # 1. 将顶点按逆时针顺序排序
    sorted_vertices = sort_vertices_counterclockwise(test_polygon)

    print("\n逆时针排序后的顶点:")
    for i, (x, y) in enumerate(sorted_vertices):
        print(f"V{i + 1}: ({x}, {y})")

    # 2. 计算内角并找出大于200度的顶点
    large_angle_vertices, all_angles = find_vertices_with_large_angles(sorted_vertices, threshold=200)

    print(f"\n所有顶点的内角:")
    for i, angle in enumerate(all_angles):
        print(f"V{i + 1}: {angle:.1f}°")

    print(f"\n内角和: {sum(all_angles):.1f}° (理论值: {(len(sorted_vertices) - 2) * 180}°)")

    # 3. 显示结果
    if large_angle_vertices:
        print(f"\n找到 {len(large_angle_vertices)} 个内角大于200度的顶点:")
        for vertex in large_angle_vertices:
            print(
                f"顶点 V{vertex['vertex_index'] + 1} ({vertex['vertex_coord'][0]}, {vertex['vertex_coord'][1]}): {vertex['angle']:.1f}°")
    else:
        print("\n没有找到内角大于200度的顶点")

    # 4. 可视化
    visualize_polygon_with_large_angles(sorted_vertices, large_angle_vertices, all_angles,
                                        "多边形内角分析 - 找出大于200度的顶点")

    # 额外测试用例
    print("\n" + "=" * 60)
    print("额外测试用例:")

    # 测试凹多边形
    concave_polygon = [(0, 0), (4, 0), (3, 1), (4, 2), (0, 2)]
    sorted_concave = sort_vertices_counterclockwise(concave_polygon)
    large_angles_concave, angles_concave = find_vertices_with_large_angles(sorted_concave, 200)

    print(f"\n凹多边形测试 - 找到 {len(large_angles_concave)} 个大角度顶点")
    visualize_polygon_with_large_angles(sorted_concave, large_angles_concave, angles_concave,
                                        "凹多边形内角分析")