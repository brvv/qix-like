class Spritz:
    
    def __init__(self,position,direction):
        self.position = position
        self.direction = direction
        self.coordinates = []
        
    def get_position(self):
        return self.position
    
    def flip_x_direction(self):
        self.direction[0] = -self.direction[0]
    
    def flip_y_direction(self):
        self.direction[1] = -self.direction[1]
    
    def get_move_direction(self):
        return self.direction
    
    def get_full_coordinates(self):
        return self.coordinates
    
    def set_position(self,position):
        self.position = position
        
    def set_direction(self,direction):
        self.direction = direction
    
    def set_full_coordinates(self,coordinates):
        self.coordinates = coordinates