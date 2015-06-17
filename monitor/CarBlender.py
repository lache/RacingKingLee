import math
import time


b = 1.0
c = 1.0
wheelbase = 1.0 + 1.0 # b + c
h = 1.0
mass = 1500.0
inertia = 1500.0
length = 3.0
width = 1.5
wheellength = 0.7
wheelwidth = 0.3

position_wc = (0, 0)
velocity_wc = (0, 0)

angle = 0.0
angularvelocity = 0.0

# input
steerangle = 0.0
throttle = 0.0
brake = 0.0


velocity = (0, 0)
acceleration_wc = (0, 0)
rot_angle = 0
sideslip = 0
slipanglefront = 0
slipanglerear = 0
force = (0, 0)
rear_slip = 0
front_slip = 0
resistance = (0, 0)
acceleration = (0, 0)
torque = 0
angular_acceleration = 0
sn = 0
cs = 0
yawspeed = 0
weight = 0
ftraction = (0, 0)
flatf = (0, 0)
flatr = (0, 0)

DRAG = 5.0
RESISTANCE = 30.0
CA_R = -5.20
CA_F = -5.0
MAX_GRIP = 2.0



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
        global sn
        global cs
        global velocity
        global yawspeed
        global wheelbase
        global angularvelocity
        global rot_angle
        global sideslip
        global slipanglefront
        global slipanglerear
        global steerangle
        global weight
        global mass
        global front_slip
        global rear_slip
        global ftraction
        global throttle
        global resistance
        global force
        global torque
        global b
        global c
        global acceleration
        global inertia
        global angular_acceleration
        global acceleration_wc
        global velocity_wc
        global position_wc
        global angle
        global flatf
        global flatr

        global CA_F
        global CA_R
        global MAX_GRIP
        global RESISTANCE
        global DRAG
        
        
        sn = math.sin(angle)
        cs = math.cos(angle)
        
        
        velocity_x = cs * velocity_wc[1] + sn * velocity_wc[0]
        velocity_y = -sn * velocity_wc[1] + cs * velocity_wc[0]
        
        velocity = (velocity_x, velocity_y)
        
        yawspeed = wheelbase * 0.5 * angularvelocity
        
        if velocity_x == 0:
            rot_angle = 0
        else:
            rot_angle = math.atan2(yawspeed, velocity_x)
            
        if velocity_x == 0:
            sideslip = 0
        else:
            sideslip = math.atan2(velocity_y, velocity_x)

        slipanglefront = sideslip + rot_angle - steerangle
        slipanglerear  = sideslip - rot_angle
        
        weight = mass * 9.8 * 0.5

        flatf_x = 0
        flatf_y = CA_F * slipanglefront
        flatf_y = min(MAX_GRIP, flatf_y)
        flatf_y = max(-MAX_GRIP, flatf_y)
        flatf_y *= weight;
        if front_slip != 0:
            flatf_y *= 0.5
        flatf = (flatf_x, flatf_y)
            
        flatr_x = 0
        flatr_y = CA_R * slipanglerear
        flatr_y = min(MAX_GRIP, flatr_y)
        flatr_y = max(-MAX_GRIP, flatr_y)
        flatr_y *= weight
        if rear_slip != 0:
            flatr_y *= 0.5
        flatr = (flatr_x, flatr_y)

        sgn = 0
        if velocity_x > 0:
            sgn = 1
        elif velocity_x < 0:
            sgn = -1
        ftraction_x = 100 * (throttle - brake * sgn)
        ftraction_y = 0
        if rear_slip!= 0:
            ftraction_x *= 0.5
        
        ftraction = (ftraction_x, ftraction_y)
        #print(ftraction)

        resistance_x = -1 * (RESISTANCE * velocity_x + DRAG * velocity_x * abs(velocity_x))
        resistance_y = -1 * (RESISTANCE * velocity_y + DRAG * velocity_y * abs(velocity_y))
        resistance = (resistance_x, resistance_y)
        
        force_x = ftraction_x + math.sin(steerangle) * flatf_x + flatr_x + resistance_x
        force_y = ftraction_y + math.cos(steerangle) * flatf_y + flatr_y + resistance_y
        force = (force_x, force_y)
        
        #print(flatf)
        #print(flatr)
        torque = b * flatf_y - c * flatr_y
        #print(torque)

        acceleration_x = force_x / mass
        acceleration_y = force_y / mass
        acceleration = (acceleration_x, acceleration_y)
        
        angular_acceleration = torque / inertia
        #print(angular_acceleration)

        acceleration_wc_x =  cs * acceleration_y + sn * acceleration_x
        acceleration_wc_y = -sn * acceleration_y + cs * acceleration_x
        acceleration_wc = (acceleration_wc_x, acceleration_wc_y)

        velocity_wc_x = velocity_wc[0] + tick_count * acceleration_wc_x
        velocity_wc_y = velocity_wc[1] + tick_count * acceleration_wc_y
        velocity_wc = (velocity_wc_x, velocity_wc_y)
        
        position_wc_x = position_wc[0] + tick_count * velocity_wc_x
        position_wc_y = position_wc[1] + tick_count * velocity_wc_y
        position_wc = (position_wc_x, position_wc_y)

        angularvelocity += tick_count * angular_acceleration
        angle += tick_count * angularvelocity 
        
        self.v_pos = position_wc


def main():
    print('hoho')
    global position_wc
    global throttle
    global velocity
    global steerangle
    
    throttle = 10
    
    e = engine()

    for i in range(0, 1000):
        e.move_tick(1.0)
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
throttle = 1

def tick(cont):
    global position_wc
    #print('hehe')
    e.move_tick(1.0 / 60.0)
    print(position_wc)
    cont.owner.position.x, cont.owner.position.y = position_wc[0] * 1, position_wc[1] * 1
    pass

def onUp():
    
    global throttle
    throttle += 1
    
    print('up')
    pass

def onDown():

    global throttle
    throttle -= 1

    print('down')
    pass

def onLeft():

    global steerangle
    steerangle -= 3.1415 / 32.0
    
    print('left')
    pass

def onRight():

    global steerangle
    steerangle += 3.1415 / 32.0


    print('right')
    pass
