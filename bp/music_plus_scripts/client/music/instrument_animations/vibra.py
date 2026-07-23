# -*- coding: utf-8 -*-

from music_plus_scripts.client.music.performance_animation_def import PerformanceAnimationDef


class VibraPerformanceAnimation(PerformanceAnimationDef):
    """颤音琴：双手持槌，在琴键上方交替下击。"""

    name = "vibra"
    default_pose = {
        "left_x": -75.0, "left_y": -18.0, "left_z": -14.0,
        "right_x": -75.0, "right_y": 18.0, "right_z": 14.0,
    }

    MIN_NOTE = 36
    MAX_NOTE = 96

    def resolve_pose(self, notes, state):
        ordered = sorted(notes, key=lambda item: item[0])
        updates = {}
        transient = set()
        next_hand = state.get("next_hand", 0)

        # 将同一批音符分配给两支槌，保证和弦也能形成交替击打动作。
        for note in ordered:
            hand = next_hand
            prefix = "left_" if hand == 0 else "right_"
            updates[prefix + "x"] = self.default_pose[prefix + "x"] - 34.0 * note[1]
            updates[prefix + "y"] = self.notes_to_range(
                [note], self.MIN_NOTE, self.MAX_NOTE, -45.0, 45.0
            )
            transient.add(prefix + "x")
            next_hand = 1 - hand

        state["next_hand"] = next_hand
        return updates, transient
