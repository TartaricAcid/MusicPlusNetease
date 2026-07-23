# -*- coding: utf-8 -*-


def register_builtin_animations(register):
    from music_plus_scripts.client.music.instrument_animations.bass import BassPerformanceAnimation
    from music_plus_scripts.client.music.instrument_animations.guzheng import GuzhengPerformanceAnimation
    from music_plus_scripts.client.music.instrument_animations.piano import PianoPerformanceAnimation
    from music_plus_scripts.client.music.instrument_animations.vibra import VibraPerformanceAnimation

    register(PianoPerformanceAnimation())
    register(BassPerformanceAnimation())
    register(VibraPerformanceAnimation())
    register(GuzhengPerformanceAnimation())
