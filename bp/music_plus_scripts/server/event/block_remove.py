# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.action.block_instrument import get_block_instrument, handle_block_instrument_remove


@Listen(Events.BlockRemoveServerEvent)
def on_block_remove(args):
    block_name = args["fullName"]
    if get_block_instrument(block_name):
        handle_block_instrument_remove(args)
