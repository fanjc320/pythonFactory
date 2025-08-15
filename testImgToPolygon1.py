from skimage import io, measure, color
from skimage.filters import sobel
from skimage.segmentation import felzenszwalb
import matplotlib.pyplot as plt
import numpy as np

def segment_to_polygons(image_path, scale=100, sigma=0.5, min_size=50):
    # 读取图像
    img = io.imread(image_path)

    # 图像分割
    segments = felzenszwalb(img, scale=scale, sigma=sigma, min_size=min_size)

    polygons = []
    for region in measure.regionprops(segments):
        # 获取每个区域的轮廓
        contour = measure.find_contours(segments == region.label, 0.5)[0]

        # 简化多边形
        polygons.append(contour.tolist())

    return polygons, segments


# 使用示例
# polygons, segments = segment_to_polygons('input.jpg')
polygons, segments = segment_to_polygons('imgs/jimeng-mengnalisha1.png')

# 可视化结果
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
ax1.imshow(segments, cmap='tab20')
ax1.set_title('Segmentation')
# ax2.imshow(io.imread('input.jpg'))
ax2.imshow(io.imread('imgs/jimeng-mengnalisha1.png'))
for poly in polygons:
    poly_arr = np.array(poly)
    ax2.plot(poly_arr[:, 1], poly_arr[:, 0], linewidth=2)
ax2.set_title('Polygons')
plt.show()