# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Client import *

COMPUTER_BLOCK = "music_plus:music_plus_computer"

factory = clientApi.GetEngineCompFactory()
game_comp = factory.CreateGame(levelId)


def is_computer_block(block_name):
    return block_name == COMPUTER_BLOCK


@AllowCall
def open_computer_ui(args=None):
    """由服务端 Call 或客户端直接调用，打开 MIDI 音乐库界面。"""
    from music_plus_scripts.client.ui.computer_ui import ComputerUI
    # 若已打开则不重复 push
    if ComputerUI.getUiNode() is None:
        ComputerUI.pushScreen()
    else:
        set_computer_ui_notice({"text": ""})


@AllowCall
def set_computer_ui_notice(args):
    """更新 MIDI 音乐库界面的提示文本。"""
    from music_plus_scripts.client.ui.computer_ui import ComputerUI, NOTICE_LABEL_PATH

    ui_node = ComputerUI.getUiNode()
    if ui_node is None:
        return
    ui_node.GetBaseUIControl(NOTICE_LABEL_PATH).asLabel().SetText(args.get("text", ""))
