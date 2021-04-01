import pygame
from .node import Node
from .node_states import State
from ..player.player import Player
from ..config import GridConfig

import random

class Grid:
    NODE_SIZE = GridConfig.NODE_SIZE.value

    def __init__(self, width, length, drawing_offset=(0,0)):
        self._offset = drawing_offset
        self.grid = self._init_grid(width, length)
        self._fill_border()
        self.grid_size = (width, length)
        self.spiders = []
        self.player = Player((self.NODE_SIZE,self.NODE_SIZE))
        self._drawn_line = []
        #self.qix = Qix()

    #This function does all the logic
    def update(self):
        pass

    def move_player(self, direction):
        if (self._is_drawing_mode_on()):
            self._move_player_while_drawing(direction)
        else:
            self._move_player_simple(direction)

    def _is_drawing_mode_on(self):
        return self.player.is_drawing_mode_on()

    def activate_drawing_mode(self):
        self.player.set_drawing_mode(True)

    def deactivate_drawing_mode(self):
        self.player.set_drawing_mode(False)

    def _move_player_simple(self, direction):
        current_player_position = self.player.get_position()
        new_x = current_player_position[0] + direction.value[0]
        new_y = current_player_position[1] + direction.value[1]
        coordinates = [new_x, new_y]

        if self._are_valid_coordinates(coordinates):
            if  self._are_coordinates_walkable(coordinates):
                self.player.set_position(coordinates)
        
        return coordinates

    def _move_player_while_drawing(self, direction):
        new_coordinates = self._move_player_simple(direction)
        if not self._are_valid_coordinates(new_coordinates):
            return None

        if self._are_coordinates_drawable(new_coordinates):
            self._fill_node_from_coordinates(new_coordinates, State.DRAWN_LINE)
            self._drawn_line.append(new_coordinates)

        elif self._are_coordinates_walkable(new_coordinates):
            self.deactivate_drawing_mode()
            self._fill_drawn_line()

    def _fill_drawn_line(self):
        self._fill_nodes_from_coordinates_list(self._drawn_line, State.WALKABLE_LINE)
        self._drawn_line = []

    def _fill_nodes_from_coordinates_list(self, lst, state):
        for coordinates in lst:
            self._fill_node_from_coordinates(coordinates, state)
    
    def _are_valid_coordinates(self, coordinates):
        is_x_valid = 0 <= coordinates[0] <= self.grid_size[0] - 1
        is_y_valid = 0 <= coordinates[1] <= self.grid_size[1] - 1
        return is_x_valid and is_y_valid 

    def _are_coordinates_walkable(self, coordinates):
        return  self._are_coordinates_walkable_line(coordinates) or (self._is_drawing_mode_on() and self._are_coordinates_drawable(coordinates))

    def _are_coordinates_walkable_line(self, coordinates):
        return (self._get_node(coordinates).get_state() == State.WALKABLE_LINE)

    def _are_coordinates_drawable(self, coordinates):
        return self._are_coordinates_empty(coordinates)
    
    def _are_coordinates_empty(self, coordinates):
        return self._get_node(coordinates).get_state() == State.EMPTY

    def _get_node(self, coordinates):
        return self.grid[coordinates[0]][coordinates[1]]

    #This function does all the drawing
    def draw(self, window):
        self._draw_grid(window)
        self._draw_objects(window)

    def _fill_border(self):
        self._fill_column(0, State.WALKABLE_LINE)
        self._fill_column(-1, State.WALKABLE_LINE)
        self._fill_row(0, State.WALKABLE_LINE)
        self._fill_row(-1, State.WALKABLE_LINE)

    def _fill_column(self, column_index, state):
        for node in (self.grid[column_index]):
            node.set_state(state)

    def _fill_row(self, row_index, state):
        for node in ([column[row_index] for column in self.grid]):
            node.set_state(state)

    def _fill_node_from_coordinates(self, coordinates, state):
        self.grid[coordinates[0]][coordinates[1]].set_state(state)

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
        return grid

