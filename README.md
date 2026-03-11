# Opencode Skills

A collection of skills for [OpenCode](https://opencode.ai).

## Available Skills

- [codebase-analyzer](./skills/codebase-analyzer/SKILL.md) - Analyze, map, and understand complex codebases

## Installation

To use these skills, copy the skill folders to your `~/.config/opencode/skills/` directory:

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/shivamashtikar/opencode-skills.git
cd opencode-skills

# Create Skills directory if not exists
mkdir -p ~/.config/opencode/skills/

# Copy all skill folders to opencode skills directory
cp -r skills/* ~/.config/opencode/skills/
```

Or copy individual skills:
```bash
cp -r skills/codebase-analyzer ~/.config/opencode/skills/
```

To use prompts, copy the prompts folder to your `~/.config/opencode/prompts/` directory:

```bash
# Copy all prompts to opencode prompts directory
cp -r prompts ~/.config/opencode/
```

after this you need to update `~/.config/opencode/opencode.json` to use prompts in your agent

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

