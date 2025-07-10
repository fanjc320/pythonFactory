import matplotlib
from matplotlib.font_manager import FontManager
import numpy as np
# import matplotlib.pyplot as plt
from matplotlib import pyplot as plt
from testSVG.polygon import getPolygonFromPath

def compute_curvature(points):
    """
    计算多边形各顶点的曲率(转角)
    """
    n = len(points)
    curvatures = []

    for i in range(n):
        # 前一个点、当前点和下一个点
        prev = points[(i - 1) % n]
        curr = points[i]
        next_p = points[(i + 1) % n]

        # 向量1: 前一点到当前点
        vec1 = np.array(prev) - np.array(curr)
        # 向量2: 当前点到后一点
        vec2 = np.array(next_p) - np.array(curr)

        # 计算转角(曲率的简单表示)
        angle = np.arctan2(vec2[1], vec2[0]) - np.arctan2(vec1[1], vec1[0])
        angle = (angle + np.pi) % (2 * np.pi) - np.pi  # 归一化到[-π, π]

        curvatures.append(angle)

    return curvatures


def find_extrema(curvatures):
    """
    找到曲率极值点(局部极大值和极小值)
    """
    n = len(curvatures)
    extrema = []

    for i in range(n):
        prev = curvatures[(i - 1) % n]
        curr = curvatures[i]
        next_c = curvatures[(i + 1) % n]

        # 局部极大值
        if curr > prev and curr > next_c:
            extrema.append((i, 'max', curr))
        # 局部极小值
        elif curr < prev and curr < next_c:
            extrema.append((i, 'min', curr))

    return extrema


def determine_concavity(points, extrema):
    """
    判断极值点的凹凸性
    """
    results = []

    for idx, typ, val in extrema:
        # 当前点及其相邻点
        prev = points[(idx - 1) % len(points)]
        curr = points[idx]
        next_p = points[(idx + 1) % len(points)]

        # 计算叉积判断凹凸性
        vec1 = np.array(prev) - np.array(curr)
        vec2 = np.array(next_p) - np.array(curr)
        cross = np.cross(vec1, vec2)

        # 叉积为正表示凸(convex)，为负表示凹(concave)
        if cross > 0:
            concavity = 'convex'
        else:
            concavity = 'concave'

        results.append({
            'index': idx,
            'point': curr,
            'type': typ,
            'curvature': val,
            'concavity': concavity
        })

    return results


# 示例使用
if __name__ == "__main__":
    # 定义一个多边形顶点(按顺时针或逆时针顺序)
    # points = [(0, 0), (1, 1), (2, 0), (3, 1), (2, 2), (1, 1.5)]
    all_polygons = getPolygonFromPath("./testSVG/test_polygon2.svg")
    polygon_np = all_polygons[0]
    print("before polygon_np:", polygon_np)
    # polygon_np = [list(t) for t in polygon_np]
    polygon_np = np.array(polygon_np)
    points = polygon_np
    # 计算曲率
    curvatures = compute_curvature(points)

    # 找到极值点
    extrema = find_extrema(curvatures)

    # 判断凹凸性
    results = determine_concavity(points, extrema)

    # 打印结果
    print("曲率极值点及其凹凸性:")
    for res in results:
        print(f"顶点 {res['index']} ({res['point']}):")
        print(f"  类型: {res['type']}, 曲率: {res['curvature']:.2f}, 凹凸性: {res['concavity']}")