# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Server import Call, serverApi
from music_plus_scripts.server.action.handheld_instrument import get_entity_instrument
from music_plus_scripts.server.action.instrument_controller import open_performer_instrument_ui
from music_plus_scripts.server.action.instrument_playback import stop_instrument_playback
from music_plus_scripts.server.action.seated_instrument import (
    prepare_instrument_seat,
    seat_performer,
)
from music_plus_scripts.server.object.entity_object import EntityObject
from music_plus_scripts.server.object.item_use_block_object import ItemUseBlockObject
from music_plus_scripts.server.object.player_object import PlayerObject
from music_plus_scripts.server.store.instrument_registry import get_handheld_instrument_config
from music_plus_scripts.server.utils.item_utils import (
    copy_with_count,
    get_mainhand_item_dict,
    item_dict_is_empty,
)

MUSICIAN_ENTITY = "music_plus:musician"
MUSICIAN_ITEM = "music_plus:musician"

factory = serverApi.GetEngineCompFactory()


def _get_item_name(item_dict):
    if item_dict is None:
        return None
    return item_dict.get("newItemName")


def handle_interact(args):
    player_id = args["playerId"]
    musician_id = args["interactEntityId"]
    player = PlayerObject(player_id)
    musician = EntityObject(musician_id)
    carried_item = get_mainhand_item_dict(player_id, True)

    if item_dict_is_empty(carried_item):
        open_performer_instrument_ui(player_id, musician_id)
        return
    if get_handheld_instrument_config(_get_item_name(carried_item)) is None:
        return

    old_item = musician.get_mainhand_item()
    if not musician.set_mainhand_item(copy_with_count(carried_item, 1)):
        return
    old_instrument = get_handheld_instrument_config(_get_item_name(old_item))
    if old_instrument is not None:
        stop_instrument_playback("entity:{}".format(musician_id))
    player.reduce_carried_item(1)
    if not item_dict_is_empty(old_item):
        player.give_item(old_item)
    Call(player_id, "set_instrument_context", {
        "target_id": None,
        "mode": None,
        "performer_id": player_id,
    })


def handle_attack(args):
    if args["cancel"]:
        return

    musician = EntityObject(args["victimId"])
    instrument = get_entity_instrument(args["victimId"])
    if instrument is not None:
        stop_instrument_playback(instrument["playback_key"])
    equipped_item = musician.get_mainhand_item()
    if not item_dict_is_empty(equipped_item):
        musician.drop_item(equipped_item)
    musician.drop_item(MUSICIAN_ITEM)
    musician.destroy()


def handle_item_use(args, instrument_config=None, block_pos=None, block_aux=None, instrument_block=None):
    use_obj = ItemUseBlockObject(args)
    if instrument_config is not None:
        seat_data = prepare_instrument_seat(
            args,
            instrument_config,
            block_pos,
            block_aux,
            instrument_block,
        )
        if seat_data is False:
            use_obj.get_player().send_tip_msg("该乐器已经有演奏者了")
            use_obj.cancel()
            return
        if seat_data is None:
            use_obj.cancel()
            return

        seat_id, view_yaw, created = seat_data
        seat_pos = factory.CreatePos(seat_id).GetPos()
        musician_id = use_obj.create_entity(
            MUSICIAN_ENTITY,
            seat_pos,
            (0, view_yaw),
            False,
            False,
        )
        if musician_id is None:
            if created:
                from music_plus_scripts.server.action.seat import remove_seat
                remove_seat(seat_id)
            return

        seat_performer(musician_id, seat_id, view_yaw)
        use_obj.reduce_player_item(1)
        use_obj.play_sound_and_swing_hand("random.pop")
        use_obj.cancel()
        return

    if use_obj.is_replaceable():
        spawn_pos = use_obj.offset_pos(0.5, 0, 0.5)
    else:
        adjacent = use_obj.get_adjacent_block_pos()
        if not use_obj.is_replaceable(use_obj.get_offset_block_name(adjacent)):
            use_obj.get_player().send_tip_msg("无法放置音乐家，空间不足")
            use_obj.cancel()
            return
        spawn_pos = (
            use_obj.x + adjacent[0] + 0.5,
            use_obj.y + adjacent[1],
            use_obj.z + adjacent[2] + 0.5,
        )

    player_rot = use_obj.get_player().get_relative_rot()
    musician_id = use_obj.create_entity(
        MUSICIAN_ENTITY,
        spawn_pos,
        (0, player_rot[1]),
        False,
        False,
    )
    if musician_id is not None:
        use_obj.reduce_player_item(1)
        use_obj.play_sound_and_swing_hand("dig.grass")
    use_obj.cancel()
