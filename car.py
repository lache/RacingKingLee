import math
import time

class vector:
    x = 0.0
    y = 0.0

    def __init__(self):
        self.X = 0.0
        self.y = 0.0

    def __str__(self):
        return '{x:%s, y:%s}' % (self.x, self.y)

class car:

    # given by system
    id = None
    token = None
    # given by system - end
    
    # given by user
    name = None
    color = None
    type = None
    # given by user - end

    # external control variables
    steer_angle = 0.0
    throttle = 0
    brake = 0
    rear_slip = 0
    front_slip = 0
    # external control variables - end

    # external read variables - begin
    angle = 0.0
    position_wc = vector()
    # external read variables - end
    
    # car simulation variables
    velocity_wc = vector()
    angular_velocity = 0.0
    
    velocity = vector()
    acceleration_wc = vector()
    rot_angle = 0.0
    side_slip = 0.0
    slipangle_front = 0.0
    slipangle_rear = 0.0
    force = vector()
    resistance = vector()
    acceleration = vector()
    torque = 0.0
    angular_acceleration = 0.0
    sn = 0.0
    cs = 0.0
    yawspeed = 0.0
    weight = 0.0
    ftraction = vector()
    flatf = vector()
    flatr = vector()
    # car simulation variables - end
    
    ## car configuration
    b = 1.0
    c = 1.0
    wheel_base = 2.0        # b + c = 0.0
    h = 1.0
    mass = 1500        
    inertia = 1500
    width = 1.5
    length = 3.0            # must be > wheel_base
    wheel_length = 0.7
    wheel_width = 0.3
    ## car configuration - end
    
    ## constants
    PI = 3.14159265359
    DRAG = 5.0              # factor for air resistance (drag)     
    RESISTANCE = 30.0       # factor for rolling resistance 
    CA_R = -5.20	           # cornering stiffness 
    CA_F = -5.0             # cornering stiffness 
    MAX_GRIP = 2.0          # maximum (normalised) friction force, =diameter of friction circle 
    ## constants - end
    

    def __init__(self, name, color, type):
        self.name = name
        self.color = color
        self.type = type

        self.steer_angle = 0.0
        self.throttle = 0
        self.brake = 0
        self.rear_slip = 0
        self.front_slip = 0
        self.angle = 0.0
        self.position_wc = vector()
        self.velocity_wc = vector()
        self.angular_velocity = 0.0
        self.velocity = vector()
        self.acceleration_wc = vector()
        self.rot_angle = 0.0
        self.side_slip = 0.0
        self.slipangle_front = 0.0
        self.slipangle_rear = 0.0
        self.force = vector()
        self.resistance = vector()
        self.acceleration = vector()
        self.torque = 0.0
        self.angular_acceleration = 0.0
        self.sn = 0.0
        self.cs = 0.0
        self.yawspeed = 0.0
        self.weight = 0.0
        self.ftraction = vector()
        self.flatf = vector()
        self.flatr = vector()

    def get_info(self):
        return (self.name, self.color, self.type)
    
    def get_pos(self):
        return (self.position_wc.x, self.position_wc.y, self.angle, self.steer_angle, self.throttle)

    def sign(self, val):
        if val >= 0.0:
            return 1.0
        return -1.0
        
    def move_tick(self, delta_t):

        self.sn = math.sin(self.angle)
        self.cs = math.cos(self.angle)

        if self.steer_angle != 0.0:
            breakme = 1

        # SAE convention: x is to the front of the car, y is to the right, z is down

        #    bangz: Velocity of Car. Vlat and Vlong
        # transform velocity in world reference frame to velocity in car reference frame
        self.velocity.x = self.cs * self.velocity_wc.y + self.sn * self.velocity_wc.x
        self.velocity.y = -self.sn * self.velocity_wc.y + self.cs * self.velocity_wc.x

        # Lateral force on wheels
        #    
        # Resulting velocity of the wheels as result of the yaw rate of the car body
        # v = yawrate * r where r is distance of wheel to CG (approx. half wheel base)
        # yawrate (ang.velocity) must be in rad/s
        #
        self.yawspeed = self.wheel_base * 0.5 * self.angular_velocity

        #bangz: velocity.x = fVLong_, velocity.y = fVLat_
        if self.velocity.x == 0:        # TODO: fix math.singularity
            self.rot_angle = 0
        else:
            self.rot_angle = math.atan2(self.yawspeed, self.velocity.x)

        # Calculate the side slip angle of the car (a.k.a. beta)
        if self.velocity.x == 0:        # TODO: fix math.singularity
            self.side_slip = 0
        else:
            self.side_slip = math.atan2(self.velocity.y, self.velocity.x)

        # Calculate slip angles for front and rear wheels (a.k.a. alpha)
        self.slipangle_front = self.side_slip + self.rot_angle - self.steer_angle
        self.slipangle_rear = self.side_slip - self.rot_angle

        # weight per axle = half car mass times 1G (=9.8m/s^2) 
        self.weight = self.mass * 9.8 * 0.5

        # lateral force on front wheels = (Ca * slip angle) capped to friction circle * load
        self.flatf.x = 0
        self.flatf.y = self.CA_F * self.slipangle_front
        self.flatf.y = min(self.MAX_GRIP, self.flatf.y)
        self.flatf.y = max(-self.MAX_GRIP, self.flatf.y)
        self.flatf.y *= self.weight
        if self.front_slip != 0:
            self.flatf.y *= 0.5

        # lateral force on rear wheels
        self.flatr.x = 0
        self.flatr.y = self.CA_R * self.slipangle_rear
        self.flatr.y = min(self.MAX_GRIP, self.flatr.y)
        self.flatr.y = max(-self.MAX_GRIP, self.flatr.y)
        self.flatr.y *= self.weight
        if self.rear_slip != 0:
            self.flatr.y *= 0.5

        # longtitudinal force on rear wheels - very simple traction model
        self.ftraction.x = 100 * (self.throttle - self.brake * self.sign(self.velocity.x))
        self.ftraction.y = 0
        if self.rear_slip != 0:
            self.ftraction.x *= 0.5

        # Forces and torque on body

        # drag and rolling resistance
        self.resistance.x = -(self.RESISTANCE * self.velocity.x + self.DRAG * self.velocity.x * abs(self.velocity.x))
        self.resistance.y = -(self.RESISTANCE * self.velocity.y + self.DRAG * self.velocity.y * abs(self.velocity.y))

        # sum forces
        self.force.x = self.ftraction.x + math.sin(self.steer_angle) * self.flatf.x + self.flatr.x + self.resistance.x
        self.force.y = self.ftraction.y + math.cos(self.steer_angle) * self.flatf.y + self.flatr.y + self.resistance.y

        # torque on body from lateral forces
        self.torque = self.b * self.flatf.y - self.c * self.flatr.y

        # Acceleration

        # Newton F = m.a, therefore a = F/m
        self.acceleration.x = self.force.x / self.mass
        self.acceleration.y = self.force.y / self.mass

        self.angular_acceleration = self.torque / self.inertia

        # Velocity and position

        # transform acceleration from car reference frame to world reference frame
        self.acceleration_wc.x = self.cs * self.acceleration.y + self.sn * self.acceleration.x
        self.acceleration_wc.y = -self.sn * self.acceleration.y + self.cs * self.acceleration.x

        # velocity is integrated acceleration
        #
        self.velocity_wc.x += delta_t * self.acceleration_wc.x
        self.velocity_wc.y += delta_t * self.acceleration_wc.y

        # position is integrated velocity
        #
        self.position_wc.x += delta_t * self.velocity_wc.x
        self.position_wc.y += delta_t * self.velocity_wc.y


        # Angular velocity and heading

        # integrate angular acceleration to get angular velocity
        #
        self.angular_velocity += delta_t * self.angular_acceleration

        # integrate angular velocity to get angular orientation
        #
        self.angle += delta_t * self.angular_velocity

    def __str__(self):
        return str(self.__dict__)

def main():
    my_car = car('john', 'red', 'truck')
    my_car.throttle = 10
    my_car.steer_angle = my_car.PI / 256.0
    for i in range(0, 100):
        my_car.move_tick(16.0 / 1000.0)

    print my_car.steer_angle
    print my_car.throttle
    print my_car.brake
    print my_car.rear_slip
    print my_car.front_slip
    print my_car.angle
    print my_car.position_wc
    print my_car.velocity_wc
    print my_car.angular_velocity
    print my_car.velocity
    print my_car.acceleration_wc
    print my_car.rot_angle
    print my_car.side_slip
    print my_car.slipangle_front
    print my_car.slipangle_rear
    print my_car.force
    print my_car.resistance
    print my_car.acceleration
    print my_car.torque
    print my_car.angular_acceleration
    print my_car.sn
    print my_car.cs
    print my_car.yawspeed
    print my_car.weight
    print my_car.ftraction
    print my_car.flatf
    print my_car.flatr


    return

    print car.PI
    
    while True:
        print
        my_car.move_tick(16.0 / 1000)
        time.sleep(1)
        print my_car.get_pos()
    
if __name__ == '__main__':
    main()
