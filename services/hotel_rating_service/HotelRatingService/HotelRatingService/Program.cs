using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

namespace HotelRatingService
{
    public class Program
    {
        public static async Task RegisterOnServiceDiscovery()
        {
            using (var client = new HttpClient())
            {
                {
                    object payload = new
                    {
                        service_id = "hotel_rating_service1",
                        name = "hotel_rating",
                        port = 21162,
                        host = "localhost"
                    };

                    // Serialize our concrete class into a JSON String
                    var stringPayload = JsonConvert.SerializeObject(payload);
                    Console.WriteLine($"Service Discovery payload: {stringPayload}");

                    // Wrap our JSON inside a StringContent which then can be used by the HttpClient class
                    var content = new StringContent(stringPayload, Encoding.UTF8, "application/json");
                    var result = await client.PostAsJsonAsync("http://localhost:8005/register", payload);

                    Console.WriteLine($"Service discovery response code: {result.StatusCode}");
                }
            }
        }


        public static void Main(string[] args)
        {
            RegisterOnServiceDiscovery().Wait();
            CreateHostBuilder(args).Build().Run();
        }

        public static IHostBuilder CreateHostBuilder(string[] args) =>
            Host.CreateDefaultBuilder(args)
                .ConfigureWebHostDefaults(webBuilder =>
                {
                    webBuilder.UseStartup<Startup>();
                })
                .ConfigureLogging((hostingContext, logging) => {
                    logging.AddConfiguration(hostingContext.Configuration.GetSection("Logging"));
                    logging.AddConsole();
                    logging.AddDebug();
                    logging.AddEventSourceLogger();
                });
    }
}
