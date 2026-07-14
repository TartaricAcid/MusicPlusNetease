# -*- coding: utf-8 -*-

import copy

from music_plus_scripts.QuModLibs.Server import *
from music_plus_scripts.server.utils.item_utils import item_dict_is_empty, item_has_tag


class ItemObject(object):
    def __init__(self, item_dict):
        self.mod_system = System
        self.item_dict = item_dict

    def get_item_dict(self):
        return self.item_dict

    def is_empty(self):
        # type: () -> bool
        return item_dict_is_empty(self.item_dict)

    def same_name(self, check_item_name):
        # type: (str) -> bool
        item_name = self.item_name()
        return item_name == check_item_name

    def item_name(self):
        # type: () -> str
        return self.item_dict.get("newItemName")

    def has_tag(self, tag_name):
        # type: (str) -> bool
        item_name = self.item_name()
        return item_has_tag(item_name, tag_name)

    def count(self):
        # type: () -> int
        return self.item_dict.get("count", 0)

    def aux(self):
        # type: () -> int
        return self.item_dict.get("newAuxValue", 0)

    def durability(self):
        # type: () -> int
        return self.item_dict.get("durability", 0)

    def copy(self):
        # type: () -> dict
        return copy.deepcopy(self.item_dict)

    def copy_with_count(self, count):
        # type: (int) -> dict
        item_copy = copy.deepcopy(self.item_dict)
        item_copy["count"] = max(0, count)
        return item_copy

    def shrink(self, amount):
        # type: (int) -> dict
        item_copy = copy.deepcopy(self.item_dict)
        item_copy["count"] = max(0, self.count() - amount)
        return item_copy

    def get_user_data(self, key=None):
        # type: (str) -> dict|None
        user_data = self.item_dict.get("userData")
        if key is not None:
            return user_data.get(key)
        return user_data
