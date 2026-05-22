---
name: setup-ai-context
description: Set up cross-tool AI context files (AGENTS.md, CLAUDE.md, Copilot, path-scoped rules, tribal knowledge, glossary, decision records) for any project — new or legacy. Use when starting a new project, onboarding a legacy codebase for AI-assisted development, or auditing an existing AI context setup.
disable-model-invocation: true
allowed-tools: Bash(*) Read Write Edit
argument-hint: "[new|legacy|audit]"
---

# Setup AI Context — Cross-Tool Configuration

You are setting up AI context files for a software project. Your goal is to create a lean, high-signal set of files that maximizes AI agent effectiveness across multiple tools (Claude Code, GitHub Copilot, Cursor, OpenCode, Codex, Windsurf, Zed, and others).

## Core Principles

1. **Less is dramatically more.** Anthropic's own CLAUDE.md is 44 lines. Instruction-following degrades uniformly as file length increases. Frontier LLMs follow ~150-200 instructions total; the system prompt uses ~50, leaving ~100-150 for context files.
2. **Focus on what the AI can't figure out by reading code.** Commands, gotchas, non-obvious constraints, boundaries. Never document what's inferrable.
3. **Never use context files as a linter.** Style rules belong in ESLint/Prettier/Biome with hooks, not in AGENTS.md.
4. **Show, don't tell.** One code example beats three paragraphs.
5. **Constraints > conventions.** Explicit "NEVER do X because Y" rules are the highest-signal content you can write.
6. **Success criteria > step-by-step.** Write "after this change, tests pass and no console.log in diff" not "step 1: open file, step 2: edit line..."

## Tool Coverage Matrix

| File | Claude Code | Copilot | Cursor | OpenCode | Codex | Windsurf | Zed |
|:--|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| AGENTS.md | via @import | Yes | Yes | Yes | Yes | Yes | Yes |
| CLAUDE.md | Yes | Yes | — | Yes | — | — | Yes |
| .github/copilot-instructions.md | — | Yes | — | — | — | — | — |
| .github/instructions/*.instructions.md | — | Yes (path-scoped) | — | — | — | — | — |
| .claude/rules/*.md | Yes (path-scoped) | Yes (VS Code) | — | — | — | — | — |

---

## Phase 1 — Detect Project State

Run these commands silently to understand the project before asking questions:

### Tech Stack Detection
!`find . -maxdepth 2 -type f \( -name "package.json" -o -name "Cargo.toml" -o -name "pyproject.toml" -o -name "go.mod" -o -name "Gemfile" -o -name "pom.xml" -o -name "build.gradle" -o -name "pubspec.yaml" -o -name "composer.json" -o -name "mix.exs" \) 2>/dev/null | head -20`

### Existing AI Config Files
!`for f in AGENTS.md CLAUDE.md .cursorrules .windsurfrules .github/copilot-instructions.md; do test -f "$f" && echo "EXISTS: $f ($(wc -l < "$f") lines)" || echo "MISSING: $f"; done 2>/dev/null`

### Project Structure
!`find . -maxdepth 2 -type d \( -name "src" -o -name "lib" -o -name "packages" -o -name "apps" -o -name "services" -o -name "modules" -o -name "components" -o -name "api" -o -name "test" -o -name "tests" -o -name "__tests__" -o -name "docs" \) 2>/dev/null | sort | head -30`

### Existing Documentation
!`for f in README.md CONTRIBUTING.md docs/adr docs/decisions docs/glossary.md docs/tribal-knowledge.md; do test -e "$f" && echo "EXISTS: $f" || echo "MISSING: $f"; done 2>/dev/null`

### Git Maturity
!`git log --oneline -5 2>/dev/null || echo "NO_GIT_HISTORY"`

### Monorepo Detection
!`test -f "pnpm-workspace.yaml" && echo "MONOREPO: pnpm workspaces" || test -f "lerna.json" && echo "MONOREPO: lerna" || test -f "nx.json" && echo "MONOREPO: nx" || test -f "turbo.json" && echo "MONOREPO: turborepo" || (node -e "try{const p=require('./package.json');if(p.workspaces)console.log('MONOREPO: npm/yarn workspaces')}catch{}" 2>/dev/null) || echo "SINGLE_PACKAGE"`

### Package Manager Detection
!`test -f "pnpm-lock.yaml" && echo "PM: pnpm" || test -f "yarn.lock" && echo "PM: yarn" || test -f "bun.lockb" && echo "PM: bun" || test -f "package-lock.json" && echo "PM: npm" || test -f "Cargo.lock" && echo "PM: cargo" || test -f "poetry.lock" && echo "PM: poetry" || test -f "Pipfile.lock" && echo "PM: pipenv" || test -f "go.sum" && echo "PM: go modules" || echo "PM: unknown"`

### Existing Commands (from package.json or Makefile)
!`test -f package.json && node -e "try{const p=require('./package.json');const s=p.scripts||{};Object.keys(s).slice(0,15).forEach(k=>console.log(k+': '+s[k]))}catch{}" 2>/dev/null || test -f Makefile && grep -E '^[a-zA-Z_-]+:' Makefile | head -10 2>/dev/null || echo "NO_SCRIPTS_FOUND"`

---

## Phase 2 — Interview

Based on the detection results above, ask the user the following questions. Adapt based on what was detected — skip questions you can already answer from Phase 1.

### Question 1: AI Tools (always ask)
Ask the user which AI coding tools their team uses. Offer multi-select:
- Claude Code (CLI/IDE)
- GitHub Copilot (IDE + coding agent)
- Cursor
- OpenCode
- Codex (OpenAI)
- Windsurf
- Other

### Question 2: Project Domain & Terminology (always ask)
Ask: "Describe what this project does in 1-2 sentences. Then list 3-5 domain-specific terms that someone new wouldn't know (e.g., 'event_id is the UUID primary key across all services', 'a Workflow is a sequence of Steps that execute in order')."

### Question 3: Tribal Knowledge (the most valuable question — always ask)
Ask: "What are the non-obvious things that would bite a new developer working on this project? Think about:"
- Hidden dependencies between modules
- Deployment or environment quirks
- "Never do X because Y" rules
- Things that work in dev but break in staging/prod
- Non-obvious testing requirements
- Files or areas that are fragile or dangerous to modify

Give examples to help the user think:
- "The auth token expires after 1 hour in dev but 7 days in prod — tests hardcode the dev value"
- "Service A and Service B share a cache — changes to one can invalidate the other"
- "Don't edit database migrations — always create new ones"
- "Deployment order matters: API must deploy before workers, or queues stall"

### Question 4: Key Architectural Decisions (always ask)
Ask: "What are 2-3 key technical decisions the team has made? Format: 'We chose X over Y because Z.'"
Examples:
- "We chose PostgreSQL over MongoDB because we need strong transactional guarantees"
- "We use a monorepo because the API and frontend share types"
- "We chose server-side rendering because SEO is critical for our use case"

### Question 5: Legacy Migration (only if existing AI config files detected)
If Phase 1 found existing files (AGENTS.md, .cursorrules, .windsurfrules, copilot-instructions.md), ask:
"I found existing AI config files: [list them]. How would you like to handle them?"
- **Consolidate**: Read them, extract the valuable parts, merge into the new AGENTS.md structure
- **Keep alongside**: Create new files without touching existing ones (gradual migration)
- **Replace**: Archive old files, create fresh setup

---

## Phase 3 — Generate Files

Generate files based on detection results and user answers. Follow these rules strictly:

### File Size Targets (ENFORCE THESE)
| File | Target Lines | Absolute Max |
|:-----|:------------|:-------------|
| AGENTS.md | 60-100 | 120 |
| CLAUDE.md | 20-40 | 50 |
| .github/copilot-instructions.md | 10-20 | 30 |
| Path-scoped rules (each) | 15-30 | 50 |
| docs/tribal-knowledge.md | 25-35 per section | — |
| docs/glossary.md | 500-1000 tokens total | — |
| docs/decisions/*.md | ~30 per file | — |

### 3.1 — AGENTS.md (ALWAYS generate — this is the canonical file)

Structure the file with these sections in this order (skip sections that don't apply):

```markdown
# [Project Name]

## Overview
[1-2 sentences: what this project does and who it's for]

## Tech Stack
[Language, framework, database, infrastructure — with versions where it matters]

## Commands
[Exact commands with all flags. These are the highest-value lines in the file.]
| Command | Purpose |
|---------|---------|
| `cmd` | what it does |

## Project Structure
[Key directories and what they contain — only the ones that matter]

## Code Conventions
[Only conventions that differ from language defaults or that the AI would get wrong]

## Key Terms
[Top 5-10 domain terms with code identifiers — this makes the glossary available to ALL tools]
- **term** (`code_identifier`): brief definition + constraint

## Architecture
[5-10 lines max. Module boundaries and what breaks if you cross them. Data flow for the critical path only. Not theory — operational facts.]

## Things That Will Bite You
[The tribal knowledge section — the single most valuable part. Non-obvious constraints, hidden dependencies, environment quirks, "never do X because Y" rules.]

## Testing
[How to run tests. What coverage looks like. Non-obvious testing requirements.]

## Git Workflow
[Branch naming, PR conventions, CI requirements — only if non-standard]
```

### 3.2 — CLAUDE.md (ALWAYS generate)

Structure:
```markdown
@AGENTS.md
@docs/glossary.md
@docs/tribal-knowledge.md

## Claude Code

[Claude-specific behavior rules — things that only matter for Claude Code, not other tools]
[Examples: plan mode preferences, commit behavior, testing requirements before suggesting changes]
```

Keep this VERY short. Most content lives in AGENTS.md. CLAUDE.md is just the import hub plus Claude-specific additions.

### 3.3 — .github/copilot-instructions.md (if Copilot selected)

Structure:
```markdown
Refer to AGENTS.md at repository root for full project context.

## Copilot-Specific
[Only Copilot-specific behavior — commit message format, PR description format, code review focus areas]
```

### 3.4 — Path-Scoped Rules (if project has distinct modules)

Generate BOTH formats with identical content, different frontmatter:

**For Claude Code** — `.claude/rules/[module-name].md`:
```markdown
---
paths:
  - "src/api/**/*.ts"
  - "src/api/**/*.tsx"
---

[Module-specific rules — 15-30 lines focused on this area only]
```

**For Copilot** — `.github/instructions/[module-name].instructions.md`:
```markdown
---
applyTo: "src/api/**/*.ts,src/api/**/*.tsx"
---

[Identical content to the Claude rule above]
```

Only create rules for modules where there are specific non-obvious constraints. Don't create rules just because a directory exists.

### 3.5 — .claude/settings.json (if Claude Code selected)

Create a minimal baseline:
```json
{
  "permissions": {
    "allow": [],
    "deny": []
  }
}
```

Only add permissions based on detected project commands (e.g., allow the test command, allow the lint command).

### 3.6 — docs/tribal-knowledge.md (ALWAYS generate)

Follow Meta's 4-section format, one section per module or area:

```markdown
# Tribal Knowledge

## [Module/Area Name]

### Quick Commands
- `command` — what it does

### Key Files
- `/path/to/file` — why it matters

### Non-Obvious Patterns
- **Don't**: [what not to do] — [why]
- **Do**: [what to do instead]
- [Environment-specific behavior]
- [Hidden dependencies]

### See Also
- Related: [other module]
- Depends on: [dependency]
```

Populate with what the user shared in the tribal knowledge interview question.

### 3.7 — docs/glossary.md (ALWAYS generate)

Use YAML-style format with code identifiers:

```markdown
# Project Glossary

## [Domain Area]

- **Term** (`code_identifier`)
  Definition in one sentence.
  Constraints: [validation rules, never-null, format requirements]
  Related: [other_term, another_term]
```

Populate with terms from the user's domain description. Include how each term appears in code.

### 3.8 — docs/decisions/ (ALWAYS generate directory + template)

Create three files:

**docs/decisions/README.md**:
```markdown
# Decision Records

This directory contains architectural and technical decisions using the AgDR (Agent Decision Record) format.

## How to Add a Decision
1. Copy `000-template.md`
2. Rename to `NNN-short-description.md` (increment the number)
3. Fill in all sections
4. Commit with message: `docs: add decision NNN — short description`

## Index
[List of decisions — update when adding new ones]
```

**docs/decisions/000-template.md**:
```markdown
# [Decision Title]

**Status**: [proposed | accepted | rejected | superseded by NNN]
**Date**: YYYY-MM-DD
**Decision Makers**: [who]

## Y-Statement
In the context of **[situation]**,
facing **[concern]**,
we decided **[decision]**
to achieve **[goal]**,
accepting **[tradeoff]**.

## Options Considered

| Option | Pros | Cons |
|--------|------|------|
| Option A | ... | ... |
| Option B | ... | ... |

## Decision
[Which option was chosen and why]

## Consequences
- [What changes as a result]
- [What new constraints this introduces]
- [What becomes easier or harder]
```

**Seed 1-2 real decisions** from the user's answer to Question 4. For example, if they said "We chose PostgreSQL over MongoDB because we need transactional guarantees," create `docs/decisions/001-postgresql-over-mongodb.md` with that decision filled in.

### 3.9 — Monorepo: Nested AGENTS.md (if monorepo detected)

For each detected workspace/package, create a short AGENTS.md (20-40 lines):
```markdown
# [Package Name]

## Purpose
[What this package does — 1 sentence]

## Commands
[Package-specific commands]

## Things That Will Bite You
[Package-specific gotchas — especially cross-package dependencies]

## Dependencies
- Imports from: [list]
- Imported by: [list]
- Shared resources: [caches, databases, queues that this package touches]
```

Root AGENTS.md acts as router with pointers to package-level files.

---

## Phase 4 — Validate & Summarize

After generating all files:

1. **Show a summary table** of every file created/updated with its line count
2. **Calculate approximate token budget**: sum all files that load at session start (AGENTS.md + CLAUDE.md + always-loaded rules). Report as percentage of ~150 instruction budget.
3. **Warn if any file exceeds target size** — suggest what to cut
4. **For legacy projects**: show what was migrated and what was preserved
5. **Suggest next steps**:
   - "Run a test task with Claude Code to verify the setup works"
   - "Add rules only after the 2nd occurrence of a mistake — the first might be a fluke"
   - "Review these files quarterly — remove anything that references technologies or patterns no longer in use"
   - "When a code review catches something the AI should have known, add it to tribal-knowledge.md"

---

## Argument Handling

The skill accepts an optional argument: `$ARGUMENTS`

- **`new`** or no argument: Full setup from scratch. Skip legacy migration questions.
- **`legacy`**: Emphasize detection of existing config and migration options.
- **`audit`**: Read existing AI context files and report: file sizes, potential bloat, missing coverage, stale references, files that exceed recommended lengths. Don't generate — just analyze and recommend.
