# -*- coding: utf-8 -*-

"""
由于网易的设计过度封装且面向过程，导致方块交互相关的参数获取异常复杂。
本模块用于简化方块交互相关参数的传递。
"""

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.utils.block_utils import be_data_fix
from music_plus_scripts.server.utils.item_utils import item_dict_is_empty

if 0 > 1:
    from typing import *


class BlockObject(object):
    def __init__(self, args):
        self.mod_system = System
        self.args = args

        self.x = args.get("x", args.get("posX", 0))
        self.y = args.get("y", args.get("posY", 0))
        self.z = args.get("z", args.get("posZ", 0))
        self.dimension = args.get("dimension", args.get("dimensionId", 0))
        self.aux = args.get("aux", 0)

        self.level_id = levelId
        self.factory = serverApi.GetEngineCompFactory()
        self.block_info = self.factory.CreateBlockInfo(self.level_id)
        self.be_comp = self.factory.CreateBlockEntityData(self.level_id)
        self.state_comp = self.factory.CreateBlockState(self.level_id)

    def get_pos(self):
        # type: () -> (int, int, int)
        return self.x, self.y, self.z

    def offset_pos(self, dx, dy, dz):
        # type: (float, float, float) -> (float, float, float)
        return self.x + dx, self.y + dy, self.z + dz

    def get_dimension(self):
        # type: () -> int
        return self.dimension

    def set_to_air(self, handing_type=0, update_neighbors=False):
        # type: (int, bool) -> bool
        """
        将方块设置为空气
        :param handing_type: 0：替换，1：销毁，2：保留
        :param update_neighbors: 是否给相邻的方块触发方块更新
        :return: 方块是否发生了改变，是则返回 True，否则返回 False
        """
        air = {"name": "minecraft:air"}
        return self.block_info.SetBlockNew(
            self.get_pos(), air, handing_type, self.get_dimension(), False, update_neighbors
        )

    def set_to_air_and_drop(self, update_neighbors=False):
        # type: (bool) -> bool
        """
        将方块设置为空气并掉落物品
        :return: 方块是否发生了改变，是则返回 True，否则返回 False
        """
        return self.set_to_air(1, update_neighbors)

    def get_offset_block(self, offset=(0, 0, 0)):
        # type: ((int, int, int)) -> dict
        x, y, z = self.get_pos()
        dx, dy, dz = offset
        block = self.block_info.GetBlockNew((x + dx, y + dy, z + dz), self.get_dimension())
        if block is None:
            return {}
        return block

    def get_offset_block_name(self, offset=(0, 0, 0)):
        # type: ((int, int, int)) -> str
        block = self.get_offset_block(offset)
        return block.get("name", "")

    def get_offset_block_state(self, offset=(0, 0, 0)):
        # type: ((int, int, int)) -> dict
        x, y, z = self.get_pos()
        dx, dy, dz = offset
        block_state = self.state_comp.GetBlockStates((x + dx, y + dy, z + dz), self.get_dimension())
        if block_state is None:
            return {}
        return block_state

    def get_block_entity_data(self):
        # type: () -> dict
        be_data = self.be_comp.GetBlockEntityData(self.get_dimension(), self.get_pos())
        if be_data is None:
            return {}
        return be_data

    def get_offset_block_entity_data(self, offset=(0, 0, 0)):
        # type: ((int, int, int)) -> dict
        x, y, z = self.get_pos()
        dx, dy, dz = offset
        be_data = self.be_comp.GetBlockEntityData(self.get_dimension(), (x + dx, y + dy, z + dz))
        if be_data is None:
            return {}
        return be_data

    def set_block_entity_data(self, be_data):
        # type: (dict) -> None
        self.block_info.SetBlockEntityData(self.get_dimension(), self.get_pos(), be_data_fix(be_data))

    def set_offset_block_entity_data(self, offset, be_data):
        # type: ((int, int, int), dict) -> None
        x, y, z = self.get_pos()
        dx, dy, dz = offset
        self.block_info.SetBlockEntityData(
            self.get_dimension(), (x + dx, y + dy, z + dz),
            be_data_fix(be_data)
        )

    def get_block_state(self):
        # type: () -> dict
        block_state = self.state_comp.GetBlockStates(self.get_pos(), self.get_dimension())
        if block_state is None:
            return {}
        return block_state

    def set_block(self, pos, block_dict_or_name, update_neighbors=False, old_block_handling=0):
        # type: (Tuple[int,int,int], Union[dict,str], bool,int) -> bool
        if isinstance(block_dict_or_name, str):
            block_dict_or_name = {'name': block_dict_or_name}
        return self.block_info.SetBlockNew(pos, block_dict_or_name, old_block_handling, self.get_dimension(), False,
                                           update_neighbors)

    def set_offset_block(self, pos, offset_dict_or_name, update_neighbors=False, old_block_handling=0):
        # type: (Tuple[int,int,int], Union[dict,str], bool, int) -> bool
        if isinstance(offset_dict_or_name, str):
            offset_dict_or_name = {'name': offset_dict_or_name}
        return self.block_info.SetBlockNew(
            (self.x + pos[0], self.y + pos[1], self.z + pos[2]),
            offset_dict_or_name, old_block_handling, self.get_dimension(),
            False, update_neighbors
        )

    def set_waterlogged(self, pos):
        # type: (Tuple[int,int,int]) -> bool
        x, y, z = pos
        dim_id = self.get_dimension()
        game = self.factory.CreateGame(self.level_id)
        # 延迟，避免方块还未更新完成
        game.AddTimer(0.1, BlockObject._set_waterlogged, x, y, z, dim_id)
        return True

    def set_block_state(self, block_state):
        # type: (dict) -> None
        self.state_comp.SetBlockStates(self.get_pos(), block_state, self.get_dimension())

    def set_offset_block_state(self, offset, block_state):
        # type: ((int, int, int), dict) -> None
        x, y, z = self.get_pos()
        dx, dy, dz = offset
        self.state_comp.SetBlockStates((x + dx, y + dy, z + dz), block_state, self.get_dimension())

    def get_block_collision(self, pos=None):
        # type: (Tuple[int,int,int] | None) -> Union[Dict[str, Tuple[int, int, int]], Any]
        if pos is None:
            pos = self.get_pos()
        aabb = self.block_info.GetBlockCollision(pos, self.get_dimension())
        if aabb is None or "min" not in aabb or "max" not in aabb:
            return {
                "min": (0, 0, 0),
                "max": (1, 1, 1)
            }
        return aabb

    def remove_entity(self, entity_id):
        # type: (str) -> None
        self.mod_system.DestroyEntity(entity_id)

    def get_entities_in_aabb(self, filter_type=None, min_pos=(0, 0, 0), max_pos=(1, 1, 1), start_pos=None):
        # type: ((list|str), (float, float, float), (float, float, float), (float, float, float)) -> list[str]
        game = self.factory.CreateGame(self.level_id)
        if start_pos is None:
            x, y, z = self.get_pos()
        else:
            x, y, z = start_pos
        min_x, min_y, min_z = min_pos
        max_x, max_y, max_z = max_pos
        dim_id = self.get_dimension()
        entities = game.GetEntitiesInSquareArea(
            None, (x + min_x, y + min_y, z + min_z),
            (x + max_x, y + max_y, z + max_z), dim_id
        )

        if filter_type is None:
            return entities

        if isinstance(filter_type, str):
            filter_type = [filter_type]
        elif len(filter_type) <= 0:
            return entities

        filtered_entities = []
        for entity_id in entities:
            entity_type = self.factory.CreateEngineType(entity_id).GetEngineTypeStr()
            if entity_type in filter_type:
                filtered_entities.append(entity_id)
        return filtered_entities

    def drop_items(self, *item_list):
        # type: (Union[dict,str]) -> None
        for item in item_list:
            if isinstance(item, str):
                item = {"newItemName": item, "count": 1}
            if item_dict_is_empty(item):
                continue
            self.mod_system.CreateEngineItemEntity(item, self.get_dimension(), self.offset_pos(0.5, 0.5, 0.5))

    def delayed_execute(self, delay_time, func, *args, **kwargs):
        # type: (float, Callable, Any, Any) -> None
        game = self.factory.CreateGame(self.level_id)
        game.AddTimer(delay_time, func, args, kwargs)

    def send_simple_particle(self, name, pos):
        # type: (str,(float, float, float)) -> None
        x, y, z = pos
        command = self.factory.CreateCommand(self.level_id)
        command.SetCommand("/particle {} {} {} {}".format(name, x, y, z))

    def spawn_resources(self, block_name, pos, aux=0, probability=1.0, bonus_loot_level=0,
                        allow_randomness=True, spawn_orb=False):
        self.block_info.SpawnResources(block_name, pos, aux, probability, bonus_loot_level,
                                       self.dimension, allow_randomness, spawn_orb)

    @staticmethod
    def _set_waterlogged(x, y, z, dim_id):
        # type: (int, int, int, int) -> None
        water = {
            'name': 'minecraft:water'
        }
        level_id = serverApi.GetLevelId()
        block_info = serverApi.GetEngineCompFactory().CreateBlockInfo(level_id)
        block_info.SetLiquidBlock((x, y, z), water, dim_id)
