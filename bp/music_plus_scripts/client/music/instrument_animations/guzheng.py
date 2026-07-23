# -*- coding: utf-8 -*-

from music_plus_scripts.client.music.performance_animation_def import PerformanceAnimationDef


class GuzhengPerformanceAnimation(PerformanceAnimationDef):
    """古筝：右手拨弦，左手在筝码左侧按弦并做轻微揉弦。"""

    name = "guzheng"
    default_pose = {
        "left_x": -62.0, "left_y": -24.0, "left_z": -10.0,
        "right_x": -68.0, "right_y": 28.0, "right_z": 6.0,
    }

    MIN_NOTE = 36
    MAX_NOTE = 96

    def resolve_pose(self, notes, state):
        ordered = sorted(notes, key=lambda item: item[0])
        if len(ordered) == 1:
            left_notes = []
            right_notes = ordered
        else:
            split = len(ordered) // 2
            left_notes = ordered[:split]
            right_notes = ordered[split:]

        updates = {}
        transient = set()
        if left_notes:
            updates["left_x"] = self.default_pose["left_x"] - 12.0 * self.max_velocity(left_notes)
            updates["left_y"] = self.notes_to_range(
                left_notes, self.MIN_NOTE, self.MAX_NOTE, -42.0, -8.0
            )
            # 左手按弦时有轻微横向揉弦，下一帧自动回到自然位置。
            updates["left_z"] = self.default_pose["left_z"] - 10.0
            transient.update(("left_x", "left_z"))

        if right_notes:
            updates["right_x"] = self.default_pose["right_x"] - 30.0 * self.max_velocity(right_notes)
            updates["right_y"] = self.notes_to_range(
                right_notes, self.MIN_NOTE, self.MAX_NOTE, 8.0, 58.0
            )
            transient.add("right_x")

        return updates, transient
