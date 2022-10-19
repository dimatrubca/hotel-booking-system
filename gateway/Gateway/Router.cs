using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;
using Microsoft.Extensions.Primitives;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Threading.Tasks;

namespace Gateway
{
    public class Router
    {

        public List<Route> Routes { get; set; }
        public Destination AuthenticationService { get; set; }


        public Router(string routeConfigFilePath)
        {
            dynamic router = JsonLoader.LoadFromFile<dynamic>(routeConfigFilePath);

            Routes = JsonLoader.Deserialize<List<Route>>(Convert.ToString(router.routes)) ;
            Console.WriteLine("Routes constructor:");
            Console.WriteLine(Routes);
            Console.WriteLine($"{Routes[0].Endpoint} - {Routes[0].Destination.Path} - {Routes[0].Destination.RequiresAuthentication}");
            Console.WriteLine($"{Routes[1].Endpoint} - {Routes[1].Destination.Path} - {Routes[1].Destination.RequiresAuthentication}");

            AuthenticationService = JsonLoader.Deserialize<Destination>(Convert.ToString(router.authenticationService));

        }

        public async Task<HttpResponseMessage> RouteRequest(HttpRequest request)
        {
            string path = request.Path.ToString();
            string basePath = '/' + path.Split('/')[1];

            //Console.WriteLine(path);
            //Console.WriteLine(basePath);

            Destination destination;
            try
            {
                destination = Routes.First(r => r.Endpoint.Equals(basePath)).Destination;
            }
            catch
            {
                return ConstructErrorMessage("The path could not be found.");
            }

            if (destination.RequiresAuthentication)
            {
                string token = request.Headers["token"];
                request.Query.Append(new KeyValuePair<string, StringValues>("token", new StringValues(token)));
                HttpResponseMessage authResponse = await AuthenticationService.SendRequest(request);
                if (!authResponse.IsSuccessStatusCode) return ConstructErrorMessage("Authentication failed.");
            }

            Console.WriteLine($"Route request, destination: {destination}");

            return await destination.SendRequest(request);
        }

        private HttpResponseMessage ConstructErrorMessage(string error)
        {
            HttpResponseMessage errorMessage = new HttpResponseMessage
            {
                StatusCode = HttpStatusCode.NotFound,
                Content = new StringContent(error)
            };
            return errorMessage;
        }
    }
}
