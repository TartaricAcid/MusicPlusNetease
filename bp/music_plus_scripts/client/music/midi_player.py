# -*- coding: utf-8 -*-

"""MIDI 音符播放器（tick 驱动）

基于 OnScriptTickClient 事件逐帧检查并播放音符。
每帧约 1/30 秒，通过比较 elapsed time 与事件时间戳来决定播放。

核心数据流：
  → 客户端后台解码 MIDI
  → 事件列表 [[time, type, channel, data1, data2, program], ...]
  → 客户端缓存为 session
  → tick 事件逐帧驱动播放

  type: 1=note_on, 0=note_off, 2=sustain_pedal
"""

import math
import time

from music_plus_scripts.QuModLibs.Client import *
from music_plus_scripts.client.music.gm_program_map import resolve_program_sound_prefix
from music_plus_scripts.client.music.instruments import get_instrument
from music_plus_scripts.mido.midi_decoder import NOTE_ON, NOTE_OFF, SUSTAIN

# ─── 播放配置 ───────────────────────────────────────────────
MAX_CONCURRENT = 16  # 最多同时播放的会话数
NOTE_VOLUME = 1.0  # 默认音量
PLAYBACK_SPEED = 1.0  # 播放速度倍率 (1.0=原速, 2.0=两倍速, 0.5=半速)
NOTE_OFF_FADE_OUT = 0.2  # note_off 淡出时间（秒）

# ─── 其他常量 ───────────────────────────────────────────────
MIN_PITCH = 0.0
MAX_PITCH = 256.0
GM_PERCUSSION_CHANNEL = 9  # GM 标准打击乐通道 (Channel 10, 0-indexed 为 9)

# ─── 距离检测 ───────────────────────────────────────────────
MAX_START_DISTANCE = 64  # 开始播放时，超过此距离则忽略
MAX_LISTEN_DISTANCE = 72  # tick 中检查，超过此距离则中断播放
DISTANCE_CHECK_INTERVAL = 61  # 每隔多少 tick 检查一次距离

# ─── 合批播放 ───────────────────────────────────────────────
PLAYBACK_BATCH_WINDOW = 0.1  # 等待同批 MIDI 解码结果的时间窗口（秒）

# ─── 粒子效果 ───────────────────────────────────────────────
NOTE_PARTICLE = "music_plus:note_particle"  # 音符粒子
NOTE_PARTICLE_LIFETIME = 1.0  # 音符粒子存续时间，最长 1 秒

# ─── 全局状态 ───────────────────────────────────────────────
# 活跃的播放会话列表
# 每个会话: {
#     "notes": [[t, type, ch, d1, d2, program], ...], 按时间排序的事件列表
#     "ptr": int,                        当前播放指针
#     "start_time": float,               播放开始的 time.time()
#     "pos": (x, y, z),                  播放位置
#     "sound_prefix": str,               声音 ID 前缀
#     "instrument_group": str,           Program Change 可用乐器组
#     "active_notes": {},                活跃音符 {(channel, note): musicId}
#     "pedal_state": {},                 踏板状态 {channel: bool}
#     "sustained_notes": {},             踏板延音中的音符 {(channel, note): musicId}
# }
_active_sessions = []

# ─── 其他内容 ───────────────────────────────────────────────
_distance_check_tick = 0  # 距离检测计数器
_pending_batches = {}  # 合批播放

_factory = clientApi.GetEngineCompFactory()
_game = _factory.CreateGame(levelId)
_audio = _factory.CreateCustomAudio(levelId)
_particle_sys = _factory.CreateParticleSystem(levelId)


def start_playback(notes, pos, sound_prefix, instrument_group, enable_note_off=True, start_time=None):
    """开始播放一组音符。

    Args:
        notes: 已解码后的事件列表 [[time, type, channel, midi_note, velocity, program], ...]
        pos: (x, y, z) 播放位置
        sound_prefix: 声音 ID 前缀，如 "music_plus.music_box"
        instrument_group: Program Change 可使用的乐器组
        enable_note_off: 是否响应 note_off / sustain_pedal 中断（默认 True）。
            对八音盒等自然衰减乐器可设为 False，音符会持续播放直到自然结束。
        start_time: 可选的统一播放起点，用于让同批播放对齐。
    """
    if not notes:
        return

    # 距离检查：超过 64 格不播放
    player_pos = _factory.CreatePos(playerId).GetPos()
    if _distance_sq(player_pos, pos) > MAX_START_DISTANCE * MAX_START_DISTANCE:
        return

    # 先检查当前客户端音频是否超出了数量上限
    _enforce_limit(pos)

    # 将音频转成 sessions 存入
    session = {
        "notes": notes,
        "ptr": 0,
        "start_time": start_time if start_time is not None else time.time(),
        "pos": tuple(pos),
        "sound_prefix": sound_prefix,
        "instrument_group": instrument_group,
        "enable_note_off": enable_note_off,
        "active_notes": {},
        "pedal_state": {},
        "sustained_notes": {},
    }
    _active_sessions.append(session)


def queue_playback(notes, pos, sound_prefix, instrument_group, enable_note_off=True, batch_key=None):
    """把后台线程解码完成的 MIDI 播放请求交给 tick 主线程处理。

    解码完成时间可能有先后，这里先按 batch_key 暂存一小段时间，
    等同批请求尽量到齐后，再由 _drain_pending_playbacks 在 tick 中统一开始播放。
    """
    if not notes:
        return

    now = time.time()
    if batch_key is None:
        batch_key = ("single", now, tuple(pos))

    batch = _pending_batches.get(batch_key)
    if batch is None:
        batch = {
            "flush_time": now + PLAYBACK_BATCH_WINDOW,
            "items": [],
        }
        _pending_batches[batch_key] = batch

    batch["items"].append({
        "notes": notes,
        "pos": tuple(pos),
        "sound_prefix": sound_prefix,
        "instrument_group": instrument_group,
        "enable_note_off": enable_note_off,
    })


def cancel_queued_playback_at_pos(pos):
    """取消指定位置尚未进入播放会话的排队请求。

    这里只清理 _pending_batches 中等待合批的请求；已经开始播放的会话需要用 stop_at_pos 停止。
    """
    pos = tuple(pos)
    empty_keys = []
    for batch_key, batch in _pending_batches.items():
        batch["items"] = [item for item in batch["items"] if item["pos"] != pos]
        if not batch["items"]:
            empty_keys.append(batch_key)
    for batch_key in empty_keys:
        _pending_batches.pop(batch_key, None)


def stop_all():
    """停止所有播放会话，已发出的音符淡出停止。"""
    for session in _active_sessions:
        _stop_session_sounds(session)

    # 清空会话列表
    _active_sessions[:] = []


def stop_at_pos(pos):
    to_remove = []
    for session in _active_sessions:
        if session["pos"] == pos:
            _stop_session_sounds(session)
            to_remove.append(session)
    for s in to_remove:
        _active_sessions.remove(s)


def _stop_session_sounds(session):
    """停止单个会话中所有活跃音符。"""
    for mid in session.get("active_notes", {}).values():
        _audio.StopCustomMusicById(mid, NOTE_OFF_FADE_OUT)
    for mid in session.get("sustained_notes", {}).values():
        _audio.StopCustomMusicById(mid, NOTE_OFF_FADE_OUT)


def on_music_tick():
    # 先检查是否有排队的播放请求需要合批处理
    _drain_pending_playbacks()

    # 没有音频时，直接返回
    if not _active_sessions:
        return

    # 计数器自增
    global _distance_check_tick
    _distance_check_tick += 1

    # 每一定 tick 检查一次玩家距离，超出 72 格的会话直接中断
    if _distance_check_tick >= DISTANCE_CHECK_INTERVAL:
        player_pos = _factory.CreatePos(playerId).GetPos()

        _distance_check_tick = 0
        out_of_range = []

        for session in _active_sessions:
            if _distance_sq(player_pos, session["pos"]) > MAX_LISTEN_DISTANCE * MAX_LISTEN_DISTANCE:
                _stop_session_sounds(session)
                out_of_range.append(session)

        for s in out_of_range:
            _active_sessions.remove(s)

    # 正常更新剩下音频
    finished = []
    for session in _active_sessions:
        now = (time.time() - session["start_time"]) * PLAYBACK_SPEED
        notes = session["notes"]
        ptr = session["ptr"]
        pos = session["pos"]
        prefix = session["sound_prefix"]
        instrument_group = session["instrument_group"]
        active_notes = session["active_notes"]
        pedal_state = session["pedal_state"]
        sustained_notes = session["sustained_notes"]
        note_off_enabled = session["enable_note_off"]

        # 处理所有已到达时间点的事件
        while ptr < len(notes) and notes[ptr][0] <= now:
            event = notes[ptr]
            etype, channel = event[1], event[2]

            # GM 打击乐通道过滤：
            # Channel 10 (0-indexed=9) 仅用于鼓类乐器，非鼓组跳过；
            # 鼓组仅处理 Channel 10，跳过旋律通道。
            is_percussion_ch = (channel == GM_PERCUSSION_CHANNEL)
            is_drum_group = (instrument_group == "drum_kit")
            if is_percussion_ch != is_drum_group:
                ptr += 1
                continue

            # 音符播放
            if etype == NOTE_ON:
                midi_note, vel = event[3], event[4]
                program = event[5] if len(event) > 5 else 0
                key = (channel, midi_note)
                if note_off_enabled:
                    # 重击同音：先停掉旧的（无论在 active 还是 sustained 中）
                    old = active_notes.pop(key, None) or sustained_notes.pop(key, None)
                    if old:
                        _audio.StopCustomMusicById(old, NOTE_OFF_FADE_OUT)
                music_id = _play_note(midi_note, vel, pos, prefix, instrument_group, program)
                if music_id and note_off_enabled:
                    active_notes[key] = music_id

            elif etype == NOTE_OFF and note_off_enabled:
                midi_note = event[3]
                key = (channel, midi_note)
                music_id = active_notes.pop(key, None)
                if music_id:
                    if pedal_state.get(channel, False):
                        # 踏板踩着，暂不停止，移入延音列表
                        sustained_notes[key] = music_id
                    else:
                        _audio.StopCustomMusicById(music_id, NOTE_OFF_FADE_OUT)

            elif etype == SUSTAIN and note_off_enabled:
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


def _play_note(midi_note, velocity, pos, sound_prefix, instrument_group, program):
    resolved_prefix = resolve_program_sound_prefix(sound_prefix, instrument_group, program)
    if resolved_prefix is None:
        return None

    sound = _midi_to_sound(midi_note, resolved_prefix)
    if sound is None:
        # 超出乐器音域，跳过此音符
        return None

    name = sound["name"]
    pitch = sound["pitch"]
    volume = NOTE_VOLUME * velocity

    # 播放单个音符
    music_id = _audio.PlayCustomMusic(name, pos, volume, pitch, False, None, )

    # 粒子效果
    x, y, z = pos
    particle_id = _particle_sys.Create(NOTE_PARTICLE, (x + 0.5, y + 1, z + 0.5))
    if _particle_sys.EmitManually(particle_id):
        _game.AddTimer(NOTE_PARTICLE_LIFETIME, _remove_particle, particle_id)

    return music_id


def _drain_pending_playbacks():
    """将已到合批时间的排队请求转成真正的播放会话。

    同一个 batch 里的所有请求共用一个 start_time，避免多个 MIDI 因解码完成顺序不同而错开起播。
    """
    if not _pending_batches:
        return

    now = time.time()
    ready_keys = [batch_key for batch_key, batch in _pending_batches.items() if batch["flush_time"] <= now]
    pending_batches = [_pending_batches.pop(batch_key) for batch_key in ready_keys]

    for batch in pending_batches:
        start_time = time.time()
        for item in batch["items"]:
            start_playback(
                item["notes"],
                item["pos"],
                item["sound_prefix"],
                item["instrument_group"],
                item["enable_note_off"],
                start_time,
            )


def _remove_particle(particle_id):
    """移除粒子实例。"""
    _particle_sys.Remove(particle_id)


def _midi_to_sound(midi_note, sound_prefix):
    """将 MIDI 音符号映射为声音名称和 pitch 参数。

    根据乐器定义检查音域范围：
    - 若已注册乐器且音符超出可播放范围，返回 None（跳过该音符）。
    - 若乐器未注册（不太可能）直接返回 None
    """
    instrument = get_instrument(sound_prefix)
    if instrument is None:
        # 乐器未注册，无法播放音符
        return None

    resolved = instrument.resolve(midi_note)
    if resolved is None:
        # 超出该乐器音域或未映射，跳过
        return None

    sound_name, semitone = resolved
    pitch = math.pow(2.0, semitone / 12.0)
    pitch = max(MIN_PITCH, min(MAX_PITCH, pitch))
    return {
        "name": "{}.{}".format(sound_prefix, sound_name),
        "pitch": pitch,
    }


def _enforce_limit(new_pos):
    """确保活跃会话数不超过 MAX_CONCURRENT。

    超出限制时移除距离新播放位置最远的会话，并停止其活跃音符。
    """
    while len(_active_sessions) >= MAX_CONCURRENT:
        # 如果没有活跃会话，直接退出
        if not _active_sessions:
            break

        # 找出最远的音频
        farthest = max(_active_sessions, key=lambda s: _distance_sq(new_pos, s["pos"]))

        _stop_session_sounds(farthest)

        # 从 _active_sessions 中移除最远的会话
        _active_sessions.remove(farthest)


def _distance_sq(a, b):
    """计算两点距离的平方。"""
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    dz = a[2] - b[2]
    return dx * dx + dy * dy + dz * dz
