# Local recap contract

Use this contract for every recap created with this skill.

## Privacy boundary

- Read source, history, diffs, stats, and prior plans from local files and Git.
- Keep recap MDX, assets, validation, preview, and feedback on the local machine.
- Run the viewer on an explicit loopback origin, normally
  `http://127.0.0.1:8096`.
- Never call hosted create, update, feedback, publish, share, export, analytics,
  screenshot, or visibility actions.
- Never send a diff, recap, repository context, asset, or feedback to a remote
  block catalog or validator.
- A local recap does not make the coding model local; model privacy remains the
  responsibility of the host agent configuration.

The installed recap CLI is local-safe only for `collect-diff`, `scan`, and
`build-prompt --local-files`. Do not use its setup, publish, comment, usage,
shot, or other hosted/PR automation commands.

## Folder layout

Use a repository-owned folder when the recap should travel with the branch:

```text
plans/<slug>-recap/
├── plan.mdx
├── canvas.mdx          # optional UI storyboard
├── prototype.mdx       # optional interactive flow
├── .plan-state.json    # optional stable source metadata
└── assets/             # optional local assets
```

Use a temporary or ignored folder when the recap should remain disposable. Set
`kind: "recap"` and `localOnly: true` in `plan.mdx` frontmatter. Use the same
directory for every check, verify, serve, and feedback edit.

Treat `.plan-url`, collected diffs, stats, prompts, and catalogs as ephemeral.
Never commit them; collected diffs can duplicate secrets or sensitive history.

## Collection and redaction

- Record the exact base/head SHAs or working-tree scope before authoring.
- Include staged and unstaged tracked changes when the requested work unit is
  the working tree. Include untracked files only when they belong to that work.
- Run the recap CLI's high-confidence secret scan on the collected input.
- Stop and remove credential material from recap excerpts when scanning finds a
  likely secret. A scan is a guardrail, not proof that the diff is safe.
- Build file paths, line content, field names, methods, routes, and change flags
  from the diff. Mark narrative interpretation as inference when appropriate.

## Local catalog, check, and verify

Query blocks only from the running loopback viewer:

```bash
bash <visual-plan-skill-dir>/scripts/local-viewer.sh cli plan blocks \
  --app-url http://127.0.0.1:8096 \
  --format schema --out <tmp-dir>/plan-blocks.md
```

Run the offline check first, followed by renderer-backed verification:

```bash
bash <visual-plan-skill-dir>/scripts/local-viewer.sh cli plan local check \
  --dir plans/<slug>-recap
bash <visual-plan-skill-dir>/scripts/local-viewer.sh cli plan local verify \
  --dir plans/<slug>-recap --kind recap \
  --app-url http://127.0.0.1:8096
```

Verification is authoritative only when `validation.ran` and
`validation.valid` are both `true`. If the local renderer cannot run, still
complete the offline check and report the exact runtime blocker.

## Preview and feedback

Serve with `--kind recap` and the same explicit loopback app URL. Reject any
returned non-loopback URL. Keep the viewer and bridge alive during review.

Local feedback is chat/file feedback: edit the MDX directly, preserve stable
IDs and unrelated blocks, then rerun check and verify. A loopback URL is valid
only on the machine running its viewer and bridge. Another reviewer can check
out repository-owned MDX and start their own local viewer.
