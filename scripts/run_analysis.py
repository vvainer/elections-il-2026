#!/usr/bin/env python3
"""
Main Runner script for Election Analysis System.
Executes the evaluation pipeline across all active profiles,
incorporates static candidate & party background knowledge,
and generates Markdown reports and the interactive HTML dashboard.
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, Any

try:
    import yaml
    HAS_YAML = True
except ImportError:
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

from evaluator import evaluate_full_dataset
from generate_report import generate_markdown_report, generate_html_dashboard

def load_yaml_or_json(filepath: str) -> Dict[str, Any]:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
        
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    if filepath.endswith(".yaml") or filepath.endswith(".yml"):
        if HAS_YAML:
            return yaml.safe_load(content)
        else:
            json_path = filepath.rsplit(".", 1)[0] + ".json"
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as jf:
                    return json.load(jf)
            raise RuntimeError(f"PyYAML is not installed and no JSON fallback for {filepath}")
    else:
        return json.loads(content)

def main():
    parser = argparse.ArgumentParser(description="Run Knesset 2026 Election Analysis across Worldview Profiles")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"), help="Analysis date (YYYY-MM-DD)")
    parser.add_argument("--profiles-dir", default="config/profiles", help="Path to profiles directory")
    parser.add_argument("--profile", default="", help="Path to single profile config (optional)")
    parser.add_argument("--eval-file", default="", help="Path to raw evaluations JSON")
    parser.add_argument("--static-dir", default="data/static", help="Path to static knowledge base directory")
    args = parser.parse_args()

    date_str = args.date
    eval_path = args.eval_file or f"data/evaluations/{date_str}.json"
    static_dir = args.static_dir if os.path.exists(args.static_dir) else None

    print(f"[*] Loading evaluation dataset: {eval_path}")
    if not os.path.exists(eval_path):
        print(f"[!] Evaluation file {eval_path} does not exist.")
        sys.exit(1)

    with open(eval_path, "r", encoding="utf-8") as f:
        eval_data = json.load(f)

    # Discover profiles to evaluate
    profiles = {}
    if args.profile:
        stem = os.path.splitext(os.path.basename(args.profile))[0]
        data = load_yaml_or_json(args.profile)
        data["profile_id"] = stem
        profiles[stem] = data
    else:
        prof_dir = args.profiles_dir
        if not os.path.exists(prof_dir):
            print(f"[!] Profiles directory {prof_dir} not found.")
            sys.exit(1)
        for fname in sorted(os.listdir(prof_dir)):
            if fname.endswith((".yaml", ".yml")):
                stem = os.path.splitext(fname)[0]
                fpath = os.path.join(prof_dir, fname)
                try:
                    data = load_yaml_or_json(fpath)
                    data["profile_id"] = stem
                    profiles[stem] = data
                except Exception as e:
                    print(f"[!] Warning: failed to load profile {fpath}: {e}")

    if not profiles:
        print("[!] No valid profiles found.")
        sys.exit(1)

    print(f"[*] Evaluating {len(profiles)} worldview profile(s): {', '.join(profiles.keys())}")

    evaluated_results = {}
    reports_dir = f"reports/{date_str}"
    os.makedirs(reports_dir, exist_ok=True)
    os.makedirs("docs", exist_ok=True)

    for prof_id, prof_data in profiles.items():
        print(f"  -> Evaluating profile: '{prof_data.get('profile_name', prof_id)}' ({prof_id})")
        result = evaluate_full_dataset(eval_data, prof_data, static_kb_dir=static_dir)
        evaluated_results[prof_id] = result

        # Save individual profile evaluated JSON
        out_eval = f"data/evaluations/{date_str}_{prof_id}_evaluated.json"
        with open(out_eval, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        # Generate per-profile Markdown report
        prof_md_path = f"{reports_dir}/{prof_id}.md"
        with open(prof_md_path, "w", encoding="utf-8") as f:
            f.write(generate_markdown_report(result))

    # Generate main report.md (default profile or first profile)
    default_key = "default" if "default" in evaluated_results else list(evaluated_results.keys())[0]
    main_md_path = f"{reports_dir}/report.md"
    print(f"[*] Generating primary Markdown report: {main_md_path}")
    with open(main_md_path, "w", encoding="utf-8") as f:
        f.write(generate_markdown_report(evaluated_results[default_key]))

    # Generate GitHub Pages HTML dashboard with interactive switcher
    html_path = "docs/index.html"
    print(f"[*] Generating interactive GitHub Pages HTML dashboard: {html_path}")
    html_content = generate_html_dashboard(evaluated_results, default_profile_id=default_key)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print("\n" + "="*65)
    print(f"🏆 PRIMARY ELECTION ANALYSIS SUMMARY ({evaluated_results[default_key].get('profile_name')}):")
    print("="*65)
    for p_id, p_data in evaluated_results[default_key]["parties"].items():
        sign = "+" if p_data['overall_score'] > 0 else ""
        print(f"  #{p_data.get('rank', '-')} | {p_data.get('name_he', p_id):<18} | Score: {sign}{p_data['overall_score']:>5.1f} | Mandates: {p_data.get('poll_mandates', '-'):>2}")
    print("="*65)
    print(f"[✓] Successfully generated reports in {reports_dir} and {html_path}")

if __name__ == "__main__":
    main()
