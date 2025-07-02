import json
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path

from const import rules_dict, x_power_patterns_dict, keywords_dict


def parse_splatoon3_log(ocr_text: str, lang: str) -> dict:
    lines = [line.strip() for line in ocr_text.splitlines() if line.strip()]

    # Extract X Power
    x_power = None
    for line in lines:
        m = re.match(x_power_patterns_dict[lang], line, re.IGNORECASE)
        if m:
            x_power = m.group(1)
            break
    if not x_power:
        raise ValueError("X Power not found in the text.")

    # Determine rule
    rules = rules_dict.get(lang)
    rule = None
    for line in lines:
        for r in rules:
            if line.lower().startswith(r.lower()):
                rule = r
                break
        if rule:
            break
    if not rule:
        raise ValueError("No valid rule found in the text.")

    results = []
    scores = []
    stages = []
    keywords = keywords_dict[lang]
    victory_keyword = keywords["victory"]
    defeat_keyword = keywords["defeat"]
    score_keyword = keywords["score"]
    score_prefix = keywords["score_prefix"]
    knockout_keyword = keywords["knockout"]

    # Extract results, scores, and stages
    for line in lines:
        if victory_keyword in line.lower() or defeat_keyword in line.lower():
            results.append(line.replace("!", "").replace(".", ""))
        elif score_keyword in line.lower() or knockout_keyword in line.lower():
            score = line.replace(score_prefix, "").replace("!", "").replace("◎", "0").replace("！","").strip()
            scores.append(score)
        elif rule.lower() in line.lower():
            stage = line.replace(rule, "").strip()
            stages.append(stage)

    print("results:", results)
    print("scores:", scores)
    print("stages:", stages)

    # Verify that we have the same number of results, scores, and stages
    if not (len(results) == len(scores) == len(stages)):
        raise ValueError("Mismatch in number of results, scores, and stages.")

    # Parse each battle
    battles = []
    for result, score, stage in zip(results, scores, stages):
        battle = {
            "result": result,
            "score": score,
            "stage": stage
        }
        battles.append(battle)

    # Reverse the order of battles to match the original log order
    battles.reverse()

    return {
        "datetime": datetime.now().isoformat(),
        "set_id": str(uuid.uuid4()),
        "x_power": x_power,
        "rule": rule,
        "battles": battles
    }


def main(txt_path: Path, json_out: Path, lang: str = "en"):
    ocr_text = txt_path.read_text(encoding="utf-8")
    parsed = parse_splatoon3_log(ocr_text, lang)
    json_out.write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Parsed JSON written to {json_out}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python convert.py ../resource/input.txt ../out/output.json")
        sys.exit(1)
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])
    lang = sys.argv[3].lower()
    main(input_file, output_file, lang)
