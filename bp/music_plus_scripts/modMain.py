# -*- coding: utf-8 -*-
from .QuModLibs.QuMod import *

MUSIC_PLUS_MOD = EasyMod()

# 服务器注册
MUSIC_PLUS_MOD.Server("server.server")
# 事件注册
MUSIC_PLUS_MOD.Server("server.event.item_use")

# 客户端注册
MUSIC_PLUS_MOD.Client("client.client")
# 客户端网络
MUSIC_PLUS_MOD.Client("client.network.sound")
# 事件注册
MUSIC_PLUS_MOD.Client("client.event.tick")
