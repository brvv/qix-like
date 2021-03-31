import pygame

class Player:
    PLAYER_SPRITE = pygame.image.load('grid/parrot.png')

    def __init__(self, draw_size):
        self._draw_size = draw_size;
        self.image = pygame.transform.scale(self.PLAYER_SPRITE, self._draw_size)
        self.position = (0,0)

    def draw(self, window, coord):
        window.blit(self.image, coord)

    def get_position(self):
        return self.position