---
name: superhuman-newsletter
description: Fetches Superhuman AI newsletter posts and turns them into concise digests, recaps, reports, link roundups, or topic summaries. Use when the user asks for Superhuman AI newsletter content, recent AI news, a daily/weekly/monthly digest, "latest Superhuman" posts, or a source-linked report from superhuman.ai.
license: MIT
compatibility: Requires Python 3 and network access to public Beehiiv newsletter pages.
---

# Superhuman Newsletter

Fetch recent public Superhuman AI newsletter posts, synthesize the requested digest, and show the report in the conversation. Do not save files unless the user explicitly asks.

## Workflow

1. **Parse the request**
   - Digest type: daily recap, weekly digest, monthly report, link roundup, topic-focused summary, or "latest posts".
   - Range/count:
     - Explicit count: use that count.
     - Explicit days: estimate enough posts to cover the range, then filter/summarize by dates present in the fetched output.
     - "Daily" = 1 post, "weekly" = 7 posts, "monthly" = 30 posts, "latest" = 7 posts.
   - Focus: audience, topics, format, must-read links, tools, business impact, developer impact, or action items.

2. **Fetch source material**

   Run from this skill directory:

   ```bash
   python3 fetch-newsletter.py --source superhuman --count 7
   ```

   Adjust `--count` from the parsed request. The script writes progress to stderr and markdown content to stdout.

3. **Synthesize, don't paste**
   - Use the fetched markdown as source material, not final prose.
   - Include dates and source URLs for verification.
   - Prioritize what changed, why it matters, and what the reader can do next.
   - Deduplicate repeated stories, sponsor copy, ads, navigation, and boilerplate.
   - If the request asks for a time window, exclude fetched posts outside that window when dates are available.

4. **Show the report in the conversation**
   - Start with a short "Fetched" line: source, count, and observed date range.
   - Then provide the requested digest/report.
   - End with source links or a "Referenced posts" section.
   - Do not offer to save unless the user asks about saving/exporting.

## Output Patterns

### General digest

```markdown
Fetched: Superhuman AI — N posts, DATE–DATE

# Superhuman AI Digest

## Executive Summary
- ...

## Top Stories
1. **Title** — Summary. Why it matters. Source: URL

## Must-Read Links
- [Title](URL) — Why it is useful.

## Action Items
- ...
```

### Link roundup

```markdown
Fetched: Superhuman AI — N posts, DATE–DATE

# Superhuman AI Link Roundup

## Tools
- [Name](URL) — What it does and who should care.

## Research / Models
- ...

## Business / Policy
- ...
```

### Topic-focused report

```markdown
Fetched: Superhuman AI — N posts, DATE–DATE

# [Topic] in Recent Superhuman AI Posts

## Takeaways
- ...

## Evidence
- **Post title** (date) — Relevant point. Source: URL

## What to Watch
- ...
```

## Edge Cases

- **No posts found or fetch fails:** report the error and do not invent content.
- **Partial post failures:** produce the digest from successful posts and list failed source URLs separately.
- **Dates are missing or ambiguous:** state that the date range could not be confirmed and summarize by fetched order.
- **User requests The Code newsletter too:** the helper also supports `--source code`; fetch it only when explicitly requested.