# pcam-zg519-a1-cloud-advisor

**BITS Pilani WILP · PGAIML · PCAM ZG519 Agentic AI**  
**Assignment-1 · Set-3 · Group 11**  
**Topic:** Cloud Resource and Cost Optimization Advisor

Implementation by **Venkata Srinivasa Rao Tunuguntla** (repo root).  
Team bake-off process: [`TEAM.md`](TEAM.md) · [`docs/WORK_SPLIT.md`](docs/WORK_SPLIT.md).

Compares five classical agents and one local Ollama LLM agent on the **same** simulated cloud scenarios.

| Agent | Decision idea |
|-------|----------------|
| Simple Reflex | Fixed condition → action rules |
| Model-Based Reflex | Short internal state / streaks |
| Goal-Based | Look-ahead + pass/fail goal test |
| Utility-Based | Maximize expected utility among feasible plans |
| Learning | Utility + success/failure experience store |
| LLM (Ollama) | LangChain/Ollama tool calling (≥2 tools) |

## Scenarios

| ID | Kind | Summary |
|----|------|---------|
| A | critical | High CPU, response time above SLA |
| B | normal | Low utilization, expensive instance |
| C | normal | Sharp peak vs off-peak swing |
| D | edge | Ambiguous mixed latency/cost/CPU signals |

## Setup

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt

# Ollama must be running for the LLM agent
ollama serve
ollama pull qwen2.5:1.5b-instruct
# or: ollama pull qwen3:latest
```

Optional overrides:

```bash
set OLLAMA_MODEL=qwen2.5:1.5b-instruct
set OLLAMA_HOST=http://127.0.0.1:11434
```

## Run Streamlit UI

```bash
streamlit run app.py
```

## Run comparison from CLI

```bash
python -m src.cli A
python -m src.cli B --save evidence/scenario_B.json
python -m src.cli C --no-llm
python -m src.cli D
```

Generate classical + LLM evidence for A/B/C/D:

```bash
python scripts/generate_evidence.py
```

## BITS Prayogshala (recommended when local Ollama pull is blocked)

If Zscaler/local network blocks `ollama pull`, run on Prayogshala:

- Portal: https://prayogshala.bits-pilani.ac.in
- Guide: [`docs/PRAYOGSHALA_SETUP.md`](docs/PRAYOGSHALA_SETUP.md)
- Linux helper: `bash scripts/prayogshala_bootstrap.sh`

Save all screenshots/evidence under **Workspace** (Linux) or **D:\\** (Windows) before ending the VM session.

## Google Colab notebook (with validation)

Open [`notebooks/Cloud_Advisor_Colab_Validation.ipynb`](notebooks/Cloud_Advisor_Colab_Validation.ipynb) in Colab and **Runtime → Run all**.

It clones this repo, runs scenarios A–D, validates classical decisions, mock tools, LLM tool-evidence path (`qwen3:latest` if Ollama is available), and learning updates. Final cell should print **ALL CHECKS PASSED**.

Local equivalent:

```bash
python scripts/run_colab_validation.py
```

## Expected outputs shown

For each agent/scenario the UI and JSON include:

- Current-state summary
- Candidate configurations / actions
- Cost/performance trade-offs
- Recommendation
- Monitoring plan
- LLM tool evidence (when enabled)
- Learning stats / limitations (Learning agent)

## Project layout

```
app.py                 Streamlit UI
src/world.py           Shared scenarios + catalog
src/agents/            Five classical agents
src/tools/             Mock cloud tools for LLM
src/llm_agent.py       Ollama + LangChain tool agent
src/runner.py          Shared evaluation harness
scripts/               Evidence helpers
data/learning_history.json
evidence/              Test result dumps
screenshots/           UI screenshots
docs/                  Write-ups (comparison table, learning, submission pack)
```

Key docs for graders: [`docs/comparison_table.md`](docs/comparison_table.md) · [`docs/SUBMISSION_PACK.md`](docs/SUBMISSION_PACK.md) · [`evidence/llm_live_summary.md`](evidence/llm_live_summary.md)

## Submission checklist

- [x] Five classical agents
- [x] LLM agent with ≥2 tools (live Ollama/LangChain evidence in `evidence/`)
- [x] Shared scenarios A–D (includes edge)
- [x] Streamlit comparison UI
- [x] Learning agent experience updates (+ before/after demo)
- [x] README + setup instructions
- [x] Screenshots (`screenshots/` + INDEX)
- [x] Comparison table (`docs/comparison_table.md`)
- [x] Test results (`evidence/scenario_*_results.json`)
- [x] Selection notes drafted (`docs/SELECTION_NOTES.md`) — confirm group winner before Moodle upload
- [ ] Moodle/LMS upload of submission pack (see `docs/SUBMISSION_PACK.md`)

No video is required for this assignment.

## Disclaimer

Simulation only. Tools return local mock data. No live cloud resources are changed.
