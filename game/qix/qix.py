from ..config import QixConfig

class Qix:

    def __init__(self):
        self.position = QixConfig.QIX_START_COORDINATES.value
        self.coordinates = []
        self.movement_direction = None
        self.steps = 0

  
    def reduce_steps(self):
        self.steps -= 1
    
    def set_full_coordinates(self,coordinates):
        self.coordinates = coordinates
    
    def set_move_direction(self,direction,steps):
        self.movement_direction = direction
        self.steps = steps
    
    def get_steps(self):
        return self.steps
        
    def get_move_direction(self):
        return self.movement_direction
        
    def get_full_coordinates(self):
        return self.coordinates
  
    def get_position(self):
        return self.position
    
    def set_position(self, new_position):
        self.position = new_position

