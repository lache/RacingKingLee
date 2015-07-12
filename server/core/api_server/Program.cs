namespace api_server
{
    using System;
    using Nancy.Hosting.Self;

    class Program
    {
        static void Main(string[] args)
        {
            var service = new ApiService(ServiceType.AsyncServer);
            service.start();
        }
    }
}
