# -*- coding: utf-8 -*-

import time

from music_plus_scripts.QuModLibs.Client import *

CACHE_TIME = -1


@Listen(Events.ClientItemUseOnEvent)
def on_item_use_on(args):
    if args.get("ret"):
        return

    block_name = args["blockName"]
    item_dict = args["itemDict"]
    item_name = item_dict["newItemName"]

    pass


def _can_use(args, cool_time=0.2):
    """
    冷却判断机制
    """
    global CACHE_TIME
    timestamp = time.time()

    # 冷却时间为 cool_time 秒
    if timestamp - CACHE_TIME < cool_time:
        args["cancel"] = True
        return False
    else:
        CACHE_TIME = timestamp
        return True
