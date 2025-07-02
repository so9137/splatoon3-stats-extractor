import re
import json
import uuid
import sys
from pathlib import Path
from datetime import datetime


def parse_splatoon3_log(ocr_text: str) -> dict:
    lines = [line.strip() for line in ocr_text.splitlines() if line.strip()]
    
    # Extract X Power
    x_power = None
    for line in lines:
        m = re.match(r"X Power[:\s]+([\d\.]+)", line, re.IGNORECASE)
        if m:
            x_power = m.group(1)
            break
    if not x_power:
        raise ValueError("X Power not found in the text.")

    # Determine rule
    rules = ["Splat Zones", "Tower Control", "Rainmaker", "Clam Blitz"]
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

    # Extract results, scores, and stages
    for line in lines:
        if "victory" in line.lower() or "defeat" in line.lower():
            results.append(line)
        elif "score" in line.lower() or "knockout" in line.lower():
            score = line.replace("Score: ", "").replace("!", "").strip()
            scores.append(score)
        elif rule.lower() in line.lower():
            stage = line.replace(rule, "").strip()
            stages.append(stage)

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


def main(txt_path: Path, json_out: Path):
    ocr_text = txt_path.read_text(encoding="utf-8")
    parsed = parse_splatoon3_log(ocr_text)
    json_out.write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Parsed JSON written to {json_out}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert.py ../resource/input.txt ../out/output.json")
        sys.exit(1)
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])
    main(input_file, output_file)
