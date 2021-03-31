import pygame
from .node import Node
from .node_states import State
from .player import Player

import random

class Grid:
    NODE_SIZE = 80

    def __init__(self, width, length, drawing_offset=(0,0)):
        self._offset = drawing_offset
        self.grid = self._init_grid(width, length)
        self.grid_size = (width, length)
        self.spiders = []
        self.player = Player((self.NODE_SIZE,self.NODE_SIZE))
        #self.qix = Qix()

    #This function does all the logic
    def update(self):
        pass

    #This function does all the drawing
    def draw(self, window):
        self._draw_grid(window)
        self._draw_objects(window)

    def _get_drawing_coordinates_from_grid(self, grid_coordinates):
        x, y = grid_coordinates
        return (self._offset[0]+x*self.NODE_SIZE, self._offset[1]+y*self.NODE_SIZE)

    def _draw_objects(self,window):
        self._draw_spiders(window)
        self._draw_qix(window)
        self._draw_player(window)

    def _draw_spiders(self, window):
        pass

    def _draw_qix(self, window):
        pass

    def _draw_player(self, window):
        player_position = self.player.get_position()
        drawing_coordinates = self._get_drawing_coordinates_from_grid(player_position)
        self.player.draw(window, drawing_coordinates)

    def _draw_grid(self, window):
        for column in self.grid:
            for node in column:
                node.draw(window)

    def _init_grid(self, width, length):
        grid = [[0 for ii in range(length)] for i in range(width)]
        for x in range(width):
            for y in range(length):
                draw_coord = self._get_drawing_coordinates_from_grid((x, y))
                grid[x][y] = Node(draw_coord, State.EMPTY, self.NODE_SIZE)
                #TODO: Remove next line
                grid[x][y].set_color((random.randint(0,255),random.randint(0,255),random.randint(0,255)))
        return grid

