# -*- coding: utf-8 -*-
from .QuModLibs.QuMod import *

MUSIC_PLUS_MOD = EasyMod()

MUSIC_PLUS_MOD.Server("server.server")
MUSIC_PLUS_MOD.Server("server.event.item_use")

MUSIC_PLUS_MOD.Client("client.client")
MUSIC_PLUS_MOD.Client("client.network.sound")
MUSIC_PLUS_MOD.Client("client.music.midi_player")
