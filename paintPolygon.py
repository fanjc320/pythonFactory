import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
from matplotlib.animation import FuncAnimation

# Define coordinates (example: a trapezoid)
# coords_up = [(0.74, 2.90), (3.35, 0.25), (0.74, -1.87), (-1.38, 0.19), (0.75, 2.91)]
# coords_down = [(0.78, 1.90), (2.29, 0.30), (0.74, -0.96), (-0.72, 0.16), (0.78, 1.90)]
# coords_up = [(0.97, 2.66), (1.21, 2.42), (1.45, 2.18), (1.68, 1.94), (1.92, 1.70), (2.16, 1.46), (2.39, 1.22), (2.63, 0.98), (2.87, 0.74), (3.10, 0.50), (3.34, 0.26), (3.09, 0.04), (2.83, -0.17), (2.57, -0.38), (2.31, -0.59), (2.05, -0.81), (1.78, -1.02), (1.52, -1.23), (1.26, -1.44), (1.00, -1.65), (0.74, -1.86), (0.49, -1.63), (0.25, -1.39), (0.01, -1.16), (-0.23, -0.92), (-0.47, -0.69), (-0.71, -0.45), (-0.96, -0.22), (-1.20, 0.02), (-1.32, 0.26), (-1.11, 0.53), (-0.91, 0.79), (-0.70, 1.06), (-0.49, 1.33), (-0.28, 1.59), (-0.08, 1.86), (0.13, 2.12), (0.34, 2.39), (0.55, 2.65)]
# coords_down = [(0.93, 1.74), (1.07, 1.59), (1.21, 1.44), (1.35, 1.29), (1.50, 1.14), (1.64, 0.99), (1.78, 0.83), (1.92, 0.68), (2.07, 0.53), (2.21, 0.38), (2.21, 0.24), (2.05, 0.11), (1.89, -0.02), (1.73, -0.16), (1.57, -0.29), (1.41, -0.42), (1.24, -0.55), (1.08, -0.68), (0.92, -0.81), (0.76, -0.94), (0.59, -0.84), (0.43, -0.72), (0.26, -0.59), (0.10, -0.47), (-0.07, -0.34), (-0.24, -0.22), (-0.40, -0.09), (-0.57, 0.04), (-0.72, 0.16), (-0.58, 0.32), (-0.44, 0.48), (-0.31, 0.64), (-0.17, 0.79), (-0.03, 0.95), (0.10, 1.11), (0.24, 1.27), (0.37, 1.42), (0.51, 1.58), (0.65, 1.74)]
# coords_down = [(-0.72, 0.16), (-0.58, 0.32), (-0.44, 0.48), (-0.31, 0.64), (-0.17, 0.79), (-0.03, 0.95), (0.10, 1.11), (0.24, 1.27), (0.37, 1.42), (0.51, 1.58), (0.65, 1.74), (0.93, 1.74), (1.07, 1.59), (1.21, 1.44), (1.35, 1.29), (1.50, 1.14), (1.64, 0.99), (1.78, 0.83), (1.92, 0.68), (2.07, 0.53), (2.21, 0.38), (2.21, 0.24), (2.05, 0.11), (1.89, -0.02), (1.73, -0.16), (1.57, -0.29), (1.41, -0.42), (1.24, -0.55), (1.08, -0.68), (0.92, -0.81), (0.76, -0.94), (0.59, -0.84), (0.43, -0.72), (0.26, -0.59), (0.10, -0.47), (-0.07, -0.34), (-0.24, -0.22), (-0.40, -0.09), (-0.57, 0.04)]

coords_up = [(10, 10), (50, 10), (50, 50), (10, 50)]##################
# coords_up = [(1, 0) ,(0.7, 0.7) ,(0, 1) ,(-0.7, 0.7) ,(-1, 0) ,(-0.7, -0.7) ,(0, -1) ,(0.7, -0.7)]
# coords_down = [(0.5, 0) ,(0.4, 0.4) ,(0, 0.5) ,(-0.4, 0.4) ,(-0.5, 0) ,(-0.4, -0.4) ,(0, -0.5) ,(0.4, -0.4)]

# print("coords_up count:"+len(coords_up))
# print("coords_down count:"+len(coords_down))
# Create plot
fig, ax = plt.subplots(constrained_layout=True)
# fig, ax = plt.subplots()
polygonU = Polygon(coords_up, closed=True, edgecolor='black', facecolor='cyan')
# polygonD = Polygon(coords_down, closed=True, edgecolor='black', facecolor='green')
ax.add_patch(polygonU)
# ax.add_patch(polygonD) ######## 注释开关

# Adjust axes to fit the polygon
# ax.set_xlim(0, 400)
# ax.set_ylim(0, 400)
ax.set_xlim(0, 60)#########
ax.set_ylim(0, 60)###########
# ax.invert_yaxis()
ax.set_aspect(1)
# fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

plt.grid(True)
# Annotate each point with its coordinate.
##################
for i in range(len(coords_up)):
    plt.annotate(f'{coords_up[i]}', coords_up[i], textcoords="offset points", xytext=(0,5), ha='center')
# for i in range(len(coords_down)):
#     plt.annotate(f'{coords_down[i]}', coords_down[i], textcoords="offset points", xytext=(0,5), ha='center')



# plt.figure(figsize=(100,100))
plt.rcParams["figure.figsize"] = (100,100)
plt.show()