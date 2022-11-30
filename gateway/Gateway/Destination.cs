using Microsoft.AspNetCore.Http;
using Newtonsoft.Json;
using Polly;
using Polly.CircuitBreaker;
using Polly.Retry;
using Polly.Timeout;
using Polly.Wrap;
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Threading.Tasks;
using System.Web.Http;

namespace Gateway
{
    public class Destination
    {
        public string Host { get; set; }
        static HttpClient client = new HttpClient();

        private readonly static ConcurrentDictionary<string, AsyncPolicyWrap> _circuitBreakerPolicies = new ConcurrentDictionary<string, AsyncPolicyWrap>();


        public Destination(string uri)
        {
            Host = uri;
        }

        private Destination()
        {
            Host = "/";
        }

        private string CreateDestinationUri(HttpRequest request)
        {
            string requestPath = request.Path.ToString();
            string queryString = request.QueryString.ToString();

            Console.Write($"Host: {Host}");
            Console.WriteLine($"Request path: {requestPath}");
            Console.WriteLine($"Query string: {queryString}");

            Console.WriteLine($"CreateDestinationUri, Host: {Host}, queryString: {queryString}, requestPath: {requestPath}");
            return "http://" + Host + queryString; //todo: handle host better
          //  return Host + requestPath + queryString; //todo: maybe extend endpoint to include till end...
        }


        public async Task<HttpResponseMessage> SendRequest(HttpRequest request, bool enableCircuitBreaker, bool assignPriority)
        {
            HttpResponseMessage response = null;

            if (enableCircuitBreaker)
            {
                try
                {
                    response = await SendRequestThroughCircuitBreaker(request, assignPriority);
                } catch (BrokenCircuitException e)
                {
                    response = new HttpResponseMessage(System.Net.HttpStatusCode.InternalServerError);
                    response.Content = new StringContent("{\"details\": \"Circuit is Open\"}");
                    Console.WriteLine("Circuit is broken...");
                    return response;
                } catch (HttpResponseException e)
                {
                    return e.Response;
                } catch (Exception e)
                {
                    response = new HttpResponseMessage(System.Net.HttpStatusCode.InternalServerError);
                    response.Content = new StringContent("{\"details\": \"Error\"}");
                    //Console.WriteLine("Circuit is broken...");
                    return response;
                }
            } else
            {
                response = await SendRequest(request, assignPriority);
            }

            return response;
        }

        private void OnHalfOpen()
        {
            Console.WriteLine("=============\nCircuit in test mode, one request will be allowed.\n=============");
        }

        private void OnReset()
        {
            Console.WriteLine("=============\nCircuit closed, requests flow normally\n=============");
        }

        private void OnBreak(Exception e, TimeSpan ts)
        {
            Console.WriteLine("=============\nCircuit cut, requests will not flow for 30 seconds\n=============");
        }

        private async Task<HttpResponseMessage> SendRequestThroughCircuitBreaker(HttpRequest request, bool assignPriority)
        {
            string url = request.Path;
            AsyncPolicyWrap policyWrap;

            if (!_circuitBreakerPolicies.ContainsKey(url)) 
            {
                /*var circuitBreakerPolicy = Policy.Handle<HttpResponseException>().CircuitBreakerAsync(
                    exceptionsAllowedBeforeBreaking: 5, 
                    durationOfBreak: TimeSpan.FromSeconds(30),
                    onBreak: OnBreak,
                    onReset: OnReset,
                    onHalfOpen: OnHalfOpen
                ); */
                var circuitBreakerPolicy = Policy.Handle<Exception>().AdvancedCircuitBreakerAsync(
                    1,
                    TimeSpan.FromSeconds(30),
                    6,
                    TimeSpan.FromSeconds(30),
                    onBreak: OnBreak,
                    onReset: OnReset,
                    onHalfOpen: OnHalfOpen
                );

                var retryPolicy = Policy.Handle<Exception>().WaitAndRetryAsync(2, _ => TimeSpan.FromSeconds(1));
                policyWrap = retryPolicy.WrapAsync(circuitBreakerPolicy);

                var status = _circuitBreakerPolicies.TryAdd(url, policyWrap);
            }
            else
            {
                policyWrap = _circuitBreakerPolicies[url];
            }

            var response = await policyWrap.ExecuteAsync(async () =>
            {
                var result = await SendRequest(request, assignPriority);

                if ((int) result.StatusCode >= 500 && (int) result.StatusCode < 600 || (int) result.StatusCode == 429)
                {
                    throw new HttpResponseException(result);
                }

                return result;
            });

            return response;
        }


        private async Task<HttpResponseMessage> SendRequest(HttpRequest request, bool assignPriority)
        {
            string requestContent;
            using (Stream receiveStream = request.Body)
            {
                using (StreamReader readStream = new StreamReader(receiveStream, Encoding.UTF8))
                {
                    requestContent = readStream.ReadToEnd();
                }
            }

            if (request.ContentType!=null && request.ContentType.ToLower().Contains("application/json") && assignPriority)
            {
                var priority = 1;

                if (request.Headers.ContainsKey("Authorization"))
                {
                    priority = 2;
                }

                var requestContentDict = JsonConvert.DeserializeObject<Dictionary<dynamic, dynamic>>(requestContent);
                requestContentDict["Priority"] = priority;

                requestContent = JsonConvert.SerializeObject(requestContentDict);
            }

            using (var newRequest = new HttpRequestMessage(new HttpMethod(request.Method), CreateDestinationUri(request)))
            {


                newRequest.Content = new StringContent(requestContent, Encoding.UTF8, request.ContentType);
                Console.WriteLine($"Sending {newRequest.Method} http request to {newRequest.RequestUri}, content type: {request.ContentType}, content: {requestContent}");

                var token = request.Headers["Authorization"].ToString();

                if (!string.IsNullOrWhiteSpace(token))
                {
                    newRequest.Headers.Add("Authorization", token);
                    //Console.WriteLine($"Auth header set up: {token}");
                }

                //Console.WriteLine($"Headers: {newRequest.Headers}");
                var response = await client.SendAsync(newRequest);
                Console.WriteLine($"Response code: {response.StatusCode}");

                return response;
            }
        }

        public override string ToString()
        {
            return $"Path: {Host}";
        }
    }
}
