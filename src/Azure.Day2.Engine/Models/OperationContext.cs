namespace Models;

public class OperationContext
{
    public string CallerId { get; set; }
    public string ResourceId { get; set; }
    public IDictionary<string, string> Parameters { get; set; } = new Dictionary<string, string>();
    public object Credentials { get; set; }  // Use appropriate credential class
}