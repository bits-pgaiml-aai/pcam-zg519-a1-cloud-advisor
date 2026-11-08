from __future__ import annotations

import argparse
import json

from src.runner import run_all_agents


def main() -> None:
    parser = argparse.ArgumentParser(description="Run cloud advisor agents on one scenario")
    parser.add_argument("scenario_id", choices=["A", "B", "C", "D", "a", "b", "c", "d"])
    parser.add_argument("--no-llm", action="store_true", help="Skip Ollama LLM agent")
    args = parser.parse_args()
    payload = run_all_agents(args.scenario_id.upper(), include_llm=not args.no_llm)
    print(json.dumps(payload["comparison"], indent=2))


if __name__ == "__main__":
    main()
