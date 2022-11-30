using Gateway.Exceptions;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Microsoft.OpenApi.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Text.Json;
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


            services.AddSwaggerGen(c => {
                c.SwaggerDoc("v1", new OpenApiInfo { Title = "BookExchange", Version = "v1" });

                c.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
                {
                    In = ParameterLocation.Header,
                    Description = "Please insert JWT with Bearer into field",
                    Name = "Authorization",
                    Type = SecuritySchemeType.ApiKey
                });
                c.AddSecurityRequirement(new OpenApiSecurityRequirement {
                       {
                         new OpenApiSecurityScheme
                         {
                           Reference = new OpenApiReference
                           {
                             Type = ReferenceType.SecurityScheme,
                             Id = "Bearer"
                           }
                          },
                          new string[] { }
                        }
                      });
            });

            services.AddMvc();
        }

        // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
        public void Configure(IApplicationBuilder app, IWebHostEnvironment env, ILoggerFactory loggerFactory, IHostApplicationLifetime applicationLifetime)
        {
            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
                app.UseSwagger();
                app.UseSwaggerUI(c => c.SwaggerEndpoint("/swagger/v1/swagger.json", "BookExchange v1"));
            }

            app.UseMiddleware<CustomAuthenticationMiddleware>();
            app.UseRouting();


            Router router = new Router("routes.json", loggerFactory);
            app.Run(async (context) =>
            {
                try
                {
                    var content = await router.RouteRequest(context.Request);

                    context.Response.StatusCode = (int) content.StatusCode;
                    await context.Response.WriteAsync(await content.Content.ReadAsStringAsync());
                }
                catch (ApiException e)
                {
                    Console.WriteLine("error:");
                    Console.WriteLine(e);
                    context.Response.StatusCode = StatusCodes.Status500InternalServerError;
                    context.Response.ContentType = "application/json";

                    string errorMessageJson = JsonSerializer.Serialize(new
                    {
                        error = e.Message
                    });

                    await context.Response.WriteAsync(errorMessageJson);
                }
            });

            app.UseEndpoints(endpoints =>
            {
                endpoints.MapGet("/", async context =>
                {

                    await context.Response.WriteAsync("Hello World!");
                });
            });

            applicationLifetime.ApplicationStopping.Register(OnShutdown);
        }


        private void OnShutdown()
        {
            Console.WriteLine("On shutdown executing...\n\n\n...\n\n...\n\n");
           /* using (var client = new HttpClient())
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
            }*/
        }
    }
}
