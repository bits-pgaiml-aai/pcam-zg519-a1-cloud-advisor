# Work split — Group 11

Fair split by deliverable ownership. Scaffold already exists in the repo; each owner **owns quality** of their area (refine, test, document).

---

## 1. S. Bhagat Singh — Classical agents (Simple → Goal) + world

**Owns**

| Task | Files |
|------|--------|
| Simple Reflex agent (condition → action only) | `src/agents/simple_reflex.py` |
| Model-Based Reflex (internal state / streaks) | `src/agents/model_based.py` |
| Goal-Based (look-ahead + pass/fail goal test) | `src/agents/goal_based.py` |
| Scenario metrics A–D + catalog polish | `src/world.py` |
| Short note: why these three differ on A/B/C/D | `docs/agent_notes_reflex_goal.md` |

**Done when**

- [ ] Each agent returns `recommendation`, `reasoning`, `current_state_summary`, `trade_offs`, `monitoring_plan`
- [ ] Decisions clearly differ by mechanism (not copy-paste)
- [ ] Scenarios A/B/C match assignment text; D remains the edge/ambiguous case
- [ ] CLI works without LLM: `python -m src.cli A --no-llm`

---

## 2. Karthik K — Utility + Learning + evaluation

**Owns**

| Task | Files |
|------|--------|
| Utility-Based agent (score feasible plans) | `src/agents/utility_based.py` |
| Learning agent (experience counts, explore, explain effect) | `src/agents/learning.py` |
| Experience store | `data/learning_history.json` |
| Learning write-up: how history changes decisions + limitations | `docs/learning_evaluation.md` |
| Before/after learning demo evidence | `evidence/learning_*.json` |

**Done when**

- [ ] Utility ranking is visible in decision extras
- [ ] Learning updates success/failure counts and shows rates in output
- [ ] Streamlit “Record learning outcome” path verified end-to-end
- [ ] Limitations acknowledged in docs/UI (sparse data, exploration risk)

---

## 3. Snehalatha M — LLM agent + tools

**Owns**

| Task | Files |
|------|--------|
| Mock cloud tools (≥2 used every run) | `src/tools/cloud_tools.py` |
| Ollama + LangChain tool-calling agent | `src/llm_agent.py` |
| Tool-call evidence dumps for A/B/C (and D) | `evidence/llm_scenario_*.json` |
| Ollama setup notes (model pull, common errors) | `docs/OLLAMA_SETUP.md` |
| Pin working versions if needed | `requirements.txt` (LLM-related lines) |

**Done when**

- [ ] Local Ollama model runs (e.g. `qwen2.5:1.5b-instruct` or `qwen3:1.7b`)
- [ ] Each LLM run calls **at least two** tools and cites evidence in reasoning
- [ ] Recommendation grounded in tool results (no invented metrics)
- [ ] Fallback path documented if model skips tool calls

---

## 4. Venkata Srinivasa Rao Tunuguntla — UI, integration, docs, submit

**Owns**

| Task | Files |
|------|--------|
| Shared runner (same percept → all agents) | `src/runner.py`, `src/cli.py` |
| Streamlit comparison UI | `app.py` |
| README + run instructions | `README.md`, `docs/RUN_AND_VERIFY.md` |
| Screenshots for scenarios A/B/C (+ D) | `screenshots/` |
| Comparison table + why decisions differ | `docs/comparison_writeup.md` |
| Final zip / submission packaging | `Group15`-style folder if needed |

**Done when**

- [ ] UI: select scenario → show all six decisions + reasons + comparison table
- [ ] Three required scenario results + screenshots captured
- [ ] README has setup/run steps teammates can follow
- [ ] Submission checklist in README marked complete

---

## Shared rules (everyone)

1. **Same input:** do not give agents different scenario data for the “fair compare” runs.
2. **Branch / PR:** optional per person (`member/<name>-…`); merge to `main` after a quick peer look.
3. **No live cloud changes:** simulation + mock tools only.
4. **Group sync:** one dry-run together before submission (all scenarios + Learning update + LLM tools visible).

## Suggested timeline (due 18 Nov)

| When | Milestone |
|------|-----------|
| By 11 Nov | Bhagat + Karthik classical/learning agents stable |
| By 13 Nov | Snehalatha LLM + tools green on Ollama |
| By 15 Nov | Venkat UI + screenshots + comparison write-up |
| 16–17 Nov | Full group dry-run + fix gaps |
| 18 Nov | Submit |

## Quick contact map

| If you need… | Ask |
|--------------|-----|
| Scenario numbers / SLA | Bhagat |
| Learning history / utility scoring | Karthik |
| Ollama / tool traces | Snehalatha |
| UI / README / screenshots / packaging | Venkat |
