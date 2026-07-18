# -*- coding: utf-8 -*-

import time

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.action.seat import SEAT_ENTITY, handle_seat_tick, handle_seat_stop_riding

_STOP_RIDING_COOLDOWN = {}


@Listen(Events.EntityTickServerEvent)
def on_entity_tick(args):
    if args["identifier"] == SEAT_ENTITY:
        handle_seat_tick(args)


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
