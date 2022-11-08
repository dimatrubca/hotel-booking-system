using HotelRatingServiceML.Model;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace HotelRatingService
{
    public interface IRatingPredictionService
    {
        public ModelOutput Predict(string review);
    }
}
