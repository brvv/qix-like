import pygame
from ..config import PlayerConfig

class Player:
    PLAYER_SPRITE = PlayerConfig.PLAYER_SPRITE.value

    def __init__(self, draw_size):
        self._draw_size = draw_size;
        self.image = pygame.transform.scale(self.PLAYER_SPRITE, self._draw_size)
        #[x,y]
        self.position = [0,0]

    def draw(self, window, coord):
        window.blit(self.image, coord)

    def get_position(self):
        return self.position

    def set_position(self, new_position):
        self.position = new_position

    def move(self, direction):
        self.position[0] += direction.value[0]
        self.position[1] += direction.value[1]