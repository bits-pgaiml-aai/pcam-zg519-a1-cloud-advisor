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
```

Optional model override:

```bash
set OLLAMA_MODEL=qwen3:1.7b
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
docs/                  Write-ups
```

## Submission checklist

- [x] Five classical agents
- [x] LLM agent with ≥2 tools
- [x] Shared scenarios A–D (includes edge)
- [x] Streamlit comparison UI
- [x] Learning agent experience updates
- [x] README + setup instructions
- [ ] Screenshots (capture from Streamlit before submit)
- [ ] Group bake-off selection recorded in `docs/SELECTION_NOTES.md`

## Disclaimer

Simulation only. Tools return local mock data. No live cloud resources are changed.
