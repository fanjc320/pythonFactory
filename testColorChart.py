import matplotlib.pyplot as plt
import matplotlib
import numpy as np
matplotlib.rc("font",family='MicroSoft YaHei',weight="bold")
# 定义色卡颜色（按分组）
color_groups = {
    "柔和粉彩色系": ["#FFB6C1", "#98FF98", "#87CEEB", "#E6E6FA", "#FFFACD"],
    "活力糖果色": ["#FFA07A", "#FDFD96", "#FF6B6B", "#7DF9FF", "#A7FF83"],
    "高对比鲜艳色": ["#FF00FF", "#00FF7F", "#9400D3", "#FF8C00"],
    "自然大地色": ["#E2725B", "#808000", "#F4A460", "#4B5320"],
}

# 创建画布
fig, axes = plt.subplots(len(color_groups), 1, figsize=(10, 8))
fig.suptitle("动漫/游戏常用舒适鲜艳色卡", fontsize=16, y=1.02)

# 绘制每个分组的色卡
for ax, (group_name, colors) in zip(axes, color_groups.items()):
    # 为每个颜色创建一个矩形
    for i, color in enumerate(colors):
        rect = plt.Rectangle((i, 0), 1, 1, color=color)
        ax.add_patch(rect)
        # 添加颜色HEX标签
        ax.text(i + 0.5, 0.5, color, ha='center', va='center',
                color='black' if i % 2 == 0 else 'white', fontweight='bold')

    ax.set_xlim(0, len(colors))
    ax.set_ylim(0, 1)
    ax.set_title(group_name, pad=10)
    ax.axis('off')  # 隐藏坐标轴

plt.tight_layout()
plt.show()