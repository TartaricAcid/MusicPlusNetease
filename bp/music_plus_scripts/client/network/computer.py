# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Client import *
from music_plus_scripts.utils.midi_payload import get_midi_payload_md5

# 等待服务端确认或索取完整 MIDI 数据的刻录请求，key 为 request_id。
_PENDING_BURN_REQUESTS = {}

# 当前客户端运行期间用于生成唯一刻录 request_id 的递增计数器。
_NEXT_BURN_REQUEST_ID = 0


def request_paper_tape_burn(midi_info):
    """先发送 MIDI 索引，仅在服务端缓存未命中时补发完整数据。"""
    global _NEXT_BURN_REQUEST_ID
    _NEXT_BURN_REQUEST_ID += 1
    request_id = str(_NEXT_BURN_REQUEST_ID)

    midi_payload = midi_info["midi"]
    midi_md5 = get_midi_payload_md5(midi_payload)
    _PENDING_BURN_REQUESTS[request_id] = midi_info
    Call("burn_paper_tape_midi", {
        "request_id": request_id,
        "midi_md5": midi_md5,
        "duration": midi_info.get("duration", 0.0),
        "title": midi_info.get("title", ""),
    })


@AllowCall
def request_paper_tape_midi_payload(args):
    request_id = args["request_id"]
    if request_id not in _PENDING_BURN_REQUESTS:
        return

    midi_info = _PENDING_BURN_REQUESTS[request_id]
    request = midi_info.copy()
    request["request_id"] = request_id
    request["midi_md5"] = args["midi_md5"]
    Call("burn_paper_tape_midi", request)


@AllowCall
def finish_paper_tape_burn(args):
    _PENDING_BURN_REQUESTS.pop(args["request_id"], None)


@AllowCall
def open_computer_ui(args):
    from music_plus_scripts.client.ui.computer_ui import ComputerUI
    # 若已打开则不重复 push
    if ComputerUI.getUiNode() is None:
        ComputerUI.pushScreen()
    else:
        set_computer_ui_notice({"text": ""})


@AllowCall
def set_computer_ui_notice(args):
    from music_plus_scripts.client.ui.computer_ui import ComputerUI, NOTICE_LABEL_PATH

    ui_node = ComputerUI.getUiNode()
    if ui_node is None:
        return
    notice_node = ui_node.GetBaseUIControl(NOTICE_LABEL_PATH)
    if notice_node is not None:
        notice_node.asLabel().SetText(args.get("text", ""))
