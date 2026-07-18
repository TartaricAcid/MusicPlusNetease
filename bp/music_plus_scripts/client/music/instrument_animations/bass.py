# -*- coding: utf-8 -*-

from music_plus_scripts.client.music.performance_animation_def import PerformanceAnimationDef


class BassPerformanceAnimation(PerformanceAnimationDef):
    name = "bass"
    default_pose = {
        "left_x": -5.0, "left_y": 0.0, "left_z": -32.0,
        "right_x": -30.0, "right_y": 0.0, "right_z": 0.0,
    }

    def resolve_pose(self, notes, state):
        right_z = self.notes_to_range(notes, 28, 67, -75.0, 5.0)
        right_x = self.default_pose["right_x"] - 32.0 * self.max_velocity(notes)
        return {"right_z": right_z, "right_x": right_x}, {"right_x"}
