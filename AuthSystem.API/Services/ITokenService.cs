using AuthSystem.API.Models;

namespace AuthSystem.API.Services;

public interface ITokenService
{
    /// <summary>Generates a short-lived RS256-signed JWT access token.</summary>
    string GenerateAccessToken(string userId, string email, string name);

    /// <summary>Generates a cryptographically random opaque refresh token string.</summary>
    string GenerateRefreshToken();
}
