# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Client import *
from music_plus_scripts.client.music.performance_animation import register_queries


@Listen(Events.LoadClientAddonScriptsAfter)
def on_scripts_loaded(args):
    register_queries()
