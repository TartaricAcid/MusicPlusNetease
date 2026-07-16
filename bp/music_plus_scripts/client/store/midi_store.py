# -*- coding: utf-8 -*-

"""玩家客户端 MIDI 存储库。

使用 ClientAutoStoreCls + __GLOBAL_MODE__ = True 实现跨存档持久化。
数据结构与服务端 PaperTapeMidiStore 一致：songs = { md5_str: midi_payload }。
"""

from music_plus_scripts.QuModLibs.Modules.DataStore.Client import ClientAutoStoreCls
from music_plus_scripts.utils.midi_payload import get_midi_payload_md5


class ClientMidiStore(ClientAutoStoreCls):
    __VERSION__ = 1
    __AUTO_SAVE_INTERVAL__ = 8.0
    __GLOBAL_MODE__ = True
    __SAVED_MOD_KEY_NAME__ = "client_midi_library"

    songs = {}


def save_midi(midi_payload):
    """存入一条 MIDI，返回其 MD5 key。已存在则跳过写入。"""
    midi_md5 = get_midi_payload_md5(midi_payload)
    if midi_md5 not in ClientMidiStore.songs:
        ClientMidiStore.songs[midi_md5] = midi_payload
        ClientMidiStore.mSignNeedUpdate()
    return midi_md5


def get_midi(midi_md5):
    """按 MD5 key 取一条 MIDI payload，不存在返回 None。"""
    if not midi_md5:
        return None
    return ClientMidiStore.songs.get(midi_md5)


def remove_midi(midi_md5):
    """按 MD5 key 删除一条 MIDI，返回是否删除成功。"""
    if midi_md5 and midi_md5 in ClientMidiStore.songs:
        del ClientMidiStore.songs[midi_md5]
        ClientMidiStore.mSignNeedUpdate()
        return True
    return False


def has_midi(midi_md5):
    """检查库中是否已存在指定 MD5 的 MIDI。"""
    return bool(midi_md5) and midi_md5 in ClientMidiStore.songs


def list_midi_keys():
    """返回所有已存储 MIDI 的 MD5 key 列表。"""
    return list(ClientMidiStore.songs.keys())


def get_song_count():
    """返回库中已存储的 MIDI 数量。"""
    return len(ClientMidiStore.songs)
