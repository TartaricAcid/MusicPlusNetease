# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.action.block_instrument import handle_block_instrument_remove
from music_plus_scripts.server.action.seated_instrument import remove_seated_instrument_seat
from music_plus_scripts.server.store.instrument_registry import (
    get_paper_tape_instrument_config,
    get_seated_instrument_config,
)


@Listen(Events.BlockRemoveServerEvent)
def on_block_remove(args):
    block_name = args["fullName"]

    if get_seated_instrument_config(block_name):
        remove_seated_instrument_seat(args)
        return

    if get_paper_tape_instrument_config(block_name):
        handle_block_instrument_remove(args)
