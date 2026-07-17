# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Client import *
from music_plus_scripts.client.network.instrument import open_instrument_ui
from music_plus_scripts.client.ui.instrument_hud import InstrumentHud


@Listen(Events.ClientPlayerInventoryOpenEvent)
def on_inventory_open(args):
    ui_node = InstrumentHud.getUiNode()
    if ui_node is None:
        return
    args["cancel"] = True
    open_instrument_ui()
