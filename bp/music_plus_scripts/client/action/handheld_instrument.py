# -*- coding: utf-8 -*-

from music_plus_scripts.client.action.instrument_context import INSTRUMENT_MODE_HANDHELD, set_instrument_context
from music_plus_scripts.client.network.instrument import open_instrument_ui

HANDHELD_INSTRUMENT_TARGETS = {
    "music_plus:music_plus_bass": "bass",
}


def handle_handheld_instrument_try_use(args):
    item_dict = args["itemDict"]
    item_name = item_dict["newItemName"]

    target_id = HANDHELD_INSTRUMENT_TARGETS.get(item_name)
    if target_id is not None:
        set_instrument_context(target_id, INSTRUMENT_MODE_HANDHELD)
        open_instrument_ui()
        args["cancel"] = True
