from __future__ import annotations

import json
import sys
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.display import format_recommendation
SHOTS = ROOT / "screenshots"
OUT = SHOTS / "recovered"

PDF_MAP = {
    "Cloud Resource and Cost Optimization Advisor.pdf": "A",
    "Cloud Resource and Cost Optimization Advisor_2.pdf": "B",
    "Cloud Resource and Cost Optimization Advisor_3.pdf": "C",
    "Cloud Resource and Cost Optimization Advisor_4.pdf": "D",
}


def recover_pdf_text() -> list[str]:
    links: list[str] = []
    for pdf_name, scenario_id in PDF_MAP.items():
        pdf_path = SHOTS / pdf_name
        doc = fitz.open(pdf_path)
        pages: list[str] = []
        for i, page in enumerate(doc):
            text = page.get_text("text").replace("keyboard_arrow_down ", "")
            pages.append(f"## Page {i + 1}/{len(doc)}\n\n{text.strip()}\n")
        doc.close()
        md_path = OUT / f"scenario_{scenario_id}_from_pdf.md"
        md_path.write_text(
            f"# Scenario {scenario_id} — recovered from `{pdf_name}`\n\n"
            + "\n".join(pages),
            encoding="utf-8",
        )
        links.append(f"- Scenario {scenario_id}: [{md_path.name}]({md_path.name})")
        print(f"wrote {md_path}")
    return links


def recover_from_evidence() -> list[str]:
    links: list[str] = []
    for sid in "ABCD":
        data = json.loads(
            (ROOT / "evidence" / f"scenario_{sid}_results.json").read_text(
                encoding="utf-8"
            )
        )
        percept = data["scenario"]
        rows = []
        for result in data["results"]:
            rows.append(
                {
                    "agent": result["agent"],
                    "recommendation": result["recommendation"],
                    "display": format_recommendation(
                        percept, result["recommendation"]
                    ),
                    "reasoning": result.get("reasoning", ""),
                    "current_state_summary": result.get("current_state_summary", ""),
                    "trade_offs": result.get("trade_offs", ""),
                    "monitoring_plan": result.get("monitoring_plan", ""),
                }
            )

        json_path = OUT / f"scenario_{sid}_full_decisions.json"
        json_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")

        lines = [
            f"# Scenario {sid} — full agent decisions (recovered)",
            "",
            f"**Scenario:** {percept.get('name')} — {percept.get('description')}",
            "",
            "| agent | display |",
            "| --- | --- |",
        ]
        for row in rows:
            lines.append(f"| {row['agent']} | {row['display']} |")
        lines.append("")
        for row in rows:
            lines.extend(
                [
                    f"## {row['agent']}: {row['display']}",
                    "",
                    f"- **recommendation:** `{row['recommendation']}`",
                    f"- **current state:** {row['current_state_summary']}",
                    f"- **reasoning:** {row['reasoning']}",
                    f"- **trade-offs:** {row['trade_offs']}",
                    f"- **monitoring:** {row['monitoring_plan']}",
                    "",
                ]
            )
        md_path = OUT / f"scenario_{sid}_full_decisions.md"
        md_path.write_text("\n".join(lines), encoding="utf-8")
        links.append(
            f"- Scenario {sid}: [{md_path.name}]({md_path.name}), "
            f"[{json_path.name}]({json_path.name})"
        )
        print(f"wrote {md_path} {json_path}")
    return links


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    embeds = SHOTS / "recovered_embeds"
    if embeds.exists():
        for path in embeds.glob("*"):
            path.unlink()
        embeds.rmdir()

    pdf_links = recover_pdf_text()
    evidence_links = recover_from_evidence()
    readme = "\n".join(
        [
            "# Recovered screenshot text",
            "",
            "Browser print-to-PDF clipped some Streamlit table cells visually.",
            "The PDF text layer and expander bodies still contain the full strings.",
            "Evidence JSON is also used to rebuild complete `display` recommendations.",
            "",
            "## From PDF text layer",
            "",
            *pdf_links,
            "",
            "## Full decisions rebuilt from evidence",
            "",
            *evidence_links,
            "",
        ]
    )
    (OUT / "README.md").write_text(readme, encoding="utf-8")
    print("done")


if __name__ == "__main__":
    main()
