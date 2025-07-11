namespace Services;

public interface ISwaggerGenerator
{
    string GenerateJson();
}

public class SwaggerGenerator : ISwaggerGenerator
{
    private readonly IOperationRegistry _registry;

    public SwaggerGenerator(IOperationRegistry registry)
    {
        _registry = registry;
    }

    public string GenerateJson()
    {
        var swagger = new
        {
            openapi = "3.0.1",
            info = new
            {
                title = "Azure Day 2 Operations API",
                version = "v1",
                description = "Azure Day 2 Operations API"
            },
            paths = _registry.GetAll().ToDictionary(op => op.Describe().Path, op =>
            {
                var meta = op.Describe();
                return new
                {
                    post = new
                    {
                        summary = meta.Summary,
                        operationId = meta.OperationId,
                        requestBody = new
                        {
                            required = true,
                            content = new
                            {
                            application_json = new
                            {
                                schema = new
                                {
                                    type = "object",
                                    properties = meta.Parameters.ToDictionary(p => p.Name, p => new
                                    {
                                        type = p.Type,
                                        description = p.Description
                                    }),
                                    required = meta.Parameters.Where(p => p.Required).Select(p => p.Name)
                                }
                            }
                            }
                        },
                        responses = meta.Responses.ToDictionary(
                            kv => kv.Key.ToString(),
                            kv => new { description = kv.Value }
                        )
                    }
                };
            })
        };

        return JsonConvert.SerializeObject(swagger, Formatting.Indented);
    }
}