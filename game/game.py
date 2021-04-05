import pygame
from .grid.grid import Grid
from .player.movement_direction import MovementDirection
from .config import GridConfig, WindowConfig

class Game:
    WIDTH, HEIGHT = WindowConfig.WIDTH.value, WindowConfig.HEIGHT.value
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    FPS = WindowConfig.FPS.value

    def __init__(self):
        pygame.display.set_caption("QIX")
        self.grid = Grid(GridConfig.GRID_WIDTH.value, GridConfig.GRID_LENGTH.value)

    def update(self):
        pass

    def draw(self):
        self.WIN.fill((255,255,255))
        self.grid.draw(self.WIN)
        pygame.display.update()


    def handle_player_movement(self, keys_pressed):
        #TODO: Implement speed in terms of velocity & acceleration to prevent clunky movement
        if keys_pressed[pygame.K_SPACE]:
            self.grid.activate_drawing_mode()

        if keys_pressed[pygame.K_a]:
            self.grid.move_player(MovementDirection.left)
        if keys_pressed[pygame.K_d]:
            self.grid.move_player(MovementDirection.right)
        if keys_pressed[pygame.K_w]:
            self.grid.move_player(MovementDirection.up)
        if keys_pressed[pygame.K_s]:
            self.grid.move_player(MovementDirection.down)


    def gameloop(self):
        clock = pygame.time.Clock()
        run = True
        while run:
            clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    break

                keys_pressed = pygame.key.get_pressed()
                self.handle_player_movement(keys_pressed)


                self.update()
                self.draw()
        pygame.quit()

    def start_game(self):
        self.gameloop();