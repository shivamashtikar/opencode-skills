---
description: Commit staged changes in semantic release format
agent: build
---

**Act as an expert software engineer. Your task is to analyze the currently staged git changes and the current branch name to generate a commit message strictly following the Conventional Commits (Semantic Release) format.**

**Here are the rules you must follow:**

**1. Format:** `<type>(<optional scope>): [Optional Ticket ID] <description>`

**2. Allowed Types:**
* `feat`: A new feature (triggers a MINOR release)
* `fix`: A bug fix (triggers a PATCH release)
* `docs`: Documentation only changes
* `style`: Changes that do not affect the meaning of the code (white-space, formatting, etc.)
* `refactor`: A code change that neither fixes a bug nor adds a feature
* `perf`: A code change that improves performance
* `test`: Adding missing tests or correcting existing tests
* `build`: Changes that affect the build system or external dependencies
* `ci`: Changes to CI configuration files and scripts
* `chore`: Other changes that don't modify `src` or `test` files
* `revert`: Reverts a previous commit

**3. Scope:** Keep it short, lower-case, and related to the specific module or component modified. Omit the scope if the change is global.

**4. Ticket ID Integration:** Analyze the name of the current git branch. If the branch name contains a pattern matching the regex `[A-Z]+-[0-9]+`, extract that ticket ID. Include it in the commit message heading, enclosed in square brackets, immediately before the description. If no such pattern exists, omit it.

**5. Description (Subject):**
* Use the imperative, present tense (e.g., "add" instead of "added").
* Do not capitalize the first letter.
* Do not put a period at the end.
* Keep it concise (under 50 characters if possible).

**6. Body (Optional):** If the change is complex, provide a brief body explaining *why* the change was made, not *how*. Wrap at 72 characters.

**7. Breaking Changes (Requires Confirmation):** If your analysis suggests that the staged changes introduce a breaking backward compatibility change, **STOP**. Do NOT generate the final commit message. Instead, report back to me with a brief explanation of why you suspect it is a breaking change, and explicitly ask:
* "Is my assumption correct that this is a breaking change?"
* "Should I mark this commit with a `!` and include the `BREAKING CHANGE:` footer?"

Wait for my reply before generating the commit command.

**8. Output Conditions:**
* **If NO breaking change is suspected:** Review the staged changes and provide **ONLY** the final executable `git commit -m "..." -m "..."` command. Do not output any extra conversational text or explanations.
* **If a breaking change IS suspected:** Output **ONLY** your reasoning and the confirmation questions outlined in Rule 7.

### CURRENT BRANCH:
!`git branch --show-current`
