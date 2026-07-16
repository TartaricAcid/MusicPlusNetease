# -*- coding: utf-8 -*-

import time

from music_plus_scripts.QuModLibs.Client import *
from music_plus_scripts.client.action.computer import is_computer_block, open_computer_ui
from music_plus_scripts.client.action.paper_tape import is_paper_tape, test_record_midi

CACHE_TIME = -1


@Listen(Events.ClientItemUseOnEvent)
def on_item_use_on(args):
    if args.get("ret"):
        return

    block_name = args["blockName"]
    item_dict = args["itemDict"]
    item_name = item_dict["newItemName"]

    if is_paper_tape(item_name) and block_name == "minecraft:grass_block" and _can_use(args, 2):
        test_record_midi(args)
        return

    # 手持任意物品右键电脑方块 → 打开 MIDI 音乐库 GUI
    if is_computer_block(block_name) and _can_use(args, 0.5):
        open_computer_ui()
        args["ret"] = True


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
