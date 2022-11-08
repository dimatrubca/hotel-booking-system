using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace HotelRatingService.DTOs
{
    public class ThreadCount
    {
        public int MinWorkerThreads { get; set; }
        public int MinCompletionPortThreads { get; set; }
        public int MaxWorkerThreads { get; set; }
        public int MaxCompletionPortThreads { get; set; }
    }
}
