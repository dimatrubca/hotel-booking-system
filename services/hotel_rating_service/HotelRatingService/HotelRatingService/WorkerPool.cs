using HotelRatingService.Services;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Priority_Queue;
using HotelRatingServiceML.Model;
using HotelRatingService.DTOs;
using System.Threading;
using HotelRatingService.Controllers;
using Microsoft.Extensions.Logging;

namespace HotelRatingService
{
    public class WorkerPool
    {
        public int AvailablePredictors { get; set; } //todo: add mutex around AvailablePredictors
        SimplePriorityQueue<PredictDTO> priorityQueue = new SimplePriorityQueue<PredictDTO>();
        private readonly ILogger<WorkerPool> _logger;


        public WorkerPool(ILogger<WorkerPool> logger)
        {
            _logger = logger;
            // instantiate predictors
            AvailablePredictors = 5;

            Thread thread = new Thread(new ThreadStart(ExecuteTasks));
            thread.Start();
        }

        public void PredictTask(PredictDTO predictDTO)
        {
            RatingPredictor predictor = new RatingPredictor();
            Thread thread = new Thread(() =>
            {
                var result = predictor.Predict(new PredictRequestDTO
                {
                    Priority = predictDTO.Priority,
                    Review = predictDTO.Review
                });

                Random r = new Random();
                int sleepSeconds = 10;// r.Next(3, 10);
                Thread.Sleep(sleepSeconds * 1000);

                predictDTO.Result = result;

                lock (predictDTO.sync)
                {
                    Monitor.Pulse(predictDTO.sync);
                }
                AvailablePredictors += 1;
            });
            thread.Start();
        }

        public void ExecuteTasks()
        {
            while (true)
            {
                while (priorityQueue.Count() > 0)
                {
                    if (AvailablePredictors > 0)
                    {
                        AvailablePredictors -= 1;
                        var predictRequest = priorityQueue.Dequeue();
                        _logger.LogInformation($"Denqueued: {predictRequest.Priority}, {predictRequest.Review}");

                        PredictTask(predictRequest);
                    } else
                    {
                        Task.Delay(25);
                    }
                }
            }
        }

        public ModelOutput Predict(PredictRequestDTO predictRequest)
        {
            PredictDTO predictDTO = new PredictDTO
            {
                Priority = predictRequest.Priority,
                Review = predictRequest.Review
            };

            lock (predictDTO.sync)
            {
                priorityQueue.Enqueue(predictDTO, -predictRequest.Priority);
                //Console.WriteLine($"Enqueued: {predictRequest.Priority}");
                _logger.LogInformation($"Enqueued: {predictRequest.Priority}, {predictDTO.Review}");
                Monitor.Wait(predictDTO.sync);
            }

            return predictDTO.Result;
        }
    }
}
