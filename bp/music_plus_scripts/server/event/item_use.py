# -*- coding: utf-8 -*-

import time

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.action.block_instrument import is_paper_tape, get_block_instrument, handle_paper_tape_insert

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

    # 纸带右击方块乐器 → 塞入并播放曲目
    if is_paper_tape(item_name) and get_block_instrument(block_name) and can_use(args):
        instrument = get_block_instrument(block_name)
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
