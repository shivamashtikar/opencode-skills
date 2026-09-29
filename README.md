# Opencode Skills

A collection of skills, prompts, and commands for [OpenCode](https://opencode.ai).

## Contents

- **[skills/](./skills/)** — Specialized agent skills
  - [codebase-analyzer](./skills/codebase-analyzer/SKILL.md) - Analyze, map, and understand complex codebases
- **[prompts/](./prompts/)** — System prompts for opencode agents
  - [build.txt](./prompts/build.txt) - Primary build agent prompt
  - [plan.txt](./prompts/plan.txt) - Plan mode (read-only) agent prompt
  - [explore.txt](./prompts/explore.txt) - Explore subagent prompt
- **[commands/](./commands/)** — Slash commands
  - [commit.md](./commands/commit.md) - Generate a semantic-release commit message (`/commit`)
  - [explain.md](./commands/explain.md) - Produce a technical overview of the codebase (`/explain`)

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
    "plan": {
      "mode": "primary",
      "system": "{file:./prompts/plan.txt}"
    },
    "explore": {
      "mode": "subagent",
      "system": "{file:./prompts/explore.txt}"
    }
  }
}
```

## Plan mode in OpenCode V2

The V1 `OPENCODE_EXPERIMENTAL_PLAN_MODE` environment variable and the `plan_exit` tool no longer exist in V2 — remove the variable from your shell profile if it is set. In V2:

- Agents replace modes. Switch between them with `Shift+Tab`, `Ctrl+X` then `A`, or `/agents`.
- The plan agent is read-only by permission: it may only write plan files under `~/.opencode/plan/`.
- The plan agent ends by presenting the plan and telling you to switch to the build agent to implement it.

## License

[MIT](./LICENSE)
