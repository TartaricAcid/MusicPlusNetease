# -*- coding: utf-8 -*-
from ktavern_scripts.QuModLibs.Server import *
from ktavern_scripts.server.object.entity_object import EntityObject
from ktavern_scripts.server.utils.item_utils import give_player_item_dict, copy_with_count, reduce_carried_item_num
from ktavern_scripts.server.utils.sound_utils import get_sound_msg

if 0 > 1:
    pass


class PlayerObject(EntityObject):
    def __new__(cls, player_id):
        """非玩家不创建实例"""
        if serverApi.GetEngineCompFactory().CreateEngineType(player_id).GetEngineTypeStr() != "minecraft:player":
            return None
        return object.__new__(cls, player_id)

    def __init__(self, player_id):
        super(PlayerObject, self).__init__(player_id)
        self.player_comp = self.factory.CreatePlayer(player_id)
        self.item_comp = self.factory.CreateItem(self.entity_id)

    def get_hunger(self):
        # type: () -> float
        return self.player_comp.GetPlayerHunger()

    def set_hunger(self, hunger):
        # type: (int) -> bool
        hunger = min(hunger, 20)
        return self.player_comp.SetPlayerHunger(hunger)

    def send_tip_msg(self, msg):
        game = self.factory.CreateGame(self.entity_id)
        return game.SetOneTipMessage(self.entity_id, msg)

    def give_item(self, item_dict_or_name, item_count=1):
        # type: (Union[dict, str], int) -> None
        if isinstance(item_dict_or_name, str):
            item_dict_or_name = {"newItemName": item_dict_or_name, "count": item_count}
        elif isinstance(item_dict_or_name, dict):
            item_dict_or_name = copy_with_count(item_dict_or_name, item_count)
        give_player_item_dict(self.entity_id, item_dict_or_name)

    def reduce_carried_item(self, item_count):
        # type: (int) -> bool
        return reduce_carried_item_num(self.entity_id, item_count)

    def send_msg(self, event_name, event_data=None):
        if event_data is None:
            event_data = self.get_msg_data()
        Call("*", event_name, event_data)

    def get_msg_data(self, pos=None):
        msg_data = {"player_id": self.entity_id}
        if pos is not None:
            msg_data["pos"] = pos
        else:
            msg_data["pos"] = self.get_pos()
        return msg_data

    def swing_hand(self):
        msg_data = {"player_id": self.entity_id}
        self.send_msg("swing_hand", msg_data)

    def play_sound_and_swing_hand(self, sound_name, pos=None, volume=1.0, pitch=1.0):
        msg_data = self.get_msg_data(pos)
        msg_data["sound"] = get_sound_msg(sound_name, volume, pitch)
        self.send_msg("play_sound_and_swing_hand", msg_data)

    def play_sound(self, sound_name, pos=None, volume=1.0, pitch=1.0):
        msg_data = self.get_msg_data(pos)
        msg_data["sound"] = get_sound_msg(sound_name, volume, pitch)
        self.send_msg("play_sound", msg_data)

    def is_in_water(self):
        """
        这个方法是因为网易没有在服务端提供对应的方法，不得已而为之，效率较低，不建议频繁调用。
        """
        comp = self.factory.CreateQueryVariable(self.entity_id)
        result = comp.EvalMolangExpression('query.is_in_water')
        return result["value"] == 1.0

    def is_sneaking(self):
        return self.player_comp.isSneaking()

    def inv_items(self):
        # type: () -> list[dict]
        # 0 表示玩家背包物品栏
        return self.item_comp.GetPlayerAllItems(0)

    def set_inv_item(self, index, count):
        # type: (int, int) -> bool
        return self.item_comp.SetInvItemNum(index, count)
