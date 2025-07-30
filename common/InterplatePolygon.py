import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

def interpolate_polygon_uniformly(vertices, num_points=None, spacing=None):
    """Same implementation as before"""
    if not np.allclose(vertices[0], vertices[-1]):
        vertices = np.vstack([vertices, vertices[0]])

    diffs = np.diff(vertices, axis=0)
    segment_lengths = np.sqrt(np.sum(diffs ** 2, axis=1))
    cumulative_lengths = np.insert(np.cumsum(segment_lengths), 0, 0)
    total_length = cumulative_lengths[-1]

    if spacing is not None:
        num_points = int(np.ceil(total_length / spacing))
    elif num_points is None:
        num_points = len(vertices)

    target_distances = np.linspace(0, total_length, num_points, endpoint=False)

    t = cumulative_lengths
    x = vertices[:, 0]
    y = vertices[:, 1]

    fx = interp1d(t, x, kind='linear')
    fy = interp1d(t, y, kind='linear')

    new_x = fx(target_distances)
    new_y = fy(target_distances)

    return np.column_stack((new_x, new_y))
def interpolate_polygon_uniformly_noscipy(vertices, num_points=None, spacing=None):
    """Pure NumPy implementation"""
    # Close the polygon if not already closed
    if not np.allclose(vertices[0], vertices[-1]):
        vertices = np.vstack([vertices, vertices[0]])

    # Calculate cumulative distances
    diffs = np.diff(vertices, axis=0)
    segment_lengths = np.sqrt(np.sum(diffs ** 2, axis=1))
    cumulative_lengths = np.insert(np.cumsum(segment_lengths), 0, 0)
    total_length = cumulative_lengths[-1]

    # Determine target distances
    if spacing is not None:
        num_points = int(np.ceil(total_length / spacing))
    elif num_points is None:
        num_points = len(vertices)

    target_distances = np.linspace(0, total_length, num_points, endpoint=False)

    # Find which segment each target falls into
    segment_indices = np.searchsorted(cumulative_lengths, target_distances, side='right') - 1
    segment_indices = np.clip(segment_indices, 0, len(segment_lengths) - 1)

    # Calculate interpolation ratios for each segment
    segment_start_lengths = cumulative_lengths[segment_indices]
    segment_ratios = (target_distances - segment_start_lengths) / segment_lengths[segment_indices]

    # Interpolate points
    start_points = vertices[segment_indices]
    end_points = vertices[segment_indices + 1]
    new_points = start_points + segment_ratios[:, np.newaxis] * (end_points - start_points)

    return new_points


def plot_polygon_comparison(original_vertices, uniform_vertices):
    """Visualize both polygons for comparison"""
    plt.figure(figsize=(10, 5))

    # Plot original polygon
    plt.subplot(1, 2, 1)
    plt.plot(original_vertices[:, 0], original_vertices[:, 1], 'bo-', label='Original')
    plt.scatter(original_vertices[:, 0], original_vertices[:, 1], c='red', s=50)
    plt.title(f'Original Polygon ({len(original_vertices)} vertices)')
    plt.axis('equal')
    plt.grid(True)
    plt.legend()

    # Plot uniform polygon
    plt.subplot(1, 2, 2)
    closed_uniform = np.vstack([uniform_vertices, uniform_vertices[0]])
    plt.plot(closed_uniform[:, 0], closed_uniform[:, 1], 'go-', label='Uniform')
    plt.scatter(uniform_vertices[:, 0], uniform_vertices[:, 1], c='red', s=50)
    plt.title(f'Uniform Polygon ({len(uniform_vertices)} vertices)')
    plt.axis('equal')
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.show()

# Example usage
if __name__ == "__main__":
    # Create a sample polygon (triangle in this case)
    vertices = np.array([[0, 0], [2, 5], [5, 1]])

    # Interpolate to 20 uniformly distributed points
    # uniform_vertices = interpolate_polygon_uniformly(vertices, num_points=20)
    uniform_vertices = interpolate_polygon_uniformly_noscipy(vertices, num_points=20)

    print("Original vertices:", vertices)
    print("Uniform vertices:", uniform_vertices)

    # Visualize the comparison
    plot_polygon_comparison(vertices, uniform_vertices)