#!/usr/bin/env python3
"""
Report Generator for Election Analysis System.
Generates:
1. reports/YYYY-MM-DD/report.md (Markdown)
2. docs/index.html (Responsive RTL HTML Dashboard for GitHub Pages)
"""

import os
import json
from typing import Dict, Any, List

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
    date_str = result.get("date", "2026-09-09")
    parties = result.get("parties", {})
    topics = result.get("topics", [])
    
    md = []
    md.append(f"# דו״ח אנליזה לבחירות לכנסת ה-26 | {date_str}\n")
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
    md.append("## 🔍 ניתוח מעמיק ומקורות לפי מפלגות\n")
    
    for p_id, p_data in parties.items():
        name = p_data.get("name_he", p_id)
        leader = p_data.get("leader", "")
        overall = p_data.get("overall_score", 0.0)
        sign = "+" if overall > 0 else ""
        
        md.append(f"### מפלגת {name} (ציון כולל: `{sign}{overall:.1f}`)\n")
        md.append(f"**ראש המפלגה**: {leader} | **מנדטים צפויים**: {p_data.get('poll_mandates', '-')}\n")
        
        for t in topics:
            t_id = t["id"]
            t_eval = p_data.get("topics", {}).get(t_id, {})
            score = t_eval.get("computed_score", 0.0)
            sign_t = "+" if score > 0 else ""
            
            md.append(f"#### 📌 {t['title']} (ציון נושא: `{sign_t}{score:.1f}`)")
            md.append(f"*עמדת היעד המבוקשת:* {t.get('desired_stance', '')}\n")
            
            scores_dict = t_eval.get("scores", {})
            notes_dict = t_eval.get("notes", {})
            
            md.append("| קריטריון | ציון | פירוט והנמקה |")
            md.append("| :--- | :---: | :--- |")
            for c_key, c_label in CRITERIA_NAMES_HE.items():
                c_score = scores_dict.get(c_key, 0.0)
                c_sign = "+" if c_score > 0 else ""
                note = notes_dict.get(c_key, "אין פירוט")
                md.append(f"| {c_label} | `{c_sign}{c_score:.1f}` | {note} |")
                
            citations = t_eval.get("citations", [])
            if citations:
                md.append("\n**מקורות וסימוכין (Citations):**")
                for cite in citations:
                    title = cite.get("title", "מקור")
                    url = cite.get("url", "#")
                    quote = cite.get("quote", "")
                    quote_str = f' - *"{quote}"*' if quote else ""
                    md.append(f"- [{title}]({url}){quote_str}")
            md.append("\n")
            
        md.append("---\n")
        
    return "\n".join(md)

def generate_html_dashboard(result: Dict[str, Any]) -> str:
    date_str = result.get("date", "2026-09-09")
    parties = result.get("parties", {})
    topics = result.get("topics", [])
    
    html = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>אנליזה לבחירות לכנסת ה-26 | {date_str}</title>
    <style>
        :root {{
            --bg-primary: #0f172a;
            --bg-card: #1e293b;
            --bg-card-hover: #334155;
            --border: #334155;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent: #38bdf8;
            --accent-hover: #0284c7;
            --pos-bg: #064e3b;
            --pos-text: #34d399;
            --mild-pos-bg: #065f46;
            --mild-pos-text: #a7f3d0;
            --neutral-bg: #374151;
            --neutral-text: #d1d5db;
            --mild-neg-bg: #7f1d1d;
            --mild-neg-text: #fca5a5;
            --neg-bg: #991b1b;
            --neg-text: #fecaca;
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
        }}
        
        body {{
            background-color: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            padding: 24px 16px;
        }}
        
        .container {{
            max-width: 1300px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            margin-bottom: 32px;
            padding-bottom: 24px;
            border-bottom: 1px solid var(--border);
        }}
        
        header h1 {{
            font-size: 2.2rem;
            color: var(--accent);
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
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.9rem;
            color: var(--accent);
            margin-top: 8px;
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
        
        .table-responsive {{
            overflow-x: auto;
            background: var(--bg-card);
            border-radius: 12px;
            border: 1px solid var(--border);
            margin-bottom: 32px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: right;
        }}
        
        th, td {{
            padding: 14px 18px;
            border-bottom: 1px solid var(--border);
        }}
        
        th {{
            background: #1e293b;
            color: var(--text-secondary);
            font-size: 0.95rem;
            font-weight: 600;
        }}
        
        tr:hover td {{
            background: rgba(255, 255, 255, 0.02);
        }}
        
        .card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 24px;
        }}
        
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            padding-bottom: 12px;
            margin-bottom: 16px;
        }}
        
        .card-header h3 {{
            font-size: 1.3rem;
            color: var(--text-primary);
        }}
        
        .topic-accordion {{
            background: rgba(15, 23, 42, 0.6);
            border-radius: 8px;
            margin-bottom: 12px;
            border: 1px solid var(--border);
            overflow: hidden;
        }}
        
        .topic-summary {{
            padding: 12px 16px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            user-select: none;
            font-weight: 600;
        }}
        
        .topic-summary:hover {{
            background: rgba(255, 255, 255, 0.03);
        }}
        
        .topic-details {{
            padding: 16px;
            border-top: 1px solid var(--border);
            background: rgba(0, 0, 0, 0.15);
        }}
        
        .criteria-table {{
            width: 100%;
            margin-top: 10px;
            font-size: 0.92rem;
        }}
        
        .criteria-table th, .criteria-table td {{
            padding: 8px 12px;
        }}
        
        .citation-link {{
            color: var(--accent);
            text-decoration: none;
            transition: color 0.2s;
        }}
        
        .citation-link:hover {{
            text-decoration: underline;
            color: var(--accent-hover);
        }}
        
        .footer {{
            text-align: center;
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-top: 48px;
            padding-top: 24px;
            border-top: 1px solid var(--border);
        }}
    </style>
</head>
<body>
<div class="container">
    <header>
        <h1>מערכת אנליזה: בחירות לכנסת ה-26</h1>
        <p>ניתוח התאמה של מפלגות ומועמדים לעמדות המשתמש על פני 6 קריטריוני מצע, מנהיגות וביצוע</p>
        <span class="date-badge">תאריך ניתוח עדכני: {date_str}</span>
    </header>

    <h2 class="section-title">🏆 לוח דירוג המפלגות (Leaderboard)</h2>
    <div class="table-responsive">
        <table>
            <thead>
                <tr>
                    <th style="width: 70px; text-align: center;">דירוג</th>
                    <th>מפלגה</th>
                    <th>ראש המפלגה</th>
                    <th style="text-align: center;">מנדטים בסקרים</th>
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

    <h2 class="section-title">📊 מטריצת ציונים לפי 9 הנושאים (-100 עד +100)</h2>
    <div class="table-responsive">
        <table>
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
"""

    for p_id, p_data in parties.items():
        name = p_data.get("name_he", p_id)
        leader = p_data.get("leader", "")
        overall = p_data.get("overall_score", 0.0)
        badge = get_score_badge_html(overall)
        mandates = p_data.get("poll_mandates", "-")
        
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
    <div class="footer">
        <p>מערכת אנליזה לבחירות לכנסת ה-26 | פותח כ-Antigravity Skill | תאריך עדכון: {date_str}</p>
    </div>
</div>
</body>
</html>
"""
    return html
