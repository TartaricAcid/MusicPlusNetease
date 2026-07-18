# -*- coding: utf-8 -*-

import base64
import io

from music_plus_scripts.QuModLibs.Client import *
from music_plus_scripts.QuModLibs.UI import ScreenNodeWrapper
from music_plus_scripts.client.music.midi_analyzer import ANALYSIS_VERSION, analyze_midi_payload, format_analysis_summary
from music_plus_scripts.client.network.computer import request_paper_tape_burn
from music_plus_scripts.client.store import midi_store
from music_plus_scripts.mido import MidiFile
from music_plus_scripts.utils.midi_payload import get_midi_payload_md5, pack_midi_payload

# 根路径
BASE_SCREEN_PATH = "/variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel"
CLOSE_PATH = BASE_SCREEN_PATH + "/close_btn"

# 本体
BODY_PATH = BASE_SCREEN_PATH + "/body"

# 左侧
LEFT_INNER_PATH = BODY_PATH + "/left/left_inner"
NOTICE_LABEL_PATH = LEFT_INNER_PATH + "/notice_label"
PASTE_BTN_PATH = LEFT_INNER_PATH + "/paste_btn"

# 右侧编辑区域
EDIT_SECTION_PATH = LEFT_INNER_PATH + "/edit_section"
EDIT_INNER_PATH = EDIT_SECTION_PATH + "/edit_inner"
TITLE_EDIT_PATH = EDIT_INNER_PATH + "/title_edit"

# 右侧
RIGHT_PATH = BODY_PATH + "/right"

# 右侧组件
EMPTY_HINT_PATH = RIGHT_PATH + "/empty_hint"
SONG_SCROLL_PATH = RIGHT_PATH + "/song_scroll"

# 当前状态
MODE_IDLE = "idle"
MODE_PASTE = "paste"
MODE_EDIT = "edit"

factory = clientApi.GetEngineCompFactory()
game_comp = factory.CreateGame(levelId)
view_binder = clientApi.GetViewBinderCls()


def _format_duration(seconds):
    """将秒数格式化为 M:SS 字符串。"""
    if not seconds or seconds <= 0:
        return "--:--"
    total = int(seconds)
    m = total // 60
    s = total % 60
    return "{}:{:02d}".format(m, s)


def _extract_midi_title(midi_file):
    """读取第一个非空 track_name，作为歌曲名称默认值。"""
    for track in midi_file.tracks:
        title = track.name.strip().replace("\r", " ").replace("\n", " ")
        if title:
            return title[:50]
    return ""


@ScreenNodeWrapper.autoRegister("music_plus_midi_library.main")
class ComputerUI(ScreenNodeWrapper):
    def __init__(self, namespace, name, param):
        super(ComputerUI, self).__init__(namespace, name, param)
        self.mode = MODE_IDLE

        # 暂存的 midi 信息
        self._pending_payload = None
        self._pending_duration = 0.0
        self._pending_analysis = None
        self._selected_md5 = None

        # 右侧可用的 midi 列表
        self._song_keys = midi_store.list_midi_keys()

    def Create(self):
        ScreenNodeWrapper.Create(self)
        self._refresh_list()

    def _set_notice(self, text):
        notice_node = self.GetBaseUIControl(NOTICE_LABEL_PATH)
        if notice_node is not None:
            notice_node.asLabel().SetText(text)

    def _refresh_list(self):
        self._song_keys = midi_store.list_midi_keys()
        is_empty = len(self._song_keys) == 0
        empty_hint = self.GetBaseUIControl(EMPTY_HINT_PATH)
        song_scroll = self.GetBaseUIControl(SONG_SCROLL_PATH)
        if empty_hint is not None:
            empty_hint.SetVisible(is_empty)
        if song_scroll is not None:
            song_scroll.SetVisible(not is_empty)

    def _show_edit_section(self, visible):
        control = self.GetBaseUIControl(EDIT_SECTION_PATH)
        if control is not None:
            control.SetVisible(visible)

    def _get_title(self):
        control = self.GetBaseUIControl(TITLE_EDIT_PATH)
        if control is None:
            return ""
        return control.asTextEditBox().GetEditText()

    def _set_title(self, text):
        control = self.GetBaseUIControl(TITLE_EDIT_PATH)
        if control is not None:
            control.asTextEditBox().SetEditText(text)

    def _get_current_midi_info(self):
        if self.mode == MODE_PASTE:
            return {
                "midi": self._pending_payload,
                "duration": _format_duration(self._pending_duration),
                "title": self._get_title(),
                "analysis_summary": format_analysis_summary(self._pending_analysis),
            }
        if self.mode == MODE_EDIT and self._selected_md5:
            meta = midi_store.get_meta(self._selected_md5) or {}
            return {
                "midi": midi_store.get_midi(self._selected_md5),
                "duration": _format_duration(meta.get("duration", 0.0)),
                "title": meta.get("title", ""),
                "analysis_summary": format_analysis_summary(meta.get("analysis")),
            }
        return None

    def _enter_idle(self):
        """重置为空闲模式，隐藏编辑区，刷新列表。"""
        self.mode = MODE_IDLE
        self._pending_payload = None
        self._pending_duration = 0.0
        self._pending_analysis = None
        self._selected_md5 = None
        self._show_edit_section(False)
        self._refresh_list()

    def _on_song_select(self, md5_key):
        """点击右侧列表中某首曲目，在左侧显示其元信息供编辑。"""
        self._pending_payload = None
        self._pending_duration = 0.0
        self._pending_analysis = None
        self.mode = MODE_EDIT
        self._selected_md5 = md5_key

        meta = midi_store.get_meta(md5_key) or {}
        self._set_title(meta.get("title", ""))
        duration = meta.get("duration", 0.0)

        analysis = meta.get("analysis")
        if analysis is None or analysis.get("version") != ANALYSIS_VERSION:
            midi_payload = midi_store.get_midi(md5_key)
            if midi_payload is not None:
                try:
                    analysis = analyze_midi_payload(midi_payload)
                    midi_store.update_meta(md5_key, analysis=analysis)
                except Exception:
                    analysis = None

        self._set_notice("编辑模式 | {}\n{}".format(
            _format_duration(duration),
            format_analysis_summary(analysis, separator="\n"),
        ))

        self._show_edit_section(True)
        self._refresh_list()

    @view_binder.binding(view_binder.BF_BindInt, "#music_plus_midi_item_count")
    def music_plus_midi_item_count(self):
        return len(self._song_keys)

    @view_binder.binding_collection(
        view_binder.BF_BindString,
        "music_plus_midi_items",
        "#music_plus_midi_title",
    )
    def music_plus_midi_title(self, index):
        if index >= len(self._song_keys):
            return ""
        meta = midi_store.get_meta(self._song_keys[index]) or {}
        return meta.get("title", "") or "未命名"

    @view_binder.binding_collection(
        view_binder.BF_BindString,
        "music_plus_midi_items",
        "#music_plus_midi_duration",
    )
    def music_plus_midi_duration(self, index):
        if index >= len(self._song_keys):
            return ""
        meta = midi_store.get_meta(self._song_keys[index]) or {}
        return _format_duration(meta.get("duration", 0.0))

    @view_binder.binding(view_binder.BF_ToggleChanged, "#music_plus_midi_select")
    def music_plus_midi_select(self, args):
        index = args["index"]
        if index < len(self._song_keys):
            self._on_song_select(self._song_keys[index])

    @view_binder.binding(view_binder.BF_ButtonClickUp, '#screen_close')
    def close(self, args):
        self.popScreen()

    @view_binder.binding(view_binder.BF_ButtonClickUp, '#music_plus_midi_paste')
    def paste(self, args):
        clipboard_text = game_comp.GetClipboardContent()
        if not clipboard_text or not clipboard_text.startswith("TVRoZ"):
            self._set_notice("剪贴板中没有 MIDI 数据")
            return
        try:
            midi_bytes = base64.b64decode(clipboard_text)
        except Exception:
            self._set_notice("不是有效的 Base64 数据")
            return
        if not midi_bytes:
            self._set_notice("解码后数据为空")
            return
        try:
            midi_file = MidiFile(file=io.BytesIO(midi_bytes), charset="utf-8")
        except Exception:
            self._set_notice("MIDI 文件解析失败")
            return

        duration = float(midi_file.length)
        payload = pack_midi_payload(midi_bytes)

        # 重复歌曲不粘贴
        midi_md5 = get_midi_payload_md5(payload)
        if midi_store.has_midi(midi_md5):
            meta = midi_store.get_meta(midi_md5) or {}
            title = meta.get("title", "") or "未命名"
            self._set_notice("曲库中已存在：\n{}".format(title))
            return

        try:
            analysis = analyze_midi_payload(payload)
        except Exception:
            self._set_notice("MIDI 乐器信息分析失败")
            return

        self.mode = MODE_PASTE

        self._pending_payload = payload
        self._pending_duration = duration
        self._pending_analysis = analysis
        self._selected_md5 = None
        self._set_title(_extract_midi_title(midi_file))

        self._set_notice("已识别 MIDI ({})\n{}".format(
            _format_duration(duration),
            format_analysis_summary(analysis, separator="\n"),
        ))

        self._show_edit_section(True)
        self._refresh_list()

    @view_binder.binding(view_binder.BF_ButtonClickUp, '#music_plus_midi_save')
    def save(self, args):
        title = self._get_title().strip()
        if not title:
            self._set_notice("请先输入歌曲名称")
            return

        if self.mode == MODE_PASTE:
            if self._pending_payload is None:
                self._set_notice("没有可保存的 MIDI 数据")
                return
            midi_store.save_midi(
                self._pending_payload,
                title=title,
                duration=self._pending_duration,
                analysis=self._pending_analysis,
            )
            self._set_notice("已保存: \n" + title)
            self._enter_idle()

        elif self.mode == MODE_EDIT:
            if not self._selected_md5:
                self._set_notice("请先选择一首歌曲")
                return
            midi_store.update_meta(self._selected_md5, title=title)
            self._set_notice("已更新: \n" + title)
            self._enter_idle()

    @view_binder.binding(view_binder.BF_ButtonClickUp, '#music_plus_midi_burn')
    def burn(self, args):
        """将当前歌曲刻录到玩家背包中的第一张空白纸带。"""
        midi_info = self._get_current_midi_info()
        if midi_info is None:
            self._set_notice("请先选择或粘贴一首歌曲")
            return
        request_paper_tape_burn(midi_info)

    @view_binder.binding(view_binder.BF_ButtonClickUp, '#music_plus_midi_delete')
    def delete(self, args):
        """粘贴模式下取消粘贴；编辑模式下删除选中曲目。"""
        if self.mode == MODE_PASTE:
            self._enter_idle()
            return

        if self.mode == MODE_EDIT and self._selected_md5:
            meta = midi_store.get_meta(self._selected_md5)
            name = (meta.get("title", "") if meta else "") or "未命名"
            midi_store.remove_midi(self._selected_md5)
            self._set_notice("已删除: \n" + name)
            self._enter_idle()

        elif self.mode == MODE_EDIT:
            self._set_notice("请先选择一首歌曲")
