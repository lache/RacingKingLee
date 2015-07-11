using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace CSharp
{
    static class Environment
    {
        public static readonly float M_PI = 3.1415926f;
        public static readonly float DRAG = 5.0f;		 		/* factor for air resistance (drag) 	*/
        public static readonly float RESISTANCE = 30.0f;		/* factor for rolling resistance */
        public static readonly float CA_R = -5.20f;			    /* cornering stiffness */
        public static readonly float CA_F = -5.0f;			    /* cornering stiffness */
        public static readonly float MAX_GRIP = 2.0f;			/* maximum (normalised) friction force, =diameter of friction circle */
    }

    class Vector
    {
        public float x;
        public float y;
    }

    class CarType
    {
        public float wheelbase;
        public float b;
        public float c;
        public float h;
        public float mass;
        public float inertia;
        public float length;
        public float width;
        public float wheellength;
        public float wheelwidth;
    }

    class Car
    {
        CarType type = new CarType();

        Vector position_wc = new Vector();
        Vector velocity_wc = new Vector();

        float angle;
        float angularvelocity;

        float steerangle;
        float throttle;
        float brake;

        float sin;
        float cos;

        /// <summary>
        Vector velocity = new Vector();
        Vector acceleration_wc = new Vector();
        float rot_angle;
        float sideslip;
        float slipanglefront;
        float slipanglerear;
        Vector force = new Vector();
        int rear_slip;
        int front_slip;
        Vector resistance = new Vector();
        Vector acceleration = new Vector();
        float torque;
        float angular_acceleration;
        float sn, cs;
        float yawspeed;
        float weight;
        Vector ftraction = new Vector();
        Vector flatf = new Vector();
        Vector flatr = new Vector();
        /// </summary>

        public Car()
        {
            // initialize car type
            type.b = 1.0f;					// m							
            type.c = 1.0f;					// m
            type.wheelbase = type.b + type.c;
            type.h = 1.0f;					// m
            type.mass = 1500;				// kg			
            type.inertia = 1500;			// kg.m			
            type.width = 1.5f;				// m
            type.length = 3.0f;				// m, must be > wheelbase
            type.wheellength = 0.7f;
            type.wheelwidth = 0.3f;
        }

        public void render(Graphics g, Simulator form)
        {
            Console.WriteLine("render");


            //
            // Draw car body
            //
            Color color = Color.FromArgb(160, 0, 0);

            // wheels: 0=fr left, 1=fr right, 2 =rear right, 3=rear left

            Vector[] corners = new Vector[4];
            Vector[] wheels = new Vector[4];
            Vector[] w = new Vector[4];
            for (int k = 0; k < corners.Length; k++)
            {
                corners[k] = new Vector();
                wheels[k] = new Vector();
                w[k] = new Vector();
            }

            corners[0].x = -type.width / 2;
            corners[0].y = -type.length / 2;

            corners[1].x = type.width / 2;
            corners[1].y = -type.length / 2;

            corners[2].x = type.width / 2;
            corners[2].y = type.length / 2;

            corners[3].x = -type.width / 2;
            corners[3].y = type.length / 2;

            float sn = (float)Math.Sin(angle);
            float cs = (float)Math.Cos(angle);

            for (int i = 0; i <= 3; i++)
            {
                w[i].x = cs * corners[i].x - sn * corners[i].y;
                w[i].y = sn * corners[i].x + cs * corners[i].y;
                corners[i].x = w[i].x;
                corners[i].y = w[i].y;
            }

            float scale = 10.0f;
            Vector screen_pos = new Vector();
            screen_pos.x = (float)(position_wc.x * scale + form.Width / 2.0);
            screen_pos.y = (float)(-position_wc.y * scale + form.Height / 2.0);

            for (int i = 0; i <= 3; i++)
            {
                corners[i].x *= scale;
                corners[i].y *= scale;
                corners[i].x += screen_pos.x;
                corners[i].y += screen_pos.y;
            }

            Pen pen = new Pen(color);
            g.DrawLine(pen, corners[0].x, corners[0].y, corners[1].x, corners[1].y);
            g.DrawLine(pen, corners[1].x, corners[1].y, corners[2].x, corners[2].y);
            g.DrawLine(pen, corners[2].x, corners[2].y, corners[3].x, corners[3].y);
            g.DrawLine(pen, corners[3].x, corners[3].y, corners[0].x, corners[0].y);





            color = Color.FromArgb(0, 0, 160);

            // wheels: 0=fr left, 1=fr right, 2 =rear right, 3=rear left

            wheels[0].x = -type.width / 2;
            wheels[0].y = -type.b;

            wheels[1].x = type.width / 2;
            wheels[1].y = -type.b;

            wheels[2].x = type.width / 2;
            wheels[2].y = type.c;

            wheels[3].x = -type.width / 2;
            wheels[3].y = type.c;


            for (int i = 0; i <= 3; i++)
            {
                w[i].x = cs * wheels[i].x - sn * wheels[i].y;
                w[i].y = sn * wheels[i].x + cs * wheels[i].y;
                wheels[i].x = w[i].x;
                wheels[i].y = w[i].y;
            }

            for (int i = 0; i <= 3; i++)
            {
                wheels[i].x *= scale;
                wheels[i].y *= scale;
                wheels[i].x += screen_pos.x;
                wheels[i].y += screen_pos.y;
            }


            // "wheel spokes" to show Ackermann centre of turn
            //
            g.DrawLine(pen, wheels[0].x, wheels[0].y,
                wheels[0].x - (float)Math.Cos(angle + steerangle) * 100,
                wheels[0].y - (float)Math.Sin(angle + steerangle) * 100);
            g.DrawLine(pen, wheels[3].x, wheels[3].y,
                wheels[3].x - (float)Math.Cos(angle) * 100,
                wheels[3].y - (float)Math.Sin(angle) * 100);
        }

        float SGN(float val)
        {
            return (val >= 0) ? 1 : -1;
        }

        internal void simulate(float delta_t)
        {
            Console.WriteLine("simulate");

            sn = (float)Math.Sin(angle);
            cs = (float)Math.Cos(angle);

            if (steerangle != 0.0f)
            {
                int breakme = 1;
            }

            // SAE convention: x is to the front of the car, y is to the right, z is down

            //	bangz: Velocity of Car. Vlat and Vlong
            // transform velocity in world reference frame to velocity in car reference frame
            velocity.x = cs * velocity_wc.y + sn * velocity_wc.x;
            velocity.y = -sn * velocity_wc.y + cs * velocity_wc.x;

            // Lateral force on wheels
            //	
            // Resulting velocity of the wheels as result of the yaw rate of the car body
            // v = yawrate * r where r is distance of wheel to CG (approx. half wheel base)
            // yawrate (ang.velocity) must be in rad/s
            //
            yawspeed = type.wheelbase * 0.5f * angularvelocity;

            //bangz: velocity.x = fVLong_, velocity.y = fVLat_
            if (velocity.x == 0)		// TODO: fix singularity
                rot_angle = 0;
            else
                rot_angle = (float)Math.Atan2(yawspeed, velocity.x);

            // Calculate the side slip angle of the car (a.k.a. beta)
            if (velocity.x == 0)		// TODO: fix singularity
                sideslip = 0;
            else
                sideslip = (float)Math.Atan2(velocity.y, velocity.x);

            // Calculate slip angles for front and rear wheels (a.k.a. alpha)
            slipanglefront = sideslip + rot_angle - steerangle;
            slipanglerear = sideslip - rot_angle;

            // weight per axle = half car mass times 1G (=9.8m/s^2) 
            weight = type.mass * 9.8f * 0.5f;

            // lateral force on front wheels = (Ca * slip angle) capped to friction circle * load
            flatf.x = 0;
            flatf.y = Environment.CA_F * slipanglefront;
            flatf.y = Math.Min(Environment.MAX_GRIP, flatf.y);
            flatf.y = Math.Max(-Environment.MAX_GRIP, flatf.y);
            flatf.y *= weight;
            if (front_slip != 0)
                flatf.y *= 0.5f;

            // lateral force on rear wheels
            flatr.x = 0;
            flatr.y = Environment.CA_R * slipanglerear;
            flatr.y = Math.Min(Environment.MAX_GRIP, flatr.y);
            flatr.y = Math.Max(-Environment.MAX_GRIP, flatr.y);
            flatr.y *= weight;
            if (rear_slip != 0)
                flatr.y *= 0.5f;

            // longtitudinal force on rear wheels - very simple traction model
            ftraction.x = 100 * (throttle - brake * SGN(velocity.x));
            ftraction.y = 0;
            if (rear_slip != 0)
                ftraction.x *= 0.5f;

            // Forces and torque on body

            // drag and rolling resistance
            resistance.x = -(Environment.RESISTANCE * velocity.x + Environment.DRAG * velocity.x * Math.Abs(velocity.x));
            resistance.y = -(Environment.RESISTANCE * velocity.y + Environment.DRAG * velocity.y * Math.Abs(velocity.y));

            // sum forces
            force.x = ftraction.x + (float)Math.Sin(steerangle) * flatf.x + flatr.x + resistance.x;
            force.y = ftraction.y + (float)Math.Cos(steerangle) * flatf.y + flatr.y + resistance.y;

            // torque on body from lateral forces
            torque = type.b * flatf.y - type.c * flatr.y;

            // Acceleration

            // Newton F = m.a, therefore a = F/m
            acceleration.x = force.x / type.mass;
            acceleration.y = force.y / type.mass;

            angular_acceleration = torque / type.inertia;

            Console.WriteLine(angular_acceleration);

            // Velocity and position

            // transform acceleration from car reference frame to world reference frame
            acceleration_wc.x = cs * acceleration.y + sn * acceleration.x;
            acceleration_wc.y = -sn * acceleration.y + cs * acceleration.x;

            // velocity is integrated acceleration
            //
            velocity_wc.x += delta_t * acceleration_wc.x;
            velocity_wc.y += delta_t * acceleration_wc.y;

            // position is integrated velocity
            //
            position_wc.x += delta_t * velocity_wc.x;
            position_wc.y += delta_t * velocity_wc.y;


            // Angular velocity and heading

            // integrate angular acceleration to get angular velocity
            //
            angularvelocity += delta_t * angular_acceleration;

            // integrate angular velocity to get angular orientation
            //
            angle += delta_t * angularvelocity;
        }

        internal void keypress(KeyEventArgs e)
        {
            Console.WriteLine("Keyup");

            Keys key = e.KeyCode;
            if (key == Keys.Up)	// throttle up
            {
                if (throttle < 100)
                    throttle += 10;
            }
            else if (key == Keys.Down) // throttle down
            {
                if (throttle >= 10)
                    throttle -= 10;
            }

            if (key == Keys.RControlKey)	// brake
            {
                brake = 100;
                throttle = 0;
            }
            else
                brake = 0;

            if (key == Keys.Left)
            {
                if (steerangle > -Environment.M_PI / 4.0)
                    steerangle -= Environment.M_PI / 32.0f;
            }
            else if (key == Keys.Right)
            {
                if (steerangle < Environment.M_PI / 4.0)
                    steerangle += Environment.M_PI / 32.0f;
            }
        }
    }


}
