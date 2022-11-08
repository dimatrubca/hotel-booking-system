using HotelRatingService.Services;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Priority_Queue;
using HotelRatingServiceML.Model;
using HotelRatingService.DTOs;
using System.Threading;

namespace HotelRatingService
{
    public class WorkerPool
    {
        public int AvailablePredictors { get; set; }
        SimplePriorityQueue<PredictDTO> priorityQueue = new SimplePriorityQueue<PredictDTO>();


        public WorkerPool()
        {
            // instantiate predictors
            AvailablePredictors = 10;

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
                priorityQueue.Enqueue(predictDTO, predictRequest.Priority);
                Monitor.Wait(predictDTO.sync);
            }

            return predictDTO.Result;
        }
    }
}
