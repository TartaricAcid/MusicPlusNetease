# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.action.block_instrument import handle_block_instrument_redstone
from music_plus_scripts.server.store.instrument_registry import get_paper_tape_instrument_config


@Listen(Events.BlockStrengthChangedServerEvent)
def on_block_strength_changed(args):
    block_name = args["blockName"]

    instrument = get_paper_tape_instrument_config(block_name)
    if instrument:
        handle_block_instrument_redstone(args, instrument)
