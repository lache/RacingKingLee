import math
import time

class engine:

    c_m         = 500                           # car mass in kg
    c_drag      = 0.5 * 0.30 * 2.2 * 1.29       # resistance force
    c_rr        = 30 * 0.4257                   # rolling resistance - 30 times of c_drag

    v_u_head    = (0.7072, 0.7072)              # unit vector of car heading
    v_velocity  = (0, 0)                        # vector of velocity
    v_pos       = (0, 0)                        # position (x, y)

    f_traction  = (0, 0)                        # force of traction
    f_drag      = (0, 0)                        # force of drag
    f_rr        = (0, 0)                        # force of rolling resistance
    f_long      = (0, 0)                        # longitudinal force

    f_engine    = 0                             # force of engine - given by user

    def move_tick(self, tick_count):
        self.f_traction = [self.f_engine * x for x in self.v_u_head]
        print('self.f_traction', self.f_traction)

        v_mag = self.magnitude(self.v_velocity)
        self.f_drag = [-1 * self.c_drag * v_mag * x for x in self.v_velocity]
        print('self.f_drag', self.f_drag)

        self.f_rr = [-1 * self.c_rr * x for x in self.v_velocity]
        print('self.f_rr', self.f_rr)

        self.f_long = (self.f_traction[0] + self.f_drag[0] + self.f_rr[0],
                self.f_traction[1] + self.f_drag[1] + self.f_rr[1])
        print('self.f_long', self.f_long)

        a = [x / self.c_m for x in self.f_long]
        print('a', a)

        dt = 1.0 / 16
        v = [dt * x for x in a]
        print('v', v)
        self.v_velocity = (self.v_velocity[0] + v[0], self.v_velocity[1] + v[1])
        print('self.v_velocity', self.v_velocity)

        p = [dt * x for x in v]
        self.v_pos = (self.v_pos[0] + p[0], self.v_pos[1] + p[1])
        print('self.v_pos', self.v_pos)

    def magnitude(self, elem):
        return math.sqrt(sum([x * x for x in elem]))


def main():
    e = engine()
    e.f_engine = 10

    for i in range(0, 10):
        e.move_tick(1)
        time.sleep(0.1)
        print('')
        print('')

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


if __name__ == '__main__':
    print('main')
    main()

e = engine()
e.f_engine = 50

def tick(cont):
    print('hehe')
    e.move_tick(1)
    cont.owner.position.x, cont.owner.position.y = e.v_pos[0] * 50, e.v_pos[1] * 50
    pass
