# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.action.handheld_instrument import get_entity_instrument
from music_plus_scripts.server.action.instrument_controller import get_request_performer
from music_plus_scripts.server.action.instrument_playback import play_instrument_playback, stop_instrument_playback
from music_plus_scripts.server.store.midi_store import get_midi, save_midi
from music_plus_scripts.utils.midi_payload import get_midi_payload_md5


def _finish_play(player_id, request_id, text):
    Call(player_id, "finish_instrument_play", {
        "request_id": request_id,
        "text": text,
    })


@AllowCall
@InjectRPCPlayerId
def play_instrument_midi(player_id, args):
    request_id = args["request_id"]
    performer_id = get_request_performer(player_id, args["performer_id"])
    instrument = get_entity_instrument(performer_id) if performer_id is not None else None
    if instrument is None:
        _finish_play(player_id, request_id, "当前没有可演奏的乐器")
        return

    midi_md5 = args["midi_md5"]
    midi_payload = get_midi(midi_md5)
    if midi_payload is None:
        midi_payload = args.get("midi")
        if midi_payload is None:
            Call(player_id, "request_instrument_midi_payload", {
                "request_id": request_id,
                "midi_md5": midi_md5,
                "performer_id": performer_id,
            })
            return
        if get_midi_payload_md5(midi_payload) != midi_md5:
            _finish_play(player_id, request_id, "MIDI 数据校验失败")
            return
        save_midi(midi_payload)

    play_instrument_playback(midi_payload, midi_md5, instrument, performer_id)
    _finish_play(player_id, request_id, "正在播放")


@AllowCall
@InjectRPCPlayerId
def stop_instrument_midi(player_id, args):
    performer_id = get_request_performer(player_id, args["performer_id"])
    instrument = get_entity_instrument(performer_id) if performer_id is not None else None
    if instrument is None:
        return
    stop_instrument_playback(instrument["playback_key"])
    Call(player_id, "set_instrument_ui_notice", {"text": "已停止播放"})
