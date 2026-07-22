# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Client import *
from music_plus_scripts.QuModLibs.UI import ScreenNodeWrapper
from music_plus_scripts.client.network.instrument import open_instrument_ui

BUTTON_PATH = "/variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/button"

factory = clientApi.GetEngineCompFactory()
camera = factory.CreateCamera(levelId)
player_rot = factory.CreateRot(playerId)

_instrument_camera_departed = False


@ScreenNodeWrapper.autoRegister("music_plus_instrument_hud.main")
class InstrumentHud(ScreenNodeWrapper):
    def __init__(self, namespace, name, param):
        super(InstrumentHud, self).__init__(namespace, name, param)

    def Create(self):
        ScreenNodeWrapper.Create(self)
        self.setButtonClickHandler(BUTTON_PATH, open_instrument_ui)


def set_instrument_hud_visible(visible, depart_camera=False):
    global _instrument_camera_departed
    if visible and depart_camera and not _instrument_camera_departed:
        camera.DepartCamera()
        player_rot.LockLocalPlayerRot(True)
        _instrument_camera_departed = True

    elif _instrument_camera_departed and (not visible or not depart_camera):
        player_rot.LockLocalPlayerRot(False)
        camera.UnDepartCamera()
        _instrument_camera_departed = False

    # 显示按钮
    ui_node = InstrumentHud.getUiNode()
    if ui_node is None and visible:
        ui_node = InstrumentHud.createUI()
    if ui_node is not None:
        ui_node.GetBaseUIControl(BUTTON_PATH).SetVisible(visible)
