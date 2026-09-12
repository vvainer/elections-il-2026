#!/usr/bin/env python3
"""
merge_topics.py
Merges topic evaluation files from data/validated/YYYY-MM-DD/topics/*.json
into a unified evaluation dataset data/evaluations/YYYY-MM-DD.json.
Also supports --split to unpack a full dataset into individual topic files.
"""

import os
import sys
import json
import argparse
from typing import Dict, Any

try:
    import yaml
    HAS_YAML = True
except ImportError:
    # Try importing from local .venv if present
    import site
    venv_site = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".venv", "lib")
    if os.path.exists(venv_site):
        for root, dirs, _ in os.walk(venv_site):
            if "site-packages" in dirs:
                site.addsitedir(os.path.join(root, "site-packages"))
                break
    try:
        import yaml
        HAS_YAML = True
    except ImportError:
        HAS_YAML = False

EXPECTED_TOPICS = [
    "education",
    "governance_reform",
    "future_infrastructure",
    "strategic_posture",
    "religion_and_state",
    "returning_residents",
    "open_market",
    "welfare_reform",
    "government_downsizing"
]

def load_yaml_or_json(filepath: str) -> Any:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    if filepath.endswith(".yaml") or filepath.endswith(".yml"):
        if HAS_YAML:
            return yaml.safe_load(content)
        json_fallback = filepath.rsplit(".", 1)[0] + ".json"
        if os.path.exists(json_fallback):
            with open(json_fallback, "r", encoding="utf-8") as jf:
                return json.load(jf)
        raise RuntimeError(f"PyYAML is not installed and no JSON fallback for {filepath}")
    return json.loads(content)

def split_dataset(input_eval_file: str, output_dir: str):
    """Splits a full evaluation file into individual topic files."""
    print(f"[*] Splitting {input_eval_file} into topic files in {output_dir}...")
    with open(input_eval_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    os.makedirs(output_dir, exist_ok=True)
    parties = data.get("parties", {})

    topics_dict: Dict[str, Dict[str, Any]] = {t: {} for t in EXPECTED_TOPICS}

    for party_id, p_info in parties.items():
        p_topics = p_info.get("topics", {})
        for t_id, t_data in p_topics.items():
            if t_id not in topics_dict:
                topics_dict[t_id] = {}
            topics_dict[t_id][party_id] = {
                "scores": t_data.get("scores", {}),
                "notes": t_data.get("notes", {}),
                "citations": t_data.get("citations", [])
            }

    for t_id, parties_map in topics_dict.items():
        out_file = os.path.join(output_dir, f"{t_id}.json")
        payload = {
            "topic_id": t_id,
            "date": data.get("date", ""),
            "parties": parties_map
        }
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"    [+] Wrote {out_file} ({len(parties_map)} parties)")

    print(f"[✓] Successfully split {len(topics_dict)} topics into {output_dir}")

def merge_topics(topics_dir: str, output_eval_file: str, date_str: str, parties_config_path: str = "config/parties.yaml", polls_config_path: str = "config/polls.yaml"):
    """Merges individual topic files into a full evaluation dataset."""
    print(f"[*] Reading topic files from: {topics_dir}")
    if not os.path.exists(topics_dir):
        raise FileNotFoundError(f"Topics directory not found: {topics_dir}")

    # Load parties and polls metadata if available
    parties_meta = {}
    if os.path.exists(parties_config_path):
        raw_parties = load_yaml_or_json(parties_config_path)
        p_data = raw_parties.get("parties", {})
        if isinstance(p_data, dict):
            for p_id, p_info in p_data.items():
                if isinstance(p_info, dict):
                    parties_meta[p_id] = {
                        "name_he": p_info.get("name_he", p_id),
                        "leader": p_info.get("leader", ""),
                        "current_seats": p_info.get("current_seats", 0)
                    }
        elif isinstance(p_data, list):
            for p_info in p_data:
                if isinstance(p_info, dict):
                    p_id = p_info.get("id", "")
                    parties_meta[p_id] = {
                        "name_he": p_info.get("name_he", p_id),
                        "leader": p_info.get("leader", ""),
                        "current_seats": p_info.get("current_seats", 0)
                    }

    polls_meta = {}
    if os.path.exists(polls_config_path):
        raw_polls = load_yaml_or_json(polls_config_path)
        status_dict = raw_polls.get("parties_status", raw_polls.get("parties", {}))
        if isinstance(status_dict, dict):
            for p_id, p_info in status_dict.items():
                if isinstance(p_info, dict):
                    polls_meta[p_id] = round(p_info.get("poll_average", 0))

    # Scan topic files
    topic_files = [f for f in os.listdir(topics_dir) if f.endswith(".json") and not f.endswith("_report.json")]
    if not topic_files:
        raise ValueError(f"No JSON topic files found in {topics_dir}")

    unified_parties: Dict[str, Dict[str, Any]] = {}

    found_topics = set()
    for tf in sorted(topic_files):
        tpath = os.path.join(topics_dir, tf)
        with open(tpath, "r", encoding="utf-8") as f:
            tdata = json.load(f)

        topic_id = tdata.get("topic_id") or tf.replace(".json", "")
        found_topics.add(topic_id)
        topic_parties = tdata.get("parties", {})

        for party_id, p_eval in topic_parties.items():
            if party_id not in unified_parties:
                p_meta = parties_meta.get(party_id, {})
                mandates = polls_meta.get(party_id, p_meta.get("current_seats", 0))
                unified_parties[party_id] = {
                    "name_he": p_meta.get("name_he", party_id),
                    "leader": p_meta.get("leader", ""),
                    "poll_mandates": mandates,
                    "topics": {}
                }
            
            unified_parties[party_id]["topics"][topic_id] = {
                "scores": p_eval.get("scores", {}),
                "notes": p_eval.get("notes", {}),
                "citations": p_eval.get("citations", [])
            }

    print(f"[*] Assembled {len(found_topics)} topics across {len(unified_parties)} parties.")
    
    missing_topics = set(EXPECTED_TOPICS) - found_topics
    if missing_topics:
        print(f"[!] Warning: Missing expected topics: {missing_topics}")

    full_dataset = {
        "date": date_str,
        "notes": f"Multi-agent cross-validated evaluation dataset for {date_str}.",
        "parties": unified_parties
    }

    os.makedirs(os.path.dirname(os.path.abspath(output_eval_file)), exist_ok=True)
    with open(output_eval_file, "w", encoding="utf-8") as f:
        json.dump(full_dataset, f, ensure_ascii=False, indent=2)

    print(f"[✓] Successfully wrote merged evaluation dataset to: {output_eval_file}")

def main():
    parser = argparse.ArgumentParser(description="Merge or split election analysis topic files")
    parser.add_argument("--topics-dir", help="Directory containing topic JSON files (e.g. data/validated/YYYY-MM-DD/topics)")
    parser.add_argument("--output", help="Path for merged output JSON file (e.g. data/evaluations/YYYY-MM-DD.json)")
    parser.add_argument("--date", help="Analysis date (YYYY-MM-DD)")
    parser.add_argument("--split", help="Split an existing full evaluation file into topic files")
    parser.add_argument("--split-out", help="Output directory when splitting")
    parser.add_argument("--parties", default="config/parties.yaml", help="Path to parties.yaml")
    parser.add_argument("--polls", default="config/polls.yaml", help="Path to polls.yaml")
    args = parser.parse_args()

    if args.split:
        out_dir = args.split_out or "data/staging/split_topics"
        split_dataset(args.split, out_dir)
    elif args.topics_dir and args.output:
        date_str = args.date or os.path.basename(os.path.dirname(os.path.abspath(args.topics_dir)))
        merge_topics(args.topics_dir, args.output, date_str, args.parties, args.polls)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
