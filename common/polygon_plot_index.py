import matplotlib.pyplot as plt
import numpy as np


def draw_polygon_with_labels(vertices, color='blue', alpha=0.5, label_offset=0.1):
    """
    绘制多边形并标注顶点索引

    参数:
    - vertices: 顶点坐标列表，格式为 [(x1,y1), (x2,y2), ...]
    - color: 多边形填充颜色
    - alpha: 多边形透明度
    - label_offset: 顶点标签偏移量
    """
    # 创建图形
    fig, ax = plt.subplots()

    # 将顶点列表转换为NumPy数组以便处理
    vertices = np.array(vertices)

    # 绘制多边形
    polygon = plt.Polygon(vertices, color=color, alpha=alpha)
    ax.add_patch(polygon)

    # 绘制顶点并标注索引
    for i, (x, y) in enumerate(vertices):
        # 绘制顶点
        ax.plot(x, y, 'ro')

        # 计算标签位置（稍微偏移以避免重叠）
        offset_x = label_offset if x >= 0 else -label_offset
        offset_y = label_offset if y >= 0 else -label_offset

        # 标注索引
        ax.text(x + offset_x, y + offset_y, str(i),
                fontsize=12, color='black', weight='bold')

    # 设置坐标轴范围
    min_x, min_y = np.min(vertices, axis=0)
    max_x, max_y = np.max(vertices, axis=0)
    ax.set_xlim(min_x - 1, max_x + 1)
    ax.set_ylim(min_y - 1, max_y + 1)

    # 设置图形标题
    ax.set_title('Polygon with Vertex Indices')

    # 显示图形
    plt.grid(True)
    plt.axis('equal')  # 保持纵横比一致
    plt.show()


# 示例使用
if __name__ == "__main__":
    # 定义多边形的顶点坐标
    # polygon_vertices = [
    #     (1, 1),
    #     (3, 1),
    #     (4, 3),
    #     (3, 5),
    #     (1, 5),
    #     (0, 3)
    # ]
    polygon_vertices = [(0, 0), (0.5, 0.2), (1.5, 0.5), (2.5, 0.2), (3, 0), (3, 1), (2, 1), (2, 2), (1, 2), (1, 1), (0, 1)]
    # 调用函数绘制多边形
    draw_polygon_with_labels(polygon_vertices, color='skyblue', alpha=0.7)