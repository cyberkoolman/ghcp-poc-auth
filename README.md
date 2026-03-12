# GHCP PoC — OAuth2 + JWT Auth System

## Purpose

This repository is a **proof-of-concept learning project** exploring how GitHub Copilot's `/plan` agent works end-to-end — from prompting and planning, through code generation, to a fully functional, tested application.

The goal is not just the code itself, but to understand:
- How `/plan` interprets a high-level request and structures a phased implementation plan
- How the agent makes technology decisions through a clarifying questionnaire
- How it sequences implementation steps and maintains context across phases
- Where the planning intelligence comes from (the built-in `Plan` agent mode vs template files)
- How the generated code holds up to real build and test verification

---

## What Was Built

A production-patterned **user authentication system** using:

- **Google OAuth2** (Authorization Code Flow)
- **RS256-signed JWT** access tokens
- **Opaque refresh tokens** with rotation and replay prevention
- **Redis** for token storage with atomic Lua GET+DEL
- **React SPA** frontend with silent token refresh

### Stack

| Layer | Technology |
|---|---|
| Backend | ASP.NET Core 10 Web API (C#) |
| Auth Provider | Google OAuth2 via `Microsoft.AspNetCore.Authentication.Google` |
| Access Token | RS256 JWT, 15-minute expiry, in-memory on client |
| Refresh Token | 256-bit opaque, 7-day expiry, HttpOnly cookie |
| Token Store | Redis with atomic Lua script (replay prevention) |
| Frontend | React 19 + TypeScript + Vite 6 |
| HTTP Client | axios with request queue drain on concurrent 401s |
| Tests | xUnit + Moq (7 unit tests, all passing) |
| Security | CORS, rate limiting (10 req/min), security headers, SameSite=Strict |

---

## How `/plan` Was Used

### 1. Invocation

The session started with:
```
/plan Implement a user authentication system with OAuth2 and JWT
```

### 2. Clarifying Questionnaire

The `Plan` agent issued a questionnaire before generating any code:

| Question | Answer |
|---|---|
| Backend framework | .NET (ASP.NET Core) |
| OAuth2 provider | Google |
| OAuth2 flow | Authorization Code Flow |
| Token storage | Redis |
| Frontend | React SPA |
| Token strategy | Access + Refresh tokens |

### 3. Plan Output

The agent produced a **6-phase implementation plan** saved to session memory:

| Phase | Scope |
|---|---|
| 1 | Scaffold — solution, API project, test project, React frontend |
| 2 | Configuration — NuGet packages, `JwtSettings`, `appsettings.json` |
| 3 | Core services — `TokenService` (RS256 JWT), `RedisRefreshTokenStore` (Lua atomics) |
| 4 | Controller — 5 auth endpoints with secure cookie helpers |
| 5 | Frontend — `AuthContext`, axios interceptor, `ProtectedRoute`, pages |
| 6 | Security hardening — headers middleware, rate limiter, CORS |

### 4. Execution

After approving the plan with `Start implementation`, the agent executed all 6 phases sequentially, resolving real-world issues along the way (see [Obstacles Encountered](#obstacles-encountered)).

---

## What Was Learned About `/plan`

### The Template Is Minimal

The prompt file at `assets/prompts/plan.prompt.md` in the Copilot Chat extension is only 7 lines:

```yaml
---
name: plan
description: Research and plan with the Plan agent
agent: Plan
argument-hint: Describe what you want to plan or research
---
Plan my task.
```

The planning intelligence — questionnaire generation, phase structuring, technology selection — comes entirely from the **built-in `Plan` agent mode**, not from the template file. The file is just a routing declaration.

### How the Agent Builds Its Plan

The `Plan` agent:
1. Parses the request to identify the domain (auth system) and implied requirements
2. Identifies missing decisions and generates a targeted questionnaire
3. Uses answers to select concrete technologies and pattern trade-offs
4. Structures a sequenced, dependency-ordered implementation plan
5. Saves the plan to session memory so it persists across the implementation conversation

### Reference: `assets/prompts/` Structure

See [`docs/copilot-prompts-reference.md`](docs/copilot-prompts-reference.md) for a full breakdown of every file in the Copilot Chat extension's `assets/prompts/` directory — including all built-in slash commands and skills.

---

## Obstacles Encountered (and How They Were Resolved)

These were real issues hit during agent-driven implementation, not hypothetical:

| Problem | Root Cause | Fix |
|---|---|---|
| `.sln` file not found | .NET 10 `dotnet new sln` creates `.slnx` format | Used `AuthSystem.slnx` in subsequent commands |
| NuGet package version conflicts | Projects targeted `net8.0` but SDK was 10 | Upgraded both `.csproj` files to `net10.0` |
| `Authentication.Google` not found | No longer implicit in .NET 10 | Explicitly added as NuGet package |
| `npm create vite` `--template` flag intercepted by npm | npm consumed the flag before passing to create-vite | Used `npx -y create-vite@latest ... -- --template react-ts` |
| 300+ missing members on `IDatabase` fake | StackExchange.Redis v2.11 has a large interface | Replaced hand-rolled fake with Moq-based mock |
| Moq `StringSetAsync` setup didn't match actual call | Production code used implicit overload; Moq matched explicit | Changed production code to use explicit 5-param overload |

---

## Project Structure

```
GHCP/
├── AuthSystem.API/                  # ASP.NET Core 10 Web API
│   ├── Config/JwtSettings.cs        # Strongly-typed config record
│   ├── Controllers/AuthController.cs # 5 auth endpoints
│   ├── Models/AuthModels.cs         # DTOs: UserInfo, AuthResponse, RefreshTokenData
│   ├── Services/
│   │   ├── TokenService.cs          # RS256 JWT generation
│   │   └── RedisRefreshTokenStore.cs # Lua atomic token rotation
│   ├── Program.cs                   # DI wiring, middleware pipeline
│   └── appsettings.json             # Config skeleton (no secrets)
├── AuthSystem.Tests/                # xUnit + Moq unit tests (7 tests)
├── authsystem-frontend/             # React 19 + TypeScript + Vite
│   └── src/
│       ├── contexts/AuthContext.tsx  # In-memory auth state
│       ├── services/axiosInstance.ts # Auto-refresh with queue drain
│       ├── services/authService.ts   # Auth API calls
│       ├── components/ProtectedRoute.tsx
│       └── pages/                   # Login, Callback, Dashboard
├── docs/
│   └── copilot-prompts-reference.md # Breakdown of GHCP assets/prompts/
├── generate-keys.ps1                # RSA-2048 key pair generator
├── .gitignore
└── AuthSystem.slnx                  # .NET 10 solution file
```

---

## Running the Project

### Prerequisites
- .NET 10 SDK
- Node.js 20+
- Docker (for Redis) or a local Redis instance
- Google OAuth2 credentials ([Google Cloud Console](https://console.cloud.google.com))

### 1. Generate RSA Keys
```powershell
.\generate-keys.ps1
```

### 2. Set Secrets
```powershell
cd AuthSystem.API
dotnet user-secrets set "Jwt:PrivateKeyPem" "<private key output>"
dotnet user-secrets set "Jwt:PublicKeyPem" "<public key output>"
dotnet user-secrets set "Authentication:Google:ClientId" "<your client id>"
dotnet user-secrets set "Authentication:Google:ClientSecret" "<your client secret>"
```

### 3. Start Redis
```bash
docker run -p 6379:6379 redis
```

### 4. Run the API
```powershell
dotnet run --project AuthSystem.API
# Runs on https://localhost:7001
```

### 5. Run the Frontend
```powershell
cd authsystem-frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

### 6. Run Tests
```powershell
dotnet test
# Expected: Passed: 7, Failed: 0
```
