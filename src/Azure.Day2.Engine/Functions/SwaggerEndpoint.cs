namespace Functions;

public class SwaggerEndpoint
{
    private readonly ISwaggerGenerator _swagger;

    public SwaggerEndpoint(ISwaggerGenerator swagger) => _swagger = swagger;

    [Function("GetSwagger")]
    public HttpResponseData Run([HttpTrigger(AuthorizationLevel.Anonymous, "get", Route = "swagger.json")] HttpRequestData req)
    {
        var json = _swagger.GenerateJson();
        var response = req.CreateResponse(HttpStatusCode.OK);
        response.Headers.Add("Content-Type", "application/json");
        response.WriteString(json);
        return response;
    }
}
