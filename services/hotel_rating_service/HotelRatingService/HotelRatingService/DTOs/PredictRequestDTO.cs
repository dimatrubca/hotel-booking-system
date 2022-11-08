using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace HotelRatingService.DTOs
{
    public class PredictRequestDTO
    {
        public string Review { get; set; }
        public int Priority { get; set; }
    }
}
