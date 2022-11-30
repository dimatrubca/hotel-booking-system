using HotelRatingService.DTOs;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace HotelRatingService.Controllers
{
    [ApiController]
    [Route("")]
    public class RatingPredictionController : ControllerBase
    {

        private readonly ILogger<RatingPredictionController> _logger;
        private readonly WorkerPool _workerPool;

        public RatingPredictionController(ILogger<RatingPredictionController> logger, WorkerPool workerPool)
        {
            _logger = logger;
            _workerPool = workerPool;
        }

        [HttpPost("predict")]
        public async Task<IActionResult> Predict(PredictRequestDTO predictRequestDTO)
        {
           // _logger.LogInformation(predictRequestDTO.ToString());
            var result = _workerPool.Predict(predictRequestDTO);
            //_logger.LogInformation($"Finished: {predictRequestDTO.ToString()}");

            return Ok(result);
        }
    }
}
