---
name: visual-recap
description: >-
  Turn a completed implementation, PR, branch, commit, or working-tree diff
  into a repository-owned interactive recap with file maps, API/schema
  summaries, annotated diffs, diagrams, and UI wireframes. Use after meaningful
  multi-file, UI, architecture, API, or data-model changes need review, and keep
  both the recap source and viewer on the local machine.
---

# Local Visual Recaps

Create a recap **from** implemented changes. The Git diff is the source of truth:
a prior visual plan is optional and provides intent context only. Store recap
source as local MDX and review it in the same loopback viewer as `visual-plan`.

## Local-only invariant

Read [references/local-files.md](references/local-files.md) before collecting or
serving a recap. Never publish recap content, call hosted Plan tools, install a
GitHub Action, or open a non-loopback Plan route. Use
`http://127.0.0.1:8096` unless the user explicitly chooses another loopback port.

The sibling `visual-plan` skill owns the shared runtime. Resolve its installed
directory as `<visual-plan-skill-dir>` and read
`../visual-plan/references/local-runtime.md` before the first preview in a
session. If the sibling skill or its `scripts/local-viewer.sh` is unavailable,
report that the local visual-plan runtime is required; do not substitute a
hosted viewer.

## Decide whether a recap helps

- Create one for a substantial PR, branch, commit, or work unit; multi-file
  changes; rendered UI; schemas or API contracts; architecture; or risky
  compatibility behavior.
- Skip a tiny, single-file, or obvious diff. Tell the user the plain diff is the
  clearer review surface.
- Cover the whole requested work unit, including follow-up fixes and tests.
  Exclude unrelated dirty changes that predate the work.
- Ask one concise scope question only when the intended base/head or ownership
  of dirty changes cannot be established safely.

## Workflow

1. Resolve the work unit and preserve its exact base/head or working-tree scope.
   Inspect `git status`, `git log`, `git diff --stat`, and the diff itself.
2. Create a temporary collection directory outside the repository. For a
   committed range, collect the inputs with the installed recap CLI:

   ```bash
   bash <visual-plan-skill-dir>/scripts/local-viewer.sh cli recap collect-diff \
     --base <base-sha> --head <head-sha> \
     --out <tmp-dir>/recap.diff --stat <tmp-dir>/recap.stat
   bash <visual-plan-skill-dir>/scripts/local-viewer.sh cli recap scan \
     --diff <tmp-dir>/recap.diff --mode high-confidence
   ```

   For working-tree changes, write the equivalent tracked, staged, and relevant
   untracked inputs with local Git commands, then scan the collected diff. Never
   commit temporary diff, stat, prompt, catalog, or `.plan-url` files.
3. Start the existing viewer against the repository's plans root:

   ```bash
   bash <visual-plan-skill-dir>/scripts/local-viewer.sh bootstrap
   bash <visual-plan-skill-dir>/scripts/local-viewer.sh serve "$PWD/plans"
   ```

4. Fetch the authoritative block catalog from that loopback viewer:

   ```bash
   bash <visual-plan-skill-dir>/scripts/local-viewer.sh cli plan blocks \
     --app-url http://127.0.0.1:8096 \
     --format schema --out <tmp-dir>/plan-blocks.md
   ```

   If the catalog is unavailable, use the bundled/shared references and rely on
   local checking. Never retry against a remote endpoint.
5. Read [references/recap-quality.md](references/recap-quality.md). For rendered
   UI changes, also read `../visual-plan/references/wireframe.md`; for a top
   storyboard, read `../visual-plan/references/canvas.md`.
6. If an approved `plans/<slug>/plan.mdx` exists for the same work, compare its
   intent with the diff and add a concise **Plan alignment** section:
   **Delivered**, **Changed**, and **Deferred**. Omit the section when no prior
   plan exists. Never let planned intent override implemented evidence.
7. Write `plans/<slug>-recap/plan.mdx` with `kind: "recap"` and
   `localOnly: true`. Add `canvas.mdx` only when a top UI storyboard materially
   improves review. Ground structured facts mechanically in changed lines and
   label any inference as inference.
8. Check and verify against the loopback renderer:

   ```bash
   bash <visual-plan-skill-dir>/scripts/local-viewer.sh cli plan local check \
     --dir plans/<slug>-recap
   bash <visual-plan-skill-dir>/scripts/local-viewer.sh cli plan local verify \
     --dir plans/<slug>-recap --kind recap \
     --app-url http://127.0.0.1:8096
   ```

   Require `validation.ran: true` and `validation.valid: true` unless a clearly
   reported local runtime blocker prevents renderer verification.
9. Open only the loopback route:

   ```bash
   bash <visual-plan-skill-dir>/scripts/local-viewer.sh cli plan local serve \
     --dir plans/<slug>-recap --kind recap \
     --app-url http://127.0.0.1:8096 --open
   ```

   Reject any returned URL that does not begin with the configured loopback
   origin. Return that URL and the recap source path to the user.
10. Apply feedback by editing the local MDX directly, preserving unrelated
    blocks and stable identifiers. Rerun check and verify after every revision.

## Authoring invariants

- Lead with UI impact when UI changed; otherwise lead with the actual outcome.
- Include the changed file tree and focused evidence for every recap-worthy
  change. Do not replace evidence with a prose-only summary.
- Use split diffs for meaningful before/after code and annotated code for
  substantial new files. Keep excerpts focused and secret-free.
- Include data-model, endpoint, architecture, or compatibility blocks only when
  the diff contains the facts required to construct them.
- Redact credentials, tokens, private keys, webhook secrets, and sensitive
  literal values everywhere, including captions and snippets.
- Keep the artifact standalone. Do not depend on chat history to explain scope,
  decisions, or review risks.
- Do not commit `.plan-url`; it contains an ephemeral local bridge token.

## Handoff

Report the resolved diff range, the local recap URL, the source directory, and
the check/verify result. Mention whether plan alignment was included. For a
repository-owned recap reviewed on another machine, explain that the reviewer
must check out the files and run the local viewer there; loopback URLs are not
shareable.
