# -*- coding: utf-8 -*-

import time

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.action.music_box import is_paper_tape, is_music_box, handle_music_box_play

factory = serverApi.GetEngineCompFactory()

ITEM_COOLDOWN_KEY = "music_plus:item_use_cooldown"


@Listen(Events.ServerItemUseOnEvent)
def on_item_use_on_block(args):
    if args.get("ret"):
        return

    item = args.get("itemDict") or {}
    item_name = item.get("newItemName", "")
    block_name = args.get("blockName", "")

    # 纸带右击音乐盒 → 播放曲目
    if is_paper_tape(item_name) and is_music_box(block_name) and can_use(args):
        handle_music_box_play(args)
        args["ret"] = True


def can_use(args):
    """通用冷却检查，防止短时间内重复触发。"""
    player_id = args["entityId"]
    mod_attr = factory.CreateModAttr(player_id)
    now = time.time()
    last = mod_attr.GetAttr(ITEM_COOLDOWN_KEY)
    if last and now - last < 1.0:
        args["ret"] = True
        return False
    mod_attr.SetAttr(ITEM_COOLDOWN_KEY, now, False, False)
    return True
