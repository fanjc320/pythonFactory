import numpy as np
from shapely.geometry import Polygon, LineString, MultiPolygon
from shapely.ops import split
import matplotlib
from matplotlib import pyplot as plt
matplotlib.rc("font",family='MicroSoft YaHei',weight="bold")
def calculate_angle(p1, p2, p3):
    """
    计算三个点形成的转角（内角）
    """
    v1 = np.array([p1[0] - p2[0], p1[1] - p2[1]])
    v2 = np.array([p3[0] - p2[0], p3[1] - p2[1]])

    angle = np.arctan2(v1[0] * v2[1] - v1[1] * v2[0], v1[0] * v2[0] + v1[1] * v2[1])
    return np.abs(angle)


def find_inflection_points(polygon_coords, angle_threshold=np.pi / 4):
    """
    找到多边形的拐点
    angle_threshold: 被认为是拐点的最小角度变化阈值
    """
    inflection_points = []
    n = len(polygon_coords)

    for i in range(n):
        p1 = polygon_coords[(i - 1) % n]
        p2 = polygon_coords[i]
        p3 = polygon_coords[(i + 1) % n]

        angle = calculate_angle(p1, p2, p3)
        if angle > angle_threshold:
            inflection_points.append(i)

    return inflection_points


def split_polygon_at_inflections(polygon_coords):
    """
    在拐点处分割多边形
    """
    # 确保多边形是闭合的（首尾点相同）
    if not np.array_equal(polygon_coords[0], polygon_coords[-1]):
        polygon_coords = np.vstack([polygon_coords, polygon_coords[0]])

    inflection_indices = find_inflection_points(polygon_coords)

    if not inflection_indices:
        return [polygon_coords]

    # 创建Shapely多边形对象
    poly = Polygon(polygon_coords)

    # 在拐点之间添加分割线
    split_lines = []
    n = len(inflection_indices)

    # 简单策略：连接相隔的拐点（可根据需要优化）
    for i in range(0, n - 1, 2):
        idx1 = inflection_indices[i]
        idx2 = inflection_indices[i + 1]

        p1 = polygon_coords[idx1]
        p2 = polygon_coords[idx2]

        # 创建分割线
        split_line = LineString([p1, p2])
        split_lines.append(split_line)

    # 应用所有分割线
    result = poly
    for line in split_lines:
        if line.intersects(result):
            split_result = split(result, line)
            # 只保留多边形部分
            if isinstance(split_result, MultiPolygon):
                result = MultiPolygon([p for p in split_result.geoms if isinstance(p, Polygon)])
            elif isinstance(split_result, Polygon):
                result = split_result
            else:
                continue

    # 提取子多边形
    if isinstance(result, MultiPolygon):
        sub_polygons = [np.array(poly.exterior.coords) for poly in result.geoms if isinstance(poly, Polygon)]
    elif isinstance(result, Polygon):
        sub_polygons = [np.array(result.exterior.coords)]
    else:
        sub_polygons = []

    return sub_polygons


# 示例用法
if __name__ == "__main__":
    # 示例多边形坐标（可以替换为你的多边形坐标）
    polygon_coords = np.array([
        [0, 0], [2, 0], [3, 1], [4, 0], [6, 0],
        [6, 2], [5, 3], [6, 4], [6, 6],
        [4, 6], [3, 5], [2, 6], [0, 6],
        [0, 4], [1, 3], [0, 2], [0, 0]
    ])

    sub_polygons = split_polygon_at_inflections(polygon_coords)

    print(f"原始多边形有 {len(polygon_coords)} 个顶点")
    print(f"分割为 {len(sub_polygons)} 个子多边形")

    plt.figure()
    plt.plot(polygon_coords[:, 0], polygon_coords[:, 1], 'b-', label='原始多边形')

    for i, poly in enumerate(sub_polygons):
        plt.fill(poly[:, 0], poly[:, 1], alpha=0.5, label=f'子多边形 {i + 1}')

    plt.legend()
    plt.axis('equal')
    plt.show()