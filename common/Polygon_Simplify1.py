import cv2
import numpy as np

import matplotlib.pyplot as plt
import numpy as np
import math


def rdp_simplify(points, epsilon, max_points=100):
    """
    Ramer-Douglas-Peucker algorithm implementation
    """

    def perpendicular_distance(point, start, end):
        if start == end:
            return math.dist(point, start)
        return abs(
            (end[0] - start[0]) * (start[1] - point[1]) -
            (start[0] - point[0]) * (end[1] - start[1])
        ) / math.dist(start, end)

    def rdp_recursive(points, epsilon, simplified):
        if len(points) < 3:
            return points

        max_dist = 0
        index = 0
        start, end = points[0], points[-1]

        for i in range(1, len(points) - 1):
            dist = perpendicular_distance(points[i], start, end)
            if dist > max_dist:
                index = i
                max_dist = dist

        if max_dist > epsilon:
            left = rdp_recursive(points[:index + 1], epsilon, simplified)
            right = rdp_recursive(points[index:], epsilon, simplified)
            simplified = left[:-1] + right
        else:
            simplified = [start, end]

        return simplified

    # Adaptive epsilon to reach target point count
    while True:
        simplified = rdp_recursive(points, epsilon, [])
        if len(simplified) <= max_points or epsilon > 10:  # Safety check
            break
        epsilon *= 1.5

    return simplified, len(simplified), epsilon
def opencv_simplify(coords, max_points=100, initial_epsilon=0.01):
    """
    Simplify using OpenCV's approxPolyDP
    """
    points = np.array(coords, dtype=np.float32)
    epsilon = initial_epsilon

    while True:
        # Convert to OpenCV format
        contour = points.reshape((-1, 1, 2))

        # Approximate polygon
        approx = cv2.approxPolyDP(contour, epsilon, closed=True)
        simplified = approx.reshape((-1, 2))

        if len(simplified) <= max_points or epsilon > 10:  # Safety check
            break
        epsilon *= 1.5

    return simplified.tolist(), len(simplified), epsilon

if __name__ == "__main__":
    # Create test polygon
    t = np.linspace(0, 2*np.pi, 500)
    x = np.cos(t) * (1 + 0.3*np.sin(7*t))
    y = np.sin(t) * (1 + 0.3*np.cos(5*t))
    complex_coords = list(zip(x, y))
    print("complex_coords:", complex_coords)
    # Simplify using chosen method
    # simplified, count, tol = rdp_simplify(complex_coords, 0.01, max_points=50)
    simplified, count, tol = rdp_simplify(complex_coords, 0.01, max_points=150)

    # Visualize
    plt.figure(figsize=(12,6))
    plt.subplot(121)
    plt.plot(*zip(*complex_coords), 'b-')
    plt.title(f"Original ({len(complex_coords)} points)")

    plt.subplot(122)
    plt.plot(*zip(*simplified), 'r-')
    plt.title(f"Simplified ({count} points, tol={tol:.3f})")
    plt.show()