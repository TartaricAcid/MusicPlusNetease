# -*- coding: utf-8 -*-

import time

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.action.handheld_instrument import get_entity_instrument
from music_plus_scripts.server.action.instrument_playback import stop_instrument_playback
from music_plus_scripts.server.action.musician import (
    MUSICIAN_ENTITY,
    handle_attack,
    handle_interact,
)
from music_plus_scripts.server.action.seat import (
    SEAT_ENTITY,
    handle_seat_stop_riding,
    handle_seat_tick,
    restore_performer_seat,
)

_STOP_RIDING_COOLDOWN = {}
factory = serverApi.GetEngineCompFactory()


@Listen(Events.EntityTickServerEvent)
def on_entity_tick(args):
    if args["identifier"] == SEAT_ENTITY:
        handle_seat_tick(args)


@Listen(Events.AddEntityServerEvent)
def on_entity_added(args):
    if args["engineTypeStr"] == MUSICIAN_ENTITY:
        restore_performer_seat(args["id"])


@Listen("PlayerDoInteractServerEvent")
def on_player_interact(args):
    entity_type = factory.CreateEngineType(args["interactEntityId"]).GetEngineTypeStr()
    if entity_type == MUSICIAN_ENTITY:
        handle_interact(args)


@Listen(Events.PlayerAttackEntityEvent)
def on_player_attack(args):
    entity_type = factory.CreateEngineType(args["victimId"]).GetEngineTypeStr()
    if entity_type == MUSICIAN_ENTITY:
        handle_attack(args)


@Listen(Events.EntityDieLoottableServerEvent)
def on_entity_die_loot(args):
    entity_id = args["dieEntityId"]
    entity_type = factory.CreateEngineType(entity_id).GetEngineTypeStr()
    if entity_type != MUSICIAN_ENTITY:
        return
    instrument = get_entity_instrument(entity_id)
    if instrument is not None:
        stop_instrument_playback(instrument["playback_key"])


@Listen(Events.EntityStopRidingEvent)
def on_entity_stop_riding(args):
    ride_id = args["rideId"]
    if stop_riding_on_cooldown(ride_id):
        return

    handle_seat_stop_riding(args)


def stop_riding_on_cooldown(ride_id):
    now = time.time()
    last_time = _STOP_RIDING_COOLDOWN.get(ride_id)  # type: int
    if last_time is not None and now - last_time < 0.5:
        return True

    _STOP_RIDING_COOLDOWN[ride_id] = now
    for cached_ride_id in list(_STOP_RIDING_COOLDOWN.keys()):
        if now - _STOP_RIDING_COOLDOWN[cached_ride_id] > 1:
            del _STOP_RIDING_COOLDOWN[cached_ride_id]
        else:
            break

    return False
