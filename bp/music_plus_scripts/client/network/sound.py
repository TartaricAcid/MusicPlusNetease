# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Client import *
from music_plus_scripts.client.music.player import play_song


@AllowCall
def play_music_box(args):
    """接收服务端发来的 ABC 乐谱数据，在客户端解析并播放。

    Args 字典:
        abc: ABC 格式乐谱字符串
        pos: (x, y, z) 音乐盒方块位置
        sound_prefix: 声音 ID 前缀，如 "music_plus.music_box"
    """
    abc_text = args.get("abc", "")
    pos = args.get("pos", (0, 0, 0))
    sound_prefix = args.get("sound_prefix", "music_plus.music_box")
    if abc_text:
        play_song(abc_text, pos, sound_prefix)
