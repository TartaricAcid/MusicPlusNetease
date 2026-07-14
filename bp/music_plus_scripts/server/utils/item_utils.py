# -*- coding: utf-8 -*-
import ast
import copy

from music_plus_scripts.QuModLibs.Server import *

factory = serverApi.GetEngineCompFactory()
mc_enum = serverApi.GetMinecraftEnum()

CARRIED = mc_enum.ItemPosType.CARRIED  # type: int
INVENTORY = mc_enum.ItemPosType.INVENTORY  # type: int


def consume_mainhand_durability(player_id, cost=1):
    # type: (Union[str,int], int) -> 'bool'
    """
    损耗主手物品耐久
    """
    item_comp = factory.CreateItem(player_id)

    durability = item_comp.GetItemDurability(CARRIED, 0)
    durability = durability - cost if durability > cost else 0

    # 如果耐久为 0，那么把物品置空并播放破碎音效
    if durability <= 0:
        # 播放音效
        pos = factory.CreatePos(player_id).GetPos()
        msg_data = {
            "pos": (pos[0], pos[1] + 0.5, pos[2]),
            "sound": {"name": "random.break"}
        }
        Call(player_id, "play_sound", msg_data)
        return item_comp.SetInvItemNum(item_comp.GetSelectSlotId(), 0)
    else:
        return item_comp.SetItemDurability(CARRIED, 0, durability)


def reduce_carried_item_num(player_id, reduce_num):
    # type: (Union[str,int], int ) -> 'bool'
    item_comp = factory.CreateItem(player_id)
    select_slot_id = item_comp.GetSelectSlotId()
    item_dict = item_comp.GetPlayerItem(INVENTORY, select_slot_id)
    if item_dict is None:
        return False
    result_count = item_dict['count'] - reduce_num
    if result_count < 0:
        result_count = 0
    return item_comp.SetInvItemNum(select_slot_id, result_count)


def get_item_dict(item_name, count=1, user_data=None):
    # type: (str, int, dict) -> 'dict'
    """
    获取物品字典
    """
    item_dict = {
        "newItemName": item_name,
        "count": count
    }
    if user_data is not None:
        item_dict["userData"] = user_data
    return item_dict


def give_player_item_dict(player_id, item_dict):
    # type: (Union[str,int],dict) -> None
    item_comp = factory.CreateItem(player_id)
    result = item_comp.SpawnItemToPlayerInv(item_dict, player_id)
    # 如果失败，说明背包满了，扔到玩家脚下
    if not result:
        position = factory.CreatePos(player_id).GetFootPos()
        dim_id = factory.CreateDimension(player_id).GetEntityDimensionId()
        System.CreateEngineItemEntity(item_dict, dim_id, position)


def copy_with_count(item_dict, count=1):
    # type: (dict, int) -> 'dict'
    """
    复制物品字典并设置数量
    """
    new_item_dict = copy.deepcopy(item_dict)
    new_item_dict["count"] = count
    return new_item_dict


def spawn_item_in_world(mod_system, item_name, count, position, dimension_id):
    # type: (Any, str, int, 'Tuple[float,float,float]', int) -> None
    drop_item = {
        "newItemName": item_name,
        "count": count
    }
    mod_system.CreateEngineItemEntity(drop_item, dimension_id, position)


def get_mainhand_item_dict(player_id, get_user_data=False):
    # type: (Union[str,int], bool) -> 'Union[dict,None]'
    item_comp = factory.CreateItem(player_id)
    select_slot_id = item_comp.GetSelectSlotId()
    return item_comp.GetPlayerItem(INVENTORY, select_slot_id, get_user_data)


def set_mainhand_item_dict(player_id, item_dict):
    # type: (Union[str,int], dict) -> None
    item_comp = factory.CreateItem(player_id)
    select_slot_id = item_comp.GetSelectSlotId()
    # 需要先清空才能设置……
    item_comp.SetInvItemNum(select_slot_id, 0)
    item_comp.SpawnItemToPlayerCarried(item_dict, player_id)


def set_mainhand_item(player_id, item_name, count, durability=0):
    # type: (Union[str,int], str, int, int) -> None
    item_dict = {
        "newItemName": item_name,
        "count": count
    }
    if durability > 0:
        item_dict["durability"] = durability
    set_mainhand_item_dict(player_id, item_dict)


def item_is_empty(item_name):
    return item_name is None or item_name == "" or item_name == "minecraft:air"


def item_dict_is_empty(item_dict):
    if item_dict is None:
        return True
    if type(item_dict) is not dict:
        return True
    item_name = item_dict.get("newItemName", None)
    count = item_dict.get("count", 0)
    return item_is_empty(item_name) or count <= 0


def get_air():
    return {
        "newItemName": "minecraft:air",
        "count": 0
    }


def filter_empty_items(*items):
    # type: (*str) -> 'List[str]'
    """
    过滤空物品
    """
    result = []
    for item in items:
        if not item_is_empty(item):
            result.append(item)
    return result


def item_equals(item_dict, *item_name_check):
    # type: (Union[dict,None], *str) -> 'bool'
    """
    判断两个物品名称是否相等
    """
    if item_dict_is_empty(item_dict):
        return False
    item_name = item_dict.get("newItemName", "")
    return any(item_name == name for name in item_name_check)


def item_has_tag(item_name, tag_name):
    # type: (str, str) -> 'bool'
    """
    判断物品是否有某个标签
    """
    item = factory.CreateItem(item_name)
    tags = item.GetItemTags(item_name)
    return tag_name in tags


def get_item_display_name(item_name_or_dict):
    # type: (str | dict) -> 'str'
    """
    获取物品显示名称
    """
    item = factory.CreateItem("0")
    if isinstance(item_name_or_dict, dict):
        item_name = item_name_or_dict.get("newItemName", "")
        aux = item_name_or_dict.get("aux", 0)
    else:
        item_name = item_name_or_dict
        aux = 0
    info = item.GetItemBasicInfo(item_name, aux)
    return info.get("itemName", item_name_or_dict)


def fix_item_dict(item_dict_or_ast):
    # type: (dict|str) -> 'dict'
    """
    网易的物品字典在存入 BlockEntity 后再读取
    附魔字段会从 list(tuple) 变成 list(list)，这实在让人很无语

    2025-12-21：还是用 ast 存储物品吧，这样不容易出问题
    """
    # 如果是 ast 字符串，直接返回
    if isinstance(item_dict_or_ast, str) and len(item_dict_or_ast) > 0:
        return ast.literal_eval(item_dict_or_ast)

    # 其他情况，修正附魔字段
    if item_dict_is_empty(item_dict_or_ast):
        return item_dict_or_ast
    if "enchantData" in item_dict_or_ast:
        enchant_data = item_dict_or_ast["enchantData"]
        if enchant_data is not None:
            fixed_enchant_data = []
            for enchant in enchant_data:
                if isinstance(enchant, list):
                    fixed_enchant_data.append(tuple(enchant))
                else:
                    fixed_enchant_data.append(enchant)
            item_dict_or_ast["enchantData"] = fixed_enchant_data

    if "modEnchantData" in item_dict_or_ast:
        enchant_data = item_dict_or_ast["modEnchantData"]
        if enchant_data is not None:
            fixed_enchant_data = []
            for enchant in enchant_data:
                if isinstance(enchant, list):
                    fixed_enchant_data.append(tuple(enchant))
                else:
                    fixed_enchant_data.append(enchant)
            item_dict_or_ast["modEnchantData"] = fixed_enchant_data

    return item_dict_or_ast
