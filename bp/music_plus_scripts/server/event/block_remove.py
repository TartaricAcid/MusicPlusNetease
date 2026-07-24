# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.action.block_instrument import handle_block_instrument_remove
from music_plus_scripts.server.action.multiblock import (
    handle_multiblock_destroyed,
    handle_multiblock_remove,
    handle_multiblock_try_destroy,
)
from music_plus_scripts.server.action.podium import PODIUM_BLOCK, stop_podium_ensemble
from music_plus_scripts.server.action.seated_instrument import remove_seated_instrument_seat
from music_plus_scripts.server.store.instrument_registry import (
    get_paper_tape_instrument_config,
    get_seated_instrument_config,
)


@Listen(Events.ServerPlayerTryDestroyBlockEvent)
def on_try_destroy_block(args):
    if args["cancel"]:
        return

    handle_multiblock_try_destroy(args)


@Listen(Events.DestroyBlockEvent)
def on_destroy_block(args):
    handle_multiblock_destroyed(args)


@Listen(Events.BlockRemoveServerEvent)
def on_block_remove(args):
    if handle_multiblock_remove(args):
        return

    block_name = args["fullName"]

    if block_name == PODIUM_BLOCK:
        stop_podium_ensemble(
            (args["x"], args["y"], args["z"]),
            args["dimension"],
        )
        return

    if get_seated_instrument_config(block_name):
        remove_seated_instrument_seat(args)
        return

    if get_paper_tape_instrument_config(block_name):
        handle_block_instrument_remove(args)
