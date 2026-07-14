# -*- coding: utf-8 -*-

# 原版所有可替换的方块 ID
REPLACEABLE = (
    "minecraft:air",
    "minecraft:short_grass",
    "minecraft:tall_grass",
    "minecraft:fern",
    "minecraft:large_fern",
    "minecraft:nether_sprouts",
    "minecraft:snow_layer",
    "minecraft:vine",
    "minecraft:water",
    "minecraft:lava",
    "minecraft:fire",
    # 部分移动光源类模组会使用光源方块，所以导致放置方块时无法替换，暂时将其加入可替换列表
    "minecraft:light_block_0",
    "minecraft:light_block_1",
    "minecraft:light_block_2",
    "minecraft:light_block_3",
    "minecraft:light_block_4",
    "minecraft:light_block_5",
    "minecraft:light_block_6",
    "minecraft:light_block_7",
    "minecraft:light_block_8",
    "minecraft:light_block_9",
    "minecraft:light_block_10",
    "minecraft:light_block_11",
    "minecraft:light_block_12",
    "minecraft:light_block_13",
    "minecraft:light_block_14",
    "minecraft:light_block_15"
)

# 面方向对应的坐标偏移
FACE_OFFSETS = {
    0: (0, -1, 0),  # 下
    1: (0, 1, 0),  # 上
    2: (0, 0, -1),  # 北
    3: (0, 0, 1),  # 南
    4: (-1, 0, 0),  # 西
    5: (1, 0, 0)  # 东
}


def is_replaceable(block_name):
    """
    判断方块是否可替换
    """

    return block_name in REPLACEABLE
