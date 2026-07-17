# -*- coding: utf-8 -*-

def get_face(index):
    if index == 0:
        return "down"
    elif index == 1:
        return "up"
    elif index == 2:
        return "north"
    elif index == 3:
        return "south"
    elif index == 4:
        return "west"
    elif index == 5:
        return "east"
    return None


def direction_to_aux(direction):
    if direction == "north":
        return 0
    elif direction == "east":
        return 1
    elif direction == "south":
        return 2
    elif direction == "west":
        return 3
    return 0


def aux_to_direction(aux):
    if aux == 0:
        return "north"
    elif aux == 1:
        return "east"
    elif aux == 2:
        return "south"
    elif aux == 3:
        return "west"
    return "north"


def direction_to_rot(direction):
    if direction == "north":
        return 0.0
    elif direction == "south":
        return 180.0
    elif direction == "west":
        return 270.0
    elif direction == "east":
        return 90.0
    return 0.0


def get_axis(face):
    if face in ("north", "south"):
        return "north_south"
    elif face in ("west", "east"):
        return "east_west"
    else:
        return "up_down"


def left_right_pos(pos, direction, is_left, length=1):
    """
    获取左右相对位置
    """
    x, y, z = pos
    offset = length if is_left else -length
    if direction == "north":
        return x + offset, y, z
    elif direction == "south":
        return x - offset, y, z
    elif direction == "west":
        return x, y, z - offset
    elif direction == "east":
        return x, y, z + offset
    return x, y, z


def neighbor_pos_to_direction(n_pos, direction):
    if direction == "north":
        if n_pos == (0, 0, -1):
            return "north"
        elif n_pos == (0, 0, 1):
            return "south"
        elif n_pos == (-1, 0, 0):
            return "west"
        elif n_pos == (1, 0, 0):
            return "east"
        elif n_pos == (0, 1, 0):
            return "up"
        elif n_pos == (0, -1, 0):
            return "down"
    elif direction == "south":
        if n_pos == (0, 0, 1):
            return "south"
        elif n_pos == (0, 0, -1):
            return "north"
        elif n_pos == (1, 0, 0):
            return "east"
        elif n_pos == (-1, 0, 0):
            return "west"
        elif n_pos == (0, 1, 0):
            return "up"
        elif n_pos == (0, -1, 0):
            return "down"
    elif direction == "west":
        if n_pos == (-1, 0, 0):
            return "west"
        elif n_pos == (1, 0, 0):
            return "east"
        elif n_pos == (0, 0, 1):
            return "south"
        elif n_pos == (0, 0, -1):
            return "north"
        elif n_pos == (0, 1, 0):
            return "up"
        elif n_pos == (0, -1, 0):
            return "down"
    elif direction == "east":
        if n_pos == (1, 0, 0):
            return "east"
        elif n_pos == (-1, 0, 0):
            return "west"
        elif n_pos == (0, 0, -1):
            return "north"
        elif n_pos == (0, 0, 1):
            return "south"
        elif n_pos == (0, 1, 0):
            return "up"
        elif n_pos == (0, -1, 0):
            return "down"
    return None


def neighbor_pos(pos, face):
    x, y, z = pos
    if face == "north":
        return x, y, z - 1
    elif face == "south":
        return x, y, z + 1
    elif face == "west":
        return x - 1, y, z
    elif face == "east":
        return x + 1, y, z
    elif face == "up":
        return x, y + 1, z
    elif face == "down":
        return x, y - 1, z
    return None


def opposite(face):
    if face == "north":
        return "south"
    elif face == "south":
        return "north"
    elif face == "west":
        return "east"
    elif face == "east":
        return "west"
    elif face == "up":
        return "down"
    elif face == "down":
        return "up"
    return None


def clockwise(direction):
    """
    顺时针方向
    """
    if direction == "north":
        return "east"
    elif direction == "east":
        return "south"
    elif direction == "south":
        return "west"
    elif direction == "west":
        return "north"
    return direction


def counterclockwise(direction):
    """
    逆时针方向
    """
    if direction == "north":
        return "west"
    elif direction == "west":
        return "south"
    elif direction == "south":
        return "east"
    elif direction == "east":
        return "north"
    return direction
