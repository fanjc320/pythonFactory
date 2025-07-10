import matplotlib
from matplotlib.font_manager import FontManager
import numpy as np
# import matplotlib.pyplot as plt
from matplotlib import pyplot as plt
from testSVG.polygon import getPolygonFromPath
import cv2
# mpl_fonts = set(f.name for f in FontManager().ttflist)
# print('all font list get from matplotlib.font_manager:')
# for f in sorted(mpl_fonts):
#     print('\t' + f)

matplotlib.rc("font",family='MicroSoft YaHei',weight="bold") #解决matplotlib乱码的问题
def calculate_curvature(points, k=3):
    """计算离散点集的曲率"""
    n = len(points)
    curvatures = np.zeros(n)

    for i in range(n):
        # 取前后k个点计算曲率
        window = []
        for j in range(-k, k + 1):
            idx = (i + j) % n
            window.append(points[idx])

        x = [p[0] for p in window]
        y = [p[1] for p in window]

        # 计算一阶和二阶导数
        dx = np.gradient(x)
        dy = np.gradient(y)
        ddx = np.gradient(dx)
        ddy = np.gradient(dy)

        # 曲率公式
        curvature = np.abs(dx[-1] * ddy[-1] - dy[-1] * ddx[-1]) / (dx[-1] ** 2 + dy[-1] ** 2) ** 1.5
        curvatures[i] = curvature

    return curvatures


def find_peaks(curvatures, threshold=0.1, min_dist=1):
    """寻找曲率极值点"""
    peaks = []
    n = len(curvatures)

    for i in range(1, n - 1):
        if (curvatures[i] > curvatures[i - 1] and
                curvatures[i] > curvatures[i + 1] and
                curvatures[i] > threshold):
            # 检查最小距离
            if not any(abs(i - p) <= min_dist for p in peaks):
                peaks.append(i)

    return peaks


# 示例多边形
points = np.array([
    [0, 0], [1, 0], [2, 0.2], [3, 0], [4, 0],
    [4, 1], [3.5, 1.5], [3, 1], [2, 1.5], [1, 1], [0, 1]
])

all_polygons = getPolygonFromPath("./testSVG/test_polygon2.svg")
polygon_np = all_polygons[0]
print("before polygon_np:", polygon_np)
# polygon_np = [list(t) for t in polygon_np]
polygon_np = np.array(polygon_np)
points = polygon_np
# def testCurvature():
# 计算曲率
curvatures = calculate_curvature(points)
peaks = find_peaks(curvatures, threshold=0.3)
# 可视化
plt.figure(figsize=(12, 5))
plt.subplot(121)
plt.plot(*zip(*np.vstack([points, points[0]])), 'b-')
plt.plot(points[:, 0], points[:, 1], 'ro')
plt.title('原始多边形')
plt.subplot(122)
plt.plot(curvatures, 'g-')
plt.plot(peaks, curvatures[peaks], 'ro')
plt.title('曲率极值点检测')
plt.tight_layout()
plt.show()
print("检测到的曲率极值点索引:", peaks)
print("对应的点坐标:", points[peaks])


def detect_corners(points, quality_level=0.01, min_distance=10):
    """使用Harris角点检测"""
    # 将多边形转换为图像
    points = np.array(points, dtype=np.float32)
    min_coords = np.min(points, axis=0)
    max_coords = np.max(points, axis=0)
    size = (max_coords - min_coords + 20).astype(np.int32)

    # 创建空白图像并绘制多边形
    img = np.zeros((size[1], size[0]), dtype=np.uint8)
    shifted_points = (points - min_coords + 10).astype(np.int32)
    cv2.fillPoly(img, [shifted_points], 255)

    # Harris角点检测
    corners = cv2.cornerHarris(img, blockSize=2, ksize=3, k=0.04)
    corners = cv2.dilate(corners, None)

    # 筛选角点
    threshold = quality_level * corners.max()
    corner_coords = np.argwhere(corners > threshold)

    # 转换回原始坐标
    detected_points = corner_coords[:, ::-1] + min_coords - 10

    # 找到最近的原始多边形点
    result_indices = []
    for p in detected_points:
        distances = np.linalg.norm(points - p, axis=1)
        nearest_idx = np.argmin(distances)
        if nearest_idx not in result_indices:
            result_indices.append(nearest_idx)

    return result_indices

#太多
corner_indices = detect_corners(points)
# print("Harris检测到的角点索引:", corner_indices)
# print("对应的点坐标:", points[corner_indices])

##############################################################
#
# def determine_concavity(points, extrema):
#     """
#     判断极值点的凹凸性
#     """
#     results = []
#
#     for idx, typ, val in extrema:
#         # 当前点及其相邻点
#         prev = points[(idx - 1) % len(points)]
#         curr = points[idx]
#         next_p = points[(idx + 1) % len(points)]
#
#         # 计算叉积判断凹凸性
#         vec1 = np.array(prev) - np.array(curr)
#         vec2 = np.array(next_p) - np.array(curr)
#         cross = np.cross(vec1, vec2)
#
#         # 叉积为正表示凸(convex)，为负表示凹(concave)
#         if cross > 0:
#             concavity = 'convex'
#         else:
#             concavity = 'concave'
#
#         results.append({
#             'index': idx,
#             'point': curr,
#             'type': typ,
#             'curvature': val,
#             'concavity': concavity
#         })
#
#     return results
#
# # 判断凹凸性
# results = determine_concavity(points, points[peaks])
# # 打印结果
# print("曲率极值点及其凹凸性:")
# for res in results:
#     print(f"顶点 {res['index']} ({res['point']}):")
#     print(f"  类型: {res['type']}, 曲率: {res['curvature']:.2f}, 凹凸性: {res['concavity']}")


###############################################################
def douglas_peucker(points, epsilon):
    """Douglas-Peucker算法简化多边形"""
    points = np.array(points)
    print("points num:", len(points))
    # 使用OpenCV实现
    approx = cv2.approxPolyDP(points, epsilon, closed=True)
    # 找到保留点的原始索引
    retained_indices = []
    for p in approx.squeeze():
        distances = np.linalg.norm(points - p, axis=1)
        retained_indices.append(np.argmin(distances))
    return retained_indices

# 使用Douglas-Peucker算法
# def test_douglas_peucker():
dp_indices = douglas_peucker(points, epsilon=0.1)
print("Douglas-Peucker算法检测到的关键点索引:", dp_indices)
print("对应的点坐标:", points[dp_indices])

# test_douglas_peucker()

# 可视化所有方法检测结果
plt.figure(figsize=(10, 6))
plt.plot(*zip(*np.vstack([points, points[0]])), 'b-', label='多边形')
plt.plot(points[:, 0], points[:, 1], 'ko', label='所有顶点')

# 标记不同方法检测到的点
plt.plot(points[peaks, 0], points[peaks, 1], 'ro', markersize=10, label='曲率极值点')
plt.plot(points[corner_indices, 0], points[corner_indices, 1], 'gs', markersize=8, label='Harris角点')
plt.plot(points[dp_indices, 0], points[dp_indices, 1], 'm^', markersize=8, label='DP算法关键点')

plt.legend()
plt.axis('equal')
plt.title('多边形曲率极值点检测比较')
plt.show()