# -*- coding: utf-8 -*-

import time

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.action.block_instrument import get_block_instrument, handle_paper_tape_takeout

COMPUTER_BLOCK = "music_plus:music_plus_computer"

factory = serverApi.GetEngineCompFactory()

BLOCK_COOLDOWN_KEY = "music_plus:block_use_cooldown"


@Listen(Events.ServerBlockUseEvent)
def on_block_use(args):
    if args.get("cancel"):
        return

    block_name = args["blockName"]
    player_id = args["playerId"]

    # 空手右击电脑方块 -> 通知客户端打开 MIDI 音乐库 GUI
    if block_name == COMPUTER_BLOCK and can_use(args):
        Call(player_id, "open_computer_ui", {})
        args["cancel"] = True
        return

    # 空手右击方块乐器 -> 取出内部纸带
    if get_block_instrument(block_name) and can_use(args):
        handle_paper_tape_takeout(args)


def can_use(args):
    """
    一套自己的冷却判断机制
    """
    entity_id = args["playerId"]
    extra_data = factory.CreateModAttr(entity_id)
    timestamp = time.time()

    # 冷却时间为 0.2 秒
    if extra_data.GetAttr(BLOCK_COOLDOWN_KEY) and timestamp - extra_data.GetAttr(BLOCK_COOLDOWN_KEY) < 0.2:
        args["cancel"] = True
        return False
    else:
        extra_data.SetAttr(BLOCK_COOLDOWN_KEY, timestamp, False, False)
        return True


def record_cooldown(player_id, extra_time=0):
    """
    方块交互在物品交互之后，所以需要提供外部方法来额外阻断这个
    """
    extra_data = factory.CreateModAttr(player_id)
    timestamp = time.time() + extra_time
    extra_data.SetAttr(BLOCK_COOLDOWN_KEY, timestamp, False, False)


def record_item_use_cooldown(player_id, extra_time=0):
    """
    有时候方块交互需要禁止后面的物品交互
    """
    from music_plus_scripts.server.event.item_use import record_cooldown as item_record_cooldown
    item_record_cooldown(player_id, extra_time)
