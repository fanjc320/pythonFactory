from shapely.geometry import Polygon, LineString, MultiPolygon
from shapely.ops import split, polygonize
import numpy as np

#根据"瓶颈"分割多边形
# def find_neck(polygon, angle_threshold=60, min_width_ratio=0.2):
def find_neck(polygon, angle_threshold=60, min_width_ratio=0.5):
    """
    寻找多边形中的"颈部"（最窄的连接部分）
    参数:
        polygon: 要分割的多边形
        angle_threshold: 被认为是凹点的角度阈值(度)
        min_width_ratio: 最小宽度与包围盒宽度的比例
    返回:
        分割线(LineString)或None(如果找不到合适的颈部)
    """
    # 获取多边形顶点
    coords = list(polygon.exterior.coords)
    n = len(coords)

    # 计算每个顶点的角度
    angles = []
    for i in range(n):
        a = np.array(coords[i - 1])
        b = np.array(coords[i])
        c = np.array(coords[(i + 1) % n])

        ba = a - b
        bc = c - b
        norm_ba = np.linalg.norm(ba)
        norm_bc = np.linalg.norm(bc)
        if norm_ba == 0 or norm_bc == 0:
            cosine_angle = np.nan  # or handle it differently
        else:
            cosine_angle = np.dot(ba, bc) / (norm_ba * norm_bc)
        print("{(np.linalg.norm(ba)} {(np.linalg.norm(bc)} ", norm_bc, " ",norm_ba)
        angle = np.degrees(np.arccos(cosine_angle))
        angles.append(angle)

    # 寻找凹点候选
    concave_points = [i for i, angle in enumerate(angles) if angle > angle_threshold]
    # for point in concave_points:
    #     print("point:", point)
    # 评估凹点对之间的连接
    for bound in polygon.bounds:
        print("bound:", bound)
    min_width = polygon.bounds[2] - polygon.bounds[0]  # 初始化为包围盒宽度
    best_pair = None

    for i in range(len(concave_points)):
        for j in range(i + 1, len(concave_points)):
            p1 = coords[concave_points[i]]
            p2 = coords[concave_points[j]]

            # 创建连接线
            line = LineString([p1, p2])
            print("line:",line)
            # 检查线是否完全在多边形内部
            if line.within(polygon):
                # 计算线的长度作为颈部宽度
                width = line.length
                print("line.width:", width, " min_width:", min_width)
                if width < min_width and width / (polygon.bounds[2] - polygon.bounds[0]) < min_width_ratio:
                    min_width = width
                    best_pair = (p1, p2)
                    print("min_width:${min_width}",min_width, " best_pair:${best_pair}")

    if best_pair:
        return LineString(best_pair)
    return None


def split_polygon_at_neck(polygon):
    """
    在多形颈部进行分割
    参数:
        polygon: 要分割的多边形
    返回:
        分割后的多边形列表
    """
    # 寻找颈部
    neck = find_neck(polygon)

    if not neck:
        print("not neck!!!!")
        return [polygon]

    # 使用分割线分割多边形
    result = split(polygon, neck)

    # 将结果转换为多边形列表
    polygons = list(polygonize(result))

    # 过滤掉可能产生的无效几何体
    valid_polygons = [p for p in polygons if isinstance(p, Polygon) and not p.is_empty]

    return valid_polygons


def split_complex_polygon(polygon, max_iter=5):
    """
    递归分割复杂多边形直到没有明显颈部
    参数:
        polygon: 要分割的多边形
        max_iter: 最大递归次数
    返回:
        分割后的多边形列表
    """
    if max_iter <= 0:
        return [polygon]

    parts = split_polygon_at_neck(polygon)
    print("parts num----------- :", len(parts))

    if len(parts) == 1:
        return parts

    final_parts = []
    for part in parts:
        sub_parts = split_complex_polygon(part, max_iter - 1)
        final_parts.extend(sub_parts)

    return final_parts


# 示例用法
if __name__ == "__main__":
    # 创建一个有分叉的示例多边形
    poly = Polygon([(0, 0), (2, 0), (2, 1), (3, 1), (3, 3), (1, 3), (1, 2), (0, 2), (0, 0)])

    print("原始多边形:", poly)

    # 分割多边形
    split_polys = split_complex_polygon(poly)

    print("\n分割结果:")
    for i, p in enumerate(split_polys, 1):
        print(f"多边形{i}:", p)