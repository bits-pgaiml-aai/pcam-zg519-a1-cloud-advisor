# Team approach — independent implementations + best-one submission

Updated after team discussion.

## Decision

1. **Everyone builds a complete Assignment-1** on their own (all six agents, scenarios, Streamlit, docs).
2. Near the deadline, we **score each version** against the official rubric.
3. The **best overall implementation is submitted** as Group 11’s assignment.
4. Other versions stay in the repo as member archives (learning / backup).

This replaces the earlier “split modules across people” plan.

---

## What each person must deliver

A complete package covering all rubric rows (20 marks):

| Criterion | Marks | Must show |
|-----------|------:|-----------|
| Five classical agents | 5 | Separate, correct decision mechanisms |
| LLM agent + tool calling | 4 | Local Ollama via LangChain; ≥2 tools; evidence used |
| Shared scenarios + testing | 3 | ≥3 scenarios (normal, critical, edge); same input to all agents |
| Streamlit UI + comparison | 3 | Select scenario; show decisions/reasons; clear compare |
| Learning + evaluation | 3 | Experience/history updates; evidence checked; limitations noted |
| Documentation + demo | 2 | README, setup, screenshots, organized code |

Suggested layout (pick one):

```
members/<yourname>/
  README.md
  requirements.txt
  app.py
  src/...
  evidence/...
  screenshots/...
```

Or a personal branch: `member/<yourname>` with a full project at root of that branch.

---

## Suggested timeline

| When | Milestone |
|------|-----------|
| By 14 Nov | Personal implementation runnable end-to-end |
| 15–16 Nov | Self-test all rubric items + screenshots |
| 16–17 Nov | **Group bake-off:** run each version, score, pick winner |
| 17–18 Nov | Polish winning version + submit |

---

## How we choose the winner

Score each implementation 0–full marks per rubric row (honest group scoring).  
Winner = highest total. Tie-breakers, in order:

1. LLM tool evidence clearly shown (≥2 tools)
2. Learning agent history clearly affects decisions
3. Cleanest Streamlit comparison + docs
4. Fewest setup issues for a fresh machine

Record the decision in `docs/SELECTION_NOTES.md` (who won, scores, why).

---

## Ground rules

- Topic and required scenarios stay as in the official brief.
- Simulation only — no live cloud changes.
- Help each other with blockers (Ollama, Streamlit), but keep implementations independent until selection.
- After selection, everyone helps polish the winning submission if needed.

## Starter scaffold

Repo root has a shared starter. Use it if helpful, or build your own structure — scoring is on completeness and rubric fit, not on matching the starter exactly.
