import pygame
from ..config import SparxConfig


class Sparx:
    SPARX_SPRITE = SparxConfig.SPARX_SPRITE.value
    def __init__(self,draw_size,start_position,previous):
        
        self.image = pygame.transform.scale(self.SPARX_SPRITE, draw_size)
        self.position = start_position
        self.previous = previous
        
        
    def _update(self):
        self._draw()
        pass
    
    def draw(self,window,coord):
        window.blit(self.image,coord)
        
    def get_position(self):
        return self.position
        
    def set_position(self, coordinates):
        for c in coordinates:
            if c == self.previous:
                continue
            
            self.previous = self.position
            self.position = c
            return