# Ollama setup

```bash
ollama serve
ollama pull qwen2.5:1.5b-instruct
# optional
ollama pull qwen3:1.7b
set OLLAMA_MODEL=qwen2.5:1.5b-instruct
```

## Common issues

- `Failed to connect to Ollama` → start `ollama serve` first.
- Model not found → `ollama pull <model>`.
- No tool calls from small models → agent still gathers ≥2 tool results via ensure/fallback and grounds the recommendation.

## Verify

```bash
python -m src.cli A
```

Check `tools_called` / `tool_trace` in saved JSON under `evidence/`.
