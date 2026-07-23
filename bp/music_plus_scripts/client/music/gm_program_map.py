# -*- coding: utf-8 -*-

"""General MIDI Program Change 到现有乐器音色的归并规则。"""

# MIDI Program Change 使用 0-127 编号。
# 0 表示使用方块默认音色，不在此处显式映射。
PROGRAM_TO_INSTRUMENT = {
    # 钢琴
    1: "music_plus.piano",
    2: "music_plus.piano",
    3: "music_plus.honkytonk",
    4: "music_plus.rhodes",
    5: "music_plus.rhodes",
    6: "music_plus.harpsichord",
    7: "music_plus.harpsichord",

    # 半音阶打击乐器
    8: "music_plus.celeste",
    9: "music_plus.glockenspiel",
    10: "music_plus.music_box",
    11: "music_plus.vibra",
    12: "music_plus.marimba",
    13: "music_plus.marimba",
    14: "music_plus.bell",
    15: "music_plus.guzheng",

    # 管风琴
    16: "music_plus.e_organ",
    17: "music_plus.e_organ",
    18: "music_plus.e_organ",
    19: "music_plus.c_organ",
    20: "music_plus.e_organ",
    21: "music_plus.accordion",
    22: "music_plus.accordion",
    23: "music_plus.accordion",

    # 吉他
    24: "music_plus.nylon_guitar",
    25: "music_plus.ce_guitar",
    26: "music_plus.ce_guitar",
    27: "music_plus.ce_guitar",
    28: "music_plus.ce_guitar",
    29: "music_plus.de_guitar",
    30: "music_plus.de_guitar",
    31: "music_plus.de_guitar",

    # 贝斯
    32: "music_plus.a_bass",
    33: "music_plus.bass",
    34: "music_plus.bass",
    35: "music_plus.bass",
    36: "music_plus.bass",
    37: "music_plus.bass",
    38: "music_plus.bass",
    39: "music_plus.bass",

    # 弦乐 / 管弦打击乐器
    40: "music_plus.violin_solo",
    41: "music_plus.violin_solo",
    42: "music_plus.violin_solo",
    43: "music_plus.bass",
    44: "music_plus.str_ens",
    45: "music_plus.str_ens",
    46: "music_plus.harp",
    47: "music_plus.timp",

    # 合奏音色
    48: "music_plus.str_ens",
    49: "music_plus.str_ens",
    50: "music_plus.str_ens",
    51: "music_plus.str_ens",
    52: "music_plus.choir",
    53: "music_plus.choir",
    54: "music_plus.choir",
    55: "music_plus.orch_hit",

    # 铜管乐器
    56: "music_plus.trumpet",
    57: "music_plus.trumpet",
    58: "music_plus.trumpet",
    59: "music_plus.trumpet",
    60: "music_plus.trumpet",
    61: "music_plus.brs_ens",
    62: "music_plus.brs_ens",
    63: "music_plus.brs_ens",

    # 木管簧片乐器
    64: "music_plus.sax",
    65: "music_plus.sax",
    66: "music_plus.sax",
    67: "music_plus.sax",
    68: "music_plus.oboe",
    69: "music_plus.oboe",
    70: "music_plus.oboe",
    71: "music_plus.oboe",

    # 簧管 / 吹管乐器
    72: "music_plus.flute",
    73: "music_plus.flute",
    74: "music_plus.flute",
    75: "music_plus.flute",
    76: "music_plus.flute",
    77: "music_plus.flute",
    78: "music_plus.flute",
    79: "music_plus.flute",

    # 合成主音
    80: "music_plus.square",
    81: "music_plus.v6_saw",
    82: "music_plus.e_organ",
    83: "music_plus.flute",
    84: "music_plus.de_guitar",
    85: "music_plus.choir",
    86: "music_plus.choir",
    87: "music_plus.bass",

    # 合成铺底
    88: "music_plus.pad",
    89: "music_plus.pad",
    90: "music_plus.pad",
    91: "music_plus.pad",
    92: "music_plus.pad",
    93: "music_plus.pad",
    94: "music_plus.pad",
    95: "music_plus.pad",

    # 民族乐器
    104: "music_plus.sitar",
    105: "music_plus.de_guitar",
    106: "music_plus.de_guitar",
    107: "music_plus.guzheng",
    108: "music_plus.bell",
    109: "music_plus.accordion",
    110: "music_plus.violin_solo",
    111: "music_plus.trumpet",

    # 打击乐器
    112: "music_plus.bell",
    113: "music_plus.bell",
    114: "music_plus.bell",
    115: "music_plus.bell",
    116: "music_plus.timp",
    117: "music_plus.timp",
    118: "music_plus.timp",
    119: "music_plus.rev_crash",

    # 音效暂时没有对应采样，保持未映射并回退方块默认音色。
}

INSTRUMENT_GROUPS = {
    "music_box": {
        "music_plus.bell",
        "music_plus.celeste",
        "music_plus.glockenspiel",
        "music_plus.marimba",
        "music_plus.music_box",
        "music_plus.rev_crash",
        "music_plus.timp",
        "music_plus.vibra",
    },
    "piano": {
        "music_plus.accordion",
        "music_plus.c_organ",
        "music_plus.choir",
        "music_plus.e_organ",
        "music_plus.piano",
        "music_plus.harpsichord",
        "music_plus.honkytonk",
        "music_plus.orch_hit",
        "music_plus.pad",
        "music_plus.rhodes",
        "music_plus.square",
        "music_plus.v6_saw",
    },
    "organ": {
        "music_plus.accordion",
        "music_plus.c_organ",
        "music_plus.e_organ",
    },
    "guitar": {
        "music_plus.de_guitar",
        "music_plus.nylon_guitar",
        "music_plus.ce_guitar",
    },
    "violin": {
        "music_plus.choir",
        "music_plus.harp",
        "music_plus.str_ens",
        "music_plus.violin_solo",
    },
    "bass": {
        "music_plus.a_bass",
        "music_plus.bass",
    },
    "strings": {
        "music_plus.harp",
        "music_plus.str_ens",
        "music_plus.violin_solo",
    },
    "guzheng": {
        "music_plus.guzheng",
        "music_plus.harp",
        "music_plus.sitar",
    },
    "brass": {
        "music_plus.brs_ens",
        "music_plus.trumpet",
    },
    "pipe": {
        "music_plus.accordion",
        "music_plus.flute",
        "music_plus.oboe",
        "music_plus.sax",
    },
    "reed": {
        "music_plus.oboe",
        "music_plus.sax",
    },
    "synth_lead": {
        "music_plus.bass",
        "music_plus.choir",
        "music_plus.de_guitar",
        "music_plus.e_organ",
        "music_plus.flute",
        "music_plus.square",
        "music_plus.v6_saw",
    },
    "synth_pad": {
        "music_plus.pad",
    },
    "percussive": {
        "music_plus.bell",
        "music_plus.rev_crash",
        "music_plus.timp",
    },
    "ethnic": {
        "music_plus.accordion",
        "music_plus.guzheng",
        "music_plus.sitar",
        "music_plus.violin_solo",
        "music_plus.trumpet",
    },
    "drum_kit": {
        "music_plus.real_kit",
        "music_plus.linn_kit",
    },
}


def resolve_program_sound_prefix(default_sound_prefix, instrument_group, program):
    """根据 Program Change 选择最终音色。

    返回 None 表示 MIDI 指定了其它乐器分类，当前方块不播放该音符。
    未映射的 program 回退到方块默认音色。
    """
    if program is None or program == 0:
        return default_sound_prefix

    mapped_sound_prefix = PROGRAM_TO_INSTRUMENT.get(program)
    if mapped_sound_prefix is None:
        return default_sound_prefix

    allowed = INSTRUMENT_GROUPS.get(instrument_group)
    if allowed is not None and mapped_sound_prefix not in allowed:
        return None

    return mapped_sound_prefix
