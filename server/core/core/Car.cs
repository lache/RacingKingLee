using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace core
{
    public class CarType
    {
        public double wheelBase;
        public double b;
        public double c;
        public double h;
        public double mass;
        public double inertia;
        public double length;
        public double width;
        public double wheelLength;
        public double wheelWidth;

        public CarType()
        {
            // initialize car type
            b = 1.0f;					// m							
            c = 1.0f;					// m
            wheelBase = b + c;
            h = 1.0f;					// m
            mass = 1500;				// kg			
            inertia = 1500;			// kg.m			
            width = 1.5f;				// m
            length = 3.0f;				// m, must be > wheelBase
            wheelLength = 0.7f;
            wheelWidth = 0.3f;
        }
    }

    public class Car
    {
        // external read variables - begin
        public CarType type;
        public double angle;
        public Vector positionWC;
        // external read variables - end

        Vector velocityWC;

        double angularVelocity;

        // external control variables - begin
        public double steerAngle;
        public double throttle;
        public double brake;
        public int rearSlip;
        public int frontSlip;
        // external control variables - end

        Vector velocity;
        Vector accelerationWC;
        double rotAngle;
        double sideSlip;
        double slipangleFront;
        double slipangleRear;
        Vector force;
        Vector resistance;
        Vector acceleration;
        double torque;
        double angularAcceleration;
        double sn;
        double cs;
        double yawspeed;
        double weight;
        Vector ftraction;
        Vector flatf;
        Vector flatr;

        public Car()
        {
            type = new CarType();
            positionWC = new Vector();
            velocityWC = new Vector();
            velocity = new Vector();
            accelerationWC = new Vector();
            force = new Vector();
            resistance = new Vector();
            acceleration = new Vector();
            ftraction = new Vector();
            flatf = new Vector();
            flatr = new Vector();

            // initialize car type
            type.b = 1.0f;					// m							
            type.c = 1.0f;					// m
            type.wheelBase = type.b + type.c;
            type.h = 1.0f;					// m
            type.mass = 1500;				// kg			
            type.inertia = 1500;			// kg.m			
            type.width = 1.5f;				// m
            type.length = 3.0f;				// m, must be > wheelBase
            type.wheelLength = 0.7f;
            type.wheelWidth = 0.3f;

            steerAngle = 0;
            throttle = 0;
            brake = 0;
            rearSlip = 0;
            frontSlip = 0;
        }

        double sign(double val)
        {
            return (val >= 0) ? 1 : -1;
        }

        public void simulate(double delta_t)
        {
            Console.WriteLine("simulate");

            sn = (double)Math.Sin(angle);
            cs = (double)Math.Cos(angle);

            if (steerAngle != 0.0f)
            {
                int breakme = 1;
            }

            // SAE convention: x is to the front of the car, y is to the right, z is down

            //	bangz: Velocity of Car. Vlat and Vlong
            // transform velocity in world reference frame to velocity in car reference frame
            velocity.x = cs * velocityWC.y + sn * velocityWC.x;
            velocity.y = -sn * velocityWC.y + cs * velocityWC.x;

            // Lateral force on wheels
            //	
            // Resulting velocity of the wheels as result of the yaw rate of the car body
            // v = yawrate * r where r is distance of wheel to CG (approx. half wheel base)
            // yawrate (ang.velocity) must be in rad/s
            //
            yawspeed = type.wheelBase * 0.5f * angularVelocity;

            //bangz: velocity.x = fVLong_, velocity.y = fVLat_
            if (velocity.x == 0)		// TODO: fix singularity
                rotAngle = 0;
            else
                rotAngle = (double)Math.Atan2(yawspeed, velocity.x);

            // Calculate the side slip angle of the car (a.k.a. beta)
            if (velocity.x == 0)		// TODO: fix singularity
                sideSlip = 0;
            else
                sideSlip = (double)Math.Atan2(velocity.y, velocity.x);

            // Calculate slip angles for front and rear wheels (a.k.a. alpha)
            slipangleFront = sideSlip + rotAngle - steerAngle;
            slipangleRear = sideSlip - rotAngle;

            // weight per axle = half car mass times 1G (=9.8m/s^2) 
            weight = type.mass * 9.8f * 0.5f;

            // lateral force on front wheels = (Ca * slip angle) capped to friction circle * load
            flatf.x = 0;
            flatf.y = Environment.CA_F * slipangleFront;
            flatf.y = Math.Min(Environment.MAX_GRIP, flatf.y);
            flatf.y = Math.Max(-Environment.MAX_GRIP, flatf.y);
            flatf.y *= weight;
            if (frontSlip != 0)
                flatf.y *= 0.5f;

            // lateral force on rear wheels
            flatr.x = 0;
            flatr.y = Environment.CA_R * slipangleRear;
            flatr.y = Math.Min(Environment.MAX_GRIP, flatr.y);
            flatr.y = Math.Max(-Environment.MAX_GRIP, flatr.y);
            flatr.y *= weight;
            if (rearSlip != 0)
                flatr.y *= 0.5f;

            // longtitudinal force on rear wheels - very simple traction model
            ftraction.x = 100 * (throttle - brake * sign(velocity.x));
            ftraction.y = 0;
            if (rearSlip != 0)
                ftraction.x *= 0.5f;

            // Forces and torque on body

            // drag and rolling resistance
            resistance.x = -(Environment.RESISTANCE * velocity.x + Environment.DRAG * velocity.x * Math.Abs(velocity.x));
            resistance.y = -(Environment.RESISTANCE * velocity.y + Environment.DRAG * velocity.y * Math.Abs(velocity.y));

            // sum forces
            force.x = ftraction.x + (double)Math.Sin(steerAngle) * flatf.x + flatr.x + resistance.x;
            force.y = ftraction.y + (double)Math.Cos(steerAngle) * flatf.y + flatr.y + resistance.y;

            // torque on body from lateral forces
            torque = type.b * flatf.y - type.c * flatr.y;

            // Acceleration

            // Newton F = m.a, therefore a = F/m
            acceleration.x = force.x / type.mass;
            acceleration.y = force.y / type.mass;

            angularAcceleration = torque / type.inertia;

            Console.WriteLine(angularAcceleration);

            // Velocity and position

            // transform acceleration from car reference frame to world reference frame
            accelerationWC.x = cs * acceleration.y + sn * acceleration.x;
            accelerationWC.y = -sn * acceleration.y + cs * acceleration.x;

            // velocity is integrated acceleration
            //
            velocityWC.x += delta_t * accelerationWC.x;
            velocityWC.y += delta_t * accelerationWC.y;

            // position is integrated velocity
            //
            positionWC.x += delta_t * velocityWC.x;
            positionWC.y += delta_t * velocityWC.y;


            // Angular velocity and heading

            // integrate angular acceleration to get angular velocity
            //
            angularVelocity += delta_t * angularAcceleration;

            // integrate angular velocity to get angular orientation
            //
            angle += delta_t * angularVelocity;
        }
    }
}
