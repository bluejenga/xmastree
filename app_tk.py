#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import tkinter as tk
import copy
from PIL import Image, ImageTk
from tree import Tree

TREE_HEIGHT = 9
DISP_RATIO = 0.75
TREE_WIDTH = TREE_HEIGHT * 2 - 3

CANVAS_WIDTH = round(1700 * DISP_RATIO)
CANVAS_HEIGHT = round(1100 * DISP_RATIO)
CELL_LENGTH = round(900 / TREE_HEIGHT * DISP_RATIO)
TREE_OFFSET_X = round((CANVAS_WIDTH - CELL_LENGTH * TREE_WIDTH) / 2)
TREE_OFFSET_Y = round(150 * DISP_RATIO)
STAR_OFFSET_X = round(775 * DISP_RATIO)
STAR_OFFSET_Y = round(20 * DISP_RATIO)
STAR_WIDTH = round(149 * DISP_RATIO)
STAR_HEIGHT = round(143 * DISP_RATIO)

BG_SIZE = (CANVAS_WIDTH, CANVAS_HEIGHT)
IMG_BG = Image.open('image/bg.png').resize(BG_SIZE, Image.BILINEAR)

STAR_SIZE = (STAR_WIDTH, STAR_HEIGHT)
IMG_STAR_OFF = Image.open('image/star_off.png').resize(STAR_SIZE, Image.BILINEAR)
IMG_STAR_ON= Image.open('image/star_on.png').resize(STAR_SIZE, Image.BILINEAR)

CELL_SIZE = (CELL_LENGTH, CELL_LENGTH)
IMG_ON_P = Image.open('image/cell_on_+.png').resize(CELL_SIZE, Image.BILINEAR)
IMG_ON_I = Image.open('image/cell_on_I.png').resize(CELL_SIZE, Image.BILINEAR)
IMG_ON_L = Image.open('image/cell_on_L.png').resize(CELL_SIZE, Image.BILINEAR)
IMG_ON_T = Image.open('image/cell_on_T.png').resize(CELL_SIZE, Image.BILINEAR)
IMG_ON_O = Image.open('image/cell_on_o.png').resize(CELL_SIZE, Image.BILINEAR)
IMG_OFF_P = Image.open('image/cell_off_+.png').resize(CELL_SIZE, Image.BILINEAR)
IMG_OFF_I = Image.open('image/cell_off_I.png').resize(CELL_SIZE, Image.BILINEAR)
IMG_OFF_L = Image.open('image/cell_off_L.png').resize(CELL_SIZE, Image.BILINEAR)
IMG_OFF_T = Image.open('image/cell_off_T.png').resize(CELL_SIZE, Image.BILINEAR)
IMG_OFF_O = Image.open('image/cell_off_o.png').resize(CELL_SIZE, Image.BILINEAR)

class CellImageInfo:
    """セル毎に保持する画像に関する情報"""
    def __init__(self, off_img, on_img, angle):
        self.off_img = off_img
        self.on_img = on_img
        self.angle = angle
        self.id = None
        self.img = None
        self.photo_img = None
        self.light = None

IMG_DICT = {
        'S'   :CellImageInfo(IMG_OFF_O, IMG_ON_O,   0),
        'E'   :CellImageInfo(IMG_OFF_O, IMG_ON_O,  90),
        'N'   :CellImageInfo(IMG_OFF_O, IMG_ON_O, 180),
        'W'   :CellImageInfo(IMG_OFF_O, IMG_ON_O, 270),
        'NE'  :CellImageInfo(IMG_OFF_L, IMG_ON_L,   0),
        'NW'  :CellImageInfo(IMG_OFF_L, IMG_ON_L,  90),
        'SW'  :CellImageInfo(IMG_OFF_L, IMG_ON_L, 180),
        'ES'  :CellImageInfo(IMG_OFF_L, IMG_ON_L, 270),
        'NS'  :CellImageInfo(IMG_OFF_I, IMG_ON_I,   0),
        'EW'  :CellImageInfo(IMG_OFF_I, IMG_ON_I,  90),
        'ESW' :CellImageInfo(IMG_OFF_T, IMG_ON_T,   0),
        'NES' :CellImageInfo(IMG_OFF_T, IMG_ON_T,  90),
        'NEW' :CellImageInfo(IMG_OFF_T, IMG_ON_T, 180),
        'NSW' :CellImageInfo(IMG_OFF_T, IMG_ON_T, 270),
        'NESW':CellImageInfo(IMG_OFF_P, IMG_ON_P,   0),
        }


class Application(tk.Frame):

    def __init__(self, master, tree):
        super().__init__(master)
        self.master = master
        self.tree = tree
        self.img_info = [[None for y in range(self.tree.height)]
                               for x in range(self.tree.width)]
        self.create_tree_canvas()
        self.create_controls()
        self.pack()

    def create_tree_canvas(self):
        w, h = IMG_BG.size
        self.canvas = tk.Canvas(self, width=w, height=h)
        self.bg_img = ImageTk.PhotoImage(IMG_BG)
        self.canvas.create_image(0, 0, image=self.bg_img, anchor=tk.NW)

        # アプリ開始時は完成したツリーを表示
        self.tree.build()
        self.tree.lightup()
        for cell in tree.get_cell_list():
            info = self.get_img_info_for_cell(cell)
            x = cell.x * CELL_LENGTH + TREE_OFFSET_X
            y = cell.y * CELL_LENGTH + TREE_OFFSET_Y
            info.id = self.canvas.create_image(x, y,
                                               image=info.photo_img,
                                               anchor=tk.NW)
            self.img_info[cell.x][cell.y] = info

        self.star_img = ImageTk.PhotoImage(IMG_STAR_ON)
        self.star_id = self.canvas.create_image(STAR_OFFSET_X,
                                                STAR_OFFSET_Y,
                                                image=self.star_img,
                                                anchor=tk.NW)

        self.canvas.bind('<ButtonRelease-1>', self.on_click_canvas)
        self.canvas.pack()

    def get_img_info_for_cell(self, cell):
        info = copy.copy(IMG_DICT[cell.get_linked_dir_str()])
        info.img = info.on_img if cell.light else info.off_img
        info.light = cell.light
        info.photo_img = ImageTk.PhotoImage(info.img.rotate(info.angle))
        return info

    def on_click_canvas(self, event):
        x = (event.x - TREE_OFFSET_X) // CELL_LENGTH
        y = (event.y - TREE_OFFSET_Y) // CELL_LENGTH
        if self.tree.is_valid_coord(x, y):
            self.rotate_cell(x, y)

    def rotate_cell(self, x, y):
        info = self.img_info[x][y]
        info.angle -= 15
        info.photo_img = ImageTk.PhotoImage(info.img.rotate(info.angle))
        self.canvas.itemconfigure(info.id, image = info.photo_img)
        if info.angle % 90 == 0:
            self.tree.rotate(x, y)
            self.tree.lightup()
            self.update_tree()
            self.update_star()
        else:
            self.after(15, self.rotate_cell, x, y)

    def update_tree(self):
        for cell in tree.get_cell_list():
            info = self.img_info[cell.x][cell.y]
            if info.light != cell.light:
                info.img = info.on_img if cell.light else info.off_img
                info.light = cell.light
                info.photo_img = ImageTk.PhotoImage(info.img.rotate(info.angle))
                self.canvas.itemconfigure(info.id, image = info.photo_img)
                self.img_info[cell.x][cell.y] = info

    def update_star(self):
        if tree.is_complete():
            self.star_img = ImageTk.PhotoImage(IMG_STAR_ON)
        else:
            self.star_img = ImageTk.PhotoImage(IMG_STAR_OFF)
        self.canvas.itemconfigure(self.star_id, image=self.star_img)

    def create_controls(self):
        start = tk.Button(self, text='Start', command=self.start_new_game)
        start.pack()

    def start_new_game(self):
        self.tree.build()
        self.tree.shuffle()
        self.tree.lightup()

        for cell in tree.get_cell_list():
            info = self.get_img_info_for_cell(cell)
            info.id = self.img_info[cell.x][cell.y].id # idは前回のを引き継ぐ
            self.canvas.itemconfigure(info.id, image=info.photo_img)
            self.img_info[cell.x][cell.y] = info

        self.update_star()

tree = Tree(TREE_HEIGHT)
root = tk.Tk()
app = Application(root, tree)
app.mainloop()
