import pygame

class Node:
    def __init__(self, coord, state, node_size):
        self.rect = pygame.Rect(coord[0], coord[1], node_size, node_size)
        self.state = state
        self.color = state.value

    def draw(self, window, color=None):
        if color == None:
            color = self.color
        pygame.draw.rect(window, color, self.rect)

    def set_color(self, new_color):
        self.color = new_color

    def get_state(self):
        return self.state
    
    def set_state(self, new_state):
        self.state = new_state