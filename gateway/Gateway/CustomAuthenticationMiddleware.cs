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
            var token = context.Request.Headers["authorization"];

            if (!string.IsNullOrWhiteSpace(token))
            {
                Console.WriteLine("JWT token in header");
                using (var client = new HttpClient())
                {
                    try
                    {
                        client.DefaultRequestHeaders.Add("authorization", token.ToString());

                        HttpResponseMessage response = await client.PostAsync("http://localhost:8001/test/verify", null);

                        response.EnsureSuccessStatusCode();
                        string responseBody = await response.Content.ReadAsStringAsync();

                        Console.WriteLine("Response body auth middleware:");
                        Console.WriteLine(responseBody);
                    } catch(HttpRequestException e)
                    {
                        Console.WriteLine("error auth middleware: " + e.ToString());
                        context.Request.Headers.Remove("authorization");
                    }
                }
            }

            await _next(context);
        }
    }
}
