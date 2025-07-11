namespace Models;

public class OperationResult
{
    public string Status { get; set; }
    public object Output { get; set; }

    public static OperationResult Success(object output) =>
        new OperationResult { Status = "Success", Output = output };

    public static OperationResult Failure(object error) =>
        new OperationResult { Status = "Failure", Output = error };
}