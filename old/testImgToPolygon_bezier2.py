from skimage.segmentation import slic
from skimage.color import rgb2lab
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev
import cv2
#方法2：基于超像素分割和贝塞尔拟合
def superpixel_bezier(image_path, n_segments=100, compactness=10, smoothness=0.1):
    # 读取图像
    img = plt.imread(image_path)
    h, w = img.shape[:2]

    # SLIC超像素分割
    segments = slic(img, n_segments=n_segments, compactness=compactness,
                    convert2lab=True, start_label=1)

    # 创建空白画布
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    ax1.imshow(img)
    ax1.set_title('Original Image')

    # 对每个超像素进行贝塞尔拟合
    for i in np.unique(segments):
        # 创建当前超像素的掩码
        mask = np.zeros_like(segments, dtype=np.uint8)
        mask[segments == i] = 255

        # 查找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            # 简化轮廓
            epsilon = 0.01 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)

            points = approx.squeeze()
            if len(points) < 4:
                continue

            # 闭合曲线
            points = np.vstack([points, points[0]])

            # 计算区域平均颜色
            region_mask = segments == i
            avg_color = np.mean(img[region_mask], axis=0)

            # 贝塞尔拟合
            tck, u = splprep([points[:, 0], points[:, 1]], s=smoothness, per=True)
            u_new = np.linspace(0, 1, 100)
            x_new, y_new = splev(u_new, tck)

            # 绘制
            ax2.plot(x_new, y_new, '-', linewidth=1, color=avg_color)
            ax2.fill(x_new, y_new, color=avg_color, alpha=0.4)

    ax2.set_title('Bezier-fitted Superpixels')
    ax2.invert_yaxis()  # y轴反向
    plt.tight_layout()
    plt.show()


# 使用示例
# superpixel_bezier('input.jpg', n_segments=150, compactness=20, smoothness=0.2)
superpixel_bezier('../imgs/jimeng-mengnalisha1.png', n_segments=150, compactness=20, smoothness=0.2)