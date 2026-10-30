#!/usr/bin/env bash
# One-command deploy of the Kasafi API to the VPS. Run from Git Bash in the repo:
#   deploy/deploy.sh               deploy origin/main (must equal your pushed local main)
#   deploy/deploy.sh --rollback    go back one release
#   deploy/deploy.sh --sync-env    update the server's deploy/.env from your local .env (allowed keys only)
#   deploy/deploy.sh --sync-index  copy the document index (documents/pages/chunks/budget_lines/budget_rows and the
#                                  structured core: budget_items/projects/perf_items/entity_builds) from the dev DB
#   deploy/deploy.sh --sync-pdfs   copy the source PDFs (public documents) to the server, for evidence crops
#   deploy/deploy.sh --sync-hints  copy data/private/partners_hints.json (not in git) to deploy/private/ on the
#                                  server, mounted read-only into the app; takes effect on the next deploy/restart
#
# SSH host alias: KASAFI_SSH_HOST (default "vps"; see deploy/README.md for the ~/.ssh/config entry).
# The server's IP is never stored in this repo. Server-side steps live in deploy/remote.sh.
set -euo pipefail

HOST=${KASAFI_SSH_HOST:-vps}
PUBLIC_URL=${KASAFI_PUBLIC_URL:-https://kasafi-api.halalnumeriq.com.ng}
REMOTE_ENV=/opt/kasafi-agent/deploy/.env.incoming
REMOTE_INDEX=/opt/kasafi-agent/deploy/index.incoming.sql.gz
REMOTE_PDFS=/opt/kasafi-agent/deploy/pdfs.incoming.tar
# Keys the server may receive. DATABASE_URL is left out until the production database exists
# (the local one points at dev Postgres).
ALLOWED_KEYS='ADMIN_USER|ADMIN_PASSWORD|KASAFI_OPEN_READER|KASAFI_OPEN_READ_TIMEOUT_S|KASAFI_OPEN_STAGES|KASAFI_OPEN_STAGE_TIMEOUT_S|FIREWORKS_API_KEY|ORS_API_KEY|FIRMS_MAP_KEY|KASAFI_OPEN_ACCESS|KASAFI_ALLOW_SECURITY_BUDGET|KASAFI_PILOT_NUMBERS|KASAFI_EXEMPT_NUMBERS|KASAFI_HASH_KEY|KASAFI_VOICE_PER_DAY|KASAFI_QUESTIONS_PER_DAY|KASAFI_DAILY_SPEND_CAP_USD|KASAFI_COST_PER_VOICE_USD|KASAFI_COST_PER_QUESTION_USD|KASAFI_FETCHES_PER_DAY|META_API_KEY|BASETEN_API_KEY|SERPER_API_KEY|RELIEFWEB_APPNAME|DTMAPI_SUBSCRIPTION_KEY|DTMHNA_SUBSCRIPTION_KEY|KASAFI_TOPIC_BUDGET_S|WHATSAPP_TOKEN|WHATSAPP_PHONE_NUMBER_ID|WHATSAPP_VERIFY_TOKEN|WHATSAPP_APP_SECRET|WHATSAPP_BUSINESS_ACCOUNT_ID|WHATSAPP_WABA_ID|WABA_ID'

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"

# On Windows, prefer the system OpenSSH so the Windows ssh-agent (and its unlocked key) is used.
SSH=ssh
[ -x /c/Windows/System32/OpenSSH/ssh.exe ] && SSH=/c/Windows/System32/OpenSSH/ssh.exe

red() { printf '\033[31m%s\033[0m\n' "$*"; }
green() { printf '\033[32m%s\033[0m\n' "$*"; }
die() { red "✗ $*"; exit 1; }

run_remote() {  # mode [expected-commit]; prints server output, returns its exit code
  tr -d '\r' < deploy/remote.sh | "$SSH" "$HOST" "bash -s -- $*"
}

public_check() {  # $1 = commit expected publicly
  local want=$1 got="" i
  for i in $(seq 1 10); do
    if curl -fsS --max-time 5 "$PUBLIC_URL/health" | grep -q '"ok"'; then
      got=$(curl -fsS --max-time 5 "$PUBLIC_URL/version" | sed -n 's/.*"commit":"\([0-9a-f]*\)".*/\1/p')
      [ "$got" = "$want" ] && return 0
    fi
    sleep 3
  done
  red "public $PUBLIC_URL/health is not serving ${want:0:7} (got: ${got:-no answer})"
  return 1
}

report() {  # $1 = remote exit code, $2 = remote output
  local rc=$1 out=$2 commit
  commit=$(sed -n 's/^RESULT=[a-z_]* COMMIT=\([0-9a-f]*\).*/\1/p' <<<"$out" | tail -1)
  case $rc in
    0) public_check "$commit" && green "✓ live: ${commit:0:7} at $PUBLIC_URL" || exit 1 ;;
    2) red "✗ FAILED, rolled back automatically. The server is running ${commit:0:7}."
       failed=$(sed -n 's/.* FAILED=\([0-9a-f]*\).*/\1/p' <<<"$out" | tail -1)
       [ -n "$failed" ] && red "  The failing commit was ${failed:0:7}; see the server output above."
       exit 2 ;;
    *) red "✗ FAILED and NOT rolled back. Check the server: cd /opt/kasafi-agent/deploy && docker compose ps"
       exit 1 ;;
  esac
}

remote_and_report() {
  local out rc=0
  out=$(run_remote "$@" | tee /dev/stderr) || rc=$?
  report "$rc" "$out"
}

case "${1:-}" in
  "")
    [ "$(git rev-parse --abbrev-ref HEAD)" = main ] || die "not on main"
    # the pushed commit is what ships (by its hash), so untracked local files (notes, drafts) can't reach the server
    [ -z "$(git status --porcelain --untracked-files=no)" ] || die "working tree has uncommitted changes; commit or stash first"
    git fetch -q origin main
    LOCAL=$(git rev-parse HEAD); REMOTE=$(git rev-parse origin/main)
    [ "$LOCAL" = "$REMOTE" ] || die "local main (${LOCAL:0:7}) != origin/main (${REMOTE:0:7}); push or pull first"
    echo "→ running tests"
    uv run pytest -q || die "tests failed; not deploying"
    echo "→ deploying ${LOCAL:0:7} to $HOST"
    remote_and_report deploy "$LOCAL"
    ;;
  --rollback)
    echo "→ rolling back one release on $HOST"
    remote_and_report rollback
    ;;
  --sync-env)
    [ -f .env ] || die "no local .env"
    keys=$(tr -d '\r' < .env | grep -E "^($ALLOWED_KEYS)=" | cut -d= -f1 | tr '\n' ' ' || true)
    [ -n "$keys" ] || die "no allowed keys found in .env"
    echo "→ uploading keys (values not shown): $keys"
    tr -d '\r' < .env | grep -E "^($ALLOWED_KEYS)=" | "$SSH" "$HOST" "umask 077; cat > $REMOTE_ENV"
    remote_and_report sync-env
    ;;
  --sync-pdfs)
    tmp=$(mktemp)
    uv run python scripts/pack_pdfs.py "$tmp" || { rm -f "$tmp"; die "packing the PDFs failed"; }
    echo "→ uploading $(du -h "$tmp" | cut -f1) to $HOST"
    "$SSH" "$HOST" "umask 077; cat > $REMOTE_PDFS" < "$tmp"; rm -f "$tmp"
    remote_and_report sync-pdfs
    ;;
  --sync-index)
    echo "→ dumping documents/pages/chunks from the dev database (public documents only)"
    tmp=$(mktemp)
    MSYS_NO_PATHCONV=1 docker compose exec -T db pg_dump -U kasafi -d kasafi --data-only --no-owner       -t documents -t pages -t chunks -t budget_lines -t budget_rows       -t budget_items -t projects -t perf_items -t entity_builds | gzip > "$tmp" || { rm -f "$tmp"; die "pg_dump failed (is the dev DB running?)"; }
    echo "→ uploading $(du -h "$tmp" | cut -f1) to $HOST"
    "$SSH" "$HOST" "umask 077; cat > $REMOTE_INDEX" < "$tmp"; rm -f "$tmp"
    remote_and_report sync-index
    ;;
  --sync-hints)
    f=data/private/partners_hints.json
    [ -f "$f" ] || die "no local $f"
    echo "→ uploading $f ($(du -h "$f" | cut -f1)) to $HOST:/opt/kasafi-agent/deploy/private/ (read-only in the app)"
    # world-readable inside its own folder so the app's non-root user can read the mount; nothing else reads it
    "$SSH" "$HOST" "mkdir -p /opt/kasafi-agent/deploy/private && chmod 755 /opt/kasafi-agent/deploy/private && \
      cat > /opt/kasafi-agent/deploy/private/partners_hints.json.part && \
      mv /opt/kasafi-agent/deploy/private/partners_hints.json.part /opt/kasafi-agent/deploy/private/partners_hints.json && \
      chmod 644 /opt/kasafi-agent/deploy/private/partners_hints.json && echo uploaded" < "$f"
    ;;
  -h|--help) sed -n '2,11p' "$0" ;;
  *) die "unknown option $1 (use --help)" ;;
esac
