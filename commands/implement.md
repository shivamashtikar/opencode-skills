---
description: Execute the plan — switches the session to the build agent
agent: build
---

**Act as the build agent and execute the plan.** This session just finished planning — implement the plan now.

**Plan file (if specified):** $ARGUMENTS

**Latest plan in this project:**
!`ls -t .opencode/plan 2>/dev/null | grep '\.md$' | head -1 | sed 's|^|.opencode/plan/|'`

**Instructions:**

1. Read the plan file: prefer the path given above if one was provided with the command; otherwise use the latest plan. If no plan file exists, stop and tell the user there is nothing to implement.
2. Skim the critical files listed in the plan to confirm the codebase still matches its assumptions. If something has drifted in a way that invalidates the plan, report it and ask before proceeding.
3. Implement the plan step by step as written. Do not redesign it or expand scope; if a step is genuinely wrong, fix it and note the deviation in your final summary.
4. Run the plan's verification section (tests, lint, build, etc.) and fix any failures your changes introduced.
5. End with a concise summary: what changed, files touched, and verification results.
