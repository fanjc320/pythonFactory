# 这篇博客介绍了中轴线（骨架）提取算法，通过距离变换和像素查找表操作实现。https://blog.csdn.net/u011046017/article/details/115524873
import numpy as np
from skimage.data import horse, camera
import matplotlib.pyplot as plt
import scipy.ndimage as ndimg
from numba import jit
import cv2
from scipy.ndimage import label, generate_binary_structure

strc = np.ones((3, 3), dtype=bool)


# check whether this pixcel can be removed
def check(n):
    a = [(n >> i) & 1 for i in range(8)]
    a.insert(4, 0)  # make the 3x3 unit
    # if up, down, left, right all are 1, you cannot make a hole
    # if a[1] & a[3] & a[5] & a[7]:return False
    a = np.array(a).reshape((3, 3))
    # segments
    n = label(a, strc)[1]
    # if sum is 0, it is a isolate point, you cannot remove it.
    # if number of segments > 2, you cannot split them.
    return n < 2
    return a.sum() > 1 and n < 2
    if a.sum() == 1 or n > 2: return 2
    if a.sum() > 1 and n < 2: return 1
    return 0


lut = np.array([check(n) for n in range(256)])
lut = np.dot(lut.reshape((-1, 8)), [1, 2, 4, 8, 16, 32, 64, 128]).astype(np.uint8)
'''
lut = np.array([200, 206, 220, 204, 0, 207, 0, 204, 0, 207, 221, 51, 1, 207, 221, 51,
       0, 0, 221, 204, 0, 0, 0, 204, 1, 207, 221, 51, 1, 207, 221, 51], dtype=np.int8)
'''


@jit
def skel2dp(data, idx, lup):
    h, w = data.shape
    data = data.ravel()
    for id in idx:

        if data[id] == 0: continue
        i2 = id - w
        i8 = id + w
        i1 = i2 - 1
        i3 = i2 + 1
        i4 = id - 1
        i6 = id + 1
        i7 = i8 - 1
        i9 = i8 + 1
        c = (data[i1] > 0) << 0 | (data[i2] > 0) << 1 \
            | (data[i3] > 0) << 2 | (data[i4] > 0) << 3 \
            | (data[i6] > 0) << 4 | (data[i7] > 0) << 5 \
            | (data[i8] > 0) << 6 | (data[i9] > 0) << 7
        if (lup[c // 8] >> c % 8) & 1: data[id] = 0
    return 0


def mid_axis(img):
    dis = ndimg.distance_transform_edt(img)
    idx = np.argsort(dis.flat).astype(np.int32)
    skel2dp(dis, idx, lut)
    return dis


from time import time
img = ~horse()*255
#img = cv2.imread('123.jpg')
#img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
#ret2, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
dis = ndimg.distance_transform_edt(img)
plt.imshow(dis)
idx = np.argsort(dis.flat).astype(np.int32)
a = skel2dp(dis, idx, lut)
#mid_axis(img.copy())
t1 = time()
a = mid_axis(img)
t2 = time()
print(t2 - t1)
plt.imshow(a)
plt.show()