# Skills

A collection of reusable skills for AI coding agents. Each skill is a self-contained directory with a `SKILL.md` file that can be installed into any Claude Code project or user profile.

## Available Skills

| Skill | Description |
|:------|:------------|
| [setup-ai-context](./setup-ai-context/) | Set up cross-tool AI context files for any project (new or legacy). Generates AGENTS.md, CLAUDE.md, Copilot instructions, path-scoped rules, tribal knowledge, glossary, and decision records. |

## Installation

### Per-project (recommended for team use)

Copy a skill directory into your project's `.claude/skills/`:

```bash
cp -r setup-ai-context /path/to/your/project/.claude/skills/
```

### User-level (available in all your projects)

Symlink into your global skills directory:

```bash
ln -s /path/to/skills/setup-ai-context ~/.claude/skills/setup-ai-context
```

### Usage

Once installed, invoke the skill by name in Claude Code:

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
