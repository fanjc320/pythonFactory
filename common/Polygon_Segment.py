from shapely.geometry import LineString, Polygon, MultiLineString
from shapely.ops import split


def is_line_inside_polygon(line, polygon):
    """
    判断线段是否完全位于多边形内部（包括共线情况）

    参数:
        line: LineString对象，表示要检查的线段
        polygon: Polygon对象，表示多边形

    返回:
        bool: 如果线段完全位于多边形内部或边界上，返回True；否则返回False
    """
    print("is_line_inside_polygon line:", line, " polygon:", polygon)#line: LINESTRING (1 1, 1.5 1.5)  polygon: POLYGON ((0 0, 2 0, 2 2, 1 3, 0 2, 0 0))
    # 检查线段是否完全在多边形内部或边界上
    if not line.within(polygon) and not line.touches(polygon):
        return False

    # 检查线段是否与多边形边界完全共线
    boundary = polygon.boundary
    if line.intersection(boundary) == line:
        return True

    # 检查线段是否完全在多边形内部
    if line.within(polygon):
        return True

    return False


# 示例用法
if __name__ == "__main__":
    # 定义一个多边形（五边形）
    polygon = Polygon([(0, 0), (2, 0), (2, 2), (1, 3), (0, 2)])

    # 测试线段1：完全在多边形内部
    line1 = LineString([(1, 1), (1.5, 1.5)])
    print(is_line_inside_polygon(line1, polygon))  # 应输出 True

    # 测试线段2：与多边形边共线
    line2 = LineString([(0, 0), (2, 0)])
    print(is_line_inside_polygon(line2, polygon))  # 应输出 True

    # 测试线段3：部分在多边形外部
    line3 = LineString([(1, 1), (3, 1)])
    print(is_line_inside_polygon(line3, polygon))  # 应输出 False

    # 测试线段4：端点接触边界但不在内部
    line4 = LineString([(2, 0), (3, 0)])
    print(is_line_inside_polygon(line4, polygon))  # 应输出 False