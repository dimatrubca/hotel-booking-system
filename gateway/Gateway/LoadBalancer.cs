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

        public async Task<PriorityWrapper<ServiceDTO>> GetService(string name, Destination serviceDiscovery, List<ServiceDTO> failedServices)
        {
            Console.WriteLine($"Get Service: {name}!");
            Console.WriteLine($"after");

            var services = await GetServicesByName(name, serviceDiscovery);

            if (services == null) throw new ApiException(System.Net.HttpStatusCode.BadRequest, "Cannot get service address by name, service discovery error"); //#todo: check response
            UpdateServices(name, services);

            if (!servicesMap[name].Any())
            {
                throw new ApiException(System.Net.HttpStatusCode.BadRequest, $"No service named {name} found"); //todo: customize
            }

            var minLoadIndex = -1;

            Console.WriteLine("\n\nfs:");

            foreach (var x in failedServices)
            {
                Console.Write($"{x.Host}");
            }

            Console.WriteLine($"\nLoad balancer, Service: {name}");

            for (int i = 0; i < servicesMap[name].Count(); i++)
            {
                Console.WriteLine($"{servicesMap[name][i].Dto.Id} - {servicesMap[name][i].Priority}, {servicesMap[name][i].IsAvailable}, {!failedServices.Any(x => x.Host == servicesMap[name][i].Dto.Host)}");
                if ((minLoadIndex == -1 || servicesMap[name][i].Priority < servicesMap[name][minLoadIndex].Priority) &&  
                        servicesMap[name][i].IsAvailable &&
                        !failedServices.Any(x => x.Host == servicesMap[name][i].Dto.Host))
                {
                    minLoadIndex = i;
                }
            }

            Console.WriteLine($"Failed services param: {failedServices}, index: {minLoadIndex}");

            if (minLoadIndex == -1) return null;

            Console.WriteLine($"Selected: {servicesMap[name][minLoadIndex].Dto.Id}");
            Console.WriteLine("\n=============\n");


            servicesMap[name][minLoadIndex].Priority += 1;
            return servicesMap[name][minLoadIndex];
        }

        private void UpdateServices(string name, List<ServiceDTO> currentServices)
        {

            if (!servicesMap.ContainsKey(name))
            {
                var servicesWithPriority = currentServices.Select(x =>
                    new PriorityWrapper<ServiceDTO>
                    {
                        Dto = x,
                        Priority = 0,
                        IsAvailable = true
                    }
                ).ToList();

                servicesMap.Add(name, servicesWithPriority); // todo: add thread safety

                return;
            }

            var services = servicesMap[name];

            services.ForEach(x =>
            {
                var isAvailable = currentServices.Any(y => y.Host == x.Dto.Host);

                if (!isAvailable)
                {
                    x.IsAvailable = false;
                } else
                {
                    x.IsAvailable = true;
                }
            });

            currentServices.ForEach(x =>
            {
                var exists = services.Any(y => y.Dto.Host == x.Host);

                if (!exists)
                {
                    services.Add(new PriorityWrapper<ServiceDTO>
                    {
                        Dto = x,
                        Priority = 0,
                        IsAvailable = true
                    });
                }
            });
        }

        private async Task<List<ServiceDTO>> GetServicesByName(string name, Destination serviceDiscovery)
        {
            Console.WriteLine("Inside GetServicesByName");
            HttpResponseMessage result;
            try
            {
                result = await client.GetAsync($"http://service_discovery:8005/services/{name}");
                //result = await client.GetAsync($"http://localhost:8005/services/{name}");
            }
            catch (HttpRequestException e)
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
