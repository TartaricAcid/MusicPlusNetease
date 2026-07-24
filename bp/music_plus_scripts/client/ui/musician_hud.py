# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Client import *
from music_plus_scripts.QuModLibs.UI import ScreenNodeWrapper

MUSICIAN_ENTITY = "music_plus:musician"

_ROOT = "/variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel"
BUTTON_GRID_PATH = _ROOT + "/button_grid"
EQUIP_BTN_PATH = BUTTON_GRID_PATH + "/top_row/equip_btn"
UNEQUIP_BTN_PATH = BUTTON_GRID_PATH + "/top_row/unequip_btn"
SELECT_BTN_PATH = BUTTON_GRID_PATH + "/bottom_row/select_btn"
RECALL_BTN_PATH = BUTTON_GRID_PATH + "/bottom_row/recall_btn"

factory = clientApi.GetEngineCompFactory()
camera = factory.CreateCamera(levelId)

# 当前点击选中的音乐家实体 ID
_target_musician_id = None


@ScreenNodeWrapper.autoRegister("music_plus_musician_hud.main")
class MusicianHud(ScreenNodeWrapper):
    def __init__(self, namespace, name, param):
        super(MusicianHud, self).__init__(namespace, name, param)

    def Create(self):
        ScreenNodeWrapper.Create(self)
        self.setButtonClickHandler(EQUIP_BTN_PATH, _on_equip)
        self.setButtonClickHandler(UNEQUIP_BTN_PATH, _on_unequip)
        self.setButtonClickHandler(SELECT_BTN_PATH, _on_select)
        self.setButtonClickHandler(RECALL_BTN_PATH, _on_recall)


def get_target_musician_id():
    return _target_musician_id


def _on_equip():
    if _target_musician_id is not None:
        Call("musician_equip", {"musician_id": _target_musician_id})


def _on_unequip():
    if _target_musician_id is not None:
        Call("musician_unequip", {"musician_id": _target_musician_id})


def _on_select():
    if _target_musician_id is not None:
        Call("musician_select", {"musician_id": _target_musician_id})


def _on_recall():
    if _target_musician_id is not None:
        Call("musician_recall", {"musician_id": _target_musician_id})


@Listen(Events.GetEntityByCoordEvent)
def on_get_entity_by_coord(args):
    """玩家点击屏幕时触发，检测点击位置是否命中音乐家。"""
    global _target_musician_id

    target_id = camera.GetChosenEntity()
    if target_id:
        target_type = factory.CreateEngineType(target_id).GetEngineTypeStr()
        if target_type == MUSICIAN_ENTITY:
            _target_musician_id = target_id
            _set_hud_visible(True)
            return

    _target_musician_id = None
    _set_hud_visible(False)


def _set_hud_visible(visible):
    ui_node = MusicianHud.getUiNode()
    if ui_node is None and visible:
        ui_node = MusicianHud.createUI()
    if ui_node is not None:
        ui_node.GetBaseUIControl(BUTTON_GRID_PATH).SetVisible(visible)
