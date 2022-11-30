using Gateway.DTOs;
using Gateway.Exceptions;

using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Primitives;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Threading.Tasks;
using System.Web;

namespace Gateway
{
    public class Router
    {

        public List<ServiceNameRoute> Routes { get; set; }
        public Destination AuthenticationService { get; set; }
        public Destination ServiceDiscovery { get; set; }

        private readonly ILogger _logger;


        public Router(string routeConfigFilePath, ILoggerFactory loggerFactory)
        {
            _logger = loggerFactory.CreateLogger("Router");

            dynamic router = JsonLoader.LoadFromFile<dynamic>(routeConfigFilePath);

            Routes = JsonLoader.Deserialize<List<ServiceNameRoute>>(Convert.ToString(router.routes)) ;

            _logger.LogInformation($"Route constructor: {Routes}");
            Console.WriteLine("Routes constructor:");
            Console.WriteLine(Routes);
            Console.WriteLine($"{Routes[0].Endpoint} - {Routes[0].ServiceName}");
            Console.WriteLine($"{Routes[1].Endpoint} - {Routes[1].ServiceName}");

            AuthenticationService = JsonLoader.Deserialize<Destination>(Convert.ToString(router.authenticationService));
            ServiceDiscovery = JsonLoader.Deserialize<Destination>(Convert.ToString(router.serviceDiscovery));

        }

        public async Task CacheResponse(HttpResponseMessage responseToCache, string url) //todo: extract url from response?
        {
            PriorityWrapper<ServiceDTO> cacheDTOWrapper = null;

            try
            {
                cacheDTOWrapper = await LoadBalancer.Instance.GetService("cache", ServiceDiscovery);
            }
            catch (ApiException e)
            {
                Console.WriteLine($"Exception: {e}");
                return;
            }
            var cacheURL = "http://" + cacheDTOWrapper.Dto.Host + ':' + cacheDTOWrapper.Dto.Port + '/'; // todo: handle cache


            using (var client = new HttpClient())
            {
                object data = new
                {
                    url = "http://" + url, // todo: handle http
                    data = await responseToCache.Content.ReadAsStringAsync()// todo: avoid converting string -> ...
                };
                HttpResponseMessage response = await client.PostAsJsonAsync(cacheURL, data);

                if (response.IsSuccessStatusCode)
                {
                    Console.WriteLine($"Cached successfully, url={url}, data={data}");
                } else
                {
                    Console.WriteLine("Invalid response code from cache");
                    Console.WriteLine(await response.Content.ReadAsStringAsync());
                }
            }
        }

        public async Task<HttpResponseMessage> TryQueryCache(string url)
        {
            PriorityWrapper<ServiceDTO> cacheDTOWrapper = null;

            try
            {
                cacheDTOWrapper = await LoadBalancer.Instance.GetService("cache", ServiceDiscovery);
            }
            catch (ApiException e)
            {
                return null;
            }

            var cacheURL = cacheDTOWrapper.Dto.Host + ':' + cacheDTOWrapper.Dto.Port + '/';


            using (var client = new HttpClient())
            {
                try
                {
                    Console.WriteLine("Before response creation...");

                    // https://stackoverflow.com/questions/17096201/build-query-string-for-system-net-httpclient-get 
                    // todo: try uriBuilder
                    var query = HttpUtility.ParseQueryString(string.Empty);
                    query["query"] = "GET " + url; //todo: extract outside
                    string queryString = query.ToString();

                    var requestUrl = "http://" + cacheURL + "?" + "query=GET http://" + url;// queryString; //todo: handle http

                    Console.WriteLine($"TryQueryCache, requestUrl={requestUrl}");
                    HttpResponseMessage response = await client.GetAsync(requestUrl);

                    Console.WriteLine($"Status code: {response.StatusCode}");

                    response.EnsureSuccessStatusCode();
                    string responseBody = await response.Content.ReadAsStringAsync();

                    Console.WriteLine($"Cache Response body: {responseBody}");
                    var responseDTO = JsonConvert.DeserializeObject<Dictionary<string, CacheResponseDTO>>(responseBody);
                    var cacheResponseDTO = responseDTO["http://" + url + '/']; //todo: handle http, handle '/'
                    //    JsonConvert.DeserializeObject<CacheResponseDTO>(responseBody);  //todo: check on success false...

                    if (cacheResponseDTO.Success == true)
                    {
                        // or create new HttpResponseMessage???
                        response.Content = new StringContent(cacheResponseDTO.Response, System.Text.Encoding.UTF8, "application/json");
                        return response;
                    }

                    Console.WriteLine($"Cache Response DTO: {cacheResponseDTO}");
                }
                catch (HttpRequestException e)
                {
                    Console.WriteLine("error cache request " + e.ToString());
                    return null;
                }
                catch (Exception e)
                {
                    Console.WriteLine(e.ToString());
                    Console.WriteLine(e.Message);
                    Console.WriteLine("...\n\n\n");
                    return null;
                }
            }

            return null;
        }

        public async Task<HttpResponseMessage> RouteRequest(HttpRequest request)
        {
            string path = request.Path.ToString();
            string basePath = '/' + path.Split('/')[1];
            string servicePath = "";

            if (path.Split('/').Count() >= 3)
            {
                servicePath = path.Split('/', 3)[2];
            }

            Console.WriteLine($"First split: {path.Split('/')[0]}");
            Console.WriteLine($"Request path: {request.Path}");

            Console.WriteLine($"Path: `{path}`");
            Console.WriteLine($"Base path: `{basePath}`");
            Console.WriteLine($"Split: {path.Split('/').Count()}");
            Console.WriteLine($"Service path: {servicePath}");

            string serviceName = null;
            bool enableCircuitBreaker = false;

            Console.WriteLine($"Routes: {Routes.Count()}");
            Routes.Select(x => { Console.WriteLine(x); return x; }).ToList();
            try
            {
                var route = Routes.First(r => r.Endpoint.Equals(basePath));
                serviceName = route.ServiceName;
                enableCircuitBreaker = route.EnableCircuitBreaker;
            }
            catch
            {
                throw new ApiException(HttpStatusCode.NotFound, $"invalid path = {basePath}"); //todo: return better status code
            }

            PriorityWrapper<ServiceDTO> serviceDTOWrapper;
            serviceDTOWrapper = await LoadBalancer.Instance.GetService(serviceName, ServiceDiscovery);
            var destinationURL = serviceDTOWrapper.Dto.Host + ':' + serviceDTOWrapper.Dto.Port + "/" + servicePath; // todo: check, + request.Path;


            if (request.Method == HttpMethod.Get.Method) // todo: solve '//' in the end of url query
            {
                var cachedResponseMessage = await TryQueryCache(destinationURL);
                Console.WriteLine($"Tried query cache, response: {cachedResponseMessage}");

                if (cachedResponseMessage != null)
                {
                    return cachedResponseMessage;
                }
            }

            Console.WriteLine($"Host: {serviceDTOWrapper.Dto.Host}, Port: {serviceDTOWrapper.Dto.Port}, Path: {request.Path}");
            Console.WriteLine($"Destination url: {destinationURL}");
            Destination destination = new Destination(destinationURL);
            Console.WriteLine($"Route request, destination: {destination}");
            bool assignPriority = (basePath == "/rating");

            var response =  await destination.SendRequest(request, enableCircuitBreaker, assignPriority);

            if ((request.Method == HttpMethod.Get.Method) && (response.IsSuccessStatusCode) && (!servicePath.ToLower().Contains("error")))
            {
                Console.WriteLine($"Request status code: {response.StatusCode}, caching...");
                await CacheResponse(response, destinationURL);
            }

            serviceDTOWrapper.Priority -= 1; //todo: change position?

            Console.WriteLine($"Route request end, response code: {response.StatusCode}");
            return response;

            //todo: decrease sertviceDTOWrapper priority
            //priority wrapper ... maybe rename??
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
