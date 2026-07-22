# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Client import *
from music_plus_scripts.utils.default_midis import is_default_midi
from music_plus_scripts.utils.midi_payload import get_midi_payload_md5

_PENDING_PLAY_REQUESTS = {}
_NEXT_PLAY_REQUEST_ID = 0


def open_instrument_ui():
    from music_plus_scripts.client.action.instrument_context import get_instrument_target_id
    from music_plus_scripts.client.ui.instrument_ui import InstrumentUI
    if get_instrument_target_id() is None:
        return
    if InstrumentUI.getUiNode() is None:
        InstrumentUI.pushScreen()


def request_instrument_play(midi_payload):
    global _NEXT_PLAY_REQUEST_ID
    _NEXT_PLAY_REQUEST_ID += 1
    request_id = str(_NEXT_PLAY_REQUEST_ID)

    midi_md5 = get_midi_payload_md5(midi_payload)
    if not is_default_midi(midi_md5):
        _PENDING_PLAY_REQUESTS[request_id] = midi_payload

    Call("play_instrument_midi", {
        "request_id": request_id,
        "midi_md5": midi_md5,
    })


def request_instrument_stop():
    Call("stop_instrument_midi", {})


@AllowCall
def request_instrument_midi_payload(args):
    request_id = args["request_id"]
    midi_payload = _PENDING_PLAY_REQUESTS.get(request_id)
    if midi_payload is None:
        return
    Call("play_instrument_midi", {
        "request_id": request_id,
        "midi_md5": args["midi_md5"],
        "midi": midi_payload,
    })


@AllowCall
def finish_instrument_play(args):
    _PENDING_PLAY_REQUESTS.pop(args["request_id"], None)
    set_instrument_ui_notice(args)


@AllowCall
def set_instrument_ui_notice(args):
    from music_plus_scripts.client.ui.instrument_ui import InstrumentUI, NOTICE_LABEL_PATH

    ui_node = InstrumentUI.getUiNode()
    if ui_node is None:
        return
    notice_node = ui_node.GetBaseUIControl(NOTICE_LABEL_PATH)
    if notice_node is not None:
        notice_node.asLabel().SetText(args["text"])


@AllowCall
def set_instrument_context(args):
    from music_plus_scripts.client.action.instrument_context import set_instrument_context as set_context
    set_context(args["target_id"], args["mode"], args.get("view_yaw"))
