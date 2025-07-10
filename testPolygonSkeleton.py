import numpy as np
from skimage.morphology import skeletonize, thin, medial_axis
from skimage.draw import polygon
import matplotlib.pyplot as plt
from  testSVG.polygon import extract_svg_paths, svg_path_to_polygons

def testSkeletonPolygon():
    # Create a polygon (example: a rectangle)
    polygon_vertices = np.array([
        [50, 50],
        [150, 50],
        [150, 150],
        [50, 150]
    ])

    # Create a binary image with the polygon filled
    img = np.zeros((200, 200), dtype=np.uint8)
    print("polygon_vertices.shape:", polygon_vertices.shape)
    rr, cc = polygon(polygon_vertices[:, 0], polygon_vertices[:, 1], img.shape)
    img[rr, cc] = 1

    # Skeletonize
    skeleton = skeletonize(img)

    # Display results
    fig, axes = plt.subplots(1, 2, figsize=(8, 4))
    axes[0].imshow(img, cmap='gray')
    axes[0].set_title('Original Polygon')
    axes[1].imshow(skeleton, cmap='gray')
    axes[1].set_title('Skeleton')
    plt.show()

testSkeletonPolygon()

# svg_filename = "./testSVG/test_polygon1.svg"
svg_filename = "./testSVG/test_polygon2.svg"
path_strings = extract_svg_paths(svg_filename)
print("path_strings len:", len(path_strings))
# 2. Convert each path to polygons
all_polygons = []
for path_str in path_strings:
    polygons = svg_path_to_polygons(path_str, samples_per_curve=20)
    all_polygons.extend(polygons)
# 3. Output results
print(f"Found {len(all_polygons)} polygons in {svg_filename}")
print("all_polygons[0]:", all_polygons[0])
# print("all_polygons.shape:", all_polygons[0].shape)'list' object has no attribute 'shape'

x_coords = [point[0] for point in all_polygons[0]]
y_coords = [point[1] for point in all_polygons[0]]

# Create a binary image with the polygon filled
img = np.zeros((1200, 1200), dtype=np.uint8)
rr, cc = polygon(x_coords, y_coords, img.shape)
img[rr, cc] = 1

# Skeletonize
skeleton = skeletonize(img)
skeleton_lee = skeletonize(img, method='lee')
skeleton_thin = thin(img)
skeleton_thin_iter = thin(img, max_num_iter=25)
skel, distance = medial_axis(img, return_distance=True)
dist_on_skel = distance * skel

# Display results
fig, axes = plt.subplots(1, 7, figsize=(48, 8))
# fig, axes = plt.subplots(2, 4, figsize=(24, 12))
axes[0].imshow(img, cmap='gray')
axes[0].set_title('Original Polygon')
axes[1].imshow(skeleton, cmap='gray')
axes[1].set_title('Skeleton')

axes[2].imshow(skeleton_lee, cmap='gray')
axes[2].set_title('Skeleton_lee')
axes[3].imshow(skeleton_thin, cmap='gray')
axes[3].set_title('Skeleton_thin')
axes[4].imshow(skeleton_thin_iter, cmap='gray')
axes[4].set_title('Skeleton_thin_iter')
axes[5].imshow(skel, cmap='gray')
axes[5].set_title('medial_axis')
axes[6].imshow(dist_on_skel, cmap='gray')
axes[6].set_title('dist_on_skel')
plt.show()