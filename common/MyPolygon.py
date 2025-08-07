

class AutoIndexPolygon:
    def __init__(self, vertices, indices=None):
        self.vertices = vertices
        self.indices = indices if indices is not None else list(range(len(vertices)))

    def print_info(self):
        print("Vertices with auto-generated indices:")
        for i, (x, y) in zip(self.indices, self.vertices):
            print(f"Index {i}: Vertex at ({x}, {y})")

        print("\nPolygon edges:")
        for i in range(len(self.indices)):
            start = self.indices[i]
            end = self.indices[(i + 1) % len(self.indices)]
            print(f"Edge {i}: {start}→{end}")

# if __name__ == "__main__":
#     ###################
#     # Usage examples:
#
#     # Example 1: Auto-indexed quad
#     quad = AutoIndexPolygon([(0, 0), (1, 0), (1, 1), (0, 1)])
#     quad.print_info()
#
#     # Example 2: Explicit indices (triangle strip)
#     triangle_strip = AutoIndexPolygon(
#         vertices=[(0, 0), (1, 0), (0, 1), (1, 1)],
#         indices=[0, 1, 2, 3]  # Override auto-indexing
#     )
#     triangle_strip.print_info()
class Vertex:
    def __init__(self, x, y, index=None):
        """
        A single vertex in a polygon with coordinates and optional index.

        Args:
            x (float): X coordinate
            y (float): Y coordinate
            index (int, optional): Vertex index. Auto-assigned if None.
        """
        self.x = x
        self.y = y
        self._index = index

    @property
    def index(self):
        """Get the vertex index"""
        return self._index

    @index.setter
    def index(self, value):
        """Set the vertex index"""
        self._index = value

    @property
    def coords(self):
        """Get coordinates as a tuple"""
        return (self.x, self.y)

    def __repr__(self):
        return f"Vertex(index={self.index}, x={self.x}, y={self.y})"

    def __eq__(self, other):
        if not isinstance(other, Vertex):
            return False
        return self.x == other.x and self.y == other.y and self.index == other.index


class Polygon:
    def __init__(self, vertices=None):
        """
        A polygon composed of Vertex objects.

        Args:
            vertices (list): List of Vertex objects or (x,y) tuples
        """
        self._vertices = []
        self._indices = []

        if vertices:
            self.add_vertices(vertices)

    def add_vertex(self, vertex, index=None):
        """
        Add a vertex to the polygon.

        Args:
            vertex: Vertex object or (x,y) tuple
            index: Optional position in vertex order
        """
        if not isinstance(vertex, Vertex):
            vertex = Vertex(vertex[0], vertex[1])

        if vertex.index is None:
            vertex.index = len(self._vertices)

        self._vertices.append(vertex)
        if index is None:
            self._indices.append(vertex.index)
        else:
            self._indices.insert(index, vertex.index)

    def add_vertices(self, vertices):
        """Add multiple vertices"""
        for vertex in vertices:
            self.add_vertex(vertex)

    @property
    def vertices(self):
        """Get all vertices in the order they were added"""
        return [self._vertices[i] for i in self._indices]

    @property
    def edges(self):
        """Get all edges as (start_vertex, end_vertex) pairs"""
        edges = []
        n = len(self._indices)
        for i in range(n):
            start = self._vertices[self._indices[i]]
            end = self._vertices[self._indices[(i + 1) % n]]
            edges.append((start, end))
        return edges

    def get_vertex_by_index(self, index):
        """Get vertex by its index"""
        for vertex in self._vertices:
            if vertex.index == index:
                return vertex
        raise ValueError(f"No vertex with index {index}")

    def __str__(self):
        vertex_info = "\n".join(
            f"  {v}" for v in self.vertices
        )
        edge_info = "\n".join(
            f"  Edge {i}: {start.index}→{end.index}"
            for i, (start, end) in enumerate(self.edges)
        )
        return f"Polygon with {len(self._vertices)} vertices:\n{vertex_info}\nEdges:\n{edge_info}"

    def plot(self):
        """Visualize the polygon (requires matplotlib)"""
        try:
            import matplotlib.pyplot as plt

            # Get coordinates in order
            x = [v.x for v in self.vertices]
            y = [v.y for v in self.vertices]
            # Close the polygon
            x.append(x[0])
            y.append(y[0])

            plt.figure()
            plt.plot(x, y, 'b-', marker='o')
            for v in self.vertices:
                plt.text(v.x, v.y, f"{v.index}", color='red')
            plt.title("Polygon Visualization")
            plt.grid(True)
            plt.axis('equal')
            plt.show()
        except ImportError:
            print("Matplotlib not available for plotting")


# Usage examples:

# Example 1: Create from Vertex objects
v1 = Vertex(0, 0, 0)
v2 = Vertex(1, 0, 1)
v3 = Vertex(1, 1, 2)
v4 = Vertex(0, 1, 3)

poly1 = Polygon([v1, v2, v3, v4])
print("Polygon from Vertex objects:")
print(poly1)

# Example 2: Create from coordinates with auto-indexing
poly2 = Polygon([(0, 0), (2, 0), (1, 2)])
print("\nPolygon from coordinates with auto-indexing:")
print(poly2)

# Example 3: Mixed creation and visualization
poly3 = Polygon()
poly3.add_vertex((0, 0))
poly3.add_vertex(Vertex(2, 0))
poly3.add_vertex((1, 2))
print("\nPolygon built incrementally:")
print(poly3)
poly3.plot()

############################################
class PolygonSplitter:
    def __init__(self, polygon):
        self.polygon = polygon
        self.vertices = polygon.vertices

    def split_and_connect(self):
        # Split vertices into two equal sections
        split_point = len(self.vertices) // 2
        a = self.vertices[:split_point]
        b = self.vertices[split_point:]

        # Reverse section b
        b_reversed = b[::-1]

        # Pair up vertices from a and reversed b
        pairs = []
        min_length = min(len(a), len(b_reversed))

        for i in range(min_length):
            pairs.append((a[i], b_reversed[i]))

        # If there's an odd vertex, connect middle vertex to itself
        if len(self.vertices) % 2 != 0:
            middle = self.vertices[split_point]
            pairs.append((middle, middle))

        return a, b_reversed, pairs

    def visualize(self):
        import matplotlib.pyplot as plt

        a, b_reversed, pairs = self.split_and_connect()

        plt.figure(figsize=(10, 5))

        # Plot original polygon
        plt.subplot(1, 2, 1)
        x = [v.x for v in self.vertices] + [self.vertices[0].x]
        y = [v.y for v in self.vertices] + [self.vertices[0].y]
        plt.plot(x, y, 'b-', marker='o', label='Original')
        for v in self.vertices:
            plt.text(v.x, v.y, f"{v.index}", color='red')
        plt.title("Original Polygon")
        plt.grid(True)
        plt.axis('equal')
        plt.legend()

        # Plot split and connected lines
        plt.subplot(1, 2, 2)

        # Plot section a (blue)
        a_x = [v.x for v in a]
        a_y = [v.y for v in a]
        plt.plot(a_x, a_y, 'b-', marker='o', label='Section A')

        # Plot reversed section b (green)
        b_x = [v.x for v in b_reversed]
        b_y = [v.y for v in b_reversed]
        plt.plot(b_x, b_y, 'g-', marker='o', label='Section B Reversed')

        # Plot connecting lines (red)
        for pair in pairs:
            x = [pair[0].x, pair[1].x]
            y = [pair[0].y, pair[1].y]
            plt.plot(x, y, 'r--', label='Connection' if pair == pairs[0] else "")

        plt.title("Split and Connected")
        plt.grid(True)
        plt.axis('equal')
        plt.legend()

        plt.tight_layout()
        plt.show()


# Example usage:

# Create a sample polygon (hexagon)
vertices = [
    Vertex(0, 1, 0),
    Vertex(1, 2, 1),
    Vertex(2, 1.5, 2),
    Vertex(2.5, 0, 3),
    Vertex(1.5, -1, 4),
    Vertex(0.5, -0.5, 5)
]

polygon = Polygon(vertices)
splitter = PolygonSplitter(polygon)

# Get the split sections and connections
a, b_reversed, pairs = splitter.split_and_connect()

print("Section A vertices:")
for v in a:
    print(v)

print("\nSection B (reversed) vertices:")
for v in b_reversed:
    print(v)

print("\nConnecting pairs:")
for i, (v1, v2) in enumerate(pairs):
    print(f"Pair {i}: {v1.index} ↔ {v2.index}")

# Visualize the result
splitter.visualize()
##############################################
import math


class SegmentTruncator:
    def __init__(self, polygon, max_length):
        self.polygon = polygon
        self.max_length = max_length

    def truncate_segment(self, v1, v2):
        """Truncate a segment if longer than max_length, returning new midpoint"""
        dx = v2.x - v1.x
        dy = v2.y - v1.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance <= self.max_length:
            return None  # No truncation needed

        # Calculate ratio to truncate at max_length
        ratio = self.max_length / distance
        new_x = v1.x + ratio * dx
        new_y = v1.y + ratio * dy

        # Create new vertex (index will be assigned later)
        return Vertex(new_x, new_y)

    def process_polygon(self):
        splitter = PolygonSplitter(self.polygon)
        a, b_reversed, pairs = splitter.split_and_connect()

        new_vertices_a = []
        new_vertices_b = []
        connection_points = []

        # Process section A (original order)
        for v in a:
            new_vertices_a.append(Vertex(v.x, v.y, v.index))

        # Process section B (reversed order)
        for v in b_reversed:
            new_vertices_b.append(Vertex(v.x, v.y, v.index))

        # Process connecting segments
        for v_a, v_b in pairs:
            # Skip self-connections (middle vertex in odd-count polygons)
            if v_a == v_b:
                connection_points.append(v_a)
                continue

            # Truncate the segment in both directions
            mid1 = self.truncate_segment(v_a, v_b)
            mid2 = self.truncate_segment(v_b, v_a)

            if mid1 and mid2:
                connection_points.extend([mid1, mid2])
            else:
                connection_points.append(Vertex(
                    (v_a.x + v_b.x) / 2,
                    (v_a.y + v_b.y) / 2
                ))

        # Create new polygons
        polygon1 = Polygon(new_vertices_a + connection_points)
        polygon2 = Polygon(new_vertices_b + connection_points[::-1])

        return polygon1, polygon2, connection_points

    def visualize(self):
        import matplotlib.pyplot as plt

        poly1, poly2, connections = self.process_polygon()

        plt.figure(figsize=(12, 6))

        # Original polygon
        plt.subplot(1, 3, 1)
        x = [v.x for v in self.polygon.vertices] + [self.polygon.vertices[0].x]
        y = [v.y for v in self.polygon.vertices] + [self.polygon.vertices[0].y]
        plt.plot(x, y, 'b-', alpha=0.5)
        plt.scatter(x, y, c='blue')
        plt.title("Original Polygon")
        plt.grid(True)
        plt.axis('equal')

        # Connection points
        plt.subplot(1, 3, 2)
        plt.plot(x, y, 'b-', alpha=0.2)
        for v in connections:
            plt.scatter(v.x, v.y, c='red', marker='x', s=100)
        plt.title("Truncation Points")
        plt.grid(True)
        plt.axis('equal')

        # Resulting polygons
        plt.subplot(1, 3, 3)
        # Polygon 1
        x1 = [v.x for v in poly1.vertices] + [poly1.vertices[0].x]
        y1 = [v.y for v in poly1.vertices] + [poly1.vertices[0].y]
        plt.plot(x1, y1, 'g-')
        # Polygon 2
        x2 = [v.x for v in poly2.vertices] + [poly2.vertices[0].x]
        y2 = [v.y for v in poly2.vertices] + [poly2.vertices[0].y]
        plt.plot(x2, y2, 'm-')
        plt.title("Resulting Polygons")
        plt.grid(True)
        plt.axis('equal')

        plt.tight_layout()
        plt.show()


# Example usage:
vertices = [
    Vertex(0, 0, 0),
    Vertex(2, 0, 1),
    Vertex(3, 2, 2),
    Vertex(1, 3, 3),
    Vertex(-1, 2, 4),
    Vertex(-1, 1, 5)
]

polygon = Polygon(vertices)
truncator = SegmentTruncator(polygon, max_length=1.5)

# Get the resulting polygons
poly1, poly2, connections = truncator.process_polygon()

print("First resulting polygon vertices:")
for v in poly1.vertices:
    print(f"Vertex {v.index}: ({v.x:.2f}, {v.y:.2f})")

print("\nSecond resulting polygon vertices:")
for v in poly2.vertices:
    print(f"Vertex {v.index}: ({v.x:.2f}, {v.y:.2f})")

print("\nConnection points:")
for i, v in enumerate(connections):
    print(f"Point {i}: ({v.x:.2f}, {v.y:.2f})")

# Visualize the process
truncator.visualize()
##################################################################
import math
class PolygonProcessor:
    def __init__(self, polygon, max_length=1.5):
        self.polygon = polygon
        self.max_length = max_length
        self.vertices = polygon.vertices

    def _split_segment(self, v1, v2):
        """Split segment if longer than max_length, return new intermediate points"""
        dx = v2.x - v1.x
        dy = v2.y - v1.y
        length = math.sqrt(dx ** 2 + dy ** 2)

        if length <= self.max_length:
            return []

        num_splits = math.ceil(length / self.max_length)
        step = 1.0 / num_splits
        new_points = []

        for i in range(1, num_splits):
            t = i * step
            new_x = v1.x + t * dx
            new_y = v1.y + t * dy
            # Create new vertex with None index (to be assigned later)
            new_points.append(Vertex(new_x, new_y, None))

        return new_points

    def process(self):
        # Split vertices into two equal sections
        split_point = len(self.vertices) // 2
        a = self.vertices[:split_point]
        b = self.vertices[split_point:][::-1]  # reversed

        # Generate all connecting segments
        connections = []
        for v_a, v_b in zip(a, b):
            connections.append((v_a, v_b))

        # Process each connection to create new vertices
        new_vertices = []
        connection_info = []

        for i, (v1, v2) in enumerate(connections):
            intermediate_points = self._split_segment(v1, v2)
            connection_info.append({
                'start': v1,
                'end': v2,
                'new_points': intermediate_points,
                'original_pair': (v1.index, v2.index)
            })
            new_vertices.extend(intermediate_points)

        # Assign indices to new vertices (continuing from original max index)
        max_index = max(v.index for v in self.vertices) if self.vertices else -1
        for i, vertex in enumerate(new_vertices, start=max_index + 1):
            vertex.index = i

        # Create new polygons by combining original and new vertices
        # while maintaining original order with new connections inserted

        # First create the main polygon with inserted points
        main_poly_vertices = []
        original_index = 0

        # Add section A vertices
        for v in a:
            main_poly_vertices.append(v)

        # Add new vertices between connections
        for info in connection_info:
            main_poly_vertices.extend(info['new_points'])

        # Add section B vertices (reversed back to original order)
        for v in reversed(b):
            main_poly_vertices.append(v)

        # Create the main polygon
        main_polygon = Polygon(main_poly_vertices)

        # Create sub-polygons for each truncated segment
        sub_polygons = []
        for info in connection_info:
            if info['new_points']:
                poly_vertices = [info['start']] + info['new_points'] + [info['end']]
                sub_polygons.append(Polygon(poly_vertices))

        return {
            'main_polygon': main_polygon,
            'sub_polygons': sub_polygons,
            'connection_info': connection_info,
            'new_vertices': new_vertices
        }

    def visualize(self, result):
        import matplotlib.pyplot as plt

        plt.figure(figsize=(12, 6))

        # Original polygon
        plt.subplot(1, 2, 1)
        x = [v.x for v in self.vertices] + [self.vertices[0].x]
        y = [v.y for v in self.vertices] + [self.vertices[0].y]
        plt.plot(x, y, 'b-', marker='o', alpha=0.5, label='Original')
        for v in self.vertices:
            plt.text(v.x, v.y, f"{v.index}", color='blue')
        plt.title("Original Polygon")
        plt.grid(True)
        plt.axis('equal')
        plt.legend()

        # Processed result
        plt.subplot(1, 2, 2)

        # Plot main polygon
        main_poly = result['main_polygon']
        x = [v.x for v in main_poly.vertices] + [main_poly.vertices[0].x]
        y = [v.y for v in main_poly.vertices] + [main_poly.vertices[0].y]
        plt.plot(x, y, 'g-', marker='o', alpha=0.3, label='Main Polygon')

        # Plot new vertices
        new_vertices = result['new_vertices']
        if new_vertices:
            x = [v.x for v in new_vertices]
            y = [v.y for v in new_vertices]
            plt.scatter(x, y, c='red', marker='x', s=100, label='New Vertices')
            for v in new_vertices:
                plt.text(v.x, v.y, f"{v.index}", color='red')

        # Plot sub-polygons
        for i, poly in enumerate(result['sub_polygons']):
            x = [v.x for v in poly.vertices]
            y = [v.y for v in poly.vertices]
            plt.plot(x, y, 'm--', marker='s', alpha=0.7,
                     label=f'Segment {i + 1}' if i == 0 else "")
            for v in poly.vertices:
                if v in new_vertices:
                    plt.text(v.x, v.y, f"{v.index}", color='red')

        plt.title("Processed Result")
        plt.grid(True)
        plt.axis('equal')
        plt.legend()

        plt.tight_layout()
        plt.show()


# Example usage:
vertices = [
    Vertex(0, 0, 0),
    Vertex(2, 0, 1),
    Vertex(3, 2, 2),
    Vertex(1, 3, 3),
    Vertex(-1, 2, 4),
    Vertex(-1, 1, 5)
]

polygon = Polygon(vertices)
processor = PolygonProcessor(polygon, max_length=1.2)
result = processor.process()

print("Main Polygon Vertices:")
for v in result['main_polygon'].vertices:
    print(v)

print("\nNew Vertices Created:")
for v in result['new_vertices']:
    print(v)

print("\nSub-polygons from truncated segments:")
for i, poly in enumerate(result['sub_polygons']):
    print(f"\nSegment Polygon {i + 1}:")
    for v in poly.vertices:
        print(v)

processor.visualize(result)