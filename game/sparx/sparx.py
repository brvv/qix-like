import pygame
from ..config import SparxConfig


class Sparx:
    SPARX_SPRITE = SparxConfig.SPARX_SPRITE.value
    def __init__(self,draw_size,start_position,previous):
        
        self.image = pygame.transform.scale(self.SPARX_SPRITE, draw_size)
        self.position = start_position
        self.previous = previous
        self.dropped = False
        self.dropped_coordinates = []
        
    
    def draw(self,window,coord):
        window.blit(self.image,coord)
        
    def get_position(self):
        return self.position
     
    def in_dropped_state(self,lst):
        self.dropped = True
        self.dropped_coordinates.extend(lst)
        
    def _not_in_dropped_state(self):
        self.dropped = False
        self.dropped_coordinates = []
        
    def is_sparx_in_dropped(self):
        return self.dropped
    
    def moved_in_dropped_state(self, coordinates):
        if not self.dropped:
            return False
        
        if not self.set_position([c for c in coordinates if c in self.dropped_coordinates]):
            self.dropped = False
            self.dropped_coordinates = []
            return False    
        return True
        
        
    def set_position(self, coordinates):
        x_straight = [item for item in coordinates if item[0] == self.previous[0] == self.position[0] and item != self.previous]
        y_straight = [item for item in coordinates if item[1] == self.previous[1] == self.position[1] and item != self.previous]
        
        if x_straight != []:
            self.previous = self.position
            self.position = x_straight[0]
            return True
        
        if y_straight != []:
            self.previous = self.position
            self.position = y_straight[0]
            return True
        
        for c in coordinates:
            if c == self.previous:
                continue
            if c in self.dropped_coordinates and len(coordinates) > 2:
                self.dropped_coordinates.remove(c)
                
            self.previous = self.position
            self.position = c
            return True
        return False