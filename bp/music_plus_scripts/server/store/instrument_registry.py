# -*- coding: utf-8 -*-

"""服务端方块乐器播放配置注册表。"""

PIANO_BLOCK = "music_plus:music_plus_steinway"

# ─── 乐器注册表 ──────────────────────────────────────────────────────────────
# 全局映射：ID → 乐器播放配置
# 新增乐器时只需在此字典中添加一条记录。
#
# 每条记录的字段:
#   sound_prefix   - 声音 ID 前缀，对应 sound_definitions.json 中的条目
#   instrument_group - Program Change 可使用的乐器组
#   enable_note_off - 是否响应 note_off 截断（弦/管乐器需要，打击/八音盒不需要）
#   particle_range  - 可选粒子三轴偏移范围 ((x1,x2),(y1,y2),(z1,z2))，缺省为固定点
# ─────────────────────────────────────────────────────────────────────────────────
INSTRUMENT_REGISTRY = {
    "music_plus:music_plus_music_box": {
        "sound_prefix": "music_plus.music_box",
        "instrument_group": "music_box",
        "enable_note_off": False,
    },
    PIANO_BLOCK: {
        "sound_prefix": "music_plus.steinway",
        "instrument_group": "piano",
        "enable_note_off": True,
        "particle_range": ((-1.0, 1.0), (0.0, 0.5), (-1.0, 1.0)),
    },
    "music_plus:music_plus_harpsichord": {
        "sound_prefix": "music_plus.harpsichord",
        "instrument_group": "piano",
        "enable_note_off": True,
    },
    "music_plus:music_plus_honkytonk": {
        "sound_prefix": "music_plus.honkytonk",
        "instrument_group": "piano",
        "enable_note_off": True,
    },
    "music_plus:music_plus_rhodes": {
        "sound_prefix": "music_plus.rhodes",
        "instrument_group": "piano",
        "enable_note_off": True,
    },
    "music_plus:music_plus_vibra": {
        "sound_prefix": "music_plus.vibra",
        "instrument_group": "music_box",
        "enable_note_off": True,
    },
    "music_plus:music_plus_ce_guitar": {
        "sound_prefix": "music_plus.ce_guitar",
        "instrument_group": "guitar",
        "enable_note_off": True,
    },
    "music_plus:music_plus_nylon_guitar": {
        "sound_prefix": "music_plus.nylon_guitar",
        "instrument_group": "guitar",
        "enable_note_off": True,
    },
    "music_plus:music_plus_guzheng": {
        "sound_prefix": "music_plus.guzheng",
        "instrument_group": "guzheng",
        "enable_note_off": True,
    },
    "music_plus:music_plus_violin_solo": {
        "sound_prefix": "music_plus.violin_solo",
        "instrument_group": "violin",
        "enable_note_off": True,
    },
    "music_plus:music_plus_trumpet": {
        "sound_prefix": "music_plus.trumpet",
        "instrument_group": "brass",
        "enable_note_off": True,
    },
    "music_plus:music_plus_flute": {
        "sound_prefix": "music_plus.flute",
        "instrument_group": "pipe",
        "enable_note_off": True,
    },
    "music_plus:music_plus_bass": {
        "sound_prefix": "music_plus.bass",
        "instrument_group": "bass",
        "enable_note_off": True,
    },
    "music_plus:music_plus_real_kit": {
        "sound_prefix": "music_plus.real_kit",
        "instrument_group": "drum_kit",
        "enable_note_off": False,
    },
    "music_plus:music_plus_linn_kit": {
        "sound_prefix": "music_plus.linn_kit",
        "instrument_group": "drum_kit",
        "enable_note_off": False,
    },
}

SEATED_INSTRUMENT_BLOCKS = frozenset((PIANO_BLOCK,))


def get_instrument_config(block_name):
    return INSTRUMENT_REGISTRY.get(block_name)


def get_paper_tape_instrument_config(block_name):
    if block_name in SEATED_INSTRUMENT_BLOCKS:
        return None
    return get_instrument_config(block_name)


def get_seated_instrument_config(block_name):
    if block_name not in SEATED_INSTRUMENT_BLOCKS:
        return None
    return get_instrument_config(block_name)
