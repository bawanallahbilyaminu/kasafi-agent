#!/usr/bin/env bash
# One-command deploy of the Kasafi API to the VPS. Run from Git Bash in the repo, or from PowerShell with
# .\deploy\deploy.ps1 and the same flags (it stays in the same window):
#   deploy/deploy.sh               deploy origin/main (must equal your pushed local main)
#   deploy/deploy.sh --rollback    go back one release
#   deploy/deploy.sh --sync-env    update the server's deploy/.env from your local .env (allowed keys only)
#   deploy/deploy.sh --sync-index  copy the document index (documents/pages/chunks/budget_lines/budget_rows and the
#                                  structured core: budget_items/projects/perf_items/entity_builds) from the dev DB
#   deploy/deploy.sh --sync-pdfs   copy the source PDFs (public documents) to the server, for evidence crops; only
#                                  files that are new or changed (by sha256) are sent; nothing is ever deleted
#   deploy/deploy.sh --sync-geo    copy data/geo/*.geojson (not in git) to /data/geo on the server and run the geo
#                                  import there (LGAs, wards, facilities, places into PostGIS), with the corrections
#   deploy/deploy.sh --sync-corrections  copy data/geo/facility_corrections.yaml and apply it to the server's facility
#                                  table only (scripts/import_geo.py --corrections)
#   deploy/deploy.sh --sync-advisories  copy data/advisories/*.pdf (NIHSA AFO, NiMet SCP: not in git) to /data/pdfs,
#                                  index and OCR them there (Muse Spark vision, ~$1.4) and load data/official_outlooks.yaml
#   deploy/deploy.sh --sync-hints  copy data/private/partners_hints.json (not in git) to deploy/private/ on the
#                                  server, mounted read-only into the app; takes effect on the next deploy/restart
#   deploy/deploy.sh --sync-place  place history (docs/place-history.md): copy the UNOSAT flood maps
#                                  (data/place/floodmaps/*.gpkg) to /data/place, the water-body layer
#                                  (data/geo/water_bodies.geojson + .yaml) to /data/geo, and the precomputed
#                                  ward_history plus the per-cell satellite cache (sat_cache: rounded 100 m cells,
#                                  no user data, no plot geometry) from the dev DB, so the server never recomputes them
#
# Every run: numbered steps, a preflight before anything slow (ssh, dev database, migration heads, server disk),
# progress bars for packing and uploads, a spinner with the elapsed time for server steps, a final line in colour
# (✓ ... ok / ✗ FAILED at step N: reason) and a non-zero exit on failure. The full output goes to
# deploy/logs/<time>-<mode>.log (not in git). Progress, uploads and the PDF diff: scripts/deploykit.py.
#
# SSH host alias: KASAFI_SSH_HOST (default "vps"; see deploy/README.md for the ~/.ssh/config entry).
# The server's IP is never stored in this repo. Server-side steps live in deploy/remote.sh.
set -euo pipefail

HOST=${KASAFI_SSH_HOST:-vps}
PUBLIC_URL=${KASAFI_PUBLIC_URL:-https://kasafi-api.halalnumeriq.com.ng}
REMOTE_ENV=/opt/kasafi-agent/deploy/.env.incoming
REMOTE_INDEX=/opt/kasafi-agent/deploy/index.incoming.sql.gz
REMOTE_PDFS=/opt/kasafi-agent/deploy/pdfs.incoming.tar
REMOTE_GEO=/opt/kasafi-agent/deploy/geo.incoming.tar
REMOTE_ADVISORIES=/opt/kasafi-agent/deploy/advisories.incoming.tar
REMOTE_PLACE=/opt/kasafi-agent/deploy/place.incoming.tar
REMOTE_PLACE_SQL=/opt/kasafi-agent/deploy/place.incoming.sql.gz
# Keys the server may receive. DATABASE_URL is left out until the production database exists
# (the local one points at dev Postgres).
ALLOWED_KEYS='ADMIN_USER|ADMIN_PASSWORD|KASAFI_OPEN_READER|KASAFI_OPEN_READ_TIMEOUT_S|KASAFI_OPEN_STAGES|KASAFI_OPEN_STAGE_TIMEOUT_S|FIREWORKS_API_KEY|ORS_API_KEY|FIRMS_MAP_KEY|KASAFI_HAZARD_FETCH|KASAFI_ADVISORIES_FETCH|KASAFI_ADVISORIES_MONTHLY_USD|KASAFI_ALERTS|KASAFI_ALERTS_DRY_RUN|KASAFI_ALERTS_DAILY_CAP|KASAFI_ALERT_TEMPLATE_LANGS|KASAFI_ALERTS_NUMBER_KEY|KASAFI_OPEN_ACCESS|KASAFI_ALLOW_SECURITY_BUDGET|KASAFI_PILOT_NUMBERS|KASAFI_EXEMPT_NUMBERS|KASAFI_HASH_KEY|KASAFI_VOICE_PER_DAY|KASAFI_QUESTIONS_PER_DAY|KASAFI_DAILY_SPEND_CAP_USD|KASAFI_COST_PER_VOICE_USD|KASAFI_COST_PER_QUESTION_USD|KASAFI_FETCHES_PER_DAY|META_API_KEY|BASETEN_API_KEY|SERPER_API_KEY|RELIEFWEB_APPNAME|DTMAPI_SUBSCRIPTION_KEY|DTMHNA_SUBSCRIPTION_KEY|KASAFI_TOPIC_BUDGET_S|WHATSAPP_TOKEN|WHATSAPP_PHONE_NUMBER_ID|WHATSAPP_VERIFY_TOKEN|WHATSAPP_APP_SECRET|WHATSAPP_BUSINESS_ACCOUNT_ID|WHATSAPP_WABA_ID|WABA_ID'

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"

# On Windows, prefer the system OpenSSH so the Windows ssh-agent (and its unlocked key) is used.
SSH=ssh
[ -x /c/Windows/System32/OpenSSH/ssh.exe ] && SSH=/c/Windows/System32/OpenSSH/ssh.exe

# Python for the progress helper: the project's venv (no uv sync on every call), else uv.
if [ -x .venv/Scripts/python.exe ]; then PY=(.venv/Scripts/python.exe)
elif [ -x .venv/bin/python ]; then PY=(.venv/bin/python)
else PY=(uv run python); fi
KIT=("${PY[@]}" scripts/deploykit.py)
# paths handed to Windows programs stay relative (no MSYS rewriting); Python prints UTF-8 and unbuffered
export MSYS_NO_PATHCONV=1 PYTHONIOENCODING=utf-8 PYTHONUTF8=1 PYTHONUNBUFFERED=1
if [ -t 2 ]; then export KASAFI_PROGRESS=1; else export KASAFI_PROGRESS=0; fi

# --- the run: its log, steps and final line -----------------------------------------------------------------------
MODE=${1:-}
NAME=${MODE#--}; NAME=${NAME:-deploy}
case "$MODE" in -h|--help) sed -n '2,25p' "$0"; exit 0 ;; esac
mkdir -p deploy/logs/tmp
LOGFILE=deploy/logs/$(date +%Y%m%d-%H%M%S)-$NAME.log
export KASAFI_DEPLOY_LOG=$LOGFILE
START=$SECONDS STEP=0 TOTAL=1 KEPT="" REPORTED=0
TMPS=()

if [ -t 1 ]; then C_RED=$'\033[31m' C_GREEN=$'\033[32m' C_CYAN=$'\033[36m' C_DIM=$'\033[2m' C_OFF=$'\033[0m'
else C_RED="" C_GREEN="" C_CYAN="" C_DIM="" C_OFF=""; fi

log() { printf '%s\n' "$*" >> "$LOGFILE"; }
say() { printf '%s\n' "$*"; log "$*"; }
took() { local s=$((SECONDS - START)); if ((s < 60)); then echo "${s}s"; else printf '%dm %02ds' $((s / 60)) $((s % 60)); fi; }
commas() { sed -E ':a;s/([0-9])([0-9]{3})($|[^0-9])/\1,\2\3/;ta'; }
steps() { TOTAL=$1; }
step() { STEP=$((STEP + 1)); printf '%s[%d/%d]%s %s\n' "$C_CYAN" "$STEP" "$TOTAL" "$C_OFF" "$*"; log "[$STEP/$TOTAL] $*"; }
tmpfile() { local f; f=$(mktemp "deploy/logs/tmp/$1.XXXXXX"); TMPS+=("$f"); echo "$f"; }

ok() {  # $1 = what was done (numbers get thousands separators)
  local what; what=$(printf '%s' "${1:-}" | commas)
  REPORTED=1
  printf '%s✓ %s ok%s (%s)%s\n' "$C_GREEN" "$NAME" "${what:+: $what}" "$(took)" "$C_OFF"
  log "✓ $NAME ok${what:+: $what} ($(took))"
  printf '%s  log: %s%s\n' "$C_DIM" "$LOGFILE" "$C_OFF"
}

fail() {  # $1 = reason, $2 = exit code (default 1); KEPT says what state the server was left in
  REPORTED=1
  printf '%s✗ FAILED at step %d: %s%s%s\n' "$C_RED" "$STEP" "$1" "${KEPT:+; $KEPT}" "$C_OFF" >&2
  log "✗ FAILED at step $STEP: $1${KEPT:+; $KEPT}"
  printf '%s  log: %s%s\n' "$C_DIM" "$LOGFILE" "$C_OFF" >&2
  exit "${2:-1}"
}

on_exit() {
  local rc=$?
  rm -f ${TMPS[@]+"${TMPS[@]}"}
  if [ "$rc" -ne 0 ] && [ "$REPORTED" = 0 ]; then
    printf '%s✗ FAILED at step %d: stopped unexpectedly (exit %d)%s%s\n' "$C_RED" "$STEP" "$rc" "${KEPT:+; $KEPT}" "$C_OFF" >&2
    log "✗ FAILED at step $STEP: stopped unexpectedly (exit $rc)${KEPT:+; $KEPT}"
    printf '  log: %s\n' "$LOGFILE" >&2
  fi
}
trap on_exit EXIT
trap 'REPORTED=1; printf "\n%s✗ interrupted at step %d%s%s\n" "$C_RED" "$STEP" "${KEPT:+; $KEPT}" "$C_OFF" >&2; log "✗ interrupted at step $STEP"; exit 130' INT
log "deploy.sh $* — $(date -u +%Y-%m-%dT%H:%M:%SZ) — $(git rev-parse --short HEAD 2>/dev/null || echo '?')"

# --- the server ----------------------------------------------------------------------------------------------------
run_remote() {  # mode [expected-commit]; prints server output, returns its exit code
  tr -d '\r' < deploy/remote.sh | "$SSH" "$HOST" "bash -s -- $*"
}

remote() {  # label mode [args]: the server step under a spinner; sets RC and OUT (its full output)
  local label=$1; shift
  RC=0
  OUT=$(run_remote "$@" 2>&1 | "${KIT[@]}" follow --label "$label") || RC=$?
}

send() {  # local-file remote-path label: upload with a progress bar (to <path>.part, then renamed)
  "${KIT[@]}" upload "$1" --label "$3" -- "$SSH" "$HOST" "umask 077; cat > $2.part && mv $2.part $2" \
    || fail "the upload to $HOST failed (network or ssh); nothing was loaded on the server"
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
  echo "public $PUBLIC_URL/health is not serving ${want:0:7} (got: ${got:-no answer})"
  return 1
}

result_commit() { sed -n 's/^RESULT=[a-z_]* COMMIT=\([0-9a-f]*\).*/\1/p' <<<"$OUT" | tail -1; }
summary() { sed -n 's/^SUMMARY=//p' <<<"$OUT" | tail -1; }

after_remote() {  # $1 = what the server keeps when it rolled back (exit 2); handles RC from remote()
  local commit; commit=$(result_commit)
  case $RC in
    0) ;;
    2) local failed; failed=$(sed -n 's/.* FAILED=\([0-9a-f]*\).*/\1/p' <<<"$OUT" | tail -1)
       KEPT="$1${commit:+ (the server is running ${commit:0:7})}"
       fail "the server step failed${failed:+ for ${failed:0:7}}; see the server output above" 2 ;;
    *) KEPT="NOT rolled back: check the server (cd /opt/kasafi-agent/deploy && docker compose ps)"
       fail "the server step failed (exit $RC); see the server output above" 1 ;;
  esac
}

health_step() {  # the public check, under a spinner; the last step of every server change
  local commit; commit=$(result_commit)
  step "public health check ($PUBLIC_URL)"
  KEPT="the server change is done but the public URL isn't answering with ${commit:0:7}"
  public_check "$commit" 2>&1 | "${KIT[@]}" follow --label "public health check" >/dev/null \
    || fail "public $PUBLIC_URL/health is not serving ${commit:0:7}"
  KEPT=""
}

# --- preflight (fast; before anything slow) ------------------------------------------------------------------------
pf_ssh() {
  "$SSH" -o BatchMode=yes -o ConnectTimeout=10 "$HOST" true 2>/dev/null \
    || fail "ssh to '$HOST' failed. Fix: run 'ssh $HOST true'; if it asks for a passphrase, start the Windows ssh-agent and run ssh-add (deploy/README.md)"
  say "  ssh to $HOST: ok"
}

pf_devdb() {
  docker compose exec -T db pg_isready -q -U kasafi -d kasafi >/dev/null 2>&1 \
    || fail "the dev database isn't running. Fix: start Docker Desktop, then 'docker compose up -d db'"
  say "  dev database: running"
}

pf_migration() {  # dev's database and the server's must be at the same revision (the dump carries dev's columns)
  local cur head server
  cur=$("${PY[@]}" -m alembic current 2>/dev/null | grep -oE '^[0-9a-z_]+' | head -1 || true)
  head=$("${PY[@]}" -m alembic heads 2>/dev/null | grep -oE '^[0-9a-z_]+' | head -1 || true)
  [ -n "$cur" ] || fail "couldn't read the dev database's migration (alembic current). Fix: is the dev DB running and DATABASE_URL set?"
  [ "$cur" = "$head" ] || fail "the dev database is at migration $cur but the code's head is $head. Fix: 'uv run alembic upgrade head'"
  remote "reading the server's migration" migration
  server=$(sed -n 's/^REVISION=//p' <<<"$OUT" | tail -1)
  [ -n "$server" ] && [ "$server" != unknown ] || fail "couldn't read the server's migration (exit $RC)"
  [ "$server" = "$cur" ] || fail "the server's database is at migration $server, dev at $cur. Fix: deploy first (deploy/deploy.sh), then sync"
  say "  migrations: dev and server both at $cur"
}

FREE=0
pf_space() {  # $1 = bytes the upload needs on the server (it lands there, then is unpacked or loaded)
  local need=$1
  remote "checking the server's disk" space
  FREE=$(sed -n 's/^FREE=//p' <<<"$OUT" | tail -1)
  [ -n "$FREE" ] || fail "couldn't read the server's free disk space (exit $RC)"
  if [ "$FREE" -lt "$need" ]; then
    fail "the server has $(( FREE / 1000000 )) MB free, this needs about $(( need / 1000000 )) MB. Fix: free space on the server (ask before pruning anything: mailcow and other apps share it)"
  fi
  say "  server disk: $(( FREE / 1000000 )) MB free (needs ~$(( need / 1000000 )) MB)"
}

size_of() { stat -c %s "$1"; }

# --- modes ---------------------------------------------------------------------------------------------------------
case "$MODE" in
  "")
    steps 5
    KEPT="nothing was sent to the server"
    step "preflight"
    [ "$(git rev-parse --abbrev-ref HEAD)" = main ] || fail "not on main. Fix: git checkout main"
    # the pushed commit is what ships (by its hash), so untracked local files (notes, drafts) can't reach the server
    [ -z "$(git status --porcelain --untracked-files=no)" ] || fail "the working tree has uncommitted changes. Fix: commit or stash first"
    git fetch -q origin main
    LOCAL=$(git rev-parse HEAD); REMOTE=$(git rev-parse origin/main)
    [ "$LOCAL" = "$REMOTE" ] || fail "local main (${LOCAL:0:7}) != origin/main (${REMOTE:0:7}). Fix: push or pull first"
    say "  git: main at ${LOCAL:0:7}, pushed"
    pf_devdb
    pf_ssh
    step "end-to-end conversation suite (dev database)"
    KASAFI_E2E_REQUIRED=1 uv run pytest -q tests/test_e2e_conversation.py 2>&1 | "${KIT[@]}" follow --label "end-to-end conversations" >/dev/null \
      || fail "end-to-end conversations failed (the failures are above); not deploying"
    step "unit tests"
    uv run pytest -q 2>&1 | "${KIT[@]}" follow --label "tests" >/dev/null || fail "tests failed (the failures are above); not deploying"
    step "deploying ${LOCAL:0:7} on $HOST (backup, build, migrations, start, health)"
    KEPT=""
    remote "server" deploy "$LOCAL"
    after_remote "rolled back automatically"
    health_step
    ok "live: $(result_commit | cut -c1-7) at $PUBLIC_URL"
    ;;

  --rollback)
    steps 3
    step "preflight"; pf_ssh
    step "rolling back one release on $HOST"
    remote "server" rollback
    after_remote "the rollback failed and the server restored the release it was on"
    health_step
    ok "now running $(result_commit | cut -c1-7)"
    ;;

  --sync-env)
    steps 4
    KEPT="nothing was sent to the server"
    step "preflight"
    [ -f .env ] || fail "no local .env"
    keys=$(tr -d '\r' < .env | grep -E "^($ALLOWED_KEYS)=" | cut -d= -f1 | tr '\n' ' ' || true)
    [ -n "$keys" ] || fail "no allowed keys found in .env"
    pf_ssh
    step "uploading keys (values not shown): $keys"
    tr -d '\r' < .env | grep -E "^($ALLOWED_KEYS)=" | "$SSH" "$HOST" "umask 077; cat > $REMOTE_ENV" \
      || fail "the upload to $HOST failed"
    KEPT=""
    step "applying the new .env and restarting the app"
    remote "server" sync-env
    after_remote "the server restored the previous .env"
    health_step
    ok "$(wc -w <<<"$keys" | tr -d ' ') keys set"
    ;;

  --sync-geo)
    steps 5
    KEPT="nothing changed on the server"
    step "preflight"
    # the geo inputs only (boundaries, facilities, OSM places), never the local reports
    [ -f data/geo/sokoto_lga_codab.geojson ] || fail "no data/geo/ here"
    files=(data/geo/*.geojson); [ -f data/geo/facility_corrections.yaml ] && files+=(data/geo/facility_corrections.yaml)
    pf_ssh
    step "packing data/geo"
    tmp=$(tmpfile geo)
    "${KIT[@]}" pack "$tmp" --base data/geo --label "packing ${#files[@]} files" "${files[@]}" || fail "packing data/geo failed"
    pf_space $(( $(size_of "$tmp") * 2 + 200000000 ))
    step "uploading to $HOST"
    send "$tmp" "$REMOTE_GEO" "uploading data/geo"
    step "importing on the server"
    remote "server" sync-geo
    after_remote "the import failed"
    health_step
    ok "$(summary)"
    ;;

  --sync-corrections)
    steps 4
    KEPT="nothing changed on the server"
    step "preflight"
    # only data/geo/facility_corrections.yaml, applied to the server's facility table (no full geo import)
    [ -f data/geo/facility_corrections.yaml ] || fail "no data/geo/facility_corrections.yaml here"
    "${PY[@]}" -c "from app.geo.corrections import load; load()" || fail "the corrections file is invalid (see above)"
    say "  corrections file: valid"
    pf_ssh
    step "uploading the corrections"
    tmp=$(tmpfile corrections)
    "${KIT[@]}" pack "$tmp" --base data/geo --label "packing" data/geo/facility_corrections.yaml || fail "packing failed"
    send "$tmp" "$REMOTE_GEO" "uploading"
    step "applying on the server"
    remote "server" sync-corrections
    after_remote "the corrections were not applied"
    health_step
    ok "corrections applied"
    ;;

  --sync-pdfs)
    steps 6
    KEPT="nothing changed on the server"
    step "preflight"; pf_ssh
    step "reading the server's checksums"
    remote "checksums of /data/pdfs" pdf-sums
    [ "$RC" = 0 ] || fail "couldn't read the server's checksums (exit $RC)"
    sums=$(tmpfile sums); grep '^SUM ' <<<"$OUT" > "$sums" || true
    say "  the server holds $(wc -l < "$sums" | tr -d ' ') files"
    step "comparing with the local files and packing what's new or changed"
    tmp=$(tmpfile pdfs); rm -f "$tmp"
    DIFF=$("${KIT[@]}" pdfs-diff "$sums" "$tmp" | sed -n 's/^DIFF: //p') || fail "hashing or packing the local files failed"
    say "  $DIFF"
    if [ ! -s "$tmp" ]; then
      ok "$DIFF; nothing to upload"
      exit 0
    fi
    step "uploading $(( $(size_of "$tmp") / 1000000 )) MB to $HOST"
    pf_space $(( $(size_of "$tmp") * 2 + 200000000 ))
    send "$tmp" "$REMOTE_PDFS" "uploading PDFs"
    step "unpacking into /data/pdfs (files are replaced, never deleted)"
    remote "server" sync-pdfs
    after_remote "the PDFs were not unpacked"
    health_step
    ok "$DIFF; $(summary)"
    ;;

  --sync-advisories)
    steps 5
    KEPT="nothing changed on the server"
    step "preflight"
    # the local official documents (NIHSA AFO, NiMet SCP and its update: not in git), named <doc id>.pdf
    ls data/advisories/*.pdf > /dev/null 2>&1 || fail "no data/advisories/*.pdf here"
    pf_ssh
    step "packing data/advisories"
    tmp=$(tmpfile advisories)
    "${KIT[@]}" pack "$tmp" --base data/advisories --label "packing" data/advisories/*.pdf || fail "packing failed"
    pf_space $(( $(size_of "$tmp") * 2 + 200000000 ))
    step "uploading to $HOST"
    send "$tmp" "$REMOTE_ADVISORIES" "uploading advisories"
    step "indexing and OCR on the server (Muse Spark vision, ~\$1.4)"
    remote "server" sync-advisories
    after_remote "the advisories were not indexed"
    health_step
    ok "$(summary)"
    ;;

  --sync-index)
    steps 5
    KEPT="nothing changed on the server"
    step "preflight"
    pf_devdb
    pf_ssh
    # the dump carries dev's columns: the server must be at the same migration (1 Nov 2026: a sync failed and the
    # previous index was kept because dev had migration 0024 and the server did not; deploy first)
    pf_migration
    pf_space 1000000000
    step "dumping documents/pages/chunks from the dev database (public documents only)"
    tmp=$(tmpfile index)
    docker compose exec -T db pg_dump -U kasafi -d kasafi --data-only --no-owner \
      -t documents -t pages -t chunks -t budget_lines -t budget_rows \
      -t budget_items -t projects -t perf_items -t entity_builds \
      -t doc_cards -t section_cards -t doc_links | gzip \
      | "${KIT[@]}" meter "$tmp" --label "pg_dump | gzip" || fail "pg_dump failed (is the dev DB running?)"
    step "uploading $(( $(size_of "$tmp") / 1000000 )) MB to $HOST"
    [ "$FREE" -gt $(( $(size_of "$tmp") * 10 )) ] || fail "the server has too little disk for this index ($(( FREE / 1000000 )) MB free)"
    send "$tmp" "$REMOTE_INDEX" "uploading the index"
    step "loading on the server (one transaction)"
    remote "server" sync-index
    after_remote "the server kept the previous index"
    health_step
    ok "$(summary)"
    ;;

  --sync-place)
    steps 6
    KEPT="nothing changed on the server"
    step "preflight"
    ls data/place/floodmaps/*.gpkg > /dev/null 2>&1 || fail "no data/place/floodmaps/*.gpkg here (scripts/fetch_floodmaps.py)"
    [ -f data/geo/water_bodies.geojson ] || fail "no data/geo/water_bodies.geojson here (scripts/build_water_bodies.py)"
    pf_devdb
    pf_ssh
    pf_migration
    step "packing the flood maps and the water layer"
    tmp=$(tmpfile place)
    # two folders in one tar: place/floodmaps/*.gpkg and geo/water_bodies.*; unpacked under /data on the server
    files=(data/place/floodmaps/*.gpkg data/geo/water_bodies.geojson)
    for f in data/geo/water_bodies.yaml data/geo/osm_water_sokoto.json; do [ -f "$f" ] && files+=("$f"); done
    "${KIT[@]}" pack "$tmp" --base data --label "packing ${#files[@]} files" "${files[@]}" || fail "packing the place files failed"
    step "dumping ward_history and sat_cache from the dev database (per cell and unit; no user data, no geometry)"
    tmpsql=$(tmpfile place-sql)
    docker compose exec -T db pg_dump -U kasafi -d kasafi --data-only --no-owner \
      -t ward_history -t sat_cache | gzip | "${KIT[@]}" meter "$tmpsql" --label "pg_dump | gzip" \
      || fail "pg_dump failed (is the dev DB running?)"
    step "uploading to $HOST"
    pf_space $(( ($(size_of "$tmp") + $(size_of "$tmpsql")) * 3 + 200000000 ))
    send "$tmp" "$REMOTE_PLACE" "uploading the place files"
    send "$tmpsql" "$REMOTE_PLACE_SQL" "uploading the place tables"
    step "loading on the server (one transaction)"
    remote "server" sync-place
    after_remote "the server kept the previous place tables"
    health_step
    ok "$(summary)"
    ;;

  --sync-hints)
    steps 2
    f=data/private/partners_hints.json
    KEPT="nothing changed on the server"
    step "preflight"
    [ -f "$f" ] || fail "no local $f"
    pf_ssh
    step "uploading $f to $HOST:/opt/kasafi-agent/deploy/private/ (read-only in the app)"
    # world-readable inside its own folder so the app's non-root user can read the mount; nothing else reads it
    "${KIT[@]}" upload "$f" --label "uploading" -- "$SSH" "$HOST" "mkdir -p /opt/kasafi-agent/deploy/private && chmod 755 /opt/kasafi-agent/deploy/private && \
      cat > /opt/kasafi-agent/deploy/private/partners_hints.json.part && \
      mv /opt/kasafi-agent/deploy/private/partners_hints.json.part /opt/kasafi-agent/deploy/private/partners_hints.json && \
      chmod 644 /opt/kasafi-agent/deploy/private/partners_hints.json" || fail "the upload failed"
    ok "uploaded; takes effect on the next deploy or restart"
    ;;

  *) fail "unknown option $MODE (use --help)" ;;
esac
