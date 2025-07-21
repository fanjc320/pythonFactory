#线段共线
def cross_product(a, b):
    """叉积"""
    return a[0] * b[1] - a[1] * b[0]


# def is_point_on_segment(a, b, c):
#     """判断点c是否在线段ab上"""
#     # 先检查c是否在ab的矩形范围内
#     if min(a[0], b[0]) <= c[0] <= max(a[0], b[0]) and (min(a[1], b[1]) <= c[1] <= max(a[1], b[1]):
#         # 检查共线
#         cross = cross_product((b[0]-a[0], b[1]-a[1]), (c[0]-a[0], c[1]-a[1]))
#         return abs(cross) < 1e-10
#     return False


def is_point_on_segment(a, b, c):
    """
    Check if point c lies on the line segment between points a and b.

    Args:
        a, b: The endpoints of the segment (each as (x, y) tuples)
        c: The point to check (as (x, y) tuple)

    Returns:
        bool: True if c is on the segment ab, False otherwise
    """
    # First check if the points are colinear
    cross_product = (c[1] - a[1]) * (b[0] - a[0]) - (c[0] - a[0]) * (b[1] - a[1])

    # If not colinear, return False
    if abs(cross_product) > 1e-12:
        return False

    # Check if c is between a and b
    if min(a[0], b[0]) <= c[0] <= max(a[0], b[0]) and min(a[1], b[1]) <= c[1] <= max(a[1], b[1]):
        return True

    return False

def segments_intersect(seg1, seg2):
    """判断两条线段是否相交，共同顶点不算相交"""
    # print("segments_intersect seg1:{} seg2:{}".format(seg1, seg2)) # segments_intersect seg1:((0, 0), (2, 2)) seg2:((0, 2), (2, 0))
    a, b = seg1  # 线段1的端点
    c, d = seg2  # 线段2的端点

    # 检查是否有共同顶点
    if (a == c or a == d or b == c or b == d):
    # if (a == c).all() or (a == d).all() or (b == c).all() or (b == d).all():
        return False

    # 计算四个叉积
    ab_ac = cross_product((b[0] - a[0], b[1] - a[1]), (c[0] - a[0], c[1] - a[1]))
    ab_ad = cross_product((b[0] - a[0], b[1] - a[1]), (d[0] - a[0], d[1] - a[1]))
    cd_ca = cross_product((d[0] - c[0], d[1] - c[1]), (a[0] - c[0], a[1] - c[1]))
    cd_cb = cross_product((d[0] - c[0], d[1] - c[1]), (b[0] - c[0], b[1] - c[1]))

    # 快速排斥实验
    if max(a[0], b[0]) < min(c[0], d[0]) or max(c[0], d[0]) < min(a[0], b[0]) or \
            max(a[1], b[1]) < min(c[1], d[1]) or max(c[1], d[1]) < min(a[1], b[1]):
        return False

    # 跨立实验
    if ab_ac * ab_ad < 0 and cd_ca * cd_cb < 0:
        return True

    # 检查端点是否在另一条线段上（共线情况）
    if is_point_on_segment(a, b, c) or is_point_on_segment(a, b, d) or \
            is_point_on_segment(c, d, a) or is_point_on_segment(c, d, b):
        return True

    return False


# 测试用例
if __name__ == "__main__":
    # 测试1: 相交线段
    seg1 = ((0, 0), (2, 2))
    seg2 = ((0, 2), (2, 0))
    print(segments_intersect(seg1, seg2))  # 应输出 True

    # 测试2: 不相交线段
    seg3 = ((0, 0), (1, 1))
    seg4 = ((2, 2), (3, 3))
    print(segments_intersect(seg3, seg4))  # 应输出 False

    # 测试3: 有共同顶点但不视为相交
    seg5 = ((0, 0), (1, 1))
    seg6 = ((1, 1), (2, 2))
    print(segments_intersect(seg5, seg6))  # 应输出 False

    # 测试4: 共线但不重叠
    seg7 = ((0, 0), (1, 1))
    seg8 = ((2, 2), (3, 3))
    print(segments_intersect(seg7, seg8))  # 应输出 False

    # 测试5: 共线且重叠
    seg9 = ((0, 0), (2, 2))
    seg10 = ((1, 1), (3, 3))
    print(segments_intersect(seg9, seg10))  # 应输出 True