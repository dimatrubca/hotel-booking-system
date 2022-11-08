using HotelRatingService.DTOs;
using HotelRatingServiceML.Model;
using Microsoft.ML;
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
        private Lazy<PredictionEngine<ModelInput, ModelOutput>> PredictionEngine = new Lazy<PredictionEngine<ModelInput, ModelOutput>>(CreatePredictionEngine);


        public RatingPredictor()
        {
        }

        public ModelOutput Predict(PredictRequestDTO predictRequest)
        {
            ModelInput input = new ModelInput()
            {
                Review = predictRequest.Review
            };

            ModelOutput result = Predict_(input);

            Task.Delay(1000);

            return result;
        }

        // For more info on consuming ML.NET models, visit https://aka.ms/mlnet-consume
        // Method for consuming model in your app
        public ModelOutput Predict_(ModelInput input)
        {
            Console.WriteLine($"{input.Rating}, {input.Review}");

            ModelOutput result = PredictionEngine.Value.Predict(input);
            return result;
        }

        public static PredictionEngine<ModelInput, ModelOutput> CreatePredictionEngine()
        {
            // Create new MLContext
            MLContext mlContext = new MLContext();

            // Load model & create prediction engine
            string modelPath = @"C:\Data\Uni\Sem7\PAD\hotel-booking-system\services\hotel_rating_service\HotelRatingService\HotelRatingServiceML.Model\MLModel.zip";
            ITransformer mlModel = mlContext.Model.Load(modelPath, out var modelInputSchema);
            var predEngine = mlContext.Model.CreatePredictionEngine<ModelInput, ModelOutput>(mlModel);

            return predEngine;
        }
    }
}
