using Nancy;
using Nancy.Json;
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;


namespace api_server
{
    public class Arena
    {
        public ConcurrentQueue<string> operationQueue = new ConcurrentQueue<string>();

        public int curPlayer = 0;

        List<Player> playerList = new List<Player>();

        ConcurrentDictionary<string, int> tokenIdDict = new ConcurrentDictionary<string, int>();
        ConcurrentDictionary<int, string> idTokenDict = new ConcurrentDictionary<int, string>();

        public ConcurrentDictionary<string, string> carInfoDict = new ConcurrentDictionary<string, string>();

        public string register(string name, string color, string type)
        {
            string token = Guid.NewGuid().ToString("D");

            int id = curPlayer;
            tokenIdDict[token] = id;
            idTokenDict[id] = token;
            curPlayer++;

            var player = new Player(name, color, type);
            playerList.Add(player);
            carInfoDict[id.ToString()] = player.ToString();

            return token;
        }

        public void run()
        {
            while (true)
            {
                int counter = 0;
                while (operationQueue.IsEmpty == false || counter >= 100)
                {
                    string operation = "";
                    if (operationQueue.TryDequeue(out operation) == false) continue;

                    string[] op = operation.Split(':');
                    string token = op[1];
                    int id = tokenIdDict[token];
                    switch (op[0])
                    {
                        case "accel":
                            playerList[id].car.throttle += double.Parse(op[2]);
                            playerList[id].car.brake = 0;
                            break;
                        case "handle":
                            playerList[id].car.steerAngle += double.Parse(op[2]);
                            break;
                        case "brake":
                            playerList[id].car.throttle = 0;
                            playerList[id].car.brake = 100;
                            break;
                    }
                    counter++;
                }

                StringBuilder result = new StringBuilder();
                result.Append("{");
                foreach (var id in Enumerable.Range(0, playerList.Count))
                {
                    var player = playerList[id];
                    player.car.simulate(0.001);

                    if (id == 0)
                    {
                        result.Append(string.Format("\"{0}\":\"{1},{2},{3},{4}\"",
                            id,
                            player.car.positionWC.x,
                            player.car.positionWC.y,
                            player.car.steerAngle,
                            player.car.throttle));
                    }
                    else
                    {
                        result.Append(string.Format(",\"{0}\":\"{1},{2},{3},{4}\"",
                            id,
                            player.car.positionWC.x,
                            player.car.positionWC.y,
                            player.car.steerAngle,
                            player.car.throttle));
                    }
                }
                result.Append("}");
                int pos = (ArenaApiModule.currentCarPos + 1) % ArenaApiModule.carPosArray.Length;
                ArenaApiModule.carPosArray[pos] = result.ToString();
                ArenaApiModule.currentCarPos = pos;

                Thread.Sleep(20);
            }
        }

        public bool validateToken(string token)
        {
            return tokenIdDict.Keys.Contains(token);
        }
    }
}
