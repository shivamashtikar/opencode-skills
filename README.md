# Opencode Skills

A collection of skills, prompts, and commands for [OpenCode](https://opencode.ai).

## Contents

- **[skills/](./skills/)** — Specialized agent skills
  - [codebase-analyzer](./skills/codebase-analyzer/SKILL.md) - Analyze, map, and understand complex codebases
- **[prompts/](./prompts/)** — System prompts for opencode agents
  - [build.txt](./prompts/build.txt) - Primary build agent prompt
  - [plan.txt](./prompts/plan.txt) - Plan mode (read-only) agent prompt
  - [explore.txt](./prompts/explore.txt) - Explore subagent prompt
  - [build-switch.txt](./prompts/build-switch.txt) - Plan→build transition reminder
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
curl -sL https://raw.githubusercontent.com/shivamashtikar/opencode-skills/main/prompts/build-switch.txt -o ~/.config/opencode/prompts/build-switch.txt
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

Update `~/.config/opencode/opencode.json` to wire the prompts and commands into your agents:

```json
{
  "agent": {
    "build": {
      "mode": "primary",
      "prompt": "{file:./prompts/build.txt}"
    },
    "plan": {
      "mode": "primary",
      "prompt": "{file:./prompts/plan.txt}"
    },
    "explore": {
      "mode": "subagent",
      "prompt": "{file:./prompts/explore.txt}"
    }
  }
}
```

> **Note:** The `build-switch.txt` prompt is injected automatically by opencode when transitioning from plan mode to build mode — it does not need to be referenced in `opencode.json`.

## Required Environment Variable

The `plan.txt` prompt uses the `plan_exit` tool for the plan→build handoff. This tool is only available when opencode's experimental plan mode is enabled. Set this environment variable in your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
export OPENCODE_EXPERIMENTAL_PLAN_MODE=1
```

Without this flag, the `plan_exit` tool is not registered and the agent cannot call it — you would need to manually switch from plan to build mode.

## License

[MIT](./LICENSE)
