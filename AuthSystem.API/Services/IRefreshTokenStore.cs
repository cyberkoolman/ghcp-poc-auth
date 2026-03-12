using AuthSystem.API.Models;

namespace AuthSystem.API.Services;

public interface IRefreshTokenStore
{
    Task StoreAsync(string token, RefreshTokenData data, CancellationToken ct = default);

    /// <summary>
    /// Atomically validates an existing refresh token, revokes it, and returns its data.
    /// Returns null when the token is not found or already used (replay attack detection).
    /// </summary>
    Task<RefreshTokenData?> ConsumeAsync(string token, CancellationToken ct = default);

    Task RevokeAsync(string token, CancellationToken ct = default);
}
