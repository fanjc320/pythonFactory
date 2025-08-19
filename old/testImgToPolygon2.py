import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay


def image_to_triangles(image_path, points_count=100):
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
    corners = np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], dtype=np.float32)
    points = np.vstack([points, corners])

    # Delaunay三角剖分
    tri = Delaunay(points)

    return points, tri.simplices


# 使用示例
# points, triangles = image_to_triangles('input.jpg', points_count=200)
points, triangles = image_to_triangles('../imgs/jimeng-mengnalisha1.png', points_count=200)

# 可视化结果
# img = cv2.imread('input.jpg')
img = cv2.imread('../imgs/jimeng-mengnalisha1.png')
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.triplot(points[:, 0], points[:, 1], triangles, 'g-', linewidth=0.5, alpha=0.7)
plt.plot(points[:, 0], points[:, 1], 'r.', markersize=2)
plt.show()