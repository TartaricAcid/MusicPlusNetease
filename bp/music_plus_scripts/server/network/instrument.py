# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.action.seated_instrument import get_seated_instrument
from music_plus_scripts.server.store.midi_store import get_midi, save_midi
from music_plus_scripts.utils.midi_payload import get_midi_payload_md5

factory = serverApi.GetEngineCompFactory()


def _finish_play(player_id, request_id, text):
    Call(player_id, "finish_instrument_play", {
        "request_id": request_id,
        "text": text,
    })


def _get_player_instrument(player_id):
    ride_comp = factory.CreateRide(player_id)
    if not ride_comp.IsEntityRiding():
        return None

    seat_id = ride_comp.GetEntityRider()
    return get_seated_instrument(seat_id)


@AllowCall
@InjectRPCPlayerId
def play_instrument_midi(player_id, args):
    request_id = args["request_id"]
    instrument = _get_player_instrument(player_id)
    if instrument is None:
        _finish_play(player_id, request_id, "请先坐到乐器前")
        return

    midi_md5 = args["midi_md5"]
    midi_payload = get_midi(midi_md5)
    if midi_payload is None:
        midi_payload = args.get("midi")
        if midi_payload is None:
            Call(player_id, "request_instrument_midi_payload", {
                "request_id": request_id,
                "midi_md5": midi_md5,
            })
            return
        if get_midi_payload_md5(midi_payload) != midi_md5:
            _finish_play(player_id, request_id, "MIDI 数据校验失败")
            return
        save_midi(midi_payload)

    Call("*", "stop_music_at_pos", {"pos": instrument["pos"]})
    Call("*", "play_midi_music", {
        "midi": midi_payload,
        "midi_md5": midi_md5,
        "performer_id": player_id,
        "pos": instrument["pos"],
        "sound_prefix": instrument["sound_prefix"],
        "instrument_group": instrument["instrument_group"],
        "enable_note_off": instrument["enable_note_off"],
        "particle_range": instrument.get("particle_range"),
    })
    _finish_play(player_id, request_id, "正在播放")


@AllowCall
@InjectRPCPlayerId
def stop_instrument_midi(player_id, args):
    instrument = _get_player_instrument(player_id)
    if instrument is None:
        return
    Call("*", "stop_music_at_pos", {"pos": instrument["pos"]})
    Call(player_id, "set_instrument_ui_notice", {"text": "已停止播放"})
