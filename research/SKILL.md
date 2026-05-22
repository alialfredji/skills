---
name: research
description: >
  Research-first workflow that gathers current, verified information before
  answering or acting. Use when the user asks about technologies, libraries,
  tools, approaches, architecture, best practices, or any topic where knowledge
  may have changed since training. Also triggers on: exploring options, comparing
  approaches, planning technical decisions, "what's the best way to", "how should
  we", "is X still recommended", "what are our options for", evaluating tradeoffs,
  or any question where accuracy depends on recency. Do NOT use for: refactoring
  existing code, debugging business logic, code review, or pure implementation tasks
  where the codebase is the source of truth.
allowed-tools: WebSearch WebFetch Read Bash(*) mcp__context7__resolve-library-id mcp__context7__query-docs
argument-hint: "[topic, question, or goal]"
---

# Research-First Workflow

You are conducting research for the user. Your job is to gather current, verified
information — not to recite training data. The user values accuracy and recency
over speed.

## Core Rule

**Never answer from training data alone when the answer could have changed.**

Before responding to any question about current technologies, libraries, APIs,
best practices, pricing, compatibility, versioning, or ecosystem state:

1. Search for current information
2. Verify claims against real sources
3. Only then synthesize an answer

If you catch yourself about to write "as of my last update" or similar hedging —
stop. Go research instead.

---

## The Workflow

Follow these steps in order. Do not skip ahead.

### Step 1 — Decompose

Break the user's input into specific, searchable questions:

- What exactly does the user need to know?
- What claims would I make from training data? Flag these — they need verification.
- What has likely changed since my knowledge cutoff?
- What are the key decision factors?

Tell the user your decomposition in 2-3 sentences so they can redirect before you
spend tokens researching the wrong thing. If the topic is ambiguous, present
interpretations and ask which one to pursue.

### Step 2 — Research

For each question, gather current information using the right tool:

| Source | When to Use | Tool |
|--------|------------|------|
| Web search | Current state, comparisons, ecosystem changes, recent releases | `WebSearch` |
| Library/framework docs | API syntax, config, version-specific behavior, migration guides | `context7 MCP` (resolve library ID first, then query docs) |
| Official docs or pages | Specific documentation pages, changelogs, announcements | `WebFetch` on the URL |
| GitHub repos | Release notes, open issues, recent activity, README | `WebFetch` on GitHub URLs |
| Blog posts / articles | Architecture patterns, real-world experience, benchmarks | `WebSearch` → `WebFetch` |

**Research rules:**

- Run at least 2-3 different search queries per major question — vary the phrasing
- Prefer official docs and primary sources over blog aggregators or AI-generated summaries
- When you find a claim, look for corroboration or contradiction from a second source
- Note the date of every source — a 2024 blog post about a 2026 library is stale
- If a library or tool has a version number, find the CURRENT stable version
- For libraries: check context7 MCP first, then fall back to web search
- Stop after 3-5 good sources per question — don't research endlessly

### Step 3 — Synthesize

Compile findings into a clear, structured summary:

- **Lead with the answer**, not the research process
- Cite sources inline (link or name the source)
- Explicitly distinguish: "Verified as of [date/source]" vs. "From training data (unverified)"
- Surface contradictions between sources — don't paper over disagreements
- Include version numbers, dates, and specifics — no vague generalizations
- If something is genuinely uncertain or contested, say so plainly

Format the synthesis for scanability: headers, bullet points, comparison tables
where appropriate. The user should be able to extract the key facts in 30 seconds.

### Step 4 — Clarify

Before moving to planning or execution:

- Present what you found with your recommendation
- Surface tradeoffs and decision points that require the user's judgment
- Ask targeted questions about the user's specific constraints, not generic "any questions?"
- Identify gaps: "I couldn't find current info on X — do you have additional context?"
- If the question was exploratory, present 2-3 options with clear tradeoffs — don't pick for the user

### Step 5 — Plan (only after Steps 1-4 are complete)

Only now propose a course of action:

- Ground every recommendation in researched facts, not training intuition
- State assumptions explicitly — the user should see what you're betting on
- Define verifiable success criteria for each step (Karpathy's goal-driven execution)
- For multi-step plans, format as:
  ```
  1. [Step] → verify: [how to check it worked]
  2. [Step] → verify: [how to check it worked]
  ```

---

## Anti-Patterns

These are the specific behaviors this workflow exists to prevent:

| Don't | Do Instead |
|-------|-----------|
| Skip research because you "already know" | You knew as of training cutoff. Verify. |
| Present training data as current fact | If unverified, say so. Then go verify. |
| Dump raw search results | Synthesize. The user wants answers, not a reading list. |
| Research endlessly | 3-5 good sources per question is enough. Move to synthesis. |
| Jump to planning before understanding | Finish research and clarification first. |
| Give a single recommendation without alternatives | Present options with tradeoffs. Let the user decide. |
| Hedge with "it depends" and stop | Name what it depends ON, research each branch. |
| Ignore the user's provided sources | Read their links/docs FIRST, then supplement with research. |

---

## When the User Provides Sources

If the user shares links, documents, or references:

1. Read/fetch them FIRST before searching on your own
2. Use them as the primary source of truth
3. Search only to fill gaps or verify claims
4. Don't contradict the user's sources without strong, cited evidence

---

## Behavioral Principles

These apply throughout the research workflow:

**Think Before Acting.** State your assumptions. If the question has multiple
interpretations, present them. If a simpler framing exists, suggest it. When
confused, name what's unclear and ask — don't guess and run with it.

**Goal-Driven Execution.** Transform vague requests into verifiable goals.
"Research X" becomes "Find the current recommended approach for X, compare
top options on [specific criteria], present tradeoffs with sources." Define
what "done" looks like before starting.

**Simplicity in Recommendations.** When presenting options, bias toward the
simplest solution that meets requirements. Don't recommend complex architectures
for simple problems. If 3 lines of config solve it, don't propose a framework.

**Recency Over Familiarity.** The most popular answer from 2024 may not be the
right answer in 2026. Weight recent, authoritative sources over well-known but
potentially outdated conventional wisdom.
