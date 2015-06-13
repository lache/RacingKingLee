import math

class car:

    id = None
    token = None
    
    name = None
    color = None
    type = None

    x = 0
    y = 0
    angle = 0
    accel = 0

    def __init__(self, name, color, type):
        self.name = name
        self.color = color
        self.type = type

    def drive(self, angle, accel):
        self.angle = angle
        self.accel = accel

    def get_info(self):
        return (self.name, self.color, self.type)
    
    def get_pos(self):
        return (self.x, self.y, self.angle, self.accel)

    def move_tick(self, tick_count):

        x = self.x
        y = self.y
        angle = self.angle
        accel = self.accel

        ratio = accel * 16.0 / (60 * 60.0)
        x = x + ratio * math.cos(math.radians(270 - angle))
        y = y + ratio * math.sin(math.radians(270 - angle))

        if accel > 0:
            accel -= tick_count / 100.0
        elif accel < 0:
            accel += tick_count / 100.0

        self.x = x
        self.y = y
        self.accel = accel

