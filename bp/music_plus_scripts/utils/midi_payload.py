# -*- coding: utf-8 -*-

import _md5
import zlib

CODEC_RAW = "raw"
CODEC_ZLIB = "zlib"

DATA_KEY = "data"
CODEC_KEY = "codec"
MD5_KEY = "md5"
SIZE_KEY = "size"

COMPRESS_THRESHOLD = 2048
COMPRESS_MIN_SAVING = 128
COMPRESS_MIN_RATIO = 0.9
COMPRESS_LEVEL = 6


def binary_to_wire(data):
    """将裸二进制数据转换为可传输/存储的字符串。运行环境为 CPython 2.7。"""
    return str(data)


def wire_to_binary(data):
    """将 binary_to_wire 生成的字符串还原为裸二进制数据。"""
    return str(data)


def pack_midi_payload(midi_bytes):
    midi_bytes = str(midi_bytes)
    raw_size = len(midi_bytes)
    payload_bytes = midi_bytes
    codec = CODEC_RAW

    if raw_size >= COMPRESS_THRESHOLD:
        compressed = zlib.compress(midi_bytes, COMPRESS_LEVEL)
        if _should_use_compressed(raw_size, len(compressed)):
            payload_bytes = compressed
            codec = CODEC_ZLIB

    return {
        DATA_KEY: binary_to_wire(payload_bytes),
        CODEC_KEY: codec,
        MD5_KEY: _md5.new(midi_bytes).hexdigest(),
        SIZE_KEY: raw_size,
    }


def unpack_midi_payload(payload):
    if not isinstance(payload, dict):
        return wire_to_binary(payload)

    payload_bytes = wire_to_binary(payload.get(DATA_KEY, ""))
    codec = payload.get(CODEC_KEY, CODEC_RAW)
    if codec == CODEC_RAW:
        return payload_bytes
    if codec == CODEC_ZLIB:
        return zlib.decompress(payload_bytes)
    raise ValueError("Unsupported MIDI payload codec: {}".format(codec))


def get_midi_payload_md5(payload):
    if isinstance(payload, dict):
        midi_md5 = payload.get(MD5_KEY)
        if midi_md5:
            return midi_md5
    data = unpack_midi_payload(payload)
    return _md5.new(data).hexdigest()


def _should_use_compressed(raw_size, compressed_size):
    if raw_size - compressed_size < COMPRESS_MIN_SAVING:
        return False
    return compressed_size <= int(raw_size * COMPRESS_MIN_RATIO)
