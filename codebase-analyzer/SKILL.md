---
name: codebase-analyzer
description: Analyze, map, and understand complex codebases using parallel exploration with opencode's built-in tools. Use this skill when implementing features in unfamiliar code, debugging issues by tracing code paths, fixing bugs across service boundaries, adding functionality to existing systems, onboarding to new projects, performing deep-dive code reviews, tracing data flows, or refactoring code. Triggers on requests like "help me understand this codebase", "analyze this architecture", "how does X work in this code", "find where this is used", "fix this bug", "implement this feature", "debug this issue", "add to this codebase", "modify this code", "trace the data flow", "map dependencies", "explore the project structure", or when users need to understand code to make changes.
license: MIT
compatibility: opencode
metadata:
  audience: developers, reviewers, architects
  workflow: exploration, onboarding, refactoring
  max_depth: 3
  parallel_agents: enabled
---

## What I do

- **Strategic Exploration**: Identify optimal entry points and navigation strategies for unfamiliar codebases using `glob` and `grep`
- **Parallel Analysis**: Use opencode's `explore` and `general` subagents to explore multiple code paths simultaneously
- **Pattern Detection**: Recognize architectural patterns, state management, and API boundaries across the codebase
- **Dependency Mapping**: Trace imports, data flows, and service dependencies using `grep` and `codesearch`
- **Technical Debt Discovery**: Identify undocumented logic, anti-patterns, and areas needing attention
- **Cross-Reference Analysis**: Build understanding by connecting related components across files

## When to use me

**Perfect for:**

- Onboarding to new projects or large legacy systems
- Preparing for major refactoring or re-architecture
- Deep-dive code reviews on complex architectures
- Understanding data flows through multi-layered systems
- Tracing bugs across service boundaries
- Documenting undocumented systems

**Ask clarifying questions if:**

- The programming language or framework isn't specified
- You need specific domain knowledge (e.g., medical, financial)
- You have time constraints (some analyses may take longer)

## Quick Start: 5-Minute Codebase Overview

Use these parallel `task` calls to get a rapid orientation:

```
Task 1 (@explore): "Find and summarize the project structure at root level. List top-level directories and their apparent purposes."
Task 2 (@explore): "Identify the main entry points and bootstrapping code. Look for files named main, index, app, server, or similar."
Task 3 (@explore): "List all configuration files and their purposes. Check for package.json, tsconfig.json, .env files, etc."
Task 4 (@explore): "Find documentation (README, docs folder, inline comments in key files)."
```

**Primary model synthesizes:** Merge findings into a coherent overview with architecture notes.

## Deep Analysis Workflows

### 1. Architecture Mapping

**Goal:** Understand the high-level structure and component relationships

**Phase 1 - Parallel Component Discovery (using @explore subagent):**

```
Task A: "Find all service/module definitions and their interfaces. Search for files containing 'class', 'interface', 'service', 'module' patterns."
Task B: "Identify data models, schemas, and type definitions. Look for model files, schema definitions, types."
Task C: "Locate configuration and environment setup files. Find config directories and environment-specific files."
Task D: "Find API endpoints, routes, or public interfaces. Search for route definitions, controller files, handlers."
```

**Phase 2 - Parallel Relationship Tracing:**

```
Task A: "Trace how the main service depends on other services. Use grep to follow import/require chains."
Task B: "Map data flow from API endpoint to database. Follow request handling through storage."
Task C: "Identify shared utilities and common patterns. Look for utils, helpers, common directories."
```

**Primary model:** Create architecture overview and identify key integration points.

### 2. Data Flow Analysis

**Goal:** Trace how data moves through the system

**Parallel Exploration (using @explore):**

```
Task 1: "Find where [data entity] is created/ingested. Search for constructor calls, factory functions, or API endpoints that create this entity."
Task 2: "Trace [data entity] through validation/transformation layers. Follow the data through validation, parsing, transformation."
Task 3: "Find where [data entity] is stored/persisted. Locate database operations, storage calls."
Task 4: "Identify where [data entity] is consumed/displayed. Find UI components, API responses, or downstream consumers."
Task 5: "Find event triggers and side effects related to [data entity]. Look for event emitters, listeners, or side effects."
```

**Primary model:** Synthesize into a complete data flow description with state transitions.

### 3. Pattern Recognition

**Goal:** Identify recurring patterns and conventions

**Parallel Pattern Search (using @explore):**

```
Task A: "Find error handling patterns across the codebase. Look for try/catch, error boundaries, error classes."
Task B: "Identify logging/monitoring patterns and conventions. Search for logger imports, metric collections."
Task C: "Locate state management patterns. Look for Redux, Context, stores, or state containers."
Task D: "Find testing patterns and conventions. Search for test files, describe/it blocks, assertion patterns."
Task E: "Identify naming conventions and code style patterns. Analyze file structures and naming."
```

**Primary model:** Document patterns with examples and note inconsistencies.

### 4. Technical Debt Audit

**Goal:** Find areas needing attention

**Parallel Audit (using @explore):**

```
Task 1: "Find TODO/FIXME/HACK comments and their context. Use grep to locate all such markers."
Task 2: "Identify files with high complexity. Look for files with many conditionals, long functions, or large classes."
Task 3: "Find duplicated code or logic. Search for similar function implementations or repeated patterns."
Task 4: "Locate deprecated patterns or libraries. Look for deprecation comments, old API usage."
Task 5: "Identify undocumented public APIs or complex functions. Find exported functions lacking documentation."
```

**Primary model:** Prioritize findings by impact and effort.

## Tool Orchestration Strategies

### Chain: Discovery → Detail → Synthesis

```
Step 1 (Discovery): Use `glob` to find relevant files
  glob pattern: "**/*.{ts,tsx}"  # Find all TypeScript files

Step 2 (Detail): Use `grep` to search within discovered files
  grep pattern: "class.*Service"  # Find service classes

Step 3 (Synthesis): Use `read` to examine key files
  read: specific file paths from grep results
```

### Chain: Search → Cross-Reference → Map

```
Step 1 (Search): Use `grep` to find all usages
  grep pattern: "function.*handleSubmit"

Step 2 (Cross-Reference): Use `glob` to find related test files
  glob pattern: "**/*.test.ts"  # Find tests

Step 3 (Map): Use `read` to understand relationships
  read: main function file + test file
```

### Using codesearch for External Context

When analyzing code that uses external libraries:

```
codesearch query: "React useEffect cleanup patterns"
codesearch query: "Express middleware error handling"
```

This provides documentation and examples from the broader ecosystem.

## Subagent Prompt Templates

### Entry Point Finder

```
Find the best entry point to understand [specific feature/concept] in this codebase.

Instructions:
1. Use glob to find files related to [feature/concept]
2. Use grep to search for [feature/concept] in file contents
3. Look for main files that initialize or bootstrap this feature
4. Check for configuration that enables/disables it
5. Find test files that demonstrate usage
6. Look for documentation or comments explaining it

Return: File paths, line numbers, and brief description of what each contains.
```

### Pattern Analyzer

```
Analyze [file(s)/directory] for [specific pattern, e.g., "authentication flow"].

Instructions:
1. Use grep to find all files related to [pattern]
2. Read key files to understand the implementation
3. Identify:
   - Where this pattern starts and ends
   - Key functions/classes involved
   - Dependencies it relies on
   - How it handles errors/edge cases
   - Any configuration or environment variables

Return: Structured breakdown with code snippets and file:line references.
```

### Dependency Mapper

```
Map all dependencies of [module/file/class].

Instructions:
1. Read the main file to understand its imports
2. Use grep to find where this module is imported by others
3. Find:
   - Direct imports and their purposes
   - Indirect dependencies (transitive)
   - Circular dependencies if any
   - External vs internal dependencies
   - Dependencies on shared state or global config

Return: Dependency tree with annotations about coupling strength.
```

### Cross-Reference Builder

```
Find all usages of [function/class/constant] across the codebase.

Instructions:
1. Use grep to search for all occurrences
2. For each usage, note:
   - File and line number
   - Context (what feature/module is using it)
   - How it's being used (called, extended, imported, etc.)
   - Any patterns or conventions in usage

Return: Categorized list with context for each usage.
```

## Language-Specific Entry Point Patterns

### TypeScript/JavaScript

```
Entry point patterns:
- package.json "main" or "exports" field
- Files: index.ts, main.ts, app.ts, server.ts
- Directories: src/, lib/, dist/
- Config: tsconfig.json, vite.config.ts, webpack.config.js

Use: glob "**/package.json" then read to find entry points
```

### Python

```
Entry point patterns:
- Files: __main__.py, main.py, app.py, server.py, manage.py
- Directories with __init__.py
- Config: requirements.txt, pyproject.toml, setup.py
- Entry points defined in setup.py or pyproject.toml

Use: glob "**/__main__.py" and glob "**/requirements.txt"
```

### Go

```
Entry point patterns:
- Files: main.go (in cmd/ directory)
- Directories: cmd/, pkg/, internal/
- Config: go.mod (defines module and dependencies)
- Look for package main declarations

Use: grep "package main" to find executables
```

### Rust

```
Entry point patterns:
- Files: main.rs (binaries), lib.rs (libraries)
- Config: Cargo.toml (workspace, dependencies)
- Directories: src/bin/ for multiple binaries
- Look for fn main() definitions

Use: grep "^fn main()" to find entry points
```

### Java/Kotlin

```
Entry point patterns:
- Files with public static void main method
- Config: build.gradle, pom.xml
- Directories: src/main/java/, src/test/java/
- Look for @SpringBootApplication or similar

Use: grep "public static void main" to find entry points
```

### Haskell

```
Entry point patterns:
- Files: Main.hs (executables), Lib.hs (libraries)
- Config: package.yaml, *.cabal, stack.yaml, cabal.project
- Directories: app/ (executables), src/ (libraries), test/ (tests)
- Look for module Main where declarations
- Check executables section in .cabal or package.yaml

Use: grep "module Main" to find entry points
glob "**/*.cabal" or glob "**/package.yaml" for config
```

### PureScript

```
Entry point patterns:
- Files: Main.purs (entry point)
- Config: spago.dhall, spago.yaml, bower.json
- Directories: src/, test/
- FFI files: *.js alongside *.purs
- Look for module Main declarations

Use: grep "module Main" to find entry points
glob "**/spago.dhall" for project config
```

### ReScript

```
Entry point patterns:
- Files: *.res (implementation), *.resi (interfaces)
- Config: bsconfig.json or rescript.json
- Directories: src/
- Look for @react.component or similar decorators
- Check "sources" and "bs-dependencies" in config

Use: glob "**/bsconfig.json" or glob "**/rescript.json" for config
read bsconfig.json to find entry points
```

## Advanced Techniques

### 1. Multi-Layer Analysis

For complex systems with multiple layers (frontend, API, database):

```
Layer 1 (Parallel using @explore):
  Task A: "Analyze frontend components. Find React/Vue components, hooks, state management."
  Task B: "Analyze API routes/handlers. Find controllers, endpoints, middleware."
  Task C: "Analyze database models/queries. Find ORM models, SQL, migrations."

Layer 2 (Parallel):
  Task A: "Map frontend → API calls. Find where frontend makes API requests."
  Task B: "Map API → database operations. Trace from handlers to database."

Layer 3 (Primary model):
  Synthesize complete request lifecycle
```

### 2. Temporal Analysis

For understanding how the system evolves:

```
Task 1: "Analyze recent commits to understand active development areas. Use git log."
Task 2: "Find migration files or version changes. Look for migrations, changelogs."
Task 3: "Identify deprecated code and replacement patterns. Search for deprecated markers."
Task 4: "Find changelog or release notes. Look for CHANGELOG, RELEASES files."
```

### 3. Comparative Analysis

For understanding variations:

```
Task A: "Analyze how Feature X is implemented in Module 1"
Task B: "Analyze how Feature X is implemented in Module 2"
Task C: "Analyze how Feature X is implemented in Module 3"

Primary model: Compare implementations and identify best practices vs inconsistencies
```

## Output Formats

Choose based on your goal:

### Architecture Overview

```markdown
# [Project Name] Architecture

## High-Level Structure

- [Component diagram description]

## Key Components

1. **[Component Name]** (files: [paths])
   - Purpose: [description]
   - Dependencies: [list]
   - Key patterns: [patterns]

## Data Flows

1. **[Flow Name]**: [source] → [intermediate steps] → [destination]
```

### Detailed Analysis Report

```markdown
# Deep Dive: [Topic]

## Entry Points

- [File:Line] - [Description]

## Key Functions/Classes

1. **[Name]** ([file:line])
   - Purpose: [description]
   - Parameters: [list]
   - Returns: [description]
   - Side effects: [if any]

## Data Flow

[Step-by-step with code snippets]

## Dependencies

- Internal: [list with coupling notes]
- External: [list]

## Patterns Used

- [Pattern name]: [example location]

## Technical Debt

- [Issue]: [location] - [severity]
```

### Quick Reference Card

```markdown
# [Feature] Quick Reference

## Start Here

- [Best entry point file]

## Key Files

| Purpose   | File   | Line   |
| --------- | ------ | ------ |
| [purpose] | [path] | [line] |

## Common Patterns

- [Pattern]: [Example location]

## Gotchas

- [Issue]: [Where it occurs]
```

## Best Practices for Subagent Usage

### 1. Scope Appropriately

- **Too broad:** "Analyze the entire codebase" → Subagent gets overwhelmed
- **Just right:** "Find all authentication-related files and summarize their roles"

### 2. Provide Context

Always include relevant findings from previous subagents:

```
"Based on Task A's finding that [X], now analyze how [Y] relates to it."
```

### 3. Validate Assumptions

After subagents report, verify critical findings:

```
"Subagent found [pattern X]. Confirm this by checking [specific file] directly."
```

### 4. Iterative Refinement

Start broad, then drill down:

```
Phase 1: "Find all API routes" (using @explore)
Phase 2: "For each route found, analyze its handler" (using @general)
Phase 3: "For complex handlers, trace data flow" (using @explore)
```

## Common Pitfalls

### 1. Over-Parallelization

Don't create subagents for trivial tasks that take <30 seconds.
**Good:** 4-6 subagents for complex analysis
**Bad:** 20 subagents each checking one file

### 2. Missing Context

Subagents lack full conversation context. Include necessary background in prompts.

### 3. Circular Dependencies

When analyzing circular deps, limit depth to prevent infinite loops.

### 4. Incomplete Synthesis

Don't just list subagent outputs - synthesize into coherent understanding.

## Performance Tips

1. **Cache intermediate results** - Save subagent findings to reference later
2. **Reuse findings** - Build on previous analysis instead of starting fresh
3. **Limit scope** - Analyze one subsystem at a time for large codebases
4. **Use grep first** - Quick searches can guide subagent tasks
5. **Read READMEs** - Often contain architecture overviews
6. **Use glob smartly** - Be specific with patterns to reduce noise

## Example Sessions

### Example 1: New Developer Onboarding

**User:** "Help me understand this authentication system"

**Workflow:**

1. **Parallel discovery** (4 @explore tasks):
   - Find auth-related files
   - Locate user models/schemas
   - Find middleware/guards
   - Identify auth endpoints

2. **Synthesis** → Architecture overview with auth flow description

3. **Deep dive** (3 @general tasks):
   - Analyze login flow
   - Analyze token handling
   - Analyze session management

4. **Final output** → Complete auth system documentation

### Example 2: Refactoring Preparation

**User:** "I need to refactor the data layer, what's the scope?"

**Workflow:**

1. **Impact analysis** (5 @explore tasks):
   - Find all database models
   - Map model relationships
   - Find all database queries
   - Identify external dependencies on data layer
   - Find test coverage for data layer

2. **Synthesis** → Refactoring plan with risk assessment

3. **Detailed mapping** (4 @explore tasks):
   - Trace each model's usage
   - Identify coupling points
   - Find transaction boundaries
   - Locate data migrations

4. **Final output** → Comprehensive refactoring guide

## Troubleshooting

### Subagents return conflicting information

**Solution:** Launch a verification task to reconcile:

```
"Task A found [X] but Task B found [Y]. Verify which is correct by checking [specific files]."
```

### Analysis is taking too long

**Solution:** Narrow scope or split into multiple sessions:

```
"Focus only on the API layer. We'll analyze the database layer in a follow-up session."
```

### Can't find entry points

**Solution:** Use broader search patterns:

```
"Find files with 'main', 'init', 'bootstrap', 'start', or 'server' in their name or content"
```

### Codebase is too large

**Solution:** Use a phased approach:

```
Phase 1: High-level module overview (use @explore)
Phase 2: Focus on one module at a time (use @general)
Phase 3: Cross-module integration analysis (use @explore)
```
