# -*- coding: utf-8 -*-

"""玩家客户端 MIDI 存储库。

使用 ClientAutoStoreCls + __GLOBAL_MODE__ = True 实现跨存档持久化。

数据结构:
    songs = { md5_str: midi_payload }
    meta  = { md5_str: { "title": str, "duration": float, "analysis": dict } }
"""

from music_plus_scripts.QuModLibs.Modules.DataStore.Client import ClientAutoStoreCls
from music_plus_scripts.utils.default_midis import (
    DEFAULT_MIDI_KEYS,
    get_default_midi,
    get_default_midi_meta,
    is_default_midi,
)
from music_plus_scripts.utils.midi_payload import get_midi_payload_md5


class ClientMidiStore(ClientAutoStoreCls):
    __VERSION__ = 2
    __AUTO_SAVE_INTERVAL__ = 8.0
    __GLOBAL_MODE__ = True
    __SAVED_MOD_KEY_NAME__ = "client_midi_library"

    songs = {}
    meta = {}


def save_midi(midi_payload, title="", duration=0.0, analysis=None):
    """存入一条 MIDI 及其元信息，返回 MD5 key。已存在则跳过。"""
    midi_md5 = get_midi_payload_md5(midi_payload)
    if midi_md5 not in ClientMidiStore.songs:
        ClientMidiStore.songs[midi_md5] = midi_payload
        ClientMidiStore.meta[midi_md5] = {
            "title": title,
            "duration": duration,
            "analysis": analysis,
        }
        ClientMidiStore.mSignNeedUpdate()
    return midi_md5


def get_midi(midi_md5):
    """按 MD5 key 取一条 MIDI payload，不存在返回 None。"""
    if not midi_md5:
        return None
    default_midi = get_default_midi(midi_md5)
    if default_midi is not None:
        return default_midi
    return ClientMidiStore.songs.get(midi_md5)


def get_meta(midi_md5):
    """按 MD5 key 取元信息 dict，不存在返回 None。"""
    if not midi_md5:
        return None
    default_meta = get_default_midi_meta(midi_md5)
    if default_meta is not None:
        return default_meta
    return ClientMidiStore.meta.get(midi_md5)


def update_meta(midi_md5, title=None, analysis=None):
    """更新指定 MIDI 的元信息（仅更新非 None 的字段）。"""
    if is_default_midi(midi_md5):
        return title is None
    info = ClientMidiStore.meta.get(midi_md5)
    if info is None:
        return False
    if title is not None:
        info["title"] = title
    if analysis is not None:
        info["analysis"] = analysis
    ClientMidiStore.mSignNeedUpdate()
    return True


def remove_midi(midi_md5):
    """按 MD5 key 删除一条 MIDI 及其元信息，返回是否成功。"""
    if is_default_midi(midi_md5):
        return False
    if midi_md5 and midi_md5 in ClientMidiStore.songs:
        del ClientMidiStore.songs[midi_md5]
        ClientMidiStore.meta.pop(midi_md5, None)
        ClientMidiStore.mSignNeedUpdate()
        return True
    return False


def has_midi(midi_md5):
    """检查库中是否已存在指定 MD5 的 MIDI。"""
    return is_default_midi(midi_md5) or bool(midi_md5) and midi_md5 in ClientMidiStore.songs


def list_midi_keys():
    """返回所有已存储 MIDI 的 MD5 key 列表。"""
    user_keys = [key for key in ClientMidiStore.songs.keys() if not is_default_midi(key)]
    return list(DEFAULT_MIDI_KEYS) + user_keys


def get_song_count():
    """返回库中已存储的 MIDI 数量。"""
    return len(list_midi_keys())
