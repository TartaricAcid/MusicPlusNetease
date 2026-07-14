# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Client import *
from music_plus_scripts.client.music.midi_player import on_music_tick


@Listen(Events.OnScriptTickClient)
def on_script_tick():
    on_music_tick()
