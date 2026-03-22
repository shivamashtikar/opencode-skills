# Opencode Skills

A collection of skills for [OpenCode](https://opencode.ai).

## Available Skills

- [codebase-analyzer](./skills/codebase-analyzer/SKILL.md) - Analyze, map, and understand complex codebases

## Installation

To use these skills, copy the skills, prompts and commands folders to your `~/.config/opencode/` directory:

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/shivamashtikar/opencode-skills.git
cd opencode-skills

# Copy all skills to opencode skills directory
cp -r skills ~/.config/opencode/

# Copy all prompts to opencode prompts directory
cp -r prompts ~/.config/opencode/

# Copy all commands to opencode commands directory
cp -r commands ~/.config/opencode/
```

after this you need to update `~/.config/opencode/opencode.json` to use prompts and commands in your agent

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
