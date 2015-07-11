using core;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace viewer
{
    public partial class Viewer : Form
    {
        private Car car = new Car();

        protected override CreateParams CreateParams
        {
            get
            {
                var cp = base.CreateParams;
                cp.ExStyle |= 0x02000000;    // Turn on WS_EX_COMPOSITED
                return cp;
            }
        }

        public Viewer()
        {
            InitializeComponent();
        }

        private void Viewer_KeyUp(object sender, KeyEventArgs e)
        {
            Keys key = e.KeyCode;
            if (key == Keys.Up)	// throttle up
            {
                if (car.throttle < 100)
                    car.throttle += 10;
            }
            else if (key == Keys.Down) // throttle down
            {
                if (car.throttle >= 10)
                    car.throttle -= 10;
            }

            if (key == Keys.S)	// brake
            {
                car.brake = 100;
                car.throttle = 0;
            }
            else
                car.brake = 0;

            if (key == Keys.Left)
            {
                if (car.steerAngle > -RacingEnvironment.M_PI / 4.0)
                    car.steerAngle -= RacingEnvironment.M_PI / 32.0f;
            }
            else if (key == Keys.Right)
            {
                if (car.steerAngle < RacingEnvironment.M_PI / 4.0)
                    car.steerAngle += RacingEnvironment.M_PI / 32.0f;
            }

            if (key == Keys.R)
                car.rearSlip = 1;
            if (key == Keys.F)
                car.frontSlip = 1;
            if (key == Keys.Space)
            {
                car.rearSlip = 1;
                car.frontSlip = 1;
            }
        }

        private void Viewer_Paint(object sender, PaintEventArgs e)
        {

            Graphics g = e.Graphics;

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

            corners[0].x = -car.type.width / 2;
            corners[0].y = -car.type.length / 2;

            corners[1].x = car.type.width / 2;
            corners[1].y = -car.type.length / 2;

            corners[2].x = car.type.width / 2;
            corners[2].y = car.type.length / 2;

            corners[3].x = -car.type.width / 2;
            corners[3].y = car.type.length / 2;

            float sn = (float)System.Math.Sin(car.angle);
            float cs = (float)System.Math.Cos(car.angle);

            for (int i = 0; i <= 3; i++)
            {
                w[i].x = cs * corners[i].x - sn * corners[i].y;
                w[i].y = sn * corners[i].x + cs * corners[i].y;
                corners[i].x = w[i].x;
                corners[i].y = w[i].y;
            }

            float scale = 10.0f;
            Vector screen_pos = new Vector();
            screen_pos.x = (float)(car.positionWC.x * scale + Width / 2.0);
            screen_pos.y = (float)(-car.positionWC.y * scale + Height / 2.0);

            for (int i = 0; i <= 3; i++)
            {
                corners[i].x *= scale;
                corners[i].y *= scale;
                corners[i].x += screen_pos.x;
                corners[i].y += screen_pos.y;
            }

            Pen pen = new Pen(color);
            g.DrawLine(pen, (float)corners[0].x, (float)corners[0].y, (float)corners[1].x, (float)corners[1].y);
            g.DrawLine(pen, (float)corners[1].x, (float)corners[1].y, (float)corners[2].x, (float)corners[2].y);
            g.DrawLine(pen, (float)corners[2].x, (float)corners[2].y, (float)corners[3].x, (float)corners[3].y);
            g.DrawLine(pen, (float)corners[3].x, (float)corners[3].y, (float)corners[0].x, (float)corners[0].y);


            color = Color.FromArgb(0, 0, 160);

            // wheels: 0=fr left, 1=fr right, 2 =rear right, 3=rear left

            wheels[0].x = -car.type.width / 2;
            wheels[0].y = -car.type.b;

            wheels[1].x = car.type.width / 2;
            wheels[1].y = -car.type.b;

            wheels[2].x = car.type.width / 2;
            wheels[2].y = car.type.c;

            wheels[3].x = -car.type.width / 2;
            wheels[3].y = car.type.c;


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
            g.DrawLine(pen, 
                (float)wheels[0].x, (float)wheels[0].y,
                (float)wheels[0].x - (float)System.Math.Cos(car.angle + car.steerAngle) * 100,
                (float)wheels[0].y - (float)System.Math.Sin(car.angle + car.steerAngle) * 100);
            g.DrawLine(pen,
                (float)wheels[3].x, (float)wheels[3].y,
                (float)wheels[3].x - (float)System.Math.Cos(car.angle) * 100,
                (float)wheels[3].y - (float)System.Math.Sin(car.angle) * 100);
        }

        private void ticker_Tick(object sender, System.EventArgs e)
        {
            Invalidate(false);
            car.simulate(0.01);
        }
    }
}
