# -*- coding: utf-8 -*-


def register_builtin_animations(register):
    from music_plus_scripts.client.music.instrument_animations.bass import BassPerformanceAnimation
    from music_plus_scripts.client.music.instrument_animations.piano import PianoPerformanceAnimation

    register(PianoPerformanceAnimation())
    register(BassPerformanceAnimation())
