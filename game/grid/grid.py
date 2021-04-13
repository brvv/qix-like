import pygame, time, random
from .node import Node
from .node_states import State
from ..player.player import Player
from ..qix.qix import Qix
from ..sparx.sparx import Sparx
from ..config import GridConfig, PlayerConfig
from ..spritz.spritz import Spritz


import random

class Grid:
    NODE_SIZE = GridConfig.NODE_SIZE.value
    SPARX_MOVE_FACTOR = 3
    FUSE_GRACE_PERIOD = 100

    
    def __init__(self, width, length, window, drawing_offset=(0,0)):
        self.window = window
        self._offset = drawing_offset
        self.grid = self._init_grid(width, length)
        self._width = width
        self._length = length
        self.grid_size = (width, length)
        
        self.border = []
        self._fill_border()
        
        self.player = Player((self.NODE_SIZE*PlayerConfig.PLAYER_SPRITE_SCALE.value,self.NODE_SIZE*PlayerConfig.PLAYER_SPRITE_SCALE.value))
        self.qix = Qix()
        self._set_qix_area()
        
        self.sparxs = []
        self._add_sparx()
        
        self.spritz = []
        
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
        self._update_qix()
        self._update_spritz()
            
    
    def _add_spritz(self):
        start_pos = self.qix.get_position()
        direction = [random.choice([-1,1]),random.choice([-1,1])]
        self.spritz.append(Spritz(start_pos,direction))
        
    def _update_spritz(self):
        spawn_rate = 1
        if random.randint(1,500) <= spawn_rate:
            self._add_spritz()

        for spritz in self.spritz:
            direction = spritz.get_move_direction()
            if any(self._are_coordinates_claimed([c[0]+direction[0],c[1]]) or self._are_coordinates_claimed([c[0],c[1]+direction[1]]) for c in spritz.get_full_coordinates()):
                self._fill_nodes_from_coordinates_list(spritz.get_full_coordinates(), State.RED_FILL)
                self.spritz.remove(spritz)
                continue
            
            if any(self._are_coordinates_walkable_line([c[0]+direction[0],c[1]]) for c in spritz.get_full_coordinates()):
                spritz.flip_x_direction()
            if any(self._are_coordinates_walkable_line([c[0],c[1]+direction[1]]) for c in spritz.get_full_coordinates()):
                spritz.flip_y_direction()
            if not self._check_next_qix_or_spritz_position(spritz):
                spritz.flip_x_direction()
                spritz.flip_y_direction()
            
            next_position = self._get_next_move_coordinates(direction,spritz.get_position())
            spritz.set_position(next_position)
            self._set_spritz_area()
         
    def _update_qix(self):
        if self.qix.get_steps() == 0:
            self._qix_set_next_movement_direction()
        
        while not self._check_next_qix_or_spritz_position(self.qix):
            self._qix_set_next_movement_direction()
        
        qix_direction = self.qix.get_move_direction()
        next_position = self._get_next_move_coordinates(qix_direction,self.qix.get_position())

        self.qix.reduce_steps()
        self.qix.set_position(next_position)
        self._set_qix_area()
        
    def _check_next_qix_or_spritz_position(self,obj):
        direction = obj.get_move_direction()
        coordinates = obj.get_full_coordinates()
        for coordinate in coordinates:
            new_coordinates = self._get_next_move_coordinates(direction,coordinate)
            
            if not (self._are_valid_coordinates(new_coordinates) and (self._are_coordinates_empty(new_coordinates) 
                    or self._are_coordinates_on_qix(new_coordinates) or new_coordinates in self._drawn_line
                    or self._are_coordinates_on_spritz(new_coordinates))):
                    
                return False
        return True
    
    def _update_player(self):
        self._win()
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
            sparx._not_in_dropped_state()
            
        self._sparx_current_move_val = self.SPARX_MOVE_FACTOR

    def _qix_set_next_movement_direction(self):
        direction = (random.randint(-1,1),random.randint(-1,1))
        steps = random.randint(5,15)
        self.qix.set_move_direction(direction,steps) 
        
    def _add_to_claim(self,lst):
        number_of_nodes = len(set( [(c[0],c[1]) for c in lst] ))
        self.claimed += self.node_percentage * number_of_nodes
        self.player.increase_score(number_of_nodes)
        
    def _check_if_lost_life(self):
        if not (self._check_if_sparx_killed() or self._fuse() or self._check_if_qix_killed() or self._check_if_spritz_killed()):
            return False
        
        self.deactivate_drawing_mode()
        self.player.died()
        if self.player.get_lives() <= 0:
            self._died()
        else:
            self._reset_after_lost_life()
        return True
    
    def _win(self):
        if self.claimed < self.claim_target:
            return
        width = self.window.get_width()
        height = self.window.get_height()
        self._write_text(self.window,width/2,height/2,self._apply_center,"Congratulations",50)
        self._write_text(self.window,width/2,height/2 + 50,self._apply_center,"Score: {}".format(self.player.get_score()),50)
        self._write_text(self.window,width/2,height/2 + 100,self._apply_center,"Claimed: {}%".format(int(self.claimed)),50)
        self._write_text(self.window,width/2,height/2 + 150,self._apply_center,"Remaining Lives: {}".format(self.player.get_lives()),50)
        pygame.display.update()
        self._time_wait(4)
        pygame.quit()
          
    def _reset_game(self):
        pass
    
    def _time_wait(self,seconds):
        timeout = time.time() + seconds
        while time.time() < timeout:
            continue
    
    def _died(self):
        width = self.window.get_width()
        height = self.window.get_height()
        #notdone = True
        
        self._write_text(self.window,width/2,height/2,self._apply_center,"Game Over",50)
        self._write_text(self.window,width/2,height/2 + 50,self._apply_center,"Score: {}".format(self.player.get_score()),50)
        #notdone = self._button("Play Again",width/2,height/2 + 100,(255,0,0),(127,0,0),self._reset_game)
        
        pygame.display.update()
        self._time_wait(3)
        pygame.quit()
         
    def _button(self,msg,x_pos1,y_pos1,act_colour,inact_colour,action):
        button_width = 100
        button_height = 50
        mouse = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        x_pos2 = x_pos1 + button_width
        y_pos2 = y_pos1 + button_height

        self._write_text(self.window,(x_pos1+x_pos2)//2,(y_pos1+y_pos2)//2,self._apply_center,msg)
        if x_pos1 <= mouse[0] <= x_pos2 and y_pos1 <= mouse[1] <= y_pos2:
            pygame.draw.rect(self.window,act_colour,[x_pos1,y_pos1,button_width,button_height])
            if mouse_click:
                action()
                return False
        else:
            pygame.draw.rect(self.window,inact_colour,[x_pos1,y_pos1,button_width,button_height])
        
        return True
    
    def _lost_life_screen(self):
        self._write_text(self.window,self.window.get_width()/2,self.window.get_height()/2,self._apply_center,"Died",40,(255,255,0))
        pygame.display.update()
        self._time_wait(1)
 
    def _remove_spritz(self):
        for spritz in self.spritz:
            self._fill_nodes_from_coordinates_list(spritz.get_full_coordinates(),State.EMPTY)
        self.spritz = []
    
    def _reset_after_lost_life(self):
        self._lost_life_screen()  
        player_position = self.player.get_position()
        if not self._are_coordinates_walkable_line(player_position):
            self.player.set_position(self._drawn_line[0])
            self._fill_nodes_from_coordinates_list(self._drawn_line[1:],State.EMPTY)
            self._drawn_line = []
        self._remove_spritz()
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
    
    def _check_if_spritz_killed(self):
        for spritz in self.spritz:
            spritz_coordinates = spritz.get_full_coordinates()
            if self.player.get_position() in spritz_coordinates:
                return True
            if any(coordinate in self._drawn_line for coordinate in spritz_coordinates):
                return True
        return False
    
    def _check_if_qix_killed(self):
        qix_coordinates = self.qix.get_full_coordinates()
        if self.player.get_position() in qix_coordinates:
            return True
        if any(coordinate in self._drawn_line for coordinate in qix_coordinates):
            return True
        return False
        
    def _check_sparx_path(self,dropped):
        for sparx in self.sparxs:
            if sparx.get_position() in dropped or sparx.is_sparx_in_dropped():
                sparx.in_dropped_state(dropped.copy())
    
    def _check_if_sparx_killed(self):
        player_position = self.player.get_position()
        hitbox_coordinates = self._get_neighbouring_nodes_coordinates(player_position)
        for sparx in self.sparxs:
            if sparx.get_position() in hitbox_coordinates:
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
        self._write_text(window,0,window.get_height(),self._apply_bottom_left,"Lives: {}".format(self.player.get_lives()))
        self._write_text(window,window.get_width()/2,window.get_height()- 45,self._apply_bottom,"Score: {}".format(self.player.get_score()))
        self._write_text(window,window.get_width()/2,window.get_height(),self._apply_bottom,"Claimed: {}% ".format(int(self.claimed)))
        self._write_text(window,window.get_width(),window.get_height(),self._apply_bottom_right,"Target: {}%".format(self.claim_target))
     
    def _write_text(self,window,x_pos,y_pos,apply,txt,font_size = 32,color = (0,0,0)):
        font = pygame.font.Font('freesansbold.ttf',font_size)
        text = font.render(txt,True,color)
        textRect = text.get_rect()
        apply(textRect,x_pos,y_pos)
        window.blit(text,textRect)
    
    def _apply_center(self,textRect,x_pos,y_pos):
        textRect.center = (x_pos,y_pos)
    
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
    
    def _get_next_move_coordinates(self, direction, current_coordinates):
        new_x_1 = current_coordinates[0] + direction[0]
        new_y_1 = current_coordinates[1] + direction[1]
        return [new_x_1, new_y_1]
    
    def _get_next_move_coordinates_enum(self, direction, current_coordinates):
        new_x_1 = current_coordinates[0] + direction.value[0]
        new_y_1 = current_coordinates[1] + direction.value[1]
        return [new_x_1, new_y_1]
        
    def _move_player_simple(self, direction):
        current_player_position = self.player.get_position()
        coordinates1 = self._get_next_move_coordinates_enum(direction,current_player_position)
        coordinates2 = self._get_next_move_coordinates_enum(direction,coordinates1)
        
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
                if self._is_drawn_line_valid(coordinates):
                    self._fill_area_opposite_to_qix(coordinates)
                    self._fill_drawn_line()
                else:
                    self._drawn_line = []
    
    def _is_drawn_line_valid(self, end_coordinates):
        if len(self._drawn_line) >= 3:
            is_start_valid = self._are_coordinates_walkable(self._drawn_line[0])
            is_end_valid = self._are_coordinates_walkable(end_coordinates)
            is_middle_valid = not self._is_coordinate_list_walkable(self._drawn_line[1:-1])
            return is_start_valid and is_middle_valid and is_end_valid
        return False

    def _is_coordinate_list_walkable(self, lst):
        for coordinate in lst:
            if not self._are_coordinates_walkable(coordinate):
                return False
        return True

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
        qix_coordinates = self.qix.get_full_coordinates()
        valid_neighbours = []
        for coordinate_pair in neighbouring_coordinates:
            if self._are_coordinates_empty(coordinate_pair) or coordinate_pair in qix_coordinates:
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
        
        for coordinate in dropped_walkable:
            while coordinate in self.border:
                self.border.remove(coordinate)
        
        self._add_to_claim(dropped_walkable)
        self._check_sparx_path(dropped_walkable)
        
    
    def _are_coordinates_on_spritz(self,coordinates):
        return (self._get_node(coordinates).get_state() == State.SPRITZ)
      
    def _are_coordinates_on_qix(self,coordinates):
        return (self._get_node(coordinates).get_state() == State.QIX)
    
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

    def _are_coordinates_claimed(self,coordinates):
        return self._get_node(coordinates).get_state() == State.RED_FILL
        
    def _are_coordinates_drawable(self, coordinates):
        return self._are_coordinates_empty(coordinates) or coordinates in self.qix.get_full_coordinates()
    
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
        self._draw_player(window)
    
    
    def _add_sparx(self):
        sparx_spawn_offset = 10
        player_position = self.player.get_position()
        invalid_coordinates = [player_position]
        self._get_invalid_coordinates_to_add_sparx(player_position,sparx_spawn_offset,invalid_coordinates)
        valid_coordinates = player_position
        
        while valid_coordinates in invalid_coordinates or not self._are_coordinates_walkable_line(valid_coordinates):
            valid_coordinates = random.choice(self.border)
        
    
        adjacent = [c for c in self._get_neighbouring_nodes_coordinates(valid_coordinates) if self._are_coordinates_walkable_line(c)]
        random.shuffle(adjacent)
        self.sparxs.append(Sparx((self.NODE_SIZE,self.NODE_SIZE), valid_coordinates,adjacent[0]))
        self.sparxs.append(Sparx((self.NODE_SIZE,self.NODE_SIZE), valid_coordinates,adjacent[1]))
    
            
    def _draw_spiders(self, window):
        for sparx in self.sparxs:
            sparx_position = sparx.get_position()
            drawing_coordinates = self._get_drawing_coordinates_from_grid(sparx_position)
            sparx.draw(window, drawing_coordinates)
        
    def _find_qix_or_spritz_nodes(self,coordinate,lst,iterations):
        if iterations == 0 or coordinate in lst:
            return
        lst.append(coordinate)
        for element in self._get_neighbouring_nodes_coordinates(coordinate):
            self._find_qix_or_spritz_nodes(element,lst,iterations - 1)
        
    def _set_qix_area(self):
        qix_position = self.qix.get_position()
        lst = []
        self._find_qix_or_spritz_nodes(qix_position,lst,5)
        self._fill_nodes_from_coordinates_list(self.qix.get_full_coordinates(),State.EMPTY)
        self.qix.set_full_coordinates(lst)
        self._fill_nodes_from_coordinates_list(lst,State.QIX)
        
    
    def _set_spritz_area(self):
        for spritz in self.spritz:
            position = spritz.get_position()
            lst = []
            self._find_qix_or_spritz_nodes(position,lst,2)
            self._fill_nodes_from_coordinates_list(spritz.get_full_coordinates(),State.EMPTY)
            spritz.set_full_coordinates(lst)
            for coordinate in lst:
                if not self._are_coordinates_on_qix(coordinate):
                    self._fill_node_from_coordinates(coordinate,State.SPRITZ)
                        
    
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

