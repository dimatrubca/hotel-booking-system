using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Gateway
{
    public class ServiceNameRoute
    {
        public string Endpoint { get; set; }
        public string ServiceName { get; set; }
        public bool EnableCircuitBreaker { get; set; }

        public override string ToString()
        {
            return $"Endpoint: {Endpoint}, Servicename: {ServiceName}, EnableCircuitBreaker: {EnableCircuitBreaker}";
        }
    }
}
