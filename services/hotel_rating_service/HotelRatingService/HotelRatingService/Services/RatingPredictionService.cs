using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using HotelRatingServiceML.Model;
using Microsoft.Extensions.Logging;

namespace HotelRatingService
{
    public class RatingPredictionService : IRatingPredictionService
    {
        private readonly ILogger<RatingPredictionService> _logger;

        public RatingPredictionService(ILogger<RatingPredictionService> logger)
        {
            _logger = logger;
        }

        public ModelOutput Predict(string review)
        {
            _logger.LogInformation($"Input: {review}");
            ModelInput input = new ModelInput()
            {
                Review = review
            };

            ModelOutput result = ConsumeModel.Predict(input);
            
            _logger.LogInformation($"Prediction result: {result.Prediction}");
            return result;
        }
    }
}
