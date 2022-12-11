using Microsoft.AspNetCore.Http;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Threading.Tasks;

namespace Gateway
{
    public class CustomAuthenticationMiddleware
    {
        private readonly RequestDelegate _next;

        public CustomAuthenticationMiddleware(RequestDelegate next)
        {
            _next = next;
        }

        public async Task InvokeAsync(HttpContext context)
        {
            var token = context.Request.Headers["Authorization"];

            if (!string.IsNullOrWhiteSpace(token))
            {
                Console.WriteLine("JWT token in header");
                using (var client = new HttpClient())
                {
                    try
                    {
                        client.DefaultRequestHeaders.Add("Authorization", token.ToString());

                        Console.WriteLine("Before response creation...");
                        //HttpResponseMessage response = await client.PostAsync("http://localhost:8000/verify", new StringContent(String.Empty));
                        HttpResponseMessage response = await client.PostAsync("http://authentication_server:8000/verify", new StringContent(String.Empty));
                        Console.WriteLine("After response creation...");

                        response.EnsureSuccessStatusCode();
                        string responseBody = await response.Content.ReadAsStringAsync();

                        Console.WriteLine("Response body auth middleware:");
                        Console.WriteLine(responseBody);
                        Console.WriteLine("...\n\n\n\n");
                    } catch(HttpRequestException e)
                    {
                        Console.WriteLine("error auth middleware: " + e.ToString());
                        context.Request.Headers.Remove("Authorization");
                    } catch (Exception e)
                    {
                        Console.WriteLine(e.ToString());
                        Console.WriteLine(e.Message);
                        Console.WriteLine("...\n\n\n");
                    }
                }
            }

            await _next(context);
        }
    }
}
