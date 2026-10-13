#!/bin/bash
# ================================================================
#  QuantDesk Watchdog v3 — self-healing supervisor (LaunchAgent)
#
#  Runs FROM ~/Library/Application Support/QuantDesk/ (TCC-exempt).
#  Detection : pgrep only (never touches protected Desktop paths).
#  Healing   : primary  -> osascript Terminal relay (one-time
#              consent, PROVEN working 2026-08-27)
#              fallback -> open -g -a Terminal <generated .command>
#              executes INSIDE Terminal, which holds repo grants.
#  Targeting : heals ONLY components actually down, via
#              ./quant heal <components>   (idempotent).
#  Anti-loop : max one heal dispatch per COOLDOWN seconds.
#  Suppressor: ~/.quantdesk_disabled planted by ./quant stop,
#              cleared by ./quant start — intentional wins.
# ================================================================
set -u

DIR="$HOME/Library/Application Support/QuantDesk"
# --- all writable paths FIRST (set -u safe: nothing below may use $LOG/$ERRLOG before this point)
LOG="$HOME/Library/Logs/qd-watchdog.log"
ERRLOG="$HOME/Library/Logs/qd-watchdog-osascript.err"
FLAG="$HOME/.quantdesk_disabled"
INTERVAL="${QD_WATCHDOG_INTERVAL:-120}"
COOLDOWN="${QD_WATCHDOG_COOLDOWN:-300}"

REPO="${QD_REPO:-}"
# Installer drops repo.conf next to this script (paths travel via variable
# expansion at WRITE time — never fragile sed-on-paths token surgery).
[ -f "$DIR/repo.conf" ] && . "$DIR/repo.conf"        # repo.conf exports QD_REPO
REPO="${QD_REPO:-${REPO:-}}"                          # ← derive AFTER sourcing (bugfix: was evaluated only before)
if [ -z "$REPO" ] || [ ! -d "$REPO" ]; then
  log_missing="FATAL: no usable REPO (set QD_REPO or add $DIR/repo.conf)"
  printf '[%s] %s\n' "$(date '+%F %T')" "$log_missing" >>"$LOG" 2>/dev/null || echo "$log_missing" >&2
fi

mkdir -p "$DIR" "$(dirname "$LOG")"
log() { printf '[%s] %s\n' "$(date '+%F %T')" "$*" >>"$LOG"; }
alive() { pgrep -f "$1" >/dev/null 2>&1; }

heal_via_terminal() {
  local need="$1"
  local inner="cd '$REPO' && { NO_BROWSER=1 ./quant heal $need ; } >>logs/heal_relay.log 2>&1"
  log "DETECTED DOWN ($need) -> osascript Terminal relay…"
  if osascript -e "tell application \"Terminal\" to do script \"$inner\"" 2>>"$ERRLOG"; then
    log "relay dispatched to Terminal OK"
    return 0
  fi
  log "WARN osascript rc!=0 — falling back to open(LaunchServices)"
  local cmd="$DIR/heal.command"
  printf '#!/bin/bash\ncd "%s" || exit 1\nNO_BROWSER=1 ./quant heal %s\nexit\n' "$REPO" "$need" >"$cmd"
  chmod +x "$cmd"
  if open -g -a Terminal "$cmd" 2>>"$LOG"; then
    log "fallback relay dispatched (open -> Terminal)"
  else
    log "ERROR: both relays blocked — run manually: ./quant heal $need"
  fi
}

log "watchdog v3 booted (pid $$ · interval ${INTERVAL}s · cooldown ${COOLDOWN}s · repo=$REPO)"

tick=0
while :; do
  sleep "$INTERVAL"

  if [ -f "$FLAG" ]; then                      # intentional shutdown wins
    tick=$((tick + 1)); [ $((tick % 15)) -eq 1 ] && log "standing by — suppressor flag present"
    continue
  fi
  [ -d "$REPO" ] || { log "ERROR: repo missing at $REPO"; continue; }

  need=""
  if ! alive 'execution\.autopilot'; then
    need="$need autopilot"
  else
    # Process is up; probe heartbeat staleness during market hours
    if [ -x "$REPO/.venv/bin/python" ] && ! "$REPO/.venv/bin/python" -m execution.deadmans_switch --check >/dev/null 2>&1; then
      log "WARN: autopilot process alive but heartbeat stale during market hours -> marking autopilot for heal"
      need="$need autopilot"
    fi
  fi
  if ! alive 'uvicorn.*webapp\.app'; then
    need="$need webapp"
  else
    # Process is up; probe HTTP /health endpoint to detect hung event loops
    if ! curl -s -f -m 3 http://127.0.0.1:8080/health >/dev/null 2>&1 && \
       ! curl -s -f -m 3 http://127.0.0.1:8081/health >/dev/null 2>&1; then
      log "WARN: webapp process alive but /health unresponsive -> marking webapp for heal"
      need="$need webapp"
    fi
  fi
  need="${need# }"

  tick=$((tick + 1))
  if [ -z "$need" ]; then                      # healthy — hourly heartbeat
    [ $((tick % 30)) -eq 0 ] && log "heartbeat: healthy"
    continue
  fi

  now=$(date +%s)
  last=$(cat "$DIR/last_heal_epoch" 2>/dev/null || echo 0)
  if [ $((now - last)) -lt "$COOLDOWN" ]; then
    log "cooldown: deferring heal for [$need]"
    continue
  fi
  echo "$now" >"$DIR/last_heal_epoch"

  heal_via_terminal "$need"
done
