public interface IRBACMiddleware
{
    UserClaims ExtractClaims(HttpRequestData req);
}