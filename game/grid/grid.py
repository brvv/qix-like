import pygame
from .node import Node
from .node_states import State
from ..player.player import Player
from ..qix.qix import Qix
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
        self.qix = Qix((self.NODE_SIZE,self.NODE_SIZE))

        self._width = width
        self._length = length
        self._drawn_line = []
        
    #This function does all the logic
    def update(self):
        self._update_player()

    def _update_player(self):
        if self.player.get_velocity == 0.0:
            return None
        else:
            self.player.increase_movement_counter()
            if self.player.is_counter_above_thres(2):
                self.player.decrease_movement_counter(2)
                direction = self.player.get_movement_direction()
                self._update_node(self.player.get_position())
                self.move_player(direction)
                
    def _update_node(self, coordinates):
        self._get_node(coordinates).update_node()
    
    def start_moving_player(self, direction):
        self.player.start_moving()
        self.player.set_movement_direction(direction)

    def stop_moving_player(self, direction):
        if self.player.get_movement_direction() == direction:
            self.player.stop_moving()

    def draw(self, window):
        self._draw_grid(window)
        self._draw_objects(window)

    def move_player(self, direction):
        if (self._is_drawing_mode_on()):
            self._move_player_while_drawing(direction)
        else:
            self._move_player_simple(direction)

    def activate_drawing_mode(self):
        self.player.set_drawing_mode(True)

    def deactivate_drawing_mode(self):
        self.player.set_drawing_mode(False)

    def _is_drawing_mode_on(self):
        return self.player.is_drawing_mode_on()

    def _move_player_simple(self, direction):
        current_player_position = self.player.get_position()
        new_x_1 = current_player_position[0] + direction.value[0]
        new_y_1 = current_player_position[1] + direction.value[1]
        new_x_2 = new_x_1 + direction.value[0]
        new_y_2 = new_y_1 + direction.value[1]

        coordinates1 = [new_x_1, new_y_1]
        coordinates2 = [new_x_2, new_y_2]

        if self._are_valid_coordinates(coordinates1) and self._are_valid_coordinates(coordinates2):
            if  self._are_coordinates_walkable(coordinates1) and self._are_coordinates_walkable(coordinates2):
                self.player.set_position(coordinates2)
        
                return [coordinates1, coordinates2]

    def _move_player_while_drawing(self, direction):
        new_coordinates = self._move_player_simple(direction)
        if new_coordinates == None:
            return None

        for coordinates in new_coordinates:
            if not self._are_valid_coordinates(coordinates):
                return None

            if self._are_coordinates_drawable(coordinates):
                self._fill_node_from_coordinates(coordinates, State.DRAWN_LINE)
                self._drawn_line.append(coordinates)

            elif self._are_coordinates_walkable(coordinates):
                self.deactivate_drawing_mode()
                if len(self._drawn_line) > 0:
                    self._fill_area_opposite_to_qix(coordinates)
                    self._fill_drawn_line()

    def _fill_area_opposite_to_qix(self, new_coordinates):
        flood_fill_start_coordinates = self._find_flood_fill_start_coordinates(new_coordinates)
        flood_fill_queue = self._get_flood_fill_queue_opposite_to_qix(flood_fill_start_coordinates)
        self._fill_nodes_from_coordinates_list(flood_fill_queue, State.RED_FILL)

    def _find_flood_fill_start_coordinates(self, new_coordinates):
        drawn_line_end = self._drawn_line[-1]

        delta_x = new_coordinates[0] - drawn_line_end[0]
        delta_y = new_coordinates[1] - drawn_line_end[1]

        if delta_y == 0:
            return [[drawn_line_end[0], drawn_line_end[1]-1], [drawn_line_end[0], drawn_line_end[1]+1]]
        elif delta_x == 0:
            return [[drawn_line_end[0]-1, drawn_line_end[1]], [drawn_line_end[0]+1, drawn_line_end[1]]]

    def _get_flood_fill_queue_opposite_to_qix(self, coordinates):
        queue1 = self._get_fill_queue_(coordinates[0])
        queue2 = self._get_fill_queue_(coordinates[1])
        return queue1 if queue1 != None else queue2

    def _get_fill_queue_(self, coordinates):
        queue = []
        queue.append(coordinates)
        qix_coordinates = self.qix.get_position()

        fill_queue = []
        visited_matrix = [[0 for ii in range(self._length)] for i in range(self._width)]

        while len(queue) > 0:
            current_node_coordinates = queue.pop()
            visited_matrix[current_node_coordinates[0]][current_node_coordinates[1]] = 1
            fill_queue.append(current_node_coordinates)
            neighbours = self._get_empty_neighbouring_nodes_coordinates(current_node_coordinates)
            for neighbour in neighbours:
                if neighbour == qix_coordinates:
                    return None
                if visited_matrix[neighbour[0]][neighbour[1]] != 1:
                    queue.append(neighbour)

        return fill_queue

    def _get_empty_neighbouring_nodes_coordinates(self, coordinates):
        neighbouring_coordinates = [[coordinates[0]-1,coordinates[1]],[coordinates[0]+1,coordinates[1]],
                                    [coordinates[0],coordinates[1]-1],[coordinates[0],coordinates[1]+1]]

        valid_neighbours = []
        for coordinate_pair in neighbouring_coordinates:
            if self._are_valid_coordinates(coordinate_pair) and self._are_coordinates_empty(coordinate_pair):
                valid_neighbours.append(coordinate_pair)
        return valid_neighbours

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
        qix_position = self.qix.get_position()
        drawing_coordinates = self._get_drawing_coordinates_from_grid(qix_position)
        self.qix.draw(window, drawing_coordinates)

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

