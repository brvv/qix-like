import pygame
from .grid.grid import Grid
from .player.movement_direction import MovementDirection
from .config import GridConfig, WindowConfig

class Game:
    WIDTH, HEIGHT = WindowConfig.WIDTH.value, WindowConfig.HEIGHT.value
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    FPS = WindowConfig.FPS.value

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("QIX")
        self.grid = Grid(GridConfig.GRID_WIDTH.value, GridConfig.GRID_LENGTH.value,self.WIN)
        self.WIN.fill((128,128,128))

    def update(self):
        self.WIN.fill((128,128,128))
        self.grid.update()

    def draw(self):
        self.grid.draw(self.WIN)
        pygame.display.update()
        



    def handle_key_down(self, key_pressed):
        if key_pressed == pygame.K_SPACE:
            self.grid.activate_drawing_mode()
        
        if key_pressed == pygame.K_a:
            self.grid.start_moving_player(MovementDirection.left)
        if key_pressed == pygame.K_d:
            self.grid.start_moving_player(MovementDirection.right)
        if key_pressed == pygame.K_w:
            self.grid.start_moving_player(MovementDirection.up)
        if key_pressed == pygame.K_s:
            self.grid.start_moving_player(MovementDirection.down)

    def handle_key_up(self, key_released):
        if key_released == pygame.K_a:
            self.grid.stop_moving_player(MovementDirection.left)
        if key_released == pygame.K_d:
            self.grid.stop_moving_player(MovementDirection.right)
        if key_released == pygame.K_w:
            self.grid.stop_moving_player(MovementDirection.up)
        if key_released == pygame.K_s:
            self.grid.stop_moving_player(MovementDirection.down)

    def gameloop(self):
        clock = pygame.time.Clock()
        run = True
        while run:
            clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    break

                if event.type == pygame.KEYDOWN:
                    self.handle_key_down(event.key)

                if event.type == pygame.KEYUP:
                    self.handle_key_up(event.key)
            
            self.update()
            self.draw()
        pygame.quit()

    def start_game(self):
        self.gameloop();