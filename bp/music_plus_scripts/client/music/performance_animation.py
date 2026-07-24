# -*- coding: utf-8 -*-

"""客户端通用乐器演奏动画驱动。"""

from music_plus_scripts.QuModLibs.Client import *
from music_plus_scripts.client.music.instrument_animations import register_builtin_animations
from music_plus_scripts.client.music.performance_animation_def import PERFORMANCE_AXES

PLAYING_QUERY = "query.mod.music_plus_perform_playing"
AXIS_QUERIES = dict(
    (axis, "query.mod.music_plus_perform_{}".format(axis))
    for axis in PERFORMANCE_AXES
)

ANIMATION_KEY = "music_plus_instrument_play"
ANIMATION_NAME = "animation.music_plus.player.instrument_play"

ANIMATION_TICK_INTERVAL = 3
ANIMATION_SNAP_EPSILON = 0.01

_REGISTRY = {}
_REGISTERED_PLAYERS = set()
_REGISTERED_ACTORS = set()
_PERFORMER_STATES = {}
_ANIMATION_TICK = 0

factory = clientApi.GetEngineCompFactory()


def register_performance_animation(animation_def):
    _REGISTRY[animation_def.name] = animation_def
    return animation_def


def get_performance_animation(name):
    return _REGISTRY.get(name)


# 注册所有的动画
register_builtin_animations(register_performance_animation)


def register_queries():
    query_comp = factory.CreateQueryVariable(levelId)
    query_comp.Register(PLAYING_QUERY, 0.0)
    for query_name in AXIS_QUERIES.values():
        query_comp.Register(query_name, 0.0)


def _ensure_performer_animation(performer_id):
    performer_type = factory.CreateEngineType(performer_id).GetEngineTypeStr()
    render_comp = factory.CreateActorRender(performer_id)

    if performer_type == "minecraft:player":
        if performer_id in _REGISTERED_PLAYERS:
            return
        render_comp.AddPlayerAnimation(ANIMATION_KEY, ANIMATION_NAME)
        render_comp.AddPlayerScriptAnimate(ANIMATION_KEY, PLAYING_QUERY + "&& !variable.is_first_person")
        render_comp.RebuildPlayerRender()
        _REGISTERED_PLAYERS.add(performer_id)
    else:
        if performer_type in _REGISTERED_ACTORS:
            return
        render_comp.AddActorAnimation(performer_type, ANIMATION_KEY, ANIMATION_NAME)
        render_comp.AddActorScriptAnimate(performer_type, ANIMATION_KEY, PLAYING_QUERY)
        render_comp.RebuildActorRender(performer_type)
        _REGISTERED_ACTORS.add(performer_type)


def start_performance_animation(performer_id, profile_id):
    animation_def = get_performance_animation(profile_id)
    if not performer_id or animation_def is None:
        return

    _ensure_performer_animation(performer_id)

    state = _PERFORMER_STATES.get(performer_id)
    if state is None:
        state = {
            "session_count": 0,
            "animation_def": animation_def,
            "current": animation_def.default_pose.copy(),
            "target": animation_def.default_pose.copy(),
            "active_axes": set(),
            "transient": set(),
            "profile_state": {},
            "query_comp": factory.CreateQueryVariable(performer_id),
            "query_values": {},
        }
        _PERFORMER_STATES[performer_id] = state

    elif state["animation_def"].name != profile_id:
        state["animation_def"] = animation_def
        state["current"] = animation_def.default_pose.copy()
        state["target"] = animation_def.default_pose.copy()
        state["active_axes"].clear()
        state["transient"].clear()
        state["profile_state"].clear()

    state["session_count"] += 1
    _set_query(state, PLAYING_QUERY, 1.0)
    for axis in PERFORMANCE_AXES:
        _set_query(state, AXIS_QUERIES[axis], state["current"][axis])


def stop_performance_animation(performer_id):
    state = _PERFORMER_STATES.get(performer_id)
    if state is None:
        return
    state["session_count"] = max(0, state["session_count"] - 1)
    if state["session_count"] > 0:
        return

    _set_query(state, PLAYING_QUERY, 0.0)
    for query_name in AXIS_QUERIES.values():
        _set_query(state, query_name, 0.0)
    _PERFORMER_STATES.pop(performer_id, None)


def update_performance_notes(performer_id, profile_id, notes):
    state = _PERFORMER_STATES.get(performer_id)
    if state is None or state["animation_def"].name != profile_id or not notes:
        return

    updates, transient = state["animation_def"].resolve_pose(notes, state["profile_state"])
    state["target"].update(updates)
    state["active_axes"].update(updates)
    state["transient"].update(transient)


def on_performance_animation_tick():
    global _ANIMATION_TICK
    _ANIMATION_TICK += 1

    for performer_id, state in _PERFORMER_STATES.items():
        if (_ANIMATION_TICK + hash(performer_id)) % ANIMATION_TICK_INTERVAL != 0:
            continue

        animation_def = state["animation_def"]
        smoothing = 1.0 - (1.0 - animation_def.smoothing) ** ANIMATION_TICK_INTERVAL
        for axis in tuple(state["active_axes"]):
            current = state["current"][axis]
            target = state["target"][axis]
            if abs(target - current) <= ANIMATION_SNAP_EPSILON:
                current = target
                state["active_axes"].discard(axis)
            else:
                current += (target - current) * smoothing
            state["current"][axis] = current
            _set_query(state, AXIS_QUERIES[axis], current)

        for axis in state["transient"]:
            state["target"][axis] = animation_def.default_pose[axis]
            state["active_axes"].add(axis)
        state["transient"].clear()


def _set_query(state, query_name, value):
    if state["query_values"].get(query_name) == value:
        return
    state["query_comp"].Set(query_name, value)
    state["query_values"][query_name] = value


def handle_remove_player_aoi(args):
    remote_player_id = args["playerId"]
    _REGISTERED_PLAYERS.discard(remote_player_id)
    _PERFORMER_STATES.pop(remote_player_id, None)


def handle_remove_entity(args):
    _PERFORMER_STATES.pop(args["id"], None)
