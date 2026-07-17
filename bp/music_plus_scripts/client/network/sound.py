# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Client import *
from music_plus_scripts.client.music.midi_playback_controller import play_midi_music_data, stop_midi_music_at_pos
from music_plus_scripts.client.music.midi_player import stop_player_animation

factory = clientApi.GetEngineCompFactory()
level_id = clientApi.GetLevelId()
audio = factory.CreateCustomAudio(level_id)


@AllowCall
def play_midi_music(args):
    """接收服务端发来的 MIDI 数据，在客户端启动 tick 驱动播放。

    Args 字典:
        midi: MIDI payload 字典
        pos: (x, y, z) 音乐盒方块位置
        sound_prefix: 声音 ID 前缀，如 "music_plus.music_box"
        instrument_group: Program Change 可使用的乐器组
        enable_note_off: 是否响应 note_off / sustain_pedal 中断（默认 True）
    """
    play_midi_music_data(
        args["midi"],
        args.get("pos", (0, 0, 0)),
        args.get("sound_prefix", "music_plus.music_box"),
        args.get("instrument_group", "music_box"),
        args.get("enable_note_off", True),
        args.get("midi_md5"),
        args.get("performer_id"),
    )


@AllowCall
def stop_music_at_pos(args):
    stop_midi_music_at_pos(args.get("pos", (0, 0, 0)))


@AllowCall
def stop_player_piano_animation(args):
    stop_player_animation(args["player_id"])


@AllowCall
def play_sound(args):
    pos = args["pos"]
    sound = args["sound"]
    name = sound.get("name", "random.explode")
    volume = sound.get("volume", 1.0)
    pitch = sound.get("pitch", 1.0)
    loop = sound.get("loop", False)

    audio.PlayCustomMusic(name, pos, volume, pitch, loop, None)


@AllowCall
def play_sound_and_swing_hand(args):
    if "sound" in args:
        play_sound(args)

    player_id = args["player_id"]
    if player_id == clientApi.GetLocalPlayerId():
        player = factory.CreatePlayer(level_id)
        player.Swing()
