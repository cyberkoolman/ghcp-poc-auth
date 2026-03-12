using System.Text.Json;
using AuthSystem.API.Config;
using AuthSystem.API.Models;
using Microsoft.Extensions.Options;
using StackExchange.Redis;

namespace AuthSystem.API.Services;

public sealed class RedisRefreshTokenStore : IRefreshTokenStore
{
    private readonly IDatabase _db;
    private readonly JwtSettings _settings;
    private static readonly JsonSerializerOptions JsonOpts = new(JsonSerializerDefaults.Web);

    public RedisRefreshTokenStore(IConnectionMultiplexer redis, IOptions<JwtSettings> settings)
    {
        _db = redis.GetDatabase();
        _settings = settings.Value;
    }

    private static string KeyFor(string token) => $"refresh:{token}";

    public async Task StoreAsync(string token, RefreshTokenData data, CancellationToken ct = default)
    {
        var json = JsonSerializer.Serialize(data, JsonOpts);
        var ttl = TimeSpan.FromDays(_settings.RefreshTokenExpiryDays);
        // Explicit overload: (key, value, expiry, When, CommandFlags) avoids Moq overload ambiguity in tests
        await _db.StringSetAsync(KeyFor(token), json, ttl, When.Always, CommandFlags.None);
    }

    public async Task<RefreshTokenData?> ConsumeAsync(string token, CancellationToken ct = default)
    {
        var key = KeyFor(token);

        // Atomic GET + DEL via Lua script — prevents two concurrent callers both succeeding
        const string script = """
            local val = redis.call('GET', KEYS[1])
            if val then redis.call('DEL', KEYS[1]) end
            return val
            """;

        var result = (RedisValue)await _db.ScriptEvaluateAsync(script, [(RedisKey)key]);
        if (result.IsNullOrEmpty) return null;

        return JsonSerializer.Deserialize<RefreshTokenData>(result.ToString(), JsonOpts);
    }

    public async Task RevokeAsync(string token, CancellationToken ct = default)
        => await _db.KeyDeleteAsync(KeyFor(token));
}
