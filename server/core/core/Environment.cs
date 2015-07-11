using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace core
{
    public static class Environment
    {
        public static readonly double M_PI = Math.PI;
        public static readonly double DRAG = 5.0f;		 		/* factor for air resistance (drag) 	*/
        public static readonly double RESISTANCE = 30.0f;		/* factor for rolling resistance */
        public static readonly double CA_R = -5.20f;			/* cornering stiffness */
        public static readonly double CA_F = -5.0f;			    /* cornering stiffness */
        public static readonly double MAX_GRIP = 2.0f;			/* maximum (normalised) friction force, =diameter of friction circle */
    }
}
