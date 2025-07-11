namespace Models;

public class UserClaims
{
    public string Id { get; set; }
    public List<string> Roles { get; set; } = new();

    public bool HasRole(string role) =>
        Roles.Any(r => string.Equals(r, role, StringComparison.OrdinalIgnoreCase));
}