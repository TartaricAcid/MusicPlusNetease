# -*- coding: utf-8 -*-

from music_plus_scripts.client.music.performance_animation_def import PerformanceAnimationDef


class PianoPerformanceAnimation(PerformanceAnimationDef):
    name = "piano"
    default_pose = {
        "left_x": -60.0, "left_y": 0.0, "left_z": 0.0,
        "right_x": -60.0, "right_y": 0.0, "right_z": 0.0,
    }

    MIN_NOTE = 21
    MAX_NOTE = 108
    HAND_SPLIT_NOTE = 60

    def resolve_pose(self, notes, state):
        ordered = sorted(notes, key=lambda item: item[0])
        if len(ordered) == 1:
            left_notes = ordered if ordered[0][0] < self.HAND_SPLIT_NOTE else []
            right_notes = ordered if not left_notes else []
        else:
            split = len(ordered) // 2
            left_notes = ordered[:split]
            right_notes = ordered[split:]

        updates = {}
        if left_notes:
            updates["left_x"] = self.default_pose["left_x"] - 32.0 * self.max_velocity(left_notes)
            updates["left_y"] = self.notes_to_range(
                left_notes, self.MIN_NOTE, self.MAX_NOTE, -120.0, 120.0
            )
        if right_notes:
            updates["right_x"] = self.default_pose["right_x"] - 32.0 * self.max_velocity(right_notes)
            updates["right_y"] = self.notes_to_range(
                right_notes, self.MIN_NOTE, self.MAX_NOTE, -120.0, 120.0
            )
        return updates, set(updates.keys())
