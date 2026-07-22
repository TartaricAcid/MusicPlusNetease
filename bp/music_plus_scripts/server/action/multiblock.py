# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.object.item_use_block_object import ItemUseBlockObject
from music_plus_scripts.utils.blocks import REPLACEABLE
from music_plus_scripts.utils.direction import aux_to_direction, direction_to_aux
from music_plus_scripts.utils.multiblock import (
    CORE_BLOCK_KEY,
    CORE_POS_KEY,
    MEMBER_INDEX_KEY,
    MULTIBLOCK_PART_BLOCKS,
    STRUCTURE_VERSION_KEY,
    get_all_multiblock_configs,
    get_core_member_index,
    get_member_positions,
    get_multiblock_by_core,
    get_placement_origin,
    rotate_offset,
)

factory = serverApi.GetEngineCompFactory()
block_info = factory.CreateBlockInfo(levelId)
block_entity_data = factory.CreateBlockEntityData(levelId)
game = factory.CreateGame(levelId)

# 正在由脚本放置或拆除的结构，用于忽略 SetBlockNew 引发的重入事件。
_MUTATING_STRUCTURES = set()

# 暂存销毁前解析出的结构信息，供随后的销毁完成事件继续处理。
_PENDING_DESTROYS = {}


def place_multiblock_instrument(args, config):
    use = ItemUseBlockObject(args)
    player = use.get_player()

    if use.face != 1:
        player.send_tip_msg("只能点击方块顶部放置乐器！")
        return False

    core_pos = get_placement_origin(use.get_pos(), use.get_block_name())
    direction = player.get_opposite_direction_rot()
    positions = get_member_positions(core_pos, direction, config["members"])

    for pos in positions:
        block = block_info.GetBlockNew(pos, use.get_dimension())
        if block is None or block["name"] not in REPLACEABLE:
            player.send_tip_msg("乐器占用范围内有阻挡物，无法放置！")
            return False

    structure_key = _structure_key(use.get_dimension(), core_pos)
    _MUTATING_STRUCTURES.add(structure_key)

    try:
        for index, pos in enumerate(positions):
            part_block = config["members"][index][1]
            if pos == core_pos:
                block = {
                    "name": config["core_block"],
                    "aux": direction_to_aux(direction),
                }
            else:
                block = {
                    "name": part_block,
                    "aux": direction_to_aux(direction),
                }

            block_info.SetBlockNew(pos, block, 0, use.get_dimension(), False, False)
            if pos != core_pos:
                block_info.SetBlockEntityData(
                    use.get_dimension(),
                    pos,
                    {
                        CORE_POS_KEY: list(core_pos),
                        CORE_BLOCK_KEY: config["core_block"],
                        MEMBER_INDEX_KEY: index,
                        STRUCTURE_VERSION_KEY: config["version"],
                    }
                )
    finally:
        _MUTATING_STRUCTURES.discard(structure_key)

    if game.GetPlayerGameType(use.get_player_id()) != 1:
        use.reduce_player_item(1)

    use.play_sound_and_swing_hand("dig.wood")
    return True


def resolve_multiblock(block_name, pos, dimension, aux=None):
    if block_name in MULTIBLOCK_PART_BLOCKS:
        context = _resolve_part_from_data(block_name, pos, dimension)
        if context is not None:
            return context
        return _resolve_part_from_surroundings(block_name, pos, dimension)

    config = get_multiblock_by_core(block_name)
    if config is None:
        return None

    if aux is None:
        block = block_info.GetBlockNew(pos, dimension)
        if block is None:
            return None
        aux = block.get("aux", 0)
    direction = aux_to_direction(aux)

    return _build_context(
        config,
        pos,
        direction,
        aux,
        pos,
        get_core_member_index(config["members"])
    )


def destroy_multiblock(context, dimension, player_id=None, drop_item=False):
    core_pos = context["core_pos"]
    structure_key = _structure_key(dimension, core_pos)
    if structure_key in _MUTATING_STRUCTURES:
        return

    _MUTATING_STRUCTURES.add(structure_key)
    try:
        from music_plus_scripts.server.action.seated_instrument import remove_seated_instrument_at

        remove_seated_instrument_at(core_pos, dimension)
        members = context["config"]["members"]
        positions = get_member_positions(core_pos, context["direction"], members)
        for index, pos in enumerate(positions):
            block = block_info.GetBlockNew(pos, dimension)
            if block is None:
                continue
            if pos == core_pos:
                if block["name"] != context["config"]["core_block"]:
                    continue
            elif block["name"] != members[index][1]:
                continue
            block_info.SetBlockNew(pos, {"name": "minecraft:air"}, 0, dimension, False, False)

        if drop_item and player_id is not None and game.GetPlayerGameType(player_id) != 1:
            System.CreateEngineItemEntity(
                {"newItemName": context["config"]["item_name"], "count": 1},
                dimension,
                (core_pos[0] + 0.5, core_pos[1] + 0.5, core_pos[2] + 0.5),
            )
    finally:
        _MUTATING_STRUCTURES.discard(structure_key)


def handle_multiblock_try_destroy(args):
    pos = args["x"], args["y"], args["z"]
    context = resolve_multiblock(args["fullName"], pos, args["dimensionId"], args["auxData"])
    if context is None:
        return False

    args["spawnResources"] = False
    pending_key = _pending_destroy_key(args["dimensionId"], pos)
    _PENDING_DESTROYS[pending_key] = context, args["playerId"]
    game.AddTimer(1.0, _clear_pending_destroy, pending_key)
    return True


def handle_multiblock_destroyed(args):
    pos = args["x"], args["y"], args["z"]
    pending_key = _pending_destroy_key(args["dimensionId"], pos)
    pending = _PENDING_DESTROYS.pop(pending_key, None)
    if pending is None:
        context = resolve_multiblock(args["fullName"], pos, args["dimensionId"], args["auxData"])
        player_id = args["playerId"]
    else:
        context = pending[0]
        player_id = pending[1]

    if context is None:
        return False
    destroy_multiblock(context, args["dimensionId"], player_id, True)
    return True


def handle_multiblock_remove(args):
    block_name = args["fullName"]
    if block_name not in MULTIBLOCK_PART_BLOCKS and get_multiblock_by_core(block_name) is None:
        return False

    pos = args["x"], args["y"], args["z"]
    if _pending_destroy_key(args["dimension"], pos) in _PENDING_DESTROYS:
        return True
    if block_name not in MULTIBLOCK_PART_BLOCKS:
        structure_key = _structure_key(args["dimension"], pos)
        if structure_key in _MUTATING_STRUCTURES:
            return True

    context = resolve_multiblock(block_name, pos, args["dimension"], args["auxValue"])
    if context is not None:
        destroy_multiblock(context, args["dimension"])
    return True


def _build_context(config, core_pos, direction, aux, clicked_pos, member_index):
    return {
        "config": config,
        "core_pos": core_pos,
        "core_block": config["core_block"],
        "direction": direction,
        "core_aux": aux,
        "clicked_pos": clicked_pos,
        "member_index": member_index,
    }


def _resolve_part_from_data(block_name, pos, dimension):
    be_data = block_entity_data.GetBlockEntityData(dimension, pos)
    if be_data is None:
        return None

    raw_core_pos = be_data[CORE_POS_KEY]
    core_block = be_data[CORE_BLOCK_KEY]
    member_index = be_data[MEMBER_INDEX_KEY]
    structure_version = be_data[STRUCTURE_VERSION_KEY]
    if raw_core_pos is None or core_block is None or member_index is None or structure_version is None:
        return None

    core_pos = tuple(raw_core_pos)
    config = get_multiblock_by_core(core_block)
    if config is None or structure_version != config["version"]:
        return None
    if not 0 <= member_index < len(config["members"]):
        return None
    if config["members"][member_index][1] != block_name:
        return None

    core = block_info.GetBlockNew(core_pos, dimension)
    if core is None or core["name"] != core_block:
        return None

    aux = core.get("aux", 0)
    direction = aux_to_direction(aux)
    positions = get_member_positions(core_pos, direction, config["members"])
    if positions[member_index] != pos:
        return None
    return _build_context(config, core_pos, direction, aux, pos, member_index)


def _resolve_part_from_surroundings(block_name, pos, dimension):
    for config in get_all_multiblock_configs():
        for direction in ("north", "east", "south", "west"):
            for member_index, member in enumerate(config["members"]):
                offset, part_block = member
                if offset == (0, 0, 0):
                    continue
                if part_block != block_name:
                    continue
                dx, dy, dz = rotate_offset(offset, direction)
                core_pos = pos[0] - dx, pos[1] - dy, pos[2] - dz
                core = block_info.GetBlockNew(core_pos, dimension)
                if core is None or core["name"] != config["core_block"]:
                    continue
                aux = core.get("aux", 0)
                if aux_to_direction(aux) != direction:
                    continue
                return _build_context(config, core_pos, direction, aux, pos, member_index)
    return None


def _structure_key(dimension, core_pos):
    return dimension, core_pos[0], core_pos[1], core_pos[2]


def _pending_destroy_key(dimension, pos):
    return dimension, pos[0], pos[1], pos[2]


def _clear_pending_destroy(pending_key):
    _PENDING_DESTROYS.pop(pending_key, None)
