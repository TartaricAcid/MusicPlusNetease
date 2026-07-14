# -*- coding: utf-8 -*-

from music_plus_scripts.mido.midi_decoder import decode_midi_base64
from music_plus_scripts.server.object.item_use_block_object import ItemUseBlockObject

PAPER_TAPE_ITEM = "music_plus:paper_tape"
MUSIC_BOX_BLOCK = "music_plus:music_plus_music_box"
MUSIC_BOX_SOUND_PREFIX = "music_plus.music_box"

# 默认测试曲目的 base64 MIDI（纸带无自定义数据时使用）
DEFAULT_MIDI_BASE64 = (
    "TVRoZAAAAAYAAQACAYBNVHJrAAAAQwD/AQljcmVhdG9yOiAA/wEeTGlseVBvbmQgMi4yNC4xICAgICAgICAgICAgICAgAP9YBAQCGAgA/"
    "1EDD0JA4wD/LwBNVHJrAAABfAD/AwVcbmV3OgD/WQIAAACQQ1qBQJBDAACQSFqBQJBIAACQTFqDAJBMAACQTFqBQJBMAACQTFqBQJBMAA"
    "CQTFqDAJBMAACQSlqBQJBKAACQTFqBQJBMAACQSlqBQJBKAACQSFqBQJBIAACQSFqGAJBIAACQQ1qBQJBDAACQSFqBQJBIAACQTFqDAJBM"
    "AACQSFqBQJBIAACQTFqBQJBMAACQT1qDAJBPAACQTVqBQJBNAACQTFqBQJBMAACQSlqJAJBKAACQT1qBQJBPAACQTVqBQJBNAACQTFqDAJB"
    "MAACQTFqBQJBMAACQSlqBQJBKAACQSFqDAJBIAACQSlqBQJBKAACQTFqBQJBMAACQT1qBQJBPAACQTVqBQJBNAACQTVqGAJBNAACQRVqBQJB"
    "FAACQRFqBQJBEAACQQ1qDAJBDAACQR1qBQJBHAACQSFqBQJBIAACQSlqDAJBKAACQTFqBQJBMAACQSlqBQJBKAACQSFqJAJBIAIMA/y8A"
)


def is_paper_tape(item_name):
    return item_name == PAPER_TAPE_ITEM


def is_music_box(block_name):
    return block_name == MUSIC_BOX_BLOCK


def handle_music_box_play(args):
    """处理纸带右击音乐盒：提取 MIDI 数据，解码后发送到客户端播放。"""
    use_obj = ItemUseBlockObject(args)
    item = args["itemDict"]

    notes = _get_notes_from_tape(item)
    if not notes:
        return

    pos = (args["x"] + 0.5, args["y"] + 1.0, args["z"] + 0.5)
    use_obj.send_msg("play_midi_music", {
        "notes": notes,
        "pos": pos,
        "sound_prefix": MUSIC_BOX_SOUND_PREFIX,
        # 八音盒采样自然衰减，无需响应 note_off / sustain_pedal 中断
        "enable_note_off": False,
    })
    use_obj.swing_hand()


def _get_notes_from_tape(item_dict):
    """从纸带物品的 userData 中提取 MIDI 数据并解码为音符列表。

    userData 中应包含 "midi" 键，值为 base64 编码的 MIDI 文件字符串。
    如果纸带没有写入自定义数据，返回默认测试音阶。
    """
    custom_data = item_dict.get("userData") or {}
    midi_b64 = custom_data.get("midi", "") or DEFAULT_MIDI_BASE64
    if midi_b64:
        return decode_midi_base64(midi_b64)
    return []
