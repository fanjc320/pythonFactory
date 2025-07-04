import numpy as np
import cv2
from skimage.morphology import skeletonize
from skimage import measure
from scipy import ndimage
from scipy.interpolate import splprep, splev
import matplotlib.pyplot as plt


def polygon_to_binary(polygon, shape):
    """将多边形转换为二值图像"""
    img = np.zeros(shape, dtype=np.uint8)
    cv2.fillPoly(img, [polygon], 1)
    return img


def compute_skeleton(binary_img):
    """计算二值图像的骨架"""
    skeleton = skeletonize(binary_img > 0)
    return skeleton


def find_branch_points(skeleton):
    """找到骨架的分支点"""
    kernel = np.array([[1, 1, 1],
                       [1, 10, 1],
                       [1, 1, 1]], dtype=np.uint8)
    conv = cv2.filter2D(skeleton.astype(np.uint8), -1, kernel)
    branch_points = (conv >= 12) & (skeleton > 0)
    return branch_points


def trace_skeleton_branches(skeleton, branch_points):
    """追踪骨架的所有分支"""
    # 实现分支追踪逻辑
    # 这里简化为从每个分支点向外追踪
    branches = []
    y, x = np.where(branch_points)

    for i in range(len(x)):
        # 简化的分支追踪 - 实际实现需要更复杂的算法
        branch = [(x[i], y[i])]
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x[i] + dx, y[i] + dy
            if 0 <= nx < skeleton.shape[1] and 0 <= ny < skeleton.shape[0]:
                if skeleton[ny, nx] > 0:
                    branch.append((nx, ny))
        branches.append(np.array(branch))

    return branches


def smooth_contour(contour, smoothing_factor=0.1):
    """使用样条曲线平滑轮廓"""
    if len(contour) < 4:
        return contour

    contour = contour.astype(np.float32)
    tck, u = splprep(contour.T, u=None, s=smoothing_factor, per=1)
    u_new = np.linspace(u.min(), u.max(), len(contour))
    x_new, y_new = splev(u_new, tck, der=0)
    smoothed = np.vstack((x_new, y_new)).T.astype(np.int32)

    return smoothed


def generate_split_lines(polygon, branches):
    """基于骨架分支生成分割线"""
    split_lines = []
    shape = (np.max(polygon[:, 1]) + 50, np.max(polygon[:, 0]) + 50)
    binary_img = polygon_to_binary(polygon, shape)

    for branch in branches:
        if len(branch) < 2:
            continue

        # 找到分支的两个端点
        start = branch[0]
        end = branch[-1]

        # 从端点向多边形边界延伸
        # 简化的实现 - 实际需要更复杂的边界延伸算法
        line = np.array([start, end])

        # 延伸线到多边形边界
        extended_line = extend_line_to_boundary(line, polygon, shape)
        if extended_line is not None:
            split_lines.append(extended_line)

    return split_lines


def extend_line_to_boundary(line, polygon, shape):
    """将线延伸到多边形边界"""
    # 简化的实现 - 实际需要计算线与多边形边界的交点
    # 这里返回原始线作为示例
    return line


def split_polygon(polygon, split_lines):
    """使用分割线分割多边形"""
    sub_polygons = [polygon]

    for line in split_lines:
        new_polygons = []
        for poly in sub_polygons:
            # 简化的分割 - 实际需要实现多边形分割算法
            # 这里将多边形分成两部分作为示例
            if len(poly) > 4:
                mid = len(poly) // 2
                new_polygons.append(poly[:mid])
                new_polygons.append(poly[mid:])
            else:
                new_polygons.append(poly)
        sub_polygons = new_polygons

    return sub_polygons


def morphological_polygon_splitting(polygon):
    """主函数：形态学分割多边形"""
    # 1. 将多边形转换为二值图像
    shape = (np.max(polygon[:, 1]) + 50, np.max(polygon[:, 0]) + 50)
    binary_img = polygon_to_binary(polygon, shape)

    # 2. 计算骨架
    skeleton = compute_skeleton(binary_img)

    # 3. 找到分支点
    branch_points = find_branch_points(skeleton)

    # 4. 追踪骨架分支
    branches = trace_skeleton_branches(skeleton, branch_points)

    # 5. 生成分割线
    split_lines = generate_split_lines(polygon, branches)

    # 6. 分割多边形
    sub_polygons = split_polygon(polygon, split_lines)

    # 7. 平滑子多边形
    smoothed_polygons = [smooth_contour(p) for p in sub_polygons]

    return smoothed_polygons, skeleton, split_lines


# 示例使用
if __name__ == "__main__":
    # 创建一个示例多边形
    polygon = np.array([[100, 100], [200, 50], [300, 100],
                        [350, 200], [300, 300], [200, 350],
                        [100, 300], [50, 200]])

    # 执行分割
    sub_polygons, skeleton, split_lines = morphological_polygon_splitting(polygon)

    # 可视化结果
    plt.figure(figsize=(12, 6))

    # 绘制原始多边形和骨架
    plt.subplot(121)
    plt.plot(polygon[:, 0], polygon[:, 1], 'b-', label='Original Polygon')
    plt.plot(np.hstack((polygon[:, 0], polygon[0, 0])),
             np.hstack((polygon[:, 1], polygon[0, 1])), 'b-')
    y, x = np.where(skeleton)
    plt.plot(x, y, 'r.', markersize=1, label='Skeleton')
    for line in split_lines:
        plt.plot(line[:, 0], line[:, 1], 'g-', linewidth=2, label='Split Lines')
    plt.title('Original Polygon with Skeleton and Split Lines')
    plt.axis('equal')
    plt.legend()

    # 绘制分割后的子多边形
    plt.subplot(122)
    colors = ['r', 'g', 'b', 'c', 'm', 'y']
    for i, poly in enumerate(sub_polygons):
        color = colors[i % len(colors)]
    plt.plot(poly[:, 0], poly[:, 1], color + '-', label=f'Sub-polygon {i + 1}')
    plt.plot(np.hstack((poly[:, 0], poly[0, 0])),
    np.hstack((poly[:, 1], poly[0, 1])), color + '-')
    plt.title('Split Sub-polygons')
    plt.axis('equal')
    plt.legend()

    plt.tight_layout()
    plt.show()