using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace core
{
    public class Vector
    {
        public double x;
        public double y;

        public Vector()
        {
        }

        public Vector (double x, double y)
        {
            this.x = x;
            this.y = y;
        }

        public string ToString()
        {
            return x.ToString() + "," + y.ToString();
        }
    }
}
