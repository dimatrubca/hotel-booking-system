using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Gateway.DTOs
{
    public class ServiceDTO
    {
        [JsonProperty("id")]
        public string Id { get; set; }

        [JsonProperty("name")]
        public string Name { get; set; }

        [JsonProperty("host")]
        public string Host { get; set; }

        [JsonProperty("port")]
        public string Port { get; set; }

        [JsonProperty("protocol")]
        public string Protocol { get; set; }

        public override string ToString()
        {
            return $"Id={Id}, Name={Name}, Host={Host}, Port={Port}, Protocol={Protocol}";
        }
    }
}
