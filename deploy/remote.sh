#!/usr/bin/env bash
# Server side of deploy/deploy.sh. Don't run this by hand; deploy.sh sends it over ssh:
#   ssh vps 'bash -s -- <deploy|rollback|sync-env|sync-index> [expected-commit]' < deploy/remote.sh
#
# It only touches /opt/kasafi-agent, the "kasafi-agent" compose project, the
# kasafi-agent-api images, and its own state and log files. It never prunes other
# containers or images, and never uses --remove-orphans.
# Exit codes: 0 ok, 2 failed but rolled back, 1 failed and needs attention.
set -euo pipefail

MODE=${1:?mode}
EXPECTED=${2:-}
APP=/opt/kasafi-agent
ENV_FILE=$APP/deploy/.env
DB_ENV=$APP/deploy/db.env           # POSTGRES_PASSWORD, generated here once, never synced or printed
STATE=/var/lib/kasafi-agent
RELEASES=$STATE/releases          # successfully deployed commits, newest last
LOG=/var/log/kasafi-agent/deploy.log
PORT=8010
IMAGE=kasafi-agent-api
KEEP_IMAGES=3
HEALTH_TIMEOUT=90

[ "$(id -u)" = 0 ] || { echo "remote: must run as root"; exit 1; }
mkdir -p "$STATE" "$(dirname "$LOG")"
exec 9>/var/lock/kasafi-agent-deploy.lock
flock -n 9 || { echo "remote: another kasafi-agent deploy is running"; exit 1; }

cd "$APP"
[ -f "$ENV_FILE" ] || { echo "remote: $ENV_FILE missing; run deploy.sh --sync-env first"; exit 1; }
PORT=$(grep -E '^KASAFI_PORT=[0-9]+$' "$ENV_FILE" | tail -1 | cut -d= -f2 || true); PORT=${PORT:-8010}
if [ ! -s "$DB_ENV" ]; then
  (umask 077; echo "POSTGRES_PASSWORD=$(openssl rand -hex 24)" > "$DB_ENV")
  echo "[remote] created $DB_ENV with a new database password"
fi
chmod 600 "$DB_ENV"
mkdir -p "$APP/deploy/backups"

dc() { docker compose --project-name kasafi-agent --project-directory "$APP/deploy" -f "$APP/deploy/docker-compose.yml" "$@"; }
say() { printf '[remote] %s\n' "$*"; }
log() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >> "$LOG"; }
short() { git rev-parse --short "$1"; }

wait_healthy() {  # $1 = commit the container must report
  local want=$1 deadline=$((SECONDS + HEALTH_TIMEOUT)) got=""
  while [ $SECONDS -lt $deadline ]; do
    if curl -fsS --max-time 3 "http://127.0.0.1:$PORT/health" 2>/dev/null | grep -q '"ok"'; then
      got=$(curl -fsS --max-time 3 "http://127.0.0.1:$PORT/version" 2>/dev/null | sed -n 's/.*"commit":"\([0-9a-f]*\)".*/\1/p')
      [ "$got" = "$want" ] && return 0
    fi
    sleep 3
  done
  say "health check failed after ${HEALTH_TIMEOUT}s (container reports commit: ${got:-none})"
  dc ps || true
  dc logs --tail 30 api || true
  return 1
}

build_and_start() {  # $1 = commit; runs migrations between build and start
  local commit=$1
  say "building $(short "$commit")"
  KASAFI_COMMIT=$commit dc build --quiet api db     # db: pgvector + PostGIS (db/Dockerfile), cached after once
  docker tag "$IMAGE:latest" "$IMAGE:$(short "$commit")"
  say "starting database"
  dc up -d --wait db
  if [ -f "$APP/alembic.ini" ]; then
    say "running database migrations"
    dc run --rm --no-deps api alembic upgrade head
  fi
  say "starting containers"
  dc up -d --no-build api backup
}

checkout() { git -c advice.detachedHead=false checkout -q --detach "$1"; }

prune_own_images() {  # dangling kasafi-agent-api layers + all but the newest commit tags
  docker image prune -f --filter dangling=true --filter "label=org.kasafi.app=$IMAGE" >/dev/null || true
  docker images "$IMAGE" --format '{{.Tag}}' | grep -E '^[0-9a-f]{7,}$' | tail -n +$((KEEP_IMAGES + 1)) \
    | while read -r tag; do docker rmi "$IMAGE:$tag" >/dev/null 2>&1 || true; done
}

record_release() { [ "$(tail -1 "$RELEASES" 2>/dev/null)" = "$1" ] || echo "$1" >> "$RELEASES"; }

case "$MODE" in
deploy)
  git diff --quiet && git diff --cached --quiet || { say "tracked files changed on the server; refusing"; exit 1; }
  PREV=$(git rev-parse HEAD)
  [ -s "$RELEASES" ] || echo "$PREV" > "$RELEASES"
  say "current: $(short "$PREV")"
  git fetch -q origin main
  git checkout -q main
  git pull -q --ff-only origin main
  NEW=$(git rev-parse HEAD)
  if [ -n "$EXPECTED" ] && [ "$NEW" != "$EXPECTED" ]; then
    say "server pulled $(short "$NEW") but laptop expects $(short "$EXPECTED"); refusing"
    checkout "$PREV"; exit 1
  fi
  say "target:  $(short "$NEW")"
  if build_and_start "$NEW" && wait_healthy "$NEW"; then
    record_release "$NEW"
    log "deploy ok $(short "$PREV") -> $(short "$NEW")"
    prune_own_images
    say "deployed $(short "$NEW")"
    echo "RESULT=ok COMMIT=$NEW"
    exit 0
  fi
  say "deploy of $(short "$NEW") FAILED; rolling back to $(short "$PREV")"
  checkout "$PREV"
  if build_and_start "$PREV" && wait_healthy "$PREV"; then
    log "deploy FAILED $(short "$NEW"); rolled back to $(short "$PREV")"
    echo "RESULT=rolled_back COMMIT=$PREV FAILED=$NEW"
    exit 2
  fi
  log "deploy FAILED $(short "$NEW"); rollback to $(short "$PREV") ALSO FAILED"
  echo "RESULT=failed COMMIT=none"
  exit 1
  ;;

rollback)
  [ "$(wc -l < "$RELEASES" 2>/dev/null || echo 0)" -ge 2 ] || { say "no earlier release recorded"; exit 1; }
  CUR=$(tail -1 "$RELEASES"); TARGET=$(tail -2 "$RELEASES" | head -1)
  say "rolling back $(short "$CUR") -> $(short "$TARGET")"
  checkout "$TARGET"
  if build_and_start "$TARGET" && wait_healthy "$TARGET"; then
    sed -i '$d' "$RELEASES"
    log "rollback ok $(short "$CUR") -> $(short "$TARGET")"
    echo "RESULT=ok COMMIT=$TARGET"
    exit 0
  fi
  say "rollback FAILED; restoring $(short "$CUR")"
  checkout "$CUR"
  build_and_start "$CUR" && wait_healthy "$CUR" && { log "rollback FAILED; stayed on $(short "$CUR")"; echo "RESULT=rolled_back COMMIT=$CUR"; exit 2; }
  log "rollback FAILED and restore of $(short "$CUR") FAILED"
  echo "RESULT=failed COMMIT=none"
  exit 1
  ;;

sync-env)
  # deploy.sh first uploads the allowed keys to .env.incoming (mode 600, separate ssh call),
  # since this script itself arrives on stdin. KASAFI_PORT is kept from the old file.
  umask 077
  INCOMING=$APP/deploy/.env.incoming
  [ -s "$INCOMING" ] || { say "no $INCOMING uploaded"; exit 1; }
  NEWENV=$(mktemp "$APP/deploy/.env.new.XXXXXX")
  tr -d '\r' < "$INCOMING" > "$NEWENV"; rm -f "$INCOMING"
  grep -qE '^KASAFI_PORT=' "$NEWENV" || echo "KASAFI_PORT=$PORT" >> "$NEWENV"
  cp -p "$ENV_FILE" "$ENV_FILE.bak"
  mv "$NEWENV" "$ENV_FILE"; chmod 600 "$ENV_FILE" "$ENV_FILE.bak"
  say "keys now set: $(cut -d= -f1 "$ENV_FILE" | sort | tr '\n' ' ')"
  CUR=$(git rev-parse HEAD)
  dc up -d --no-build api
  if wait_healthy "$CUR"; then log "sync-env ok at $(short "$CUR")"; echo "RESULT=ok COMMIT=$CUR"; exit 0; fi
  say "unhealthy with the new .env; restoring the previous .env"
  mv "$ENV_FILE.bak" "$ENV_FILE"
  dc up -d --no-build api
  wait_healthy "$CUR" && { log "sync-env FAILED; restored previous .env"; echo "RESULT=rolled_back COMMIT=$CUR"; exit 2; }
  log "sync-env FAILED; restore also unhealthy"
  echo "RESULT=failed COMMIT=none"
  exit 1
  ;;

sync-index)
  # deploy.sh first uploads a gzipped data-only pg_dump of documents/pages/chunks (public
  # documents only, no user data) to index.incoming.sql.gz. It replaces the server's copy
  # in one transaction, so a failure leaves the old index in place.
  INCOMING=$APP/deploy/index.incoming.sql.gz
  [ -s "$INCOMING" ] || { say "no $INCOMING uploaded"; exit 1; }
  dc up -d --wait db
  # The dev index replaces everything, including documents fetched live on the server; they are
  # fetched again the next time a question needs them.
  fetched=$(dc exec -T db psql -At -U kasafi -d kasafi -c "SELECT string_agg(id, ', ') FROM documents WHERE acquisition IN ('fetched', 'scheduled')" 2>/dev/null || true)
  [ -n "$fetched" ] && say "note: replacing live-fetched documents too: $fetched"
  say "loading index ($(du -h "$INCOMING" | cut -f1) compressed)"
  if { echo "TRUNCATE documents CASCADE;"; gunzip -c "$INCOMING"; }        | dc exec -T db psql -q -1 -v ON_ERROR_STOP=1 -U kasafi -d kasafi >/dev/null; then
    rm -f "$INCOMING"
    counts=$(dc exec -T db psql -At -U kasafi -d kasafi -c       "SELECT (SELECT count(*) FROM documents)||' documents, '||(SELECT count(*) FROM pages)||' pages, '||(SELECT count(*) FROM chunks)||' chunks, '||(SELECT count(*) FROM budget_lines)||' budget lines, '||(SELECT count(*) FROM budget_rows)||' budget rows'")
    say "index loaded: $counts"
    log "sync-index ok: $counts"
    echo "RESULT=ok COMMIT=$(git rev-parse HEAD)"
    exit 0
  fi
  rm -f "$INCOMING"
  log "sync-index FAILED; previous index kept"
  echo "RESULT=rolled_back COMMIT=$(git rev-parse HEAD)"
  exit 2
  ;;

sync-geo)
  # deploy.sh uploads a tar of data/geo/ (boundaries, facilities, places: not in git, the facility file's licence
  # isn't confirmed). It goes into the app's data volume at /data/geo, then the geo import fills the PostGIS tables.
  INCOMING=$APP/deploy/geo.incoming.tar
  [ -s "$INCOMING" ] || { say "no $INCOMING uploaded"; exit 1; }
  if dc exec -T api sh -c 'mkdir -p /data/geo && tar -x -m -C /data/geo' < "$INCOMING" \
     && dc exec -T api python scripts/import_geo.py --geo /data/geo > /dev/null; then
    rm -f "$INCOMING"
    n=$(dc exec -T db psql -At -U kasafi -d kasafi -c "SELECT (SELECT count(*) FROM lga)||' LGAs, '||(SELECT count(*) FROM ward)||' wards, '||(SELECT count(*) FROM facility)||' facilities, '||(SELECT count(*) FROM place)||' places'")
    say "geo imported: $n"
    log "sync-geo ok: $n"
    echo "RESULT=ok COMMIT=$(git rev-parse HEAD)"
    exit 0
  fi
  rm -f "$INCOMING"
  log "sync-geo FAILED"
  echo "RESULT=failed COMMIT=none"
  exit 1
  ;;

sync-advisories)
  # deploy.sh uploads a tar of data/advisories/*.pdf (official documents Bilyaminu downloaded: not in git), named by
  # document id. They join the source PDFs in /data/pdfs; the three are indexed and OCR'd there, then the official
  # outlooks (data/official_outlooks.yaml, every quote checked on its page) are loaded.
  INCOMING=$APP/deploy/advisories.incoming.tar
  DOCS="nihsa-afo-2026 nimet-scp-2026 nimet-scp-update-2026"
  [ -s "$INCOMING" ] || { say "no $INCOMING uploaded"; exit 1; }
  if dc exec -T api sh -c 'mkdir -p /data/pdfs && tar -x -m -C /data/pdfs' < "$INCOMING" \
     && dc exec -T api python scripts/index_docs.py --only $DOCS --pdf-dir /data/pdfs \
     && dc exec -T api python scripts/ocr_pages.py --only $DOCS --pdf-dir /data/pdfs | tail -1 \
     && dc exec -T api python scripts/official_outlooks.py | tail -1; then
    rm -f "$INCOMING"
    n=$(dc exec -T db psql -At -U kasafi -d kasafi -c "SELECT (SELECT count(*) FROM pages WHERE doc_id IN ('nihsa-afo-2026','nimet-scp-2026','nimet-scp-update-2026'))||' pages, '||(SELECT count(*) FROM pages WHERE source = 'none' AND doc_id IN ('nihsa-afo-2026','nimet-scp-2026','nimet-scp-update-2026'))||' without text, '||(SELECT count(*) FROM advisories WHERE doc_id IS NOT NULL)||' outlook rows'")
    say "advisory documents: $n"
    log "sync-advisories ok: $n"
    echo "RESULT=ok COMMIT=$(git rev-parse HEAD)"
    exit 0
  fi
  rm -f "$INCOMING"
  log "sync-advisories FAILED"
  echo "RESULT=failed COMMIT=none"
  exit 1
  ;;
sync-pdfs)
  # deploy.sh uploads a tar of the source PDFs (public documents, named <doc id>.pdf). They go into the
  # app's data volume at /data/pdfs, where the evidence crops read them. Files are replaced, never deleted.
  INCOMING=$APP/deploy/pdfs.incoming.tar
  [ -s "$INCOMING" ] || { say "no $INCOMING uploaded"; exit 1; }
  if dc exec -T api sh -c 'mkdir -p /data/pdfs && tar -x -m -C /data/pdfs' < "$INCOMING"; then
    rm -f "$INCOMING"
    n=$(dc exec -T api sh -c 'ls /data/pdfs | wc -l' | tr -d '[:space:]')
    say "PDFs in /data/pdfs: $n"
    log "sync-pdfs ok: $n files"
    echo "RESULT=ok COMMIT=$(git rev-parse HEAD)"
    exit 0
  fi
  rm -f "$INCOMING"
  log "sync-pdfs FAILED"
  echo "RESULT=failed COMMIT=none"
  exit 1
  ;;

*) echo "remote: unknown mode $MODE"; exit 1 ;;
esac
