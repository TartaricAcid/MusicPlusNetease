# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Modules.Items.Server import BaseItemService
from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.action.block_instrument import PAPER_TAPE_ITEM
from music_plus_scripts.server.store.midi_store import save_midi

MIDI_MD5_NBT_KEY = "midi_md5"
NBT_STRING = 8


def _set_player_notice(player_id, text):
    Call(player_id, "set_computer_ui_notice", {"text": text})


@AllowCall
@InjectRPCPlayerId
def burn_paper_tape_midi(player_id, args):
    midi_data = args.get("midi")
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

    duration = args.get("duration", 0.0)
    title = args.get("title", "")
    target_item.setCustomTips("%name%\n" + "§7歌曲： %s\n时长： %s" % (title, duration))

    target_item.setUserData({
        MIDI_MD5_NBT_KEY: {
            "__type__": NBT_STRING,
            "__value__": midi_md5,
        }
    })

    BaseItemService.setPlayerInventoryData(player_id, inventory, 0)
    _set_player_notice(player_id, "已刻录到纸带")
