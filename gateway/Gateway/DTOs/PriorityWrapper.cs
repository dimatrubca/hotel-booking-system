using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Gateway.DTOs
{
    public class PriorityWrapper<T>
    {
        public int Priority { get; set; }
        public bool IsAvailable { get; set; }
        public T Dto { get; set; }

    }
}
