using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.HttpsPolicy;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Microsoft.OpenApi.Models;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace HotelRatingService
{
    public class Startup
    {
        public Startup(IConfiguration configuration)
        {
            Configuration = configuration;
        }

        public IConfiguration Configuration { get; }

        // This method gets called by the runtime. Use this method to add services to the container.
        public void ConfigureServices(IServiceCollection services)
        {
            services.AddControllers();

            services.AddSwaggerGen(c => {
                c.SwaggerDoc("v1", new OpenApiInfo { Title = "HotelRating", Version = "v1" });
            });
            services.AddScoped<IRatingPredictionService, RatingPredictionService>();
            services.AddSingleton<WorkerPool>();
        }


        // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
        public void Configure(IApplicationBuilder app, IWebHostEnvironment env, IHostApplicationLifetime applicationLifetime)
        {
            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
                app.UseSwagger();
                app.UseSwaggerUI(c => c.SwaggerEndpoint("/swagger/v1/swagger.json", "HotelRating v1"));
            }

            app.UseHttpsRedirection();

            app.UseRouting();
            app.UseCors(configurePolicy => configurePolicy.AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader());

            app.UseAuthorization();

            app.UseEndpoints(endpoints =>
            {
                endpoints.MapControllers();
            });

            applicationLifetime.ApplicationStopping.Register(OnShutdown);
        }



        private async void OnShutdown()
        {
            Console.WriteLine("On shotdown executing...");
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
    }
}
