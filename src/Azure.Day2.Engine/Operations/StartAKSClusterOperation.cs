namespace Operations;

public class StartAKSClusterOperation : IResourceOperation
{
    public string OperationName => "StartAksCluster";

    public async Task<OperationResult> ExecuteAsync(OperationContext context)
    {
        var id = context.Parameters["ResourceId"];
        await Task.Delay(500); // simulate Azure SDK call
        return OperationResult.Success("Cluster started.");
    }

    public bool CanExecute(UserClaims claims) => claims.Roles.Contains("AKS-Operator");

    public OperationMetadata Describe() => new()
    {
        OperationId = OperationName,
        Summary = "Start an AKS cluster",
        Path = "/aks/start",
        HttpMethod = "POST",
        Parameters = new[] {
            new OperationParameter {
                Name = "ResourceId", Type = "string", Required = true
            }
        },
        Responses = new Dictionary<int, string> {
            {200, "Success"}, {401, "Unauthorized"}, {500, "Error"}
        }
    };
}
