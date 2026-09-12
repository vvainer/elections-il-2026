#!/usr/bin/env python3
"""
validate_links.py
Automated Tier-1 Link & Schema Validator for Election Analysis.
Checks HTTP status codes of all citation URLs and verifies JSON schema and score bounds.
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Any

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
VALID_CRITERIA = [
    "c1_platform",
    "c2_leader_statements",
    "c3_leader_actions",
    "c4_candidates_statements",
    "c5_candidates_actions",
    "c6_designated_executive"
]

def check_url(url: str, timeout: float = 10.0) -> Tuple[str, bool, int, str]:
    """Check if a URL is reachable via HTTP HEAD or GET."""
    if not url.startswith("http://") and not url.startswith("https://"):
        return url, False, 0, "Invalid protocol (must be http or https)"

    import urllib.parse
    try:
        parts = urllib.parse.urlsplit(url)
        safe_path = urllib.parse.quote(parts.path)
        safe_query = urllib.parse.quote(parts.query, safe="=&?+")
        safe_url = urllib.parse.urlunsplit((parts.scheme, parts.netloc, safe_path, safe_query, parts.fragment))
    except Exception:
        safe_url = url

    req = urllib.request.Request(
        safe_url,
        headers={"User-Agent": USER_AGENT, "Accept": "*/*"}
    )
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Try HEAD first
    try:
        req.get_method = lambda: "HEAD"
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as response:
            code = response.getcode()
            if code < 400:
                return url, True, code, "OK"
    except Exception:
        pass

    # Fallback to GET
    try:
        req.get_method = lambda: "GET"
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as response:
            code = response.getcode()
            if code < 400:
                return url, True, code, "OK"
            return url, False, code, f"HTTP Error {code}"
    except urllib.error.HTTPError as e:
        if e.code in [401, 403]:
            return url, True, e.code, f"Bot protection / Auth ({e.code}) - considered reachable"
        return url, False, e.code, f"HTTP Error {e.code}"
    except urllib.error.URLError as e:
        return url, False, 0, f"URL Error: {e.reason}"
    except Exception as e:
        return url, False, 0, f"Exception: {str(e)}"

def validate_topic_entry(topic_entry: Any, path_prefix: str) -> Tuple[List[str], List[Dict[str, Any]]]:
    errors = []
    citations = []

    if not isinstance(topic_entry, dict):
        return [f"{path_prefix} must be an object"], citations

    scores = topic_entry.get("scores")
    notes = topic_entry.get("notes")
    cits = topic_entry.get("citations", [])

    if not isinstance(scores, dict):
        errors.append(f"{path_prefix} missing or invalid 'scores' (must be dict)")
    else:
        for crit in VALID_CRITERIA:
            if crit not in scores:
                errors.append(f"{path_prefix}.scores missing '{crit}'")
            else:
                s = scores[crit]
                if not isinstance(s, (int, float)):
                    errors.append(f"{path_prefix}.scores.{crit} must be a number")
                elif s < -100.0 or s > 100.0:
                    errors.append(f"{path_prefix}.scores.{crit} ({s}) out of range [-100, 100]")

    if not isinstance(notes, dict):
        errors.append(f"{path_prefix} missing or invalid 'notes' (must be dict)")
    else:
        for crit in VALID_CRITERIA:
            if crit not in notes or not isinstance(notes[crit], str) or not notes[crit].strip():
                errors.append(f"{path_prefix}.notes missing non-empty string for '{crit}'")

    if not isinstance(cits, list):
        errors.append(f"{path_prefix} missing or invalid 'citations' (must be list)")
    else:
        for idx, cit in enumerate(cits):
            if not isinstance(cit, dict):
                errors.append(f"{path_prefix}.citations[{idx}] must be an object")
                continue
            if not cit.get("title"):
                errors.append(f"{path_prefix}.citations[{idx}] missing 'title'")
            if not cit.get("url"):
                errors.append(f"{path_prefix}.citations[{idx}] missing 'url'")
            else:
                citations.append(cit)

    return errors, citations

def extract_citations_from_data(data: Any, topic_id: str = "") -> Tuple[List[str], List[Tuple[str, str, Dict[str, Any]]]]:
    schema_errors = []
    citations_list = []

    if not isinstance(data, dict) or "parties" not in data:
        return ["Root object must contain 'parties' key"], []

    parties_data = data["parties"]
    if not isinstance(parties_data, dict):
        return ["'parties' must be an object"], []

    for party_id, p_val in parties_data.items():
        if not isinstance(p_val, dict):
            schema_errors.append(f"party '{party_id}' must be an object")
            continue

        if "topics" in p_val:
            # Full evaluation format: party -> topics -> topic_id -> {scores, notes, citations}
            for t_id, t_entry in p_val["topics"].items():
                errs, cits = validate_topic_entry(t_entry, f"{party_id}.topics.{t_id}")
                schema_errors.extend(errs)
                for cit in cits:
                    citations_list.append((party_id, t_id, cit))
        else:
            # Topic staging format: party -> {scores, notes, citations}
            t_id = data.get("topic_id", topic_id) or "topic"
            errs, cits = validate_topic_entry(p_val, f"{party_id} ({t_id})")
            schema_errors.extend(errs)
            for cit in cits:
                citations_list.append((party_id, t_id, cit))

    return schema_errors, citations_list

def validate_file(filepath: str, check_http: bool = True, max_workers: int = 8) -> Dict[str, Any]:
    result = {
        "file": filepath,
        "valid": True,
        "schema_errors": [],
        "broken_urls": [],
        "verified_urls": [],
        "total_citations": 0
    }

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        result["valid"] = False
        result["schema_errors"].append(f"JSON load error: {str(e)}")
        return result

    topic_id_guess = os.path.basename(filepath).replace(".json", "")
    schema_errors, citations = extract_citations_from_data(data, topic_id=topic_id_guess)
    result["schema_errors"] = schema_errors
    result["total_citations"] = len(citations)

    if schema_errors:
        result["valid"] = False

    if not check_http or not citations:
        return result

    unique_urls = list({cit["url"] for _, _, cit in citations if "url" in cit and cit["url"]})
    print(f"[*] Checking {len(unique_urls)} unique URLs across {len(citations)} citations in {os.path.basename(filepath)}...")

    url_status = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_url, u): u for u in unique_urls}
        for future in as_completed(futures):
            url, ok, code, reason = future.result()
            url_status[url] = {"ok": ok, "code": code, "reason": reason}

    for party_id, location, cit in citations:
        url = cit.get("url")
        stat = url_status.get(url, {"ok": False, "code": 0, "reason": "Not checked"})
        if not stat["ok"]:
            result["valid"] = False
            result["broken_urls"].append({
                "party": party_id,
                "location": location,
                "title": cit.get("title", ""),
                "url": url,
                "code": stat["code"],
                "reason": stat["reason"]
            })
        else:
            result["verified_urls"].append(url)

    return result

def main():
    parser = argparse.ArgumentParser(description="Validate citation links and schema for election analysis data")
    parser.add_argument("target", help="Path to JSON file or directory of topic JSON files")
    parser.add_argument("--skip-http", action="store_true", help="Skip HTTP network connectivity checks")
    parser.add_argument("--workers", type=int, default=8, help="Max concurrent HTTP request threads")
    parser.add_argument("--report", help="Optional path to write validation report JSON")
    parser.add_argument("--strict", action="store_true", help="Exit with code 1 on any schema or URL errors")
    args = parser.parse_args()

    target = args.target
    files_to_check = []

    if os.path.isdir(target):
        for root, _, files in os.walk(target):
            for file in sorted(files):
                if file.endswith(".json") and not file.endswith("_report.json"):
                    files_to_check.append(os.path.join(root, file))
    elif os.path.isfile(target):
        files_to_check.append(target)
    else:
        print(f"[!] Error: Target path '{target}' does not exist.")
        sys.exit(1)

    all_results = []
    overall_valid = True

    for fpath in files_to_check:
        res = validate_file(fpath, check_http=not args.skip_http, max_workers=args.workers)
        all_results.append(res)
        if not res["valid"]:
            overall_valid = False

    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    for res in all_results:
        f_name = os.path.basename(res["file"])
        status = "PASSED ✓" if res["valid"] else "FAILED ✗"
        print(f"- {f_name:30} : {status} (Schema Errors: {len(res['schema_errors'])}, Citations: {res['total_citations']}, Broken URLs: {len(res['broken_urls'])})")
        if res["schema_errors"]:
            for err in res["schema_errors"][:5]:
                print(f"    [Schema Error] {err}")
            if len(res["schema_errors"]) > 5:
                print(f"    ... and {len(res['schema_errors']) - 5} more schema errors")
        if res["broken_urls"]:
            for b in res["broken_urls"][:5]:
                print(f"    [Broken URL] {b['party']} ({b['location']}): {b['url']} -> {b['reason']}")
            if len(res["broken_urls"]) > 5:
                print(f"    ... and {len(res['broken_urls']) - 5} more broken URLs")

    if args.report:
        os.makedirs(os.path.dirname(os.path.abspath(args.report)), exist_ok=True)
        with open(args.report, "w", encoding="utf-8") as f:
            json.dump({"valid": overall_valid, "results": all_results}, f, ensure_ascii=False, indent=2)
        print(f"\n[*] Full report written to: {args.report}")

    if args.strict and not overall_valid:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
