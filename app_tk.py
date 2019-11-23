#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import tkinter as tk
import copy
from PIL import Image, ImageTk
from tree import Tree

TREE_HEIGHT = 8
CELL_LENGTH = 100

IMG_ON_P = Image.open('image/cell_on_+.png')
IMG_ON_I = Image.open('image/cell_on_I.png')
IMG_ON_L = Image.open('image/cell_on_L.png')
IMG_ON_T = Image.open('image/cell_on_T.png')
IMG_ON_O = Image.open('image/cell_on_o.png')
IMG_OFF_P = Image.open('image/cell_off_+.png')
IMG_OFF_I = Image.open('image/cell_off_I.png')
IMG_OFF_L = Image.open('image/cell_off_L.png')
IMG_OFF_T = Image.open('image/cell_off_T.png')
IMG_OFF_O = Image.open('image/cell_off_o.png')

class CellImageInfo:
    """セル毎に保持する画像に関する情報"""
    def __init__(self, off_img, on_img, angle):
        size = (CELL_LENGTH, CELL_LENGTH)
        self.off_img = off_img.resize(size, Image.BILINEAR)
        self.on_img = on_img.resize(size, Image.BILINEAR)
        self.angle = angle
        self.photo_img = None

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
        self.create_tree_canvas()
        self.create_controls()
        self.pack()

        self.img_info = [[None for y in range(self.tree.height)]
                               for x in range(self.tree.width)]


    def create_tree_canvas(self):
        w = CELL_LENGTH * self.tree.width
        h = CELL_LENGTH * self.tree.height
        self.canvas = tk.Canvas(self, width=w, height=h)
        self.canvas.bind('<ButtonRelease-1>', self.onClickCanvas)
        self.canvas.pack()

    def onClickCanvas(self, event):
        x = event.x // CELL_LENGTH
        y = event.y // CELL_LENGTH
        if self.tree.is_valid_coord(x, y):
            self.tree.rotate(x, y)
            self.tree.lightup()
            self.draw_tree_canvas()

    def draw_tree_canvas(self):
        for cell in tree.get_cell_list():
            info = copy.copy(IMG_DICT[cell.get_linked_dir_str()])
            if cell.light:
                img = info.on_img
            else:
                img = info.off_img
            info.photo_img = ImageTk.PhotoImage(img.rotate(info.angle))
            self.img_info[cell.x][cell.y] = info
            self.canvas.create_image(cell.x * CELL_LENGTH, cell.y * CELL_LENGTH, image=info.photo_img, anchor=tk.NW)

    def create_controls(self):
        start = tk.Button(self, text='Start', command=self.start_new_game)
        start.pack()

    def start_new_game(self):
        self.tree.build()
        self.tree.shuffle()
        self.tree.lightup()
        self.draw_tree_canvas()

tree = Tree(TREE_HEIGHT)
root = tk.Tk()
app = Application(root, tree)
app.mainloop()