from enum import Enum
import pygame

class WindowConfig(Enum):
    WIDTH = 1600
    HEIGHT = 1600
    FPS = 60

class GridConfig(Enum):
    GRID_WIDTH = 100
    GRID_LENGTH = 100
    NODE_SIZE = WindowConfig.WIDTH.value // GRID_WIDTH


class PlayerConfig(Enum):
    PLAYER_SPRITE = pygame.image.load('game/player/parrot.png')

class QixConfig(Enum):
    QIX_SPRITE = pygame.image.load('game/qix/balloon.png')
    QIX_START_COORDINATES = [GridConfig.GRID_WIDTH.value//2, GridConfig.GRID_LENGTH.value//2]
    #QIX_SPRITE = pygame.image.load('game/qix/')