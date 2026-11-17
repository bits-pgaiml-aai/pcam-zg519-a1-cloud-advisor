#!/usr/bin/env bash
set -uo pipefail

HOST="${OLLAMA_HOST:-http://127.0.0.1:11434}"
PORT="${STREAMLIT_PORT:-8501}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "== Project: $ROOT =="

if ! command -v ollama >/dev/null 2>&1; then
  echo "== Installing Ollama =="
  curl -fsSL https://ollama.com/install.sh | sh
fi

if ! curl -fsS "$HOST/" >/dev/null 2>&1; then
  echo "== Starting ollama serve =="
  nohup ollama serve >/tmp/ollama-serve.log 2>&1 &
  sleep 4
fi

echo "== Ollama status =="
curl -fsS "$HOST/"
echo

echo "== Installed models =="
ollama list || true

# Prefer explicit OLLAMA_MODEL; else first installed qwen3*; else qwen3:latest
if [[ -n "${OLLAMA_MODEL:-}" ]]; then
  MODEL="$OLLAMA_MODEL"
else
  MODEL="$(ollama list 2>/dev/null | awk 'NR>1 && $1 ~ /^qwen3(:|$)/ {print $1; exit 0}' || true)"
  if [[ -z "${MODEL}" ]]; then
    MODEL="qwen3:latest"
  fi
fi

echo "== Selected model: $MODEL =="

HAVE_MODEL=0
if ollama list 2>/dev/null | awk 'NR>1 {print $1}' | grep -Fxc -- "$MODEL" >/dev/null 2>&1; then
  HAVE_MODEL=1
fi

if [[ "$HAVE_MODEL" -eq 1 ]]; then
  echo "== Model already present; skip pull =="
else
  echo "== Pulling model: $MODEL =="
  ollama pull "$MODEL"
fi

if [[ ! -d .venv ]]; then
  echo "== Creating venv =="
  python3 -m venv .venv
fi

echo "== Activating venv and installing requirements =="
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -r requirements.txt

export OLLAMA_HOST="$HOST"
export OLLAMA_MODEL="$MODEL"

if (ss -ltn 2>/dev/null || netstat -ltn 2>/dev/null || true) | grep -qE ":${PORT}\\s"; then
  echo "== Port ${PORT} is busy =="
  echo "   Free it with:  pkill -f 'streamlit run app.py'"
  echo "   Or override:   STREAMLIT_PORT=8502 bash scripts/prayogshala_bootstrap.sh"
  PORT=$((PORT + 1))
  echo "== Using port ${PORT} instead =="
fi

echo "== Launching Streamlit on :${PORT} with model ${MODEL} =="
echo "Open http://localhost:${PORT} in the lab browser"
echo "Sidebar Model should be: ${MODEL}"
exec streamlit run app.py --server.port "${PORT}" --server.address 127.0.0.1 --server.headless true
