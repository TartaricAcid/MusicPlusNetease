# -*- coding: utf-8 -*-

import base64
import io

from music_plus_scripts.QuModLibs.Client import *
from music_plus_scripts.mido import MidiFile
from music_plus_scripts.utils.midi_payload import pack_midi_payload

PAPER_TAPE_ITEM = "music_plus:paper_tape"
MIDI_MD5_NBT_KEY = "midi_md5"

factory = clientApi.GetEngineCompFactory()
game_comp = factory.CreateGame(levelId)


def is_paper_tape(item_name):
    return item_name == PAPER_TAPE_ITEM


def test_record_midi(args):
    item_dict = args["itemDict"]

    user_data = item_dict.get("userData") or {}
    if MIDI_MD5_NBT_KEY in user_data:
        game_comp.SetTipMessage("纸带已经写入过 MIDI 数据，无法再次写入")
        return

    clipboard_text = game_comp.GetClipboardContent()
    # 幻数文件头检查
    if not clipboard_text.startswith("TVRoZ"):
        game_comp.SetTipMessage("剪贴板中没有 MIDI 数据")
        return

    midi_bytes = base64.b64decode(clipboard_text)
    if not midi_bytes:
        game_comp.SetTipMessage("不是有效的 Base64 MIDI 数据")
        return

    midi_file = MidiFile(file=io.BytesIO(midi_bytes), charset="utf-8")
    if midi_file is None:
        game_comp.SetTipMessage("不是有效的 MIDI 数据")
        return

    Call("write_paper_tape_midi", {
        "midi": pack_midi_payload(midi_bytes),
    })
    args["ret"] = True
