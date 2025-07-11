namespace Functions;

public class ExecuteOperation
{
    private readonly IOperationRegistry _registry;
    private readonly IRBACMiddleware _rbac;

    public ExecuteOperation(IOperationRegistry registry, IRBACMiddleware rbac)
    {
        _registry = registry;
        _rbac = rbac;
    }

    [Function("ExecuteAksOperation")]
    public async Task<HttpResponseData> Run(
        [HttpTrigger(AuthorizationLevel.Function, "post", Route = "aks/{operation}")] HttpRequestData req,
        string operation, [FromBody]
        OperationContext operationContext,
        FunctionContext executionContext)
    {
        var op = _registry.GetOperation(operation);
        if (op == null)
            return req.CreateResponse(HttpStatusCode.NotFound);

        var userClaims = _rbac.ExtractClaims(req); // Or from headers/context

        if (!op.CanExecute(userClaims))
            return req.CreateResponse(HttpStatusCode.Unauthorized);

        var result = await op.ExecuteAsync(operationContext);

        var response = req.CreateResponse(HttpStatusCode.OK);
        await response.WriteAsJsonAsync(result);
        return response;
    }
}