import pygame
from random import randint
from .node import Node
from .node_states import State
from ..player.player import Player
from ..qix.qix import Qix
from ..sparx.sparx import Sparx
from ..config import GridConfig


import random

class Grid:
    NODE_SIZE = GridConfig.NODE_SIZE.value
    SPARX_MOVE_FACTOR = 3
    FUSE_GRACE_PERIOD = 100
    
    def __init__(self, width, length, drawing_offset=(0,0)):
        self._offset = drawing_offset
        self.grid = self._init_grid(width, length)
        self._width = width
        self._length = length
        self.grid_size = (width, length)
        
        self.border = []
        self._fill_border()
        
        self.player = Player((self.NODE_SIZE,self.NODE_SIZE))
        self.qix = Qix((self.NODE_SIZE,self.NODE_SIZE))
        self.sparxs = []
        self._add_sparx()
        
        self.claimed = 0
        self.claim_target = 65
        self.node_percentage = 100 / (self._width*self._length)
        
        self._sparx_current_move_val = self.SPARX_MOVE_FACTOR
        self._drawn_line = []
        
        self._fuse_grace = self.FUSE_GRACE_PERIOD
        
    #This function does all the logic
    def update(self):        
        self._update_player()
        self._update_sparx()
    
    def _update_player(self):
        if self._check_if_lost_life():
            return None
            
        if self.player.get_velocity == 0.0:
            return None
        else:
            self.player.increase_movement_counter()
            if self.player.is_counter_above_thres(2):
                self.player.decrease_movement_counter(2)
                direction = self.player.get_movement_direction()
                self._update_node(self.player.get_position())
                self.move_player(direction)
                
    def _update_sparx(self):
        if self._sparx_current_move_val != 0:
            self._sparx_current_move_val -= 1
            return
            
        for sparx in self.sparxs:
            current_position = sparx.get_position()
            possible_next = self._get_neighbouring_nodes_coordinates(current_position)
            self._update_node(current_position)
            
            if sparx.moved_in_dropped_state([c for c in possible_next if self._are_coordinates_dropped(c)]):
                continue
                
            sparx.set_position([c for c in possible_next if self._are_coordinates_walkable_line(c)])        
        self._sparx_current_move_val = self.SPARX_MOVE_FACTOR
        
    # fix
    def _add_to_claim(self,lst):
        self.claimed += self.node_percentage * len(set( [(c[0],c[1]) for c in lst] ))
    
    def _check_if_lost_life(self):
        if not (self._check_if_sparx_killed() or self._fuse()):
            return False
            
        self.player.died()
        if self.player.get_lives() <= 0:
            self._died()
        else:
            self._reset_after_lost_life()
        return True
        
    def _died(self):
        
        pass
        
    def _reset_after_lost_life(self):
        player_position = self.player.get_position()
        if not self._are_coordinates_walkable_line(player_position):
            self.player.set_position(self._drawn_line[0])
            self._fill_nodes_from_coordinates_list(self._drawn_line[1:],State.EMPTY)
            self._drawn_line = []
        self.sparxs = []
        self._add_sparx()
        
    
    
    def _fuse(self):
        if not self._is_drawing_mode_on():
            self._fuse_grace = self.FUSE_GRACE_PERIOD
            return False
        
        if self.player.get_velocity() != 0.0:
            return False

        if self._fuse_grace != 0:
            self._fuse_grace -= 1
            return False
            
        for coordinates in self._drawn_line:
            if not self._are_coordinates_on_fuse(coordinates) and not self._are_coordinates_walkable_line(coordinates):
                if self.player.get_position() == coordinates:
                    return True
                self._fill_node_from_coordinates(coordinates, State.FUSE_LINE)
                break
        return False    
        
        
    def _check_sparx_path(self,dropped):
        for sparx in self.sparxs:
            if sparx.get_position() in dropped:
                sparx.in_dropped_state(dropped.copy())
    
    def _check_if_sparx_killed(self):
        player_position = self.player.get_position()
        for sparx in self.sparxs:
            if sparx.get_position() == player_position:
                self._sparx_current_move_val = self.SPARX_MOVE_FACTOR
                return True
        return False
                    
    
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
        self._draw_stats(window)
        
    def _draw_stats(self,window):
        self._write_text(window,0,window.get_height(),self._apply_bottom_left,"Lives:{}".format(self.player.get_lives()))
        self._write_text(window,window.get_width(),window.get_height(),self._apply_bottom_right,"Score:{}".format(self.player.get_score()))
        self._write_text(window,window.get_width()/2,window.get_height(),self._apply_bottom,"Claimed: {}%   Target:{}%".format(int(self.claimed),self.claim_target))
    
    def _write_text(self,window,x_pos,y_pos,apply,txt):
        font = pygame.font.Font('freesansbold.ttf',32)
        text = font.render(txt,True,(0,0,0))
        textRect = text.get_rect()
        apply(textRect,x_pos,y_pos)
        window.blit(text,textRect)
    
    def _apply_bottom(self,textRect,x_pos,y_pos):
        textRect.midbottom = (x_pos,y_pos)
        
    def _apply_bottom_right(self,textRect,x_pos,y_pos):
        textRect.bottomright = (x_pos,y_pos)
    
    def _apply_bottom_left(self,textRect,x_pos,y_pos):
        textRect.bottomleft = (x_pos,y_pos)
        
    def move_player(self, direction):
        if (self._is_drawing_mode_on()):
            
            self._move_player_while_drawing(direction)
        else:
            self._move_player_simple(direction)

    def activate_drawing_mode(self):
        if self._drawn_line == []:
            self._drawn_line.append(self.player.get_position())
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
        self._add_to_claim(flood_fill_queue)
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
    
    def get_neighbours(self,coordinates):
        return self._get_neighbouring_nodes_coordinates(coordinates)
    
    def _get_neighbouring_nodes_coordinates(self, coordinates):
        temp = [[coordinates[0]-1,coordinates[1]],[coordinates[0]+1,coordinates[1]],
                [coordinates[0],coordinates[1]-1],[coordinates[0],coordinates[1]+1]]
        return [c for c in temp if self._are_valid_coordinates(c)]
    
    def _get_extended_neighbouring_nodes_coordinates(self, coordinates):
        temp = self._get_neighbouring_nodes_coordinates(coordinates)
        temp += [[coordinates[0]-1,coordinates[1]-1], [coordinates[0]-1,coordinates[1]+1], 
                        [coordinates[0]+1,coordinates[1]-1] , [coordinates[0]+1,coordinates[1]+1]]
        return [c for c in temp if self._are_valid_coordinates(c)]
        
    
    def _get_empty_neighbouring_nodes_coordinates(self, coordinates):
        neighbouring_coordinates = self._get_neighbouring_nodes_coordinates(coordinates)
        valid_neighbours = []
        for coordinate_pair in neighbouring_coordinates:
            if self._are_coordinates_empty(coordinate_pair):
                valid_neighbours.append(coordinate_pair)
        return valid_neighbours

    def _fill_drawn_line(self):
        self._fill_nodes_from_coordinates_list(self._drawn_line, State.WALKABLE_LINE)
        self._add_walkable_coordinates_to_border(self._drawn_line)
        self._drop_old_walkable_coordinates()
        self._drawn_line = []

    def _fill_nodes_from_coordinates_list(self, lst, state):
        for coordinates in lst:
            self._fill_node_from_coordinates(coordinates, state)
            
    def _add_walkable_coordinates_to_border(self,lst):
        for coordinates in lst:
            self.border.append(coordinates)
    
    def _drop_old_walkable_coordinates(self):
        dropped_walkable = []
        for walkable_node in self.border:
            neighbours = self._get_extended_neighbouring_nodes_coordinates(walkable_node)
            if not any(self._are_coordinates_empty(item) for item in neighbours):
                dropped_walkable.append(walkable_node)
                self._fill_node_from_coordinates(walkable_node,State.DROPPED_WALKABLE_LINE)
                
        self._add_to_claim(dropped_walkable)
        self._check_sparx_path(dropped_walkable)
        
    
    def _are_valid_coordinates(self, coordinates):
        is_x_valid = 0 <= coordinates[0] <= self.grid_size[0] - 1
        is_y_valid = 0 <= coordinates[1] <= self.grid_size[1] - 1
        return is_x_valid and is_y_valid 

    def _are_coordinates_on_fuse(self,coordinates):
        return (self._get_node(coordinates).get_state() == State.FUSE_LINE)
        
    def _are_coordinates_walkable(self, coordinates):
        return  self._are_coordinates_walkable_line(coordinates) or (self._is_drawing_mode_on() and self._are_coordinates_drawable(coordinates))

    def _are_coordinates_walkable_line(self, coordinates):
        return (self._get_node(coordinates).get_state() == State.WALKABLE_LINE)

    def _are_coordinates_drawable(self, coordinates):
        return self._are_coordinates_empty(coordinates)
    
    def _are_coordinates_dropped(self, coordinates):
        return self._get_node(coordinates).get_state() == State.DROPPED_WALKABLE_LINE
    
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
        row_index = 0
        column_index_val = self._width-1 if column_index < 0 else column_index
        
        for node in (self.grid[column_index]):
            node.set_state(state)
            self.border.append([column_index_val,row_index])
            row_index += 1
            
            
    def _fill_row(self, row_index, state):
        column_index = 0
        row_index_val = self._length - 1 if row_index < 0 else row_index
        
        for node in ([column[row_index] for column in self.grid]):
            node.set_state(state)
            self.border.append([column_index,row_index_val])
            column_index += 1
            
    
    def _fill_node_from_coordinates(self, coordinates, state):
        self.grid[coordinates[0]][coordinates[1]].set_state(state)

    def _get_drawing_coordinates_from_grid(self, grid_coordinates):
        x, y = grid_coordinates
        return (self._offset[0]+x*self.NODE_SIZE, self._offset[1]+y*self.NODE_SIZE)
    
    def _get_invalid_coordinates_to_add_sparx(self,coordinates,iterations,invalid):
        if iterations == 0:
            return
        coordinates = [c for c in self._get_neighbouring_nodes_coordinates(coordinates) if self._are_coordinates_walkable_line(c)]
        for c in coordinates:
            if c in invalid:
                continue
                
            invalid.append(c)
            self._get_invalid_coordinates_to_add_sparx(c,iterations - 1,invalid)
        
            

    def _draw_objects(self,window):
        self._draw_spiders(window)
        self._draw_qix(window)
        self._draw_player(window)
    
    def _add_sparx(self):
        sparx_spawn_offset = 10
        player_position = self.player.get_position()
        invalid_coordinates = [player_position]
        self._get_invalid_coordinates_to_add_sparx(player_position,sparx_spawn_offset,invalid_coordinates)
        valid_coordinates = player_position
        
        while valid_coordinates in invalid_coordinates:
            valid_coordinates = self.border[random.randint(0,len(self.border)-1)]
        
        adjacent = [c for c in self._get_neighbouring_nodes_coordinates(valid_coordinates) if self._are_coordinates_walkable_line(c)]
        self.sparxs.append(Sparx((self.NODE_SIZE,self.NODE_SIZE), valid_coordinates,adjacent[0]))
        self.sparxs.append(Sparx((self.NODE_SIZE,self.NODE_SIZE), valid_coordinates,adjacent[1]))
    
    def _draw_spiders(self, window):
        for sparx in self.sparxs:
            sparx_position = sparx.get_position()
            drawing_coordinates = self._get_drawing_coordinates_from_grid(sparx_position)
            sparx.draw(window, drawing_coordinates)
        

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

