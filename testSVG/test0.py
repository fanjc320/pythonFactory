from svg.path import parse_path
from svg.path.path import Line, CubicBezier, QuadraticBezier, Arc


def path_to_polygon(path_string, npoints=100):
    path = parse_path(path_string)
    points = []
    # We'll sample the path at npoints equally spaced in terms of parameter t (from 0 to 1)
    for i in range(npoints):
        t = i / (npoints - 1.0)
        pos = path.point(t)
        points.append((pos.real, pos.imag))
    return points


try:
    from svg.path import parse_path
    from svg.path.path import Move, Line, Arc, CubicBezier, QuadraticBezier
except ImportError:
    raise ImportError("Required library 'svg.path' is missing. Install with 'pip install svg.path'")


def svg_path_to_polygons(path_string, samples_per_curve=10):
    """
    Converts an SVG path string to multiple polygons (list of vertices).
    Handles multiple subpaths separated by 'M' (move) commands.

    Args:
        path_string (str): SVG path 'd' attribute
        samples_per_curve (int): Points to sample on curved segments

    Returns:
        list: List of polygons, each being [(x1, y1), (x2, y2), ...]
    """
    path = parse_path(path_string)
    polygons = []  # Stores all polygons
    current_poly = []  # Current polygon being built

    for segment in path:
        if isinstance(segment, Move):
            # Finalize previous polygon if it has points
            if current_poly:
                polygons.append(current_poly)
                current_poly = []
            # Start new polygon at move destination
            current_poly.append((segment.end.real, segment.end.imag))
        else:
            # Add segment start if it's the first segment
            if not current_poly:
                current_poly.append((segment.start.real, segment.start.imag))

            # Handle different segment types
            if isinstance(segment, Line):
                current_poly.append((segment.end.real, segment.end.imag))
            elif isinstance(segment, (Arc, CubicBezier, QuadraticBezier)):
                for j in range(1, samples_per_curve + 1):
                    t = j / samples_per_curve
                    point = segment.point(t)
                    current_poly.append((point.real, point.imag))

    # Add last polygon if it exists
    if current_poly:
        polygons.append(current_poly)

    return polygons


def extract_svg_paths(svg_filename):
    """
    Extracts all path data ('d' attributes) from an SVG file

    Args:
        svg_filename (str): Path to SVG file

    Returns:
        list: SVG path strings found in the file
    """
    import xml.etree.ElementTree as ET

    # Parse XML and register SVG namespace
    tree = ET.parse(svg_filename)
    root = tree.getroot()
    # # ns = {'svg': 'http://www.w3.org/2000/svg'}
    # ns = {'svg': ''}
    # # Find all path elements
    # paths = []
    # # for elem in root.findall('.//svg:path', ns):
    # for elem in root.findall('.//svg:path'):
    #     print("elem:", elem)
    #     if 'd' in elem.attrib:
    #         paths.append(elem.attrib['d'])
    # return paths

    paths = []
    if root.tag.startswith('{http://www.w3.org/2000/svg}'):
        # SVG uses XML namespace
        namespace = {'svg': 'http://www.w3.org/2000/svg'}
        paths = root.findall('.//svg:path', namespace)
    else:
        # No namespace
        paths = root.findall('.//path')

    # Extract the 'd' attribute from each path
    path_data = [path.get('d') for path in paths if path.get('d') is not None]

    return path_data


# Usage Example
if __name__ == "__main__":
    # 1. Extract paths from SVG file
    # svg_filename = "input.svg"
    svg_filename = "test_polygon1.svg"
    path_strings = extract_svg_paths(svg_filename)
    print("path_strings len:", len(path_strings))
    # 2. Convert each path to polygons
    all_polygons = []
    for path_str in path_strings:
        polygons = svg_path_to_polygons(path_str, samples_per_curve=20)
        all_polygons.extend(polygons)

    # 3. Output results
    print(f"Found {len(all_polygons)} polygons in {svg_filename}")
    for i, polygon in enumerate(all_polygons):
        print(f"\nPolygon {i + 1} with {len(polygon)} vertices:")
        for vertex in polygon:
            print(f"  ({vertex[0]:.2f}, {vertex[1]:.2f})")