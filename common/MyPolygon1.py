### https://chat.deepseek.com/a/chat/s/e761abc6-daad-42c8-80f9-16d2dc229e7a
# python, polygon, vertices composed by point and indices, then enumerate vertices and print info
# auto index
# compose index and vertice as class
#     class Vertice:
#         vertice
#         index
# given this Polygon with  vertices of this type, split vertices into two sections as a and b equally, keeping initial order of vertices. reverse the order of vertices in b, connect vertices pairing up, so we get several line segments.
# if the above segments is longer than a fixed number, truncate them, get the new points, get the new vertices, combine with original vertices to compose new polygons, maintain the indices and order of the original vertices
# line 19, AttributeError: 'dict' object has no attribute'vertices'
import math

sPolyKey = "poly_origin"
class Vertex:
    def __init__(self, x, y, index=None, index1=0, index2=0):
        self.x = x
        self.y = y
        self.index1 = index1 # 截断产生的点，对应的线段端点的坐标
        self.index2 = index2
        self.index = index if index is not None else -1  # -1 for new vertices

    def distance_to(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def __repr__(self):
        return f"Vertex({self.x}, {self.y}, index={self.index})"


class Polygon:
    def __init__(self, vertices):
        id = 0
        if len(vertices) > 0 and (vertices[0].index is None or vertices[0].index == -1):
            for vert in vertices:
                vert.index = id
                id += 1
        # for vert in vertices:
        #     print("Polygon vert index:", vert.index)
        self.vertices = vertices
        self.indices = [v.index for v in vertices]

    def __repr__(self):
        return f"Polygon({len(self.vertices)} vertices)"


class PolygonProcessor:
    def __init__(self, polygon, max_length=1.0):
        self.original_polygon = polygon
        self.max_length = max_length
        self.new_vertices = []
        self.next_new_index = max(v.index for v in polygon.vertices) + 1 if polygon.vertices else 0

    def _truncate_segment(self, v1, v2):
        """Truncate segment if longer than max_length, return new intermediate vertices"""
        distance = v1.distance_to(v2)
        if distance <= self.max_length:
            return []

        num_segments = math.ceil(distance / self.max_length)
        segment_length = distance / num_segments

        dx = (v2.x - v1.x) / distance
        dy = (v2.y - v1.y) / distance

        new_vertices = []
        for i in range(1, num_segments):
            x = v1.x + i * segment_length * dx
            y = v1.y + i * segment_length * dy
            new_vertex = Vertex(x, y, self.next_new_index, index1=v1.index, index2=v2.index)
            self.next_new_index += 1
            new_vertices.append(new_vertex)

        return new_vertices

    def _truncate_segment_new(self, v1, v2):
        """Truncate segment if longer than max_length, return new intermediate vertices"""
        distance = v1.distance_to(v2)
        if distance <= self.max_length:
            return None

        num_segments = math.ceil(distance / self.max_length)
        segment_length = distance / num_segments

        dx = (v2.x - v1.x) / distance
        dy = (v2.y - v1.y) / distance

        x = v1.x + segment_length * dx
        y = v1.y + segment_length * dy
        new_vertex = Vertex(x, y, self.next_new_index, index1=v1.index, index2=v2.index)
        self.next_new_index += 1

        return new_vertex

    def process(self):
        original_vertices = self.original_polygon.vertices

        # Split into two sections
        split_point = len(original_vertices) // 2
        a = original_vertices[:split_point]
        b = original_vertices[split_point:][::-1]  # reversed

        # Process each pair
        connection_map_new = {}
        bNewPolygon = False
        sPolyKeyNew = sPolyKey
        v2_last = None
        for i in range(min(len(a), len(b))):# v1在被沿着画画的边
            v1 = a[i]
            v2 = b[i]
            print("PolygonProcessor process v1:", v1, " v2:", v2.index1)
            # Get intermediate vertices for this segment
            intermediate = self._truncate_segment_new(v1, v2) # return one vertex
            print("PolygonProcessor intermediate:", intermediate)

            # if len(intermediate) != 0:
            if intermediate is not None:
                connection_map_new.setdefault(sPolyKey, []).extend([v1, intermediate])
                if bNewPolygon == False: # 开启新的polygon分支
                    bNewPolygon = True
                    sPolyKeyNew = sPolyKeyNew + "_1"
                    if v2_last != None:#把前一个点也加进来，让新老polygon虽然可能有重叠，但可以完全覆盖原来的图形
                        connection_map_new.setdefault(sPolyKeyNew, []).append(v2_last)

                connection_map_new.setdefault(sPolyKeyNew, []).extend([v2, intermediate])
            else:
                if bNewPolygon == True:# 新的polygon结束，回到老的polygon
                    bNewPolygon = False
                    connection_map_new.setdefault(sPolyKeyNew, []).append(v2)#多增加一个点，让新老polygon虽然可能有重叠，但可以完全覆盖原来的图形
                connection_map_new.setdefault(sPolyKey, []).extend([v1, v2])

            v2_last = v2

        print("connection_map_new:", connection_map_new)
        # Generate new polygons
        # polygons = self._generate_polygons(connection_map)
        polygons_new = self._generate_polygons_new(connection_map_new)
        return polygons_new

    def _generate_polygons(self, connection_map):
        polygons = []

        for i, connection in enumerate(connection_map):
            next_i = (i + 1) % len(connection_map)
            next_connection = connection_map[next_i]

            vertices = [
                connection['from'],
                *connection['intermediate'],
                next_connection['from'],
                *reversed(next_connection['intermediate'])
            ]

            polygons.append(Polygon(vertices))

        return polygons

    def _generate_polygons_new(self, connection_map):
        polygons = []

        for key, vertices in connection_map.items():
            poly = []
            for vertice in vertices:
                print("_generate_polygons_new key:", key, " type:", type(vertice))
                print("_generate_polygons_new:", vertice)
                if key == sPolyKey and vertice.index2 != 0:
                    vertice.index = vertice.index2
                elif key != sPolyKey and vertice.index1 != 0:
                    vertice.index = vertice.index1
            sorted_vertices = sorted(vertices, key=lambda v: (v.index is not None, v.index))
            print("_generate_polygons_new sorted_vertices:", sorted_vertices)
            poly = Polygon(sorted_vertices)
            polygons.append(poly)

        return polygons

    def visualize(self, polygons):
        import matplotlib.pyplot as plt

        plt.figure(figsize=(12, 6))

        # Plot original polygon
        plt.subplot(1, 2, 1)
        original = self.original_polygon.vertices
        x = [v.x for v in original] + [original[0].x]
        y = [v.y for v in original] + [original[0].y]
        plt.plot(x, y, 'b-', marker='o')
        for v in original:
            plt.text(v.x, v.y, f"{v.index}", color='red')
        plt.title("Original Polygon")
        plt.grid(True)
        plt.axis('equal')

        # Plot result
        plt.subplot(1, 2, 2)

        # Plot original vertices
        orig_x = [v.x for v in original]
        orig_y = [v.y for v in original]
        plt.plot(orig_x, orig_y, 'bo', label='Original vertices')

        # Plot new vertices
        if self.new_vertices:
            new_x = [v.x for v in self.new_vertices]
            new_y = [v.y for v in self.new_vertices]
            plt.plot(new_x, new_y, 'go', label='New vertices')

        # Plot polygons
        colors = ['r', 'm', 'c', 'y']
        for i, poly in enumerate(polygons):
            x = [v.x for v in poly.vertices] + [poly.vertices[0].x]
            y = [v.y for v in poly.vertices] + [poly.vertices[0].y]
            plt.plot(x, y, '-', color=colors[i % len(colors)], label=f'Polygon {i}' if i < 3 else "")

        plt.title("Generated Polygons")
        plt.grid(True)
        plt.axis('equal')
        plt.legend()

        plt.tight_layout()
        plt.show()


#奇数个顶点，会漏掉一个点
original_vertices = [
    Vertex(0, 0, 0),
    Vertex(1, -0.2, 1),
    Vertex(2, 0, 2),
    Vertex(3, 1, 3),
    Vertex(2, 2, 4),
    Vertex(1, 2.3, 5),
    Vertex(0, 2, 6),
    Vertex(-0.5, 1.5, 7),
    Vertex(-1, 1, 8)
]

original_vertices = [
    Vertex(0, 0),
    Vertex(1, -0.2),
    Vertex(2, 0),
    Vertex(2.5, 0.2),
    Vertex(3, 1),
    Vertex(2, 2),
    Vertex(1, 2.3),
    Vertex(0, 2),
    Vertex(-0.5, 1.5),
    Vertex(-1, 1)
]

original_polygon = Polygon(original_vertices)
# processor = PolygonProcessor(original_polygon, max_length=0.8)
processor = PolygonProcessor(original_polygon, max_length=1.8)
result_polygons = processor.process()

print("Original polygon:", original_polygon)
print("\nGenerated polygons:")
for i, poly in enumerate(result_polygons):
    print(f"Polygon {i}: {poly}")
    print(f"Vertices: {poly.vertices}")
    print(f"Indices: {poly.indices}\n")

processor.visualize(result_polygons)