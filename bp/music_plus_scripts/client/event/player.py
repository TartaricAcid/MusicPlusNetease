# -*- coding: utf-8 -*-

import time

from music_plus_scripts.QuModLibs.Client import *
from music_plus_scripts.client.action.instrument_context import (
    INSTRUMENT_MODE_HANDHELD,
    INSTRUMENT_MODE_SEATED,
    set_instrument_context,
)
from music_plus_scripts.client.network.instrument import open_instrument_ui

SEAT_ENTITY = "music_plus:seat"
SEAT_INSTRUMENT_TARGET_ATTR = "music_plus:seat_instrument_target"
SEAT_VIEW_YAW_ATTR = "music_plus:seat_view_yaw"

# 脱离骑乘的事件居然会一口气触发 50 次，故还需要做个冷却判断
_STOP_RIDING_COOLDOWN = {}

factory = clientApi.GetEngineCompFactory()
player_comp = factory.CreatePlayer(playerId)
ride_comp = factory.CreateRide(playerId)
item_comp = factory.CreateItem(playerId)


def is_music_plus_seat(entity_id):
    if not entity_id:
        return False
    return factory.CreateEngineType(entity_id).GetEngineTypeStr() == SEAT_ENTITY


def get_seat_instrument_target(entity_id):
    return factory.CreateModAttr(entity_id).GetAttr(SEAT_INSTRUMENT_TARGET_ATTR)


def get_seat_view_yaw(entity_id):
    return factory.CreateModAttr(entity_id).GetAttr(SEAT_VIEW_YAW_ATTR)


def stop_riding_on_cooldown(ride_id):
    now = time.time()

    # 如果在冷却时间内，那么不触发
    last_time = _STOP_RIDING_COOLDOWN.get(ride_id)  # type: int
    if last_time is not None and now - last_time < 0.5:
        return True

    _STOP_RIDING_COOLDOWN[ride_id] = now

    # 清除老旧缓存
    for cached_ride_id in list(_STOP_RIDING_COOLDOWN.keys()):
        if now - _STOP_RIDING_COOLDOWN[cached_ride_id] > 1:
            del _STOP_RIDING_COOLDOWN[cached_ride_id]
        else:
            break

    return False


@Listen(Events.StartRidingClientEvent)
def on_start_riding(args):
    # 当骑乘者是玩家自己时才能触发逻辑
    if args["actorId"] != playerId:
        return

    # 如果骑乘的是乐器座椅
    victim_id = args["victimId"]
    is_seat = is_music_plus_seat(victim_id)
    if is_seat:
        set_instrument_context(
            get_seat_instrument_target(victim_id),
            INSTRUMENT_MODE_SEATED,
            get_seat_view_yaw(victim_id),
        )
    else:
        set_instrument_context(None)


@Listen(Events.EntityStopRidingEvent)
def on_stop_riding(args):
    # 当骑乘者是玩家自己时才能触发逻辑
    if args["id"] != playerId:
        return

    # 脱离时会多次触发，需要判断冷却时间
    ride_id = args["rideId"]
    if stop_riding_on_cooldown(ride_id):
        return

    set_instrument_context(None)


@Listen(Events.RightClickBeforeClientEvent)
def on_right_click(args):
    if not player_comp.isRiding():
        return

    seat_id = ride_comp.GetEntityRider()
    if not is_music_plus_seat(seat_id):
        return

    args["cancel"] = True
    open_instrument_ui()


@Listen(Events.LoadClientAddonScriptsAfter)
def on_scripts_loaded(args):
    seat_id = ride_comp.GetEntityRider()
    if player_comp.isRiding() and is_music_plus_seat(seat_id):
        set_instrument_context(
            get_seat_instrument_target(seat_id),
            INSTRUMENT_MODE_SEATED,
            get_seat_view_yaw(seat_id),
        )
        return

    item_dict = item_comp.GetCarriedItem()
    item_name = item_dict["newItemName"] if item_dict else None
    if item_name == "music_plus:music_plus_bass":
        set_instrument_context("bass", INSTRUMENT_MODE_HANDHELD)
    else:
        set_instrument_context(None)
