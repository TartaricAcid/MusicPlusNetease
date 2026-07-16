# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Modules.Items.Server import BaseItemService
from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.action.block_instrument import PAPER_TAPE_ITEM
from music_plus_scripts.server.store.midi_store import save_midi
from music_plus_scripts.server.utils.item_utils import get_mainhand_item_dict, set_mainhand_item_dict

MIDI_NBT_KEY = "midi"
MIDI_MD5_NBT_KEY = "midi_md5"
NBT_STRING = 8


def _set_player_notice(player_id, text):
    Call(player_id, "set_computer_ui_notice", {"text": text})


def _build_midi_user_data(midi_md5):
    return {
        MIDI_MD5_NBT_KEY: {
            "__type__": NBT_STRING,
            "__value__": midi_md5,
        }
    }


@AllowCall
@InjectRPCPlayerId
def write_paper_tape_midi(player_id, args):
    midi_data = args.get(MIDI_NBT_KEY)
    if midi_data is None:
        return

    item = get_mainhand_item_dict(player_id, True)
    if not item or item.get("newItemName") != PAPER_TAPE_ITEM:
        return

    user_data = item.get("userData") or {}
    if user_data.get(MIDI_MD5_NBT_KEY):
        return

    midi_md5 = save_midi(midi_data)

    item["customTips"] = "%name%\n§6已写入 MIDI 数据"
    item["userData"] = _build_midi_user_data(midi_md5)

    set_mainhand_item_dict(player_id, item)


@AllowCall
@InjectRPCPlayerId
def burn_paper_tape_midi(player_id, args):
    midi_data = args.get(MIDI_NBT_KEY)
    if midi_data is None:
        _set_player_notice(player_id, "没有可刻录的 MIDI 数据")
        return

    midi_md5 = save_midi(midi_data)
    inventory = BaseItemService.getPlayerInventoryData(player_id, True, 0)

    target_item = None
    for item in inventory.walk():
        if item.empty:
            continue
        if item.newItemName != PAPER_TAPE_ITEM:
            continue
        if item.userData:
            continue
        target_item = item
        break

    if target_item is None:
        _set_player_notice(player_id, "背包里没有空白纸带")
        return

    target_item.setCustomTips("§6已写入 MIDI 数据")
    target_item.setUserData(_build_midi_user_data(midi_md5))
    BaseItemService.setPlayerInventoryData(player_id, inventory, 0)
    _set_player_notice(player_id, "已刻录到纸带")
