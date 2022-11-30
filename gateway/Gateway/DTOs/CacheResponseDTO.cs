using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

#nullable enable

namespace Gateway.DTOs
{
    public class CacheResponseDTO
    {
        [JsonProperty("success")]
        public bool Success { get; set; }
        [JsonProperty("response")]
        public string? Response {get;set;}

        public override string ToString()
        {
            return $"Success: {Success}, Response: {Response}";
        }
    }
}
