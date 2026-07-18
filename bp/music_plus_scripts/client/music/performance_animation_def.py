# -*- coding: utf-8 -*-

"""乐器演奏动画定义。"""

PERFORMANCE_AXES = ("left_x", "left_y", "left_z", "right_x", "right_y", "right_z")


class PerformanceAnimationDef(object):
    """描述一种乐器的默认手臂姿态和 MIDI 音符动画映射。"""

    name = None
    smoothing = 0.35
    default_pose = {}

    def __init__(self):
        self.default_pose = dict(
            (axis, float(self.default_pose.get(axis, 0.0)))
            for axis in PERFORMANCE_AXES
        )

    def resolve_pose(self, notes, state):
        """返回 (本次目标轴, 需要自动复位的瞬时轴)。"""
        raise NotImplementedError

    @staticmethod
    def notes_to_range(notes, min_note, max_note, min_value, max_value):
        velocity_sum = sum(max(0.01, velocity) for _, velocity in notes)
        note = sum(midi_note * max(0.01, velocity) for midi_note, velocity in notes) / velocity_sum
        normalized = (note - min_note) / float(max_note - min_note)
        normalized = max(0.0, min(1.0, normalized))
        return min_value + (max_value - min_value) * normalized

    @staticmethod
    def max_velocity(notes):
        return max(velocity for _, velocity in notes)
