# -*- coding: utf-8 -*-

"""服务端 MIDI 存储库。

使用 ServerAutoStoreCls 实现存档内持久化。
数据结构与客户端 ClientMidiStore 一致：songs = { md5_str: midi_payload }。
"""

from music_plus_scripts.QuModLibs.Modules.DataStore.Server import ServerAutoStoreCls
from music_plus_scripts.utils.default_midis import get_default_midi
from music_plus_scripts.utils.midi_payload import get_midi_payload_md5


class ServerMidiStore(ServerAutoStoreCls):
    __VERSION__ = 1
    __AUTO_SAVE_INTERVAL__ = 8.0
    __SAVED_MOD_KEY_NAME__ = "server_midi_library"

    songs = {}


def save_midi(midi_payload):
    """存入一条 MIDI，返回其 MD5 key。已存在则跳过写入。"""
    midi_md5 = get_midi_payload_md5(midi_payload)
    if midi_md5 not in ServerMidiStore.songs:
        ServerMidiStore.songs[midi_md5] = midi_payload
        ServerMidiStore.mSignNeedUpdate()
    return midi_md5


def get_midi(midi_md5):
    """按 MD5 key 取一条 MIDI payload，不存在返回 None。"""
    if not midi_md5:
        return None
    default_midi = get_default_midi(midi_md5)
    if default_midi is not None:
        return default_midi
    return ServerMidiStore.songs.get(midi_md5)
