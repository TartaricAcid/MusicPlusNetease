# -*- coding: utf-8 -*-

from music_plus_scripts.server.object.entity_object import EntityObject
from music_plus_scripts.server.object.player_object import PlayerObject
from music_plus_scripts.server.store.instrument_registry import get_handheld_instrument_config
from music_plus_scripts.server.utils.item_utils import (
    copy_with_count,
    get_mainhand_item_dict,
    item_dict_is_empty,
)


MUSICIAN_ENTITY = "music_plus:musician"


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
        return
    if get_handheld_instrument_config(_get_item_name(carried_item)) is None:
        return

    old_item = musician.get_mainhand_item()
    if not musician.set_mainhand_item(copy_with_count(carried_item, 1)):
        return
    player.reduce_carried_item(1)
    if not item_dict_is_empty(old_item):
        player.give_item(old_item)


def handle_attack(args):
    if args["cancel"]:
        return

    musician = EntityObject(args["victimId"])
    equipped_item = musician.get_mainhand_item()
    if not item_dict_is_empty(equipped_item):
        musician.drop_item(equipped_item)
    musician.destroy()
