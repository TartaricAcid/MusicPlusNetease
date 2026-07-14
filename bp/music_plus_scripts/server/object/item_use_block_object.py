# -*- coding: utf-8 -*-

from music_plus_scripts.server.object.block_use_object import BlockUseObject


class ItemUseBlockObject(BlockUseObject):
    def __init__(self, args):
        super(ItemUseBlockObject, self).__init__(args)
        self.aux = args["blockAuxValue"]

    def cancel(self):
        self.args["ret"] = True

    def try_place_block(self, block_dict_or_name, sound_name="dig.stone"):
        # type: (str|dict, str) -> tuple|None
        """
        模拟一个原版的物品放置方块的行为
        返回的是相对坐标
        """
        # 如果当前方块是可替换的，直接替换
        if self.is_replaceable():
            pos = self.get_pos()
            self.set_block(pos, block_dict_or_name, True)
            # 扣除物品
            self.reduce_player_item(1)
            # 播放音效
            self.play_sound_and_swing_hand(sound_name)
            return 0, 0, 0

        # 否则尝试在点击的相邻方块放置
        adjacent_pos = self.get_adjacent_block_pos()
        adjacent_block = self.get_offset_block_name(adjacent_pos)
        if self.is_replaceable(adjacent_block):
            self.set_offset_block(adjacent_pos, block_dict_or_name, True)
            # 扣除物品
            self.reduce_player_item(1)
            # 播放音效
            self.play_sound_and_swing_hand(sound_name)
            return adjacent_pos

        return None

    def get_left_offset(self):
        """
        依据玩家朝向获取左侧偏移
        """
        face = self.get_player().get_direction_rot()
        if face == "south":
            left_offset = (-1, 0, 0)
        elif face == "west":
            left_offset = (0, 0, -1)
        elif face == "east":
            left_offset = (0, 0, 1)
        else:  # north up down
            left_offset = (1, 0, 0)
        return left_offset

    def try_place_1x2_block(self, block_dict_or_name, face, sound_name="dig.stone"):
        # type: (str|dict, str, str) -> tuple|None
        """
        模拟一个原版的物品放置双格方块的行为
        返回的是相对坐标（左下角）
        """

        # 如果当前方块是可替换的，直接替换
        if self.is_replaceable():
            # 检查左侧是否也是可替换的
            left_offset = self.get_left_offset()
            left_block = self.get_offset_block_name(left_offset)
            if not self.is_replaceable(left_block):
                self.get_player().send_tip_msg("无法放置，左侧方块空间不足")
                return None

            self.set_block(self.get_pos(), block_dict_or_name)
            self.set_offset_block(left_offset, block_dict_or_name)

            # 扣除物品
            self.reduce_player_item(1)
            # 播放音效
            self.play_sound_and_swing_hand(sound_name)
            return left_offset, (0, 0, 0)

        # 否则尝试在点击的相邻方块放置
        adjacent_pos = self.get_adjacent_block_pos()
        adjacent_block = self.get_offset_block_name(adjacent_pos)
        if self.is_replaceable(adjacent_block):
            # 检查左侧是否也是可替换的
            left_offset = self.get_left_offset()
            left_adjacent_pos = (
                adjacent_pos[0] + left_offset[0],
                adjacent_pos[1] + left_offset[1],
                adjacent_pos[2] + left_offset[2],
            )
            left_block = self.get_offset_block_name(left_adjacent_pos)
            if not self.is_replaceable(left_block):
                self.get_player().send_tip_msg("无法放置，左侧方块空间不足")
                return None

            self.set_offset_block(adjacent_pos, block_dict_or_name)
            self.set_offset_block(left_adjacent_pos, block_dict_or_name)

            # 扣除物品
            self.reduce_player_item(1)
            # 播放音效
            self.play_sound_and_swing_hand(sound_name)
            return left_adjacent_pos, adjacent_pos

        return None
