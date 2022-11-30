using System;
using System.Net;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;
using System.Web.Http.Filters;

namespace Gateway.Exceptions
{
    public class ApiExceptionFilter : ExceptionFilterAttribute
    {
        public override void OnException(HttpActionExecutedContext context)
        {
            if (context.Exception is ApiException apiException)
            {
                context.Response = new HttpResponseMessage(HttpStatusCode.NotImplemented);
                    //new ObjectResult(apiException.Message) { StatusCode = (int)apiException.Code };
            }
            Console.WriteLine("Inside APIEXCEPTIONFILTER\n\n\n\n");
        }
        /*
        public override Task OnExceptionAsync(HttpActionExecutedContext context)
        {
            if (context.Exception is ApiException apiException)
            {
                context.Response = new HttpResponseMessage(HttpStatusCode.NotImplemented);
                // context.Result = new ObjectResult(apiException.Message) { StatusCode = (int)apiException.Code };
            }
            Console.WriteLine("Inside APIEXCEPTIONFILTER\n\n\n\n");

            return Task.CompletedTask;
        }*/
    }
}
