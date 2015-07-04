using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace CSharp
{
    public partial class Simulator : Form
    {
        private Car car = new Car();

        public Simulator()
        {
            InitializeComponent();
        }

        private void ticker_Tick(object sender, EventArgs e)
        {
            car.simulate(0.01f);
            Invalidate();
        }

        private void Simulator_KeyUp(object sender, KeyEventArgs e)
        {
            car.keypress(e);
        }

        private void Simulator_Paint(object sender, PaintEventArgs e)
        {
            car.render(e.Graphics, this);
        }
    }
}
