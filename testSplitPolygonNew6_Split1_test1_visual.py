import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection
import numpy as np
import random
from testSplitPolygonNew6_Split1_test1 import *

def visualize_decomposition(decomposition, title="Polygon Decomposition"):
    """可视化多边形分解结果"""
    global global_polygon

    fig, ax = plt.subplots(figsize=(10, 8))

    # 绘制原始多边形
    original_poly = np.array(global_polygon)
    original_patch = patches.Polygon(original_poly, alpha=0.2, edgecolor='black',
                                     facecolor='lightgray', linestyle='--', label='Original')
    ax.add_patch(original_patch)

    # 为每个子多边形生成随机颜色
    colors = []
    patches_list = []
    labels = []

    for i, indices in enumerate(decomposition):
        # 从索引获取多边形顶点
        poly_vertices = [global_polygon[idx] for idx in indices]
        poly_array = np.array(poly_vertices)

        # 生成随机颜色（避免太浅的颜色）
        color = (random.random() * 0.7 + 0.3, random.random() * 0.7 + 0.3, random.random() * 0.7 + 0.3)
        colors.append(color)

        # 创建多边形补丁
        patch = patches.Polygon(poly_array, alpha=0.6, edgecolor='black',
                                facecolor=color, linewidth=2)
        patches_list.append(patch)
        labels.append(f'Part {i + 1}')

        # 添加顶点编号
        for j, idx in enumerate(indices):
            x, y = global_polygon[idx]
            ax.text(x, y, f'{idx}', fontsize=8, ha='center', va='center',
                    bbox=dict(boxstyle="circle,pad=0.2", facecolor='white', alpha=0.8))

    # 添加所有多边形补丁
    collection = PatchCollection(patches_list, match_original=True)
    ax.add_collection(collection)

    # 设置坐标轴
    all_points = np.array(global_polygon)
    x_min, y_min = all_points.min(axis=0) - 1
    x_max, y_max = all_points.max(axis=0) + 1

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_aspect('equal')

    # 添加图例
    ax.legend(handles=[original_patch] + patches_list,
              labels=['Original'] + labels, loc='best')

    # 添加标题和网格
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')

    plt.tight_layout()
    plt.show()


def visualize_split_process(original_poly, splits_history, final_decomposition):
    """可视化拆分过程"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # 绘制原始多边形
    original_array = np.array(original_poly)
    axes[0].add_patch(patches.Polygon(original_array, alpha=0.7, edgecolor='blue',
                                      facecolor='lightblue'))
    axes[0].set_title('Original Polygon', fontweight='bold')
    axes[0].set_aspect('equal')
    axes[0].grid(True, alpha=0.3)

    # 绘制拆分过程
    colors = ['red', 'green', 'orange', 'purple', 'brown']
    for i, split in enumerate(splits_history[:min(4, len(splits_history))]):
        color = colors[i % len(colors)]
        axes[1].plot([split[0][0], split[1][0]], [split[0][1], split[1][1]],
                     color=color, linewidth=2, marker='o', label=f'Split {i + 1}')

    original_patch = patches.Polygon(original_array, alpha=0.3, edgecolor='black',
                                     facecolor='lightgray')
    axes[1].add_patch(original_patch)
    axes[1].set_title('Split Lines', fontweight='bold')
    axes[1].set_aspect('equal')
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()

    # 绘制最终分解结果
    for i, indices in enumerate(final_decomposition):
        poly_vertices = [original_poly[idx] for idx in indices]
        color = (random.random() * 0.7 + 0.3, random.random() * 0.7 + 0.3, random.random() * 0.7 + 0.3)
        axes[2].add_patch(patches.Polygon(poly_vertices, alpha=0.6, edgecolor='black',
                                          facecolor=color))

    axes[2].set_title('Final Decomposition', fontweight='bold')
    axes[2].set_aspect('equal')
    axes[2].grid(True, alpha=0.3)

    # 设置统一的坐标范围
    all_points = np.array(original_poly)
    x_min, y_min = all_points.min(axis=0) - 1
    x_max, y_max = all_points.max(axis=0) + 1

    for ax in axes:
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)

    plt.tight_layout()
    plt.show()


def visualize_concave_vertices(polygon, concave_vertices, threshold=2.6):
    """可视化凹顶点"""
    fig, ax = plt.subplots(figsize=(8, 6))

    # 绘制多边形
    poly_array = np.array(polygon)
    ax.add_patch(patches.Polygon(poly_array, alpha=0.3, edgecolor='blue',
                                 facecolor='lightblue', label='Polygon'))

    # 标记所有顶点
    for i, (x, y) in enumerate(polygon):
        ax.plot(x, y, 'bo', markersize=6)
        ax.text(x, y, f'{i}', fontsize=10, ha='right', va='bottom')

    # 标记凹顶点
    for i in concave_vertices:
        x, y = polygon[i]
        ax.plot(x, y, 'ro', markersize=8, markerfacecolor='red',
                label='Concave Vertex' if i == concave_vertices[0] else "")

    # 设置图形属性
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_title(f'Concave Vertices (Threshold: {threshold})', fontweight='bold')
    ax.legend()

    # 设置坐标范围
    x_min, y_min = poly_array.min(axis=0) - 1
    x_max, y_max = poly_array.max(axis=0) + 1
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    plt.tight_layout()
    plt.show()


def visualize_concave_vertices_with_indices(indices, threshold=2.6):
    """可视化凹顶点（使用索引）"""
    global global_polygon
    poly = [global_polygon[i] for i in indices]
    global_concave_verts = find_concave_vertices_with_indices(indices, threshold)

    fig, ax = plt.subplots(figsize=(8, 6))

    # 绘制多边形
    poly_array = np.array(poly)
    ax.add_patch(patches.Polygon(poly_array, alpha=0.3, edgecolor='blue',
                                 facecolor='lightblue', label='Polygon'))

    # 标记所有顶点（显示全局索引）
    for i, vertex_idx in enumerate(indices):
        x, y = global_polygon[vertex_idx]
        ax.plot(x, y, 'bo', markersize=6)
        ax.text(x, y, f'{vertex_idx}', fontsize=10, ha='right', va='bottom')

    # 标记凹顶点（红色）
    for global_idx in global_concave_verts:
        if global_idx in indices:
            x, y = global_polygon[global_idx]
            ax.plot(x, y, 'ro', markersize=8, markerfacecolor='red',
                    label='Concave Vertex' if global_idx == global_concave_verts[0] else "")

    # 设置图形属性
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_title(f'Concave Vertices (Threshold: {threshold})', fontweight='bold')
    ax.legend()

    # 设置坐标范围
    x_min, y_min = poly_array.min(axis=0) - 1
    x_max, y_max = poly_array.max(axis=0) + 1
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    plt.tight_layout()
    plt.show()
# 修改后的主函数，包含可视化
def main_with_visualization():
    global global_polygon

    print("原始多边形顶点:")
    for i, vertex in enumerate(global_polygon):
        print(f"  {i}: {vertex}")

    # 查找凹顶点并可视化
    concave_verts = find_concave_vertices(global_polygon, threshold=2.6)
    print(f"\n凹顶点索引: {concave_verts}")

    visualize_concave_vertices(global_polygon, concave_verts)

    # 初始部分包含所有顶点的索引
    initial_indices = list(range(len(global_polygon)))

    # 执行递归拆分
    print("\n开始递归拆分...")
    decompositions = recursive_split(initial_indices, threshold=2.6)

    # 输出结果并可视化
    print(f"\n找到 {len(decompositions)} 种分解方案")

    for i, decomp in enumerate(decompositions):
        # print(f"\n分解方案 {i + 1}:")
        # total_area = 0
        # for j, indices in enumerate(decomp):
        #     poly = get_polygon_from_indices(indices)
        #     area = polygon_area(poly)
        #     total_area += area
        #     print(f"  子多边形 {j + 1} (面积: {area:.2f}): 顶点索引 {indices}")
        #
        # print(f"  总面积: {total_area:.2f}")

        # 可视化每个分解方案
        visualize_decomposition(decomp, title=f"Decomposition Solution {i + 1}")

    # 选择第一个分解方案进行详细可视化
    if decompositions:
        best_decomposition = decompositions[0]
        print(f"\n最佳分解方案包含 {len(best_decomposition)} 个子多边形")

        # 这里可以添加更详细的分析和可视化
        for j, indices in enumerate(best_decomposition):
            poly = get_polygon_from_indices(indices)
            is_convex = len(find_concave_vertices(poly, 2.6)) == 0
            print(f"  子多边形 {j + 1}: {'凸' if is_convex else '凹'}多边形，{len(indices)}个顶点")


# 运行示例
if __name__ == "__main__":
    main_with_visualization()