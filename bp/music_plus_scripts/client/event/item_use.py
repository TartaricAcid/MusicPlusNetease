# -*- coding: utf-8 -*-

import time

from music_plus_scripts.QuModLibs.Client import *
from music_plus_scripts.client.action.paper_tape import is_paper_tape, test_record_midi

CACHE_TIME = -1


@Listen(Events.ClientItemUseOnEvent)
def on_item_use_on(args):
    if args.get("ret"):
        return

    block_name = args["blockName"]
    item_dict = args["itemDict"]
    item_name = item_dict["newItemName"]

    if is_paper_tape(item_name) and block_name == "minecraft:grass_block" and _can_use(args):
        test_record_midi(args)


def _can_use(args):
    """
    冷却判断机制
    """
    global CACHE_TIME
    timestamp = time.time()

    # 冷却时间为 0.2 秒
    if timestamp - CACHE_TIME < 0.2:
        args["cancel"] = True
        return False
    else:
        CACHE_TIME = timestamp
        return True
