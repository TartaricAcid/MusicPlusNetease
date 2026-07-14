# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.action.block_instrument import PAPER_TAPE_ITEM
from music_plus_scripts.server.utils.item_utils import get_mainhand_item_dict, set_mainhand_item_dict

MIDI_NBT_KEY = "midi"
NBT_STRING = 8


@AllowCall
@InjectRPCPlayerId
def write_paper_tape_midi(player_id, args):
    midi_data = args.get(MIDI_NBT_KEY)
    if midi_data is None:
        return

    item = get_mainhand_item_dict(player_id, True)
    if not item or item.get("newItemName") != PAPER_TAPE_ITEM:
        return

    user_data = item.get("userData") or {}
    if user_data.get(MIDI_NBT_KEY):
        return

    item["customTips"] = "§6已写入 MIDI 数据"
    item["userData"] = {
        "midi": {
            "__type__": 8,
            "__value__": midi_data
        }
    }

    set_mainhand_item_dict(player_id, item)
