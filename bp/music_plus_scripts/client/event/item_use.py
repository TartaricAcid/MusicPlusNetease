# -*- coding: utf-8 -*-

import time

from music_plus_scripts.QuModLibs.Client import *
from music_plus_scripts.client.action.handheld_instrument import handle_handheld_instrument_try_use, HANDHELD_INSTRUMENT_TARGETS
from music_plus_scripts.client.action.multiblock import check_multiblock_instrument_place

CACHE_TIME = -1


@Listen(Events.ClientItemUseOnEvent)
def on_item_use_on(args):
    if args["ret"]:
        return

    if check_multiblock_instrument_place(args) and can_use(args):
        return


@Listen(Events.ClientItemTryUseEvent)
def on_item_try_use(args):
    if args["cancel"]:
        return

    item_dict = args["itemDict"]
    item_name = item_dict["newItemName"]

    if item_name in HANDHELD_INSTRUMENT_TARGETS and can_use(args):
        handle_handheld_instrument_try_use(args)


def can_use(args, cool_time=0.2):
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
