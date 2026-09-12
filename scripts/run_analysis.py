#!/usr/bin/env python3
"""
Main Runner script for Election Analysis System.
Executes the evaluation pipeline and generates reports.
"""

import os
import sys
import json
import argparse
from datetime import datetime

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from evaluator import evaluate_full_dataset
from generate_report import generate_markdown_report, generate_html_dashboard

def load_yaml_or_json(filepath: str):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
        
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    if filepath.endswith(".yaml") or filepath.endswith(".yml"):
        if HAS_YAML:
            return yaml.safe_load(content)
        else:
            # Fallback: check if json equivalent exists
            json_path = filepath.rsplit(".", 1)[0] + ".json"
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as jf:
                    return json.load(jf)
            raise RuntimeError(f"PyYAML is not installed and no JSON fallback for {filepath}")
    else:
        return json.loads(content)

def main():
    parser = argparse.ArgumentParser(description="Run Knesset 2026 Election Analysis")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"), help="Analysis date (YYYY-MM-DD)")
    parser.add_argument("--profile", default="config/profiles/default.yaml", help="Path to profile config")
    parser.add_argument("--eval-file", default="", help="Path to raw evaluations JSON")
    args = parser.parse_args()

    date_str = args.date
    profile_path = args.profile
    eval_path = args.eval_file or f"data/evaluations/{date_str}.json"

    print(f"[*] Loading profile: {profile_path}")
    profile_data = load_yaml_or_json(profile_path)

    print(f"[*] Loading evaluation dataset: {eval_path}")
    if not os.path.exists(eval_path):
        print(f"[!] Evaluation file {eval_path} does not exist.")
        sys.exit(1)

    with open(eval_path, "r", encoding="utf-8") as f:
        eval_data = json.load(f)

    print("[*] Running scoring evaluation across 6 criteria with normalized weights...")
    evaluated_result = evaluate_full_dataset(eval_data, profile_data)

    # Ensure output directories exist
    reports_dir = f"reports/{date_str}"
    os.makedirs(reports_dir, exist_ok=True)
    os.makedirs("docs", exist_ok=True)

    # 1. Generate Markdown report
    md_path = f"{reports_dir}/report.md"
    print(f"[*] Generating Markdown report: {md_path}")
    md_content = generate_markdown_report(evaluated_result)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    # 2. Generate GitHub Pages HTML dashboard
    html_path = "docs/index.html"
    print(f"[*] Generating GitHub Pages HTML dashboard: {html_path}")
    html_content = generate_html_dashboard(evaluated_result)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print("\n" + "="*60)
    print("🏆 ELECTION ANALYSIS SUMMARY (TOP PARTIES):")
    print("="*60)
    for p_id, p_data in evaluated_result["parties"].items():
        score = p_data["overall_score"]
        sign = "+" if score > 0 else ""
        print(f"#{p_data['rank']} | {p_data['name_he']:<25} | Score: {sign}{score:.1f} | Mandates: {p_data.get('poll_mandates', '-')}")
    print("="*60)
    print(f"Reports saved to {md_path} and {html_path}")

if __name__ == "__main__":
    main()
