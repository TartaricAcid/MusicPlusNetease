# -*- coding: utf-8 -*-
from .QuModLibs.QuMod import *

MUSIC_PLUS_MOD = EasyMod()

# 服务器注册
MUSIC_PLUS_MOD.Server("server.server")
# 事件注册
MUSIC_PLUS_MOD.Server("server.event.item_use")
MUSIC_PLUS_MOD.Server("server.event.block_use")
MUSIC_PLUS_MOD.Server("server.event.block_remove")
# 服务端网络
MUSIC_PLUS_MOD.Server("server.network.paper_tape")

# 客户端注册
MUSIC_PLUS_MOD.Client("client.client")
# 客户端网络
MUSIC_PLUS_MOD.Client("client.network.sound")
MUSIC_PLUS_MOD.Client("client.network.player")
# 事件注册
MUSIC_PLUS_MOD.Client("client.event.tick")
MUSIC_PLUS_MOD.Client("client.event.item_use")
