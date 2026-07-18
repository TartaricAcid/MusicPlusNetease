# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.action.seated_instrument import get_seated_instrument
from music_plus_scripts.server.utils.block_utils import be_data_fix

SEAT_ENTITY = "music_plus:seat"
SEAT_BLOCK_DATA_ATTR = "music_plus:seat_block_data"
SEAT_ENTITY_ID_KEY = "music_plus:seat_entity_id"

factory = serverApi.GetEngineCompFactory()
block_info = factory.CreateBlockInfo(levelId)
block_entity_data = factory.CreateBlockEntityData(levelId)


def configure_seat(seat_id, block_pos, dimension):
    x, y, z = block_pos
    factory.CreateModAttr(seat_id).SetAttr(
        SEAT_BLOCK_DATA_ATTR,
        [x, y, z, dimension],
        True
    )


def get_seat_block_data(seat_id):
    block_data = factory.CreateModAttr(seat_id).GetAttr(SEAT_BLOCK_DATA_ATTR)
    if not block_data or len(block_data) != 4:
        return None
    return block_data


def get_block_seat_id(dimension, block_pos):
    be_data = block_entity_data.GetBlockEntityData(dimension, block_pos)
    if be_data is None:
        return None
    return be_data[SEAT_ENTITY_ID_KEY]


def set_block_seat_id(dimension, block_pos, seat_id):
    be_data = block_entity_data.GetBlockEntityData(dimension, block_pos)
    if be_data is None:
        be_data = {}
    be_data[SEAT_ENTITY_ID_KEY] = seat_id
    block_info.SetBlockEntityData(dimension, block_pos, be_data_fix(be_data))


def remove_seat(seat_id):
    block_data = get_seat_block_data(seat_id)
    if block_data is not None:
        x, y, z, dimension = block_data
        block_pos = (x, y, z)
        be_data = block_entity_data.GetBlockEntityData(dimension, block_pos)
        if be_data is not None:
            be_data[SEAT_ENTITY_ID_KEY] = None
            block_info.SetBlockEntityData(dimension, block_pos, be_data_fix(be_data))
    DestroyEntity(seat_id)


def is_seat(entity_id):
    return factory.CreateEngineType(entity_id).GetEngineTypeStr() == SEAT_ENTITY


def handle_seat_tick(args):
    seat_id = args["entityId"]
    if len(factory.CreateRide(seat_id).GetRiders()) <= 0:
        remove_seat(seat_id)


def handle_seat_stop_riding(args):
    ride_id = args["rideId"]
    player_id = args["id"]

    instrument = get_seated_instrument(ride_id)
    if instrument is not None:
        Call("*", "stop_player_piano_animation", {"player_id": player_id})
        Call("*", "stop_music_at_pos", {"pos": instrument["pos"]})
        remove_seat(ride_id)
        return

    if is_seat(ride_id):
        remove_seat(ride_id)
