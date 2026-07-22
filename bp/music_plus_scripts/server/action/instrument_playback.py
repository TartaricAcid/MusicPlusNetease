# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.utils.default_midis import is_default_midi


def build_block_playback(pos, dimension, direction=None):
    x, y, z = pos
    anchor = {
        "type": "block",
        "pos": tuple(pos),
        "dimension": dimension,
    }
    if direction is not None:
        anchor["direction"] = direction
    return {
        "playback_key": "block:{}:{}:{}:{}".format(dimension, x, y, z),
        "anchor": anchor,
    }


def build_entity_playback(entity_id, pos, dimension):
    return {
        "playback_key": "entity:{}".format(entity_id),
        "anchor": {
            "type": "entity",
            "entity_id": entity_id,
            "fallback_pos": tuple(pos),
            "offset": (0, 1.0, 0),
            "dimension": dimension,
        },
    }


def stop_instrument_playback(playback_key):
    Call("*", "stop_midi_music", {"playback_key": playback_key})


def stop_entity_instrument_playback(entity_id):
    stop_instrument_playback("entity:{}".format(entity_id))


def play_instrument_playback(midi_payload, midi_md5, instrument, performer_id=None):
    stop_instrument_playback(instrument["playback_key"])
    args = {
        "midi_md5": midi_md5,
        "playback_key": instrument["playback_key"],
        "anchor": instrument["anchor"],
        "performer_id": performer_id,
        "animation_profile": instrument.get("animation_profile"),
        "sound_prefix": instrument["sound_prefix"],
        "instrument_group": instrument["instrument_group"],
        "enable_note_off": instrument["enable_note_off"],
        "particle_range": instrument.get("particle_range"),
    }
    if not is_default_midi(midi_md5):
        args["midi"] = midi_payload
    Call("*", "play_midi_music", args)
