# -*- coding: utf-8 -*-

"""服务端乐器播放配置注册表。"""

PIANO_BLOCK = "music_plus:music_plus_piano"
HARPSICHORD_BLOCK = "music_plus:music_plus_harpsichord"
HONKYTONK_BLOCK = "music_plus:music_plus_honkytonk"
VIBRA_BLOCK = "music_plus:music_plus_vibra"
GUZHENG_BLOCK = "music_plus:music_plus_guzheng"
ELECTRONIC_KEYBOARD_BLOCK = "music_plus:music_plus_electronic_keyboard"

# ─── 乐器注册表 ──────────────────────────────────────────────────────────────
# 全局映射：ID → 乐器播放配置
# 新增乐器时只需在此字典中添加一条记录。
#
# 每条记录的字段:
#   display_name   - 玩家界面和世界标记使用的中文名称
#   target_id      - MIDI 分析和乐器 UI 使用的目标标识
#   sound_prefix   - 声音 ID 前缀，对应 sound_definitions.json 中的条目
#   instrument_group - Program Change 可使用的乐器组
#   percussion_sound_prefix - all 分类使用的鼓组声音 ID 前缀
#   enable_note_off - 是否允许客户端音色响应 note_off 截断
#   animation_profile - 可选的演奏动画配置
#   particle_range  - 可选粒子局部三轴偏移范围 ((x1,x2),(y1,y2),(z1,z2))，随方块朝向旋转
#   seat_offset     - 可选座位局部偏移 (横向, 高度, 前向)，相对方块中心并随方块旋转
# ─────────────────────────────────────────────────────────────────────────────────
BLOCK_INSTRUMENT_REGISTRY = {
    "music_plus:music_plus_synthesizer_player": {
        "display_name": "合成播放器",
        "target_id": "synthesizer_player",
        "sound_prefix": "music_plus.piano",
        "instrument_group": "all",
        "percussion_sound_prefix": "music_plus.real_kit",
        "enable_note_off": True,
    },
    "music_plus:music_plus_music_box": {
        "display_name": "八音盒",
        "sound_prefix": "music_plus.music_box",
        "instrument_group": "music_box",
        "enable_note_off": False,
    },
    PIANO_BLOCK: {
        "display_name": "钢琴",
        "target_id": "piano",
        "sound_prefix": "music_plus.piano",
        "instrument_group": "piano",
        "enable_note_off": True,
        "animation_profile": "piano",
        "particle_range": ((-1.0, 1.0), (0.0, 0.5), (-1.0, 1.0)),
        "seat_offset": (0.0, 0.0, 2.375),
    },
    HARPSICHORD_BLOCK: {
        "display_name": "羽管键琴",
        "target_id": "harpsichord",
        "sound_prefix": "music_plus.harpsichord",
        "instrument_group": "piano",
        "enable_note_off": True,
        "animation_profile": "piano",
        "particle_range": ((-1.0, 1.0), (0.0, 0.5), (-1.0, 1.0)),
        "seat_offset": (0.0, 0.0, 2.375),
    },
    HONKYTONK_BLOCK: {
        "display_name": "酒吧钢琴",
        "target_id": "honkytonk",
        "sound_prefix": "music_plus.honkytonk",
        "instrument_group": "piano",
        "enable_note_off": True,
        "animation_profile": "piano",
        "particle_range": ((-1, 1), (0.0, 0.5), (0.625, 0.875)),
        "seat_offset": (0.0, 0.125, 1.5),
    },
    VIBRA_BLOCK: {
        "display_name": "颤音琴",
        "target_id": "vibra",
        "sound_prefix": "music_plus.vibra",
        "instrument_group": "music_box",
        "enable_note_off": True,
        "animation_profile": "vibra",
        "particle_range": ((-1, 1), (0.25, 0.75), (0, 0)),
        "seat_offset": (0.0, 0.25, 0.875),
    },
    GUZHENG_BLOCK: {
        "display_name": "古筝",
        "target_id": "guzheng",
        "sound_prefix": "music_plus.guzheng",
        "instrument_group": "guzheng",
        "enable_note_off": True,
        "animation_profile": "guzheng",
        "particle_range": ((-1.25, 1.25), (0.25, 0.75), (0, 0)),
        "seat_offset": (0.0, 0.2, 0.5625),
    },
    ELECTRONIC_KEYBOARD_BLOCK: {
        "display_name": "电子琴",
        "target_id": "electronic_keyboard",
        "sound_prefix": "music_plus.piano",
        "instrument_group": "all",
        "percussion_sound_prefix": "music_plus.linn_kit",
        "enable_note_off": True,
        "animation_profile": "piano",
        "particle_range": ((-1.25, 1.25), (0.25, 0.75), (0, 0)),
        "seat_offset": (0.0, 0.125, 0.9375),
    }
}

ITEM_INSTRUMENT_REGISTRY = {
    "music_plus:bass": {
        "display_name": "贝斯",
        "target_id": "bass",
        "sound_prefix": "music_plus.bass",
        "instrument_group": "bass",
        "enable_note_off": True,
        "particle_range": ((-0.25, 0.25), (-0.125, 0.25), (-0.25, 0.25)),
        "animation_profile": "bass",
    },
}

SEATED_INSTRUMENT_BLOCKS = frozenset((
    PIANO_BLOCK,
    HARPSICHORD_BLOCK,
    HONKYTONK_BLOCK,
    VIBRA_BLOCK,
    GUZHENG_BLOCK,
    ELECTRONIC_KEYBOARD_BLOCK,
))


def get_instrument_config(block_name):
    return BLOCK_INSTRUMENT_REGISTRY.get(block_name)


def get_handheld_instrument_config(item_name):
    return ITEM_INSTRUMENT_REGISTRY.get(item_name)


def get_paper_tape_instrument_config(block_name):
    if block_name in SEATED_INSTRUMENT_BLOCKS:
        return None
    return get_instrument_config(block_name)


def get_seated_instrument_config(block_name):
    if block_name not in SEATED_INSTRUMENT_BLOCKS:
        return None
    return get_instrument_config(block_name)
