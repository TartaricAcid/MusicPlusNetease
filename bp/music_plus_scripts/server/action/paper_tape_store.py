# -*- coding: utf-8 -*-

import _md5

from music_plus_scripts.QuModLibs.Modules.DataStore.Server import ServerAutoStoreCls


class PaperTapeMidiStore(ServerAutoStoreCls):
    __VERSION__ = 1
    __AUTO_SAVE_INTERVAL__ = 8.0
    __SAVED_MOD_KEY_NAME__ = "paper_tape_midi"

    songs = {}


def save_midi(midi_base64):
    midi_bytes = midi_base64.encode("utf-8")
    midi_md5 = _md5.new(midi_bytes).hexdigest()
    if midi_md5 not in PaperTapeMidiStore.songs:
        PaperTapeMidiStore.songs[midi_md5] = midi_base64
        PaperTapeMidiStore.mSignNeedUpdate()
    return midi_md5


def get_midi(midi_md5):
    if not midi_md5:
        return None
    return PaperTapeMidiStore.songs.get(midi_md5)
