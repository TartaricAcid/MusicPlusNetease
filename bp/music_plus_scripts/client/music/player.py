# -*- coding: utf-8 -*-

"""音乐盒曲目播放器

管理客户端的音乐盒播放实例。支持：
- 解析 ABC 字符串并按时序播放音符
- 最多同时存在 MAX_CONCURRENT 首歌曲
- 超出限制时移除距离玩家当前位置最远的播放实例
"""

from music_plus_scripts.QuModLibs.Client import *
from music_plus_scripts.client.music.abc_parser import parse_abc

MAX_CONCURRENT = 3
EIGHTH_NOTE_SECONDS = 0.18
NOTE_VOLUME = 1.0

# 活跃的播放实例列表
# 每个元素: {"pos": (x, y, z), "timers": [timer_id, ...], "finished": bool}
_active_songs = []

factory = clientApi.GetEngineCompFactory()
game = factory.CreateGame(levelId)
particle_sys = factory.CreateParticleSystem(levelId)

NOTE_PARTICLE = "music_plus:note_particle"
NOTE_PARTICLE_LIFETIME = 1.0


def play_song(abc_text, pos, sound_prefix):
    """解析 ABC 文本并在指定位置播放。

    Args:
        abc_text: ABC 格式乐谱字符串
        pos: (x, y, z) 播放位置
        sound_prefix: 声音 ID 前缀，如 "music_plus.music_box"
    """
    events = parse_abc(abc_text, sound_prefix)
    if not events:
        return

    _enforce_limit(pos)

    song = {"pos": tuple(pos), "timers": [], "finished": False}
    _active_songs.append(song)

    audio = factory.CreateCustomAudio(levelId)
    delay = 0.0
    total_duration = 0.0

    for notes, length in events:
        for note in notes:
            timer = game.AddTimer(delay, _play_note, audio, note, pos)
            song["timers"].append(timer)
        delay += EIGHTH_NOTE_SECONDS * length
        total_duration = delay

    # 播放结束后自动清理
    game.AddTimer(total_duration + 0.5, _mark_finished, song)


def _enforce_limit(new_pos):
    """确保活跃歌曲数量不超过 MAX_CONCURRENT。

    如果已满，移除距离 new_pos 最远的播放实例。
    同时清理已结束的实例。
    """
    # 先清理已结束的
    _cleanup_finished()

    while len(_active_songs) >= MAX_CONCURRENT:
        farthest = _find_farthest(new_pos)
        if farthest is not None:
            _stop_song(farthest)
        else:
            break


def _find_farthest(pos):
    """找到距离指定位置最远的活跃歌曲。"""
    if not _active_songs:
        return None
    max_dist = -1
    farthest = None
    for song in _active_songs:
        dist = _distance_sq(pos, song["pos"])
        if dist > max_dist:
            max_dist = dist
            farthest = song
    return farthest


def _distance_sq(a, b):
    """计算两个坐标的距离平方。"""
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    dz = a[2] - b[2]
    return dx * dx + dy * dy + dz * dz


def _stop_song(song):
    """停止一个播放实例，取消所有待执行的定时器。"""
    for timer in song["timers"]:
        try:
            game.CancelTimer(timer)
        except Exception:
            pass
    if song in _active_songs:
        _active_songs.remove(song)


def _mark_finished(song):
    """标记歌曲播放完毕。"""
    song["finished"] = True
    song["timers"] = []
    _cleanup_finished()


def _cleanup_finished():
    """移除所有已播放完毕的实例。"""
    finished = [s for s in _active_songs if s["finished"]]
    for s in finished:
        _active_songs.remove(s)


def _play_note(audio, note, pos):
    """播放单个音符，并在方块上方生成粒子。"""
    audio.PlayCustomMusic(
        note.get("name"),
        pos,
        NOTE_VOLUME,
        note.get("pitch", 1.0),
        False,
        None,
    )
    particle_id = particle_sys.Create(NOTE_PARTICLE, pos)
    if particle_sys.EmitManually(particle_id):
        game.AddTimer(NOTE_PARTICLE_LIFETIME, _remove_particle, particle_id)


def _remove_particle(particle_id):
    """移除粒子实例。"""
    particle_sys.Remove(particle_id)
