import pygame
from grid.grid import Grid

class Game:
    WIDTH, HEIGHT = 800, 800
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    FPS = 60

    def __init__(self):
        pygame.display.set_caption("QIX")
        self.grid = Grid(10,10)

    def update(self):
        pass

    def draw(self):
        self.WIN.fill((255,255,255))
        self.grid.draw(self.WIN)
        pygame.display.update()

    def gameloop(self):
        clock = pygame.time.Clock()
        run = True
        while run:
            clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                self.update()
                self.draw()
        pygame.quit()

    def start_game(self):
        self.gameloop();