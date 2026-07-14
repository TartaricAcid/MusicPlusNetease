# -*- coding: utf-8 -*-


def get_sound_msg(sound_name, volume=1.0, pitch=1.0):
    # type: (str, float, float) -> dict
    """
    获取音频消息字典
    """
    return {
        "name": sound_name,
        "volume": volume,
        "pitch": pitch
    }
