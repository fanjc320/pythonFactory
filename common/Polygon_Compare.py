import numpy as np
from shapely.geometry import Polygon
import math
from common.polygon_plot import *

def calculate_shape_regularity(polygon):
    """
    计算多边形的形状规则性，返回多个形状评估指标

    Args:
        polygon: Shapely Polygon对象

    Returns:
        dict: 包含多种形状规则性指标的字典
    """
    if not isinstance(polygon, Polygon) or polygon.area <= 0:
        print(f"calculate_shape_regularity error polygon:{polygon} polygon.area:{polygon.area}")
        return {"error": "无效的多边形"}

    # 基础几何属性
    area = polygon.area
    perimeter = polygon.length
    convex_hull = polygon.convex_hull
    convex_hull_area = convex_hull.area
    print(f"calculate_shape_regularity area:{area} perimeter:{perimeter} convex_hull:{convex_hull} convex_hull_area:{convex_hull_area}")
    # 1. 等周商 (Isoperimetric Quotient) - 越接近1越规则
    if perimeter > 0:
        isoperimetric_quotient = (4 * math.pi * area) / (perimeter ** 2)
    else:
        isoperimetric_quotient = 0

    # 2. 凸度比 (Convexity Ratio) - 越接近1越凸
    convexity_ratio = area / convex_hull_area if convex_hull_area > 0 else 0

    # 3. 紧密度 (Compactness) - 基于最小外接圆
    min_circle = polygon.minimum_rotated_rectangle
    min_circle_area = min_circle.area if min_circle else 0
    compactness = area / min_circle_area if min_circle_area > 0 else 0

    # 4. 形状指数 (Shape Index) - 基于周长和面积
    shape_index = perimeter / (2 * math.sqrt(math.pi * area)) if area > 0 else float('inf')

    # 5. 矩形拟合度 (Rectangular Fit)
    bounding_box = polygon.bounds
    bbox_width = bounding_box[2] - bounding_box[0]
    bbox_height = bounding_box[3] - bounding_box[1]
    bbox_area = bbox_width * bbox_height
    rectangular_fit = area / bbox_area if bbox_area > 0 else 0

    # 6. 圆度 (Circularity) - 另一种计算方式
    circularity = (4 * math.pi * area) / (perimeter ** 2) if perimeter > 0 else 0

    # 7. 偏心度 (Eccentricity) - 基于最小外接矩形
    if min_circle and hasattr(min_circle, 'exterior'):
        coords = list(min_circle.exterior.coords)
        if len(coords) >= 4:
            # 计算最小外接矩形的长宽比
            side1 = math.sqrt((coords[1][0] - coords[0][0]) ** 2 + (coords[1][1] - coords[0][1]) ** 2)
            side2 = math.sqrt((coords[2][0] - coords[1][0]) ** 2 + (coords[2][1] - coords[1][1]) ** 2)
            eccentricity = max(side1, side2) / min(side1, side2) if min(side1, side2) > 0 else 1
        else:
            eccentricity = 1
    else:
        eccentricity = 1

    return {
        "isoperimetric_quotient": isoperimetric_quotient,  # 越接近1越好
        "convexity_ratio": convexity_ratio,  # 越接近1越好
        "compactness": compactness,  # 越接近1越好
        "shape_index": shape_index,  # 越接近1越好
        "rectangular_fit": rectangular_fit,  # 越接近1越好
        "circularity": circularity,  # 越接近1越好
        "eccentricity": eccentricity,  # 越接近1越好
        "overall_score": calculate_overall_score({
            "isoperimetric_quotient": isoperimetric_quotient,
            "convexity_ratio": convexity_ratio,
            "compactness": compactness,
            "shape_index": min(1.0, 1.0 / shape_index) if shape_index > 0 else 0,
            "rectangular_fit": rectangular_fit,
            "circularity": circularity,
            "eccentricity": 1.0 / eccentricity if eccentricity > 0 else 0
        })
    }


def calculate_overall_score(metrics, weights=None):
    """
    计算综合形状评分

    Args:
        metrics: 各个指标的值
        weights: 各指标的权重

    Returns:
        float: 综合评分 (0-1)
    """
    if weights is None:
        weights = {
            "isoperimetric_quotient": 0.2,
            "convexity_ratio": 0.2,
            "compactness": 0.15,
            "shape_index": 0.15,
            "rectangular_fit": 0.15,
            "circularity": 0.1,
            "eccentricity": 0.05
        }

    total_weight = sum(weights.values())
    weighted_sum = 0

    for metric, value in metrics.items():
        if metric in weights:
            # 确保值在0-1范围内
            clamped_value = max(0, min(1, value))
            weighted_sum += clamped_value * weights[metric]

    return weighted_sum / total_weight


def compare_shape_regularity(polygons):
    """
    比较多个多边形的形状规则性

    Args:
        polygons: 多边形列表

    Returns:
        list: 按规则性排序的多边形和评分
    """
    results = []

    for i, poly in enumerate(polygons):
        regularity = calculate_shape_regularity(poly)
        results.append({
            "polygon_index": i,
            "polygon": poly,
            "regularity_scores": regularity,
            "overall_score": regularity.get("overall_score", 0)
        })

    # 按综合评分排序
    results.sort(key=lambda x: x["overall_score"], reverse=True)
    return results

def get_aggregate_regularity(polygons):
    """
    比较多个多边形的形状规则性

    Args:
        polygons: 多边形列表

    Returns:
        list: 按规则性排序的多边形和评分
    """
    # results = []
    score_aggregate = 0
    for i, poly in enumerate(polygons):
        regularity = calculate_shape_regularity(poly)
        # results.append({
        #     "polygon_index": i,
        #     "polygon": poly,
        #     "regularity_scores": regularity,
        #     "overall_score": regularity.get("overall_score", 0)
        # })
        score_aggregate += regularity.get("overall_score", 0)

    return score_aggregate / len(polygons)

# 使用示例
if __name__ == "__main__":
    # 创建一些测试多边形
    from shapely.geometry import Polygon

    # 规则形状
    square = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    circle_approx = Polygon([(0, 0), (0.5, 0.866), (1, 0), (0.5, -0.866)])  # 近似等边三角形

    # 不规则形状
    irregular = Polygon([(0, 0), (2, 0), (1.5, 1), (0.5, 1.5), (-0.5, 1)])
    very_irregular = Polygon([(0, 0), (3, 0), (2, 1), (3, 2), (1, 3), (0, 2)])

    test_polygons = [square, circle_approx, irregular, very_irregular]
    print(f"square.exterior:{list(square.exterior.coords)}")
    plot_polygons(list(square.exterior.coords))
    plot_polygons(list(circle_approx.exterior.coords))
    plot_polygons(list(irregular.exterior.coords))
    plot_polygons(list(very_irregular.exterior.coords))
    # 计算并比较形状规则性
    results = compare_shape_regularity(test_polygons)

    print("形状规则性比较结果:")
    print("=" * 80)
    for result in results:
        print(f"多边形 {result['polygon_index']}: 综合评分 = {result['overall_score']:.3f}")
        scores = result['regularity_scores']
        for key, value in scores.items():
            if key != 'overall_score':
                print(f"  {key}: {value:.3f}")
        print("-" * 40)

    # 最佳形状
    best = results[0]
    print(f"\n最规则的多边形: #{best['polygon_index']}, 评分: {best['overall_score']:.3f}")