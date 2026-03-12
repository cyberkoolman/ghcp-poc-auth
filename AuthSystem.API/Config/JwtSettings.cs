namespace AuthSystem.API.Config;

public sealed record JwtSettings
{
    public string Issuer { get; init; } = string.Empty;
    public string Audience { get; init; } = string.Empty;
    /// <summary>PEM-encoded RSA private key (for signing access tokens).</summary>
    public string PrivateKeyPem { get; init; } = string.Empty;
    /// <summary>PEM-encoded RSA public key (for validating access tokens).</summary>
    public string PublicKeyPem { get; init; } = string.Empty;
    public int AccessTokenExpiryMinutes { get; init; } = 15;
    public int RefreshTokenExpiryDays { get; init; } = 7;
}
