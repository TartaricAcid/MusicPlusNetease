# -*- coding: utf-8 -*-

from ktavern_scripts.QuModLibs.Server import *

factory = serverApi.GetEngineCompFactory()
mc_enum = serverApi.GetMinecraftEnum()
block_info = factory.CreateBlockInfo(levelId)

if 0 > 1:
    from typing import *


def block_has_tag(block_name, check_tag):
    """
    判断方块是否含有此 tag
    """
    tags = block_info.GetBlockTags(block_name)
    if tags is None:
        return False
    return check_tag in tags


def init_block_entity_data(be_data, key, default_value=None):
    # type: (Any, str, object) -> Any
    """
    获取方块实体数据
    """
    data = be_data[key]
    if data is None:
        be_data[key] = default_value
        return default_value
    return data


def be_data_fix(be_data):
    # type: (Any) -> dict
    """
    新版网易更新后，BlockEntityData 强制要求必须是 dict 类型，否则会报错。
    该方法用于将 BlockEntityData 转换为 dict
    """
    if isinstance(be_data, dict):
        return be_data
    return {k: v for k, v in vars(be_data).items() if not k.startswith('_')}
