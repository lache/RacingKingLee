using Nancy;
using Nancy.Hosting.Self;
using Nancy.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Text;
using System.Threading;

namespace api_server
{
    public enum ServiceType
    {
        NancyFX,
        AsyncServer,
    }

    public class ApiService
    {
        private ServiceType type = ServiceType.NancyFX;

        public ApiService(ServiceType type)
        {
            this.type = type;
        }

        public void start()
        {
            switch (type)
            {
                case ServiceType.NancyFX:
                    startNancy();
                    break;
                case ServiceType.AsyncServer:
                    startAsync();
                    break;
            }
        }

        private void startNancy()
        {
            Thread simulator = new Thread(new ThreadStart(ArenaApiModule.arena.run));
            simulator.Start();

            var uri = new Uri("http://localhost:9999");

            using (var host = new NancyHost(uri))
            {
                host.Start();

                Console.WriteLine("Your application is running on " + uri);
                Console.WriteLine("Press any [Enter] to close the host.");
                Console.ReadLine();
            }
        }

        private void startAsync()
        {
            Thread simulator = new Thread(new ThreadStart(AsyncServer.arena.run));
            simulator.Start();
            
            var server = new AsyncServer();
            server.start();
        }
    }

    public class ArenaApiModule : NancyModule
    {
        public static Arena arena = new Arena();
        public static string[] carPosArray = new string[10];
        public static int currentCarPos = 0;

        public ArenaApiModule()
        {
            /**
             * @api {get} /join/:name/:color/:type Join to arena
             * @apiName join
             * @apiGroup arena
             * @apiParam {string} name name of your car
             * @apiParam {string} color color of your car
             * @apiParam {string} type type of your car
             *
             * @apiSuccess {string} result success
             * @apiSuccess {string} token unique ID to control your car.
             * @apiError {string} result error
             * @apiError {string} message error description
             */
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
                if (token == null)
                {
                    result["result"] = "error";
                    result["message"] = "maximum number of player";
                    return new JavaScriptSerializer().Serialize(result);
                }
                result["token"] = token;
                result["result"] = "success";

                return new JavaScriptSerializer().Serialize(result);
            };

            /**
             * @api {get} /car_pos Get positions of all cars
             * @apiName car_pos
             * @apiGroup arena
             *
             * @apiSuccess {array} none Array of json "id:position" where each position consist of "x, y, angle, accel"
             * @apiSuccess {x} x position of x Axis
             * @apiSuccess {y} y position of y Axis
             * @apiSuccess {angle} angle radian. angle of car
             * @apiSuccess {accel} accel current acceleration power
             * 
             */
            Get["/car_pos"] = _ =>
            {
                return carPosArray[currentCarPos];
            };

            /**
             * @api {get} /car_info Get information of all cars
             * @apiName car_info
             * @apiGroup arena
             *
             * @apiSuccess {array} none Array of json "id:information" where each information consist of "name, color, type"
             */
            Get["/car_info"] = _ =>
            {
                return new JavaScriptSerializer().Serialize(arena.carInfoDict);
            };

            /**
             * @api {get} /accel/:token/:relativeThrottle Control your accelerator
             * @apiName accel
             * @apiGroup arena
             * @apiParam {string} token When you join this arena, a token is given. Use that!
             * @apiParam {int} relativeThrottle Relative control of your accelerator. Server accumlates your relativeThrottle to your current accelerator.
             *
             * @apiSuccess {string} result success
             * @apiError {string} result error
             * @apiError {string} message error description
             */
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

            /**
             * @api {get} /handle/:token/:relativeAngle Control your handle
             * @apiName handle
             * @apiGroup arena
             * @apiParam {string} token When you join this arena, a token is given. Use that!
             * @apiParam {int} relativeAngle Radian. Relative angle of your handle. Server accumlates your relativeAngle to your current angle of handle.
             *
             * @apiSuccess {string} result success
             * @apiError {string} result error
             * @apiError {string} message error description
             */
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

            /**
             * @api {get} /brake/:token Stop your car
             * @apiName brake
             * @apiGroup arena
             * @apiParam {string} token When you join this arena, a token is given. Use that!
             *
             * @apiSuccess {string} result success
             * @apiError {string} result error
             * @apiError {string} message error description
             */
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

    public class AsyncServer
    {
        public static Arena arena = new Arena();

        public void start()
        {
            var listener = new HttpListener();

            listener.Prefixes.Add("http://localhost:9999/");
            listener.Prefixes.Add("http://127.0.0.1:9999/");
            listener.Start();

            while (true)
            {
                try
                {
                    var context = listener.GetContext();
                    ThreadPool.QueueUserWorkItem(o => HandleRequest(context));
                }
                catch (Exception)
                {
                    // Ignored for this example
                }
            }
        }

        private void HandleRequest(object state)
        {
            try
            {
                var context = (HttpListenerContext)state;

                context.Response.StatusCode = 200;
                context.Response.StatusDescription = "OK";

                while (true)
                {
                    string[] segments = context.Request.Url.Segments;
                    switch (segments[1].ToLower().Replace("/", ""))
                    {
                        case "join":
                            HandleJoin(context);
                            break;
                        case "car_pos":
                            HandleCarPos(context);
                            break;
                        case "car_info":
                            HandleCarInfo(context);
                            break;
                        case "accel":
                            HandleAccel(context);
                            break;
                        case "handle":
                            HandleHandle(context);
                            break;
                        case "brake":
                            HandleBrake(context);
                            break;
                    }
                }
            }
            catch (Exception)
            {
                // Client disconnected or some other error - ignored for this example
            }
        }

        private void HandleJoin(HttpListenerContext context)
        {
            Dictionary<string, string> result = new Dictionary<string, string>();
            
            string[] segments = context.Request.Url.Segments;

            if (segments.Length != 5)
            {
                result["result"] = "error";
                result["message"] = "Invalid request. Url must be /join/:name/:color/:type";
            }
            else
            {
                string name = segments[2].Replace("/", "");
                string color = segments[3].Replace("/", "");
                string type = segments[4].Replace("/", "");

                if (name.Length == 0)
                {
                    result["result"] = "error";
                    result["message"] = "name is empty";
                }
                else if (color.Length == 0)
                {
                    result["result"] = "error";
                    result["message"] = "color is empty";
                }
                else if (type.Length == 0)
                {
                    result["result"] = "error";
                    result["message"] = "type is empty";
                }
                else
                {
                    string token = arena.register(name, color, type);
                    result["result"] = "success";
                    result["token"] = token;
                }
            }

            var bytes = Encoding.UTF8.GetBytes(new JavaScriptSerializer().Serialize(result));
            context.Response.OutputStream.Write(bytes, 0, bytes.Length);
            context.Response.OutputStream.Close();
            context.Response.Close();
        }

        private void HandleCarPos(HttpListenerContext context)
        {
            var bytes = Encoding.UTF8.GetBytes(ArenaApiModule.carPosArray[ArenaApiModule.currentCarPos]);
            context.Response.OutputStream.Write(bytes, 0, bytes.Length);
            context.Response.OutputStream.Close();
            context.Response.Close();
        }

        private void HandleCarInfo(HttpListenerContext context)
        {
            var bytes = Encoding.UTF8.GetBytes(new JavaScriptSerializer().Serialize(arena.carInfoDict));
            context.Response.OutputStream.Write(bytes, 0, bytes.Length);
            context.Response.OutputStream.Close();
            context.Response.Close();
        }

        private void HandleAccel(HttpListenerContext context)
        {
            Dictionary<string, string> result = new Dictionary<string, string>();

            string[] segments = context.Request.Url.Segments;

            if (segments.Length != 4)
            {
                result["result"] = "error";
                result["message"] = "Invalid request. Url must be /accel/:token/:relativeThrottle";
            }
            else
            {
                string token = segments[2].Replace("/", "");
                string relativeThrottle = segments[3].Replace("/", "");

                if (token.Length == 0)
                {
                    result["result"] = "error";
                    result["message"] = "token is empty";
                }
                else if (relativeThrottle.Length == 0)
                {
                    result["result"] = "error";
                    result["message"] = "relativeThrottle is empty";
                }
                else
                {
                    arena.operationQueue.Enqueue("accel:" + token + ":" + relativeThrottle);
                    result["result"] = "success";
                }
            }

            var bytes = Encoding.UTF8.GetBytes(new JavaScriptSerializer().Serialize(result));
            context.Response.OutputStream.Write(bytes, 0, bytes.Length);
            context.Response.OutputStream.Close();
            context.Response.Close();
        }

        private void HandleHandle(HttpListenerContext context)
        {
            Dictionary<string, string> result = new Dictionary<string, string>();

            string[] segments = context.Request.Url.Segments;

            if (segments.Length != 4)
            {
                result["result"] = "error";
                result["message"] = "Invalid request. Url must be /handle/:token/:relativeAngle";
            }
            else
            {
                string token = segments[2].Replace("/", "");
                string relativeAngle = segments[3].Replace("/", "");

                if (token.Length == 0)
                {
                    result["result"] = "error";
                    result["message"] = "token is empty";
                }
                else if (relativeAngle.Length == 0)
                {
                    result["result"] = "error";
                    result["message"] = "relativeAngle is empty";
                }
                else
                {
                    arena.operationQueue.Enqueue("handle:" + token + ":" + relativeAngle);
                    result["result"] = "success";
                }
            }

            var bytes = Encoding.UTF8.GetBytes(new JavaScriptSerializer().Serialize(result));
            context.Response.OutputStream.Write(bytes, 0, bytes.Length);
            context.Response.OutputStream.Close();
            context.Response.Close();
        }

        private void HandleBrake(HttpListenerContext context)
        {
            Dictionary<string, string> result = new Dictionary<string, string>();

            string[] segments = context.Request.Url.Segments;

            if (segments.Length != 3)
            {
                result["result"] = "error";
                result["message"] = "Invalid request. Url must be /brake/:token";
            }
            else
            {
                string token = segments[2].Replace("/", "");

                if (token.Length == 0)
                {
                    result["result"] = "error";
                    result["message"] = "token is empty";
                }
                else
                {
                    arena.operationQueue.Enqueue("brake:" + token);
                    result["result"] = "success";
                }
            }

            var bytes = Encoding.UTF8.GetBytes(new JavaScriptSerializer().Serialize(result));
            context.Response.OutputStream.Write(bytes, 0, bytes.Length);
            context.Response.OutputStream.Close();
            context.Response.Close();
        }
    }
}
