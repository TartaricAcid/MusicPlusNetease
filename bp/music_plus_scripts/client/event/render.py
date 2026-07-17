# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Client import *
from music_plus_scripts.client.music.piano_animation import handle_remove_player_aoi


@Listen(Events.RemovePlayerAOIClientEvent)
def on_remove_player_aoi(args):
    handle_remove_player_aoi(args)
