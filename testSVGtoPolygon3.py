import numpy as np
from sklearn.metrics.pairwise import euclidean_distances
from matplotlib.colors import hex2color
from testSVGtoPolygon2 import extract_polygons_with_colors
import matplotlib.pyplot as plt
def find_closest_color(target_hex, palette_hex):
    """
    Find the closest color in palette to target color using Euclidean distance in RGB space

    Args:
        target_hex: Original color in hex format (e.g., '#FF0000')
        palette_hex: List of palette colors in hex format

    Returns:
        Closest color from palette in hex format
    """
    # Convert hex colors to RGB [0-1] range
    target_rgb = np.array(hex2color(target_hex)).reshape(1, -1)
    palette_rgb = np.array([hex2color(c) for c in palette_hex])

    # Calculate distances between target and all palette colors
    distances = euclidean_distances(target_rgb, palette_rgb)

    # Return closest color
    return palette_hex[np.argmin(distances)]


def visualize_with_similar_colors(svg_file, custom_palette):
    """
    Process SVG and visualize with original colors replaced by similar palette colors
    """
    # Extract polygons with original colors
    colored_polygons = extract_polygons_with_colors(svg_file)

    # Find closest palette color for each original color
    processed_polygons = []
    color_mapping = {}  # Cache color mappings

    for polygon, orig_color in colored_polygons:
        if orig_color not in color_mapping:
            color_mapping[orig_color] = find_closest_color(orig_color, custom_palette)
        processed_polygons.append((polygon, color_mapping[orig_color]))

    # Visualize with the new colors
    plt.figure(figsize=(12, 10))
    plt.title("SVG with Similar Colors from Custom Palette")

    # Create legend entries
    legend_elements = []
    for orig, new in color_mapping.items():
        legend_elements.append(plt.Rectangle((0, 0), 1, 1, fc=new,
                                             label=f"{orig} → {new}"))

    # Plot all polygons
    for polygon, color in processed_polygons:
        x, y = zip(*polygon)
        plt.fill(x + (x[0],), y + (y[0],), color, edgecolor='black', linewidth=0.5)

    plt.axis('equal')
    plt.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.gca().invert_yaxis()
    plt.show()


# Custom color palette
custom_palette = [
    '#FF0000', '#FF7F00', '#FFFF00', '#7FFF00', '#00FF00',
    '#00FF7F', '#00FFFF', '#007FFF', '#0000FF', '#7F00FF',
    '#FF00FF', '#FF007F', '#FF5733', '#33FF57', '#3357FF',
    '#F033FF', '#FF33F0', '#33FFF0', '#FFD700', '#9400D3'
]

# Example usage
visualize_with_similar_colors("testSVG/jimeng-little-girl.svg", custom_palette)