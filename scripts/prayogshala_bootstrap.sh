#!/usr/bin/env bash
set -euo pipefail

MODEL="${OLLAMA_MODEL:-qwen2.5:1.5b-instruct}"
HOST="${OLLAMA_HOST:-http://127.0.0.1:11434}"
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
curl -fsS "$HOST/" || { echo "Ollama not reachable at $HOST"; exit 1; }

echo "== Pulling model: $MODEL =="
ollama pull "$MODEL"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -r requirements.txt

export OLLAMA_HOST="$HOST"
export OLLAMA_MODEL="$MODEL"

echo "== Launching Streamlit on :8501 =="
echo "Open http://localhost:8501 in the lab browser"
exec streamlit run app.py --server.port 8501 --server.headless true
