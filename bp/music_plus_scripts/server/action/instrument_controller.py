# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.action.handheld_instrument import get_entity_instrument

CONTROLLED_PERFORMER_ATTR = "music_plus:controlled_instrument_performer"
MAX_CONTROL_DISTANCE_SQ = 64.0

factory = serverApi.GetEngineCompFactory()


def open_performer_instrument_ui(player_id, performer_id):
    performer_type = factory.CreateEngineType(performer_id).GetEngineTypeStr()
    if performer_id != player_id and performer_type == "minecraft:player":
        return False

    instrument = get_entity_instrument(performer_id)
    if instrument is None:
        return False

    factory.CreateModAttr(player_id).SetAttr(
        CONTROLLED_PERFORMER_ATTR,
        performer_id,
        False,
        False,
    )
    Call(player_id, "set_instrument_context", {
        "target_id": instrument["target_id"],
        "mode": instrument["mode"],
        "view_yaw": instrument.get("view_yaw"),
        "performer_id": performer_id,
    })
    Call(player_id, "open_instrument_ui", {})
    return True


def get_request_performer(player_id, requested_performer_id):
    if requested_performer_id is None:
        return None
    if requested_performer_id == player_id:
        return player_id

    controlled_id = factory.CreateModAttr(player_id).GetAttr(CONTROLLED_PERFORMER_ATTR)
    if controlled_id != requested_performer_id:
        return None

    player_dimension = factory.CreateDimension(player_id).GetEntityDimensionId()
    performer_dimension = factory.CreateDimension(requested_performer_id).GetEntityDimensionId()
    if player_dimension != performer_dimension:
        return None

    player_pos = factory.CreatePos(player_id).GetPos()
    performer_pos = factory.CreatePos(requested_performer_id).GetPos()
    if player_pos is None or performer_pos is None:
        return None
    distance_sq = sum(
        (player_pos[index] - performer_pos[index]) ** 2
        for index in range(3)
    )
    if distance_sq > MAX_CONTROL_DISTANCE_SQ:
        return None
    return requested_performer_id
