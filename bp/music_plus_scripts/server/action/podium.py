# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Server import serverApi
from music_plus_scripts.server.action.handheld_instrument import get_entity_instrument
from music_plus_scripts.server.action.instrument_playback import (
    play_ensemble_playback,
    stop_instrument_playbacks,
)
from music_plus_scripts.server.action.musician import MUSICIAN_ENTITY

PODIUM_BLOCK = "music_plus:music_plus_podium"
ENSEMBLE_RADIUS = 12

factory = serverApi.GetEngineCompFactory()
game = factory.CreateGame(serverApi.GetLevelId())

_PODIUM_PLAYBACKS = {}


def _get_podium_key(pos, dimension):
    return "{}:{}:{}:{}".format(dimension, pos[0], pos[1], pos[2])


def get_ensemble_performers(pos, dimension):
    min_pos = tuple(value - ENSEMBLE_RADIUS for value in pos)
    max_pos = tuple(value + ENSEMBLE_RADIUS for value in pos)
    entity_ids = list(game.GetEntitiesInSquareArea(None, min_pos, max_pos, dimension))

    for player_id in serverApi.GetPlayerList():
        if player_id not in entity_ids:
            entity_ids.append(player_id)

    performers = []
    playback_keys = set()
    for entity_id in entity_ids:
        entity_type = factory.CreateEngineType(entity_id).GetEngineTypeStr()
        if entity_type not in ("minecraft:player", MUSICIAN_ENTITY):
            continue
        if factory.CreateDimension(entity_id).GetEntityDimensionId() != dimension:
            continue

        entity_pos = factory.CreatePos(entity_id).GetPos()
        if entity_pos is None:
            continue
        if any(entity_pos[index] < min_pos[index] or entity_pos[index] > max_pos[index] for index in range(3)):
            continue

        instrument = get_entity_instrument(entity_id)
        if instrument is None or instrument["playback_key"] in playback_keys:
            continue
        playback_keys.add(instrument["playback_key"])
        performers.append((instrument, entity_id))
    return performers


def play_podium_ensemble(pos, dimension, midi_payload, midi_md5):
    stop_podium_ensemble(pos, dimension)
    performers = get_ensemble_performers(pos, dimension)
    if not performers:
        return 0

    play_ensemble_playback(midi_payload, midi_md5, performers)
    _PODIUM_PLAYBACKS[_get_podium_key(pos, dimension)] = [
        instrument["playback_key"] for instrument, performer_id in performers
    ]
    return len(performers)


def stop_podium_ensemble(pos, dimension):
    playback_keys = _PODIUM_PLAYBACKS.pop(_get_podium_key(pos, dimension), [])
    stop_instrument_playbacks(playback_keys)
    return len(playback_keys)
