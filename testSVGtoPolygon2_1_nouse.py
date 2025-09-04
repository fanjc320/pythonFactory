from svg.path import parse_path
from xml.dom import minidom
from svgpathtools import svg2paths
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import re

def svg_to_polygons(svg_file_path, n_segments_base=20, curvature_threshold=0.1, max_segments=100):
    """
    将SVG路径转换为多边形，根据曲率自适应调整分段数

    参数:
        svg_file_path: SVG文件路径
        n_segments_base: 基础分段数
        curvature_threshold: 曲率阈值，高于此值增加分段数
        max_segments: 最大分段数限制

    返回:
        polygons: 多边形列表，每个多边形是点坐标数组
    """
    # 解析SVG文件
    doc = minidom.parse(svg_file_path)
    path_strings = [path.getAttribute('d') for path in doc.getElementsByTagName('path')]
    doc.unlink()

    polygons = []

    for path_string in path_strings:
        try:
            path = parse_path(path_string)
            points = []

            for segment in path:
                # 根据段类型和曲率确定分段数
                n_segments = calculate_adaptive_segments(
                    segment, n_segments_base, curvature_threshold, max_segments
                )

                # 采样点
                if hasattr(segment, 'point'):
                    # 直线段
                    if n_segments == 1:
                        points.append(segment.start)
                        points.append(segment.end)
                    else:
                        for i in range(n_segments + 1):
                            t = i / n_segments
                            point = segment.point(t)
                            points.append((point.real, point.imag))
                else:
                    # 曲线段，使用更密集的采样
                    for i in range(n_segments + 1):
                        t = i / n_segments
                        point = segment.point(t)
                        points.append((point.real, point.imag))

            if points:
                polygons.append(np.array(points))

        except Exception as e:
            print(f"Error parsing path: {e}")
            continue

    return polygons


def calculate_adaptive_segments(segment, base_segments, curvature_threshold, max_segments):
    """
    根据段的曲率计算自适应分段数
    """
    # 直线段只需要2个点
    if segment.__class__.__name__ == 'Line':
        return 1

    # 计算段的近似曲率
    curvature = estimate_curvature(segment)

    # 根据曲率调整分段数
    if curvature > curvature_threshold:
        # 高曲率区域，增加分段数
        additional_segments = int((curvature / curvature_threshold) * base_segments)
        n_segments = min(base_segments + additional_segments, max_segments)
    else:
        # 低曲率区域，使用基础分段数
        n_segments = base_segments

    return max(2, n_segments)  # 至少2个分段


def estimate_curvature(segment):
    """
    估计曲线段的曲率
    """
    try:
        # 采样几个点来估计曲率
        t_values = np.linspace(0, 1, 5)
        points = []

        for t in t_values:
            point = segment.point(t)
            points.append((point.real, point.imag))

        points = np.array(points)

        # 计算弦长和最大偏移量来估计曲率
        chord_vector = points[-1] - points[0]
        chord_length = np.linalg.norm(chord_vector)

        if chord_length < 1e-10:
            return 0.0

        # 计算点到弦的最大距离
        max_distance = 0
        for i in range(1, len(points) - 1):
            point = points[i]
            # 计算点到直线的距离
            distance = np.abs(np.cross(chord_vector, point - points[0])) / chord_length
            max_distance = max(max_distance, distance)

        # 曲率近似为最大偏移量与弦长的比值
        return max_distance / chord_length if chord_length > 0 else 0.0

    except:
        return 0.5  # 如果计算失败，默认中等曲率


def estimate_bezier_curvature(segment):
    """
    专门针对贝塞尔曲线的曲率估计（更精确）
    """
    if segment.__class__.__name__ in ['CubicBezier', 'QuadraticBezier']:
        try:
            # 对于贝塞尔曲线，可以使用控制点来估计最大曲率
            if hasattr(segment, 'control1') and hasattr(segment, 'control2'):
                # 三次贝塞尔曲线
                p0 = np.array([segment.start.real, segment.start.imag])
                p1 = np.array([segment.control1.real, segment.control1.imag])
                p2 = np.array([segment.control2.real, segment.control2.imag])
                p3 = np.array([segment.end.real, segment.end.imag])

                # 计算控制多边形的弯曲程度
                vec1 = p1 - p0
                vec2 = p2 - p1
                vec3 = p3 - p2

                # 计算角度变化
                angle1 = np.arctan2(vec1[1], vec1[0])
                angle2 = np.arctan2(vec2[1], vec2[0])
                angle3 = np.arctan2(vec3[1], vec3[0])

                angle_diff = np.abs(angle2 - angle1) + np.abs(angle3 - angle2)
                return min(angle_diff / np.pi, 1.0)

        except:
            pass

    return estimate_curvature(segment)  # 回退到通用方法


# 增强版的曲率估计函数
def enhanced_curvature_estimation(segment):
    """
    增强版的曲率估计，结合多种方法
    """
    if segment.__class__.__name__ in ['CubicBezier', 'QuadraticBezier']:
        return estimate_bezier_curvature(segment)
    else:
        return estimate_curvature(segment)

def extract_polygons_with_colors(svg_file, tolerance=0.1):
    """
    Extract polygons with their colors from SVG
    """
    paths, attributes = svg2paths(svg_file)
    colored_polygons = []

    for path, attr in zip(paths, attributes):
        # Get fill color with fallback to stroke then default
        fill_color = attr.get('fill', attr.get('stroke', '#000000'))
        hex_color = parse_svg_color(fill_color)

        # Convert path to polygon
        polyline = []
        for segment in path:
            if segment.length() == 0:
                continue
            n_segments = max(2, int(segment.length() / tolerance))
            path_len = len(path)
            print("extract_polygons_with_colors segment.length():", segment.length(), " n_segments:", n_segments," path_len:",path_len)
            if path_len < 10:
                n_segments = 100 # 视觉上没啥进步
            for t in np.linspace(0, 1, n_segments):
                point = segment.point(t)
                polyline.append((point.real, point.imag))

        if polyline and hex_color:
            colored_polygons.append((polyline, hex_color))

    return colored_polygons


def visualize_colored_polygons(colored_polygons, palette=None, title="SVG Polygons"):
    """Visualize polygons with colors"""
    plt.figure(figsize=(10, 10))
    plt.title(title)
    ax = plt.gca()

    color_palette = [
        '#FF0000', '#FF7F00', '#FFFF00', '#7FFF00', '#00FF00',
        '#00FF7F', '#00FFFF', '#007FFF', '#0000FF', '#7F00FF',
        '#FF00FF', '#FF007F', '#FF5733', '#33FF57', '#3357FF',
        '#F033FF', '#FF33F0', '#33FFF0', '#FFD700', '#9400D3'
    ] if palette is None else palette

    color_usage = defaultdict(int)

    for i, (polygon, orig_color) in enumerate(colored_polygons):
        fill_color = color_palette[i % len(color_palette)] if palette else orig_color
        color_usage[fill_color] += 1
        label = f"Polygon {i + 1} ({fill_color})"

        x, y = zip(*polygon)
        plt.fill(x + (x[0],), y + (y[0],),
                 fill_color,
                 edgecolor='black',
                 linewidth=0.5,
                 label=label)

    plt.axis('equal')
    if len(color_usage) <= 20:
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.gca().invert_yaxis()
    plt.show()


def parse_svg_color(color_str):
    """Simplified color parser without cssutils"""
    if not color_str or color_str.lower() in ['none', 'transparent']:
        return None

    # Hex colors
    if re.match(r'^#(?:[0-9a-f]{3}){1,2}$', color_str, re.IGNORECASE):
        return color_str.upper()

    # rgb() colors
    rgb_match = re.match(r'rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', color_str)
    if rgb_match:
        r, g, b = map(int, rgb_match.groups())
        return "#%02X%02X%02X" % (r, g, b)

    # Named colors (basic set)
    named_colors = {
        'black': '#000000', 'white': '#FFFFFF', 'red': '#FF0000',
        'green': '#00FF00', 'blue': '#0000FF', 'yellow': '#FFFF00',
        'cyan': '#00FFFF', 'magenta': '#FF00FF', 'silver': '#C0C0C0',
        'gray': '#808080', 'maroon': '#800000', 'olive': '#808000',
        'purple': '#800080', 'teal': '#008080', 'navy': '#000080'
    }
    return named_colors.get(color_str.lower(), '#000000')

# def testCurvature():# 根据曲率大小增加采样点
#     # 创建一个测试SVG文件（包含高曲率路径）
#     test_svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
#            <path d="M10,10 C50,100 150,100 190,10" stroke="black" fill="none"/>
#            <path d="M10,50 L190,50" stroke="blue" fill="none"/>
#            <path d="M10,100 Q100,150 190,100" stroke="red" fill="none"/>
#        </svg>'''
#
#     with open('test_curvature.svg', 'w') as f:
#         f.write(test_svg_content)
#
#     # 转换SVG为多边形
#     polygons = svg_to_polygons('test_curvature.svg', n_segments_base=10, curvature_threshold=0.05)
#
#     # 可视化结果
#     plt.figure(figsize=(12, 8))
#     colors = ['red', 'blue', 'green', 'orange', 'purple']
#
#     for i, polygon in enumerate(polygons):
#         if len(polygon) > 0:
#             color = colors[i % len(colors)]
#             plt.plot(polygon[:, 0], polygon[:, 1], '-o', color=color, markersize=3,
#                      label=f'Path {i + 1} ({len(polygon)} points)')
#             plt.scatter(polygon[0, 0], polygon[0, 1], color=color, s=50, zorder=5)
#             plt.scatter(polygon[-1, 0], polygon[-1, 1], color=color, s=50, zorder=5)
#
#     plt.axis('equal')
#     plt.legend()
#     plt.grid(True, alpha=0.3)
#     plt.title('SVG Paths with Adaptive Sampling (High Curvature = More Points)')
#     plt.show()
#
#     # 显示每个路径的点数统计
#     for i, polygon in enumerate(polygons):
#         print(f"Path {i + 1}: {len(polygon)} points")
# 使用示例
if __name__ == "__main__":
    svg_file = "testSVG/jimeng-little-girl.svg"
    colored_polygons = extract_polygons_with_colors(svg_file, 20)
    print("colored_polygons type:", type(colored_polygons), " len:",
          len(colored_polygons))  # type: <class 'list'>  len: 51
    # print("colored_polygons:", colored_polygons[0][0])
    # extract_polygons_with_colors tolerence->len 1->5197,10->515,20->256, 200->28 变形了
    print("colored_polygons  00 len:", len(colored_polygons[0][0]))

    visualize_colored_polygons(colored_polygons)  # Original colors

    pass

