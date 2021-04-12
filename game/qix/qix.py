import pygame
from ..config import QixConfig

class Qix:
    #QIX_SPRITE = QixConfig.QIX_SPRITE.value

    def __init__(self):
        #self._draw_size = draw_size;
        #self.image = pygame.transform.scale(self.QIX_SPRITE, self._draw_size)
        self.position = QixConfig.QIX_START_COORDINATES.value
        self.coordinates = []
        self.movement_direction = None
        self.steps = 0

    #TODO: WOrks on an image right now, need to change it later to be something else
    def draw(self, window, coord):
        window.blit(self.image, coord)
  
    def reduce_steps(self):
        self.steps -= 1
    
    def set_full_coordinates(self,coordinates):
        self.coordinates = coordinates
    
    def set_move_direction(self,direction,steps):
        self.movement_direction = direction
        self.steps = steps
    
    def get_steps(self):
        return self.steps
        
    def get_move_direction(self):
        return self.movement_direction
        
    def get_full_coordinates(self):
        return self.coordinates
  
    def get_position(self):
        return self.position
    
    def set_position(self, new_position):
        self.position = new_position

