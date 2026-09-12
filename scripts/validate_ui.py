#!/usr/bin/env python3
"""
validate_ui.py
Automated UI Validation & Snapshot Capture Script for Election Analysis.
Captures Desktop and Mobile screenshots using headless Chromium/Google Chrome,
validates HTML DOM structure, RTL direction, table integrity, and topic accordions,
and writes an audit log to data/validation_logs/YYYY-MM-DD/ui_validation.json.
"""

import os
import sys
import json
import argparse
import subprocess
import shutil
import re
from html.parser import HTMLParser
from typing import Dict, List, Any, Optional

CHROME_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
    shutil.which("chromium-browser") or ""
]

def find_chrome_binary() -> Optional[str]:
    for path in CHROME_PATHS:
        if path and os.path.exists(path) and os.access(path, os.X_OK):
            return path
    return None

def capture_snapshot(chrome_bin: str, html_path: str, output_img: str, width: int, height: int) -> bool:
    os.makedirs(os.path.dirname(os.path.abspath(output_img)), exist_ok=True)
    file_url = f"file://{os.path.abspath(html_path)}"
    cmd = [
        chrome_bin,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        f"--window-size={width},{height}",
        f"--screenshot={output_img}",
        file_url
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return os.path.exists(output_img) and os.path.getsize(output_img) > 0
    except Exception as e:
        print(f"[!] Warning: Snapshot capture failed: {e}")
        return False

class DashboardHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.html_attrs = {}
        self.has_viewport = False
        self.leaderboard_cards = 0
        self.overview_table_rows = 0
        self.topic_accordions = 0
        self.criteria_tables = 0
        self.criteria_rows = 0
        self.citation_links = []
        self.badges = []
        self.tab_buttons = 0
        self.candidate_cards = 0
        self.github_links = 0
        
        # State tracking
        self.in_overview_tbody = False
        self.in_criteria_tbody = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        if tag == "html":
            self.html_attrs = attrs_dict
            
        elif tag == "meta":
            if attrs_dict.get("name") == "viewport":
                self.has_viewport = True

        elif tag == "button":
            cls = attrs_dict.get("class", "")
            if "tab-button" in cls:
                self.tab_buttons += 1
                
        elif tag == "div":
            cls = attrs_dict.get("class", "")
            if "leaderboard-card" in cls:
                self.leaderboard_cards += 1
            if "candidate-card" in cls:
                self.candidate_cards += 1
                
        elif tag == "details":
            cls = attrs_dict.get("class", "")
            if "topic-accordion" in cls:
                self.topic_accordions += 1
                
        elif tag == "table":
            cls = attrs_dict.get("class", "")
            if "criteria-table" in cls:
                self.criteria_tables += 1
                
        elif tag == "tbody":
            pass
            
        elif tag == "tr":
            pass
            
        elif tag == "a":
            cls = attrs_dict.get("class", "")
            if "github-link-btn" in cls:
                self.github_links += 1
            if "citation-link" in cls or "href" in attrs_dict:
                href = attrs_dict.get("href", "")
                self.citation_links.append(href)
                
        elif tag == "span":
            cls = attrs_dict.get("class", "")
            if "badge" in cls:
                self.badges.append(cls)

def validate_html_dom(html_path: str) -> Tuple[List[str], Dict[str, Any]]:
    defects = []
    metrics = {}

    if not os.path.exists(html_path):
        return [f"HTML dashboard file does not exist: {html_path}"], {}

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    parser = DashboardHTMLParser()
    try:
        parser.feed(content)
    except Exception as e:
        defects.append(f"HTML parsing error: {e}")

    # 1. RTL and Language check
    lang = parser.html_attrs.get("lang", "")
    direction = parser.html_attrs.get("dir", "")
    if lang != "he":
        defects.append(f"Root <html> tag has incorrect lang='{lang}' (expected 'he')")
    if direction != "rtl":
        defects.append(f"Root <html> tag has incorrect dir='{direction}' (expected 'rtl')")

    # 2. Viewport check
    if not parser.has_viewport:
        defects.append("Missing <meta name='viewport'> tag for responsive layout")

    # 3. Leaderboard Cards check
    if parser.leaderboard_cards < 3:
        defects.append(f"Leaderboard contains only {parser.leaderboard_cards} cards (minimum 3 required)")

    # 4. Topic Accordions check (Expect 9 topics)
    if parser.topic_accordions < 9:
        defects.append(f"Found {parser.topic_accordions} topic accordions (expected 9 policy topics)")

    # 5. Criteria Tables check
    if parser.criteria_tables < parser.topic_accordions:
        defects.append(f"Criteria tables count ({parser.criteria_tables}) is less than topic accordions ({parser.topic_accordions})")

    # 6. Badges check
    if len(parser.badges) < 20:
        defects.append(f"Found unusually low number of score badges ({len(parser.badges)})")

    # 7. Citations check
    invalid_links = [l for l in parser.citation_links if not l or l == "#" or not l.startswith("http")]
    if invalid_links:
        defects.append(f"Found {len(invalid_links)} empty or invalid citation link hrefs")

    # 8. CSS Media Query check
    if "@media" not in content:
        defects.append("Missing CSS media queries for responsive layouts (@media)")

    # 9. Navigation Tabs check
    if parser.tab_buttons < 4:
        defects.append(f"Found only {parser.tab_buttons} navigation tab buttons (minimum 4 required)")

    # 10. Candidate Dossiers check
    if parser.candidate_cards < 14:
        defects.append(f"Found only {parser.candidate_cards} candidate cards (minimum 14 required)")

    # 11. Public GitHub Raw Matrix links check
    if parser.github_links < 8:
        defects.append(f"Found only {parser.github_links} public GitHub matrix links (minimum 8 required)")

    metrics = {
        "lang": lang,
        "dir": direction,
        "has_viewport": parser.has_viewport,
        "tab_buttons": parser.tab_buttons,
        "leaderboard_cards": parser.leaderboard_cards,
        "candidate_cards": parser.candidate_cards,
        "topic_accordions": parser.topic_accordions,
        "criteria_tables": parser.criteria_tables,
        "total_badges": len(parser.badges),
        "total_links": len(parser.citation_links),
        "github_links": parser.github_links,
        "file_size_kb": round(len(content.encode("utf-8")) / 1024, 1)
    }

    return defects, metrics

def main():
    parser = argparse.ArgumentParser(description="Validate HTML dashboard UI and capture headless screenshots")
    parser.add_argument("--html", default="docs/index.html", help="Path to index.html")
    parser.add_argument("--date", default="2026-09-09", help="Analysis date (YYYY-MM-DD)")
    parser.add_argument("--out-dir", help="Output directory for logs and snapshots")
    parser.add_argument("--skip-snapshots", action="store_true", help="Skip headless browser snapshot capture")
    parser.add_argument("--strict", action="store_true", help="Exit with code 1 if validation defects exist")
    args = parser.parse_args()

    date_str = args.date
    html_path = args.html
    out_dir = args.out_dir or os.path.join("data", "validation_logs", date_str)
    snapshots_dir = os.path.join(out_dir, "snapshots")
    os.makedirs(snapshots_dir, exist_ok=True)

    print(f"=== UI VALIDATION: {html_path} ({date_str}) ===")

    # DOM validation
    print("[*] Running DOM structure and RTL compliance verification...")
    defects, metrics = validate_html_dom(html_path)

    # Browser snapshots
    desktop_snap = os.path.join(snapshots_dir, "desktop.png")
    mobile_snap = os.path.join(snapshots_dir, "mobile.png")
    snapshots_taken = False

    if not args.skip_snapshots:
        chrome_bin = find_chrome_binary()
        if chrome_bin:
            print(f"[*] Found Chrome binary at: {chrome_bin}")
            print(f"[*] Capturing Desktop snapshot (1280x800) -> {desktop_snap}...")
            d_ok = capture_snapshot(chrome_bin, html_path, desktop_snap, 1280, 800)
            print(f"[*] Capturing Mobile snapshot (375x812) -> {mobile_snap}...")
            m_ok = capture_snapshot(chrome_bin, html_path, mobile_snap, 375, 812)
            snapshots_taken = d_ok and m_ok
            if not snapshots_taken:
                defects.append("Failed to capture one or more browser snapshots")
        else:
            print("[!] Warning: Google Chrome binary not found; skipping visual snapshots.")
            defects.append("Chrome binary not found for headless snapshot capture")

    status = "APPROVED" if len(defects) == 0 else "REJECTED"

    report_payload = {
        "date": date_str,
        "html_file": html_path,
        "status": status,
        "defects_count": len(defects),
        "defects": defects,
        "metrics": metrics,
        "snapshots": {
            "desktop": desktop_snap if os.path.exists(desktop_snap) else None,
            "mobile": mobile_snap if os.path.exists(mobile_snap) else None
        }
    }

    json_report_path = os.path.join(out_dir, "ui_validation.json")
    with open(json_report_path, "w", encoding="utf-8") as f:
        json.dump(report_payload, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"UI VALIDATION RESULT: {status}")
    print("=" * 60)
    print(f"- Log written to: {json_report_path}")
    if snapshots_taken:
        print(f"- Desktop Snapshot: {desktop_snap}")
        print(f"- Mobile Snapshot:  {mobile_snap}")
    print(f"- Leaderboard Cards: {metrics.get('leaderboard_cards', 0)}")
    print(f"- Topic Accordions:  {metrics.get('topic_accordions', 0)}")
    print(f"- Total Citations:   {metrics.get('total_links', 0)}")

    if defects:
        print(f"\n[!] Defect details ({len(defects)} issues):")
        for d in defects:
            print(f"    ✗ {d}")

    if args.strict and status == "REJECTED":
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
