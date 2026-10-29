#!/bin/bash
# Atomic run lock for the brain's routines.
# Two runs that wake together (Mac asleep through the night, then ingest + morning fire at once)
# can both see "no lock" and both write one. Creation here is atomic (O_CREAT|O_EXCL),
# so exactly one run wins.
#
#   scripts/lock.sh acquire <name> <mode>   -> prints a run id, exit 0; exit 1 + holder if held
#   scripts/lock.sh owns    <name> <id>     -> exit 0 if the lock is still this run's
#   scripts/lock.sh release <name> <id>     -> deletes the lock only if it is this run's
#   scripts/lock.sh held    <name>          -> exit 0 + holder if a fresh lock exists
#
# <name> is "ingest" (.ingest.lock) or "morning" (.morning.lock); add a name to the case line below
# for a new routine. A lock older than 120 minutes is stale and is taken over.
set -u
cd "$(dirname "$0")/.." || exit 2
cmd=${1:-}; name=${2:-}
case "$name" in ingest|morning) ;; *) echo "usage: $0 acquire|owns|release|held ingest|morning [arg]" >&2; exit 2;; esac
file=".$name.lock"

fresh() { [ -e "$file" ] && [ -n "$(find "$file" -mmin -120 2>/dev/null)" ]; }

create() {  # atomic create; prints nothing, exit 0 on success
  python3 -I -c 'import os,sys
try: fd=os.open(sys.argv[1], os.O_CREAT|os.O_EXCL|os.O_WRONLY, 0o644)
except FileExistsError: sys.exit(1)
os.write(fd, sys.argv[2].encode()); os.close(fd)' "$file" "$1"
}

case "$cmd" in
  acquire)
    mode=${3:-run}
    id="$(date +%Y%m%dT%H%M%S)-$$-$RANDOM"
    line="$id $(date -Iseconds) $mode"
    if create "$line"; then echo "$id"; exit 0; fi
    if ! fresh; then  # stale: take it over once
      rm -f "$file"
      if create "$line"; then echo "$id"; exit 0; fi
    fi
    echo "held: $(cat "$file" 2>/dev/null)" >&2; exit 1 ;;
  owns)
    [ -e "$file" ] && [ "$(cut -d' ' -f1 "$file")" = "${3:-}" ] ;;
  release)
    if [ -e "$file" ] && [ "$(cut -d' ' -f1 "$file")" = "${3:-}" ]; then rm -f "$file"; exit 0; fi
    echo "not released: lock is not this run's" >&2; exit 1 ;;
  held)
    if fresh; then cat "$file"; exit 0; fi; exit 1 ;;
  *) echo "usage: $0 acquire|owns|release|held ingest|morning [arg]" >&2; exit 2 ;;
esac
