using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using System;
using System.Web.Http;
using Gateway.Exceptions;
using System.IO;

namespace Gateway
{
    public class Program
    {
        public static void Main(string[] args)
        {
            Console.WriteLine("Inside Main in Program");

            CreateHostBuilder(args).Build().Run();
            GlobalConfiguration.Configuration.Filters.Add(new ApiExceptionFilter());
        }

        public static IHostBuilder CreateHostBuilder(string[] args) =>
            Host.CreateDefaultBuilder(args)
                .ConfigureWebHostDefaults(webBuilder =>
                {
                    webBuilder.UseStartup<Startup>()
                    .ConfigureKestrel((context, options) => 
                    {
                        options.AllowSynchronousIO = true;
                    });
                })
                .ConfigureLogging((hostingContext, logging) => {
                    logging.AddConfiguration(hostingContext.Configuration.GetSection("Logging"));
                    logging.AddConsole();
                    logging.AddDebug();
                    logging.AddEventSourceLogger();
                    logging.AddFile($@"Logs/log.txt");

                    //logging.AddFile($@"{Directory.GetCurrentDirectory()}\Logs\log.txt");
                });
    }
}
