# OpenCV-Python——第22章：分水岭算法实现图像分割 https://blog.csdn.net/yukinoai/article/details/88575861 https://blog.csdn.net/u011186532/article/details/145411130
# https://docs.opencv.org/3.4/d3/db4/tutorial_py_watershed.html
import numpy as np
import cv2
from matplotlib import pyplot as plt
from shapely.geometry import LinearRing, Polygon
from testSVG.polygon import getPolygonGrayImgFromPath

src = cv2.imread('imgs/coin1.png')
img = src.copy()
# 转换为灰度图像
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# gray = getPolygonGrayImgFromPath("./testSVG/test_polygon01.svg")
print("gray.shape:",gray.shape)
# 使用OTSU方法进行二值化
ret, thresh = cv2.threshold(
    gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# 消除噪声 进行形态学开运算以去除小的噪声点
kernel = np.ones((3, 3), np.uint8)
opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)

# 膨胀操作得到背景区域
sure_bg = cv2.dilate(opening, kernel, iterations=3)
print("sure_bg.shape:",sure_bg.shape)
# 距离变换得到前景区域 https://docs.opencv.org/3.4/d2/dbd/tutorial_distance_transform.html
dist_transform = cv2.distanceTransform(opening, 1, 5)
ret, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)

# 获得未知区域
sure_fg = np.uint8(sure_fg)
unknown = cv2.subtract(sure_bg, sure_fg) # 膨胀操作得到的背景区域-距离变换得到的前景区域

# 标记连通区域
ret, markers1 = cv2.connectedComponents(sure_fg) #https://blog.csdn.net/jgj123321/article/details/93489417
#https://blog.csdn.net/m0_37816922/article/details/136638105
# print("connectedComponents ret:", ret, "markers1:", markers1)# markers1 有不同的值，0,8,12,....等
# 所有标记加1，确保背景标记为1而不是0
markers = markers1 + 1
print("markers.shape:",markers.shape)
# 未知区域标记为0
markers[unknown == 255] = 0

# 使用分水岭算法进行分割
markers3 = cv2.watershed(img, markers)#
# markers3 = cv2.watershed(gray, markers)# 报错
print("markers3 type:", type(markers3))#markers3 有-1，1， 9，10，11,12...等各种值
markers4 = markers3.copy()
markers4[markers4 != -1] = 0
markers4[markers4 == -1] = 255

img[markers3 == -1] = [0, 0, 255] # The boundary region will be marked with -1.

# plt.subplot(341), plt.imshow(cv2.cvtColor(src, cv2.COLOR_BGR2RGB)),
# plt.title('Original'), plt.axis('off')
# plt.subplot(342), plt.imshow(thresh, cmap='gray'),
# plt.title('Threshold thresh'), plt.axis('off')
# plt.subplot(343), plt.imshow(sure_bg, cmap='gray'),
# plt.title('Dilate sure_bg'), plt.axis('off')
# plt.subplot(344), plt.imshow(dist_transform, cmap='gray'),
# plt.title('Dist Transform'), plt.axis('off')
# plt.subplot(345), plt.imshow(sure_fg, cmap='gray'),
# plt.title('sure_fg'), plt.axis('off')
#
# plt.subplot(346), plt.imshow(unknown, cmap='gray'),
# plt.title('Unkown'), plt.axis('off')
# plt.subplot(347), plt.imshow(markers1, cmap='jet'),
# plt.title('Markers1 from sure_fg'), plt.axis('off')
#
# plt.subplot(348), plt.imshow(np.abs(markers), cmap='jet'),
# plt.title('Markers'), plt.axis('off')
# plt.subplot(349), plt.imshow(np.abs(markers3), cmap='jet'),
# plt.title('Markers3'), plt.axis('off')
# plt.subplot(3410), plt.imshow(np.abs(markers4), cmap='gray'),
# plt.title('Markers4'), plt.axis('off')
# plt.subplot(3411), plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)),
# plt.title('Result'), plt.axis('off')

fig, axes = plt.subplots(nrows=3, ncols=4, figsize=(36, 27))
axes[0, 0].imshow(cv2.cvtColor(src, cv2.COLOR_BGR2RGB))
axes[0, 0].set_title('Original'), axes[0, 0].axis('off')
axes[0, 1].imshow(thresh, cmap='gray'),
axes[0, 1].set_title('thresh'), axes[0, 1].axis('off')
axes[0, 2].imshow(sure_bg, cmap='gray'),
axes[0, 2].set_title('Dilate sure_bg'), axes[0, 2].axis('off')
axes[0, 3].imshow(dist_transform, cmap='gray'),
axes[0, 3].set_title('Dist Transform'), axes[0, 3].axis('off')
axes[1, 0].imshow(sure_fg, cmap='gray'),
axes[1, 0].set_title('sure_fg'), axes[1, 0].axis('off')

axes[1, 1].imshow(unknown, cmap='gray'),
axes[1, 1].set_title('Unkown'), axes[1, 1].axis('off')
axes[1, 2].imshow(markers1, cmap='jet'),
axes[1, 2].set_title('Markers1 from sure_fg'), axes[1, 2].axis('off')

axes[1, 3].imshow(np.abs(markers), cmap='jet'),
axes[1, 3].set_title('Markers'), axes[1, 3].axis('off')
axes[2, 0].imshow(np.abs(markers3), cmap='jet'),
axes[2, 0].set_title('Markers3'), axes[2, 0].axis('off')
axes[2, 1].imshow(np.abs(markers4), cmap='gray'),
axes[2, 1].set_title('Markers4'), axes[2, 1].axis('off')
axes[2, 2].imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)),
axes[2, 2].set_title('Result'), axes[2, 2].axis('off')

plt.show()