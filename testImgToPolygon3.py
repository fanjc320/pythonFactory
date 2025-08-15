import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d


def image_to_voronoi(image_path, points_count=100):
    # 读取图像
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 使用FAST角点检测
    fast = cv2.FastFeatureDetector_create()
    kp = fast.detect(gray, None)

    # 获取关键点坐标
    points = np.array([k.pt for k in kp], dtype=np.float32)

    # 如果点太多，随机采样
    if len(points) > points_count:
        indices = np.random.choice(len(points), points_count, replace=False)
        points = points[indices]

    # 添加图像四个角点
    h, w = gray.shape
    corners = np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]],
                       dtype=np.float32)
    points = np.vstack([points, corners])

    # 计算Voronoi图
    vor = Voronoi(points)

    return vor


# 使用示例
# vor = image_to_voronoi('input.jpg', points_count=200)
vor = image_to_voronoi('imgs/jimeng-mengnalisha1.png', points_count=200)

# 可视化结果
# img = cv2.imread('input.jpg')
img = cv2.imread('imgs/jimeng-mengnalisha1.png')
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.plot(vor.points[:, 0], vor.points[:, 1], 'r.', markersize=2)

# 正确使用voronoi_plot_2d
fig = voronoi_plot_2d(vor, show_points=False, show_vertices=False, line_width=0.5)
plt.show()