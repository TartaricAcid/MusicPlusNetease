# -*- coding: utf-8 -*-

"""客户端钢琴演奏动画驱动。"""

from music_plus_scripts.QuModLibs.Client import *

PIANO_MIN_NOTE = 21
PIANO_MAX_NOTE = 108
HAND_SPLIT_NOTE = 60
MAX_ARM_Y_ROTATION = 120.0
ARM_SMOOTHING = 0.35
ARM_RETURN_SPEED = 0.16

PLAYING_QUERY = "query.mod.music_plus_piano_playing"
LEFT_ARM_QUERY = "query.mod.music_plus_piano_left_y"
RIGHT_ARM_QUERY = "query.mod.music_plus_piano_right_y"

ANIMATION_KEY = "music_plus_piano_play"
ANIMATION_NAME = "animation.music_plus.player.piano_play"

_factory = clientApi.GetEngineCompFactory()
_registered_players = set()
_player_states = {}


def register_queries():
    query_comp = _factory.CreateQueryVariable(levelId)
    query_comp.Register(PLAYING_QUERY, 0.0)
    query_comp.Register(LEFT_ARM_QUERY, 0.0)
    query_comp.Register(RIGHT_ARM_QUERY, 0.0)


def _ensure_player_animation(player_id):
    if player_id in _registered_players:
        return

    render_comp = _factory.CreateActorRender(player_id)
    render_comp.AddPlayerAnimation(ANIMATION_KEY, ANIMATION_NAME)
    render_comp.AddPlayerScriptAnimate(ANIMATION_KEY, PLAYING_QUERY + "&& !variable.is_first_person")
    render_comp.RebuildPlayerRender()
    _registered_players.add(player_id)


def start_piano_animation(player_id):
    if not player_id:
        return

    _ensure_player_animation(player_id)
    state = _player_states.get(player_id)
    if state is None:
        state = {
            "session_count": 0,
            "left": 0.0,
            "right": 0.0,
            "left_target": 0.0,
            "right_target": 0.0,
            "left_active": False,
            "right_active": False,
        }
        _player_states[player_id] = state
    state["session_count"] += 1
    _set_query(player_id, PLAYING_QUERY, 1.0)


def stop_piano_animation(player_id):
    state = _player_states.get(player_id)
    if state is None:
        return

    state["session_count"] = max(0, state["session_count"] - 1)
    if state["session_count"] > 0:
        return

    _set_query(player_id, PLAYING_QUERY, 0.0)
    _set_query(player_id, LEFT_ARM_QUERY, 0.0)
    _set_query(player_id, RIGHT_ARM_QUERY, 0.0)
    _player_states.pop(player_id, None)


def update_piano_notes(player_id, notes):
    """根据同一 tick 内触发的 [(midi_note, velocity), ...] 更新双手目标。"""
    state = _player_states.get(player_id)
    if state is None or not notes:
        return

    ordered = sorted(notes, key=lambda item: item[0])
    if len(ordered) == 1:
        left_notes = ordered if ordered[0][0] < HAND_SPLIT_NOTE else []
        right_notes = ordered if not left_notes else []
    else:
        split = len(ordered) // 2
        left_notes = ordered[:split]
        right_notes = ordered[split:]

    if left_notes:
        state["left_target"] = _notes_to_rotation(left_notes)
        state["left_active"] = True
    if right_notes:
        state["right_target"] = _notes_to_rotation(right_notes)
        state["right_active"] = True


def on_piano_animation_tick():
    if not _player_states:
        return

    for player_id, state in _player_states.items():
        left_factor = ARM_SMOOTHING if state["left_active"] else ARM_RETURN_SPEED
        right_factor = ARM_SMOOTHING if state["right_active"] else ARM_RETURN_SPEED
        left_target = state["left_target"] if state["left_active"] else 0.0
        right_target = state["right_target"] if state["right_active"] else 0.0

        state["left"] += (left_target - state["left"]) * left_factor
        state["right"] += (right_target - state["right"]) * right_factor
        state["left_active"] = False
        state["right_active"] = False

        _set_query(player_id, LEFT_ARM_QUERY, state["left"])
        _set_query(player_id, RIGHT_ARM_QUERY, state["right"])


def _notes_to_rotation(notes):
    velocity_sum = sum(max(0.01, velocity) for _, velocity in notes)
    note = sum(midi_note * max(0.01, velocity) for midi_note, velocity in notes) / velocity_sum
    normalized = (note - PIANO_MIN_NOTE) / float(PIANO_MAX_NOTE - PIANO_MIN_NOTE)
    normalized = max(0.0, min(1.0, normalized))
    return (normalized * 2.0 - 1.0) * MAX_ARM_Y_ROTATION


def _set_query(player_id, query_name, value):
    _factory.CreateQueryVariable(player_id).Set(query_name, value)


def handle_remove_player_aoi(args):
    remote_player_id = args["playerId"]
    _registered_players.discard(remote_player_id)
    _player_states.pop(remote_player_id, None)
