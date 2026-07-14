# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Client import *


@AllowCall
def swing_hand(args):
    player_id = args["player_id"]

    # 仅当事人会挥手
    if player_id == clientApi.GetLocalPlayerId():
        factory = clientApi.GetEngineCompFactory()
        level_id = clientApi.GetLevelId()
        player = factory.CreatePlayer(level_id)
        player.Swing()
