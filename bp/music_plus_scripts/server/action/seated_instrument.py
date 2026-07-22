# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.action.instrument_playback import build_block_playback
from music_plus_scripts.server.object.block_object import BlockObject
from music_plus_scripts.server.object.block_use_object import BlockUseObject
from music_plus_scripts.utils.direction import aux_to_direction, direction_to_rot

factory = serverApi.GetEngineCompFactory()
block_info = factory.CreateBlockInfo(levelId)


def handle_seated_instrument_use(args, instrument_config, block_pos=None, block_aux=None):
    from music_plus_scripts.server.action.seat import (
        SEAT_ENTITY,
        configure_seat,
        get_block_seat_id,
        is_seat,
        set_block_seat_id,
    )

    use_obj = BlockUseObject(args)
    if not use_obj.get_item().is_empty():
        return False

    if block_pos is None:
        block_pos = use_obj.get_pos()
    if block_aux is None:
        block_aux = use_obj.aux
    face = aux_to_direction(block_aux)
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

    seat_pos = _get_seat_pos(block_pos, face, instrument_config["seat_offset"])
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

    factory.CreateRide(seat_id).SetRiderRideEntity(use_obj.get_player_id(), seat_id)
    use_obj.swing_hand()
    return True


def remove_seated_instrument_seat(args):
    block = BlockObject(args)
    remove_seated_instrument_at(block.get_pos(), block.get_dimension())


def remove_seated_instrument_at(block_pos, dimension):
    from music_plus_scripts.server.action.instrument_playback import stop_instrument_playback
    from music_plus_scripts.server.action.seat import get_block_seat_id, remove_seat

    playback = build_block_playback(block_pos, dimension)
    stop_instrument_playback(playback["playback_key"])
    seat_id = get_block_seat_id(dimension, block_pos)
    if seat_id is not None:
        remove_seat(seat_id)


def get_seated_instrument(seat_id):
    from music_plus_scripts.server.action.seat import get_seat_block_data, is_seat
    from music_plus_scripts.server.store.instrument_registry import get_seated_instrument_config

    if not seat_id or not is_seat(seat_id):
        return None

    block_data = get_seat_block_data(seat_id)
    if block_data is None:
        return None

    x, y, z, dimension = block_data
    block = block_info.GetBlockNew((x, y, z), dimension)
    if block is None:
        return None

    instrument_config = get_seated_instrument_config(block.get("name"))
    if instrument_config is None:
        return None

    result = instrument_config.copy()
    result["pos"] = (x, y, z)
    result["dimension"] = dimension
    result.update(build_block_playback(result["pos"], dimension))
    return result


def _get_seat_pos(block_pos, face, seat_offset):
    x, y, z = block_pos
    lateral, vertical, forward = seat_offset
    center_x = x + 0.5
    center_z = z + 0.5

    if face == "north":
        return center_x + lateral, y + vertical, center_z + forward
    if face == "south":
        return center_x - lateral, y + vertical, center_z - forward
    if face == "west":
        return center_x + forward, y + vertical, center_z - lateral
    if face == "east":
        return center_x - forward, y + vertical, center_z + lateral
    return center_x, y + vertical, center_z
