using Gateway.DTOs;
using Gateway.Exceptions;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Collections.Specialized;
using System.Linq;
using System.Net.Http;
using System.Threading.Tasks;

namespace Gateway
{
    public sealed class LoadBalancer
    {
        private static readonly LoadBalancer instance = new LoadBalancer();
        private static readonly HttpClient client = new HttpClient();

        static LoadBalancer() { }
        private LoadBalancer() {
        }


        public static LoadBalancer Instance
        {
            get
            {
                return instance;
            }
        }

        private Dictionary<string, List<PriorityWrapper<ServiceDTO>>> servicesMap = new Dictionary<string, List<PriorityWrapper<ServiceDTO>>>();

        public async Task<PriorityWrapper<ServiceDTO>> GetService(string name, Destination serviceDiscovery)
        {
            Console.WriteLine($"Get Service: {name}!");
            Console.WriteLine($"after");

            if (!servicesMap.ContainsKey(name) || !servicesMap[name].Any()) {
                Console.WriteLine("Inside if");
                var services = await GetServicesByName(name, serviceDiscovery);

                if (services == null) throw new ApiException(System.Net.HttpStatusCode.BadRequest, "Cannot get service address by name, service discovery error"); //#todo: check response
                var servicesWithPriority = services.Select(x => 
                    new PriorityWrapper<ServiceDTO>
                    {
                        Dto = x,
                        Priority = 0
                    }
                ).ToList();

                Console.WriteLine($"> {name}, {servicesWithPriority[0]}");

                if (!servicesMap.ContainsKey(name)) servicesMap.Add(name, servicesWithPriority); //todo: solve concurrency, remove if
            }
            var item = servicesMap[name];

            if (!servicesMap[name].Any())
            {
                throw new ApiException(System.Net.HttpStatusCode.BadRequest, $"No service named {name} found"); //todo: customize
            }

            var minLoadIndex = 0;

            Console.WriteLine("\n\n");
            Console.WriteLine($"Load balancer, Service: {name}");
            Console.WriteLine($"{servicesMap[name][0].Dto.Id} - {servicesMap[name][0].Priority}");
            for (int i = 1; i < servicesMap[name].Count(); i++)
            {
                Console.WriteLine($"{servicesMap[name][i].Dto.Id} - {servicesMap[name][i].Priority}");
                if (servicesMap[name][i].Priority < servicesMap[name][minLoadIndex].Priority)
                {
                    minLoadIndex = i;
                }
            }
            Console.WriteLine($"Selected: {servicesMap[name][minLoadIndex].Dto.Id}");
            Console.WriteLine("\n=============\n");

            servicesMap[name][minLoadIndex].Priority += 1;
            return servicesMap[name][minLoadIndex];
        }

        private async Task<List<ServiceDTO>> GetServicesByName(string name, Destination serviceDiscovery)
        {
            Console.WriteLine("Inside GetServicesByName");
            HttpResponseMessage result;
            try
            {
                result = await client.GetAsync($"http://service_discovery:8005/services/{name}");

            } catch (HttpRequestException e)
            {
                Console.WriteLine($"http error: {e}");
                return null;
            }

            if (!result.IsSuccessStatusCode)
            {
                Console.WriteLine($"Status code: {result.StatusCode}");
                return null;
            }

            var content = await result.Content.ReadAsStringAsync();

            var services = JsonConvert.DeserializeObject<List<ServiceDTO>>(content);

            //var services = JsonSerializer.Deserialize<List<ServiceDTO>>(content);
            Console.WriteLine($"GetServicesByName, name={name}, result={content}, count={services.Count()}");
            Console.WriteLine($"First Service: {services[0]}");

            return services;
        }

        
    }
}
