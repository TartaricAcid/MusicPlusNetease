# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.action.seated_instrument import get_instrument_seat_pos, get_seated_instrument
from music_plus_scripts.server.store.instrument_registry import get_seated_instrument_config
from music_plus_scripts.server.utils.block_utils import be_data_fix
from music_plus_scripts.utils.direction import aux_to_direction, direction_to_rot

SEAT_ENTITY = "music_plus:seat"
SEAT_BLOCK_DATA_ATTR = "music_plus:seat_block_data"
SEAT_INSTRUMENT_BLOCK_ATTR = "music_plus:seat_instrument_block"
SEAT_INSTRUMENT_TARGET_ATTR = "music_plus:seat_instrument_target"
SEAT_VIEW_YAW_ATTR = "music_plus:seat_view_yaw"
SEAT_BLOCK_DIRECTION_ATTR = "music_plus:seat_block_direction"
SEAT_ENTITY_ID_KEY = "music_plus:seat_entity_id"
PERFORMER_SEAT_BLOCK_EXTRA_KEY = "music_plus:performer_seat_block"

factory = serverApi.GetEngineCompFactory()
block_info = factory.CreateBlockInfo(levelId)
block_entity_data = factory.CreateBlockEntityData(levelId)


def configure_seat(
        seat_id,
        block_pos,
        dimension,
        instrument_block,
        instrument_target,
        view_yaw,
        block_direction,
):
    x, y, z = block_pos
    mod_attr = factory.CreateModAttr(seat_id)
    mod_attr.SetAttr(
        SEAT_BLOCK_DATA_ATTR,
        [x, y, z, dimension],
        True
    )
    mod_attr.SetAttr(SEAT_INSTRUMENT_BLOCK_ATTR, instrument_block, True)
    mod_attr.SetAttr(SEAT_INSTRUMENT_TARGET_ATTR, instrument_target, True)
    mod_attr.SetAttr(SEAT_VIEW_YAW_ATTR, view_yaw, True)
    mod_attr.SetAttr(SEAT_BLOCK_DIRECTION_ATTR, block_direction, True)


def get_seat_block_data(seat_id):
    block_data = factory.CreateModAttr(seat_id).GetAttr(SEAT_BLOCK_DATA_ATTR)
    if not block_data or len(block_data) != 4:
        return None
    return block_data


def get_seat_instrument_block(seat_id):
    return factory.CreateModAttr(seat_id).GetAttr(SEAT_INSTRUMENT_BLOCK_ATTR)


def get_seat_block_direction(seat_id):
    return factory.CreateModAttr(seat_id).GetAttr(SEAT_BLOCK_DIRECTION_ATTR)


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


def save_performer_seat_block(performer_id, seat_id):
    block_data = get_seat_block_data(seat_id)
    if block_data is None:
        return
    factory.CreateExtraData(performer_id).SetExtraData(
        PERFORMER_SEAT_BLOCK_EXTRA_KEY,
        list(block_data),
    )


def restore_performer_seat(performer_id):
    block_data = factory.CreateExtraData(performer_id).GetExtraData(
        PERFORMER_SEAT_BLOCK_EXTRA_KEY
    )

    # 没有此 extra data，那么就是创建新实体时，此处不处理恢复问题
    if not block_data or len(block_data) != 4:
        return False

    x, y, z, dimension = block_data
    block_pos = (x, y, z)
    seat_id = get_block_seat_id(dimension, block_pos)

    # 座位实体丢失时，根据乐器方块重新创建。
    if seat_id is None or not is_seat(seat_id):
        block = block_info.GetBlockNew(block_pos, dimension)
        if block is None:
            return False
        instrument_block = block["name"]
        instrument_config = get_seated_instrument_config(instrument_block)
        if instrument_config is None:
            factory.CreateExtraData(performer_id).CleanExtraData(
                PERFORMER_SEAT_BLOCK_EXTRA_KEY
            )
            return False

        face = aux_to_direction(block["aux"])
        view_yaw = direction_to_rot(face) - 180
        seat_pos = get_instrument_seat_pos(
            block_pos,
            face,
            instrument_config["seat_offset"],
        )
        seat_id = System.CreateEngineEntityByTypeStr(
            SEAT_ENTITY,
            seat_pos,
            (0, view_yaw),
            dimension,
            True,
        )
        if seat_id is None:
            return False
        configure_seat(
            seat_id,
            block_pos,
            dimension,
            instrument_block,
            instrument_config["target_id"],
            view_yaw,
            face,
        )
        set_block_seat_id(dimension, block_pos, seat_id)

    ride_comp = factory.CreateRide(seat_id)
    if len(ride_comp.GetRiders()) > 0:
        return False

    if not ride_comp.SetRiderRideEntity(performer_id, seat_id):
        return False

    view_yaw = factory.CreateModAttr(seat_id).GetAttr(SEAT_VIEW_YAW_ATTR)
    factory.CreateRot(performer_id).SetRot((0, view_yaw))
    return True


def remove_seat(seat_id):
    for rider in factory.CreateRide(seat_id).GetRiders():
        rider_id = rider.get("entityId")
        factory.CreateExtraData(rider_id).CleanExtraData(PERFORMER_SEAT_BLOCK_EXTRA_KEY)

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
    from music_plus_scripts.server.action.instrument_playback import stop_instrument_playback
    ride_id = args["rideId"]
    instrument = get_seated_instrument(ride_id)

    if instrument is not None:
        stop_instrument_playback(instrument["playback_key"])
        remove_seat(ride_id)
        return

    if is_seat(ride_id):
        remove_seat(ride_id)
