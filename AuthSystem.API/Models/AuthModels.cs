namespace AuthSystem.API.Models;

public sealed record UserInfo(string Id, string Email, string Name, string? Picture);

public sealed record AuthResponse(string AccessToken, int ExpiresIn, UserInfo User);

public sealed record RefreshTokenData(string UserId, string Email, string Name, string? Picture, DateTimeOffset ExpiresAt);
