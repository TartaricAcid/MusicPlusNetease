# -*- coding: utf-8 -*-

"""乐器注册表

所有可用乐器及其 MIDI note 到声音文件的映射定义在此处。

MIDI 音符号参考:
  C4=60, A4=69, C5=72, C6=84, C7=96
"""

from music_plus_scripts.client.music.instrument_def import InstrumentDef
from music_plus_scripts.client.music.instrument_map_builder import c_octave_a_sample, named_notes, percussion, octave_up

MUSIC_BOX = InstrumentDef(
    name="music_box",
    sound_prefix="music_plus.music_box",
    lowest_note=57,
    highest_note=80,
    note_map=named_notes(57, (
        "a4", "a4s", "b4", "c5", "c5s", "d5", "d5s", "e5",
        "f5", "f5s", "g5", "g5s", "a5", "a5s", "b5", "c6",
        "c6s", "d6", "d6s", "e6", "f6", "f6s", "g6", "g6s",
    )),
)

STEINWAY = InstrumentDef(
    name="steinway",
    sound_prefix="music_plus.steinway",
    lowest_note=24,
    highest_note=108,
    note_map=octave_up(c_octave_a_sample(range(1, 9), 24, 108)),
)

HARPSICHORD = InstrumentDef(
    name="harpsichord",
    sound_prefix="music_plus.harpsichord",
    lowest_note=36,
    highest_note=89,
    note_map=octave_up(c_octave_a_sample(range(2, 8), 36, 89)),
)

CE_GUITAR = InstrumentDef(
    name="ce_guitar",
    sound_prefix="music_plus.ce_guitar",
    lowest_note=40,
    highest_note=88,
    note_map=octave_up(c_octave_a_sample(range(3, 7), 40, 88)),
)

NYLON_GUITAR = InstrumentDef(
    name="nylon_guitar",
    sound_prefix="music_plus.nylon_guitar",
    lowest_note=40,
    highest_note=88,
    note_map=octave_up(c_octave_a_sample(range(3, 7), 40, 88)),
)

GUZHENG = InstrumentDef(
    name="guzheng",
    sound_prefix="music_plus.guzheng",
    lowest_note=48,
    highest_note=84,
    note_map=octave_up(c_octave_a_sample(range(3, 7), 48, 84)),
)

VIOLIN_SOLO = InstrumentDef(
    name="violin_solo",
    sound_prefix="music_plus.violin_solo",
    lowest_note=55,
    highest_note=100,
    note_map=octave_up(c_octave_a_sample(range(4, 8), 55, 100)),
)

TRUMPET = InstrumentDef(
    name="trumpet",
    sound_prefix="music_plus.trumpet",
    lowest_note=40,
    highest_note=84,
    note_map=octave_up(c_octave_a_sample(range(4, 8), 40, 84)),
)

FLUTE = InstrumentDef(
    name="flute",
    sound_prefix="music_plus.flute",
    lowest_note=47,
    highest_note=84,
    note_map=octave_up(c_octave_a_sample(range(5, 8), 47, 84)),
)

BASS = InstrumentDef(
    name="bass",
    sound_prefix="music_plus.bass",
    lowest_note=28,
    highest_note=64,
    note_map=c_octave_a_sample(range(3, 6), 28, 64),
)

REAL_KIT = InstrumentDef(
    name="real_kit",
    sound_prefix="music_plus.real_kit",
    lowest_note=35,
    highest_note=51,
    note_map=percussion("real", True),
)

LINN_KIT = InstrumentDef(
    name="linn_kit",
    sound_prefix="music_plus.linn_kit",
    lowest_note=35,
    highest_note=51,
    note_map=percussion("linn", False),
)

_REGISTRY = {
    MUSIC_BOX.sound_prefix: MUSIC_BOX,
    STEINWAY.sound_prefix: STEINWAY,
    HARPSICHORD.sound_prefix: HARPSICHORD,
    CE_GUITAR.sound_prefix: CE_GUITAR,
    NYLON_GUITAR.sound_prefix: NYLON_GUITAR,
    GUZHENG.sound_prefix: GUZHENG,
    VIOLIN_SOLO.sound_prefix: VIOLIN_SOLO,
    TRUMPET.sound_prefix: TRUMPET,
    FLUTE.sound_prefix: FLUTE,
    BASS.sound_prefix: BASS,
    REAL_KIT.sound_prefix: REAL_KIT,
    LINN_KIT.sound_prefix: LINN_KIT,
}


def get_instrument(sound_prefix):
    """根据 sound_prefix 获取对应的乐器定义。"""
    return _REGISTRY.get(sound_prefix)
