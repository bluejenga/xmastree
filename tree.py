#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import itertools
import sys

# Direction
DIR_N = 0  # North
DIR_E = 1  # East
DIR_S = 2  # South
DIR_W = 3  # West
DIR_NUM = 4
# 隣のセルへの座標の差分
DELTA = [(0, -1), (1, 0), (0, 1), (-1, 0)]


class Cell:
    """Treeを構成するCellのクラス"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # 迷路の一部に割り当てられたかどうか
        self.used = False
        # 隣接するセルと接続している方角
        self.linked_dir = [False, False, False, False]  # [N, E, S, W]
        self.light = False

    def rotate(self, n):
        """セルを時計回りに90*n度回転する"""
        self.linked_dir = self.linked_dir[-n:] + self.linked_dir[:-n]

    def get_linked_dir_str(self):
        """接続している方角を文字で取得する"""
        s = ''
        if self.linked_dir[DIR_N]:
            s += 'N'
        if self.linked_dir[DIR_E]:
            s += 'E'
        if self.linked_dir[DIR_S]:
            s += 'S'
        if self.linked_dir[DIR_W]:
            s += 'W'
        return s


class Tree:
    """
    木を表すクラス。
    長方形に並んだCellで構成される。
    不要な領域にはCellの代わりにNoneを割り当てて、木の形を表現する。
    CellとCellの接続が迷路の通路を表す。
    """
    def __init__(self, height):
        self.height = height
        # widthはheightから算出する。
        width = height * 2 - 3 if height > 1 else 1
        self.width = width

        self.cells = [None] * (width * height)
        for y, x in itertools.product(range(height), range(width)):
            if self.is_valid_coord(x, y):
                self.cells[x + y * width] = (Cell(x, y))
        # 有効なセルの数
        self.cellnum = height * height - 2 * height + 2
        # 点灯しているセルの数
        self.lightcellnum = 0

        # 根元、幹のCell
        center = self.height - 2 if self.height > 1 else 0
        self.root = self.cells[center + (height - 1) * width]

    def is_valid_coord(self, x, y):
        """
        指定した座標が有効かどうかを返す。
        """

        # 長方形の範囲に収まるかどうか
        if x < 0 or x >= self.width:
            return False
        if y < 0 or y >= self.height:
            return False

        # 木の形の範囲に収まるかどうか
        center = self.height - 2 if self.height > 1 else 0
        if x + y < center:
            return False
        if x - y > center:
            return False
        if x != center and y == self.height - 1:
            return False

        return True

    def get_next_cell(self, cell, direction):
        """指定した方角の隣接するセルを取得する"""
        dx, dy = DELTA[direction]
        x, y = cell.x + dx, cell.y + dy
        if self.is_valid_coord(x, y):
            return self.cells[x + y * self.width]
        return None

    def get_available_links_from(self, src):
        """srcセルを起点とする使用可能な接続（通路）を列挙する"""
        links = []
        for direction in range(DIR_NUM):
            dst = self.get_next_cell(src, direction)
            if dst is not None and not dst.used:
                links.append((src, direction, dst))
        return links

    def build(self):
        """迷路を構築する"""

        # 初期化
        for cell in self.cells:
            if cell is not None:
                cell.used = False
                cell.linked_dir = [False, False, False, False]
                cell.light = False
        self.lightcellnum = 0

        # 木の根元から迷路作成開始（実際にはどこからでもよい）
        self.root.used = True
        links = self.get_available_links_from(self.root)

        # 通路候補がなくなるまで繰り返し
        while len(links) > 0:

            # 候補から通路を一つ選択
            src, direction, dst = random.choice(links)
            dst.used = True
            src.linked_dir[direction] = True
            dst.linked_dir[(direction + 2) % 4] = True

            # 既存候補の中から、dstが重複しているものを削除
            links = [ln for ln in links if ln[2] != dst]
            # dstを起点とした通路を候補に追加
            links.extend(self.get_available_links_from(dst))

    def shuffle(self):
        """各セルの向きをシャッフルする"""
        for cell in self.cells:
            if cell is not None and cell is not self.root:
                n = random.choice(range(DIR_NUM))
                cell.rotate(n)

    def rotate(self, x, y):
        """指定した座標のセルを時計回りに90度回転する"""
        if self.is_valid_coord(x, y):
            cell = self.cells[x + y * self.width]
            cell.rotate(1)

    def lightup(self):
        """根元から辿って、繋がっているセルを点灯する"""
        # 一旦すべて消灯
        self.lightcellnum = 0
        for cell in self.cells:
            if cell is not None:
                cell.light = False

        self._lightup_recursive(self.root)

    def _lightup_recursive(self, cell):
        """lightup()の内部で再帰的に呼び出す関数"""
        # まずは点灯
        cell.light = True
        self.lightcellnum = self.lightcellnum + 1

        # 通路が伸びている方角を取得
        dirs = [d for d, ln in enumerate(cell.linked_dir) if ln]
        # その方角のセルを取得
        lncells = [self.get_next_cell(cell, d) for d in dirs]
        # そのセルからも自分の方に通路が伸びていれば、再帰的に点灯処理
        for d, lncell in zip(dirs, lncells):
            if (lncell is not None
                    and lncell.linked_dir[(d + 2) % 4]
                    and not lncell.light):
                self._lightup_recursive(lncell)

    def is_complete(self):
        """すべてのセルが点灯していればTrueを返す"""
        return self.cellnum == self.lightcellnum

    def get_cell_list(self):
        return [c for c in self.cells if c is not None]


def print_tree(tree):
    """コンソールに木の絵を出力"""

    def getString(cell):
        if cell is None:
            return ['     '] * 3

        n = '   ' if cell.linked_dir[DIR_N] else '---'
        s = '   ' if cell.linked_dir[DIR_S] else '---'
        w = ' ' if cell.linked_dir[DIR_W] else '|'
        e = ' ' if cell.linked_dir[DIR_E] else '|'
        L = 'X' if cell.light else ' '
        return [f'+{n}+', f'{w} {L} {e}', f'+{s}+']

    print('  ', end='')
    for x in range(tree.width):
        print(f'  {x}  ', end='')
    print('')

    cellstr = [getString(cell) for cell in tree.cells]
    for y in range(tree.height):
        for i in range(3):
            if i == 1:
                print(y, '', end='')
            else:
                print('  ', end='')

            for x in range(tree.width):
                print(cellstr[x + y * tree.width][i], end='')
            print()


if __name__ == '__main__':
    """引数に木の高さを指定する"""
    if len(sys.argv) != 2:
        print('usage: tree.py <height>')
        exit()

    tree = Tree(int(sys.argv[1]))
    tree.build()
    tree.shuffle()
    tree.lightup()

    print('Enter Commands.')
    print('    X Y  Rotate cell')
    print('    n    Start new game')
    print('    e    Exit')
    print('')
    print_tree(tree)

    while True:
        print('>>>', end='')
        str = input()

        if str == 'e':
            break
        elif str == 'n':
            tree.build()
            tree.shuffle()
        else:
            coord = str.split()
            if (len(coord) != 2
                    or not coord[0].isdecimal
                    or not coord[1].isdecimal):
                continue
            x, y = (int(s) for s in coord)
            if not tree.is_valid_coord(x, y):
                continue
            tree.rotate(int(coord[0]), int(coord[1]))

        tree.lightup()
        print_tree(tree)

        if tree.is_complete():
            print('Congratulations!!!!!')
