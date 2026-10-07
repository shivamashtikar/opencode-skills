# Opencode Skills

A collection of skills, prompts, and commands for [OpenCode](https://opencode.ai).

## Contents

- **[skills/](./skills/)** — Specialized agent skills
  - [codebase-analyzer](./skills/codebase-analyzer/SKILL.md) - Analyze, map, and understand complex codebases
  - [html](./skills/html/SKILL.md) - Generate self-contained Bootstrap 5 HTML reports with Chart.js charts and Mermaid diagrams
  - [pdf](./skills/pdf/SKILL.md) - Generate polished PDF reports with ReportLab + matplotlib
- **[prompts/](./prompts/)** — System prompts for opencode agents
  - [build.txt](./prompts/build.txt) - Primary build agent prompt
  - [plan.txt](./prompts/plan.txt) - Planner (read-only) agent prompt
  - [explore.txt](./prompts/explore.txt) - Explore subagent prompt
- **[commands/](./commands/)** — Slash commands
  - [commit.md](./commands/commit.md) - Generate a semantic-release commit message (`/commit`)
  - [explain.md](./commands/explain.md) - Produce a technical overview of the codebase (`/explain`)
  - [implement.md](./commands/implement.md) - Execute the plan by switching to the build agent (`/implement`)

## Installation

### Quick install (prompts only)

To grab just the agent prompts without cloning the repo, `curl` each file directly into `~/.config/opencode/prompts/`:

```bash
mkdir -p ~/.config/opencode/prompts
curl -sL https://raw.githubusercontent.com/shivamashtikar/opencode-skills/main/prompts/build.txt       -o ~/.config/opencode/prompts/build.txt
curl -sL https://raw.githubusercontent.com/shivamashtikar/opencode-skills/main/prompts/plan.txt        -o ~/.config/opencode/prompts/plan.txt
curl -sL https://raw.githubusercontent.com/shivamashtikar/opencode-skills/main/prompts/explore.txt     -o ~/.config/opencode/prompts/explore.txt
```

> **Note:** Use the `raw.githubusercontent.com` URLs as shown above — the `github.com/.../blob/main/...` URLs return the HTML page, not the file content.

### Full installation

Copy the `skills`, `prompts`, and `commands` folders into your `~/.config/opencode/` directory:

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/shivamashtikar/opencode-skills.git
cd opencode-skills

# Copy skills, prompts, and commands to opencode config directory
cp -r skills   ~/.config/opencode/
cp -r prompts  ~/.config/opencode/
cp -r commands ~/.config/opencode/
```

## Configuration

Update `~/.config/opencode/opencode.json` to wire the prompts and commands into your agents (OpenCode V2 shape):

```json
{
  "$schema": "https://opencode.ai/config.json",
  "agents": {
    "build": {
      "mode": "primary",
      "system": "{file:./prompts/build.txt}"
    },
    "planner": {
      "mode": "primary",
      "description": "Read-only planning agent. Researches, writes plans to .opencode/plan/, and hands off to the build agent.",
      "system": "{file:./prompts/plan.txt}",
      "permissions": [
        { "action": "question", "resource": "*", "effect": "allow" },
        { "action": "edit", "resource": "*", "effect": "deny" },
        { "action": "edit", "resource": ".opencode/plan/*", "effect": "allow" },
        { "action": "shell", "resource": "*", "effect": "ask" },
        { "action": "shell", "resource": "ls*", "effect": "allow" },
        { "action": "shell", "resource": "pwd", "effect": "allow" },
        { "action": "shell", "resource": "cd*", "effect": "allow" },
        { "action": "shell", "resource": "cat*", "effect": "allow" },
        { "action": "shell", "resource": "grep*", "effect": "allow" },
        { "action": "shell", "resource": "rg*", "effect": "allow" },
        { "action": "shell", "resource": "find*", "effect": "allow" },
        { "action": "shell", "resource": "head*", "effect": "allow" },
        { "action": "shell", "resource": "tail*", "effect": "allow" },
        { "action": "shell", "resource": "wc*", "effect": "allow" },
        { "action": "shell", "resource": "which*", "effect": "allow" },
        { "action": "shell", "resource": "file*", "effect": "allow" },
        { "action": "shell", "resource": "stat*", "effect": "allow" },
        { "action": "shell", "resource": "du*", "effect": "allow" },
        { "action": "shell", "resource": "df*", "effect": "allow" },
        { "action": "shell", "resource": "git status*", "effect": "allow" },
        { "action": "shell", "resource": "git log*", "effect": "allow" },
        { "action": "shell", "resource": "git diff*", "effect": "allow" },
        { "action": "shell", "resource": "git show*", "effect": "allow" },
        { "action": "shell", "resource": "git branch*", "effect": "allow" },
        { "action": "shell", "resource": "git blame*", "effect": "allow" },
        { "action": "shell", "resource": "git rev-parse*", "effect": "allow" },
        { "action": "shell", "resource": "git ls-files*", "effect": "allow" },
        { "action": "shell", "resource": "git grep*", "effect": "allow" }
      ]
    },
    "explore": {
      "mode": "subagent",
      "system": "{file:./prompts/explore.txt}"
    }
  }
}
```

## Planning agent in OpenCode V2

The V1 `OPENCODE_EXPERIMENTAL_PLAN_MODE` environment variable and the `plan_exit` tool no longer exist in V2 — remove the variable from your shell profile if it is set. In V2, agents replace modes; switch between them with `Shift+Tab`, `Ctrl+X` then `A`, or `/agents`.

V2's built-in `plan` agent injects a per-turn reminder ("do not create plan files unless the user explicitly asks") and hardcodes its plan directory to the global `~/.opencode/plan/` — neither is configurable. This repo's prompt is therefore wired to a custom `planner` agent instead:

- Always writes the plan file at Phase 4 — never asks "Want me to save this?"
- Stores plans project-locally under `.opencode/plan/`, so plans from different projects never collide
- Read-only by permission: `edit` is denied everywhere except `.opencode/plan/*`; shell is limited to read-only commands (`ls`, `cat`, `grep`, `git log/diff/status`, ...) — anything else prompts instead of running silently (ssh MCP tools follow the global permission rules)
- Ends by presenting the plan and telling you to run `/implement`, which switches the session to the build agent and points it at the plan file (or switch manually with `Shift+Tab` / `/agents`)

Add `.opencode/plan/` to your global git ignores (`~/.config/git/ignore`) so plans don't get committed. The built-in `Plan` agent remains available in the agent switcher if you prefer V2's default discussion-first behavior.

## License

[MIT](./LICENSE)
