# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Client import *
from music_plus_scripts.client.music.midi_player import on_music_tick


@Listen(Events.GameRenderTickEvent)
def on_game_render_tick(args):
    on_music_tick()
