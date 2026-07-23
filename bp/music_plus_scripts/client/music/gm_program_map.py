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
    8: "music_plus.music_box",
    9: "music_plus.music_box",
    10: "music_plus.music_box",
    11: "music_plus.vibra",
    12: "music_plus.music_box",
    13: "music_plus.music_box",
    14: "music_plus.music_box",
    15: "music_plus.guzheng",

    # 管风琴

    # 吉他
    24: "music_plus.nylon_guitar",
    25: "music_plus.ce_guitar",
    26: "music_plus.ce_guitar",
    27: "music_plus.ce_guitar",
    28: "music_plus.ce_guitar",
    29: "music_plus.ce_guitar",
    30: "music_plus.ce_guitar",
    31: "music_plus.ce_guitar",

    # 贝斯
    32: "music_plus.bass",
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
    44: "music_plus.violin_solo",
    45: "music_plus.violin_solo",
    46: "music_plus.guzheng",

    # 合奏音色
    48: "music_plus.violin_solo",
    49: "music_plus.violin_solo",
    50: "music_plus.violin_solo",
    51: "music_plus.violin_solo",

    # 铜管乐器
    56: "music_plus.trumpet",
    57: "music_plus.trumpet",
    58: "music_plus.trumpet",
    59: "music_plus.trumpet",
    60: "music_plus.trumpet",
    61: "music_plus.trumpet",
    62: "music_plus.trumpet",
    63: "music_plus.trumpet",

    # 木管簧片乐器

    # 簧管 / 吹管乐器
    72: "music_plus.flute",
    73: "music_plus.flute",
    74: "music_plus.flute",
    75: "music_plus.flute",
    77: "music_plus.flute",
    78: "music_plus.flute",
    79: "music_plus.flute",

    # 合成主音
    # 合成铺底
    # 合成效果音

    # 民族乐器
    104: "music_plus.guzheng",
    105: "music_plus.guzheng",
    106: "music_plus.guzheng",
    107: "music_plus.guzheng",
    108: "music_plus.guzheng",
    110: "music_plus.violin_solo",
    111: "music_plus.trumpet",

    # 打击乐器
    # 音效
}

INSTRUMENT_GROUPS = {
    "music_box": {
        "music_plus.music_box",
        "music_plus.vibra",
    },
    "piano": {
        "music_plus.piano",
        "music_plus.harpsichord",
        "music_plus.honkytonk",
        "music_plus.rhodes",
    },
    "guitar": {
        "music_plus.nylon_guitar",
        "music_plus.ce_guitar",
    },
    "violin": {
        "music_plus.violin_solo",
    },
    "bass": {
        "music_plus.bass",
    },
    "guzheng": {
        "music_plus.guzheng",
    },
    "brass": {
        "music_plus.trumpet",
    },
    "pipe": {
        "music_plus.flute",
    },
    "ethnic": {
        "music_plus.guzheng",
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
