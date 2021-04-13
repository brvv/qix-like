import pygame
from ..config import PlayerConfig

class Player:
    PLAYER_SPRITE = PlayerConfig.PLAYER_SPRITE.value

    def __init__(self, draw_size):
        self._draw_size = draw_size;
        self.image = pygame.transform.scale(self.PLAYER_SPRITE, self._draw_size)
        self.lives = 3
        self.score = 0
        self.position = [0,0]
        self.is_drawing = False
        self._velocity = 0
        self._movement_counter = 0.0
        self._movement_direction = None

    def get_lives(self):
        return self.lives
        
    def died(self):
        self.lives -= 1
    
    def get_score(self):
        return self.score
    
    def increase_score(self,fact = 1):
        self.score += 150 * fact
    
    
    def draw(self, window, coord):
        window.blit(self.image, (coord[0] - self._draw_size[0]//2+2, coord[1] - self._draw_size[1]//2+2))

    def get_velocity(self):
        return self._velocity

    def set_movement_direction(self, direction):
        self._movement_direction = direction
    
    def get_movement_direction(self):
        return self._movement_direction

    def increase_movement_counter(self):
        self._movement_counter += self._velocity

    def decrease_movement_counter(self, value = 2):
        self._movement_counter -= value

    def reset_movement_counter(self):
        self._movement_counter = 0.0

    def is_counter_above_thres(self, thres):
        return self._movement_counter >= thres

    def start_moving(self):
        self._velocity = PlayerConfig.PLAYER_VELOCITY.value

    def stop_moving(self):
        self._velocity = 0

    def get_position(self):
        return self.position

    def is_drawing_mode_on(self):
        return self.is_drawing

    def set_drawing_mode(self, value):
        self.is_drawing = value

    def set_position(self, new_position):
        self.position = new_position

    def move(self, direction):
        self.position[0] += direction.value[0]
        self.position[1] += direction.value[1]