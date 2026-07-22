# -*- coding: utf-8 -*-

"""乐器定义类

定义 InstrumentDef 数据结构，描述一种乐器的可播放音域和音符映射。
"""


class InstrumentDef(object):
    """乐器定义。

    Attributes:
        name: 乐器标识名（与 sound_prefix 的最后一段对应）
        sound_prefix: 声音 ID 前缀，如 "music_plus.music_box"
        lowest_note: 可播放的最低 MIDI 音符号（含）
        highest_note: 可播放的最高 MIDI 音符号（含）
        note_map: MIDI 音符号到 (声音文件名, pitch 偏移半音数) 的映射
    """

    def __init__(self, name, sound_prefix, lowest_note, highest_note, note_map):
        self.name = name
        self.sound_prefix = sound_prefix
        self.lowest_note = lowest_note
        self.highest_note = highest_note
        self.note_map = note_map

        # 音域内没有精确采样时，使用最近的已有采样，并按两者的
        # MIDI 音符差额追加变调，避免因为采样点稀疏而直接跳过音符。
        if note_map:
            sample_notes = note_map.keys()
            for midi_note in range(lowest_note, highest_note + 1):
                if midi_note in note_map:
                    continue
                nearest_note = min(sample_notes, key=lambda note: abs(note - midi_note))
                sound_name, semitone = note_map[nearest_note]
                note_map[midi_note] = (
                    sound_name,
                    semitone + midi_note - nearest_note,
                )

    def in_range(self, midi_note):
        """判断 MIDI 音符是否在该乐器的可播放范围内。"""
        return self.lowest_note <= midi_note <= self.highest_note

    def resolve(self, midi_note):
        """返回 MIDI 音符对应的 (声音文件名, pitch 偏移半音数)。"""
        if not self.in_range(midi_note):
            return None
        return self.note_map.get(midi_note)
