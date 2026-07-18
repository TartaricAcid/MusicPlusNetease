# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Client import *
from music_plus_scripts.QuModLibs.UI import ScreenNodeWrapper
from music_plus_scripts.client.music.midi_analyzer import (
    ANALYSIS_VERSION,
    analyze_midi_payload,
    format_instrument_summary,
)
from music_plus_scripts.client.network.instrument import request_instrument_play, request_instrument_stop
from music_plus_scripts.client.store import midi_store

BASE_SCREEN_PATH = "/variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel"
BODY_PATH = BASE_SCREEN_PATH + "/body"
LEFT_INNER_PATH = BODY_PATH + "/left/left_inner"
SELECTION_PATH = LEFT_INNER_PATH + "/selection"
TITLE_LABEL_PATH = SELECTION_PATH + "/selection_inner/title"
DURATION_LABEL_PATH = SELECTION_PATH + "/selection_inner/duration"
ANALYSIS_LABEL_PATH = SELECTION_PATH + "/selection_inner/analysis"
NOTICE_LABEL_PATH = LEFT_INNER_PATH + "/notice"
RIGHT_PATH = BODY_PATH + "/right"
EMPTY_HINT_PATH = RIGHT_PATH + "/empty_hint"
SONG_SCROLL_PATH = RIGHT_PATH + "/song_scroll"

view_binder = clientApi.GetViewBinderCls()


def _format_duration(seconds):
    if not seconds or seconds <= 0:
        return "--:--"
    total = int(seconds)
    return "{}:{:02d}".format(total // 60, total % 60)


@ScreenNodeWrapper.autoRegister("music_plus_instrument_library.main")
class InstrumentUI(ScreenNodeWrapper):
    def __init__(self, namespace, name, param):
        super(InstrumentUI, self).__init__(namespace, name, param)
        self._selected_md5 = None
        self._song_keys = midi_store.list_midi_keys()

    def Create(self):
        ScreenNodeWrapper.Create(self)
        self._refresh_list()

    def _set_label(self, path, text):
        control = self.GetBaseUIControl(path)
        if control is not None:
            control.asLabel().SetText(text)

    def _set_notice(self, text):
        self._set_label(NOTICE_LABEL_PATH, text)

    def _refresh_list(self):
        self._song_keys = midi_store.list_midi_keys()
        is_empty = len(self._song_keys) == 0
        empty_hint = self.GetBaseUIControl(EMPTY_HINT_PATH)
        song_scroll = self.GetBaseUIControl(SONG_SCROLL_PATH)
        if empty_hint is not None:
            empty_hint.SetVisible(is_empty)
        if song_scroll is not None:
            song_scroll.SetVisible(not is_empty)

    def _on_song_select(self, midi_md5):
        self._selected_md5 = midi_md5
        meta = midi_store.get_meta(midi_md5) or {}
        self._set_label(TITLE_LABEL_PATH, meta.get("title", "") or "未命名")
        self._set_label(DURATION_LABEL_PATH, _format_duration(meta.get("duration", 0.0)))

        analysis = meta.get("analysis")
        if analysis is None or analysis.get("version") != ANALYSIS_VERSION:
            midi_payload = midi_store.get_midi(midi_md5)
            if midi_payload is not None:
                try:
                    analysis = analyze_midi_payload(midi_payload)
                    midi_store.update_meta(midi_md5, analysis=analysis)
                except Exception:
                    analysis = None

        instrument_summary = format_instrument_summary(analysis, "steinway")
        self._set_label(ANALYSIS_LABEL_PATH, instrument_summary)

        selection = self.GetBaseUIControl(SELECTION_PATH)
        if selection is not None:
            selection.SetVisible(True)
        self._set_notice("")

    @view_binder.binding(view_binder.BF_BindInt, "#music_plus_instrument_item_count")
    def music_plus_instrument_item_count(self):
        return len(self._song_keys)

    @view_binder.binding_collection(
        view_binder.BF_BindString,
        "music_plus_instrument_items",
        "#music_plus_instrument_title",
    )
    def music_plus_instrument_title(self, index):
        if index >= len(self._song_keys):
            return ""
        meta = midi_store.get_meta(self._song_keys[index]) or {}
        return meta.get("title", "") or "未命名"

    @view_binder.binding_collection(
        view_binder.BF_BindString,
        "music_plus_instrument_items",
        "#music_plus_instrument_duration",
    )
    def music_plus_instrument_duration(self, index):
        if index >= len(self._song_keys):
            return ""
        meta = midi_store.get_meta(self._song_keys[index]) or {}
        return _format_duration(meta.get("duration", 0.0))

    @view_binder.binding(view_binder.BF_ToggleChanged, "#music_plus_instrument_select")
    def music_plus_instrument_select(self, args):
        index = args["index"]
        if index < len(self._song_keys):
            self._on_song_select(self._song_keys[index])

    @view_binder.binding(view_binder.BF_ButtonClickUp, "#screen_close")
    def close(self, args):
        self.popScreen()

    @view_binder.binding(view_binder.BF_ButtonClickUp, "#music_plus_instrument_play")
    def play(self, args):
        if not self._selected_md5:
            return
        midi_payload = midi_store.get_midi(self._selected_md5)
        if midi_payload is None:
            self._set_notice("歌曲数据不存在")
            return
        self._set_notice("正在请求播放")
        request_instrument_play(midi_payload)

    @view_binder.binding(view_binder.BF_ButtonClickUp, "#music_plus_instrument_stop")
    def stop(self, args):
        request_instrument_stop()
