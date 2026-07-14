# -*- coding: utf-8 -*-

"""乐器定义类

定义 InstrumentDef 数据结构，描述一种乐器的采样音域范围。
"""


class InstrumentDef(object):
    """乐器定义。

    Attributes:
        name: 乐器标识名（与 sound_prefix 的最后一段对应）
        sound_prefix: 声音 ID 前缀，如 "music_plus.music_box"
        lowest_note: 可用采样的最低 MIDI 音符号（含）
        highest_note: 可用采样的最高 MIDI 音符号（含）
        pitch_shift_range: 允许的 pitch 偏移半音数（0=不允许偏移，仅播放采样范围内的音符）
        note_offset: MIDI 音符号到采样文件的偏移量（如八音盒为 12，表示采样比标注低一个八度）
    """

    def __init__(self, name, sound_prefix, lowest_note, highest_note, pitch_shift_range=0, note_offset=0):
        self.name = name
        self.sound_prefix = sound_prefix
        self.lowest_note = lowest_note
        self.highest_note = highest_note
        self.pitch_shift_range = pitch_shift_range
        self.note_offset = note_offset

    def in_range(self, midi_note):
        """判断 MIDI 音符是否在该乐器的可播放范围内。

        考虑 pitch_shift_range 允许的额外偏移。
        """
        low = self.lowest_note - self.pitch_shift_range
        high = self.highest_note + self.pitch_shift_range
        return low <= midi_note <= high
