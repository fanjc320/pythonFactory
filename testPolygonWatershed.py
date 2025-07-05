# https://blog.csdn.net/sinat_29018995/article/details/123832684
import cv2
import numpy as np
from queue import Queue  # 队列
from  testSVG.test0 import getPolygonFromPath
from skimage.draw import polygon
maxhigh = 255  # 水位
mask = -2  # 用于标记每次涨水时，将会被水淹没的像素
watershed = 0  # 用于标记分水岭边缘


# fixmark = np.array([-1,-1])#用于隔开队列的每个部分

def checkedge(inputidx, w, h):
    if inputidx[0] >= h:
        return -1
    if inputidx[1] >= w:
        return -1
    if inputidx[0] < 0:
        return -1
    if inputidx[1] < 0:
        return -1

    return 0


# def mark_end_que(que):

# que.put(fixmark)

def water(inputimg, size):
    imsize = size[0] * size[1]
    w = size[1]
    h = size[0]
    pixarray = np.zeros([imsize, 2])  # 用于储存所有像素，以及坐标
    labelout = np.zeros(size) - 1
    # distance = np.zeros(size)
    putquemask = np.zeros(size)
    labelsize = np.zeros(imsize)
    cnt = np.zeros(257)  # 累积直方图
    currenLabel = 0  # 湖区标号
    que = Queue(maxsize=0)  # 创建队列
    neighborbias4 = np.array([[0, -1], [-1, 0], [0, 1], [1, 0]])  # 邻域偏移
    # neighborbias8 = np.array([[0,-1],[-1,-1],[-1,0],[-1,1],[0,1],[1,1],[1,0],[1,-1]])#邻域偏移

    # 计算直方图，知道每个灰度级的位置
    hist = cv2.calcHist([inputimg], [0], None, [256], [0, 256])
    # 累计直方图的点就是每个灰度级在pixarray中的起始位置，但是要去除空的点
    hist[0] = hist[0] - 1  # 由于累积直方图是作为下标使用，因此最终求和结果不可等于imsize
    histsum = 0
    for i in range(0, 256):
        histsum = histsum + hist[i]
        cnt[i + 1] = histsum

    cnt = cnt.astype(np.int32)
    cntidx = cnt[1:257].copy()

    # 遍历图片记录全部像素，根据累积直方图排列像素顺序，到时候按顺序从低到高一个个涨水
    for y in range(0, h):
        for x in range(0, w):
            pix = inputimg[y, x]
            pixarray[(cntidx[pix]), :] = y, x

            cntidx[pix] = cntidx[pix] - 1

    # 准备完成，开始涨水
    for nowgraylevel in range(0, maxhigh + 1):
        print(nowgraylevel)

        # 标记当前层灰度
        for idx in range(cnt[nowgraylevel], cnt[nowgraylevel + 1] + 1):

            nowpixaxis = pixarray[idx].astype(np.int32)

            labelout[nowpixaxis[0], nowpixaxis[1]] = mask
            # 把在水池边缘的当前灰度级入队
            for nei in range(0, 4):
                neighboraxis = nowpixaxis + neighborbias4[nei]
                if checkedge(neighboraxis, w, h) < 0:
                    continue

                if labelout[neighboraxis[0], neighboraxis[1]] >= 0:  # 周围有已经计算过的

                    putquemask[neighboraxis[0], neighboraxis[1]] > 0  # 标记已经入队过了
                    que.put(nowpixaxis)  # 入队
                    break

        # 开始遍历队列
        while (True):
            if que.empty():
                break

            nowpixaxis = que.get()

            # 蔓延过程
            # 1 周围有1个label，加入其中
            # 2 周围两个不同label，分水岭
            # 3 周围无label，新水池
            # 4 周围有同层，入队蔓延

            for nei in range(0, 4):
                neighboraxis = nowpixaxis + neighborbias4[nei]
                if checkedge(neighboraxis, w, h) < 0:
                    continue
                labelnow = labelout[nowpixaxis[0], nowpixaxis[1]]
                labelneighbor = int(labelout[neighboraxis[0], neighboraxis[1]])

                if labelnow == -2 and labelneighbor > 0:
                    labelout[nowpixaxis[0], nowpixaxis[1]] = labelneighbor
                    labelsize[labelneighbor] = labelsize[labelneighbor] + 1

                elif labelnow > 0 and labelneighbor > 0 and labelnow != labelneighbor:
                    labelout[nowpixaxis[0], nowpixaxis[1]] = 0

                if labelneighbor == -2 and putquemask[neighboraxis[0], neighboraxis[1]] == 0:
                    que.put(neighboraxis)
                    putquemask[neighboraxis[0], neighboraxis[1]] = 1  # 标记这个像素已经入队了不要重复使用

        # 找到了新的水坑（邻域没有水）
        for idx in range(cnt[nowgraylevel], cnt[nowgraylevel + 1] + 1):
            nowpixaxis = pixarray[idx, :].astype(np.int32)
            if (labelout[nowpixaxis[0], nowpixaxis[1]] == -2):  # 经过之前的赋值，仍然没有被标记的是新水池
                # print("new pool %d",)
                currenLabel = currenLabel + 1
                # 配置序号
                labelout[nowpixaxis[0], nowpixaxis[1]] = currenLabel

                que.put(nowpixaxis)

                # 将新坑底所有同灰度级像素都填上水
                while not que.empty():
                    nowpixaxis = que.get()

                    for nei in range(0, 4):
                        neighboraxis = nowpixaxis + neighborbias4[nei]
                        # 防越界
                        if checkedge(neighboraxis, w, h) < 0:
                            continue
                        if putquemask[neighboraxis[0], neighboraxis[1]] == 0 and labelout[
                            neighboraxis[0], neighboraxis[1]] == -2:
                            labelout[neighboraxis[0], neighboraxis[1]] = currenLabel
                            que.put(neighboraxis)
                            putquemask[neighboraxis[0], neighboraxis[1]] = 1
                            labelsize[currenLabel] = labelsize[currenLabel] + 1

    return labelout


image = cv2.imread(
    'imgs/coin.png')  # F:/tf_learn--------/impixiv/1606.jpg #F:/tf_learn--------/impo
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY, cv2.CV_16S)
print("aaa gray:", gray)

# all_polygons = getPolygonFromPath("./testSVG/test_polygon2.svg")
# polygon_np = all_polygons[0]
# x_coords = [point[0] for point in all_polygons[0]]
# y_coords = [point[1] for point in all_polygons[0]]
#
# # Create a binary image with the polygon filled
# gray = np.zeros((1600, 1000), dtype=np.uint8)
# rr, cc = polygon(x_coords, y_coords, gray.shape)
# gray[rr, cc] = 255
# # print("bbb gray:", gray)

size = gray.shape  # h w c

# 二值化
ret, gray = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY)
# ret, gray = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY)
cv2.imshow("ret", gray)
cv2.waitKey(0)
# 膨胀
kernel = np.ones((5, 5), np.uint8)
gray = cv2.dilate(gray, kernel)

# 腐蚀
gray = cv2.erode(gray, kernel)

# 边缘检测
# edgeimage = np.uint8(np.abs(cv2.Sobel(gray,cv2.CV_16S, 1, 1, ksize=3)))#这个sobel不太方便
edgeimage = cv2.Canny(gray, 10, 100)

cv2.imshow("gray", edgeimage)
cv2.waitKey(0)

label = water(edgeimage, size)
label = cv2.resize(label, (size[1], size[0]))

# 标记
b = image[:, :, 0]
g = image[:, :, 1]
r = image[:, :, 2]
r[label == 0] = 255
g[label == 2] = 255
b[label == 3] = 255
b[label == 4] = 125
g[label == 4] = 125

largeimage = cv2.resize(image, (size[1], size[0]), cv2.INTER_LINEAR)
cv2.imshow("lab", largeimage)
cv2.waitKey(0)



