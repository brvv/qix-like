from enum import Enum
import pygame

class WindowConfig(Enum):
    WIDTH = 1616 //2
    HEIGHT = 1816 //2 
    FPS = 60

class GridConfig(Enum):
    #BOTH HAVE TO BE AN ODD NUMBER
    GRID_WIDTH = 101
    GRID_LENGTH = 101
    NODE_SIZE = WindowConfig.WIDTH.value // GRID_WIDTH


class PlayerConfig(Enum):
    PLAYER_SPRITE = pygame.image.load('game/player/parrot.png')
    PLAYER_VELOCITY = 1
    #Scales player's image to 4 nodes in size
    PLAYER_SPRITE_SCALE = 4

class QixConfig(Enum):
    #QIX_SPRITE = pygame.image.load('game/qix/balloon.png')
    QIX_START_COORDINATES = [GridConfig.GRID_WIDTH.value//2, GridConfig.GRID_LENGTH.value//2]
    #QIX_SPRITE = pygame.image.load('game/qix/')
    
    
class SparxConfig(Enum):
    SPARX_SPRITE =pygame.image.load('game/sparx/darl.png')