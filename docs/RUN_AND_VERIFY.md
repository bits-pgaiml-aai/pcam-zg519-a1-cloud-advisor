# Run and verify

1. `python -m venv .venv` and activate it.
2. `pip install -r requirements.txt`
3. Start Ollama and pull the model in README.
4. `streamlit run app.py`
5. Run scenarios A, B, C, D → confirm six agents (or five if LLM unchecked).
6. Record a Learning outcome and re-run.
7. Save screenshots under `screenshots/` and JSON under `evidence/`.
8. Optional: `python scripts/generate_evidence.py`
