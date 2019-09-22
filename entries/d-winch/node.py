import math

class Node:

    end_location = None
    move_cost = 1

    def __init__(self, x, y, possible_directions):
        self.x = x
        self.y = y
        self.possible_directions = possible_directions
        self.is_dead_end = len(possible_directions) == 1
        self.distance_from_end = abs(self.end_location[0] - x) + abs(self.end_location[1] - y)
        # Not really needed in our case as squares are 1x1
        #self.distance_from_end = math.sqrt(abs(x - self.end_location[0]) ** 2 + abs(y - self.end_location[1]))

    def remove_dead(self, dead):
        for k, v in self.possible_directions.copy().items():
            if v in dead:
                self.possible_directions.pop(k)
        self.check_if_dead()

    def check_if_dead(self):
        self.is_dead_end = len(self.possible_directions) == 1

    def remove_direction(self, direction):
        self.possible_directions.pop(direction)

    def get_single_route(self):
        return self.possible_directions

    def __len__(self):
        return len(self.possible_directions)

    def __str__(self):
        return f'X: {self.x} | Y: {self.y} | Directions: {self.possible_directions} | Dead End: {self.is_dead_end} | Distance: {self.distance_from_end}'
