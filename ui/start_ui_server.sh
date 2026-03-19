#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UI_SCRIPT="${SCRIPT_DIR}/generate_autoware_map.py"
WORKSPACE_ROOT="$(cd "${SCRIPT_DIR}/../../../.." && pwd)"
WORKSPACE_SETUP="${WORKSPACE_ROOT}/install/setup.bash"
WORKSPACE_INSTALL_PREFIX="${WORKSPACE_ROOT}/install"
HOST="${1:-127.0.0.1}"
PORT="${2:-8090}"
OPEN_INDEX="${3:-false}"
SERVER_PID=""

normalize_bool() {
  local value="${1,,}"
  case "${value}" in
    1|true|yes|on)
      echo "true"
      ;;
    0|false|no|off)
      echo "false"
      ;;
    *)
      echo "false"
      ;;
  esac
}

browser_host() {
  case "${HOST}" in
    0.0.0.0|::|[::])
      echo "127.0.0.1"
      ;;
    *)
      echo "${HOST}"
      ;;
  esac
}

open_index_page() {
  if [[ "$(normalize_bool "${OPEN_INDEX}")" != "true" ]]; then
    return 0
  fi

  if [[ -z "${DISPLAY:-}" ]]; then
    echo "DISPLAY is not set. Skipping automatic browser open."
    return 0
  fi

  if ! command -v xdg-open >/dev/null 2>&1; then
    echo "xdg-open is not available. Skipping automatic browser open."
    return 0
  fi

  local url="http://$(browser_host):${PORT}/index.html"
  xdg-open "${url}" >/dev/null 2>&1 &
  echo "Opened UI page: ${url}"
}

wait_for_server() {
  local url="http://$(browser_host):${PORT}/health"
  local _=0
  for _ in $(seq 1 40); do
    if curl -fsS "${url}" >/dev/null 2>&1; then
      return 0
    fi
    sleep 0.25
  done
  echo "UI server did not become ready in time: ${url}"
  return 1
}

cleanup() {
  local exit_code=$?
  if [[ -n "${SERVER_PID}" ]] && kill -0 "${SERVER_PID}" >/dev/null 2>&1; then
    kill "${SERVER_PID}" >/dev/null 2>&1 || true
    wait "${SERVER_PID}" >/dev/null 2>&1 || true
  fi
  exit "${exit_code}"
}

if pgrep -af "${UI_SCRIPT}" >/dev/null 2>&1; then
  echo "UI server already running from ${UI_SCRIPT}. Reusing the existing process."
  open_index_page
  exit 0
fi

if ss -ltn "( sport = :${PORT} )" | grep -q LISTEN; then
  echo "Port ${PORT} is already in use. Skipping auto-start of ${UI_SCRIPT}."
  exit 0
fi

echo "Starting UI server: http://${HOST}:${PORT}/index.html"
trap cleanup EXIT INT TERM

workspace_already_sourced=false
case ":${AMENT_PREFIX_PATH:-}:" in
  *":${WORKSPACE_INSTALL_PREFIX}:"*)
    workspace_already_sourced=true
    ;;
esac

if [[ "${workspace_already_sourced}" != "true" && -f "${WORKSPACE_SETUP}" ]]; then
  # Colcon/Ament setup scripts may read optional trace vars that are unset.
  # Temporarily disable nounset so sourcing works even under `set -u`.
  set +u
  # shellcheck disable=SC1090
  source "${WORKSPACE_SETUP}"
  set -u
fi

python3 "${UI_SCRIPT}" --host "${HOST}" --port "${PORT}" &
SERVER_PID=$!

if wait_for_server; then
  open_index_page
fi

wait "${SERVER_PID}"
