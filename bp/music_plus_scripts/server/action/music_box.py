# -*- coding: utf-8 -*-

"""音乐盒交互逻辑

处理纸带右击音乐盒的业务逻辑：
- 判定物品/方块是否属于本模块管辖
- 从纸带中提取 ABC 乐谱并发送到客户端播放
"""

from music_plus_scripts.QuModLibs.Server import *

PAPER_TAPE_ITEM = "music_plus:paper_tape"
MUSIC_BOX_BLOCK = "music_plus:music_plus_music_box"
MUSIC_BOX_SOUND_PREFIX = "music_plus.music_box"

# 内嵌的默认测试曲目（纸带无自定义数据时使用）
DEFAULT_ABC = r'''
X: 1
T: Daisy Bell
C: Harry Dacre
R: waltz
M: 3/4
L: 1/8
K: G
"Intro"\
| "G"[d2d'2] [^c2^c'2] [d2d'2] | [B2b2] [A2a2] [G2g2] | "D7"[A4a4] f2 | d4 d'2 \
| "G"bd ef ga | ^ab e'd' bg | "D7"[a4c4] [d2c2] | [g4B4] z2 |]
"Verse"\
[| "G"d2 ^c2 d2 | B2 A2 G2 | "D7"A4 F2 | D4 z2 "D7"A6 | D6 | "G"d6 | B4 z2 |
w: There is a flow-er with-in my heart, Dai-sy, Dai-sy.
| "G"d2 ^c2 d2 | B2 A2 G2 | "D7"A4 F2 | D4 z2 | "G"G2 d2 G2 | "D7"F2 D2 A2 | "G"G6- | G2 z4 |
w: Plant-ed one day by a glanc-ing dart, plant-ed by Dai_sy Bell.
| "Em"B2 c2 B2 | "B7"A2 G2 F2 | "Em"B4 G2 | E4 z2 | "D7"d2 c2 B2 | A4 ^A2 | "G"B6- | B2 z4 |
w: Whe-ther she loves me or loves me not, some-times it's hard to tell.
| "Em"B2 c2 B2 | "B7"A2 G2 F2 | "Em"B4 G2 | E4 B2 | "A7"A2 e2 ^c2 | B4 A2 | "D7"d6- | d2 z4 |]
w: Yet I am long-ing to share the lot of beau-ti-ful Dai-sy Bell.
"Chorus"\
[| "G"d6 | B6 | G6 | D6 | "C"E2 F2 G2 | E4 G2 | "G"D6- | D2 z2 |
w: Dai-sy, Dai-sy, give me your an-swer, do.
| "D7"A6 d6 | "G"B6 G6 | "A7"E2 F2 G2 | A4 B2 | "D"A6- | A2 z2 B2 |
w: I'm half cra-zy, all for the love of you.* It
| "D7"c2 B2 A2 | d4 B2 | "G"A2 G4- | G2 z2 A2 | "Em"B4 G2 | "C"E4 G2 | "G"E2 D4- | D2 z2 D2 |
w: won't be a styl-ish mar-riage,* I can't af-ford a car-riage,* But
| "G"G4 B2 | "D7"A2 z4 | "G"G4 B2 | "D7"A2 z2 Bc | "G"d2 B2 G2 | "D7"A4 D2 | "G"G6- | G2 z4 |]
w: you'll look sweet on the seat of a bi-cy-cle built for two.
'''


def is_paper_tape(item_name):
    """判断物品是否为纸带。"""
    return item_name == PAPER_TAPE_ITEM


def is_music_box(block_name):
    """判断方块是否为音乐盒。"""
    return block_name == MUSIC_BOX_BLOCK


def handle_music_box_play(args):
    """处理纸带右击音乐盒：提取 ABC 乐谱并发送到客户端播放。"""
    player_id = args["entityId"]
    item = args.get("itemDict") or {}
    abc_text = _get_abc_from_tape(item)

    pos = (args["x"] + 0.5, args["y"] + 1.0, args["z"] + 0.5)
    Call(player_id, "play_music_box", {
        "abc": abc_text,
        "pos": pos,
        "sound_prefix": MUSIC_BOX_SOUND_PREFIX,
    })


def _get_abc_from_tape(item_dict):
    """从纸带物品的 userData 中提取 ABC 文本。

    如果纸带没有写入自定义数据，返回内嵌的默认测试曲目。
    """
    custom_data = item_dict.get("userData") or {}
    abc = custom_data.get("abc", "")
    if abc:
        return abc
    return DEFAULT_ABC
