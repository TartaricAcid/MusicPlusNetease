# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Client import *

COMPUTER_BLOCK = "music_plus:music_plus_computer"

factory = clientApi.GetEngineCompFactory()
game_comp = factory.CreateGame(levelId)


def is_computer(item_name):
    return item_name == COMPUTER_BLOCK


def on_computer_use(args):
    pass
