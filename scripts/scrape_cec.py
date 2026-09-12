#!/usr/bin/env python3
"""
scrape_cec.py
Automated web scraping utility for Central Elections Committee (CEC) candidate lists
on https://www.gov.il/he/pages/candidates-lists-26 using headless Chrome stealth.
Outputs parsed candidate rosters to data/static/raw_cec/scraped_cec_all.json.
"""

import subprocess
from bs4 import BeautifulSoup
import re
import json
import os
import shutil
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "static", "raw_cec")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "scraped_cec_all.json")

CHROME_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
    shutil.which("chromium-browser") or ""
]

def find_chrome_binary():
    for p in CHROME_PATHS:
        if p and os.path.exists(p) and os.access(p, os.X_OK):
            return p
    return None

TARGETS = {
    "likud": "https://www.gov.il/he/pages/halikud-tikvahadasha_iist29",
    "yashar": "https://www.gov.il/he/pages/yashar_list_2",
    "beyachad": "https://www.gov.il/he/pages/beyahad_list1",
    "yisrael_beiteinu": "https://www.gov.il/he/pages/israel-beitenu_list11",
    "democrats": "https://www.gov.il/he/pages/hademokratim_list17",
    "shas": "https://www.gov.il/he/pages/shas_list19",
    "yahadut_hatorah": "https://www.gov.il/he/pages/yahadut-degel_list37",
    "otzma_yehudit": "https://www.gov.il/he/pages/yehudit-meuhedet_list14",
    "religious_zionism": "https://www.gov.il/he/pages/tzionutdatit-zehut_list31",
    "raam": "https://www.gov.il/he/pages/raam_list18",
    "hadash_taal": "https://www.gov.il/he/pages/hareshima-hameshutefet_list35",
    "hendel_zeleka": "https://www.gov.il/he/pages/hamiluimnikim-vehakalkalit_list16",
    "amcha-israel_list6": "https://www.gov.il/he/pages/amcha-israel_list6",
    "kachol-lavan_list30": "https://www.gov.il/he/pages/kachol-lavan_list30"
}

def is_valid_candidate_name(name: str) -> bool:
    if not name or len(name.strip()) < 3:
        return False
    # Reject any strings containing digits (e.g. '09.2026')
    if re.search(r"\d", name):
        return False
    # Must contain Hebrew letters
    if not re.search(r"[\u0590-\u05FF]", name):
        return False
    # Reject metadata keywords
    metadata_kws = ["תאריך", "פרסום", "עדכון", "סוג", "יחידות", "שתפו", "ועדת הבחירות", "הבחירות לכנסת", "רשימת המועמדים הוגשה"]
    if any(kw in name for kw in metadata_kws):
        return False
    return True

def scrape_all():
    chrome_bin = find_chrome_binary()
    if not chrome_bin:
        raise RuntimeError("Google Chrome binary not found for stealth scraping.")

    print(f"[*] Starting stealth scraping of {len(TARGETS)} CEC candidate lists...")
    results = {}

    for p_id, url in TARGETS.items():
        final_candidates = []
        t_text = ""
        for attempt in range(1, 4):
            cmd = [
                chrome_bin,
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
                "--dump-dom",
                url
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            html = res.stdout
            soup = BeautifulSoup(html, "html.parser")
            title = soup.find("h3", id="content_title") or soup.find("h1")
            t_text = title.get_text(strip=True) if title else ""
            text = soup.get_text("\n", strip=True)
            lines = [l for l in text.split("\n") if l.strip()]

            candidates = []
            for l in lines:
                # Match pattern: "1. שם המועמד"
                m = re.match(r"^(\d+)\.\s*(.+)$", l)
                if m:
                    pos = int(m.group(1))
                    name = m.group(2).strip()
                    if is_valid_candidate_name(name):
                        candidates.append({"position": pos, "name": name})

            dedup = {}
            for c in candidates:
                if c["position"] not in dedup:
                    dedup[c["position"]] = c["name"]
            final_candidates = [{"position": k, "name": dedup[k]} for k in sorted(dedup.keys())]

            if len(final_candidates) > 0:
                break
            time.sleep(1)

        results[p_id] = {
            "title": t_text,
            "url": url,
            "total_candidates": len(final_candidates),
            "candidates": final_candidates
        }
        print(f"  [✓] {p_id:<20}: {len(final_candidates)} candidates scraped ({t_text})")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n[✓] Saved official scraped CEC lists to {OUTPUT_FILE}")
    return OUTPUT_FILE

if __name__ == "__main__":
    scrape_all()
