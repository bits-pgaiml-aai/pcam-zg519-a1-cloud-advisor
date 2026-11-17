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
screenshots/          # scenario_*.png + scenario_*_results.json + INDEX.md
docs/comparison_table.md
docs/comparison_writeup.md
docs/scenario_results_summary.md
docs/learning_evaluation.md
docs/learning_before_after.md
docs/SELECTION_NOTES.md
```

## Pre-submit checks

1. Confirm screenshots A–D PNG + JSON are present under `screenshots/`.
2. Run `python scripts/sync_reports_from_screenshots.py` so evidence/docs match those JSON files.
3. Confirm LLM rows are live Ollama/LangChain with ≥2 tools (see `evidence/llm_live_summary.md`).
4. Fill bake-off winner in `docs/SELECTION_NOTES.md`.
5. Do not include secrets, `.venv/`, or personal PATs.

## Regenerate helper artifacts

```bash
python scripts/sync_reports_from_screenshots.py
# optional live re-run (needs Ollama), then sync again:
python scripts/generate_evidence.py
python scripts/sync_reports_from_screenshots.py
```
