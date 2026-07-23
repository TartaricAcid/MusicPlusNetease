# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Client import *
from music_plus_scripts.client.ui.instrument_hud import set_instrument_hud_visible

# 钢琴等方块类乐器，需要玩家右键骑乘上去才能演奏使用
INSTRUMENT_MODE_SEATED = "seated"

# 贝斯等物品类乐器，主手拿着就能演奏使用
INSTRUMENT_MODE_HANDHELD = "handheld"

# 当前选曲界面控制的乐器和实际演奏实体。
_CURRENT_CONTEXT = None

factory = clientApi.GetEngineCompFactory()
camera = factory.CreateCamera(levelId)
player_rot = factory.CreateRot(playerId)


def get_instrument_target_id():
    if _CURRENT_CONTEXT is None:
        return None
    return _CURRENT_CONTEXT["target_id"]


def get_instrument_performer_id():
    if _CURRENT_CONTEXT is None:
        return None
    return _CURRENT_CONTEXT["performer_id"]


def set_instrument_context(target_id, mode=None, view_yaw=None, performer_id=None):
    global _CURRENT_CONTEXT
    resolved_performer_id = performer_id if performer_id is not None else playerId
    _CURRENT_CONTEXT = {
        "target_id": target_id,
        "mode": mode,
        "performer_id": resolved_performer_id,
    } if target_id is not None else None

    is_local_performer = resolved_performer_id == playerId
    is_local_seated = (
            target_id is not None
            and is_local_performer
            and mode == INSTRUMENT_MODE_SEATED
    )
    if is_local_seated and view_yaw is not None:
        player_rot.SetRot((10, view_yaw))

    set_instrument_hud_visible(target_id is not None and is_local_performer, is_local_seated)

    from music_plus_scripts.client.ui.instrument_ui import InstrumentUI
    ui_node = InstrumentUI.getUiNode()
    if ui_node is not None and target_id is None:
        ui_node.popScreen()

    elif ui_node is not None:
        ui_node.refresh_instrument_analysis()
