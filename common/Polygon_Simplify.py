from shapely.geometry import Polygon
from shapely import simplify  # Note the changed import location


def simplify_polygon(coords, max_points=100, initial_tolerance=0.01, max_iterations=20, visualize=False):
    """
    Simplify a polygon to have fewer than max_points while preserving shape.

    Args:
        coords (list): List of (x,y) coordinate tuples defining the polygon
        max_points (int): Maximum number of points allowed in simplified polygon (default: 100)
        initial_tolerance (float): Starting simplification tolerance (default: 0.01)
        max_iterations (int): Maximum attempts to find good simplification (default: 20)
        visualize (bool): Whether to show before/after plots (default: False)

    Returns:
        list: Simplified polygon coordinates
        int: Final point count
        float: Final tolerance used
    """
    # Create original polygon
    original_poly = Polygon(coords)

    # Simplify with adaptive tolerance
    tolerance = initial_tolerance
    simplified_poly = original_poly
    iteration = 0

    while len(simplified_poly.exterior.coords) > max_points and iteration < max_iterations:
        simplified_poly = simplify(original_poly, tolerance=tolerance, preserve_topology=True)
        tolerance *= 1.5  # Increase tolerance if needed
        iteration += 1

    # Handle case where we still have too many points
    if len(simplified_poly.exterior.coords) > max_points:
        print(f"Warning: Could not reduce below {len(simplified_poly.exterior.coords)} points")

    simplified_coords = list(simplified_poly.exterior.coords)

    # Visualization if requested
    if visualize:
        import matplotlib.pyplot as plt

        plt.figure(figsize=(12, 6))
        plt.subplot(121)
        x, y = zip(*coords)
        plt.plot(x, y, 'b-')
        plt.title(f"Original ({len(coords)} points)")

        plt.subplot(122)
        xs, ys = zip(*simplified_coords)
        plt.plot(xs, ys, 'r-')
        plt.title(f"Simplified ({len(simplified_coords)} points), tol={tolerance:.4f}")

        plt.tight_layout()
        plt.show()

    return simplified_coords, len(simplified_coords), tolerance


# Example usage:
if __name__ == "__main__":
    # Sample complex polygon (replace with your data)
    import numpy as np

    t = np.linspace(0, 2 * np.pi, 500)
    x = np.cos(t) * (1 + 0.3 * np.sin(7 * t))
    y = np.sin(t) * (1 + 0.3 * np.cos(5 * t))
    complex_coords = list(zip(x, y))

    # Simplify
    simplified, point_count, final_tol = simplify_polygon(
        complex_coords,
        max_points=50,  # Target <50 points
        visualize=True
    )

    print(f"Simplified from {len(complex_coords)} to {point_count} points")
    print(f"Final tolerance: {final_tol}")