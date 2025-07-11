namespace Models;

public class OperationMetadata
{
    public string OperationId { get; set; }
    public string Summary { get; set; }
    public string Path { get; set; }
    public string HttpMethod { get; set; }
    public IEnumerable<OperationParameter> Parameters { get; set; }
    public IDictionary<int, string> Responses { get; set; }
}

public class OperationParameter
{
    public string Name { get; set; }
    public string Type { get; set; }  // e.g., "string", "integer", "boolean"
    public string Description { get; set; }
    public bool Required { get; set; }
}