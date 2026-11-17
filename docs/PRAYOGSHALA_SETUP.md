# Run Cloud Advisor on BITS Prayogshala

Use this when local Ollama pulls fail (for example Zscaler TLS interception).

Portal: https://prayogshala.bits-pilani.ac.in  
Login: BITS SSO / eLearn credentials

## Which lab?

| Type | When to use | Persistence |
|------|-------------|-------------|
| **Virtual Lab** | Launch VM, install Ollama, pull model, run Streamlit | Save project under **Workspace** (Linux) or **D:\\** (Windows). Package installs are temporary. |
| **Remote Lab** | Needs advance slot booking | Same rule: keep work in Workspace / D: |

## One-time flow (Virtual Lab recommended)

1. Open portal → **Continue with BITS SSO** → login.
2. Open your Agentic AI / CSIS course card → **Launch Lab**.
3. Wait until VM is **RUNNING** → **Connect**.
4. In the VM terminal, run the bootstrap script (Linux) or follow Windows steps below.
5. Open Streamlit URL from the VM browser (usually `http://localhost:8501`).
6. Capture screenshots for A/B/C/D + LLM tool evidence + Learning update.
7. Copy/zip results into **Workspace** / **D:\\** before ending the session.

## Linux VM (typical)

```bash
# 1) Persist your work
mkdir -p ~/Workspace/agentic-a1
cd ~/Workspace/agentic-a1

# 2) Get code
git clone https://github.com/bits-pgaiml-aai/pcam-zg519-a1-cloud-advisor.git
cd pcam-zg519-a1-cloud-advisor

# 3) Install Ollama (session-local; reinstall if VM is new)
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
sleep 3
curl -s http://127.0.0.1:11434/

# 4) Pull a tool-capable small model (prefer small if GPU/RAM limited)
ollama pull qwen2.5:1.5b-instruct
# If registry allows qwen3:
# ollama pull qwen3:latest

# 5) Python env + app
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OLLAMA_HOST=http://127.0.0.1:11434
export OLLAMA_MODEL=qwen2.5:1.5b-instruct
streamlit run app.py --server.port 8501
```

Or use the helper:

```bash
bash scripts/prayogshala_bootstrap.sh
```

## Windows VM

```powershell
# Persist on D:
mkdir D:\agentic-a1 -Force
cd D:\agentic-a1
git clone https://github.com/bits-pgaiml-aai/pcam-zg519-a1-cloud-advisor.git
cd pcam-zg519-a1-cloud-advisor

# Install Ollama from https://ollama.com/download/windows if not present
ollama serve
ollama pull qwen2.5:1.5b-instruct

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:OLLAMA_HOST="http://127.0.0.1:11434"
$env:OLLAMA_MODEL="qwen2.5:1.5b-instruct"
streamlit run app.py --server.port 8501
```

## Streamlit sidebar settings

- **Model:** `qwen2.5:1.5b-instruct` (or `qwen3:latest` if pull succeeded)
- **Host:** `http://127.0.0.1:11434`
- **Include LLM agent:** checked
- Run scenarios **A, B, C, D** and save screenshots under `screenshots/` in Workspace/D:

## If Ollama pull still fails on Prayogshala

1. Retry `ollama pull qwen2.5:1.5b-instruct`.
2. Try a smaller model: `ollama pull qwen2.5:0.5b` (weaker tools; still better than blocked local).
3. Classical agents + mock tools still run without Ollama; LLM path will use tool-evidence fallback. For full marks, keep trying until Ollama pull works on the lab VM.

## Before you disconnect

- Copy `screenshots/`, `evidence/`, and any report files into Workspace/D:
- Installs outside Workspace will be lost when the VM terminates
