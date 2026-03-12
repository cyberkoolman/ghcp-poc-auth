using AuthSystem.API.Config;
using AuthSystem.API.Models;
using AuthSystem.API.Services;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Google;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Options;
using System.Security.Claims;

namespace AuthSystem.API.Controllers;

[ApiController]
[Route("auth")]
public sealed class AuthController : ControllerBase
{
    private const string RefreshTokenCookie = "refresh_token";

    private readonly ITokenService _tokens;
    private readonly IRefreshTokenStore _store;
    private readonly JwtSettings _jwtSettings;

    public AuthController(ITokenService tokens, IRefreshTokenStore store, IOptions<JwtSettings> jwtSettings)
    {
        _tokens = tokens;
        _store = store;
        _jwtSettings = jwtSettings.Value;
    }

    // ── GET /auth/login/google ────────────────────────────────────────────────
    [HttpGet("login/google")]
    public IActionResult LoginWithGoogle([FromQuery] string? returnUrl = "/")
    {
        var props = new AuthenticationProperties
        {
            RedirectUri = Url.Action(nameof(GoogleCallback), "Auth", new { returnUrl }),
            Items = { ["returnUrl"] = returnUrl }
        };
        return Challenge(props, GoogleDefaults.AuthenticationScheme);
    }

    // ── GET /auth/callback/google ─────────────────────────────────────────────
    [HttpGet("callback/google")]
    public async Task<IActionResult> GoogleCallback([FromQuery] string? returnUrl = "/", CancellationToken ct = default)
    {
        var result = await HttpContext.AuthenticateAsync(GoogleDefaults.AuthenticationScheme);
        if (!result.Succeeded)
            return Unauthorized(new { error = "Google authentication failed." });

        var principal = result.Principal!;
        var userId = principal.FindFirstValue(ClaimTypes.NameIdentifier)
                     ?? principal.FindFirstValue("sub")
                     ?? throw new InvalidOperationException("Missing user identifier from Google.");
        var email = principal.FindFirstValue(ClaimTypes.Email) ?? string.Empty;
        var name = principal.FindFirstValue(ClaimTypes.Name) ?? string.Empty;
        var picture = principal.FindFirstValue("picture");

        var accessToken = _tokens.GenerateAccessToken(userId, email, name);
        var refreshToken = _tokens.GenerateRefreshToken();

        var tokenData = new RefreshTokenData(userId, email, name, picture,
            DateTimeOffset.UtcNow.AddDays(_jwtSettings.RefreshTokenExpiryDays));
        await _store.StoreAsync(refreshToken, tokenData, ct);

        SetRefreshTokenCookie(refreshToken);

        var response = new AuthResponse(
            accessToken,
            _jwtSettings.AccessTokenExpiryMinutes * 60,
            new UserInfo(userId, email, name, picture));

        // Redirect SPA callback page which will extract the token from the JSON body
        // For SPAs the API returns JSON; SPA handles navigation.
        return Ok(response);
    }

    // ── POST /auth/refresh ────────────────────────────────────────────────────
    [HttpPost("refresh")]
    public async Task<IActionResult> Refresh(CancellationToken ct = default)
    {
        var oldToken = Request.Cookies[RefreshTokenCookie];
        if (string.IsNullOrEmpty(oldToken))
            return Unauthorized(new { error = "Refresh token cookie missing." });

        var data = await _store.ConsumeAsync(oldToken, ct);
        if (data is null || data.ExpiresAt <= DateTimeOffset.UtcNow)
        {
            // Token was not found or already consumed — possible replay attack; clear cookie
            ClearRefreshTokenCookie();
            return Unauthorized(new { error = "Invalid or expired refresh token." });
        }

        var newAccessToken = _tokens.GenerateAccessToken(data.UserId, data.Email, data.Name);
        var newRefreshToken = _tokens.GenerateRefreshToken();

        var newData = new RefreshTokenData(data.UserId, data.Email, data.Name, data.Picture,
            DateTimeOffset.UtcNow.AddDays(_jwtSettings.RefreshTokenExpiryDays));
        await _store.StoreAsync(newRefreshToken, newData, ct);

        SetRefreshTokenCookie(newRefreshToken);

        return Ok(new
        {
            accessToken = newAccessToken,
            expiresIn = _jwtSettings.AccessTokenExpiryMinutes * 60
        });
    }

    // ── POST /auth/logout ─────────────────────────────────────────────────────
    [HttpPost("logout")]
    public async Task<IActionResult> Logout(CancellationToken ct = default)
    {
        var token = Request.Cookies[RefreshTokenCookie];
        if (!string.IsNullOrEmpty(token))
            await _store.RevokeAsync(token, ct);

        ClearRefreshTokenCookie();
        return NoContent();
    }

    // ── GET /auth/me ──────────────────────────────────────────────────────────
    [Authorize]
    [HttpGet("me")]
    public IActionResult Me()
    {
        var userId = User.FindFirstValue(ClaimTypes.NameIdentifier)
                     ?? User.FindFirstValue("sub");
        var email = User.FindFirstValue(ClaimTypes.Email)
                    ?? User.FindFirstValue("email");
        var name = User.FindFirstValue(ClaimTypes.Name)
                   ?? User.FindFirstValue("name");

        return Ok(new UserInfo(userId ?? string.Empty, email ?? string.Empty, name ?? string.Empty, null));
    }

    // ── Helpers ───────────────────────────────────────────────────────────────
    private void SetRefreshTokenCookie(string token)
    {
        Response.Cookies.Append(RefreshTokenCookie, token, new CookieOptions
        {
            HttpOnly = true,
            Secure = true,
            SameSite = SameSiteMode.Strict,
            Path = "/auth/refresh",   // scoped — invisible to all other requests
            Expires = DateTimeOffset.UtcNow.AddDays(_jwtSettings.RefreshTokenExpiryDays),
            IsEssential = true
        });
    }

    private void ClearRefreshTokenCookie()
    {
        Response.Cookies.Delete(RefreshTokenCookie, new CookieOptions
        {
            HttpOnly = true,
            Secure = true,
            SameSite = SameSiteMode.Strict,
            Path = "/auth/refresh"
        });
    }
}
