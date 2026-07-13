# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Client import *
from music_plus_scripts.client.music.midi_player import start_playback


@AllowCall
def play_music_box(args):
    """接收服务端发来的 MIDI 音符数据，在客户端启动 tick 驱动播放。

    Args 字典:
        notes: 音符列表 [[time, type, channel, midi_note, velocity], ...]
        pos: (x, y, z) 音乐盒方块位置
        sound_prefix: 声音 ID 前缀，如 "music_plus.music_box"
        enable_note_off: 是否响应 note_off / sustain_pedal 中断（默认 True）
    """
    notes = args.get("notes", [])
    pos = args.get("pos", (0, 0, 0))
    sound_prefix = args.get("sound_prefix", "music_plus.music_box")
    enable_note_off = args.get("enable_note_off", True)
    if notes:
        start_playback(notes, pos, sound_prefix, enable_note_off)
