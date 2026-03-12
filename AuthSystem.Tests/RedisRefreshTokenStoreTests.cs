using AuthSystem.API.Config;
using AuthSystem.API.Models;
using AuthSystem.API.Services;
using Microsoft.Extensions.Options;
using Moq;
using StackExchange.Redis;
using Xunit;

namespace AuthSystem.Tests;

public sealed class RedisRefreshTokenStoreTests
{
    // Uses Moq to mock IDatabase — avoids implementing the 300+ member interface.
    private static (RedisRefreshTokenStore store, Dictionary<string, string> backing) Build()
    {
        var opts = Options.Create(new JwtSettings
        {
            RefreshTokenExpiryDays = 7,
            PrivateKeyPem = string.Empty,
            PublicKeyPem = string.Empty,
        });

        var backing = new Dictionary<string, string>();
        var mockDb = new Mock<IDatabase>();

        // StringSetAsync — write into backing dictionary
        // Match the (key, value, expiry, when) overload that the production code calls
        mockDb.Setup(db => db.StringSetAsync(
                It.IsAny<RedisKey>(), It.IsAny<RedisValue>(),
                It.IsAny<TimeSpan?>(), It.IsAny<When>()))
            .Callback<RedisKey, RedisValue, TimeSpan?, When>(
                (k, v, _, _) => backing[(string)k!] = v.ToString())
            .ReturnsAsync(true);

        mockDb.Setup(db => db.StringSetAsync(
                It.IsAny<RedisKey>(), It.IsAny<RedisValue>(),
                It.IsAny<TimeSpan?>(), It.IsAny<When>(), It.IsAny<CommandFlags>()))
            .Callback<RedisKey, RedisValue, TimeSpan?, When, CommandFlags>(
                (k, v, _, _, _) => backing[(string)k!] = v.ToString())
            .ReturnsAsync(true);

        // ScriptEvaluateAsync — simulate Lua GET+DEL
        mockDb.Setup(db => db.ScriptEvaluateAsync(
                It.IsAny<string>(), It.IsAny<RedisKey[]?>(),
                It.IsAny<RedisValue[]?>(), It.IsAny<CommandFlags>()))
            .Returns<string, RedisKey[]?, RedisValue[]?, CommandFlags>((_, keys, _, _) =>
            {
                if (keys is null || keys.Length == 0)
                    return Task.FromResult(RedisResult.Create(RedisValue.Null));
                var key = (string)keys[0]!;
                if (!backing.TryGetValue(key, out var val))
                    return Task.FromResult(RedisResult.Create(RedisValue.Null));
                backing.Remove(key);
                return Task.FromResult(RedisResult.Create((RedisValue)val));
            });

        // KeyDeleteAsync — remove from dictionary
        mockDb.Setup(db => db.KeyDeleteAsync(It.IsAny<RedisKey>(), It.IsAny<CommandFlags>()))
            .Returns<RedisKey, CommandFlags>((k, _) => Task.FromResult(backing.Remove((string)k!)));

        var mockMux = new Mock<IConnectionMultiplexer>();
        mockMux.Setup(m => m.GetDatabase(It.IsAny<int>(), It.IsAny<object?>()))
               .Returns(mockDb.Object);

        return (new RedisRefreshTokenStore(mockMux.Object, opts), backing);
    }

    [Fact]
    public async Task StoreAsync_ThenConsumeAsync_ReturnsData()
    {
        var (store, _) = Build();
        var data = new RefreshTokenData("uid", "e@test.com", "Name", null, DateTimeOffset.UtcNow.AddDays(7));

        await store.StoreAsync("tok123", data);
        var result = await store.ConsumeAsync("tok123");

        Assert.NotNull(result);
        Assert.Equal("uid", result.UserId);
        Assert.Equal("e@test.com", result.Email);
    }

    [Fact]
    public async Task ConsumeAsync_SecondCall_ReturnsNull_PreventingReplay()
    {
        var (store, _) = Build();
        var data = new RefreshTokenData("uid", "e@test.com", "Name", null, DateTimeOffset.UtcNow.AddDays(7));

        await store.StoreAsync("tok-replay", data);
        await store.ConsumeAsync("tok-replay");              // first consume — ok
        var second = await store.ConsumeAsync("tok-replay"); // replay attempt

        Assert.Null(second); // must be rejected — replay attack prevention
    }

    [Fact]
    public async Task RevokeAsync_RemovesToken()
    {
        var (store, backing) = Build();
        var data = new RefreshTokenData("uid", "e@test.com", "Name", null, DateTimeOffset.UtcNow.AddDays(7));

        await store.StoreAsync("tok-revoke", data);
        await store.RevokeAsync("tok-revoke");
        var result = await store.ConsumeAsync("tok-revoke");

        Assert.Null(result);
        Assert.False(backing.ContainsKey("refresh:tok-revoke"));
    }
}
