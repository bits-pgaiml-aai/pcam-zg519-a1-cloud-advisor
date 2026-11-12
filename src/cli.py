from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.runner import run_all_agents


def main() -> None:
    parser = argparse.ArgumentParser(description="Run cloud advisor agents on one scenario")
    parser.add_argument("scenario_id", choices=["A", "B", "C", "D", "a", "b", "c", "d"])
    parser.add_argument("--no-llm", action="store_true", help="Skip Ollama LLM agent")
    parser.add_argument(
        "--save",
        type=str,
        default="",
        help="Optional path to write full JSON results",
    )
    args = parser.parse_args()
    payload = run_all_agents(args.scenario_id.upper(), include_llm=not args.no_llm)
    print(json.dumps(payload["comparison"], indent=2))
    print("\nWhy decisions differ:")
    print(payload["why_decisions_differ"])
    if args.save:
        path = Path(args.save)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"\nSaved: {path}")


if __name__ == "__main__":
    main()
