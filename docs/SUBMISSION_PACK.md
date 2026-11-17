# Submission pack (Group 11)

**Due:** Wednesday, 18 November 2026, 11:59 PM

## What the assignment asks for

- Source code (5 classical + 1 LLM agent)
- `requirements.txt`, README, Streamlit UI, setup/run instructions
- ≥3 scenario test results and screenshots
- Comparison table and explanation of why decisions differ

No video upload is required.

## Include in the Moodle zip / repo pointer

```text
app.py
requirements.txt
README.md
src/                  # agents, tools, llm_agent, world, runner
data/learning_history.json
evidence/             # scenario_*_results.json, comparison_summary.json,
                      # learning_before_after.json
screenshots/          # PDFs + PNGs + INDEX.md
docs/comparison_table.md
docs/comparison_writeup.md
docs/learning_evaluation.md
docs/learning_before_after.md
docs/SELECTION_NOTES.md
```

## Pre-submit checks

1. `python scripts/generate_evidence.py` with Ollama up and a tools-capable model.
2. Confirm LLM rows are **not** labeled only as fallback (live tool-calling preferred).
3. Screenshots cover A/B/C (D optional but included).
4. Fill bake-off winner in `docs/SELECTION_NOTES.md`.
5. Do not include secrets, `.venv/`, or personal PATs.

## Regenerate helper artifacts

```bash
python scripts/generate_evidence.py
python scripts/generate_submission_artifacts.py
```
