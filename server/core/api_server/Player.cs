using core;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace api_server
{
    public class Player
    {
        public Car car = new Car();
        public string name;
        public string color;
        public string type;
        public string token;

        public Player(string name, string color, string type)
        {
            this.name = name;
            this.color = color;
            this.type = type;
        }

        public string ToString()
        {
            return string.Format("name={0},color={1},type={2}", name, color, type);
        }
    }
}
