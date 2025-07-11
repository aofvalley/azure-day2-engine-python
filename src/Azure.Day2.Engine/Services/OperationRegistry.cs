namespace Services;

public interface IOperationRegistry
{
    IEnumerable<IResourceOperation> GetAll();
    IResourceOperation? GetOperation(string name);
}

public class OperationRegistry : IOperationRegistry
{
    private readonly IEnumerable<IResourceOperation> _operations;
    private readonly Dictionary<string, IResourceOperation> _map;

    public OperationRegistry(IEnumerable<IResourceOperation> operations)
    {
        _operations = operations;
        _map = operations.ToDictionary(op => op.OperationName, StringComparer.OrdinalIgnoreCase);
    }

    public IEnumerable<IResourceOperation> GetAll() => _operations;

    public IResourceOperation? GetOperation(string name) =>
        _map.TryGetValue(name, out var op) ? op : null;
}