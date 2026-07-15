# -*- coding: utf-8 -*-

import traceback

from music_plus_scripts.QuModLibs.Modules.Thread.Client import RUN_IN_MAIN_THREAD
from music_plus_scripts.QuModLibs.Modules.Thread.Util import QThreadPool
from music_plus_scripts.client.music.midi_player import cancel_queued_playback_at_pos, queue_playback, stop_at_pos
from music_plus_scripts.mido.midi_decoder import decode_midi_payload
from music_plus_scripts.utils.midi_payload import get_midi_payload_md5

# MIDI 解码线程池
_DECODE_POOL = QThreadPool(maxThreadCount=1, daemon=True).start()

# 全局播放请求递增版本号
# 用于丢弃异步解码完成后，过期播放请求
_PLAY_REQUEST_VERSION = 0
# 方块 pos -> REQUEST_VERSION 映射表
_PLAY_REQUEST_VERSIONS_BY_POS = {}

# 最多缓存数量
_MAX_DECODE_CACHE = 8
# 已解码 MIDI 事件缓存，key 为 MIDI md5
_DECODE_CACHE = {}

# MIDI 解码缓存，按 LRU 缓存顺序
_DECODE_CACHE_ORDER = []

# 正在等待同一个 MIDI 解码结果的播放请求列表
_DECODE_WAITERS = {}


def play_midi_music_data(midi_payload, pos, sound_prefix, enable_note_off=True, midi_md5=None):
    # 构建解码请求
    pos = tuple(pos)
    request_version = _next_play_request_version(pos)
    cache_key = _get_cache_key(midi_payload, midi_md5)
    request = {
        "pos": pos,
        "sound_prefix": sound_prefix,
        "enable_note_off": enable_note_off,
        "version": request_version,
    }

    # 先尝试去缓存里检查是否有解码后的 midi
    cached_notes = _DECODE_CACHE.get(cache_key)
    if cached_notes is not None:
        # 有此缓存，那么按照 LRU 策略将其移动至队尾
        _touch_cache_key(cache_key)
        # 加入合批播放队列
        _queue_if_latest(cached_notes, cache_key, request)
        return

    # 没有命中缓存，检查是否在解码队列里
    waiters = _DECODE_WAITERS.get(cache_key)
    if waiters is not None:
        # 如果已经在解码队列里，那么仅需将当前请求加入等待列表
        waiters.append(request)
        return

    # 否则将当前请求加入等待列表，并提交解码任务
    _DECODE_WAITERS[cache_key] = [request]

    # 尝试解码 MIDI 数据
    def decode_task():
        try:
            decoded_notes = decode_midi_payload(midi_payload)
        except Exception:
            # 如果解码失败，则打印异常信息，并清理等待列表
            traceback.print_exc()
            RUN_IN_MAIN_THREAD(lambda _cache_key=cache_key: _DECODE_WAITERS.pop(_cache_key, None))
            return

        # 完成解码后，回到主线程处理播放请求
        RUN_IN_MAIN_THREAD(
            lambda _cache_key=cache_key, _decoded_notes=decoded_notes: _finish_decode(_cache_key, _decoded_notes)
        )

    _DECODE_POOL.addTask(decode_task)


def stop_midi_music_at_pos(pos):
    pos = tuple(pos)
    _next_play_request_version(pos)
    cancel_queued_playback_at_pos(pos)
    stop_at_pos(pos)


def _next_play_request_version(pos):
    global _PLAY_REQUEST_VERSION
    _PLAY_REQUEST_VERSION += 1
    _PLAY_REQUEST_VERSIONS_BY_POS[pos] = _PLAY_REQUEST_VERSION
    return _PLAY_REQUEST_VERSION


def _queue_if_latest(notes, cache_key, request):
    if _PLAY_REQUEST_VERSIONS_BY_POS.get(request["pos"]) != request["version"]:
        return

    queue_playback(
        notes,
        request["pos"],
        request["sound_prefix"],
        request["enable_note_off"],
        batch_key=cache_key
    )


def _finish_decode(cache_key, notes):
    # 从解码等待列表里弹出
    waiters = _DECODE_WAITERS.pop(cache_key, [])
    if not notes:
        return

    # 按照 LRU 策略更新缓存
    _DECODE_CACHE[cache_key] = notes
    _touch_cache_key(cache_key)
    while len(_DECODE_CACHE_ORDER) > _MAX_DECODE_CACHE:
        old_key = _DECODE_CACHE_ORDER.pop(0)
        _DECODE_CACHE.pop(old_key, None)

    # 通知其他等待的播放请求
    for pending_request in waiters:
        _queue_if_latest(notes, cache_key, pending_request)


def _touch_cache_key(cache_key):
    if cache_key in _DECODE_CACHE_ORDER:
        _DECODE_CACHE_ORDER.remove(cache_key)
    _DECODE_CACHE_ORDER.append(cache_key)


def _get_cache_key(midi_payload, midi_md5=None):
    if midi_md5:
        return midi_md5
    return get_midi_payload_md5(midi_payload)
