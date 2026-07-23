# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.action.instrument_playback import (
    build_entity_playback,
    stop_entity_instrument_playback,
    stop_instrument_playback,
)
from music_plus_scripts.server.action.seated_instrument import get_seated_instrument
from music_plus_scripts.server.object.entity_object import EntityObject
from music_plus_scripts.server.store.instrument_registry import get_handheld_instrument_config

factory = serverApi.GetEngineCompFactory()
mc_enum = serverApi.GetMinecraftEnum()
CARRIED = mc_enum.ItemPosType.CARRIED


def _get_item_name(item_dict):
    if not item_dict:
        return None
    return item_dict["newItemName"]


def _get_handheld_instrument(entity_id, item_dict=None):
    if item_dict is None:
        entity_type = factory.CreateEngineType(entity_id).GetEngineTypeStr()
        if entity_type == "minecraft:player":
            item_dict = factory.CreateItem(entity_id).GetPlayerItem(CARRIED, 0)
        else:
            item_dict = EntityObject(entity_id).get_mainhand_item()

    config = get_handheld_instrument_config(_get_item_name(item_dict))
    if config is None:
        return None

    result = config.copy()
    pos = factory.CreatePos(entity_id).GetPos()
    dimension = factory.CreateDimension(entity_id).GetEntityDimensionId()
    result["mode"] = "handheld"
    result.update(build_entity_playback(entity_id, pos, dimension))
    return result


def _get_seated_entity_instrument(entity_id):
    ride_comp = factory.CreateRide(entity_id)
    if not ride_comp.IsEntityRiding():
        return None
    return get_seated_instrument(ride_comp.GetEntityRider())


def get_entity_instrument(entity_id):
    seated = _get_seated_entity_instrument(entity_id)
    if seated is not None:
        return seated
    return _get_handheld_instrument(entity_id)


def get_player_instrument(player_id):
    return get_entity_instrument(player_id)


def handle_carried_item_changed(args):
    player_id = args["playerId"]
    old_instrument = _get_handheld_instrument(player_id, args["oldItemDict"])
    if old_instrument is not None:
        stop_instrument_playback(old_instrument["playback_key"])

    if _get_seated_entity_instrument(player_id) is not None:
        return

    new_instrument = _get_handheld_instrument(player_id, args["newItemDict"])
    Call(player_id, "set_instrument_context", {
        "target_id": new_instrument.get("target_id") if new_instrument else None,
        "mode": "handheld" if new_instrument else None,
        "performer_id": player_id,
    })


def handle_player_instrument_end(player_id):
    stop_entity_instrument_playback(player_id)
