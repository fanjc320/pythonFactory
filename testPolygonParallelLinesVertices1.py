import matplotlib.pyplot as plt
import numpy as np
from math import sqrt


def distance(p1, p2):
    """Calculate Euclidean distance between two points"""
    return sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def split_segment(p1, p2, max_length):
    """
    Split segment between p1 and p2 if longer than max_length.
    Returns list of points including new intermediate points.
    """
    seg_length = distance(p1, p2)
    if seg_length <= max_length:
        return [p1, p2]

    num_splits = int(np.ceil(seg_length / max_length))
    new_points = []
    for i in range(1, num_splits):
        t = i / num_splits
        x = p1[0] + t * (p2[0] - p1[0])
        y = p1[1] + t * (p2[1] - p1[1])
        new_points.append((x, y))

    return [p1] + new_points + [p2]


def process_polygon(vertices, max_segment_length):
    """
    Process polygon vertices and truncate long segments.
    Returns:
    - new_vertices: Updated list of vertices with new points
    - new_indices: Indices of newly added points
    """
    new_vertices = []
    new_indices = []
    original_count = len(vertices)

    for i in range(len(vertices)):
        p1 = vertices[i]
        p2 = vertices[(i + 1) % len(vertices)]  # Wrap around to close polygon

        # Add current vertex
        new_vertices.append(p1)

        # Split segment if needed
        split_points = split_segment(p1, p2, max_segment_length)
        if len(split_points) > 2:  # New points were added
            new_points = split_points[1:-1]  # Exclude endpoints
            new_vertices.extend(new_points)
            new_indices.extend(range(len(new_vertices) - len(new_points), len(new_vertices)))

    return new_vertices, new_indices


def visualize(original_vertices, new_vertices, new_indices):
    """Visualize original and modified polygon with new points highlighted"""
    plt.figure(figsize=(10, 5))

    # Plot original polygon
    plt.subplot(1, 2, 1)
    orig_x, orig_y = zip(*original_vertices + [original_vertices[0]])
    plt.plot(orig_x, orig_y, 'b-o', label='Original')
    plt.title('Original Polygon')
    plt.axis('equal')

    # Plot modified polygon
    plt.subplot(1, 2, 2)
    new_x, new_y = zip(*new_vertices + [new_vertices[0]])
    plt.plot(new_x, new_y, 'g-o', label='Modified')

    # Highlight new points
    if new_indices:
        new_points = [new_vertices[i] for i in new_indices]
        new_x, new_y = zip(*new_points)
        plt.scatter(new_x, new_y, c='r', s=100, label='New Points')

    plt.title('With Segment Truncation')
    plt.axis('equal')
    plt.legend()
    plt.tight_layout()
    plt.show()


# Example usage
if __name__ == "__main__":
    # Create a sample polygon (rectangle with one long side)
    # original_vertices = [(0, 0), (3, 0), (3, 1), (0, 1)]
    original_vertices = [(0, 0), (2, 0), (2, 3), (0, 3), (0.5, 1.5)]
    colors = ['b', 'r', 'g', 'm', 'c']
    max_length = 1.0  # Maximum allowed segment length

    new_vertices, new_indices = process_polygon(original_vertices, max_length)

    print("Original vertices:", original_vertices)
    print("New vertices:", new_vertices)
    print("Indices of new points:", new_indices)

    visualize(original_vertices, new_vertices, new_indices)