# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Client import *
from music_plus_scripts.QuModLibs.UI import ScreenNodeWrapper
from music_plus_scripts.client.network.instrument import open_instrument_ui

BUTTON_PATH = "/variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/button"


@ScreenNodeWrapper.autoRegister("music_plus_instrument_hud.main")
class InstrumentHud(ScreenNodeWrapper):
    def __init__(self, namespace, name, param):
        super(InstrumentHud, self).__init__(namespace, name, param)

    def Create(self):
        ScreenNodeWrapper.Create(self)
        self.setButtonClickHandler(BUTTON_PATH, open_instrument_ui)


@AllowCall
def set_instrument_hud_visible(args):
    ui_node = InstrumentHud.getUiNode()
    if ui_node is None:
        ui_node = InstrumentHud.createUI()
    if ui_node is not None:
        ui_node.GetBaseUIControl(BUTTON_PATH).SetVisible(args["visible"])
