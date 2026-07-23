# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Client import *
from music_plus_scripts.client.music.performance_animation import handle_remove_entity, handle_remove_player_aoi


@Listen(Events.RemovePlayerAOIClientEvent)
def on_remove_player_aoi(args):
    handle_remove_player_aoi(args)


@Listen(Events.RemoveEntityClientEvent)
def on_remove_entity(args):
    handle_remove_entity(args)
