# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.action.handheld_instrument import (
    handle_carried_item_changed,
    handle_player_instrument_end,
)


@Listen(Events.OnCarriedNewItemChangedServerEvent)
def on_carried_item_changed(args):
    handle_carried_item_changed(args)


@Listen(Events.PlayerDieEvent)
def on_player_die(args):
    handle_player_instrument_end(args["id"])


@Listen(Events.DelServerPlayerEvent)
def on_player_removed(args):
    handle_player_instrument_end(args["id"])
