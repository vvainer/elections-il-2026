#!/usr/bin/env python3
"""
orchestrate_analysis.py
Master Pipeline Orchestrator for Knesset 2026 Election Analysis.
Coordinates validation, merging, report generation, and deployment across pipeline stages.
"""

import os
import sys
import argparse
import subprocess
from datetime import datetime

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPTS_DIR)

def run_cmd(cmd_list, check=True):
    cmd_str = " ".join(cmd_list)
    print(f"\n[RUN] {cmd_str}")
    res = subprocess.run(cmd_list, cwd=PROJECT_ROOT)
    if check and res.returncode != 0:
        print(f"[!] Error: Command failed with exit code {res.returncode}")
        sys.exit(res.returncode)
    return res.returncode

def stage_validate(date_str: str, source: str = "validated", skip_http: bool = False, strict: bool = False):
    topics_dir = os.path.join(PROJECT_ROOT, "data", source, date_str, "topics")
    if not os.path.exists(topics_dir):
        # Fallback to checking staging if validated doesn't exist yet
        staging_dir = os.path.join(PROJECT_ROOT, "data", "staging", date_str, "topics")
        if os.path.exists(staging_dir):
            topics_dir = staging_dir
        else:
            print(f"[!] Neither validated nor staging directory found for date {date_str}.")
            return 1

    report_path = os.path.join(PROJECT_ROOT, "data", "validation_logs", date_str, "tier1_summary.json")
    cmd = [
        sys.executable,
        os.path.join(SCRIPTS_DIR, "validate_links.py"),
        topics_dir,
        "--report", report_path
    ]
    if skip_http:
        cmd.append("--skip-http")
    if strict:
        cmd.append("--strict")
    return run_cmd(cmd, check=strict)

def stage_merge(date_str: str, source: str = "validated"):
    topics_dir = os.path.join(PROJECT_ROOT, "data", source, date_str, "topics")
    if not os.path.exists(topics_dir):
        staging_dir = os.path.join(PROJECT_ROOT, "data", "staging", date_str, "topics")
        if os.path.exists(staging_dir):
            print(f"[*] Validated dir not found, using staging dir: {staging_dir}")
            topics_dir = staging_dir
        else:
            raise FileNotFoundError(f"Topics directory not found for date {date_str}")

    out_file = os.path.join(PROJECT_ROOT, "data", "evaluations", f"{date_str}.json")
    cmd = [
        sys.executable,
        os.path.join(SCRIPTS_DIR, "merge_topics.py"),
        "--topics-dir", topics_dir,
        "--output", out_file,
        "--date", date_str
    ]
    return run_cmd(cmd)

def stage_build(date_str: str, profile: str = "config/profiles/default.yaml"):
    eval_file = os.path.join(PROJECT_ROOT, "data", "evaluations", f"{date_str}.json")
    cmd = [
        sys.executable,
        os.path.join(SCRIPTS_DIR, "run_analysis.py"),
        "--date", date_str,
        "--profile", profile,
        "--eval-file", eval_file
    ]
    return run_cmd(cmd)

def stage_validate_ui(date_str: str, strict: bool = True):
    cmd = [
        sys.executable,
        os.path.join(SCRIPTS_DIR, "validate_ui.py"),
        "--date", date_str
    ]
    if strict:
        cmd.append("--strict")
    return run_cmd(cmd, check=strict)

def stage_push(date_str: str):
    ui_log = os.path.join(PROJECT_ROOT, "data", "validation_logs", date_str, "ui_validation.json")
    if not os.path.exists(ui_log):
        print(f"[!] Deployment BLOCKED: UI validation log does not exist for {date_str} ({ui_log}).")
        sys.exit(1)

    import json
    with open(ui_log, "r", encoding="utf-8") as f:
        ui_data = json.load(f)

    if ui_data.get("status") != "APPROVED":
        print(f"[!] Deployment BLOCKED: UI validation status is '{ui_data.get('status')}'. Defects: {ui_data.get('defects')}")
        sys.exit(1)

    print(f"[*] UI Validation APPROVED. Preparing git commit and push for {date_str}...")
    run_cmd(["git", "add", "data/", "reports/", "docs/"])
    status_res = subprocess.run(["git", "status", "--porcelain"], cwd=PROJECT_ROOT, capture_output=True, text=True)
    if not status_res.stdout.strip():
        print("[*] No changes to commit.")
        return 0
    commit_msg = f"Weekly election analysis update: {date_str} [UI Validated]"
    run_cmd(["git", "commit", "-m", commit_msg])
    run_cmd(["git", "push", "origin", "main"])
    print("[✓] Successfully pushed to origin/main.")
    return 0

def main():
    parser = argparse.ArgumentParser(description="Election Analysis Master Pipeline Orchestrator")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"), help="Analysis date (YYYY-MM-DD)")
    parser.add_argument("--stage", choices=["validate", "merge", "build", "validate-ui", "push", "all"], default="all", help="Pipeline stage to execute")
    parser.add_argument("--source", default="validated", help="Source folder for topics ('validated' or 'staging')")
    parser.add_argument("--skip-http", action="store_true", help="Skip HTTP network checks during validation")
    parser.add_argument("--strict", action="store_true", help="Fail immediately if link or schema errors occur")
    parser.add_argument("--profile", default="config/profiles/default.yaml", help="Path to profile config")
    parser.add_argument("--auto-push", action="store_true", help="Automatically git commit and push after building")
    args = parser.parse_args()

    date_str = args.date
    stage = args.stage

    print(f"=== ELECTION ANALYSIS PIPELINE: {date_str} (Stage: {stage}) ===")

    if stage in ["validate", "all"]:
        stage_validate(date_str, source=args.source, skip_http=args.skip_http, strict=args.strict)

    if stage in ["merge", "all"]:
        stage_merge(date_str, source=args.source)

    if stage in ["build", "all"]:
        stage_build(date_str, profile=args.profile)

    if stage in ["validate-ui", "all"]:
        stage_validate_ui(date_str, strict=args.strict)

    if stage == "push" or (stage == "all" and args.auto_push):
        stage_push(date_str)

    print(f"\n[✓] Stage '{stage}' completed successfully.")

if __name__ == "__main__":
    main()
