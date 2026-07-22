# -*- coding: utf-8 -*-

"""方块乐器通用处理模块

纸带右击方块乐器时，根据方块 ID 查找对应的乐器配置，
读取 MIDI 数据并发送到客户端播放。

新增方块乐器只需在 server.store.instrument_registry 中注册即可。
"""

import ast
import base64

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.object.block_object import BlockObject
from music_plus_scripts.server.object.block_use_object import BlockUseObject
from music_plus_scripts.server.object.item_use_block_object import ItemUseBlockObject
from music_plus_scripts.server.store.midi_store import get_midi
from music_plus_scripts.server.utils.item_utils import item_dict_is_empty
from music_plus_scripts.utils.midi_payload import pack_midi_payload

PAPER_TAPE_ITEM = "music_plus:paper_tape"
PAPER_TAPE_DATA_KEY = "music_plus:paper_tape"
REDSTONE_PLAYING_DATA_KEY = "music_plus:redstone_playing"
MIDI_MD5_NBT_KEY = "midi_md5"

# 默认测试曲目的 base64 MIDI（纸带无自定义数据时使用）
DEFAULT_MIDI_BASE64 = (
    "TVRoZAAAAAYAAQACAYBNVHJrAAAAQwD/AQljcmVhdG9yOiAA/wEeTGlseVBvbmQgMi4yNC4xICAgICAgICAgICAgICAgAP9YBAQCGAgA/"
    "1EDD0JA4wD/LwBNVHJrAAABfAD/AwVcbmV3OgD/WQIAAACQQ1qBQJBDAACQSFqBQJBIAACQTFqDAJBMAACQTFqBQJBMAACQTFqBQJBMAA"
    "CQTFqDAJBMAACQSlqBQJBKAACQTFqBQJBMAACQSlqBQJBKAACQSFqBQJBIAACQSFqGAJBIAACQQ1qBQJBDAACQSFqBQJBIAACQTFqDAJBM"
    "AACQSFqBQJBIAACQTFqBQJBMAACQT1qDAJBPAACQTVqBQJBNAACQTFqBQJBMAACQSlqJAJBKAACQT1qBQJBPAACQTVqBQJBNAACQTFqDAJB"
    "MAACQTFqBQJBMAACQSlqBQJBKAACQSFqDAJBIAACQSlqBQJBKAACQTFqBQJBMAACQT1qBQJBPAACQTVqBQJBNAACQTVqGAJBNAACQRVqBQJB"
    "FAACQRFqBQJBEAACQQ1qDAJBDAACQR1qBQJBHAACQSFqBQJBIAACQSlqDAJBKAACQTFqBQJBMAACQSlqBQJBKAACQSFqJAJBIAIMA/y8A"
)

DEFAULT_MIDI_PAYLOAD = pack_midi_payload(base64.b64decode(DEFAULT_MIDI_BASE64))

factory = serverApi.GetEngineCompFactory()
game = factory.CreateGame(levelId)


def is_paper_tape(item_name):
    return item_name == PAPER_TAPE_ITEM


def handle_paper_tape_insert(args, instrument_config):
    use_obj = ItemUseBlockObject(args)
    item_obj = use_obj.get_item()

    if item_obj.is_empty():
        return

    _stop_midi_sound(use_obj)

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
    _stop_midi_sound(block)


def handle_block_instrument_redstone(args, instrument_config):
    block = BlockObject(args)
    new_strength = args.get("newStrength", 0)
    old_strength = args.get("oldStrength", 0)

    if old_strength <= 0 < new_strength:
        be_data = block.get_block_entity_data()
        is_playing = be_data[REDSTONE_PLAYING_DATA_KEY] or False
        is_playing = not is_playing
        be_data[REDSTONE_PLAYING_DATA_KEY] = is_playing
        block.set_block_entity_data(be_data)

        if is_playing:
            _stop_midi_sound(block)
            tape = get_stored_paper_tape(block)
            if not item_dict_is_empty(tape):
                _play_midi_sound(instrument_config, tape, block)
        else:
            _stop_midi_sound(block)


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

    _stop_midi_sound(use_obj)

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


def _get_midi_from_tape(item_dict):
    """从纸带 userData 中读取 MIDI 索引，并从服务端存档回查 MIDI 数据。"""
    custom_data = item_dict.get("userData") or {}
    if MIDI_MD5_NBT_KEY not in custom_data:
        return DEFAULT_MIDI_PAYLOAD, None

    midi_md5 = custom_data[MIDI_MD5_NBT_KEY]["__value__"]
    midi_payload = get_midi(midi_md5)
    if midi_payload is None:
        return DEFAULT_MIDI_PAYLOAD, None
    else:
        return midi_payload, midi_md5


def _play_midi_sound(instrument_config, tape_item, use_obj):
    from music_plus_scripts.server.action.instrument_playback import build_block_playback, play_instrument_playback
    from music_plus_scripts.utils.direction import aux_to_direction

    midi_payload, midi_md5 = _get_midi_from_tape(tape_item)
    if midi_payload:
        block_aux = use_obj.get_offset_block().get("aux", use_obj.aux)
        instrument = instrument_config.copy()
        instrument.update(build_block_playback(
            use_obj.get_pos(),
            use_obj.get_dimension(),
            aux_to_direction(block_aux),
        ))
        play_instrument_playback(midi_payload, midi_md5, instrument)


def _stop_midi_sound(block):
    from music_plus_scripts.server.action.instrument_playback import build_block_playback, stop_instrument_playback

    playback = build_block_playback(block.get_pos(), block.get_dimension())
    stop_instrument_playback(playback["playback_key"])
