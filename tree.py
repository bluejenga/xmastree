#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import random
import itertools

#Direction
DIR_N = 0 #North
DIR_E = 1 #East
DIR_S = 2 #South
DIR_W = 3 #West
DIR_NUM = 4
#隣のセルへの座標の差分
DELTA = [(0, -1), (1, 0), (0, 1), (-1, 0)]

class Cell:
    """Treeを構成するCellのクラス"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        #迷路の一部に割り当てられたかどうか
        self.used = False
        #隣接するセルと接続している方角
        self.linked_dir = [False, False, False, False] #[N, E, S, W]

    def rotate(self, n):
        """セルを時計回りに90*n度回転する"""
        self.linked_dir = self.linked_dir[-n:] + self.linked_dir[:-n]


class Tree:
    """
    木を表すクラス。
    長方形に並んだCellで構成される。
    不要な領域にはCellの代わりにNoneを割り当てて、木の形を表現する。
    CellとCellの接続が迷路の通路を表す。
    """
    def __init__(self, height):
        self.height = height
        #widthはheightから算出する。
        width = height * 2 - 3 if height > 1 else 1
        self.width = width

        self.cells = [None] * (width * height)
        for y, x in itertools.product(range(height), range(width)):
            if self.is_valid_coord(x, y):
                self.cells[x + y * width] = (Cell(x, y))


    def is_valid_coord(self, x, y):
        """
        指定した座標が有効かどうかを返す。
        """

        #長方形の範囲に収まるかどうか
        if x < 0 or x >= self.width:
            return False
        if y < 0 or y >= self.height:
            return False

        #木の形の範囲に収まるかどうか
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
            if dst != None and dst.used == False:
                links.append((src, direction, dst))
        return links

    def build(self):
        """迷路を構築する"""

        #初期化
        for cell in self.cells:
            if cell != None:
                cell.used = False
                cell.fixed = False
                cell.linked_dir = [False, False, False, False]

        #木の頂点から迷路作成開始（実際にはどこからでもよい）
        center = self.height - 2 if self.height > 1 else 0
        start = self.cells[center]
        start.used = True
        links = self.get_available_links_from(start)

        #通路候補がなくなるまで繰り返し
        while len(links) > 0:

            #候補から通路を一つ選択
            src, direction, dst = random.choice(links)
            dst.used = True
            src.linked_dir[direction] = True
            dst.linked_dir[(direction + 2) % 4] = True

            #既存候補の中から、dstが重複しているものを削除
            links = [ln for ln in links if ln[2] != dst]
            #dstを起点とした通路を候補に追加
            links.extend(self.get_available_links_from(dst))

    def print_tree(self):
        """コンソールに木の絵を出力"""

        def getString(cell):
            if cell == None:
                return ['     '] * 3

            n = '   ' if cell.linked_dir[DIR_N] else '---'
            s = '   ' if cell.linked_dir[DIR_S] else '---'
            w = ' ' if cell.linked_dir[DIR_W] else '|'
            e = ' ' if cell.linked_dir[DIR_E] else '|'
            return ['+' + n + '+', w + '   ' + e, '+' + s + '+']

        cellstr = [getString(cell) for cell in self.cells]
        for y in range(self.height):
            for i in range(3):
                for x in range(self.width):
                    print(cellstr[x + y * self.width][i], end='')
                print()


    def shuffle(self):
        for cell in self.cells:
            if cell != None and cell.y < self.height - 1:
                n = random.choice(range(DIR_NUM))
                cell.rotate(n)

if __name__ == '__main__':
    tree = Tree(10)
    tree.build()
    #tree.shuffle()
    tree.print_tree()
