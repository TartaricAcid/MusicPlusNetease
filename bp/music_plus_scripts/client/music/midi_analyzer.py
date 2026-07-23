# -*- coding: utf-8 -*-

"""按实际播放规则分析 MIDI 在各类方块乐器上的可播放音符数。"""

from music_plus_scripts.client.music.gm_program_map import resolve_program_sound_prefix
from music_plus_scripts.client.music.instruments import get_instrument
from music_plus_scripts.mido.midi_decoder import NOTE_ON, decode_midi_payload

GM_PERCUSSION_CHANNEL = 9
ANALYSIS_VERSION = 1

# (标识, 显示名, 分类标识, 分类显示名, 默认声音前缀, Program 乐器组)
INSTRUMENT_TARGETS = (
    ("music_box", "八音盒", "music_box", "八音盒类", "music_plus.music_box", "music_box"),
    ("vibra", "颤音琴", "music_box", "八音盒类", "music_plus.vibra", "music_box"),
    ("piano", "钢琴", "piano", "钢琴类", "music_plus.piano", "piano"),
    ("harpsichord", "羽管键琴", "piano", "钢琴类", "music_plus.harpsichord", "piano"),
    ("honkytonk", "酒吧钢琴", "piano", "钢琴类", "music_plus.honkytonk", "piano"),
    ("rhodes", "电钢琴", "piano", "钢琴类", "music_plus.rhodes", "piano"),
    ("ce_guitar", "电吉他", "guitar", "吉他类", "music_plus.ce_guitar", "guitar"),
    ("nylon_guitar", "尼龙吉他", "guitar", "吉他类", "music_plus.nylon_guitar", "guitar"),
    ("guzheng", "古筝", "guzheng", "古筝", "music_plus.guzheng", "guzheng"),
    ("violin_solo", "小提琴", "violin", "小提琴", "music_plus.violin_solo", "violin"),
    ("trumpet", "小号", "brass", "铜管类", "music_plus.trumpet", "brass"),
    ("flute", "长笛", "pipe", "管乐类", "music_plus.flute", "pipe"),
    ("bass", "贝斯", "bass", "贝斯", "music_plus.bass", "bass"),
    ("real_kit", "原声鼓组", "drum_kit", "鼓组", "music_plus.real_kit", "drum_kit"),
    ("linn_kit", "电子鼓组", "drum_kit", "鼓组", "music_plus.linn_kit", "drum_kit"),
)


def analyze_midi_payload(midi_payload):
    """返回各乐器按当前播放规则预计可播放的 note_on 数量。"""
    events = decode_midi_payload(midi_payload)
    note_events = [event for event in events if event[1] == NOTE_ON]
    program_counts = {}
    for event in note_events:
        program = event[5] if len(event) > 5 else 0
        key = str(program)
        program_counts[key] = program_counts.get(key, 0) + 1

    instruments = {}
    groups = {}
    for target in INSTRUMENT_TARGETS:
        target_id, label, group_id, group_label, default_prefix, instrument_group = target
        result = _analyze_target(note_events, default_prefix, instrument_group)
        result["label"] = label
        result["group"] = group_id
        instruments[target_id] = result

        current = groups.get(group_id)
        if current is None or result["playable"] > current["playable"]:
            groups[group_id] = {
                "label": group_label,
                "playable": result["playable"],
                "instrument": target_id,
                "instrument_label": label,
            }

    return {
        "version": ANALYSIS_VERSION,
        "total_notes": len(note_events),
        "programs": program_counts,
        "instruments": instruments,
        "groups": groups,
    }


def format_analysis_summary(analysis, limit=3, separator="、 "):
    """生成适合 UI 和纸带 tooltip 的简短可演奏性摘要。"""
    if not analysis:
        return "乐器分析： 暂无"

    total = analysis.get("total_notes", 0)
    if total <= 0:
        return "乐器分析： 没有音符"

    groups = analysis.get("groups", {})
    candidates = [group for group in groups.values() if group.get("playable", 0) > 0]
    candidates.sort(key=lambda item: (-item.get("playable", 0), item.get("label", "")))
    if not candidates:
        return "可演奏： 无匹配乐器 (0/{})".format(total)

    parts = []
    for group in candidates[:limit]:
        parts.append("{} {}/{}".format(group["label"], group["playable"], total))
    return "可演奏： " + separator.join(parts)


def format_instrument_summary(analysis, target_id):
    """生成单个方块乐器的可播放数量及跳过原因。"""
    if not analysis:
        return "乐器分析： 暂无"

    total = analysis.get("total_notes", 0)
    result = analysis.get("instruments", {}).get(target_id)
    if result is None:
        return "乐器分析： 暂无"

    text = "{}可播放： {}/{}".format(result.get("label", "乐器"), result.get("playable", 0), total)
    skipped = []

    if result.get("channel_skipped", 0) > 0:
        channel_label = "旋律通道" if result.get("group") == "drum_kit" else "鼓组通道"
        skipped.append("{} {}".format(channel_label, result["channel_skipped"]))

    if result.get("program_skipped", 0) > 0:
        skipped.append("乐器不匹配 {}".format(result["program_skipped"]))

    if result.get("range_skipped", 0) > 0:
        skipped.append("超出音域 {}".format(result["range_skipped"]))

    if skipped:
        text += "\n跳过： " + "、 ".join(skipped)
    return text


def _analyze_target(note_events, default_prefix, instrument_group):
    playable = 0
    channel_skipped = 0
    program_skipped = 0
    range_skipped = 0
    is_drum_group = instrument_group == "drum_kit"

    for event in note_events:
        channel = event[2]
        if (channel == GM_PERCUSSION_CHANNEL) != is_drum_group:
            channel_skipped += 1
            continue

        program = event[5] if len(event) > 5 else 0
        resolved_prefix = resolve_program_sound_prefix(default_prefix, instrument_group, program)
        if resolved_prefix is None:
            program_skipped += 1
            continue

        instrument = get_instrument(resolved_prefix)
        if instrument is None or instrument.resolve(event[3]) is None:
            range_skipped += 1
            continue
        playable += 1

    return {
        "playable": playable,
        "channel_skipped": channel_skipped,
        "program_skipped": program_skipped,
        "range_skipped": range_skipped,
    }
