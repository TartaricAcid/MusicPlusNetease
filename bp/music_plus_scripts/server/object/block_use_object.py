# -*- coding: utf-8 -*-

"""
由于网易的设计过度封装且面向过程，导致方块交互相关的参数获取异常复杂。
本模块用于简化方块交互相关参数的传递。
"""
from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.object.block_object import BlockObject
from music_plus_scripts.server.object.item_object import ItemObject
from music_plus_scripts.server.object.player_object import PlayerObject
from music_plus_scripts.server.utils.item_utils import give_player_item_dict, copy_with_count, reduce_carried_item_num, \
    consume_mainhand_durability
from music_plus_scripts.server.utils.sound_utils import get_sound_msg
from music_plus_scripts.utils.blocks import REPLACEABLE, FACE_OFFSETS

if 0 > 1:
    from typing import *


class BlockUseObject(BlockObject):
    def __init__(self, args):
        super(BlockUseObject, self).__init__(args)

        self.player_id = args.get("playerId")
        if self.player_id is None:
            self.player_id = args["entityId"]

        self.item = ItemObject(args["itemDict"])
        self.player = PlayerObject(self.player_id)

        self.block_name = args["blockName"]
        self.aux = args.get("aux")
        self.face = args["face"]
        self.click_x = args["clickX"]
        self.click_y = args["clickY"]
        self.click_z = args["clickZ"]

    def get_player_id(self):
        # type: () -> str
        return self.player_id

    def get_player(self):
        return self.player

    def get_block_name(self):
        # type: () -> str
        return self.block_name

    def get_item(self):
        # type: () -> ItemObject
        return self.item

    def cancel(self):
        self.args["cancel"] = True

    def give_player_item(self, item_dict_or_name, item_count=1):
        # type: (Union[dict, str], int) -> None
        if isinstance(item_dict_or_name, str):
            item_dict_or_name = {"newItemName": item_dict_or_name, "count": item_count}
        elif isinstance(item_dict_or_name, dict):
            item_dict_or_name = copy_with_count(item_dict_or_name, item_count)
        give_player_item_dict(self.player_id, item_dict_or_name)

    def reduce_player_item(self, item_count):
        # type: (int) -> bool
        return reduce_carried_item_num(self.player_id, item_count)

    def consume_player_item_durability(self, cost=1):
        game = self.factory.CreateGame(self.player_id)
        game.AddTimer(0.2, consume_mainhand_durability, self.player_id, cost)

    def get_msg_data(self):
        return {
            "player_id": self.get_player_id(),
            "pos": self.get_pos(),
        }

    def send_msg(self, event_name, event_data=None):
        if event_data is None:
            event_data = self.get_msg_data()
        Call("*", event_name, event_data)

    def swing_hand(self):
        msg_data = {"player_id": self.get_player_id()}
        self.send_msg("swing_hand", msg_data)

    def play_sound_and_swing_hand(self, sound_name, volume=1.0, pitch=1.0):
        msg_data = self.get_msg_data()
        msg_data["sound"] = get_sound_msg(sound_name, volume, pitch)
        self.send_msg("play_sound_and_swing_hand", msg_data)

    def create_entity(self, entity_type, pos, rot, is_npc=False, is_global=False):
        # type: (str, tuple, tuple, bool, bool) -> str
        return self.mod_system.CreateEngineEntityByTypeStr(
            entity_type, pos, rot, self.get_dimension(), is_npc, is_global
        )

    def is_click_up(self):
        # type: () -> bool
        return self.face == 1

    def is_click_down(self):
        # type: () -> bool
        return self.face == 0

    def is_replaceable(self, input_block_name=None):
        # type: (str | None) -> bool
        """
        判断当前方块是否可被替换
        """
        if input_block_name is not None:
            return input_block_name in REPLACEABLE
        return self.block_name in REPLACEABLE

    def get_adjacent_block_pos(self):
        # type: () -> Tuple[int, int, int]
        """
        根据点击面获取相邻方块坐标
        用于判断方块放置位置
        """
        return FACE_OFFSETS.get(self.face, (0, 0, 0))
