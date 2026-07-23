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

_REGISTRY = {}
_REGISTERED_PLAYERS = set()
_REGISTERED_ACTORS = set()
_PERFORMER_STATES = {}

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
            "transient": set(),
            "profile_state": {},
        }
        _PERFORMER_STATES[performer_id] = state

    elif state["animation_def"].name != profile_id:
        state["animation_def"] = animation_def
        state["current"] = animation_def.default_pose.copy()
        state["target"] = animation_def.default_pose.copy()
        state["transient"].clear()
        state["profile_state"].clear()

    state["session_count"] += 1
    _set_query(performer_id, PLAYING_QUERY, 1.0)
    for axis in PERFORMANCE_AXES:
        _set_query(performer_id, AXIS_QUERIES[axis], state["current"][axis])


def stop_performance_animation(performer_id):
    state = _PERFORMER_STATES.get(performer_id)
    if state is None:
        return
    state["session_count"] = max(0, state["session_count"] - 1)
    if state["session_count"] > 0:
        return

    _set_query(performer_id, PLAYING_QUERY, 0.0)
    for query_name in AXIS_QUERIES.values():
        _set_query(performer_id, query_name, 0.0)
    _PERFORMER_STATES.pop(performer_id, None)


def update_performance_notes(performer_id, profile_id, notes):
    state = _PERFORMER_STATES.get(performer_id)
    if state is None or state["animation_def"].name != profile_id or not notes:
        return

    updates, transient = state["animation_def"].resolve_pose(notes, state["profile_state"])
    state["target"].update(updates)
    state["transient"].update(transient)


def on_performance_animation_tick():
    for performer_id, state in _PERFORMER_STATES.items():
        animation_def = state["animation_def"]
        for axis in PERFORMANCE_AXES:
            current = state["current"][axis]
            target = state["target"][axis]
            current += (target - current) * animation_def.smoothing
            state["current"][axis] = current
            _set_query(performer_id, AXIS_QUERIES[axis], current)

        for axis in state["transient"]:
            state["target"][axis] = animation_def.default_pose[axis]
        state["transient"].clear()


def _set_query(performer_id, query_name, value):
    factory.CreateQueryVariable(performer_id).Set(query_name, value)


def handle_remove_player_aoi(args):
    remote_player_id = args["playerId"]
    _REGISTERED_PLAYERS.discard(remote_player_id)
    _PERFORMER_STATES.pop(remote_player_id, None)


def handle_remove_entity(args):
    _PERFORMER_STATES.pop(args["id"], None)
