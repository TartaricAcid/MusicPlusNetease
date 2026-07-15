# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.action.block_instrument import get_block_instrument, handle_block_instrument_redstone


@Listen(Events.BlockStrengthChangedServerEvent)
def on_block_strength_changed(args):
    block_name = args["blockName"]
    instrument = get_block_instrument(block_name)
    if instrument:
        handle_block_instrument_redstone(args, instrument)
