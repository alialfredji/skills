---
name: visual-plan
description: >-
  Turn implementation plans into local, interactive MDX review artifacts with
  diagrams, file maps, annotated code, open questions, wireframes, and optional
  prototypes. Use when a coding task needs visual planning, architecture or data
  review, UI direction, a reviewable approval gate, or a richer version of an
  existing text plan, and keep both the plan files and viewer on the local machine.
---

# Local Visual Plans

Create the plan as a repository-owned MDX artifact and review it in the local
Plan viewer. Never publish plan content, call hosted Plan tools, or open a hosted
Plan route. Use `http://127.0.0.1:8096` unless the user explicitly chooses a
different loopback port.

## Plan discipline

- Inspect the real repository before drafting. Name actual files, symbols,
  actions, schemas, helpers, and tests.
- Decide hard-to-reverse choices first: public identifiers, wire formats, data
  shape, authentication, ownership, migration boundaries, and rollout.
- Keep the first implementation slice small without foreclosing the intended
  architecture. State what is included and deferred.
- Treat existing text plans as source material. Produce a standalone document,
  not a revision memo.
- Make no implementation edits while planning. The visual plan is the approval
  gate; start implementation only after the user approves it.
- Ask only questions that materially change the direction. Put unresolved
  decisions in one bottom `question-form` block with a recommended default.
- Skip visual planning for trivial, unambiguous, one-line work.

## Local-only invariant

Read [references/local-files.md](references/local-files.md) before creating or
serving a plan. The following are prohibited:

- Hosted Plan MCP tools, including create, update, feedback, share, publish, and
  export actions.
- Any `agent-native.com` or other non-loopback Plan viewer URL.
- Uploading plan MDX, assets, repository context, or feedback to a Plan service.
- Falling back to a hosted viewer when the local viewer is unavailable.

If the local viewer cannot run, still author and check the MDX locally, report
the plan directory, and explain the local runtime blocker.

## Runtime

Read [references/local-runtime.md](references/local-runtime.md) before the first
preview in a session.

Bootstrap the open-source viewer once:

```bash
bash <skill-dir>/scripts/local-viewer.sh bootstrap
```

Start it in a long-running terminal with the target repository's plans root:

```bash
bash <skill-dir>/scripts/local-viewer.sh serve "$PWD/plans"
```

The viewer must listen on `http://127.0.0.1:8096`. Keep it running through
review. Use the same URL explicitly in every check, verify, and serve command.

## Workflow

1. Inspect the repository and any source plan. Keep this phase read-only.
2. Choose a slug and create `plans/<slug>/` containing `plan.mdx`, plus optional
   `canvas.mdx`, `prototype.mdx`, `.plan-state.json`, and `assets/`.
3. Start the local viewer. Fetch the renderer's block catalog from that viewer:

   ```bash
   bash <skill-dir>/scripts/local-viewer.sh cli plan blocks \
     --app-url http://127.0.0.1:8096 \
     --format schema \
     --out plan-blocks.md
   ```

   If the local catalog is unavailable, use the bundled references and rely on
   local checking. Never fetch the catalog from a remote endpoint.
4. Read [references/document-quality.md](references/document-quality.md) and
   [references/exemplar.md](references/exemplar.md). For UI work, also read
   [references/wireframe.md](references/wireframe.md) and
   [references/canvas.md](references/canvas.md).
5. Author a standalone plan grounded in the inspected code. Use document blocks
   for technical depth and a top canvas only when the work is visually oriented.
6. Check and verify against the loopback renderer:

   ```bash
   bash <skill-dir>/scripts/local-viewer.sh cli plan local check \
     --dir plans/<slug>
   bash <skill-dir>/scripts/local-viewer.sh cli plan local verify \
     --dir plans/<slug> \
     --kind plan \
     --app-url http://127.0.0.1:8096
   ```

7. Open only the loopback route:

   ```bash
   bash <skill-dir>/scripts/local-viewer.sh cli plan local serve \
     --dir plans/<slug> \
     --kind plan \
     --app-url http://127.0.0.1:8096 \
     --open
   ```

   Confirm the returned URL begins with `http://127.0.0.1:8096/`. If it does
   not, stop and do not open it.
8. Give the user the local URL and plan path, name the implementation areas the
   plan touches, and request approval before editing source code.
9. Apply feedback by editing the MDX files directly. Rerun check and verify after
   every revision; the files, not chat, remain the source of truth.

## Visual surface choice

- Use no top visual surface for backend-only, architecture-only, migration,
  copy-only, API-contract, or data-flow work. Put diagrams beside the claims
  they explain in `plan.mdx`.
- Use canvas only for a static screen, state, popover, before/after comparison,
  or visual direction.
- Use canvas plus prototype for multi-step flows, onboarding, wizards,
  navigation changes, or review interactions.
- Use prototype-first when interaction is the primary question.
- Default to renderer-owned wireframes. Use full-fidelity design only when the
  user explicitly asks for branded, pixel-accurate, or production-like screens.

For UI plans, make the first artboard resemble the real product shell and
density. Keep UI frames separate from architecture diagrams and implementation
notes. Reuse the same labels, states, and screen identifiers across canvas and
prototype files.

## Authoring invariants

- Keep `plan.mdx` self-contained and outcome-first. Lead with the recommendation
  and concrete user or system effect.
- Use real runtime line breaks in Markdown data, not literal `\n` text.
- Give every block, artboard, screen, annotation, question, and option a stable,
  unique identifier where the schema requires one.
- Encode multiline `Code`, `AnnotatedCode`, and `Diff` attributes as valid JSON
  string expressions.
- Keep canvas artboards non-scrolling. Increase frame height when necessary and
  inspect the bottom edge at default zoom.
- Preserve all unrelated MDX when revising. Make targeted file edits rather
  than regenerating the entire artifact.
- Never commit `.plan-url`; it may contain a local bridge token.
- Do not consider a plan complete until both local check and renderer-backed
  verify pass, or until a clearly reported local runtime blocker prevents the
  renderer verification.

## Self-review

Before handoff, check that the plan:

- anchors every implementation step in real files or symbols;
- commits to one recommended direction instead of presenting an unranked menu;
- addresses hard-to-reverse decisions explicitly;
- separates product UI, system mechanics, and explanatory notes;
- includes realistic verification and rollout steps;
- contains no filler, duplicated visuals, remote URLs, or hosted workflows.

For security-sensitive or irreversible work, run an additional skeptical review
of the written artifact. Apply clear fixes directly to the MDX and leave genuine
judgment calls in the bottom open-questions block.
