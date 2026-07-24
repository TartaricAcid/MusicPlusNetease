# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.action.podium import (
    PODIUM_BLOCK,
    play_podium_ensemble,
    stop_podium_ensemble,
)
from music_plus_scripts.server.store.midi_store import get_midi, save_midi
from music_plus_scripts.utils.midi_payload import get_midi_payload_md5

factory = serverApi.GetEngineCompFactory()


def _finish(player_id, request_id, text):
    Call(player_id, "finish_podium_play", {
        "request_id": request_id,
        "text": text,
    })


def _get_valid_podium(player_id, args):
    pos_data = args["pos"]
    pos = (pos_data[0], pos_data[1], pos_data[2])
    dimension = args["dimension"]
    if factory.CreateDimension(player_id).GetEntityDimensionId() != dimension:
        return None

    block = factory.CreateBlockInfo(levelId).GetBlockNew(pos, dimension)
    if block is None or block.get("name") != PODIUM_BLOCK:
        return None

    player_pos = factory.CreatePos(player_id).GetPos()
    if player_pos is None:
        return None
    center = (pos[0] + 0.5, pos[1] + 1.0, pos[2] + 0.5)
    distance_sq = sum((player_pos[index] - center[index]) ** 2 for index in range(3))
    if distance_sq > 64.0:
        return None
    return pos, dimension


@AllowCall
@InjectRPCPlayerId
def play_podium_midi(player_id, args):
    request_id = args["request_id"]
    podium = _get_valid_podium(player_id, args)
    if podium is None:
        _finish(player_id, request_id, "指挥台已失效或距离过远")
        return

    midi_md5 = args["midi_md5"]
    midi_payload = get_midi(midi_md5)
    if midi_payload is None:
        midi_payload = args.get("midi")
        if midi_payload is None:
            Call(player_id, "request_podium_midi_payload", {
                "request_id": request_id,
                "midi_md5": midi_md5,
                "pos": podium[0],
                "dimension": podium[1],
            })
            return
        if get_midi_payload_md5(midi_payload) != midi_md5:
            _finish(player_id, request_id, "MIDI 数据校验失败")
            return
        save_midi(midi_payload)

    count = play_podium_ensemble(podium[0], podium[1], midi_payload, midi_md5)
    if count <= 0:
        _finish(player_id, request_id, "12 格内没有可演奏的乐器")
        return
    _finish(player_id, request_id, "正在指挥 {} 位演奏者".format(count))


@AllowCall
@InjectRPCPlayerId
def stop_podium_midi(player_id, args):
    podium = _get_valid_podium(player_id, args)
    if podium is None:
        return
    count = stop_podium_ensemble(podium[0], podium[1])
    text = "已停止合奏" if count > 0 else "当前没有正在进行的合奏"
    Call(player_id, "set_podium_ui_notice", {"text": text})
