# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Client import clientApi, levelId, playerId
from music_plus_scripts.client.action.instrument_context import INSTRUMENT_MODE_HANDHELD, set_instrument_context
from music_plus_scripts.client.network.instrument import open_instrument_ui

HANDHELD_INSTRUMENT_TARGETS = {
    "music_plus:bass": "bass",
}
MUSICIAN_ENTITY = "music_plus:musician"

factory = clientApi.GetEngineCompFactory()
camera = factory.CreateCamera(levelId)


def is_targeting_musician():
    target_id = camera.GetChosenEntity()
    if not target_id:
        return False
    target_type = factory.CreateEngineType(target_id).GetEngineTypeStr()
    return target_type == MUSICIAN_ENTITY


def handle_handheld_instrument_try_use(args):
    if is_targeting_musician():
        return

    item_dict = args["itemDict"]
    item_name = item_dict["newItemName"]

    target_id = HANDHELD_INSTRUMENT_TARGETS.get(item_name)
    if target_id is not None:
        set_instrument_context(target_id, INSTRUMENT_MODE_HANDHELD, performer_id=playerId)
        open_instrument_ui()
        args["cancel"] = True
