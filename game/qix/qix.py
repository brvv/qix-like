import pygame
from ..config import QixConfig

class Qix:
    QIX_SPRITE = QixConfig.QIX_SPRITE.value

    def __init__(self, draw_size):
        self._draw_size = draw_size;
        self.image = pygame.transform.scale(self.QIX_SPRITE, self._draw_size)
        self.position = QixConfig.QIX_START_COORDINATES.value

    #TODO: WOrks on an image right now, need to change it later to be something else
    def draw(self, window, coord):
        window.blit(self.image, coord)

    def get_position(self):
        return self.position

    def set_position(self, new_position):
        self.position = new_position

