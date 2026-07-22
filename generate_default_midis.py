# -*- coding: utf-8 -*-

"""将 midi 目录中的 MIDI 文件生成成 Python 2.7 可用的内置曲库模块。"""

from __future__ import print_function

import base64
import hashlib
import os
import sys
import struct
import zlib


try:
    text_type = unicode
except NameError:
    text_type = str


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(ROOT_DIR, "midi")
OUTPUT_PATH = os.path.join(
    ROOT_DIR,
    "bp",
    "music_plus_scripts",
    "utils",
    "default_midis.py",
)
MIDI_EXTENSIONS = (".mid", ".midi")
BASE64_LINE_LENGTH = 100


def _read_varlen(data, offset):
    value = 0
    while True:
        byte = bytearray(data[offset:offset + 1])[0]
        offset += 1
        value = (value << 7) | (byte & 0x7f)
        if not byte & 0x80:
            return value, offset


def _read_track_events(track_data):
    events = []
    offset = 0
    tick = 0
    running_status = None
    while offset < len(track_data):
        delta, offset = _read_varlen(track_data, offset)
        tick += delta
        status = bytearray(track_data[offset:offset + 1])[0]
        if status < 0x80:
            status = running_status
        else:
            offset += 1
            if status < 0xf0:
                running_status = status

        if status == 0xff:
            meta_type = bytearray(track_data[offset:offset + 1])[0]
            offset += 1
            length, offset = _read_varlen(track_data, offset)
            value = track_data[offset:offset + length]
            offset += length
            if meta_type == 0x51 and length == 3:
                tempo = struct.unpack(">I", b"\x00" + value)[0]
                events.append((tick, tempo))
            if meta_type == 0x2f:
                break
        elif status in (0xf0, 0xf7):
            length, offset = _read_varlen(track_data, offset)
            offset += length
        else:
            message_type = status & 0xf0
            offset += 1 if message_type in (0xc0, 0xd0) else 2
    return tick, events


def _get_midi_duration(data):
    if data[:4] != b"MThd":
        raise ValueError("不是有效的 MIDI 文件")
    header_length = struct.unpack(">I", data[4:8])[0]
    header = data[8:8 + header_length]
    track_count, division = struct.unpack(">HH", header[2:6])
    if division & 0x8000:
        raise ValueError("暂不支持 SMPTE 时间格式")

    offset = 8 + header_length
    end_tick = 0
    tempo_events = []
    for track_index in range(track_count):
        if data[offset:offset + 4] != b"MTrk":
            raise ValueError("第 {} 个轨道格式无效".format(track_index + 1))
        track_length = struct.unpack(">I", data[offset + 4:offset + 8])[0]
        track_data = data[offset + 8:offset + 8 + track_length]
        track_end_tick, track_tempos = _read_track_events(track_data)
        end_tick = max(end_tick, track_end_tick)
        tempo_events.extend(track_tempos)
        offset += 8 + track_length

    tempo_events.sort(key=lambda item: item[0])
    current_tick = 0
    current_tempo = 500000
    duration = 0.0
    for tick, tempo in tempo_events:
        if tick > end_tick:
            break
        if tick > current_tick:
            duration += (tick - current_tick) * current_tempo / float(division * 1000000)
            current_tick = tick
        current_tempo = tempo
    duration += (end_tick - current_tick) * current_tempo / float(division * 1000000)
    return duration


def _python_string(value):
    if not isinstance(value, text_type):
        value = value.decode("utf-8")
    literal = repr(value.encode("utf-8"))
    if literal.startswith("b'") or literal.startswith('b"'):
        literal = literal[1:]
    return literal


def _python_literal(value):
    if isinstance(value, dict):
        items = []
        for key in sorted(value.keys()):
            items.append("{}: {}".format(_python_literal(key), _python_literal(value[key])))
        return "{" + ", ".join(items) + "}"
    if isinstance(value, (list, tuple)):
        values = [_python_literal(item) for item in value]
        if isinstance(value, tuple):
            suffix = "," if len(values) == 1 else ""
            return "(" + ", ".join(values) + suffix + ")"
        return "[" + ", ".join(values) + "]"
    if isinstance(value, text_type):
        return _python_string(value)
    return repr(value)


def _load_analyzer():
    scripts_path = os.path.join(ROOT_DIR, "bp")
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)

    if sys.version_info[0] >= 3:
        import builtins
        builtins.unicode = str

        from music_plus_scripts.mido import py2
        py2.PY2 = False

        from music_plus_scripts.utils import midi_payload
        midi_payload.str = lambda value: value
        midi_payload._md5.new = lambda value: hashlib.md5(value)

    from music_plus_scripts.client.music.midi_analyzer import analyze_midi_payload
    from music_plus_scripts.utils.midi_payload import pack_midi_payload
    return analyze_midi_payload, pack_midi_payload


def _build_module(songs):
    lines = [
        "# -*- coding: utf-8 -*-",
        "",
        '"""由 generate_default_midis.py 自动生成，请勿手动修改。"""',
        "",
        "import base64",
        "",
        'from music_plus_scripts.utils.midi_payload import CODEC_ZLIB, binary_to_wire',
        "",
        "",
        "_DEFAULT_MIDIS = {",
    ]
    for song in songs:
        lines.extend([
            '    "{}": {{'.format(song["md5"]),
            '        "title": {},'.format(_python_string(song["title"])),
            '        "duration": {:.6f},'.format(song["duration"]),
            '        "analysis": {},'.format(_python_literal(song["analysis"])),
            '        "size": {},'.format(song["size"]),
            '        "data": (',
        ])
        encoded = song["data"]
        for offset in range(0, len(encoded), BASE64_LINE_LENGTH):
            lines.append('            "{}"'.format(encoded[offset:offset + BASE64_LINE_LENGTH]))
        lines.extend(["        ),", "    },"])
    lines.extend([
        "}",
        "",
        "DEFAULT_MIDI_KEYS = (",
    ])
    for song in songs:
        lines.append('    "{}",'.format(song["md5"]))
    lines.extend([
        ")",
        "",
        "_PAYLOAD_CACHE = {}",
        "",
        "",
        "def is_default_midi(midi_md5):",
        "    return bool(midi_md5) and midi_md5 in _DEFAULT_MIDIS",
        "",
        "",
        "def get_default_midi(midi_md5):",
        "    info = _DEFAULT_MIDIS.get(midi_md5)",
        "    if info is None:",
        "        return None",
        "    payload = _PAYLOAD_CACHE.get(midi_md5)",
        "    if payload is None:",
        '        compressed = base64.b64decode("".join(info["data"]))',
        "        payload = {",
        '            "data": binary_to_wire(compressed),',
        '            "codec": CODEC_ZLIB,',
        '            "md5": midi_md5,',
        '            "size": info["size"],',
        "        }",
        "        _PAYLOAD_CACHE[midi_md5] = payload",
        "    return payload",
        "",
        "",
        "def get_default_midi_meta(midi_md5):",
        "    info = _DEFAULT_MIDIS.get(midi_md5)",
        "    if info is None:",
        "        return None",
        "    return {",
        '        "title": info["title"],',
        '        "duration": info["duration"],',
        '        "analysis": info["analysis"],',
        "    }",
        "",
    ])
    return "\n".join(lines)


def main():
    analyze_midi_payload, pack_midi_payload = _load_analyzer()
    midi_dir = MIDI_DIR
    output_path = OUTPUT_PATH
    if not isinstance(midi_dir, text_type):
        midi_dir = midi_dir.decode("utf-8")
        output_path = output_path.decode("utf-8")
    filenames = sorted(
        filename for filename in os.listdir(midi_dir)
        if os.path.splitext(filename)[1].lower() in MIDI_EXTENSIONS
    )
    if not filenames:
        raise SystemExit("midi 目录中没有 .mid 或 .midi 文件")

    songs = []
    for filename in filenames:
        path = os.path.join(midi_dir, filename)
        with open(path, "rb") as midi_file:
            data = midi_file.read()
        compressed = zlib.compress(data, 9)
        songs.append({
            "title": os.path.splitext(filename)[0],
            "md5": hashlib.md5(data).hexdigest(),
            "duration": _get_midi_duration(data),
            "analysis": analyze_midi_payload(pack_midi_payload(data)),
            "size": len(data),
            "data": base64.b64encode(compressed).decode("ascii"),
        })

    source = _build_module(songs)
    with open(output_path, "wb") as output_file:
        output_file.write(source.encode("utf-8"))
    print("Generated {} default MIDI files".format(len(songs)))


if __name__ == "__main__":
    main()
