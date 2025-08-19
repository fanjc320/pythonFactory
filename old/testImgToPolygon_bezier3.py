import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev
#方法3：基于边缘检测和贝塞尔拟合
def edge_based_bezier(image_path, threshold1=100, threshold2=200, smoothness=0.1):
    # 读取图像
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Canny边缘检测
    edges = cv2.Canny(gray, threshold1, threshold2)

    # 查找轮廓
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 创建画布
    plt.figure(figsize=(12, 6))
    plt.subplot(121)
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.title('Original Image')

    plt.subplot(122)
    plt.imshow(np.zeros_like(img), extent=[0, img.shape[1], 0, img.shape[0]])

    for cnt in contours:
        # 简化轮廓
        epsilon = 0.005 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        points = approx.squeeze()
        if len(points) < 4:
            continue

        # 闭合曲线
        points = np.vstack([points, points[0]])

        # 贝塞尔拟合
        tck, u = splprep([points[:, 0], points[:, 1]], s=smoothness, per=True)
        u_new = np.linspace(0, 1, 100)
        x_new, y_new = splev(u_new, tck)

        # 绘制
        plt.plot(x_new, y_new, '-', linewidth=1.5, color='white')

    plt.title('Edge-based Bezier Fitting')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()


# 使用示例
# edge_based_bezier('input.jpg', threshold1=50, threshold2=150, smoothness=0.15)
# edge_based_bezier('imgs/jimeng-mengnalisha1.png', threshold1=15, threshold2=100, smoothness=0.05)
# edge_based_bezier('imgs/jimeng-bunny1.jpeg', threshold1=15, threshold2=100, smoothness=0.05)
edge_based_bezier('../imgs/jimeng-girl1.jpeg', threshold1=15, threshold2=100, smoothness=0.05)