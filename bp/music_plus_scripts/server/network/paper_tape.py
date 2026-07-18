# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Modules.Items.Server import BaseItemService
from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.action.block_instrument import PAPER_TAPE_ITEM
from music_plus_scripts.server.store.midi_store import get_midi, save_midi
from music_plus_scripts.server.utils.item_utils import give_player_item_dict
from music_plus_scripts.utils.midi_payload import get_midi_payload_md5

MIDI_MD5_NBT_KEY = "midi_md5"
NBT_STRING = 8


def _set_player_notice(player_id, text):
    Call(player_id, "set_computer_ui_notice", {"text": text})


def _finish_burn_request(player_id, request_id):
    Call(player_id, "finish_paper_tape_burn", {"request_id": request_id})


@AllowCall
@InjectRPCPlayerId
def burn_paper_tape_midi(player_id, args):
    request_id = args["request_id"]
    midi_md5 = args["midi_md5"]
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
        _finish_burn_request(player_id, request_id)
        return

    midi_data = get_midi(midi_md5)
    if midi_data is None:
        midi_data = args.get("midi")
        if midi_data is None:
            Call(player_id, "request_paper_tape_midi_payload", {
                "request_id": request_id,
                "midi_md5": midi_md5,
            })
            return

        actual_md5 = get_midi_payload_md5(midi_data)
        if actual_md5 != midi_md5:
            _set_player_notice(player_id, "MIDI 数据校验失败")
            _finish_burn_request(player_id, request_id)
            return
        save_midi(midi_data)

    duration = args.get("duration", 0.0)
    title = args.get("title", "")
    analysis_summary = args.get("analysis_summary", "")
    burned_item = target_item.getDict()
    burned_item["count"] = 1

    burned_item["customTips"] = "%name%\n" + "§7歌曲： %s\n时长： %s" % (title, duration)
    if analysis_summary:
        burned_item["customTips"] += "\n§7%s" % analysis_summary

    burned_item["userData"] = {
        MIDI_MD5_NBT_KEY: {
            "__type__": NBT_STRING,
            "__value__": midi_md5,
        }
    }

    if target_item.count == 1:
        target_item.setCustomTips(burned_item["customTips"])
        target_item.setUserData(burned_item["userData"])
        BaseItemService.setPlayerInventoryData(player_id, inventory, 0)
    else:
        target_item.setCount(target_item.count - 1)
        BaseItemService.setPlayerInventoryData(player_id, inventory, 0)
        give_player_item_dict(player_id, burned_item)

    _set_player_notice(player_id, "已刻录到纸带")
    _finish_burn_request(player_id, request_id)
