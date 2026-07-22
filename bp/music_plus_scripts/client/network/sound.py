# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Client import *
from music_plus_scripts.client.music.midi_playback_controller import play_midi_music_data, stop_midi_music as stop_playback
from music_plus_scripts.utils.default_midis import get_default_midi

factory = clientApi.GetEngineCompFactory()
level_id = clientApi.GetLevelId()
audio = factory.CreateCustomAudio(level_id)


@AllowCall
def play_midi_music(args):
    """接收服务端发来的 MIDI 数据，在客户端启动 tick 驱动播放。

    Args 字典:
        midi: MIDI payload 字典
        playback_key: 播放实例身份
        anchor: 方块或实体播放锚点
        sound_prefix: 声音 ID 前缀，如 "music_plus.music_box"
        instrument_group: Program Change 可使用的乐器组
        enable_note_off: 是否响应 note_off / sustain_pedal 中断（默认 True）
        particle_range: 可选的粒子局部三轴偏移范围，方块锚点会随朝向旋转
    """
    midi_payload = args.get("midi")
    if midi_payload is None:
        midi_payload = get_default_midi(args.get("midi_md5"))
    if midi_payload is None:
        return
    play_midi_music_data(
        midi_payload,
        args["playback_key"],
        args["anchor"],
        args.get("sound_prefix", "music_plus.music_box"),
        args.get("instrument_group", "music_box"),
        args.get("enable_note_off", True),
        args.get("midi_md5"),
        args.get("performer_id"),
        args.get("animation_profile"),
        args.get("particle_range"),
    )


@AllowCall
def stop_midi_music(args):
    stop_playback(args["playback_key"])


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
