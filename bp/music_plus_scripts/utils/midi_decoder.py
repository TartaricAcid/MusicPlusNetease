# -*- coding: utf-8 -*-

"""MIDI 解码器

将 base64 编码的 MIDI 文件解码为排序后的音符事件列表。

输出格式: [[absolute_time, type, channel, data1, data2], ...] 按时间升序排列。

type: 0=note_off, 1=note_on, 2=sustain_pedal
note_on/off: data1=midi_note, data2=velocity
sustain: data1=pedal_state(1=down,0=up), data2=0
"""

import base64
import io

from music_plus_scripts.mido import MidiFile

NOTE_OFF = 0
NOTE_ON = 1
SUSTAIN = 2


def decode_midi_base64(midi_base64):
    """将 base64 编码的 MIDI 数据解码为音符事件列表。

    Args:
        midi_base64: base64 编码的 MIDI 文件字符串

    Returns:
        按时间升序排列的事件列表: [[time, type, channel, data1, data2], ...]
        time 为秒，type: 0=note_off / 1=note_on / 2=sustain_pedal
        channel: 0~15，velocity 为 0.0~1.0
    """
    midi_bytes = base64.b64decode(midi_base64)
    midi_file = MidiFile(file=io.BytesIO(midi_bytes), charset='utf-8')
    return _extract_events(midi_file)


def _extract_events(midi_file):
    """从 MidiFile 对象中提取所有 note_on / note_off / CC#64 事件。

    利用 MidiFile.__iter__ 自动合并多轨并处理 tempo 变化，
    返回按绝对时间排序的事件列表。
    """
    events = []
    current_time = 0.0

    for msg in midi_file:
        current_time += msg.time

        # 音频停止事件
        if msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            events.append([
                round(current_time, 4),
                NOTE_OFF,
                msg.channel,
                msg.note,
                0,
            ])

        # 音符开始时间，此时 data2 需要额外记录 velocity
        elif msg.type == 'note_on' and msg.velocity > 0:
            events.append([
                round(current_time, 4),
                NOTE_ON,
                msg.channel,
                msg.note,
                round(msg.velocity / 127.0, 2),
            ])

        # CC#64 延音踏板: value >= 64 踩下, < 64 松开
        elif msg.type == 'control_change' and msg.control == 64:
            events.append([
                round(current_time, 4),
                SUSTAIN,
                msg.channel,
                1 if msg.value >= 64 else 0,
                0,
            ])

    return events
