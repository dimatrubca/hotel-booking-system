using HotelRatingService.DTOs;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace HotelRatingService.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class ThreadsCountController : ControllerBase
    {
        [HttpGet]
        public ThreadCount Get()
        {
            ThreadCount threadCount = new ThreadCount();
            /*WorkerPool.GetMinThreads(out int workerThreads, out int completionPortThreads);
            threadCount.MinWorkerThreads = workerThreads;
            threadCount.MinCompletionPortThreads = completionPortThreads;

            WorkerPool.GetMaxThreads(out workerThreads, out completionPortThreads);
            threadCount.MaxWorkerThreads = workerThreads;
            threadCount.MaxCompletionPortThreads = completionPortThreads;

            Thread.Sleep(1000 * 5);*/

            return threadCount;
        }
    }
}
