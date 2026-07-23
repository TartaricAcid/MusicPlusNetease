# -*- coding: utf-8 -*-

import time

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.action.block_instrument import is_paper_tape, handle_paper_tape_insert
from music_plus_scripts.server.action.multiblock import place_multiblock_instrument
from music_plus_scripts.server.action.multiblock import resolve_multiblock
from music_plus_scripts.server.action.musician import MUSICIAN_ITEM, handle_item_use
from music_plus_scripts.server.store.instrument_registry import get_paper_tape_instrument_config
from music_plus_scripts.server.store.instrument_registry import get_seated_instrument_config
from music_plus_scripts.utils.multiblock import get_multiblock_by_item

factory = serverApi.GetEngineCompFactory()
game = factory.CreateGame(levelId)

ITEM_COOLDOWN_KEY = "music_plus:item_use_cooldown"


@Listen(Events.ServerItemUseOnEvent)
def on_item_use_on_block(args):
    if args.get("ret"):
        return

    item = args["itemDict"]
    block_name = args["blockName"]
    item_name = item["newItemName"]

    if item_name == MUSICIAN_ITEM and can_use(args):
        multiblock = resolve_multiblock(
            block_name,
            (args["x"], args["y"], args["z"]),
            args["dimensionId"],
            args["blockAuxValue"],
        )
        if multiblock:
            instrument_config = get_seated_instrument_config(multiblock["core_block"])
            if instrument_config:
                handle_item_use(
                    args,
                    instrument_config,
                    multiblock["core_pos"],
                    multiblock["core_aux"],
                    multiblock["core_block"],
                )
                from music_plus_scripts.server.event.block_use import record_cooldown as record_block_use_cooldown
                record_block_use_cooldown(args["entityId"])
                return

        instrument_config = get_seated_instrument_config(block_name)
        if instrument_config:
            handle_item_use(args, instrument_config)
            from music_plus_scripts.server.event.block_use import record_cooldown as record_block_use_cooldown
            record_block_use_cooldown(args["entityId"])
            return

        handle_item_use(args)
        return

    multiblock_config = get_multiblock_by_item(item_name)
    if multiblock_config:
        if can_use(args):
            place_multiblock_instrument(args, multiblock_config)
            from music_plus_scripts.server.event.block_use import record_cooldown as record_block_use_cooldown
            record_block_use_cooldown(args["entityId"])
        args["ret"] = True
        return

    # 纸带右击方块乐器 → 塞入并播放曲目
    instrument = get_paper_tape_instrument_config(block_name)
    if is_paper_tape(item_name) and instrument and can_use(args):
        handle_paper_tape_insert(args, instrument)
        args["ret"] = True


def is_player_sneaking(player_id):
    """
    判断玩家是否按下了潜行键
    """
    player = factory.CreatePlayer(player_id)
    return player.isSneaking()


def can_use(args):
    """
    先写一套自己的冷却判断机制
    """
    entity_id = args["entityId"]
    extra_data = factory.CreateModAttr(entity_id)
    timestamp = time.time()

    # 冷却时间为 0.2 秒
    if extra_data.GetAttr(ITEM_COOLDOWN_KEY) and timestamp - extra_data.GetAttr(ITEM_COOLDOWN_KEY) < 0.2:
        args["ret"] = True
        return False
    else:
        extra_data.SetAttr(ITEM_COOLDOWN_KEY, timestamp, False, False)
        return True


def record_cooldown(player_id, extra_time=0):
    """
    有时候方块交互需要禁止下一帧的物品交互
    """
    extra_data = factory.CreateModAttr(player_id)
    timestamp = time.time() + extra_time
    extra_data.SetAttr(ITEM_COOLDOWN_KEY, timestamp, False, False)
