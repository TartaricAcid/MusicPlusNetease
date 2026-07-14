# -*- coding: utf-8 -*-

"""乐器音符映射构建工具。"""


def c_octave_a_sample(sample_octaves, lowest_note=None, highest_note=None):
    """用 aN 样本覆盖同八度 C-B。"""
    note_map = {}
    for octave in sample_octaves:
        sample_name = "a{}".format(octave)
        sample_note = midi_note(octave, 9)
        for note_index in range(12):
            note = midi_note(octave, note_index)
            if lowest_note is not None and note < lowest_note:
                continue
            if highest_note is not None and note > highest_note:
                continue
            note_map[note] = (sample_name, note - sample_note)
    return note_map


def named_notes(start_note, names):
    note_map = {}
    for i, name in enumerate(names):
        note_map[start_note + i] = (name, 0)
    return note_map


def percussion(prefix, has_open_hat=True):
    note_map = {
        35: ("{}_kick".format(prefix), 0),
        36: ("{}_kick".format(prefix), 0),
        38: ("{}_snare".format(prefix), 0),
        40: ("{}_snare".format(prefix), 0),
        42: ("{}_ch".format(prefix), 0),
        44: ("{}_pedal".format(prefix), 0),
        47: ("{}_lt".format(prefix), 0),
        48: ("{}_mt".format(prefix), 0),
        49: ("{}_crash".format(prefix), 0),
        50: ("{}_ht".format(prefix), 0),
        51: ("{}_ride".format(prefix), 0),
    }
    if has_open_hat:
        note_map[46] = ("{}_oh".format(prefix), 0)
    else:
        note_map[46] = ("{}_ch".format(prefix), 0)
    return note_map


def midi_note(octave, note_index):
    return (octave + 1) * 12 + note_index
