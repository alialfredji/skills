# Recap quality bar

Read this file before authoring a recap.

## Evidence and scope

The diff is authoritative. Derive paths, change flags, schema fields, endpoint
contracts, literal before/after code, and UI labels from changed lines. Never
invent missing facts. Use conversation context and a prior plan only to explain
intent, and label conclusions not directly present in the diff as inference.

Cover the whole requested work unit without absorbing unrelated pre-existing
dirty changes. Before authoring, inventory the changed routes, components,
dialogs/popovers, states, permissions, schemas, endpoints, shared abstractions,
tests, and migrations. Represent every meaningful item or intentionally omit it
because it is small or redundant.

## Canonical shape

Use this order, omitting sections that do not apply:

1. UI wireframes or storyboard when rendered UI changed.
2. A one-to-three paragraph outcome narrative: what changed and why.
3. Optional **Plan alignment**: Delivered, Changed, Deferred.
4. Data-model, endpoint, compatibility, or architecture blocks.
5. A file tree covering the changed footprint with change flags.
6. `## Key changes` followed by one horizontal tabs block containing focused
   split diffs or annotated new-file excerpts.

Keep titles under roughly 70 characters and briefs to one to three sentences.
For a substantial change, use three to eight key-change tabs and keep each
excerpt near or below 150 lines. Prefer load-bearing files over exhaustive
coverage. A recap should be lean, but never so thin that the reviewer must
reconstruct its entire shape from the raw diff.

## Diff-to-block mapping

- Schema or migration: show the resulting data model, with added, modified,
  removed, or renamed fields and prior types where the diff supplies them.
- API, action, or route: show method, path, params, request, and responses from
  the implemented contract. Keep every JSON example a single valid JSON value.
- Compatibility risk: put a short breaking/risky/non-breaking note beside the
  relevant contract block and include the literal supporting diff.
- Existing code: use a split diff with real before/after text, filename,
  language, one-line summary, and a few high-signal annotations.
- New file or large new block: use annotated code when there is no meaningful
  before side.
- Added, removed, modified, or renamed files: use a file tree with matching
  change flags and only useful notes/snippets.
- Architecture or data flow: use a two-dimensional diagram such as layered,
  swimlane, or before/after panels. Do not use a diagram to imitate UI.
- Rendered UI: use wireframes grounded in actual labels, surfaces, roles, and
  states. Read the shared wireframe reference before authoring them.

Resolve conceptual block names against the live loopback block catalog. Every
structured block needs a stable unique ID. Use the catalog's exact tags and
schemas rather than remembered component names. Encode multiline `Code`,
`AnnotatedCode`, and `Diff` values as valid JSON string expressions.

## UI coverage

When UI changed, show the smallest set of surfaces that explains the actual
flow:

- the entry surface where the change appears;
- the interaction surface that opens or changes;
- the destination or persistent result;
- meaningful empty, error, loading, permission, or role variants.

Use before/after when direct comparison adds value, after-only for a purely
additive surface, and a short state sequence for flow-dependent work. Use the
real footprint (`browser`, `desktop`, `mobile`, `popover`, or `panel`) and do not
redraw a full page around a small sub-surface.

Read `../../visual-plan/references/wireframe.md` before any wireframe and
`../../visual-plan/references/canvas.md` before a top canvas. Visually inspect a
UI recap in the local viewer when browser tooling is available. Fix clipping,
overlap, contrast, or misleading controls before handoff.

## Plan alignment

A prior visual plan is optional. When one clearly belongs to the same work unit,
add a concise alignment section:

- **Delivered** — approved outcomes visibly present in the diff.
- **Changed** — implementation that differs from the approved approach, with a
  factual reason when the evidence or conversation supplies one.
- **Deferred** — approved scope absent from the implementation.

Do not score compliance, hide useful unplanned improvements, or claim an item
was delivered without diff evidence. Omit this section when no matching plan
exists.

## Security and self-review

Redact API keys, tokens, private-key blocks, webhook secrets, credential-bearing
URLs, `.env` values, and sensitive literals from every block and caption. Do not
assume automated scanning catches every secret.

Before handoff, confirm:

- the stated range matches the requested work unit;
- every structured claim traces to changed lines;
- the recap explains outcome and review risk without boilerplate;
- UI, contracts, and architecture use the right visual blocks;
- key evidence is focused, annotated, and secret-free;
- optional plan alignment treats the diff as authoritative;
- local check and renderer-backed verify pass.
