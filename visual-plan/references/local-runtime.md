# Local viewer runtime

The local viewer is a standalone scaffold of the open-source Plan template. The
helper stores it outside project repositories and uses its installed CLI for all
subsequent plan commands.

## Requirements

- Node.js 22.22 or newer
- `pnpm`, or Corepack with pnpm support
- Network access for the one-time bootstrap only

## Bootstrap

Run:

```bash
bash <skill-dir>/scripts/local-viewer.sh bootstrap
```

The default runtime directory is:

```text
${XDG_DATA_HOME:-$HOME/.local/share}/visual-plan/plan-viewer
```

Override it with `VISUAL_PLAN_RUNTIME_DIR`. Bootstrap downloads the Plan
template and installs its dependencies. It does not publish or upload a plan.

## Serve

From the target repository, run this as a long-lived process:

```bash
bash <skill-dir>/scripts/local-viewer.sh serve "$PWD/plans"
```

The helper exports `PLAN_LOCAL_DIR` to the absolute plans directory, enables
local mode, and starts Vite on `127.0.0.1:8096` with strict port matching. Set
`VISUAL_PLAN_PORT` to use another loopback port, and then pass that same origin
to every CLI `--app-url` option.

Do not let Vite select another port automatically. A port collision is a
blocker to resolve, not permission to drift to a different or remote origin.

## Run the installed CLI

Use:

```bash
bash <skill-dir>/scripts/local-viewer.sh cli <agent-native arguments>
```

For example:

```bash
bash <skill-dir>/scripts/local-viewer.sh cli plan local check \
  --dir plans/example
```

This avoids downloading the CLI again after bootstrap.

## Print a direct URL

For a simple slug:

```bash
bash <skill-dir>/scripts/local-viewer.sh url example
```

The command prints a loopback `/local-plans/<slug>` URL. Use `plan local serve`
when the route also needs the repository-relative `path` query or a bridge.
