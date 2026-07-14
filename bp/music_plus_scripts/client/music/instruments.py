# -*- coding: utf-8 -*-

"""乐器注册表

所有可用乐器及其音域范围定义在此处。
播放时超出该乐器音域的音符将被跳过，不做 pitch 补偿。

MIDI 音符号参考:
  C4=60, A4=69, C5=72, C6=84, C7=96

注意：这里的音域指的是"采样文件实际覆盖的 MIDI 音符范围"，
即经过 +12 半音校正后的有效范围（因为采样文件实际音高比文件名低一个八度）。
"""

from music_plus_scripts.client.music.instrument_def import InstrumentDef

# 八音盒: 采样 A4(69) ~ G#6(92)，共 24 个半音
MUSIC_BOX = InstrumentDef(
    name="music_box",
    sound_prefix="music_plus.music_box",
    lowest_note=57,  # A3 (adjusted 后为 A4=69)
    highest_note=80,  # G#5 (adjusted 后为 G#6=92)
    pitch_shift_range=0,
    note_offset=12,  # 采样文件实际音高比文件名标注低一个八度
)

_REGISTRY = {
    MUSIC_BOX.sound_prefix: MUSIC_BOX,
}


def get_instrument(sound_prefix):
    """根据 sound_prefix 获取对应的乐器定义。

    Args:
        sound_prefix: 声音 ID 前缀，如 "music_plus.music_box"

    Returns:
        InstrumentDef 实例，若未注册则返回 None（此时播放器不做音域过滤）。
    """
    return _REGISTRY.get(sound_prefix)
