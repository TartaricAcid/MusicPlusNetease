# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.action.handheld_instrument import get_entity_instrument
from music_plus_scripts.server.action.instrument_controller import open_performer_instrument_ui
from music_plus_scripts.server.action.instrument_playback import stop_instrument_playback
from music_plus_scripts.server.action.musician import (
    MUSICIAN_ENTITY,
    MUSICIAN_ITEM,
    equip_to_musician,
    unequip_from_musician,
)
from music_plus_scripts.server.object.entity_object import EntityObject
from music_plus_scripts.server.object.player_object import PlayerObject
from music_plus_scripts.server.utils.item_utils import (
    get_mainhand_item_dict,
    item_dict_is_empty,
)

MAX_INTERACT_DISTANCE_SQ = 64.0

factory = serverApi.GetEngineCompFactory()


def _validate_musician(player_id, musician_id):
    """校验音乐家实体合法性和距离。返回 (PlayerObject, EntityObject) 或 None。"""
    if musician_id is None:
        return None

    engine_type = factory.CreateEngineType(musician_id).GetEngineTypeStr()
    if engine_type != MUSICIAN_ENTITY:
        return None

    player_pos = factory.CreatePos(player_id).GetPos()
    musician_pos = factory.CreatePos(musician_id).GetPos()
    if player_pos is None or musician_pos is None:
        return None

    dist_sq = sum((player_pos[i] - musician_pos[i]) ** 2 for i in range(3))
    if dist_sq > MAX_INTERACT_DISTANCE_SQ:
        return None

    player = PlayerObject(player_id)
    if player is None:
        return None
    musician = EntityObject(musician_id)
    return player, musician


@AllowCall
@InjectRPCPlayerId
def musician_equip(player_id, args):
    result = _validate_musician(player_id, args["musician_id"])
    if result is None:
        return
    player, musician = result
    carried_item = get_mainhand_item_dict(player_id, True)
    if item_dict_is_empty(carried_item):
        player.send_tip_msg("请先手持要装备的乐器")
        return
    equip_to_musician(player, musician, args["musician_id"], carried_item)


@AllowCall
@InjectRPCPlayerId
def musician_unequip(player_id, args):
    result = _validate_musician(player_id, args["musician_id"])
    if result is None:
        return
    player, musician = result
    unequip_from_musician(player, musician, args["musician_id"])


@AllowCall
@InjectRPCPlayerId
def musician_select(player_id, args):
    result = _validate_musician(player_id, args["musician_id"])
    if result is None:
        return
    player, musician = result
    if not open_performer_instrument_ui(player_id, args["musician_id"]):
        player.send_tip_msg("请先为音乐家装备乐器")


@AllowCall
@InjectRPCPlayerId
def musician_recall(player_id, args):
    musician_id = args["musician_id"]
    result = _validate_musician(player_id, musician_id)
    if result is None:
        return
    player, musician = result

    instrument = get_entity_instrument(musician_id)
    if instrument is not None:
        stop_instrument_playback(instrument["playback_key"])

    mainhand = musician.get_mainhand_item()
    if not item_dict_is_empty(mainhand):
        player.give_item(mainhand)

    offhand = musician.get_offhand_item()
    if not item_dict_is_empty(offhand):
        player.give_item(offhand)

    player.give_item(MUSICIAN_ITEM)
    musician.destroy()
