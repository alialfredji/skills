#!/usr/bin/env bash
set -euo pipefail

command_name="${1:-help}"

if [[ -n "${VISUAL_PLAN_RUNTIME_DIR:-}" ]]; then
  runtime_root="$VISUAL_PLAN_RUNTIME_DIR"
elif [[ -n "${XDG_DATA_HOME:-}" ]]; then
  runtime_root="$XDG_DATA_HOME/visual-plan"
else
  runtime_root="${HOME:?HOME must be set}/.local/share/visual-plan"
fi

viewer_dir="$runtime_root/plan-viewer"
port="${VISUAL_PLAN_PORT:-8096}"

case "$port" in
  ''|*[!0-9]*)
    echo "VISUAL_PLAN_PORT must be an integer between 1 and 65535." >&2
    exit 2
    ;;
esac
if (( port < 1 || port > 65535 )); then
  echo "VISUAL_PLAN_PORT must be an integer between 1 and 65535." >&2
  exit 2
fi

if command -v pnpm >/dev/null 2>&1; then
  pnpm_runner=(pnpm)
elif command -v corepack >/dev/null 2>&1; then
  pnpm_runner=(corepack pnpm)
else
  echo "pnpm or Corepack is required." >&2
  exit 1
fi

require_viewer() {
  if [[ ! -f "$viewer_dir/package.json" ]]; then
    echo "Local Plan viewer is not bootstrapped." >&2
    echo "Run: bash $0 bootstrap" >&2
    exit 1
  fi
}

print_help() {
  cat <<'EOF'
Usage:
  local-viewer.sh bootstrap
  local-viewer.sh serve [plans-root]
  local-viewer.sh cli <agent-native arguments...>
  local-viewer.sh url <slug>

Environment:
  VISUAL_PLAN_RUNTIME_DIR  Runtime root (default: XDG data dir or ~/.local/share/visual-plan)
  VISUAL_PLAN_PORT         Loopback viewer port (default: 8096)
EOF
}

case "$command_name" in
  bootstrap)
    mkdir -p "$runtime_root"
    if [[ ! -f "$viewer_dir/package.json" ]]; then
      (
        cd "$runtime_root"
        "${pnpm_runner[@]}" dlx @agent-native/core@latest create plan-viewer \
          --standalone \
          --template plan
      )
    fi
    "${pnpm_runner[@]}" --dir "$viewer_dir" install
    echo "Local Plan viewer ready at $viewer_dir"
    ;;
  serve)
    require_viewer
    plans_root="${2:-$PWD/plans}"
    mkdir -p "$plans_root"
    plans_root="$(cd "$plans_root" && pwd -P)"
    export PLAN_LOCAL_DIR="$plans_root"
    export PLAN_LOCAL_MODE=1
    echo "Serving local Plan viewer at http://127.0.0.1:$port"
    echo "Plans root: $plans_root"
    exec "${pnpm_runner[@]}" --dir "$viewer_dir" exec vite \
      --host 127.0.0.1 \
      --port "$port" \
      --strictPort
    ;;
  cli)
    require_viewer
    shift
    if (( $# == 0 )); then
      echo "cli requires agent-native arguments." >&2
      exit 2
    fi
    cli_bin="$viewer_dir/node_modules/.bin/agent-native"
    if [[ ! -x "$cli_bin" ]]; then
      echo "Local Plan CLI is unavailable. Run: bash $0 bootstrap" >&2
      exit 1
    fi
    exec "$cli_bin" "$@"
    ;;
  url)
    slug="${2:-}"
    if [[ -z "$slug" || "$slug" == *[!A-Za-z0-9._-]* ]]; then
      echo "url requires a slug containing only letters, digits, dot, underscore, or hyphen." >&2
      exit 2
    fi
    printf 'http://127.0.0.1:%s/local-plans/%s\n' "$port" "$slug"
    ;;
  help|-h|--help)
    print_help
    ;;
  *)
    echo "Unknown command: $command_name" >&2
    print_help >&2
    exit 2
    ;;
esac
