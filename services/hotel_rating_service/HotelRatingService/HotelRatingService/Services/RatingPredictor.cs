using HotelRatingService.DTOs;
using HotelRatingServiceML.Model;
using Priority_Queue;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace HotelRatingService.Services
{
    public class RatingPredictor
    {
        public RatingPredictorState State { get; set; }
        public Mutex stateMut = new Mutex();
        private SimplePriorityQueue<PredictRequestDTO> _priorityQueue;

        public RatingPredictor()
        {
        }

        public ModelOutput Predict(PredictRequestDTO predictRequest)
        {
            ModelInput input = new ModelInput()
            {
                Review = predictRequest.Review
            };

            ModelOutput result = ConsumeModel.Predict(input);

            Task.Delay(1000);

            return result;
        } 
    }
}
