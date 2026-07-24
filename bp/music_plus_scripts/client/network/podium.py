# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Client import *
from music_plus_scripts.utils.default_midis import is_default_midi
from music_plus_scripts.utils.midi_payload import get_midi_payload_md5

_PENDING_PLAY_REQUESTS = {}
_NEXT_PLAY_REQUEST_ID = 0


@AllowCall
def open_podium_ui(args):
    from music_plus_scripts.client.ui.instrument_ui import InstrumentUI
    if InstrumentUI.getUiNode() is not None:
        return
    InstrumentUI.pushScreen(createParams={
        "podium_context": {
            "pos": tuple(args["pos"]),
            "dimension": args["dimension"],
        },
    })


def request_podium_play(midi_payload, podium_context):
    global _NEXT_PLAY_REQUEST_ID
    _NEXT_PLAY_REQUEST_ID += 1
    request_id = str(_NEXT_PLAY_REQUEST_ID)

    midi_md5 = get_midi_payload_md5(midi_payload)
    if not is_default_midi(midi_md5):
        _PENDING_PLAY_REQUESTS[request_id] = midi_payload

    Call("play_podium_midi", {
        "request_id": request_id,
        "midi_md5": midi_md5,
        "pos": podium_context["pos"],
        "dimension": podium_context["dimension"],
    })


def request_podium_stop(podium_context):
    Call("stop_podium_midi", {
        "pos": podium_context["pos"],
        "dimension": podium_context["dimension"],
    })


@AllowCall
def request_podium_midi_payload(args):
    midi_payload = _PENDING_PLAY_REQUESTS.get(args["request_id"])
    if midi_payload is None:
        return
    Call("play_podium_midi", {
        "request_id": args["request_id"],
        "midi_md5": args["midi_md5"],
        "midi": midi_payload,
        "pos": args["pos"],
        "dimension": args["dimension"],
    })


@AllowCall
def finish_podium_play(args):
    _PENDING_PLAY_REQUESTS.pop(args["request_id"], None)
    set_podium_ui_notice(args)


@AllowCall
def set_podium_ui_notice(args):
    from music_plus_scripts.client.ui.instrument_ui import InstrumentUI, NOTICE_LABEL_PATH
    ui_node = InstrumentUI.getUiNode()
    if ui_node is None:
        return
    notice_node = ui_node.GetBaseUIControl(NOTICE_LABEL_PATH)
    if notice_node is not None:
        notice_node.asLabel().SetText(args["text"])
