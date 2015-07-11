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
    public class ArenaApiModule : NancyModule
    {
        private static Arena arena = new Arena();

        public ArenaApiModule()
        {
            Get["/join/{name}/{color}/{type}"] = _ =>
            {
                Dictionary<string, string> result = new Dictionary<string, string>();

                string name = _.name;
                string color = _.color;
                string type = _.type;

                if (name.Length == 0)
                {
                    result["result"] = "error";
                    result["message"] = "name is empty";
                    return new JavaScriptSerializer().Serialize(result);
                }
                if (color.Length == 0)
                {
                    result["result"] = "error";
                    result["message"] = "color is empty";
                    return new JavaScriptSerializer().Serialize(result);
                }
                if (type.Length == 0)
                {
                    result["result"] = "error";
                    result["message"] = "type is empty";
                    return new JavaScriptSerializer().Serialize(result);
                }

                string token = arena.register(name, color, type);
                result["token"] = token;
                result["result"] = "success";

                return new JavaScriptSerializer().Serialize(result);
            };

            Get["/car_pos"] = _ =>
            {
                return new JavaScriptSerializer().Serialize(arena.carPosDict);
            };


            Get["/car_info"] = _ =>
            {
                return new JavaScriptSerializer().Serialize(arena.carInfoDict);
            };


            Get["/accel/{token}/{relativeThrottle}"] = _ =>
            {
                Dictionary<string, string> result = new Dictionary<string, string>();

                string token = _.token;
                string relativeThrottle = _.relativeThrottle;

                if (arena.validateToken(token) == false)
                {
                    result["result"] = "error";
                    result["message"] = "token is invalid";
                    return new JavaScriptSerializer().Serialize(result);
                }

                arena.operationQueue.Enqueue("accel:" + token + ":" + relativeThrottle);
                result["result"] = "success";
                return new JavaScriptSerializer().Serialize(result);
            };

            Get["/handle/{token}/{relativeAngle}"] = _ =>
            {
                Dictionary<string, string> result = new Dictionary<string, string>();

                string token = _.token;
                string relativeAngle = _.relativeAngle;

                if (arena.validateToken(token) == false)
                {
                    result["result"] = "error";
                    result["message"] = "token is invalid";
                    return new JavaScriptSerializer().Serialize(result);
                }

                arena.operationQueue.Enqueue("handle:" + token + ":" + relativeAngle);
                result["result"] = "success";
                return new JavaScriptSerializer().Serialize(result);
            };

            Get["/brake/{token}"] = _ =>
            {
                Dictionary<string, string> result = new Dictionary<string, string>();

                string token = _.token;

                if (arena.validateToken(token) == false)
                {
                    result["result"] = "error";
                    result["message"] = "token is invalid";
                    return new JavaScriptSerializer().Serialize(result);
                }

                arena.operationQueue.Enqueue("brake:" + _.token);
                result["result"] = "success";
                return new JavaScriptSerializer().Serialize(result);
            };

            Thread simulator = new Thread(new ThreadStart(arena.run));
            simulator.Start();
        }
    }

    public class Arena
    {
        public ConcurrentQueue<string> operationQueue = new ConcurrentQueue<string>();

        int curPlayer = 0;

        List<Player> playerList = new List<Player>();

        ConcurrentDictionary<string, int> tokenIdDict = new ConcurrentDictionary<string, int>();
        ConcurrentDictionary<int, string> idTokenDict = new ConcurrentDictionary<int, string>();

        public ConcurrentDictionary<string, string> carPosDict = new ConcurrentDictionary<string, string>();
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
            carPosDict[id.ToString()] = player.car.printPos();

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
                            playerList[id].car.angle += double.Parse(op[2]);
                            break;
                        case "brake":
                            playerList[id].car.throttle = 0;
                            playerList[id].car.brake = 100;
                            break;
                    }
                    counter++;
                }

                foreach (var id in Enumerable.Range(0, playerList.Count))
                {
                    var player = playerList[id];
                    player.car.simulate(0.001);
                    carPosDict[id.ToString()] = player.car.printPos();
                }

                Thread.Sleep(10);
            }
        }

        public bool validateToken(string token)
        {
            return tokenIdDict.Keys.Contains(token);
        }
    }
}
