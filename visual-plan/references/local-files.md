# Local-files contract

Use this contract for every plan created with this skill.

## Boundaries

- Keep repository inspection, plan source, assets, validation, preview, and
  feedback on the local machine.
- Run the Plan viewer on an explicit loopback origin. The default is
  `http://127.0.0.1:8096`.
- Never call hosted Plan tools or use a remote Plan app as a fallback.
- Never send plan content to a block-catalog, validation, publish, comment, or
  analytics endpoint.
- A local visual plan does not make the coding model local. The model boundary
  remains the responsibility of the host agent configuration.

## Folder layout

Use `plans/<slug>/` for repository-owned plans:

```text
plans/<slug>/
├── plan.mdx
├── canvas.mdx          # optional static UI surface
├── prototype.mdx       # optional interactive surface
├── .plan-state.json    # optional stable source metadata
└── assets/             # optional local assets
```

Use the same directory in every check, verify, serve, and feedback edit. Treat
`.plan-url` as ephemeral and never commit it.

## Catalog and authoring

Start the local viewer before requesting the block catalog. Point the CLI at the
loopback app explicitly:

```bash
bash <skill-dir>/scripts/local-viewer.sh cli plan blocks \
  --app-url http://127.0.0.1:8096 \
  --format schema \
  --out plan-blocks.md
```

This catalog request must resolve to the local viewer. If it fails, use the
bundled references and the offline linter; do not retry against a remote app.

Important schema details:

- `checklist` items need `id` and `label`.
- `question-form` questions need `id`, `title`, and `mode`; each option needs
  `id` and `label`.
- `Code`, `AnnotatedCode`, and `Diff` are whitespace-sensitive. Encode
  multiline code as JSON string attributes such as
  `code={"const x =\n  y"}`.

## Check, verify, and preview

Run the offline syntax check first:

```bash
bash <skill-dir>/scripts/local-viewer.sh cli plan local check \
  --dir plans/<slug>
```

Then verify against the loopback renderer:

```bash
bash <skill-dir>/scripts/local-viewer.sh cli plan local verify \
  --dir plans/<slug> \
  --kind plan \
  --app-url http://127.0.0.1:8096
```

Require `validation.ran: true` and `validation.valid: true`. If validation does
not run, repair or start the local viewer; do not accept remote validation.

Open the plan through the loopback app only:

```bash
bash <skill-dir>/scripts/local-viewer.sh cli plan local serve \
  --dir plans/<slug> \
  --kind plan \
  --app-url http://127.0.0.1:8096 \
  --open
```

Reject any returned URL whose origin is not the configured loopback origin.
The direct route is:

```text
http://127.0.0.1:8096/local-plans/<slug>?path=plans%2F<slug>
```

Keep both the viewer and any bridge process running while the user reviews.

## Feedback

Treat feedback as file and chat feedback. Edit the MDX source directly, preserve
stable identifiers and unrelated content, rerun check and verify, then return
the refreshed loopback URL. Hosted comments, sharing, history, usage attachment,
and publish receipts are intentionally unavailable.
