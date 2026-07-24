# -*- coding: utf-8 -*-
from .QuModLibs.QuMod import *

MUSIC_PLUS_MOD = EasyMod()

# 服务器注册
MUSIC_PLUS_MOD.Server("server.server")
# 事件注册
MUSIC_PLUS_MOD.Server("server.event.item_use")
MUSIC_PLUS_MOD.Server("server.event.block_use")
MUSIC_PLUS_MOD.Server("server.event.block_remove")
MUSIC_PLUS_MOD.Server("server.event.redstone")
MUSIC_PLUS_MOD.Server("server.event.entity")
MUSIC_PLUS_MOD.Server("server.event.player")
# 服务端网络
MUSIC_PLUS_MOD.Server("server.network.paper_tape")
MUSIC_PLUS_MOD.Server("server.network.instrument")
MUSIC_PLUS_MOD.Server("server.network.podium")

# 客户端注册
MUSIC_PLUS_MOD.Client("client.client")
# 客户端网络
MUSIC_PLUS_MOD.Client("client.network.sound")
MUSIC_PLUS_MOD.Client("client.network.player")
MUSIC_PLUS_MOD.Client("client.network.computer")
MUSIC_PLUS_MOD.Client("client.network.instrument")
MUSIC_PLUS_MOD.Client("client.network.podium")
# 事件注册
MUSIC_PLUS_MOD.Client("client.event.tick")
MUSIC_PLUS_MOD.Client("client.event.item_use")
MUSIC_PLUS_MOD.Client("client.event.render")
MUSIC_PLUS_MOD.Client("client.event.script")
MUSIC_PLUS_MOD.Client("client.event.player")
# UI 注册
MUSIC_PLUS_MOD.Client("client.ui.computer_ui")
MUSIC_PLUS_MOD.Client("client.ui.instrument_ui")
MUSIC_PLUS_MOD.Client("client.ui.instrument_hud")
