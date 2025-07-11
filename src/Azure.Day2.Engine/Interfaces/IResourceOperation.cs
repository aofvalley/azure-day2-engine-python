namespace Interfaces;

public interface IResourceOperation
{
    string OperationName { get; }
    Task<OperationResult> ExecuteAsync(OperationContext context);
    bool CanExecute(UserClaims claims);
    OperationMetadata Describe();
}