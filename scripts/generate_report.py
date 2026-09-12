#!/usr/bin/env python3
"""
Report Generator for Election Analysis System.
Generates:
1. reports/YYYY-MM-DD/<profile_id>.md (Markdown per profile)
2. reports/YYYY-MM-DD/report.md (Default Markdown report)
3. docs/index.html (Responsive RTL HTML Dashboard with interactive profile switcher & candidate static KB)
"""

import os
import json
from typing import Dict, Any, List, Union

CRITERIA_NAMES_HE = {
    "c1_platform": "מצע המפלגה (15%)",
    "c2_leader_statements": "אמירות וכתיבה של ראש המפלגה (15%)",
    "c3_leader_actions": "ניסיון ופעילות מעשית של ראש המפלגה (30%)",
    "c4_candidates_statements": "אמירות וכתיבה של מועמדים ריאליים (10%)",
    "c5_candidates_actions": "ניסיון ופעילות מעשית של מועמדים ריאליים (20%)",
    "c6_designated_executive": "מועמד ריאלי ייעודי לתפקיד ביצועי (20%)"
}

def get_score_color_class(score: float) -> str:
    if score >= 40:
        return "positive"
    elif score > 0:
        return "mild-positive"
    elif score == 0:
        return "neutral"
    elif score > -40:
        return "mild-negative"
    else:
        return "negative"

def get_score_badge_html(score: float) -> str:
    sign = "+" if score > 0 else ""
    css_class = get_score_color_class(score)
    return f'<span class="badge {css_class}">{sign}{score:.1f}</span>'

def generate_markdown_report(result: Dict[str, Any], delta_info: Dict[str, Any] = None) -> str:
    date_str = result.get("date", "2026-09-12")
    profile_name = result.get("profile_name", "ברירת מחדל")
    profile_desc = result.get("profile_description", "")
    parties = result.get("parties", {})
    topics = result.get("topics", [])
    
    md = []
    md.append(f"# דו״ח אנליזה לבחירות לכנסת ה-26 | {date_str}\n")
    md.append(f"**פרופיל עולם ערכים נבחר**: {profile_name}  \n")
    if profile_desc:
        md.append(f"*{profile_desc}*\n")
    md.append("> ניתוח מפלגות ומועמדים לפי עמדות מוגדרות מראש בששת קריטריוני איכות וביצוע.\n")
    
    md.append("## 🏆 לוח תוצאות ודירוג כללי (Leaderboard)\n")
    md.append("| דירוג | מפלגה | ראש המפלגה | מנדטים בסקרים | ציון התאמה כולל | נושא חזק ביותר | נושא חלש ביותר |")
    md.append("| :---: | :--- | :--- | :---: | :---: | :--- | :--- |")
    
    for p_id, p_data in parties.items():
        rank = p_data.get("rank", "-")
        name = p_data.get("name_he", p_id)
        leader = p_data.get("leader", "")
        mandates = p_data.get("poll_mandates", "-")
        overall = p_data.get("overall_score", 0.0)
        
        t_scores = p_data.get("topic_scores", {})
        if t_scores:
            best_t = max(t_scores.items(), key=lambda x: x[1])
            worst_t = min(t_scores.items(), key=lambda x: x[1])
            best_title = next((t["title"] for t in topics if t["id"] == best_t[0]), best_t[0])
            worst_title = next((t["title"] for t in topics if t["id"] == worst_t[0]), worst_t[0])
            best_str = f"{best_title} ({'+' if best_t[1]>0 else ''}{best_t[1]})"
            worst_str = f"{worst_title} ({'+' if worst_t[1]>0 else ''}{worst_t[1]})"
        else:
            best_str = "-"
            worst_str = "-"
            
        sign = "+" if overall > 0 else ""
        md.append(f"| **#{rank}** | **{name}** | {leader} | {mandates} | **`{sign}{overall:.1f}`** | {best_str} | {worst_str} |")
        
    md.append("\n---\n")
    md.append("## 📊 מטריצת ציונים לפי נושאים (-100 עד +100)\n")
    
    header = "| מפלגה |" + "|".join([f" {t['title']} " for t in topics]) + "|"
    sep = "| :--- |" + "|".join([" :---: " for _ in topics]) + "|"
    md.append(header)
    md.append(sep)
    
    for p_id, p_data in parties.items():
        name = p_data.get("name_he", p_id)
        row = f"| **{name}** |"
        for t in topics:
            score = p_data.get("topic_scores", {}).get(t["id"], 0.0)
            sign = "+" if score > 0 else ""
            row += f" `{sign}{score:.1f}` |"
        md.append(row)
        
    md.append("\n---\n")
    md.append("## 🔍 ניתוח מעמיק, מועמדים ומקורות לפי מפלגות\n")
    
    for p_id, p_data in parties.items():
        name = p_data.get("name_he", p_id)
        leader = p_data.get("leader", "")
        overall = p_data.get("overall_score", 0.0)
        sign = "+" if overall > 0 else ""
        
        md.append(f"### מפלגת {name} (ציון כולל: `{sign}{overall:.1f}`)\n")
        md.append(f"- **יו״ר / ראש המפלגה**: {leader}")
        md.append(f"- **מנדטים ממוצעים בסקרים**: {p_data.get('poll_mandates', '-')}")
        
        # Static candidates summary
        static_data = p_data.get("static_data", {})
        candidates = static_data.get("candidates", [])
        if candidates:
            realistic_cands = [c for c in candidates if c.get("is_realistic_zone")]
            md.append(f"- **נבחרת מועמדים ריאליים מאומתת**: {len(realistic_cands)} מועמדים בטווח הריאלי ({', '.join([c['name'] for c in realistic_cands[:6]])})")
        
        md.append("\n#### פירוט לפי נושאי מדיניות:\n")
        
        for t in topics:
            t_id = t["id"]
            t_title = t["title"]
            t_eval = p_data.get("topics", {}).get(t_id, {})
            score = t_eval.get("computed_score", 0.0)
            t_sign = "+" if score > 0 else ""
            
            md.append(f"##### 📌 {t_title} (ציון נושא: `{t_sign}{score:.1f}`)")
            
            notes = t_eval.get("notes", {})
            scores = t_eval.get("scores", {})
            
            for c_key, c_label in CRITERIA_NAMES_HE.items():
                c_score = scores.get(c_key, 0.0)
                c_sign = "+" if c_score > 0 else ""
                note = notes.get(c_key, "אין מידע")
                md.append(f"- **{c_label}** [`{c_sign}{c_score:.1f}`]: {note}")
                
            citations = t_eval.get("citations", [])
            if citations:
                md.append("- **מקורות ואסמכתאות:**")
                for cite in citations:
                    title = cite.get("title", "מקור")
                    url = cite.get("url", "")
                    quote = cite.get("quote", "")
                    quote_str = f' - *"{quote}"*' if quote else ""
                    md.append(f"  - [{title}]({url}){quote_str}")
            md.append("")
        md.append("\n---\n")
        
    return "\n".join(md)

def generate_html_dashboard(
    profiles_input: Union[Dict[str, Any], Dict[str, Dict[str, Any]]], 
    default_profile_id: str = "default"
) -> str:
    # Normalize input to dict of profiles
    if "parties" in profiles_input and "topics" in profiles_input:
        # Single profile passed
        profiles_dict = {default_profile_id: profiles_input}
    else:
        profiles_dict = profiles_input

    if not profiles_dict:
        raise ValueError("No profile results provided to generate_html_dashboard")

    # Select active profile
    if default_profile_id in profiles_dict:
        active_id = default_profile_id
    else:
        active_id = list(profiles_dict.keys())[0]

    active_result = profiles_dict[active_id]
    date_str = active_result.get("date", "2026-09-12")
    topics = active_result.get("topics", [])
    parties = active_result.get("parties", {})

    # Top 3 parties for initial cards
    sorted_parties = sorted(parties.items(), key=lambda x: x[1].get("overall_score", 0), reverse=True)
    top_3 = sorted_parties[:3]

    # JSON serialization for interactive client switcher
    clean_profiles_json = {}
    for p_key, p_val in profiles_dict.items():
        clean_profiles_json[p_key] = {
            "profile_id": p_key,
            "profile_name": p_val.get("profile_name", p_key),
            "profile_description": p_val.get("profile_description", ""),
            "topics": p_val.get("topics", []),
            "parties": p_val.get("parties", {})
        }
    profiles_json_str = json.dumps(clean_profiles_json, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>מדד התאמה לבחירות לכנסת ה-26 | ניתוח מפלגות ומועמדים</title>
    <style>
        :root {{
            --bg-page: #f8fafc;
            --bg-card: #ffffff;
            --text-primary: #0f172a;
            --text-secondary: #475569;
            --border: #e2e8f0;
            --accent: #2563eb;
            --accent-light: #dbeafe;
            --pos-bg: #dcfce7;
            --pos-text: #166534;
            --mild-pos-bg: #f0fdf4;
            --mild-pos-text: #15803d;
            --neutral-bg: #f1f5f9;
            --neutral-text: #475569;
            --mild-neg-bg: #fff1f2;
            --mild-neg-text: #be123c;
            --neg-bg: #ffe4e6;
            --neg-text: #9f1239;
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg-page);
            color: var(--text-primary);
            line-height: 1.6;
            padding: 24px 16px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            margin-bottom: 28px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border);
        }}
        
        header h1 {{
            font-size: 2.2rem;
            color: var(--text-primary);
            margin-bottom: 8px;
        }}
        
        header p {{
            color: var(--text-secondary);
            font-size: 1.1rem;
        }}
        
        .date-badge {{
            display: inline-block;
            background: var(--bg-card);
            border: 1px solid var(--border);
            padding: 4px 14px;
            border-radius: 9999px;
            font-size: 0.9rem;
            color: var(--accent);
            margin-top: 8px;
            font-weight: 600;
        }}

        /* Profile Selector */
        .profile-selector-box {{
            background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
            border: 2px solid var(--accent-light);
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 28px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        }}

        .profile-selector-row {{
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
        }}

        .profile-selector-row label {{
            font-weight: 700;
            font-size: 1.05rem;
            color: var(--text-primary);
        }}

        .profile-dropdown {{
            padding: 8px 14px;
            border-radius: 8px;
            border: 1px solid var(--accent);
            background: #ffffff;
            font-size: 1rem;
            font-weight: 600;
            color: var(--accent);
            cursor: pointer;
            outline: none;
        }}

        .profile-desc {{
            color: var(--text-secondary);
            font-size: 0.92rem;
        }}
        
        .section-title {{
            font-size: 1.5rem;
            margin: 32px 0 16px 0;
            border-right: 4px solid var(--accent);
            padding-right: 12px;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 0.95rem;
        }}
        .badge.positive {{ background-color: var(--pos-bg); color: var(--pos-text); }}
        .badge.mild-positive {{ background-color: var(--mild-pos-bg); color: var(--mild-pos-text); }}
        .badge.neutral {{ background-color: var(--neutral-bg); color: var(--neutral-text); }}
        .badge.mild-negative {{ background-color: var(--mild-neg-bg); color: var(--mild-neg-text); }}
        .badge.negative {{ background-color: var(--neg-bg); color: var(--neg-text); }}
        
        .leaderboard-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        
        .leaderboard-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            position: relative;
            transition: transform 0.2s, border-color 0.2s;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }}
        
        .leaderboard-card:hover {{
            transform: translateY(-2px);
            border-color: var(--accent);
        }}
        
        .card-rank {{
            position: absolute;
            top: 16px;
            left: 16px;
            font-size: 1.5rem;
            font-weight: 800;
            color: var(--accent);
        }}

        .table-responsive {{
            overflow-x: auto;
            background: var(--bg-card);
            border-radius: 12px;
            border: 1px solid var(--border);
            margin-bottom: 32px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: right;
        }}
        
        th, td {{
            padding: 12px 14px;
            border-bottom: 1px solid var(--border);
        }}
        
        th {{
            background-color: #f1f5f9;
            font-weight: 700;
            color: var(--text-primary);
        }}
        
        tr:last-child td {{
            border-bottom: none;
        }}
        
        tr:hover td {{
            background-color: #f8fafc;
        }}
        
        .card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }}
        
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            padding-bottom: 12px;
            margin-bottom: 16px;
            flex-wrap: wrap;
            gap: 8px;
        }}

        /* Candidates KB Section */
        .candidates-kb {{
            background: #f8fafc;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 14px;
            margin-bottom: 16px;
        }}

        .candidate-tag {{
            display: inline-block;
            background: #ffffff;
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 3px 8px;
            margin: 3px;
            font-size: 0.85rem;
        }}

        .candidate-tag.realistic {{
            border-color: #93c5fd;
            background: #eff6ff;
            color: #1d4ed8;
            font-weight: 600;
        }}
        
        .topic-accordion {{
            border: 1px solid var(--border);
            border-radius: 8px;
            margin-bottom: 10px;
            background: #ffffff;
        }}
        
        .topic-summary {{
            padding: 12px 16px;
            cursor: pointer;
            font-weight: 600;
            display: flex;
            justify-content: space-between;
            align-items: center;
            user-select: none;
            background-color: #fafafa;
        }}
        
        .topic-details {{
            padding: 16px;
            border-top: 1px solid var(--border);
        }}
        
        .criteria-table {{
            margin-top: 8px;
            font-size: 0.92rem;
        }}
        
        .citation-link {{
            color: var(--accent);
            text-decoration: none;
            font-weight: 500;
        }}
        .citation-link:hover {{
            text-decoration: underline;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 48px;
            padding-top: 24px;
            border-top: 1px solid var(--border);
            color: var(--text-secondary);
            font-size: 0.9rem;
        }}

        @media (max-width: 768px) {{
            body {{
                padding: 12px 8px;
            }}
            header h1 {{
                font-size: 1.6rem;
            }}
            .section-title {{
                font-size: 1.25rem;
            }}
            th, td {{
                padding: 10px 8px;
                font-size: 0.88rem;
            }}
            .card {{
                padding: 14px;
            }}
        }}
    </style>
</head>
<body>
<div class="container">
    <header>
        <h1>מדד התאמה לבחירות לכנסת ה-26</h1>
        <p>ניתוח מפלגות, מצעים, ראשי מפלגות ומועמדים ריאליים מול עמדות יעד אובייקטיביות</p>
        <span class="date-badge">תאריך עדכון אחרון: {date_str}</span>
    </header>

    <!-- Profile Selector Box -->
    <div class="profile-selector-box">
        <div class="profile-selector-row">
            <label for="profileSelect">🎯 בחר עולם ערכים / פרופיל בוחר:</label>
            <select id="profileSelect" onchange="switchProfile(this.value)" class="profile-dropdown">
"""
    for p_key, p_val in profiles_dict.items():
        selected = "selected" if p_key == active_id else ""
        p_name = p_val.get("profile_name", p_key)
        html += f'                <option value="{p_key}" {selected}>{p_name}</option>\n'

    html += f"""            </select>
        </div>
        <p id="profileDescription" class="profile-desc">{active_result.get("profile_description", "")}</p>
    </div>

    <!-- Top 3 Cards -->
    <h2 class="section-title">🥇 מובילי ההתאמה הכללית</h2>
    <div class="leaderboard-cards" id="leaderboardCards">
"""
    for p_id, p_data in top_3:
        rank = p_data.get("rank", "-")
        name = p_data.get("name_he", p_id)
        leader = p_data.get("leader", "")
        mandates = p_data.get("poll_mandates", "-")
        overall = p_data.get("overall_score", 0.0)
        badge = get_score_badge_html(overall)
        html += f"""
        <div class="leaderboard-card">
            <div class="card-rank">#{rank}</div>
            <h3 style="margin-bottom: 4px;">{name}</h3>
            <div style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 12px;">ראש המפלגה: {leader}</div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">
                <span>ציון התאמה כולל:</span>
                {badge}
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 6px; font-size: 0.88rem; color: var(--text-secondary);">
                <span>מנדטים בסקרים:</span>
                <strong>{mandates} מנדטים</strong>
            </div>
        </div>
"""

    html += """
    </div>

    <h2 class="section-title">🏆 לוח תוצאות ודירוג מלא</h2>
    <div class="table-responsive">
        <table id="overviewTable">
            <thead>
                <tr>
                    <th style="width: 8%; text-align: center;">דירוג</th>
                    <th>מפלגה</th>
                    <th>ראש המפלגה</th>
                    <th style="text-align: center;">מנדטים</th>
                    <th style="text-align: center;">ציון התאמה כולל</th>
                    <th>נושא חזק ביותר</th>
                    <th>נושא חלש ביותר</th>
                </tr>
            </thead>
            <tbody>
"""
    for p_id, p_data in parties.items():
        rank = p_data.get("rank", "-")
        name = p_data.get("name_he", p_id)
        leader = p_data.get("leader", "")
        mandates = p_data.get("poll_mandates", "-")
        overall = p_data.get("overall_score", 0.0)
        badge = get_score_badge_html(overall)
        
        t_scores = p_data.get("topic_scores", {})
        if t_scores:
            best_t = max(t_scores.items(), key=lambda x: x[1])
            worst_t = min(t_scores.items(), key=lambda x: x[1])
            best_title = next((t["title"] for t in topics if t["id"] == best_t[0]), best_t[0])
            worst_title = next((t["title"] for t in topics if t["id"] == worst_t[0]), worst_t[0])
            best_str = f"{best_title} ({'+' if best_t[1]>0 else ''}{best_t[1]})"
            worst_str = f"{worst_title} ({'+' if worst_t[1]>0 else ''}{worst_t[1]})"
        else:
            best_str = "-"
            worst_str = "-"
            
        html += f"""
                <tr>
                    <td style="text-align: center; font-weight: bold; font-size: 1.1rem; color: var(--accent);">#{rank}</td>
                    <td style="font-weight: bold; font-size: 1.05rem;">{name}</td>
                    <td>{leader}</td>
                    <td style="text-align: center;">{mandates}</td>
                    <td style="text-align: center;">{badge}</td>
                    <td style="color: var(--pos-text);">{best_str}</td>
                    <td style="color: var(--neg-text);">{worst_str}</td>
                </tr>
"""

    html += """
            </tbody>
        </table>
    </div>

    <h2 class="section-title">📊 מטריצת ציונים לפי נושאים (-100 עד +100)</h2>
    <div class="table-responsive">
        <table id="matrixTable">
            <thead>
                <tr>
                    <th>מפלגה</th>
"""
    for t in topics:
        html += f"                    <th style='text-align: center; font-size: 0.85rem;'>{t['title']}</th>\n"
        
    html += """
                </tr>
            </thead>
            <tbody>
"""
    for p_id, p_data in parties.items():
        name = p_data.get("name_he", p_id)
        html += f"""
                <tr>
                    <td style="font-weight: bold;">{name}</td>
"""
        for t in topics:
            score = p_data.get("topic_scores", {}).get(t["id"], 0.0)
            badge = get_score_badge_html(score)
            html += f"                    <td style='text-align: center;'>{badge}</td>\n"
        html += "                </tr>\n"
        
    html += """
            </tbody>
        </table>
    </div>

    <h2 class="section-title">🔍 ניתוח מעמיק, מועמדים ומקורות לפי מפלגה</h2>
    <div id="partiesContainer">
"""

    for p_id, p_data in parties.items():
        name = p_data.get("name_he", p_id)
        leader = p_data.get("leader", "")
        overall = p_data.get("overall_score", 0.0)
        badge = get_score_badge_html(overall)
        mandates = p_data.get("poll_mandates", "-")
        static_data = p_data.get("static_data", {})
        candidates = static_data.get("candidates", [])
        
        html += f"""
    <div class="card" id="party-{p_id}">
        <div class="card-header">
            <div>
                <h3>{name} <span style="font-size: 0.95rem; color: var(--text-secondary); font-weight: normal;">(ראש המפלגה: {leader} | {mandates} מנדטים בסקרים)</span></h3>
            </div>
            <div>
                {badge}
            </div>
        </div>
"""
        # Static candidates roster display
        if candidates:
            html += """
        <details class="candidates-accordion" style="margin-bottom: 16px; border: 1px solid var(--border); border-radius: 8px;">
            <summary class="topic-summary" style="background-color: #f1f5f9;">
                <span>👥 נבחרת המועמדים ורקע מעשי (נתונים סטטיים מאומתים)</span>
                <span style="font-size: 0.85rem; color: var(--text-secondary);">הצג מועמדים</span>
            </summary>
            <div class="topic-details">
                <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px;">
"""
            for c in candidates:
                pos = c.get("position", "-")
                c_name = c.get("name", "")
                is_real = c.get("is_realistic_zone", False)
                real_cls = "realistic" if is_real else ""
                real_badge = "★ " if is_real else ""
                html += f'                    <span class="candidate-tag {real_cls}" title="{c_name}">#{pos} {real_badge}{c_name}</span>\n'

            html += """
                </div>
                <div style="font-size: 0.88rem; color: var(--text-secondary);">
                    <em>★ מועמדים בטווח המנדטים הריאלי לפי סקרי הבחירות העדכניים.</em>
                </div>
            </div>
        </details>
"""

        for t in topics:
            t_id = t["id"]
            t_eval = p_data.get("topics", {}).get(t_id, {})
            score = t_eval.get("computed_score", 0.0)
            t_badge = get_score_badge_html(score)
            
            html += f"""
        <details class="topic-accordion">
            <summary class="topic-summary">
                <span>📌 {t['title']}</span>
                <span>{t_badge}</span>
            </summary>
            <div class="topic-details">
                <p style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 12px;"><strong>עמדת יעד:</strong> {t.get('desired_stance', '')}</p>
                <table class="criteria-table">
                    <thead>
                        <tr>
                            <th style="width: 28%;">קריטריון ניתוח</th>
                            <th style="width: 14%; text-align: center;">ציון (-100..+100)</th>
                            <th>הנמקה, עדויות ועשייה בפועל</th>
                        </tr>
                    </thead>
                    <tbody>
"""
            scores_dict = t_eval.get("scores", {})
            notes_dict = t_eval.get("notes", {})
            
            for c_key, c_label in CRITERIA_NAMES_HE.items():
                c_score = scores_dict.get(c_key, 0.0)
                c_badge = get_score_badge_html(c_score)
                note = notes_dict.get(c_key, "אין מידע")
                html += f"""
                        <tr>
                            <td style="font-weight: 600;">{c_label}</td>
                            <td style="text-align: center;">{c_badge}</td>
                            <td>{note}</td>
                        </tr>
"""
            html += """
                    </tbody>
                </table>
"""
            citations = t_eval.get("citations", [])
            if citations:
                html += '<div style="margin-top: 12px; font-size: 0.88rem;"><strong>מקורות וקישורים:</strong><ul style="margin-right: 20px; margin-top: 4px;">'
                for cite in citations:
                    title = cite.get("title", "מקור")
                    url = cite.get("url", "#")
                    quote = cite.get("quote", "")
                    quote_html = f' &mdash; <em>"{quote}"</em>' if quote else ""
                    html += f'<li><a href="{url}" target="_blank" rel="noopener noreferrer" class="citation-link">{title}</a>{quote_html}</li>'
                html += '</ul></div>'

            html += """
            </div>
        </details>
"""
        html += "    </div>\n"

    html += f"""
    </div>

    <div class="footer">
        <p>מערכת אנליזה לבחירות לכנסת ה-26 | פותח כ-Antigravity Multi-Agent Skill | תאריך עדכון: {date_str}</p>
    </div>
</div>

<!-- Embedded Profile Data for Dynamic Client-Side Switching -->
<script id="electionProfilesData" type="application/json">
{profiles_json_str}
</script>

<script>
const profilesData = JSON.parse(document.getElementById('electionProfilesData').textContent);

function getBadgeHtml(score) {{
    const sign = score > 0 ? "+" : "";
    let cls = "neutral";
    if (score >= 40) cls = "positive";
    else if (score > 0) cls = "mild-positive";
    else if (score > -40 && score < 0) cls = "mild-negative";
    else if (score <= -40) cls = "negative";
    return `<span class="badge ${{cls}}">${{sign}}${{Number(score).toFixed(1)}}</span>`;
}}

function switchProfile(profileId) {{
    const prof = profilesData[profileId];
    if (!prof) return;

    // 1. Update Description
    const descEl = document.getElementById('profileDescription');
    if (descEl) descEl.textContent = prof.profile_description || '';

    // 2. Sort Parties
    const partiesList = Object.entries(prof.parties).map(([id, p]) => ({{ id, ...p }}));
    partiesList.sort((a, b) => b.overall_score - a.overall_score);

    // 3. Update Top 3 Cards
    const cardsEl = document.getElementById('leaderboardCards');
    if (cardsEl) {{
        const top3 = partiesList.slice(0, 3);
        let cardsHtml = '';
        top3.forEach((p, idx) => {{
            cardsHtml += `
            <div class="leaderboard-card">
                <div class="card-rank">#${{idx + 1}}</div>
                <h3 style="margin-bottom: 4px;">${{p.name_he}}</h3>
                <div style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 12px;">ראש המפלגה: ${{p.leader}}</div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">
                    <span>ציון התאמה כולל:</span>
                    ${{getBadgeHtml(p.overall_score)}}
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 6px; font-size: 0.88rem; color: var(--text-secondary);">
                    <span>מנדטים בסקרים:</span>
                    <strong>${{p.poll_mandates}} מנדטים</strong>
                </div>
            </div>`;
        }});
        cardsEl.innerHTML = cardsHtml;
    }}

    // 4. Update Overview Table
    const tableBody = document.querySelector('#overviewTable tbody');
    if (tableBody) {{
        let rowsHtml = '';
        partiesList.forEach((p, idx) => {{
            const tScores = Object.entries(p.topic_scores || {{}});
            let bestStr = '-', worstStr = '-';
            if (tScores.length > 0) {{
                tScores.sort((a, b) => b[1] - a[1]);
                const best = tScores[0];
                const worst = tScores[tScores.length - 1];
                const bestTopic = prof.topics.find(t => t.id === best[0]);
                const worstTopic = prof.topics.find(t => t.id === worst[0]);
                bestStr = `${{bestTopic ? bestTopic.title : best[0]}} (${{best[1] > 0 ? '+' : ''}}${{best[1]}})`;
                worstStr = `${{worstTopic ? worstTopic.title : worst[0]}} (${{worst[1] > 0 ? '+' : ''}}${{worst[1]}})`;
            }}
            rowsHtml += `
            <tr>
                <td style="text-align: center; font-weight: bold; font-size: 1.1rem; color: var(--accent);">#${{idx + 1}}</td>
                <td style="font-weight: bold; font-size: 1.05rem;">${{p.name_he}}</td>
                <td>${{p.leader}}</td>
                <td style="text-align: center;">${{p.poll_mandates}}</td>
                <td style="text-align: center;">${{getBadgeHtml(p.overall_score)}}</td>
                <td style="color: var(--pos-text);">${{bestStr}}</td>
                <td style="color: var(--neg-text);">${{worstStr}}</td>
            </tr>`;
        }});
        tableBody.innerHTML = rowsHtml;
    }}
}}
</script>
</body>
</html>
"""
    return html
