# -*- coding: utf-8 -*-

"""方块乐器通用处理模块

纸带右击方块乐器时，根据方块 ID 查找对应的乐器配置，
解码 MIDI 数据并发送到客户端播放。

新增方块乐器只需在 BLOCK_INSTRUMENT_REGISTRY 中注册即可。
"""

import ast

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.mido.midi_decoder import decode_midi_base64
from music_plus_scripts.server.object.block_object import BlockObject
from music_plus_scripts.server.object.block_use_object import BlockUseObject
from music_plus_scripts.server.object.item_use_block_object import ItemUseBlockObject
from music_plus_scripts.server.utils.item_utils import item_dict_is_empty

PAPER_TAPE_ITEM = "music_plus:paper_tape"
PAPER_TAPE_DATA_KEY = "music_plus:paper_tape"

# 默认测试曲目的 base64 MIDI（纸带无自定义数据时使用）
DEFAULT_MIDI_BASE64 = (
    "TVRoZAAAAAYAAQACAYBNVHJrAAAAQwD/AQljcmVhdG9yOiAA/wEeTGlseVBvbmQgMi4yNC4xICAgICAgICAgICAgICAgAP9YBAQCGAgA/"
    "1EDD0JA4wD/LwBNVHJrAAABfAD/AwVcbmV3OgD/WQIAAACQQ1qBQJBDAACQSFqBQJBIAACQTFqDAJBMAACQTFqBQJBMAACQTFqBQJBMAA"
    "CQTFqDAJBMAACQSlqBQJBKAACQTFqBQJBMAACQSlqBQJBKAACQSFqBQJBIAACQSFqGAJBIAACQQ1qBQJBDAACQSFqBQJBIAACQTFqDAJBM"
    "AACQSFqBQJBIAACQTFqBQJBMAACQT1qDAJBPAACQTVqBQJBNAACQTFqBQJBMAACQSlqJAJBKAACQT1qBQJBPAACQTVqBQJBNAACQTFqDAJB"
    "MAACQTFqBQJBMAACQSlqBQJBKAACQSFqDAJBIAACQSlqBQJBKAACQTFqBQJBMAACQT1qBQJBPAACQTVqBQJBNAACQTVqGAJBNAACQRVqBQJB"
    "FAACQRFqBQJBEAACQQ1qDAJBDAACQR1qBQJBHAACQSFqBQJBIAACQSlqDAJBKAACQTFqBQJBMAACQSlqBQJBKAACQSFqJAJBIAIMA/y8A"
)

# ─── 方块乐器注册表 ──────────────────────────────────────────────────────────────
# 全局映射：方块 ID → 乐器播放配置
# 新增方块乐器时只需在此字典中添加一条记录。
#
# 每条记录的字段:
#   sound_prefix   - 声音 ID 前缀，对应 sound_definitions.json 中的条目
#   enable_note_off - 是否响应 note_off 截断（弦/管乐器需要，打击/八音盒不需要）
# ─────────────────────────────────────────────────────────────────────────────────

BLOCK_INSTRUMENT_REGISTRY = {
    "music_plus:music_plus_music_box": {
        "sound_prefix": "music_plus.music_box",
        "enable_note_off": False,
    },
    "music_plus:music_plus_steinway": {
        "sound_prefix": "music_plus.steinway",
        "enable_note_off": True,
    },
    "music_plus:music_plus_harpsichord": {
        "sound_prefix": "music_plus.harpsichord",
        "enable_note_off": True,
    },
    "music_plus:music_plus_ce_guitar": {
        "sound_prefix": "music_plus.ce_guitar",
        "enable_note_off": True,
    },
    "music_plus:music_plus_nylon_guitar": {
        "sound_prefix": "music_plus.nylon_guitar",
        "enable_note_off": True,
    },
    "music_plus:music_plus_guzheng": {
        "sound_prefix": "music_plus.guzheng",
        "enable_note_off": True,
    },
    "music_plus:music_plus_violin_solo": {
        "sound_prefix": "music_plus.violin_solo",
        "enable_note_off": True,
    },
    "music_plus:music_plus_real_kit": {
        "sound_prefix": "music_plus.real_kit",
        "enable_note_off": False,
    },
    "music_plus:music_plus_linn_kit": {
        "sound_prefix": "music_plus.linn_kit",
        "enable_note_off": False,
    },
}

factory = serverApi.GetEngineCompFactory()
game = factory.CreateGame(levelId)


def is_paper_tape(item_name):
    return item_name == PAPER_TAPE_ITEM


def get_block_instrument(block_name):
    return BLOCK_INSTRUMENT_REGISTRY.get(block_name)


def handle_paper_tape_insert(args, instrument_config):
    use_obj = ItemUseBlockObject(args)
    item_obj = use_obj.get_item()

    if item_obj.is_empty():
        return

    use_obj.send_msg("stop_music_at_pos")

    old_tape = get_stored_paper_tape(use_obj)
    if not item_dict_is_empty(old_tape):
        use_obj.drop_items(old_tape)

    tape_item = item_obj.copy_with_count(1)
    be_data = use_obj.get_block_entity_data()
    be_data[PAPER_TAPE_DATA_KEY] = str(tape_item)
    use_obj.set_block_entity_data(be_data)

    use_obj.reduce_player_item(1)
    use_obj.swing_hand()

    game.AddTimer(0.2, _play_midi_sound, instrument_config, tape_item, use_obj)


def handle_block_instrument_remove(args):
    block = BlockObject(args)
    tape = get_stored_paper_tape(block)
    if not item_dict_is_empty(tape):
        block.drop_items(tape)
    Call("*", "stop_music_at_pos", {
        "pos": block.get_pos()
    })


def handle_paper_tape_takeout(args):
    use_obj = BlockUseObject(args)
    item_obj = use_obj.get_item()

    # 必须是空手
    if not item_obj.is_empty():
        return

    # 总是挥手
    use_obj.swing_hand()

    tape = get_stored_paper_tape(use_obj)
    if item_dict_is_empty(tape):
        return

    be_data = use_obj.get_block_entity_data()
    be_data[PAPER_TAPE_DATA_KEY] = None
    use_obj.set_block_entity_data(be_data)

    Call("*", "stop_music_at_pos", {
        "pos": use_obj.get_pos()
    })

    use_obj.drop_items(tape)
    use_obj.cancel()

    # 避免重复收放物品
    from music_plus_scripts.server.event.block_use import record_item_use_cooldown
    record_item_use_cooldown(use_obj.get_player().entity_id)


def get_stored_paper_tape(block):
    be_data = block.get_block_entity_data()
    tape_data = be_data[PAPER_TAPE_DATA_KEY]
    if tape_data is None:
        return {}
    return ast.literal_eval(tape_data)


def _get_notes_from_tape(item_dict):
    """从纸带物品的 userData 中提取 MIDI 数据并解码为音符列表。

    userData 中应包含 "midi" 键，值为 base64 编码的 MIDI 文件字符串。
    如果纸带没有写入自定义数据，返回默认测试音阶。
    """
    custom_data = item_dict.get("userData") or {}

    if "midi" in custom_data:
        midi_b64 = custom_data["midi"]["__value__"]
    else:
        midi_b64 = DEFAULT_MIDI_BASE64

    return decode_midi_base64(midi_b64)


def _play_midi_sound(instrument_config, tape_item, use_obj):
    notes = _get_notes_from_tape(tape_item)
    if notes:
        use_obj.send_msg("play_midi_music", {
            "notes": notes,
            "pos": use_obj.get_pos(),
            "sound_prefix": instrument_config["sound_prefix"],
            "enable_note_off": instrument_config["enable_note_off"],
        })
