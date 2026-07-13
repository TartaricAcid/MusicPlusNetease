# -*- coding: utf-8 -*-

"""MIDI 音符播放器（tick 驱动）

基于 OnScriptTickClient 事件逐帧检查并播放音符。
每帧约 1/30 秒，通过比较 elapsed time 与事件时间戳来决定播放。

核心数据流：
  服务端解码 MIDI → 事件列表 [[time, type, channel, data1, data2], ...]
  → 客户端缓存为 session → tick 事件逐帧驱动播放
  type: 1=note_on, 0=note_off, 2=sustain_pedal
"""

import math
import time as _time

from music_plus_scripts.QuModLibs.Client import *

# ─── 音色映射常量 ───────────────────────────────────────────
# 音乐盒可用采样音域: A4(69) ~ G#6(92)，共 24 个 .ogg 采样
MUSICBOX_LOWEST_MIDI_NOTE = 69
MUSICBOX_HIGHEST_MIDI_NOTE = 92
MUSICBOX_NOTE_NAMES = (
    "c", "cs", "d", "ds", "e", "f", "fs", "g", "gs", "a", "as", "b"
)

# ─── 播放配置 ───────────────────────────────────────────────
MAX_CONCURRENT = 3          # 最多同时播放的会话数
NOTE_VOLUME = 1.0           # 默认音量
PLAYBACK_SPEED = 1.0        # 播放速度倍率 (1.0=原速, 2.0=两倍速, 0.5=半速)

# ─── 粒子效果 ───────────────────────────────────────────────
NOTE_PARTICLE = "music_plus:note_particle"
NOTE_PARTICLE_LIFETIME = 1.0
NOTE_OFF_FADE_OUT = 0.05        # note_off 淡出时间（秒）

# ─── 全局状态 ───────────────────────────────────────────────
# 活跃的播放会话列表
# 每个会话: {
#     "notes": [[t, type, ch, d1, d2], ...], 按时间排序的事件列表
#     "ptr": int,                        当前播放指针
#     "start_time": float,               播放开始的 time.time()
#     "pos": (x, y, z),                  播放位置
#     "sound_prefix": str,               声音 ID 前缀
#     "active_notes": {},                活跃音符 {(channel, note): musicId}
#     "pedal_state": {},                 踏板状态 {channel: bool}
#     "sustained_notes": {},             踏板延音中的音符 {(channel, note): musicId}
# }
_active_sessions = []

factory = clientApi.GetEngineCompFactory()
_game = factory.CreateGame(levelId)
_audio = factory.CreateCustomAudio(levelId)
_particle_sys = factory.CreateParticleSystem(levelId)


# ─── 公开 API ───────────────────────────────────────────────

def start_playback(notes, pos, sound_prefix, enable_note_off=True):
    """开始播放一组音符。

    Args:
        notes: 服务端解码后的事件列表 [[time, type, channel, midi_note, velocity], ...]
        pos: (x, y, z) 播放位置
        sound_prefix: 声音 ID 前缀，如 "music_plus.music_box"
        enable_note_off: 是否响应 note_off / sustain_pedal 中断（默认 True）。
            对八音盒等自然衰减乐器可设为 False，音符会持续播放直到自然结束。
    """
    if not notes:
        return

    _enforce_limit(pos)

    session = {
        "notes": notes,
        "ptr": 0,
        "start_time": _time.time(),
        "pos": tuple(pos),
        "sound_prefix": sound_prefix,
        "enable_note_off": enable_note_off,
        "active_notes": {},
        "pedal_state": {},
        "sustained_notes": {},
    }
    _active_sessions.append(session)


def stop_all():
    """停止所有播放会话，已发出的音符淡出停止。"""
    for session in _active_sessions:
        for mid in session.get("active_notes", {}).values():
            _audio.StopCustomMusicById(mid, NOTE_OFF_FADE_OUT)
        for mid in session.get("sustained_notes", {}).values():
            _audio.StopCustomMusicById(mid, NOTE_OFF_FADE_OUT)
    _active_sessions[:] = []


# ─── tick 驱动核心 ──────────────────────────────────────────

@Listen(Events.OnScriptTickClient)
def _on_tick(_args={}):
    """每帧检查并播放到达播放时间的事件。"""
    if not _active_sessions:
        return

    finished = []
    for session in _active_sessions:
        now = (_time.time() - session["start_time"]) * PLAYBACK_SPEED
        notes = session["notes"]
        ptr = session["ptr"]
        pos = session["pos"]
        prefix = session["sound_prefix"]
        active_notes = session["active_notes"]
        pedal_state = session["pedal_state"]
        sustained_notes = session["sustained_notes"]
        note_off_enabled = session["enable_note_off"]

        # 处理所有已到达时间点的事件
        while ptr < len(notes) and notes[ptr][0] <= now:
            event = notes[ptr]
            etype, channel = event[1], event[2]

            if etype == 1:  # note_on
                midi_note, vel = event[3], event[4]
                key = (channel, midi_note)
                if note_off_enabled:
                    # 重击同音：先停掉旧的（无论在 active 还是 sustained 中）
                    old = active_notes.pop(key, None) or sustained_notes.pop(key, None)
                    if old:
                        _audio.StopCustomMusicById(old, NOTE_OFF_FADE_OUT)
                music_id = _play_note(midi_note, vel, pos, prefix)
                if music_id and note_off_enabled:
                    active_notes[key] = music_id

            elif etype == 0 and note_off_enabled:  # note_off
                midi_note = event[3]
                key = (channel, midi_note)
                music_id = active_notes.pop(key, None)
                if music_id:
                    if pedal_state.get(channel, False):
                        # 踏板踩着，暂不停止，移入延音列表
                        sustained_notes[key] = music_id
                    else:
                        _audio.StopCustomMusicById(music_id, NOTE_OFF_FADE_OUT)

            elif etype == 2 and note_off_enabled:  # sustain pedal
                pedal_on = event[3]
                if pedal_on:
                    pedal_state[channel] = True
                else:
                    pedal_state[channel] = False
                    # 踏板松开，释放该 channel 所有延音中的音符
                    to_release = [k for k in sustained_notes if k[0] == channel]
                    for k in to_release:
                        mid = sustained_notes.pop(k)
                        _audio.StopCustomMusicById(mid, NOTE_OFF_FADE_OUT)

            ptr += 1

        session["ptr"] = ptr

        # 所有事件处理完毕
        if ptr >= len(notes):
            if note_off_enabled:
                # 停止残留活跃音符和延音音符
                for mid in active_notes.values():
                    _audio.StopCustomMusicById(mid, NOTE_OFF_FADE_OUT)
                for mid in sustained_notes.values():
                    _audio.StopCustomMusicById(mid, NOTE_OFF_FADE_OUT)
            finished.append(session)

    # 清理已结束的会话
    for s in finished:
        _active_sessions.remove(s)


# ─── 内部工具函数 ──────────────────────────────────────────

def _play_note(midi_note, velocity, pos, sound_prefix):
    """播放单个音符并生成粒子效果。返回 musicId 供后续停止使用。"""
    sound = _midi_to_sound(midi_note, sound_prefix)
    music_id = _audio.PlayCustomMusic(
        sound["name"],
        pos,
        NOTE_VOLUME * velocity,
        sound["pitch"],
        False,
        None,
    )
    # 粒子效果
    particle_id = _particle_sys.Create(NOTE_PARTICLE, pos)
    if _particle_sys.EmitManually(particle_id):
        _game.AddTimer(NOTE_PARTICLE_LIFETIME, _remove_particle, particle_id)
    return music_id


def _remove_particle(particle_id):
    """移除粒子实例。"""
    _particle_sys.Remove(particle_id)


def _midi_to_sound(midi_note, sound_prefix):
    """将 MIDI 音符号映射为声音名称和 pitch 参数。

    将音符钳制到可用采样范围 (A4~G#6)，
    超出范围的部分通过 pitch 移调补偿。

    采样文件实际音高比文件名标注低一个八度，
    因此将 MIDI 音符号上移 12 半音后再做映射。
    """
    adjusted = midi_note + 12
    sample = max(MUSICBOX_LOWEST_MIDI_NOTE, min(MUSICBOX_HIGHEST_MIDI_NOTE, adjusted))
    note_name = MUSICBOX_NOTE_NAMES[sample % 12]
    sample_octave = sample // 12 - 1
    if note_name.endswith("s"):
        sound_name = "{}{}s".format(note_name[0], sample_octave)
    else:
        sound_name = "{}{}".format(note_name, sample_octave)
    return {
        "name": "{}.{}".format(sound_prefix, sound_name),
        "pitch": math.pow(2.0, (adjusted - sample) / 12.0),
    }


def _enforce_limit(new_pos):
    """确保活跃会话数不超过 MAX_CONCURRENT。

    超出限制时移除距离新播放位置最远的会话，并停止其活跃音符。
    """
    while len(_active_sessions) >= MAX_CONCURRENT:
        if not _active_sessions:
            break
        farthest = max(_active_sessions, key=lambda s: _distance_sq(new_pos, s["pos"]))
        for mid in farthest.get("active_notes", {}).values():
            _audio.StopCustomMusicById(mid, NOTE_OFF_FADE_OUT)
        for mid in farthest.get("sustained_notes", {}).values():
            _audio.StopCustomMusicById(mid, NOTE_OFF_FADE_OUT)
        _active_sessions.remove(farthest)


def _distance_sq(a, b):
    """计算两点距离的平方。"""
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    dz = a[2] - b[2]
    return dx * dx + dy * dy + dz * dz
