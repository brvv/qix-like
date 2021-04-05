import pygame


class Node:
    def __init__(self, coord, state, node_size):
        self.rect = pygame.Rect(coord[0], coord[1], node_size, node_size)
        self.state = state
        self.color = state.value
        self._is_updated = True

    def draw(self, window, color=None):
        if color == None:
            color = self.color
        if self._is_updated:
            pygame.draw.rect(window, color, self.rect)
            self._is_updated = False

    def set_color(self, new_color):
        self.color = new_color
        self._is_updated = True

    def update_node(self):
        self._is_updated = True

    def get_state(self):
        return self.state
    
    def set_state(self, new_state):
        self.state = new_state
        self.color = new_state.value
        self._is_updated = True