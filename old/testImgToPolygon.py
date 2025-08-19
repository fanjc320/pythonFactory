import cv2
import numpy as np
import matplotlib.pyplot as plt


def image_to_polygons(image_path, epsilon=0.01, min_area=100):
    # 读取图像并转为灰度
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 二值化处理
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

    # 查找轮廓
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    polygons = []
    for cnt in contours:
        # 计算轮廓面积，过滤小区域
        area = cv2.contourArea(cnt)
        if area < min_area:
            continue

        # 多边形近似
        # epsilon = epsilon * cv2.arcLength(cnt, True) # 太小了会报错
        print("image_to_polygons epsilon:", epsilon)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        # 转换为点列表
        points = approx.reshape(-1, 2).tolist()
        polygons.append(points)

    return polygons


# 使用示例
# polygons = image_to_polygons('input.jpg', epsilon=0.02, min_area=50)
polygons = image_to_polygons('../imgs/jimeng_mengnalisha.png', epsilon=0.02, min_area=50)

# 可视化结果
# img = cv2.imread('input.jpg')
img = cv2.imread('../imgs/jimeng_mengnalisha.png')
for poly in polygons:
    pts = np.array(poly, np.int32)
    pts = pts.reshape((-1, 1, 2))
    cv2.polylines(img, [pts], True, (0, 255, 0), 2)

plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.show()