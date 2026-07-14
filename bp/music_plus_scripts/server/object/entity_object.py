# -*- coding: utf-8 -*-

from ktavern_scripts.QuModLibs.Server import *

from ktavern_scripts.server.utils.item_utils import copy_with_count

if 0 > 1:
    from typing import *


class EntityObject(object):
    def __init__(self, entity_id):
        self.mod_system = System
        self.factory = serverApi.GetEngineCompFactory()
        self.entity_id = entity_id

        self.effect_comp = self.factory.CreateEffect(entity_id)
        self.item_comp = self.factory.CreateItem(entity_id)
        self.attr = self.factory.CreateAttr(entity_id)

        self.inventory_slot = 0
        self.offhand_slot = 1
        self.mainhand_slot = 2
        self.armor_slot = 3
        self.head_slot = 0
        self.body_slot = 1
        self.leg_slot = 2
        self.foot_slot = 3

    def get_pos(self):
        # type: () -> tuple[float, float, float]
        pos_comp = self.factory.CreatePos(self.entity_id)
        return pos_comp.GetPos()

    def get_foot_pos(self):
        # type: () -> tuple[float, float, float]
        pos_comp = self.factory.CreatePos(self.entity_id)
        return pos_comp.GetFootPos()

    def get_offset_pos(self, offset):
        # type: (tuple[float, float, float]) -> tuple[float, float, float]
        pos_comp = self.factory.CreatePos(self.entity_id)
        pos = pos_comp.GetPos()
        return pos[0] + offset[0], pos[1] + offset[1], pos[2] + offset[2]

    def get_dimension(self):
        # type: () -> int
        dim_comp = self.factory.CreateDimension(self.entity_id)
        return dim_comp.GetEntityDimensionId()

    def get_rot(self):
        # type: () -> tuple[float, float]
        rot_comp = self.factory.CreateRot(self.entity_id)
        return rot_comp.GetRot()

    def get_direction_rot(self):
        # type: () -> str
        rot = self.get_rot()
        yaw = rot[1] % 360
        if 45 <= yaw < 135:
            return "east"
        elif 135 <= yaw < 225:
            return "south"
        elif 225 <= yaw < 315:
            return "west"
        else:
            return "north"

    def get_opposite_direction_rot(self):
        # type: () -> str
        """
        获取与实体朝向相反的方向字符串
        """
        direction = self.get_direction_rot()
        if direction == "north":
            return "south"
        elif direction == "south":
            return "north"
        elif direction == "west":
            return "east"
        else:
            return "west"

    def get_relative_rot(self):
        # type: () -> tuple[float, float]
        rot = self.get_rot()
        return rot[0], (rot[1] - 180) % 360

    def has_effect(self, effect_name):
        # type: (str) -> bool
        return self.effect_comp.HasEffect(effect_name)

    def add_effect(self, effect_name, duration, amplifier=0, show_particles=True):
        # type: (str, int, int, bool) -> bool
        return self.effect_comp.AddEffectToEntity(effect_name, duration, amplifier, show_particles)

    def remove_effect(self, effect_name):
        # type: (str) -> bool
        return self.effect_comp.RemoveEffectFromEntity(effect_name)

    def get_mainhand_item(self):
        # type: () -> dict
        return self.item_comp.GetEntityItem(self.mainhand_slot, 0, True)

    def get_offhand_item(self):
        # type: () -> dict
        return self.item_comp.GetEntityItem(self.offhand_slot, 0, True)

    def get_head_item(self):
        # type: () -> dict
        return self.item_comp.GetEntityItem(self.armor_slot, self.head_slot, True)

    def get_body_item(self):
        # type: () -> dict
        return self.item_comp.GetEntityItem(self.armor_slot, self.body_slot, True)

    def get_leg_item(self):
        # type: () -> dict
        return self.item_comp.GetEntityItem(self.armor_slot, self.leg_slot, True)

    def get_foot_item(self):
        # type: () -> dict
        return self.item_comp.GetEntityItem(self.armor_slot, self.foot_slot, True)

    def set_mainhand_item(self, item_dict_or_name):
        # type: (dict) -> bool
        item_dict = self._handle_item(item_dict_or_name)
        return self.item_comp.SetEntityItem(self.mainhand_slot, item_dict)

    def set_offhand_item(self, item_dict_or_name):
        # type: (dict) -> bool
        item_dict = self._handle_item(item_dict_or_name)
        return self.item_comp.SetEntityItem(self.offhand_slot, item_dict)

    def set_head_item(self, item_dict_or_name):
        # type: (dict) -> bool
        item_dict = self._handle_item(item_dict_or_name)
        return self.item_comp.SetEntityItem(self.armor_slot, item_dict, self.head_slot)

    def set_body_item(self, item_dict_or_name):
        # type: (dict) -> bool
        item_dict = self._handle_item(item_dict_or_name)
        return self.item_comp.SetEntityItem(self.armor_slot, item_dict, self.body_slot)

    def set_leg_item(self, item_dict_or_name):
        # type: (dict) -> bool
        item_dict = self._handle_item(item_dict_or_name)
        return self.item_comp.SetEntityItem(self.armor_slot, item_dict, self.leg_slot)

    def set_foot_item(self, item_dict_or_name):
        # type: (dict) -> bool
        item_dict = self._handle_item(item_dict_or_name)
        return self.item_comp.SetEntityItem(self.armor_slot, item_dict, self.foot_slot)

    def drop_item(self, item_dict_or_name, position=None):
        # type: (Union[dict,str], tuple[float,float,float]|None) -> Union[str,None]
        item_dict = self._handle_item(item_dict_or_name)
        if position is None:
            position = self.get_offset_pos((0, 1, 0))
        dimension_id = self.get_dimension()
        return self.mod_system.CreateEngineItemEntity(item_dict, dimension_id, position)

    def set_attr(self, attr_type, value, set_default=1):
        # type: (int, float, int) -> bool
        return self.attr.SetAttrValue(attr_type, value, set_default)

    def set_mod_attr(self, param_name, param_value, need_restore=False, auto_save=True):
        # type: (str, any, bool, bool) -> None
        mod_attr = self.factory.CreateModAttr(self.entity_id)
        mod_attr.SetAttr(param_name, param_value, need_restore, auto_save)

    def get_attr(self, param_name):
        # type: (int) -> float
        return self.attr.GetAttrValue(param_name)

    def reset_attr(self, attr_type):
        # type: (int) -> bool
        return self.attr.ResetToDefaultValue(attr_type)

    def get_mod_attr(self, param_name, default_value=None):
        # type: (str, any) -> any
        mod_attr = self.factory.CreateModAttr(self.entity_id)
        return mod_attr.GetAttr(param_name, default_value)

    def destroy(self):
        # type: () -> bool
        return self.mod_system.DestroyEntity(self.entity_id)

    @staticmethod
    def _handle_item(item_dict_or_name, count=1):
        # type: (Union[dict,str], int) -> dict
        if isinstance(item_dict_or_name, str):
            return {
                "newItemName": item_dict_or_name,
                "count": count
            }
        else:
            count = max(item_dict_or_name.get("count", 1), 1)
            return copy_with_count(item_dict_or_name, count)
