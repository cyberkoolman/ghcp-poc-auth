# GitHub Copilot Chat — `assets/prompts` Reference

> Extension: `github.copilot-chat-0.38.2`  
> Path: `assets/prompts/`

This folder is Copilot's **meta-customization layer** — the tools that teach the agent how to help *you* customize the agent itself. The `create-*` prompts are your entry points; the skills and reference docs are the detailed knowledge they load behind the scenes.

---

## Root-level `.prompt.md` files

These are the **built-in slash commands** you can invoke in chat by typing `/`.

| File | Slash Command | Purpose |
|---|---|---|
| `plan.prompt.md` | `/plan` | Routes to the built-in `Plan` agent for research & planning |
| `init.prompt.md` | `/init` | Bootstraps a `copilot-instructions.md` or `AGENTS.md` file for your workspace by exploring the codebase and generating conventions |
| `create-agent.prompt.md` | `/create-agent` | Guides you through creating a custom `.agent.md` file (a specialized persona with restricted tools) |
| `create-hook.prompt.md` | `/create-hook` | Guides you through creating a hook `.json` that enforces policy at lifecycle events (`PreToolUse`, `SessionStart`, etc.) |
| `create-instructions.prompt.md` | `/create-instructions` | Guides you through creating a `.instructions.md` file (persistent coding rules/conventions) |
| `create-prompt.prompt.md` | `/create-prompt` | Guides you through creating a new reusable `.prompt.md` slash command |
| `create-skill.prompt.md` | `/create-skill` | Guides you through creating a `SKILL.md` skill that packages a multi-step workflow |

All six `create-*` prompts follow the same pattern:
1. Look at your conversation history to infer what you want
2. Ask clarifying questions if needed
3. Draft the file and save it
4. Suggest related customizations

---

## `skills/` subdirectory

These are **built-in skills** — loaded automatically by the agent when the task description matches.

### `skills/agent-customization/`

The master reference skill used internally by all the `create-*` prompts above.

| File | Purpose |
|---|---|
| `SKILL.md` | Decision-flow table for when to use each customization primitive (instructions vs skill vs prompt vs agent vs hook), plus creation checklist and common pitfalls |
| `references/agents.md` | Full template + frontmatter spec for `.agent.md` — tool aliases, model fallback, `user-invocable`, `disable-model-invocation` |
| `references/hooks.md` | Full spec for hook `.json` — events, stdin/stdout contract, `permissionDecision`, exit codes |
| `references/instructions.md` | Spec for `.instructions.md` — `applyTo` glob patterns, on-demand vs explicit discovery, anti-patterns |
| `references/prompts.md` | Spec for `.prompt.md` — frontmatter options, tool priority rules, when prompts vs skills |
| `references/skills.md` | Spec for `SKILL.md` — folder structure, progressive loading (discovery → instructions → resources), slash command behavior |
| `references/workspace-instructions.md` | Template for `copilot-instructions.md` / `AGENTS.md` — monorepo hierarchy, what to include/exclude |

### Other built-in skills

| Folder | Purpose |
|---|---|
| `skills/get-search-view-results/` | Teaches the agent how to programmatically read the VS Code Search panel via `search.action.getSearchResults` |
| `skills/install-vscode-extension/` | Teaches the agent how to install a VS Code extension by ID using `workbench.extensions.installExtension` |
| `skills/project-setup-info-context7/` | How to scaffold a new project using the Context7 MCP tools (`resolve-library-id` + `get-library-docs`) |
| `skills/project-setup-info-local/` | How to scaffold projects locally — includes templates for VS Code extensions (Yeoman/generator-code), Next.js, and other project types |

---

## Customization Primitive Quick Reference

Sourced from `skills/agent-customization/SKILL.md`:

| Primitive | File Type | Location | When to Use |
|---|---|---|---|
| Workspace Instructions | `copilot-instructions.md` or `AGENTS.md` | `.github/` or root | Always-on rules that apply to every task in the project |
| File Instructions | `*.instructions.md` | `.github/instructions/` | Rules scoped to specific file types or task contexts |
| Prompts | `*.prompt.md` | `.github/prompts/` | Single focused, reusable task with parameterized inputs |
| Hooks | `*.json` | `.github/hooks/` | Deterministic enforcement via shell commands at lifecycle events |
| Custom Agents | `*.agent.md` | `.github/agents/` | Specialized persona with restricted tools and context isolation |
| Skills | `SKILL.md` | `.github/skills/<name>/` | Multi-step workflow with bundled scripts/templates/references |

### Decision Shortcuts

- **Instructions vs Skill?** Applies to *most* work → Instructions. Specific on-demand task → Skill.
- **Skill vs Prompt?** Multi-step workflow with assets → Skill. Single focused task → Prompt.
- **Skill vs Custom Agent?** Same tools throughout → Skill. Need context isolation or different tools per stage → Custom Agent.
- **Hooks vs Instructions?** Instructions *guide* (non-deterministic). Hooks *enforce* via shell commands (deterministic, can block).

### Common Pitfalls

- **Description is the discovery surface.** The `description` field is how the agent decides whether to load a skill, instruction, or agent. If trigger phrases aren't in the description, the agent won't find it.
- **YAML frontmatter silent failures.** Unescaped colons in values, tabs instead of spaces, or a `name` that doesn't match the folder name all cause silent failures with no error message. Always quote descriptions containing colons: `description: "Use when: doing X"`.

---

## Where Your Own Customizations Live

| Scope | Path |
|---|---|
| Workspace (team-shared) | `.github/prompts/`, `.github/instructions/`, `.github/agents/`, `.github/hooks/`, `.github/skills/` |
| User profile (personal, roams with settings sync) | `%APPDATA%\Code\User\prompts\` (Windows) |
