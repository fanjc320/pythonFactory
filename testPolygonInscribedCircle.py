import numpy as np
from skimage.morphology import medial_axis
from skimage.draw import polygon
import matplotlib.pyplot as plt

def testInscribedCircle():
    # 创建多边形（示例为矩形）
    polygon_vertices = np.array([[50, 50], [150, 50], [150, 150], [50, 150]])
    img = np.zeros((200, 200), dtype=np.uint8)
    rr, cc = polygon(polygon_vertices[:, 0], polygon_vertices[:, 1], img.shape)
    img[rr, cc] = 1
    from scipy.ndimage import distance_transform_edt

    # 计算距离变换
    dist_transform = distance_transform_edt(img)

    # 找到最大内切圆的半径和中心
    radius = np.max(dist_transform)
    center = np.unravel_index(np.argmax(dist_transform), dist_transform.shape)

    # 绘制结果
    plt.imshow(img, cmap='gray')
    circle = plt.Circle((center[1], center[0]), radius, color='r', fill=False)
    plt.gca().add_patch(circle)
    plt.title(f'Maximum Inscribed Circle (Radius: {radius:.1f})')
    plt.show()

testInscribedCircle()