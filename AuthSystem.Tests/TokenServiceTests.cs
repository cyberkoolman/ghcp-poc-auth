using System.IdentityModel.Tokens.Jwt;
using System.Security.Cryptography;
using AuthSystem.API.Config;
using AuthSystem.API.Services;
using Microsoft.Extensions.Options;
using Xunit;

namespace AuthSystem.Tests;

public sealed class TokenServiceTests
{
    private readonly TokenService _sut;
    private readonly JwtSettings _settings;

    public TokenServiceTests()
    {
        // Generate a fresh RSA key pair for each test run — no secrets on disk
        using var rsa = RSA.Create(2048);
        _settings = new JwtSettings
        {
            Issuer = "https://test-issuer",
            Audience = "test-audience",
            PrivateKeyPem = rsa.ExportRSAPrivateKeyPem(),
            PublicKeyPem = rsa.ExportRSAPublicKeyPem(),
            AccessTokenExpiryMinutes = 15,
            RefreshTokenExpiryDays = 7,
        };
        _sut = new TokenService(Options.Create(_settings));
    }

    [Fact]
    public void GenerateAccessToken_ReturnsValidJwt()
    {
        var token = _sut.GenerateAccessToken("user-123", "test@example.com", "Test User");

        var handler = new JwtSecurityTokenHandler();
        Assert.True(handler.CanReadToken(token));

        var jwt = handler.ReadJwtToken(token);
        Assert.Equal("https://test-issuer", jwt.Issuer);
        Assert.Contains(jwt.Audiences, a => a == "test-audience");
        Assert.Equal("user-123", jwt.Subject);
        Assert.Equal("test@example.com", jwt.Claims.First(c => c.Type == "email").Value);
    }

    [Fact]
    public void GenerateAccessToken_ExpiryMatchesSettings()
    {
        var before = DateTime.UtcNow;
        var token = _sut.GenerateAccessToken("u", "e@e.com", "E");
        var after = DateTime.UtcNow;

        var jwt = new JwtSecurityTokenHandler().ReadJwtToken(token);
        Assert.InRange(jwt.ValidTo,
            before.AddMinutes(_settings.AccessTokenExpiryMinutes - 1),
            after.AddMinutes(_settings.AccessTokenExpiryMinutes + 1));
    }

    [Fact]
    public void GenerateRefreshToken_IsBase64AndSufficientEntropy()
    {
        var t1 = _sut.GenerateRefreshToken();
        var t2 = _sut.GenerateRefreshToken();

        var bytes = Convert.FromBase64String(t1); // throws if invalid base64
        Assert.Equal(32, bytes.Length);            // 256-bit
        Assert.NotEqual(t1, t2);                   // no collisions
    }
}
