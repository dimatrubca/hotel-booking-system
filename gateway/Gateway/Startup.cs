using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;



namespace Gateway
{
    public class Startup
    {
        // This method gets called by the runtime. Use this method to add services to the container.
        // For more information on how to configure your application, visit https://go.microsoft.com/fwlink/?LinkID=398940
        public void ConfigureServices(IServiceCollection services)
        {
            services.Configure<IISServerOptions>(options =>
            {
                options.AllowSynchronousIO = true;
            });
           // services.AddHttpClient().AddPol
        }

        // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
        public void Configure(IApplicationBuilder app, IWebHostEnvironment env, ILoggerFactory loggerFactory)
        {
            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
            }

            app.UseMiddleware<CustomAuthenticationMiddleware>();
            app.UseRouting();


            Router router = new Router("routes.json");
            app.Run(async (context) =>
            {
                var content = await router.RouteRequest(context.Request);
                //Console.WriteLine("Content!");
                //Console.WriteLine(content);
                //Console.WriteLine("Context:");
                //Console.Write(context);
               // dynamic res = await content.Content.ReadAsStringAsync();
               // Console.WriteLine(res);

                await context.Response.WriteAsync(await content.Content.ReadAsStringAsync());
            });

            app.UseEndpoints(endpoints =>
            {
                endpoints.MapGet("/", async context =>
                {

                    await context.Response.WriteAsync("Hello World!");
                });
            });
        }
    }
}
