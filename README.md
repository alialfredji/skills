# Skills

A collection of reusable skills for AI coding agents. Each skill is a self-contained directory with a `SKILL.md` file that can be installed into any Claude Code project or user profile.

## Available Skills

| Skill | Description |
|:------|:------------|
| [setup-ai-context](./setup-ai-context/) | Set up cross-tool AI context files for any project (new or legacy). Generates AGENTS.md, CLAUDE.md, Copilot instructions, path-scoped rules, tribal knowledge, glossary, and decision records. |
| [research](./research/) | Research-first workflow that gathers current, verified information before answering or acting. Prevents stale training-data answers by enforcing: decompose → research → synthesize → clarify → plan. |
| [code-discipline](./code-discipline/) | Behavioral guardrails for disciplined coding. Four principles: Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution. |
| [visual-plan](./visual-plan/) | Create repository-owned visual implementation plans and review them through a loopback-only local Plan viewer. |
| [visual-recap](./visual-recap/) | Turn implemented changes into repository-owned visual recaps reviewed through the loopback-only local Plan viewer. |

## Installation

```bash
npx skills add https://github.com/alialfredji/skills
```

### Usage

Once installed, invoke any skill by name in Claude Code:

```
/setup-ai-context          # Full setup from scratch
/setup-ai-context new      # Explicit new project mode
/setup-ai-context legacy   # Emphasize migration of existing config
/setup-ai-context audit    # Analyze existing setup without generating files
```

## Skill Structure

Each skill follows this convention:

```
skill-name/
├── SKILL.md          # Required: instructions + YAML frontmatter
├── templates/        # Optional: reference templates
├── scripts/          # Optional: helper scripts
└── examples/         # Optional: example outputs
```

## Adding a Skill

1. Create a new directory with a descriptive name
2. Add a `SKILL.md` with YAML frontmatter (`name`, `description`, `disable-model-invocation`, etc.)
3. Update this README's table
4. Commit and push

## License

MIT
