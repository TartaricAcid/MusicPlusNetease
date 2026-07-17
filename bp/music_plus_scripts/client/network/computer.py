# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Client import *


@AllowCall
def open_computer_ui(args):
    from music_plus_scripts.client.ui.computer_ui import ComputerUI
    # 若已打开则不重复 push
    if ComputerUI.getUiNode() is None:
        ComputerUI.pushScreen()
    else:
        set_computer_ui_notice({"text": ""})


@AllowCall
def set_computer_ui_notice(args):
    from music_plus_scripts.client.ui.computer_ui import ComputerUI, NOTICE_LABEL_PATH

    ui_node = ComputerUI.getUiNode()
    if ui_node is None:
        return
    notice_node = ui_node.GetBaseUIControl(NOTICE_LABEL_PATH)
    if notice_node is not None:
        notice_node.asLabel().SetText(args.get("text", ""))
