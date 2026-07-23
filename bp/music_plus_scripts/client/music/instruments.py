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

PIANO = InstrumentDef(
    name="piano",
    sound_prefix="music_plus.piano",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(1, 9), 24, 119)),
)

HARPSICHORD = InstrumentDef(
    name="harpsichord",
    sound_prefix="music_plus.harpsichord",
    lowest_note=24,
    highest_note=119,
    note_map=c_octave_a_sample(range(2, 8), 36, 107),
)

HONKYTONK = InstrumentDef(
    name="honkytonk",
    sound_prefix="music_plus.honkytonk",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(2, 8), 36, 107)),
)

RHODES = InstrumentDef(
    name="rhodes",
    sound_prefix="music_plus.rhodes",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(2, 8), 36, 107)),
)

VIBRA = InstrumentDef(
    name="vibra",
    sound_prefix="music_plus.vibra",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(4, 7), 60, 95)),
)

CE_GUITAR = InstrumentDef(
    name="ce_guitar",
    sound_prefix="music_plus.ce_guitar",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(3, 7), 48, 95)),
)

NYLON_GUITAR = InstrumentDef(
    name="nylon_guitar",
    sound_prefix="music_plus.nylon_guitar",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(3, 7), 48, 95)),
)

GUZHENG = InstrumentDef(
    name="guzheng",
    sound_prefix="music_plus.guzheng",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(3, 7), 48, 95)),
)

VIOLIN_SOLO = InstrumentDef(
    name="violin_solo",
    sound_prefix="music_plus.violin_solo",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(4, 8), 60, 107)),
)

TRUMPET = InstrumentDef(
    name="trumpet",
    sound_prefix="music_plus.trumpet",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(4, 8), 60, 107)),
)

FLUTE = InstrumentDef(
    name="flute",
    sound_prefix="music_plus.flute",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(5, 8), 72, 107)),
)

BASS = InstrumentDef(
    name="bass",
    sound_prefix="music_plus.bass",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(3, 6), 48, 83)),
)

ACOUSTIC_BASS = InstrumentDef(
    name="a_bass",
    sound_prefix="music_plus.a_bass",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(2, 6), 24, 119)),
)

ACCORDION = InstrumentDef(
    name="accordion",
    sound_prefix="music_plus.accordion",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(2, 8), 24, 119)),
)

BELL = InstrumentDef(
    name="bell",
    sound_prefix="music_plus.bell",
    lowest_note=24,
    highest_note=119,
    note_map=named_notes(60, ("bell",)),
)

BRASS_ENSEMBLE = InstrumentDef(
    name="brs_ens",
    sound_prefix="music_plus.brs_ens",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(3, 8), 24, 119)),
)

CHURCH_ORGAN = InstrumentDef(
    name="c_organ",
    sound_prefix="music_plus.c_organ",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(1, 8), 24, 119)),
)

CELESTE = InstrumentDef(
    name="celeste",
    sound_prefix="music_plus.celeste",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(3, 9), 24, 119)),
)

CHOIR = InstrumentDef(
    name="choir",
    sound_prefix="music_plus.choir",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(2, 8), 24, 119)),
)

DISTORTION_GUITAR = InstrumentDef(
    name="de_guitar",
    sound_prefix="music_plus.de_guitar",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(3, 7), 24, 119)),
)

ELECTRIC_ORGAN = InstrumentDef(
    name="e_organ",
    sound_prefix="music_plus.e_organ",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(2, 9), 24, 119)),
)

GLOCKENSPIEL = InstrumentDef(
    name="glockenspiel",
    sound_prefix="music_plus.glockenspiel",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(4, 8), 24, 119)),
)

HARP = InstrumentDef(
    name="harp",
    sound_prefix="music_plus.harp",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(2, 8), 24, 119)),
)

MARIMBA = InstrumentDef(
    name="marimba",
    sound_prefix="music_plus.marimba",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(2, 8), 24, 119)),
)

OBOE = InstrumentDef(
    name="oboe",
    sound_prefix="music_plus.oboe",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(4, 8), 24, 119)),
)

ORCHESTRA_HIT = InstrumentDef(
    name="orch_hit",
    sound_prefix="music_plus.orch_hit",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(4, 6), 24, 119)),
)

PAD = InstrumentDef(
    name="pad",
    sound_prefix="music_plus.pad",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(2, 8), 24, 119)),
)

REVERSE_CRASH = InstrumentDef(
    name="rev_crash",
    sound_prefix="music_plus.rev_crash",
    lowest_note=24,
    highest_note=119,
    note_map=named_notes(60, ("rev_crash",)),
)

SAX = InstrumentDef(
    name="sax",
    sound_prefix="music_plus.sax",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(3, 7), 24, 119)),
)

SITAR = InstrumentDef(
    name="sitar",
    sound_prefix="music_plus.sitar",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(2, 8), 24, 119)),
)

SQUARE = InstrumentDef(
    name="square",
    sound_prefix="music_plus.square",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(4, 5), 24, 119)),
)

STRING_ENSEMBLE = InstrumentDef(
    name="str_ens",
    sound_prefix="music_plus.str_ens",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(3, 9), 24, 119)),
)

TIMPANI = InstrumentDef(
    name="timp",
    sound_prefix="music_plus.timp",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(4, 6), 24, 119)),
)

V6_SAW = InstrumentDef(
    name="v6_saw",
    sound_prefix="music_plus.v6_saw",
    lowest_note=24,
    highest_note=119,
    note_map=octave_up(c_octave_a_sample(range(4, 5), 24, 119)),
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
    PIANO.sound_prefix: PIANO,
    HARPSICHORD.sound_prefix: HARPSICHORD,
    HONKYTONK.sound_prefix: HONKYTONK,
    RHODES.sound_prefix: RHODES,
    VIBRA.sound_prefix: VIBRA,
    CE_GUITAR.sound_prefix: CE_GUITAR,
    NYLON_GUITAR.sound_prefix: NYLON_GUITAR,
    GUZHENG.sound_prefix: GUZHENG,
    VIOLIN_SOLO.sound_prefix: VIOLIN_SOLO,
    TRUMPET.sound_prefix: TRUMPET,
    FLUTE.sound_prefix: FLUTE,
    BASS.sound_prefix: BASS,
    ACOUSTIC_BASS.sound_prefix: ACOUSTIC_BASS,
    ACCORDION.sound_prefix: ACCORDION,
    BELL.sound_prefix: BELL,
    BRASS_ENSEMBLE.sound_prefix: BRASS_ENSEMBLE,
    CHURCH_ORGAN.sound_prefix: CHURCH_ORGAN,
    CELESTE.sound_prefix: CELESTE,
    CHOIR.sound_prefix: CHOIR,
    DISTORTION_GUITAR.sound_prefix: DISTORTION_GUITAR,
    ELECTRIC_ORGAN.sound_prefix: ELECTRIC_ORGAN,
    GLOCKENSPIEL.sound_prefix: GLOCKENSPIEL,
    HARP.sound_prefix: HARP,
    MARIMBA.sound_prefix: MARIMBA,
    OBOE.sound_prefix: OBOE,
    ORCHESTRA_HIT.sound_prefix: ORCHESTRA_HIT,
    PAD.sound_prefix: PAD,
    REVERSE_CRASH.sound_prefix: REVERSE_CRASH,
    SAX.sound_prefix: SAX,
    SITAR.sound_prefix: SITAR,
    SQUARE.sound_prefix: SQUARE,
    STRING_ENSEMBLE.sound_prefix: STRING_ENSEMBLE,
    TIMPANI.sound_prefix: TIMPANI,
    V6_SAW.sound_prefix: V6_SAW,
    REAL_KIT.sound_prefix: REAL_KIT,
    LINN_KIT.sound_prefix: LINN_KIT,
}


def get_instrument(sound_prefix):
    """根据 sound_prefix 获取对应的乐器定义。"""
    return _REGISTRY.get(sound_prefix)
