# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Client import *
from music_plus_scripts.utils.blocks import REPLACEABLE
from music_plus_scripts.utils.multiblock import (
    direction_from_yaw,
    get_member_positions,
    get_multiblock_by_item,
    get_placement_origin,
    opposite_direction,
)

factory = clientApi.GetEngineCompFactory()
block_info = factory.CreateBlockInfo(levelId)
game = factory.CreateGame(playerId)


def check_multiblock_instrument_place(args):
    item_name = args["itemDict"]["newItemName"]
    config = get_multiblock_by_item(item_name)
    if config is None:
        return False

    if args["face"] != 1:
        args["ret"] = True
        game.SetTipMessage("只能点击方块顶部放置乐器！")
        return True

    clicked_pos = args["x"], args["y"], args["z"]
    clicked_block_name = _get_block_name(clicked_pos)
    core_pos = get_placement_origin(clicked_pos, clicked_block_name)
    yaw = factory.CreateRot(playerId).GetRot()[1]
    direction = opposite_direction(direction_from_yaw(yaw))

    for pos in get_member_positions(core_pos, direction, config["members"]):
        block_name = _get_block_name(pos)
        if block_name not in REPLACEABLE:
            args["ret"] = True
            game.SetTipMessage("乐器占用范围内有阻挡物，无法放置！")
            return True
    return True


def _get_block_name(pos):
    block = block_info.GetBlock(pos)
    if block is None:
        return ""
    return block[0]
