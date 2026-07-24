# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Client import *

ENSEMBLE_RADIUS = 12
PREVIEW_DURATION = 30.0
PREVIEW_COLOR = (0.15, 0.85, 1.0)
GRID_COLOR = (0.12, 0.68, 0.82)
GRID_SPACING = 3
PERFORMER_COLOR = (0.2, 1.0, 0.3)
INSTRUMENT_TEXT_COLOR = (1.0, 1.0, 1.0)
ARROW_HEAD_HEIGHT = 2
ARROW_START_HEIGHT = 2.6
INSTRUMENT_TEXT_HEIGHT = 2.9

factory = clientApi.GetEngineCompFactory()
game = factory.CreateGame(levelId)

_preview_shapes = []
_preview_generation = 0


def toggle_podium_range_preview(pos, dimension, performers):
    if _preview_shapes:
        clear_podium_range()
        return False
    return show_podium_range(pos, dimension, performers)


def show_podium_range(pos, dimension, performers):
    clear_podium_range()
    if game.GetCurrentDimension() != dimension:
        return False

    drawing = factory.CreateDrawing(levelId)

    diameter = ENSEMBLE_RADIUS * 2
    box_pos = (
        pos[0] + 0.5 - ENSEMBLE_RADIUS,
        pos[1] + 0.5 - ENSEMBLE_RADIUS,
        pos[2] + 0.5 - ENSEMBLE_RADIUS,
    )
    shape = drawing.AddBoxShape(box_pos, (diameter, diameter, diameter), PREVIEW_COLOR)
    if shape is not None:
        shape.SetPriority(1)
        _preview_shapes.append(shape)
    _add_box_grid(drawing, box_pos, diameter)

    for performer in performers:
        marker_pos = _get_marker_pos(performer["entity_id"])
        if marker_pos is None:
            continue
        start_pos, end_pos, text_pos = marker_pos
        text = drawing.AddTextShape(
            text_pos, performer["instrument_name"], INSTRUMENT_TEXT_COLOR
        )
        if text is not None:
            text.SetPriority(2)
            _preview_shapes.append(text)
        arrow = drawing.AddArrowShape(start_pos, end_pos, PERFORMER_COLOR, 3, 0.25, 0.25)
        if arrow is not None:
            arrow.SetPriority(2)
            _preview_shapes.append(arrow)

    if not _preview_shapes:
        return False
    game.AddTimer(PREVIEW_DURATION, _expire_podium_range, _preview_generation)
    return True


def _add_box_grid(drawing, box_pos, diameter):
    min_x, min_y, min_z = box_pos
    max_x = min_x + diameter
    max_y = min_y + diameter
    max_z = min_z + diameter

    for offset in range(GRID_SPACING, diameter, GRID_SPACING):
        x = min_x + offset
        y = min_y + offset
        z = min_z + offset
        segments = (
            ((x, min_y, min_z), (x, min_y, max_z)),
            ((x, max_y, min_z), (x, max_y, max_z)),
            ((x, min_y, min_z), (x, max_y, min_z)),
            ((x, min_y, max_z), (x, max_y, max_z)),
            ((min_x, y, min_z), (max_x, y, min_z)),
            ((min_x, y, max_z), (max_x, y, max_z)),
            ((min_x, y, min_z), (min_x, y, max_z)),
            ((max_x, y, min_z), (max_x, y, max_z)),
            ((min_x, min_y, z), (max_x, min_y, z)),
            ((min_x, max_y, z), (max_x, max_y, z)),
            ((min_x, min_y, z), (min_x, max_y, z)),
            ((max_x, min_y, z), (max_x, max_y, z)),
        )
        for start_pos, end_pos in segments:
            shape = drawing.AddLineShape(start_pos, end_pos, GRID_COLOR)
            if shape is not None:
                _preview_shapes.append(shape)


def _get_marker_pos(performer_id):
    entity_pos = factory.CreatePos(performer_id).GetPos()
    if entity_pos is None:
        return None
    x, y, z = entity_pos
    return (
        (x, y + ARROW_START_HEIGHT, z),
        (x, y + ARROW_HEAD_HEIGHT, z),
        (x, y + INSTRUMENT_TEXT_HEIGHT, z),
    )


def _expire_podium_range(generation):
    if generation != _preview_generation:
        return
    clear_podium_range()


def clear_podium_range():
    global _preview_generation
    _preview_generation += 1
    while _preview_shapes:
        _preview_shapes.pop().Remove()
