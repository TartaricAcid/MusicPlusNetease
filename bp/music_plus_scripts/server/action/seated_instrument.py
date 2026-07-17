# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Server import *

factory = serverApi.GetEngineCompFactory()
block_info = factory.CreateBlockInfo(levelId)


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
    return result
