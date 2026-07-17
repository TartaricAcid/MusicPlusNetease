# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.action.seat import SEAT_ENTITY, handle_seat_tick, is_seat, handle_seat_start_riding, handle_seat_stop_riding


@Listen(Events.EntityTickServerEvent)
def on_entity_tick(args):
    if args["identifier"] == SEAT_ENTITY:
        handle_seat_tick(args)


@Listen(Events.EntityStartRidingEvent)
def on_entity_start_riding(args):
    ride_id = args["rideId"]
    if is_seat(ride_id):
        handle_seat_start_riding(args)


@Listen(Events.EntityStopRidingEvent)
def on_entity_stop_riding(args):
    ride_id = args["rideId"]
    if is_seat(ride_id):
        handle_seat_stop_riding(args)
