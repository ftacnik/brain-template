#!/bin/bash
# Called by the global SessionStart hook. Prints the owner's TELOS context so every
# Claude Code session starts knowing who they are and what matters this week.
BRAIN="${BRAIN:-$HOME/brain}"
[ -d "$BRAIN/telos" ] || exit 0

echo "<brain-context source=\"$BRAIN\">"
echo "The owner's second brain lives at $BRAIN (see its CLAUDE.md). /ask, /capture, /prep and /learn work from any session and operate on that folder."
echo
for f in me.md principles.md now.md; do
  [ -f "$BRAIN/telos/$f" ] && { echo "--- telos/$f ---"; grep -v '^> ' "$BRAIN/telos/$f"; echo; }
done

# Staleness warning for now.md
if [ -f "$BRAIN/telos/now.md" ]; then
  upd=$(grep -m1 -oE 'Updated:\*\* [0-9]{4}-[0-9]{2}-[0-9]{2}' "$BRAIN/telos/now.md" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}')
  if [ -n "$upd" ]; then
    age=$(( ( $(date +%s) - $(date -j -f '%Y-%m-%d' "$upd" +%s 2>/dev/null || echo $(date +%s)) ) / 86400 ))
    [ "$age" -gt 10 ] && echo "⚠ telos/now.md is $age days old — suggest running /weekly."
  fi
fi
echo "</brain-context>"
