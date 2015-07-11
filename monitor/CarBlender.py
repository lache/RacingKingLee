import math
import time
from math import radians

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
steerangle = 0
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
C_RESISTANCE = 30.0
CA_R = -5.20
CA_F = -5.0
MAX_GRIP = 2.0

keychaser = 0


class engine:

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
        global brake

        global CA_F
        global CA_R
        global MAX_GRIP
        global C_RESISTANCE
        global DRAG
        
        
        sn = math.sin(angle)
        cs = math.cos(angle)
        
        steerangle_t = steerangle * 3.1415926 / 320.0
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

        slipanglefront = sideslip + rot_angle - steerangle_t
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
        if velocity_x >= 0:
            sgn = 1
        elif velocity_x < 0:
            sgn = -1
        ftraction_x = 100 * (throttle - brake * sgn)
        ftraction_y = 0
        if rear_slip!= 0:
            ftraction_x *= 0.5
        
        ftraction = (ftraction_x, ftraction_y)
        #print(ftraction)

        resistance_x = -1 * (C_RESISTANCE * velocity_x + DRAG * velocity_x * abs(velocity_x))
        resistance_y = -1 * (C_RESISTANCE * velocity_y + DRAG * velocity_y * abs(velocity_y))
        resistance = (resistance_x, resistance_y)
        
        force_x = ftraction_x + math.sin(steerangle_t) * flatf_x + flatr_x + resistance_x
        force_y = ftraction_y + math.cos(steerangle_t) * flatf_y + flatr_y + resistance_y
        force = (force_x, force_y)
        
        print("force:", force)
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


		
def main():
    print('hoho')
    global position_wc
    global throttle
    global velocity
    global steerangle
    
    throttle = 0
    steerangle = 0.1
    
    e = engine()

    for i in range(0, 1000):
        e.move_tick(0.01)
        time.sleep(0.01)
        print(position_wc)
		
if __name__ == '__main__':
    print('main')
    main()

e = engine()
throttle = 0
rear_slip = 0
front_slip = 0

def tick(cont):
    global position_wc
    global angle
    global steerangle
	
    #print('hehe')
    e.move_tick(1.0 / 60.0)
    print(position_wc)
    print("angle: ", angle)
    print("steerangle: ", steerangle)
    cont.owner.position.x, cont.owner.position.y = position_wc[0] * 0.1, position_wc[1] * 0.1
    
    from mathutils import Euler
    cont.owner.localOrientation = Euler([0,0, angle]).to_matrix()    
    pass

def onUp():
    
    global throttle
    global brake
    throttle += 1
    brake = 0
    
    print('up')
    pass

def onDown():

    global throttle
    global brake
    throttle = 0
    brake = 100

    print('down')
    pass

def onLeft():

    global keychaser
    keychaser += 1
    if keychaser % 20 != 0:
        return
    else:
        keychaser = 0
	
    global steerangle
    if steerangle * 3.1415926 / 32.0 < 3.1415926 / 4.0:
        steerangle += 1
    
    print('left')
    pass

def onRight():

    global keychaser
    keychaser += 1
    if keychaser % 20 != 0:
        return
    else:
        keychaser = 0

    global steerangle
    if steerangle * 3.1415926 / 32.0 > - 3.1415926 / 4.0:
        steerangle -= 1

    print('right')
    pass
