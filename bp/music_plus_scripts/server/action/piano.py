# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.action.seat import (
    SEAT_ENTITY,
    configure_seat,
    get_block_seat_id,
    is_seat,
    remove_seat,
    set_block_seat_id,
)
from music_plus_scripts.server.object.block_object import BlockObject
from music_plus_scripts.server.object.block_use_object import BlockUseObject
from music_plus_scripts.utils.direction import direction_to_rot, aux_to_direction

factory = serverApi.GetEngineCompFactory()


def handle_piano_use(args):
    use_obj = BlockUseObject(args)
    if not use_obj.get_item().is_empty():
        return False

    face = aux_to_direction(use_obj.aux)
    block_pos = use_obj.get_pos()
    dimension = use_obj.get_dimension()
    seat_id = get_block_seat_id(dimension, block_pos)

    if seat_id is not None and is_seat(seat_id):
        ride_comp = factory.CreateRide(seat_id)
        if len(ride_comp.GetRiders()) > 0:
            return False
        ride_comp.SetRiderRideEntity(use_obj.get_player_id(), seat_id)
        use_obj.swing_hand()
        return True

    if seat_id is not None:
        set_block_seat_id(dimension, block_pos, None)

    seat_pos = _get_seat_pos(use_obj.get_pos(), face)

    seat_id = use_obj.create_entity(
        SEAT_ENTITY,
        seat_pos,
        (0, direction_to_rot(face) - 180),
        True,
        False,
    )
    if seat_id is None:
        return False

    configure_seat(seat_id, block_pos, dimension)
    set_block_seat_id(dimension, block_pos, seat_id)

    ride_comp = factory.CreateRide(seat_id)
    ride_comp.SetRiderRideEntity(use_obj.get_player_id(), seat_id)
    use_obj.swing_hand()
    return True


def remove_piano_seat(args):
    block = BlockObject(args)
    x, y, z = block.get_pos()
    Call("*", "stop_music_at_pos", {"pos": (x, y, z)})
    seat_id = get_block_seat_id(block.get_dimension(), block.get_pos())
    if seat_id is None:
        return
    remove_seat(seat_id)


def _get_seat_pos(block_pos, face):
    x, y, z = block_pos
    if face == "north":
        return x + 0.5, y, z + 2.875
    if face == "south":
        return x + 0.5, y, z - 1.875
    if face == "west":
        return x + 2.875, y, z + 0.5
    if face == "east":
        return x - 1.875, y, z + 0.5
    return x, y, z
