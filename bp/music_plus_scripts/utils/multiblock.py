# -*- coding: utf-8 -*-

"""多方块乐器的共享结构定义与坐标计算。"""

MULTIBLOCK_PART_TALL_BLOCK = "music_plus:multiblock_part_tall"
MULTIBLOCK_PART_FULL_BLOCK = "music_plus:multiblock_part_full"
MULTIBLOCK_PART_HALF_BLOCK = "music_plus:multiblock_part_half"

MULTIBLOCK_PART_BLOCKS = frozenset((
    MULTIBLOCK_PART_TALL_BLOCK,
    MULTIBLOCK_PART_FULL_BLOCK,
    MULTIBLOCK_PART_HALF_BLOCK,
))

# 成员格式为 (本地坐标偏移, 辅助方块 ID)，核心位置的辅助方块 ID 为 None。
# 竖半砖的基准 AABB 位于本地南侧，并随放置方向的 aux 旋转。

CORE_POS_KEY = "music_plus:multiblock_core"
CORE_BLOCK_KEY = "music_plus:multiblock_core_block"
MEMBER_INDEX_KEY = "music_plus:multiblock_member"
STRUCTURE_VERSION_KEY = "music_plus:multiblock_version"

MEMBERS_TRIANGLE = (
    ((-1, 0, -2), MULTIBLOCK_PART_TALL_BLOCK),
    ((0, 0, -2), MULTIBLOCK_PART_TALL_BLOCK),
    ((-1, 0, -1), MULTIBLOCK_PART_TALL_BLOCK),
    ((0, 0, -1), MULTIBLOCK_PART_TALL_BLOCK),
    ((-1, 0, 0), MULTIBLOCK_PART_TALL_BLOCK),
    ((0, 0, 0), None),
    ((1, 0, 0), MULTIBLOCK_PART_TALL_BLOCK),
    ((-1, 0, 1), MULTIBLOCK_PART_TALL_BLOCK),
    ((0, 0, 1), MULTIBLOCK_PART_TALL_BLOCK),
    ((1, 0, 1), MULTIBLOCK_PART_TALL_BLOCK),
    ((-1, 0, 2), MULTIBLOCK_PART_HALF_BLOCK),
    ((0, 0, 2), MULTIBLOCK_PART_HALF_BLOCK),
    ((1, 0, 2), MULTIBLOCK_PART_HALF_BLOCK),
)

HONKYTONK_MEMBERS = (
    ((-1, 0, 1), MULTIBLOCK_PART_HALF_BLOCK),
    ((0, 0, 1), MULTIBLOCK_PART_HALF_BLOCK),
    ((1, 0, 1), MULTIBLOCK_PART_HALF_BLOCK),
    ((-1, 0, 0), MULTIBLOCK_PART_FULL_BLOCK),
    ((0, 0, 0), None),
    ((1, 0, 0), MULTIBLOCK_PART_FULL_BLOCK),
    ((-1, 1, 0), MULTIBLOCK_PART_FULL_BLOCK),
    ((0, 1, 0), MULTIBLOCK_PART_FULL_BLOCK),
    ((1, 1, 0), MULTIBLOCK_PART_FULL_BLOCK),
)

MEMBERS_3X1 = (
    ((-1, 0, 0), MULTIBLOCK_PART_TALL_BLOCK),
    ((0, 0, 0), None),
    ((1, 0, 0), MULTIBLOCK_PART_TALL_BLOCK)
)

MULTIBLOCK_REGISTRY = {
    "music_plus:piano": {
        "core_block": "music_plus:music_plus_piano",
        "members": MEMBERS_TRIANGLE,
        "version": 1,
    },
    "music_plus:harpsichord": {
        "core_block": "music_plus:music_plus_harpsichord",
        "members": MEMBERS_TRIANGLE,
        "version": 1,
    },
    "music_plus:honkytonk": {
        "core_block": "music_plus:music_plus_honkytonk",
        "members": HONKYTONK_MEMBERS,
        "version": 1,
    },
    "music_plus:vibra": {
        "core_block": "music_plus:music_plus_vibra",
        "members": MEMBERS_3X1,
        "version": 1,
    },
    "music_plus:guzheng": {
        "core_block": "music_plus:music_plus_guzheng",
        "members": MEMBERS_3X1,
        "version": 1,
    },
    "music_plus:electronic_keyboard": {
        "core_block": "music_plus:music_plus_electronic_keyboard",
        "members": MEMBERS_3X1,
        "version": 1,
    },
}

MULTIBLOCK_BY_CORE = dict(
    (config["core_block"], dict(config, item_name=item_name))
    for item_name, config in MULTIBLOCK_REGISTRY.items()
)


def get_multiblock_by_item(item_name):
    config = MULTIBLOCK_REGISTRY.get(item_name)
    if config is None:
        return None
    result = config.copy()
    result["item_name"] = item_name
    return result


def get_multiblock_by_core(core_block):
    return MULTIBLOCK_BY_CORE.get(core_block)


def get_all_multiblock_configs():
    return MULTIBLOCK_BY_CORE.values()


def get_placement_origin(clicked_pos, clicked_block_name):
    from music_plus_scripts.utils.blocks import REPLACEABLE

    if clicked_block_name in REPLACEABLE:
        return clicked_pos
    return clicked_pos[0], clicked_pos[1] + 1, clicked_pos[2]


def rotate_offset(offset, direction):
    x, y, z = offset
    if direction == "east":
        return -z, y, x
    if direction == "south":
        return -x, y, -z
    if direction == "west":
        return z, y, -x
    return x, y, z


def get_member_positions(core_pos, direction, members):
    positions = []
    for offset, _part_block in members:
        dx, dy, dz = rotate_offset(offset, direction)
        positions.append((core_pos[0] + dx, core_pos[1] + dy, core_pos[2] + dz))
    return positions


def get_core_member_index(members):
    for index, member in enumerate(members):
        if member[0] == (0, 0, 0):
            return index
    raise ValueError("Multiblock members must contain the core offset")


def direction_from_yaw(yaw):
    yaw %= 360
    if 45 <= yaw < 135:
        return "east"
    if 135 <= yaw < 225:
        return "south"
    if 225 <= yaw < 315:
        return "west"
    return "north"


def opposite_direction(direction):
    if direction == "north":
        return "south"
    if direction == "south":
        return "north"
    if direction == "west":
        return "east"
    return "west"
