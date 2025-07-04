import cv2
import numpy as np
from subprocess import call
#转化成lowpoly风格
# 1. 读取图片并边缘检测
img = cv2.imread("jimeng-2025-06-03-692-.jpeg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray, 100, 200)

# 2. 提取特征点
points = np.argwhere(edges > 0)
points = np.fliplr(points).astype(np.float32)

# 3. Delaunay三角剖分
rect = (0, 0, img.shape[1], img.shape[0])
subdiv = cv2.Subdiv2D(rect)
subdiv.insert(points)
triangles = subdiv.getTriangleList()

# 4. 绘制低多边形效果
output = np.zeros_like(img)
for t in triangles:
    pts = t.reshape(3, 2).astype(np.int32)
    color = np.mean(img[pts[:, 1], pts[:, 0]], axis=0)
    cv2.fillPoly(output, [pts], color)

cv2.imwrite("low_poly_output.jpg", output)