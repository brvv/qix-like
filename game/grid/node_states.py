from enum import Enum

class State(Enum):
    EMPTY = (0,0,0)
    WALKABLE_LINE = (255,255,255)
    DROPPED_WALKABLE_LINE = (192,192,192)
    DRAWN_LINE = (200, 30, 30)
    RED_FILL = (255,0,0)
    GREEN_FILL = (0,255,0)
    BLUE_FILL = (0,0,255)
    