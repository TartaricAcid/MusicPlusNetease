# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Modules.DataStore.Server import ServerAutoStoreCls
from music_plus_scripts.utils.midi_payload import get_midi_payload_md5


class PaperTapeMidiStore(ServerAutoStoreCls):
    __VERSION__ = 1
    __AUTO_SAVE_INTERVAL__ = 8.0
    __SAVED_MOD_KEY_NAME__ = "paper_tape_midi"

    songs = {}


def save_midi(midi_payload):
    midi_md5 = get_midi_payload_md5(midi_payload)
    if midi_md5 not in PaperTapeMidiStore.songs:
        PaperTapeMidiStore.songs[midi_md5] = midi_payload
        PaperTapeMidiStore.mSignNeedUpdate()
    return midi_md5


def get_midi(midi_md5):
    if not midi_md5:
        return None
    return PaperTapeMidiStore.songs.get(midi_md5)
