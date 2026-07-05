# -*- coding: utf-8 -*-

"""ABC 记谱法解析器

将 ABC 格式文本解析为音符事件序列，供音乐盒播放使用。
每个事件为 (notes, length) 元组：
  - notes: 包含 {"name": str, "pitch": float} 的列表（空列表 = 休止符）
  - length: 以八分音符为单位的时值
"""

import math
import re

MUSICBOX_LOWEST_MIDI_NOTE = 69
MUSICBOX_HIGHEST_MIDI_NOTE = 92
MUSICBOX_NOTE_NAMES = (
    "c", "cs", "d", "ds", "e", "f", "fs", "g", "gs", "a", "as", "b"
)

KEY_SIGNATURE_ACCIDENTALS = {
    "G": {"F": 1},
    "D": {"F": 1, "C": 1},
    "A": {"F": 1, "C": 1, "G": 1},
    "E": {"F": 1, "C": 1, "G": 1, "D": 1},
    "F": {"B": -1},
    "Bb": {"B": -1, "E": -1},
    "C": {},
}

BASE_SEMITONES = {
    "C": 0,
    "D": 2,
    "E": 4,
    "F": 5,
    "G": 7,
    "A": 9,
    "B": 11,
}


def parse_abc(abc_text, sound_prefix, key_name=None):
    """解析 ABC 文本，返回事件列表。

    Args:
        abc_text: ABC 格式的乐谱文本
        sound_prefix: 声音 ID 前缀，如 "music_plus.music_box"
        key_name: 调号名称，None 表示从 K: 行自动检测

    Returns:
        events 列表，每个元素为 (notes, length) 元组
    """
    detected_key = key_name
    body = []
    for line in abc_text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("w:"):
            continue
        key_match = re.match(r"^K:\s*(\w+)", line)
        if key_match and detected_key is None:
            detected_key = key_match.group(1)
            continue
        if re.match(r"^[A-Z]:", line):
            continue
        body.append(line)

    if detected_key is None:
        detected_key = "C"

    text = " ".join(body).replace("\\", " ")
    events = []
    cursor = 0
    accidentals = KEY_SIGNATURE_ACCIDENTALS.get(detected_key, {})

    while cursor < len(text):
        char = text[cursor]
        if char == '"':
            cursor = _skip_quoted(text, cursor)
        elif char == "[":
            if cursor + 1 < len(text) and text[cursor + 1] == "|":
                cursor += 2
            else:
                cursor = _parse_chord(text, cursor + 1, events, accidentals, sound_prefix)
        elif char in "|]":
            cursor += 1
        elif char == "z":
            cursor = _parse_rest(text, cursor, events)
        elif _is_note_start(text, cursor):
            note, length, cursor = _parse_note(text, cursor, accidentals, sound_prefix)
            events.append(([note], length))
        else:
            cursor += 1

    return events


def _skip_quoted(text, cursor):
    cursor += 1
    while cursor < len(text) and text[cursor] != '"':
        cursor += 1
    return cursor + 1


def _parse_chord(text, cursor, events, accidentals, sound_prefix):
    notes = []
    chord_length = 0
    while cursor < len(text) and text[cursor] != "]":
        if _is_note_start(text, cursor):
            note, length, cursor = _parse_note(text, cursor, accidentals, sound_prefix)
            notes.append(note)
            chord_length = max(chord_length, length)
        else:
            cursor += 1
    if notes:
        events.append((notes, chord_length or 1))
    return cursor + 1


def _parse_rest(text, cursor, events):
    cursor += 1
    length, cursor = _parse_length(text, cursor)
    events.append(([], length))
    return cursor


def _parse_note(text, cursor, accidentals, sound_prefix):
    accidental = None
    if text[cursor] in "^_=":
        accidental = text[cursor]
        cursor += 1

    note_char = text[cursor]
    cursor += 1
    octave = 5 if note_char.islower() else 4
    note_name = note_char.upper()

    while cursor < len(text) and text[cursor] in "',":
        if text[cursor] == "'":
            octave += 1
        else:
            octave -= 1
        cursor += 1

    length, cursor = _parse_length(text, cursor)
    while cursor < len(text) and text[cursor] == "-":
        cursor += 1

    semitone = BASE_SEMITONES[note_name]
    if accidental == "^":
        semitone += 1
    elif accidental == "_":
        semitone -= 1
    elif accidental is None:
        semitone += accidentals.get(note_name, 0)

    midi_note = (octave + 1) * 12 + semitone
    return _midi_to_musicbox(midi_note, sound_prefix), length, cursor


def _parse_length(text, cursor):
    start = cursor
    while cursor < len(text) and text[cursor].isdigit():
        cursor += 1
    if start == cursor:
        return 1, cursor
    return int(text[start:cursor]), cursor


def _is_note_start(text, cursor):
    char = text[cursor]
    if char in "ABCDEFGabcdefg":
        return True
    return char in "^_=" and cursor + 1 < len(text) and text[cursor + 1] in "ABCDEFGabcdefg"


def _midi_to_musicbox(midi_note, sound_prefix):
    """将 MIDI 音符号转换为声音名称和 pitch 参数。

    Args:
        midi_note: MIDI 音符编号
        sound_prefix: 声音 ID 前缀，最终拼接为 "{sound_prefix}.c5" 等
    """
    sample = max(MUSICBOX_LOWEST_MIDI_NOTE, min(MUSICBOX_HIGHEST_MIDI_NOTE, midi_note))
    note_name = MUSICBOX_NOTE_NAMES[sample % 12]
    sample_octave = sample // 12 - 1
    if note_name.endswith("s"):
        sound_name = "{}{}s".format(note_name[0], sample_octave)
    else:
        sound_name = "{}{}".format(note_name, sample_octave)
    return {
        "name": "{}.{}".format(sound_prefix, sound_name),
        "pitch": math.pow(2.0, (midi_note - sample) / 12.0),
    }
