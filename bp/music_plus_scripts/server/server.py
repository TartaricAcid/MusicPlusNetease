# -*- coding: utf-8 -*-

from music_plus_scripts.QuModLibs.Server import *

factory = serverApi.GetEngineCompFactory()
item_comp = factory.CreateItem(levelId)

# 添加 Use Data 白名单事件
item_comp.GetUserDataInEvent("ServerItemUseOnEvent")
item_comp.GetUserDataInEvent("ServerBlockUseEvent")
item_comp.GetUserDataInEvent("BlockRemoveServerEvent")
