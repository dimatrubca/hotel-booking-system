using HotelRatingServiceML.Model;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace HotelRatingService.DTOs
{
    public class PredictDTO
    {
        public string Review { get; set; }
        public int Priority { get; set; }
        public ModelOutput Result { get; set; }
        public object sync = new Object();

    }
}
