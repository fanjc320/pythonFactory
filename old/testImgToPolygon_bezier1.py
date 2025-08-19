import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev
#deepseek python, 导入图片分解成多边形块
# 根据颜色块，用贝塞尔去拟合
# 方法1：基于颜色分割和贝塞尔拟合

def color_segmentation_bezier(image_path, num_colors=5, smoothness=0.1):
    # 读取图像
    img = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w = img.shape[:2]

    # 颜色量化
    pixels = img_rgb.reshape(-1, 3).astype(np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    _, labels, centers = cv2.kmeans(pixels, num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    centers = np.uint8(centers)
    segmented = centers[labels.flatten()].reshape((h, w, 3))

    # 对每种颜色区域进行贝塞尔拟合
    plt.figure(figsize=(12, 6))
    plt.subplot(121)
    plt.imshow(img_rgb)
    plt.title('Original Image')

    plt.subplot(122)
    for i in range(num_colors):
        # 获取当前颜色区域
        mask = np.all(segmented == centers[i], axis=-1).astype(np.uint8) * 255

        # 查找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            # 简化轮廓点
            epsilon = 0.005 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)

            # 转换为点集
            points = approx.squeeze()
            if len(points) < 4:  # 至少需要4个点来拟合贝塞尔曲线
                continue

            # 闭合曲线
            points = np.vstack([points, points[0]])

            # 参数化曲线
            tck, u = splprep([points[:, 0], points[:, 1]], s=smoothness, per=True)

            # 生成平滑曲线
            u_new = np.linspace(0, 1, 100)
            x_new, y_new = splev(u_new, tck)

            # 绘制贝塞尔曲线
            plt.plot(x_new, y_new, '-', linewidth=2, color=centers[i] / 255)
            plt.fill(x_new, y_new, color=centers[i] / 255, alpha=0.3)

    ax = plt.gca()
    ax.invert_yaxis()  # y轴反向

    plt.title('Bezier-fitted Color Regions')
    plt.tight_layout()
    plt.show()


# 使用示例
# color_segmentation_bezier('input.jpg', num_colors=5, smoothness=0.05)
color_segmentation_bezier('../imgs/jimeng-mengnalisha1.png', num_colors=10, smoothness=0.1)