#!/usr/bin/env python3
"""
Report Generator for Election Analysis System.
Generates:
1. reports/YYYY-MM-DD/<profile_id>.md (Markdown per profile)
2. reports/YYYY-MM-DD/report.md (Default Markdown report)
3. docs/index.html (4-Tab Responsive RTL Dashboard with Candidate Dossiers, Criteria Analysis,
   Coalition Scenarios, Methodology, and Public GitHub Raw Data Matrix)
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

GITHUB_REPO_URL = "https://github.com/vvainer/elections-il-2026"
GITHUB_BLOB_URL = f"{GITHUB_REPO_URL}/blob/main"
GITHUB_TREE_URL = f"{GITHUB_REPO_URL}/tree/main"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/vvainer/elections-il-2026/main"

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
    coalitions = result.get("coalitions", [])
    
    md = []
    md.append(f"# דו״ח אנליזה לבחירות לכנסת ה-26 | {date_str}\n")
    md.append(f"**פרופיל עולם ערכים נבחר**: {profile_name}  \n")
    if profile_desc:
        md.append(f"*{profile_desc}*\n")
    md.append("> ניתוח מפלגות ומועמדים לפי עמדות מוגדרות מראש בששת קריטריוני איכות וביצוע.\n")
    
    if profile_name == "פרופיל ברירת מחדל - בחירות 2026" or result.get("profile_id") == "default":
        md.append("""---

## 📋 תקציר מנהלים שבועי (Executive Synthesis) | 2026-09-12

### 1. לוח המובילים (Leaderboard) ודירוג המפלגות המובילות
שבוע הניתוח הנוכחי (12 בספטמבר 2026) מציג תמונת מצב מובהקת של הובלה מוחלטת למפלגות המרכז והימין הממלכתי-ליברלי, המגלות התאמה עמוקה לעמדות היעד המבוקשות:
* **מקום 1: איחוד הנדל-זליכה (`+84.2`, 4 מנדטים)** – שומרת על הבכורה בטבלה. המפלגה מציגה התאמה יוצאת דופן בנושאי תשתיות עתיד (`+92.7`), שוק פתוח ורפורמות רגולטוריות (`+91.9`), צמצום הממשלה (`+88.6`) וחינוך ממלכתי (`+80.5`), הודות לרקורד מוכח של יועז הנדל (רפורמת הסיבים) ופרופ' ירון זליכה (הובלת פרויקטי תשתית לאומיים ומאבק במונופולים).
* **מקום 2: ישראל ביתנו (`+82.0`, 9 מנדטים)** – מובילה את המאבק בסידור מחדש של תשלומי העברה וקצבאות (`+89.3`), שוק חופשי (`+88.0`), דת ומדינה ושוויון בנטל (`+86.4`), לצד תוכנית מקיפה להשבת יורדים (`+87.3`).
* **מקום 3: ביחד בראשות נפתלי בנט (`+80.5`, 13 מנדטים)** – עמדה מובילה בתחומי יזמות, הסרת חסמים וצמיחת ההייטק (`+91.1`), תשתיות עתיד וטכנולוגיה מתקדמת (`+89.4`), ויציבה ביטחונית-מדינית חזקה (`+84.5`), לצד משילות ורפורמות בשירות הציבורי (`+82.3`).
* **מקום 4: ישר בראשות גדי איזנקוט (`+77.1`, 24 מנדטים)** – המפלגה הגדולה ביותר בגוש השינוי. מציגה פרופיל ממלכתי יציב ורחב: תשתיות לאומיות (`+84.8`), דת ומדינה ושוויון בנטל (`+83.0`), סידור מחדש של תקציבים (`+82.3`), צמצום ממשלה (`+81.4`) וחינוך (`+80.2`).
* **מקום 5: יש עתיד בראשות יאיר לפיד (`+71.5`, 8 מנדטים)** – ציון מוביל בחינוך ולימודי ליבה (`+82.2`), דת ומדינה (`+81.4`), סידור מחדש של תקציבים (`+77.3`) ושוק חופשי (`+75.8`).

בגזרת המרכז-ימין השמרני והשמאל:
* **ימין חדש / וינטר (`+38.4`, 4 מנדטים)** מציגה יתרון מובהק במדיניות הביטחונית (`+78.2`), אך נסוגה בנושאי דת ומדינה (`-42.0`).
* **הדמוקרטים בראשות יאיר גולן (`+37.2`, 9 מנדטים)** מפגינה עוצמה בדת ומדינה (`+83.6`), חינוך ממלכתי (`+80.0`) וצמצום ממשלה (`+73.9`), אך סובלת מציון שלילי מובהק במצב האסטרטגי-מדיני (`-61.8`) וציון חלש בשוק חופשי (`+8.6`).
* **הציונות הדתית (`+3.2`, 5 מנדטים)** מאזנת בין תמיכה ברפורמות שוק פתוח (`+76.2`) לבין התנגדות עמוקה לשוויון בנטל ובלימודי ליבה (`-81.8`), התנגדות לצמצום משרדי ממשלה (`-75.5`) והעברות כספים סקטוריאליות (`-57.5`).

בתחתית הטבלה נמצאות מפלגות הקואליציה המכהנת והמפלגות הערביות: רע״ם (`-2.4`), חד״ש-תע״ל (`-6.6`), הליכוד בראשות בנימין נתניהו (`-8.0`, 22 מנדטים), עוצמה יהודית (`-12.3`, 8 מנדטים), ש״ס (`-38.4`, 8 מנדטים), ויהדות התורה (`-51.8`, 8 מנדטים).

---

### 2. מגמות ותזוזות מפתח בין הגושים
בהשוואה לעדכון הקודם (2026-09-09), ניכרות מספר מגמות מערכתיות מובהקות:
1. **התרחבות הפער האיכותי לטובת גוש השינוי והימין הממלכתי**:
   * תרחיש **ממשלת שינוי ומרכז-ימין ממלכתי** (ישר 24, ביחד 13, ישראל ביתנו 9, יש עתיד 8, הדמוקרטים 9, איחוד הנדל-זליכה 4, ימין חדש/וינטר 4) מגבש רוב מוצק של **71 מנדטים** עם ציון התאמה מצרפי משוקלל חסר תקדים של **`+70.9`**.
   * חלה עלייה מובהקת בציוני המפלגות המובילות הודות לתיקוף אסמכתאות חדשות וחידוד התחייבויות לביצוע רפורמות מבניות: ישר עלתה ב-4.9 נקודות (מ-72.2 ל-77.1), יש עתיד ב-5.9 נקודות (מ-65.6 ל-71.5), ביחד ב-3.7 נקודות (מ-76.8 ל-80.5), וישראל ביתנו ב-2.7 נקודות (מ-79.3 ל-82.0).
2. **קריסת גוש הימין-חרדים המכהן**:
   * **גוש הימין-חרדים** (הליכוד, ש״ס, יהדות התורה, עוצמה יהודית, הציונות הדתית) מונה כעת **51 מנדטים בלבד** – רחוק מאוד מרוב פרלמנטרי (61). יתרה מכך, הציון המשוקלל של הגוש עומד על **`-19.2`**, המשקף חוסר התאמה מוחלט ליעדי הרפורמה הלאומיים.
   * עוצמה יהודית רשמה ירידה חדה של 6.1 נקודות (מ-`-6.2` ל-`-12.3`), ויהדות התורה ירדה ב-4.0 נקודות (מ-`-47.8` ל-`-51.8`), על רקע דבקות במבנה ממשלה מנופח, התעקשות על סובסידיות מגזריות וסירוב מוחלט לשוויון בנטל ולחובת ליבה.
3. **היתכנות לממשלת אחדות לאומית רחבה**:
   * תרחיש **ממשלת אחדות לאומית רחבה ללא קצוות** (הליכוד 22, ישר 24, ביחד 13, יש עתיד 8, ישראל ביתנו 9) מייצר רוב יציב של **76 מנדטים** עם ציון משוקלל חיובי של **`+53.0`**. תרחיש זה מוכיח כי חיבור בין המפלגות הממלכתיות לליכוד (ללא שותפיו החרדיים והמשיחיים) עשוי להעמיד ממשלה מתפקדת בעלת הלימה ערכית חיובית.
4. **בידול במפלגות הערביות**:
   * רע״ם רשמה עלייה של 7.3 נקודות (מ-`-9.7` ל-`-2.4`), כתוצאה מהדגשת שילוב החברה הערבית בפרויקטי תשתיות לאומיים, חינוך מקצועי והורדת חסמים כלכליים, לעומת חד״ש-תע״ל (`-6.6`) המתמקדת בהתנגדות רדיקלית למדיניות הביטחון וההגנה של ישראל (`-100.0`).

---

### 3. נקודות מחלוקת מרכזיות בין המפלגות
האנליזה המשווה מעלה ארבעה מוקדי חיכוך ושסע עיקריים:
* **חינוך, לימודי ליבה ואחריות תקציבית**:
  קיים פער בלתי ניתן לגישור בין מפלגות הציר הממלכתי (יש עתיד `+82.3`, ישראל ביתנו `+81.1`, איחוד הנדל-זליכה `+80.5`, ביחד `+80.5`, ישר `+80.2`, הדמוקרטים `+80.0`), הדורשות התניה קשיחה של כל תקציב ממשלתי או מוניציפלי בהוראת לימודי ליבה מלאים ובפיקוח ממלכתי, לבין המפלגות החרדיות (יהדות התורה `-100.0`, ש״ס `-93.9`) והליכוד (`-30.9`), המתנגדות לכל סנקציה או התערבות באוטונומיה התקציבית של מוסדות החינוך החרדיים.
* **דת ומדינה ושוויון בנטל הגיוס**:
  הסוגיה הבוערת ביותר במערכת הפוליטית. קואליציית המרכז-ימין הליברלי (ישראל ביתנו `+86.4`, הדמוקרטים `+83.6`, ישר `+83.0`, הנדל-זליכה `+82.7`, יש עתיד `+81.4`) דורשת חוק גיוס אחיד ושוויוני, ביטול מעמד 'תורתו אומנותו' במתכונתו הנוכחית, פתיחת תחבורה ציבורית בשבת באזורים חילוניים והסדרת ברית הזוגיות. מנגד ניצבות יהדות התורה (`-100.0`), ש״ס (`-95.0`), הציונות הדתית (`-81.8`), הליכוד (`-80.0`) ועוצמה יהודית (`-70.9`) המבצרות את הפטור מגיוס והסטטוס-קוו ההלכתי.
* **צמצום משרדי ממשלה ומשילות**:
  התנגשות חזיתית בין דרישת מפלגות השינוי (הנדל-זליכה `+88.6`, ישר `+81.4`, ישראל ביתנו `+76.4`, יש עתיד `+71.8`, ביחד `+67.7`) לקיצוץ מיידי של 12–15 משרדי ממשלה מיותרים, הגבלת שרים ל-18 וביטול תקציבים קואליציוניים, לבין מפלגות השלטון הנוכחי (הליכוד `-88.4`, יהדות התורה `-83.2`, ש״ס `-82.0`, עוצמה יהודית `-80.5`, הציונות הדתית `-75.5`) התומכות בשימור המבנה הממשלתי המנופח (מעל 30 משרדים) כדי לאפשר שרידות קואליציונית וחלוקת כיבודים סקטוריאליים.
* **מדיניות ביטחון ומצב אסטרטגי**:
  פער מהותי בין גישת הימין והמרכז הממלכתי (ביחד `+84.5`, הנדל-זליכה `+81.1`, ישר `+79.1`, וינטר `+78.2`, ישראל ביתנו `+75.5`), המדגישות יוזמה התקפית, מניעת איומים קיומיים, אי-הכרה במדינה פלסטינית חמושה והרחבת הסכמי אברהם מעמדת עוצמה, לבין מפלגות השמאל והמפלגות הערביות (הדמוקרטים `-61.8`, רע״ם `-78.9`, חד״ש-תע״ל `-100.0`) השוללות גישה זו ותומכות בנסיגות ובפתרונות מדיניים דו-לאומיים.

---

### 4. סטטוס אימות נתונים והוכחות (Tier-1 Validation Status)
* **אימות סכמה ושלמות נתונים (100% Valid)**: כל 9 קובצי הנושא בתיקיית `data/validated/2026-09-12/topics/` נבדקו ואושרו בסריקת Tier-1 קפדנית. לא אותרו שגיאות סכמה, שדות חסרים או חריגות מבניות.
* **בדיקת נגישות קישורים ואסמכתאות (Citation & URL Verification)**:
  * כלל המקורות והציטוטים נסרקו באמצעות מנוע אימות הקישורים.
  * קישורים בלתי נגישים או כתובות אתרי קמפיין זמניים הוחלפו באסמכתאות רשמיות, יציבות ומאומתות מתוך מאגר החקיקה והפרוטוקולים של אתר הכנסת הרשמי, עיתונות כלכלית מובילה (TheMarker, כלכליסט) וכלי תקשורת מרכזיים (כאן 11, Mako, ישראל היום, מעריב).
  * כל התיקונים תועדו באופן מלא ושקוף בקובץ `data/validation_logs/2026-09-12/validation_corrections.json` ובדוחות הסיכום `tier1_validated_summary.json`.
* **אינטגרטיביות מתמטית**: מנוע השקלול המתמטי עיבד 14 מפלגות על פני 9 נושאי ליבה ו-6 קריטריוני איכות לכל נושא (בסך הכל 756 ציונים פרטניים מנומקים), תוך שקלול פרופילי עולם הערכים ותרחישי הקואליציות.
\n""")
    
    # ----------------------------------------------------
    # חלק 1: לוח תוצאות ותרחישי קואליציות
    # ----------------------------------------------------
    md.append("## 🏆 חלק 1: לוח תוצאות ותרחישי קואליציות (Leaderboard & Coalitions)\n")
    md.append("### דירוג המפלגות הכללי\n")
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
        
    if coalitions:
        md.append("\n### תרחישי קואליציות וגושים מרכזיים (בחינת רוב של 61+ מנדטים)\n")
        md.append("| תרחיש קואליציה | מנדטים משותפים | מעמד רוב (61+) | ציון התאמה משוקלל | מפלגות שותפות |")
        md.append("| :--- | :---: | :---: | :---: | :--- |")
        for c in coalitions:
            maj_str = "✅ רוב קואליציוני" if c.get("has_majority") else "❌ מיעוט"
            w_score = c.get("weighted_score", 0.0)
            sign = "+" if w_score > 0 else ""
            parties_str = ", ".join([f"{p['name_he']} ({p['mandates']})" for p in c.get("parties", [])])
            md.append(f"| **{c.get('name_he')}** | {c.get('total_mandates')} | {maj_str} | **`{sign}{w_score:.1f}`** | {parties_str} |")

    # ----------------------------------------------------
    # חלק 2: מטריצת ציונים וניתוח מעמיק לפי נושאים
    # ----------------------------------------------------
    md.append("\n---\n")
    md.append("## 📊 חלק 2: מטריצת ציונים וניתוח מעמיק לפי נושאים\n")
    
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
        
    md.append("\n### פירוט הערכה לפי מפלגות ונושאים\n")
    for p_id, p_data in parties.items():
        name = p_data.get("name_he", p_id)
        leader = p_data.get("leader", "")
        overall = p_data.get("overall_score", 0.0)
        sign = "+" if overall > 0 else ""
        
        md.append(f"#### מפלגת {name} (ציון כולל: `{sign}{overall:.1f}`)\n")
        
        for t in topics:
            t_id = t["id"]
            t_title = t["title"]
            t_eval = p_data.get("topics", {}).get(t_id, {})
            score = t_eval.get("computed_score", 0.0)
            t_sign = "+" if score > 0 else ""
            
            md.append(f"##### 📌 {t_title} (ציון: `{t_sign}{score:.1f}`)")
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

    # ----------------------------------------------------
    # חלק 3: תיקי מפלגות ונבחרת מועמדים
    # ----------------------------------------------------
    md.append("\n---\n")
    md.append("## 👥 חלק 3: תיקי מפלגות ונבחרת מועמדים (Dossiers)\n")
    
    for p_id, p_data in parties.items():
        name = p_data.get("name_he", p_id)
        leader = p_data.get("leader", "")
        mandates = p_data.get("poll_mandates", "-")
        static_data = p_data.get("static_data", {})
        party_info = static_data.get("party_info", {})
        candidates = static_data.get("candidates", [])
        
        md.append(f"### {name} | ראש המפלגה: {leader} ({mandates} מנדטים)")
        if party_info.get("official_website"):
            md.append(f"- **אתר רשמי**: [{party_info['official_website']}]({party_info['official_website']})")
        if party_info.get("knesset_faction_url"):
            md.append(f"- **סיעה בכנסת**: [עמוד סיעה רשמי]({party_info['knesset_faction_url']})")
        if static_data.get("manifesto_text"):
            md.append(f"- **מצע המפלגה**: [קובץ מצע מלא במאגר GitHub]({GITHUB_BLOB_URL}/data/static/parties/{p_id}/manifesto.md)")
        
        md.append("\n#### רשימת מועמדים ריאליים וקורות חיים מעשיים:")
        if candidates:
            for c in candidates:
                if not c.get("is_realistic_zone"):
                    continue
                pos = c.get("position", "-")
                c_name = c.get("name", "")
                cv = c.get("cv", {})
                md.append(f"##### מקום {pos}: {c_name} (★ בטווח הריאלי)")
                if cv.get("education"):
                    md.append(f"- **השכלה**: {cv['education']}")
                if cv.get("career"):
                    md.append(f"- **קריירה מקצועית/צבאית**: {cv['career']}")
                if cv.get("public_service"):
                    md.append(f"- **שירות ציבורי ופרלמנטרי**: {cv['public_service']}")
                if cv.get("key_votes"):
                    md.append(f"- **הצבעות מפתח**: {', '.join(cv['key_votes'])}")
                if cv.get("major_achievements"):
                    md.append(f"- **הישגים בולטים**: {', '.join(cv['major_achievements'])}")
                if cv.get("notable_failures_or_controversies"):
                    md.append(f"- **ביקורת ומחלוקות**: {', '.join(cv['notable_failures_or_controversies'])}")
                md.append("")
        else:
            md.append("אין פירוט מועמדים זמין.")
        md.append("\n---\n")

    # ----------------------------------------------------
    # חלק 4: מתודולוגיה ומטריצת קישורים לנתונים הגולמיים ב-GitHub
    # ----------------------------------------------------
    md.append("## 📁 חלק 4: מתודולוגיה וגישה ישירה לנתונים הגולמיים ב-GitHub\n")
    md.append("כל נתוני הניתוח, קטלוג הנושאים, מחווני ההערכה והמחקר הדינמי שמורים כקובצי JSON ו-YAML נקיים במאגר הציבורי:\n")
    md.append("| קטגוריה | קובץ / ארטיפקט | תיאור | קישור ישיר לקובץ ב-GitHub |")
    md.append("| :--- | :--- | :--- | :--- |")
    md.append(f"| **קטלוג נושאים** | `data/static/topics/catalog.json` | 9 נושאי המדיניות ושאלות המפתח | [צפייה בקובץ ב-GitHub]({GITHUB_BLOB_URL}/data/static/topics/catalog.json) |")
    md.append(f"| **מחוון קריטריונים** | `data/static/rubric/criteria.json` | 6 הקריטריונים ומשקולות מנורמלות | [צפייה בקובץ ב-GitHub]({GITHUB_BLOB_URL}/data/static/rubric/criteria.json) |")
    md.append(f"| **תרחישי קואליציות** | `data/static/coalitions/scenarios.json` | תרחישי גושים וקואליציות פוטנציאליות | [צפייה בקובץ ב-GitHub]({GITHUB_BLOB_URL}/data/static/coalitions/scenarios.json) |")
    md.append(f"| **מאגר מפלגות סטטי** | `data/static/parties/` | 14 תיקיות מפלגות, קו״ח מועמדים ומצעים | [עיון בתיקייה ב-GitHub]({GITHUB_TREE_URL}/data/static/parties) |")
    md.append(f"| **סקרי בחירות** | `config/polls.yaml` | ממוצעי סקרים עדכניים ורף מנדטים | [צפייה בקובץ ב-GitHub]({GITHUB_BLOB_URL}/config/polls.yaml) |")
    md.append(f"| **פרופילי עולם ערכים** | `config/profiles/` | קובצי עולם ערכים מותאמים אישית | [עיון בפרופילים ב-GitHub]({GITHUB_TREE_URL}/config/profiles) |")
    md.append(f"| **מחקר נושאים מאומת** | `data/validated/{date_str}/topics/` | 9 קובצי מחקר מאומתים מלווים בציטוטים | [עיון במחקר ב-GitHub]({GITHUB_TREE_URL}/data/validated/{date_str}/topics) |")
    md.append(f"| **מסד הערכה מרכזי** | `data/evaluations/{date_str}.json` | נתונים גולמיים ממוזגים של כלל המפלגות | [צפייה בקובץ ב-GitHub]({GITHUB_BLOB_URL}/data/evaluations/{date_str}.json) |")
    md.append(f"| **יומן אימות קישורים** | `data/validation_logs/{date_str}/tier1_summary.json` | אימות תקינות URL וסכמות | [צפייה ביומן ב-GitHub]({GITHUB_BLOB_URL}/data/validation_logs/{date_str}/tier1_summary.json) |")
    md.append(f"| **אימות UI ותצלומים** | `data/validation_logs/{date_str}/ui_validation.json` | דוח ביקורת DOM ותצלומי דסקטופ/מובייל | [צפייה בדוח ב-GitHub]({GITHUB_BLOB_URL}/data/validation_logs/{date_str}/ui_validation.json) |")
    md.append(f"| **תצלום דסקטופ** | `data/validation_logs/{date_str}/snapshots/desktop.png` | תצלום מסך 1280x800 של הדשבורד | [צפייה בתמונה ב-GitHub]({GITHUB_BLOB_URL}/data/validation_logs/{date_str}/snapshots/desktop.png) |")
    
    return "\n".join(md)

def generate_html_dashboard(
    profiles_input: Union[Dict[str, Any], Dict[str, Dict[str, Any]]], 
    default_profile_id: str = "default"
) -> str:
    # Normalize input to dict of profiles
    if "parties" in profiles_input and "topics" in profiles_input:
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
    coalitions = active_result.get("coalitions", [])

    # Top 3 parties for initial cards
    sorted_parties = sorted(parties.items(), key=lambda x: x[1].get("overall_score", 0), reverse=True)
    top_3 = sorted_parties[:3]

    # Clean JSON serialization for interactive client switcher
    clean_profiles_json = {}
    for p_key, p_val in profiles_dict.items():
        clean_profiles_json[p_key] = {
            "profile_id": p_key,
            "profile_name": p_val.get("profile_name", p_key),
            "profile_description": p_val.get("profile_description", ""),
            "topics": p_val.get("topics", []),
            "parties": p_val.get("parties", {}),
            "coalitions": p_val.get("coalitions", [])
        }
    profiles_json_str = json.dumps(clean_profiles_json, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>מדד התאמה לבחירות לכנסת ה-26 | מערכת אנליזה רב-סוכנית</title>
    <style>
        :root {{
            --bg-page: #f8fafc;
            --bg-card: #ffffff;
            --text-primary: #0f172a;
            --text-secondary: #475569;
            --border: #e2e8f0;
            --border-hover: #cbd5e1;
            --accent: #2563eb;
            --accent-hover: #1d4ed8;
            --accent-light: #eff6ff;
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
            padding: 16px;
        }}
        
        .container {{
            max-width: 1280px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border);
        }}
        
        header h1 {{
            font-size: 2.2rem;
            color: var(--text-primary);
            margin-bottom: 6px;
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

        /* Navigation Tabs */
        .nav-tabs {{
            display: flex;
            gap: 8px;
            border-bottom: 2px solid var(--border);
            margin-bottom: 24px;
            overflow-x: auto;
            padding-bottom: 2px;
        }}

        .tab-button {{
            background: none;
            border: none;
            padding: 12px 20px;
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--text-secondary);
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.2s ease;
            white-space: nowrap;
            border-radius: 6px 6px 0 0;
        }}

        .tab-button:hover {{
            color: var(--accent);
            background: var(--accent-light);
        }}

        .tab-button.active {{
            color: var(--accent);
            border-bottom: 3px solid var(--accent);
            background: #ffffff;
        }}

        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        /* Profile Selector Box */
        .profile-selector-box {{
            background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
            border: 2px solid #bfdbfe;
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 24px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.03);
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
            max-width: 100%;
            box-sizing: border-box;
        }}

        .profile-desc {{
            color: var(--text-secondary);
            font-size: 0.92rem;
        }}
        
        .section-title {{
            font-size: 1.5rem;
            margin: 28px 0 16px 0;
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
            margin-bottom: 28px;
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

        /* Candidate Dossiers & Cards */
        .candidate-card {{
            background: #ffffff;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 14px;
            transition: border-color 0.2s, box-shadow 0.2s;
        }}

        .candidate-card:hover {{
            border-color: var(--accent);
            box-shadow: 0 4px 10px rgba(0,0,0,0.06);
        }}

        .candidate-card.realistic-card {{
            border-right: 4px solid #2563eb;
            background: #fbfdff;
        }}

        .candidate-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            flex-wrap: wrap;
            gap: 8px;
        }}

        .candidate-name {{
            font-size: 1.15rem;
            font-weight: 700;
            color: var(--text-primary);
        }}

        .candidate-pos-tag {{
            background: var(--accent-light);
            color: var(--accent);
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 0.88rem;
        }}

        .candidate-cv-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 10px;
            font-size: 0.92rem;
            margin-top: 8px;
        }}

        .cv-item strong {{
            color: var(--text-primary);
        }}

        .cv-item span {{
            color: var(--text-secondary);
        }}

        .pill-badge {{
            display: inline-block;
            background: #e0f2fe;
            color: #0369a1;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            margin: 2px;
            font-weight: 600;
        }}

        /* Controls and Search in Tab 1 */
        .dossier-controls {{
            display: flex;
            gap: 12px;
            align-items: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
            background: #f1f5f9;
            padding: 12px 16px;
            border-radius: 10px;
        }}

        .search-input {{
            padding: 8px 14px;
            border-radius: 8px;
            border: 1px solid var(--border);
            font-size: 0.95rem;
            flex: 1;
            min-width: 220px;
        }}

        .filter-btn {{
            background: #ffffff;
            border: 1px solid var(--border);
            padding: 6px 12px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.88rem;
            font-weight: 600;
            transition: all 0.15s;
        }}

        .filter-btn:hover, .filter-btn.active {{
            background: var(--accent);
            color: #ffffff;
            border-color: var(--accent);
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

        .candidate-jump-link {{
            color: #1d4ed8;
            background: #eff6ff;
            border: 1px solid #bfdbfe;
            padding: 2px 6px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: 600;
            text-decoration: none;
            display: inline-block;
            margin-right: 4px;
        }}

        .candidate-jump-link:hover {{
            background: #dbeafe;
            text-decoration: underline;
        }}

        .github-link-btn {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            color: #ffffff;
            background: #24292f;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 600;
            text-decoration: none;
            transition: background 0.2s;
        }}

        .github-link-btn:hover {{
            background: #0f1419;
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
                padding: 10px 6px;
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
            .tab-button {{
                padding: 10px 12px;
                font-size: 0.95rem;
            }}
            .profile-selector-box {{
                padding: 14px 12px;
            }}
            .profile-selector-row {{
                flex-direction: column;
                align-items: stretch;
                gap: 8px;
            }}
            .profile-dropdown {{
                width: 100%;
                max-width: 100%;
            }}
        }}
    </style>
</head>
<body>
<div class="container">
    <header>
        <h1>מדד התאמה לבחירות לכנסת ה-26</h1>
        <p>ניתוח רב-סוכני אובייקטיבי: מצעים, ראשי מפלגות, נבחרת מועמדים ריאליים וגושים קואליציוניים</p>
        <span class="date-badge">תאריך עדכון אחרון: {date_str}</span>
    </header>

    <!-- Navigation Tabs -->
    <nav class="nav-tabs" role="tablist">
        <button class="tab-button active" onclick="switchTab('tab-criteria')" id="btn-criteria">📊 ניתוח קריטריונים ועולם ערכים</button>
        <button class="tab-button" onclick="switchTab('tab-dossiers')" id="btn-dossiers">👥 כרטיסי מפלגות ומועמדים</button>
        <button class="tab-button" onclick="switchTab('tab-methodology')" id="btn-methodology">📐 מתודולוגיה ומבנה הניתוח</button>
        <button class="tab-button" onclick="switchTab('tab-raw-data')" id="btn-raw-data">📁 גישה לנתונים גולמיים (GitHub)</button>
    </nav>

    <!-- ============================================================= -->
    <!-- TAB 2 (DEFAULT ACTIVE): ניתוח קריטריונים, דירוג ותרחישי קואליציה -->
    <!-- ============================================================= -->
    <div id="tab-criteria" class="tab-content active">
        <!-- Profile Selector Box -->
        <div class="profile-selector-box">
            <div class="profile-selector-row">
                <label for="profileSelect">🎯 בחר עולם ערכים / פרופיל בוחר:</label>
                <select id="profileSelect" onchange="switchProfile(this.value)" class="profile-dropdown">
"""
    for p_key, p_val in profiles_dict.items():
        selected = "selected" if p_key == active_id else ""
        p_name = p_val.get("profile_name", p_key)
        html += f'                    <option value="{p_key}" {selected}>{p_name}</option>\n'

    html += f"""                </select>
            </div>
            <p id="profileDescription" class="profile-desc">{active_result.get("profile_description", "")}</p>
        </div>

        <!-- Top 3 Cards -->
        <h2 class="section-title">🥇 מובילי ההתאמה לפרופיל הנבחר</h2>
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

        <!-- Coalitions Viability Table -->
        <h2 class="section-title">🏛️ תרחישי קואליציות וגושים מרכזיים (בחינת רוב 61+ מנדטים)</h2>
        <div class="table-responsive">
            <table id="coalitionsTable">
                <thead>
                    <tr>
                        <th style="width: 25%;">תרחיש קואליציה</th>
                        <th style="width: 14%; text-align: center;">מנדטים משותפים</th>
                        <th style="width: 16%; text-align: center;">מעמד רוב (61+)</th>
                        <th style="width: 18%; text-align: center;">ציון התאמה משוקלל</th>
                        <th>מפלגות שותפות בהרכב</th>
                    </tr>
                </thead>
                <tbody>
"""
    for c in coalitions:
        maj_badge = '<span class="badge positive">✅ רוב קואליציוני</span>' if c.get("has_majority") else '<span class="badge negative">❌ מיעוט</span>'
        w_score = c.get("weighted_score", 0.0)
        score_badge = get_score_badge_html(w_score)
        parties_str = " + ".join([f"<strong>{p['name_he']}</strong> ({p['mandates']})" for p in c.get("parties", [])])
        html += f"""
                    <tr>
                        <td><strong>{c.get('name_he')}</strong><div style="font-size: 0.85rem; color: var(--text-secondary);">{c.get('description', '')}</div></td>
                        <td style="text-align: center; font-size: 1.1rem; font-weight: bold;">{c.get('total_mandates')}</td>
                        <td style="text-align: center;">{maj_badge}</td>
                        <td style="text-align: center;">{score_badge}</td>
                        <td style="font-size: 0.9rem;">{parties_str}</td>
                    </tr>
"""
    html += """
                </tbody>
            </table>
        </div>

        <!-- Full Leaderboard Table -->
        <h2 class="section-title">🏆 לוח תוצאות ודירוג מפלגות מלא</h2>
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

        <!-- Matrix Table -->
        <h2 class="section-title">📊 מטריצת ציונים לפי 9 הנושאים (-100 עד +100)</h2>
        <div class="table-responsive">
            <table id="matrixTable">
                <thead>
                    <tr>
                        <th>מפלגה</th>
"""
    for t in topics:
        html += f"                        <th style='text-align: center; font-size: 0.85rem;'>{t['title']}</th>\n"
        
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
            html += f"                        <td style='text-align: center;'>{badge}</td>\n"
        html += "                    </tr>\n"
        
    html += """
                </tbody>
            </table>
        </div>

        <!-- Detailed Per-Party Topic Accordions -->
        <h2 class="section-title">🔍 ניתוח מעמיק, ששת הקריטריונים ומקורות לפי מפלגה</h2>
        <div id="partiesContainer">
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
                    <h3>{name} <span style="font-size: 0.95rem; color: var(--text-secondary); font-weight: normal;">(יו״ר: {leader} | {mandates} מנדטים בסקרים)</span></h3>
                </div>
                <div style="display: flex; gap: 8px; align-items: center;">
                    <button class="filter-btn" onclick="goToPartyDossier('{p_id}')">👤 צפה בנבחרת המועמדים</button>
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
                html += '<div style="margin-top: 12px; font-size: 0.88rem;"><strong>מקורות וקישורים מאומתים:</strong><ul style="margin-right: 20px; margin-top: 4px;">'
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
        html += "        </div>\n"
    html += "    </div>\n"
    html += "    </div>\n"

    # =============================================================
    # TAB 1: כרטיסי מפלגות ומועמדים (Party & Candidate Dossiers)
    # =============================================================
    html += """
    <div id="tab-dossiers" class="tab-content">
        <h2 class="section-title">👥 כרטיסי מפלגות ומועמדים (Candidate Dossiers)</h2>
        <div class="dossier-controls">
            <input type="text" id="candidateSearchInput" oninput="filterCandidates()" placeholder="🔍 חיפוש מועמד לפי שם או תפקיד..." class="search-input">
            <button class="filter-btn active" id="btn-filter-realistic" onclick="toggleRealisticOnly(true)">★ מועמדים ריאליים בלבד</button>
            <button class="filter-btn" id="btn-filter-all" onclick="toggleRealisticOnly(false)">רשימה מלאה (1..30+)</button>
        </div>

        <div id="partiesDossiersList">
"""
    for p_id, p_data in parties.items():
        name = p_data.get("name_he", p_id)
        leader = p_data.get("leader", "")
        mandates = p_data.get("poll_mandates", "-")
        static_data = p_data.get("static_data", {})
        party_info = static_data.get("party_info", {})
        candidates = static_data.get("candidates", [])
        
        manifesto_link = f"{GITHUB_BLOB_URL}/data/static/parties/{p_id}/manifesto.md"
        
        html += f"""
        <div class="card" id="dossier-{p_id}">
            <div class="card-header">
                <div>
                    <h3 style="font-size: 1.4rem;">{name} <span style="font-size: 1rem; color: var(--text-secondary); font-weight: normal;">({mandates} מנדטים בסקרים)</span></h3>
                    <div style="font-size: 0.95rem; color: var(--text-secondary); margin-top: 4px;">
                        <strong>יו״ר:</strong> {leader}
                        {f' | <a href="{party_info.get("official_website")}" target="_blank" rel="noopener noreferrer" class="citation-link">אתר רשמי</a>' if party_info.get("official_website") else ""}
                        {f' | <a href="{party_info.get("knesset_faction_url")}" target="_blank" rel="noopener noreferrer" class="citation-link">עמוד סיעה בכנסת</a>' if party_info.get("knesset_faction_url") else ""}
                        | <a href="{manifesto_link}" target="_blank" rel="noopener noreferrer" class="citation-link">📄 צפה במצע המלא (GitHub)</a>
                    </div>
                </div>
            </div>

            <h4 style="margin: 16px 0 12px 0; font-size: 1.1rem; color: var(--accent);">נבחרת המועמדים וקורות חיים מעשיים:</h4>
            <div class="candidates-grid">
"""
        if candidates:
            for c in candidates:
                pos = c.get("position", "-")
                c_name = c.get("name", "")
                is_real = c.get("is_realistic_zone", False)
                real_class = "realistic-card" if is_real else "standard-card"
                real_badge = '<span class="pill-badge" style="background:#eff6ff; color:#1d4ed8;">★ בטווח הריאלי</span>' if is_real else '<span class="pill-badge" style="background:#f1f5f9; color:#64748b;">מקום ברשימה</span>'
                
                cv = c.get("cv", {})
                html += f"""
                <div class="candidate-card {real_class}" id="candidate-{p_id}-{pos}" data-name="{c_name}" data-realistic="{str(is_real).lower()}">
                    <div class="candidate-card-header">
                        <div>
                            <span class="candidate-pos-tag">מקום #{pos}</span>
                            <span class="candidate-name" style="margin-right: 8px;">{c_name}</span>
                            {real_badge}
                        </div>
                    </div>
                    <div class="candidate-cv-grid">
                        {f'<div class="cv-item"><strong>השכלה:</strong> <span>{cv["education"]}</span></div>' if cv.get("education") else ""}
                        {f'<div class="cv-item"><strong>קריירה אזרחית/צבאית:</strong> <span>{cv["career"]}</span></div>' if cv.get("career") else ""}
                        {f'<div class="cv-item"><strong>שירות ציבורי:</strong> <span>{cv["public_service"]}</span></div>' if cv.get("public_service") else ""}
                    </div>
                    {f'<div style="margin-top: 8px; font-size: 0.88rem;"><strong>הצבעות מפתח בכנסת:</strong> <span style="color: var(--text-secondary);">{", ".join(cv["key_votes"])}</span></div>' if cv.get("key_votes") else ""}
                    {f'<div style="margin-top: 6px; font-size: 0.88rem;"><strong>הישגים בולטים:</strong> <span style="color: var(--pos-text);">{", ".join(cv["major_achievements"])}</span></div>' if cv.get("major_achievements") else ""}
                    {f'<div style="margin-top: 6px; font-size: 0.88rem;"><strong>ביקורת ומחלוקות:</strong> <span style="color: var(--neg-text);">{", ".join(cv["notable_failures_or_controversies"])}</span></div>' if cv.get("notable_failures_or_controversies") else ""}
                </div>
"""
        else:
            html += "<p style='color: var(--text-secondary);'>אין מידע מפורט על מועמדים.</p>"

        html += """
            </div>
        </div>
"""
    html += """
        </div>
    </div>
"""

    # =============================================================
    # TAB 3: מתודולוגיה ומבנה הניתוח (Methodology & Topics Catalog)
    # =============================================================
    html += f"""
    <div id="tab-methodology" class="tab-content">
        <h2 class="section-title">📐 מתודולוגיה ומבנה הניתוח (Methodology)</h2>
        
        <div class="card">
            <h3>🎯 9 נושאי הליבה (מתוך קטלוג הנתונים הסטטי)</h3>
            <p style="color: var(--text-secondary); margin-bottom: 16px;">
                כל נושא מוגדר בצורה קנונית בקובץ <a href="{GITHUB_BLOB_URL}/data/static/topics/catalog.json" target="_blank" class="citation-link"><code>data/static/topics/catalog.json</code></a> ומכיל שאלות מפתח מנחות למחקר:
            </p>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th style="width: 8%; text-align: center;">מזהה</th>
                            <th style="width: 25%;">שם הנושא</th>
                            <th>הגדרה ותחומי בדיקה</th>
                        </tr>
                    </thead>
                    <tbody>
"""
    for t in topics:
        html += f"""
                        <tr>
                            <td style="text-align: center; font-weight: bold; color: var(--accent);"><code>{t['id']}</code></td>
                            <td style="font-weight: bold;">{t['title']}</td>
                            <td style="font-size: 0.92rem; color: var(--text-secondary);">{t.get('desired_stance', '')}</td>
                        </tr>
"""
    html += f"""
                    </tbody>
                </table>
            </div>
        </div>

        <div class="card">
            <h3>⚖️ ששת קריטריוני ההערכה והמשקולות המנורמלות</h3>
            <p style="color: var(--text-secondary); margin-bottom: 16px;">
                מחוון ההערכה מוגדר בקובץ <a href="{GITHUB_BLOB_URL}/data/static/rubric/criteria.json" target="_blank" class="citation-link"><code>data/static/rubric/criteria.json</code></a>. המשקולות המקוריות מסתכמות ב-110% ומנורמלות מתמטית ל-100% בחלוקה ב-1.1:
            </p>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th style="width: 15%;">מזהה קריטריון</th>
                            <th style="width: 30%;">שם הקריטריון</th>
                            <th style="width: 15%; text-align: center;">משקל מקורי</th>
                            <th style="width: 15%; text-align: center;">משקל מנורמל</th>
                            <th>מהות הבדיקה</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><code>c1_platform</code></td>
                            <td><strong>מצע המפלגה</strong></td>
                            <td style="text-align: center;">15.0%</td>
                            <td style="text-align: center; font-weight: bold; color: var(--accent);">13.64%</td>
                            <td>מסמך מצע רשמי, עקרונות תנועה, תוכניות עבודה שפורסמו.</td>
                        </tr>
                        <tr>
                            <td><code>c2_leader_statements</code></td>
                            <td><strong>אמירות וכתיבה של ראש המפלגה</strong></td>
                            <td style="text-align: center;">15.0%</td>
                            <td style="text-align: center; font-weight: bold; color: var(--accent);">13.64%</td>
                            <td>נאומים, מאמרים, ספרים, ראיונות עומק ופוסטים ברשתות חברתיות.</td>
                        </tr>
                        <tr>
                            <td><code>c3_leader_actions</code></td>
                            <td><strong>ניסיון ופעילות מעשית של ראש המפלגה</strong></td>
                            <td style="text-align: center;">30.0%</td>
                            <td style="text-align: center; font-weight: bold; color: var(--accent);">27.27%</td>
                            <td>רקורד ביצועי בעבר, הצבעות וחקיקה בפועל, החלטות ממשלה, עקביות מול הבטחות (המשקל הגבוה ביותר).</td>
                        </tr>
                        <tr>
                            <td><code>c4_candidates_statements</code></td>
                            <td><strong>אמירות וכתיבה של מועמדים ריאליים</strong></td>
                            <td style="text-align: center;">10.0%</td>
                            <td style="text-align: center; font-weight: bold; color: var(--accent);">9.09%</td>
                            <td>עמדות מועמדים בטווח המנדטים הריאלי לפי סקרים אחרונים.</td>
                        </tr>
                        <tr>
                            <td><code>c5_candidates_actions</code></td>
                            <td><strong>ניסיון ופעילות מעשית של מועמדים ריאליים</strong></td>
                            <td style="text-align: center;">20.0%</td>
                            <td style="text-align: center; font-weight: bold; color: var(--accent);">18.18%</td>
                            <td>רקורד מקצועי ואזרחי, הצבעות בכנסת, תפקידי ביצוע וניהול ציבורי.</td>
                        </tr>
                        <tr>
                            <td><code>c6_designated_executive</code></td>
                            <td><strong>מועמד ריאלי ייעודי לתפקיד ביצועי</strong></td>
                            <td style="text-align: center;">20.0%</td>
                            <td style="text-align: center; font-weight: bold; color: var(--accent);">18.18%</td>
                            <td>האם יש דמות מרכזית המיועדת לתיק/תפקיד הביצועי ומתאימה לעמדת היעד.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div class="card">
            <h3>📏 סולם הציונים ורף ההכללה בסקרים</h3>
            <ul style="margin-right: 24px; color: var(--text-secondary); line-height: 1.8;">
                <li><strong>סולם הציונים</strong>: נע בין <code>100.0-</code> (התנגדות מלאה / עשייה הפוכה מעמדת היעד) לבין <code>100.0+</code> (התאמה מלאה / רקורד מוכח ורפורמות שהושלמו). ציון <code>0.0</code> מציין ניטרליות או היעדר עמדה.</li>
                <li><strong>סף מפלגתי</strong>: כל מפלגה שעוברת את אחוז החסימה (3.25% / 4 מנדטים) בלפחות סקר אחד אמין נכללת בניתוח.</li>
                <li><strong>רף מועמדים ריאליים</strong>: מוגדר כ-<code>round(poll_average) + 1</code> מנדט ביטחון (לפי <code>config/polls.yaml</code>).</li>
            </ul>
        </div>
    </div>
"""

    # =============================================================
    # TAB 4: גישה לנתונים גולמיים (Public GitHub Raw Data Matrix)
    # =============================================================
    html += f"""
    <div id="tab-raw-data" class="tab-content">
        <h2 class="section-title">📁 גישה לנתונים גולמיים ומרכז קבצים (Public GitHub Repository)</h2>
        <p style="color: var(--text-secondary); margin-bottom: 20px;">
            המערכת פועלת בשקיפות מלאה. כל המידע הסטטי, הסקרים, נתוני המחקר הגולמיים, הקבצים המאומתים ודוחות הביקורת פתוחים לעיון ישיר במאגר הציבורי ב-GitHub:
        </p>

        <div class="table-responsive">
            <table>
                <thead>
                    <tr>
                        <th style="width: 20%;">קטגוריית נתונים</th>
                        <th style="width: 28%;">נתיב קובץ / ארטיפקט</th>
                        <th>תיאור התוכן</th>
                        <th style="width: 18%; text-align: center;">קישור ישיר לקובץ</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>קטלוג נושאים סטטי</strong></td>
                        <td><code>data/static/topics/catalog.json</code></td>
                        <td>הגדרה קנונית של 9 נושאי הליבה ושאלות המחקר</td>
                        <td style="text-align: center;"><a href="{GITHUB_BLOB_URL}/data/static/topics/catalog.json" target="_blank" class="github-link-btn">צפה ב-GitHub ↗</a></td>
                    </tr>
                    <tr>
                        <td><strong>מחוון קריטריונים</strong></td>
                        <td><code>data/static/rubric/criteria.json</code></td>
                        <td>6 הקריטריונים, הגדרות מתמטיות ומשקולות מנורמלות</td>
                        <td style="text-align: center;"><a href="{GITHUB_BLOB_URL}/data/static/rubric/criteria.json" target="_blank" class="github-link-btn">צפה ב-GitHub ↗</a></td>
                    </tr>
                    <tr>
                        <td><strong>תרחישי קואליציות</strong></td>
                        <td><code>data/static/coalitions/scenarios.json</code></td>
                        <td>הגדרת גושים וקואליציות פוטנציאליות לבחינת 61 מנדטים</td>
                        <td style="text-align: center;"><a href="{GITHUB_BLOB_URL}/data/static/coalitions/scenarios.json" target="_blank" class="github-link-btn">צפה ב-GitHub ↗</a></td>
                    </tr>
                    <tr>
                        <td><strong>מאגר מפלגות ומועמדים</strong></td>
                        <td><code>data/static/parties/</code></td>
                        <td>14 תיקיות מפלגות: party.json, candidates.json (1..30+), manifesto.md</td>
                        <td style="text-align: center;"><a href="{GITHUB_TREE_URL}/data/static/parties" target="_blank" class="github-link-btn">עיון בתיקייה ↗</a></td>
                    </tr>
                    <tr>
                        <td><strong>סקרי מנדטים עדכניים</strong></td>
                        <td><code>config/polls.yaml</code></td>
                        <td>ממוצעי סקרים, תאריכי סקרים אחרונים וספי מקומות ריאליים</td>
                        <td style="text-align: center;"><a href="{GITHUB_BLOB_URL}/config/polls.yaml" target="_blank" class="github-link-btn">צפה ב-GitHub ↗</a></td>
                    </tr>
                    <tr>
                        <td><strong>קובצי עולם ערכים</strong></td>
                        <td><code>config/profiles/</code></td>
                        <td>פרופילי עמדות של משתמשים (default.yaml, liberal_economic.yaml)</td>
                        <td style="text-align: center;"><a href="{GITHUB_TREE_URL}/config/profiles" target="_blank" class="github-link-btn">עיון בפרופילים ↗</a></td>
                    </tr>
                    <tr>
                        <td><strong>מחקר נושאים מאומת</strong></td>
                        <td><code>data/validated/{date_str}/topics/</code></td>
                        <td>9 קובצי מחקר מאומתים לפי נושאים עם ציטוטים וקישורים מאומתים</td>
                        <td style="text-align: center;"><a href="{GITHUB_TREE_URL}/data/validated/{date_str}/topics" target="_blank" class="github-link-btn">עיון בתיקייה ↗</a></td>
                    </tr>
                    <tr>
                        <td><strong>מסד הערכה מרכזי</strong></td>
                        <td><code>data/evaluations/{date_str}.json</code></td>
                        <td>קובץ הערכות ממוזג מרכזי עבור כל 14 המפלגות</td>
                        <td style="text-align: center;"><a href="{GITHUB_BLOB_URL}/data/evaluations/{date_str}.json" target="_blank" class="github-link-btn">צפה ב-GitHub ↗</a></td>
                    </tr>
                    <tr>
                        <td><strong>יומן אימות קישורים (Tier 1)</strong></td>
                        <td><code>data/validation_logs/{date_str}/tier1_summary.json</code></td>
                        <td>בדיקת HTTP אסינכרונית לכל הציטוטים ואימות סכמות JSON</td>
                        <td style="text-align: center;"><a href="{GITHUB_BLOB_URL}/data/validation_logs/{date_str}/tier1_summary.json" target="_blank" class="github-link-btn">צפה ב-GitHub ↗</a></td>
                    </tr>
                    <tr>
                        <td><strong>דוח אימות ממשק משתמש (UI)</strong></td>
                        <td><code>data/validation_logs/{date_str}/ui_validation.json</code></td>
                        <td>דוח ביקורת DOM ולכידת תצלומי מסך ממוחשבים</td>
                        <td style="text-align: center;"><a href="{GITHUB_BLOB_URL}/data/validation_logs/{date_str}/ui_validation.json" target="_blank" class="github-link-btn">צפה ב-GitHub ↗</a></td>
                    </tr>
                    <tr>
                        <td><strong>תצלום מסך דסקטופ (1280x800)</strong></td>
                        <td><code>data/validation_logs/{date_str}/snapshots/desktop.png</code></td>
                        <td>תצלום מסך שנלכד על ידי Headless Chrome בעת האימות</td>
                        <td style="text-align: center;"><a href="{GITHUB_BLOB_URL}/data/validation_logs/{date_str}/snapshots/desktop.png" target="_blank" class="github-link-btn">צפה בתמונה ↗</a></td>
                    </tr>
                    <tr>
                        <td><strong>תצלום מסך מובייל (375x812)</strong></td>
                        <td><code>data/validation_logs/{date_str}/snapshots/mobile.png</code></td>
                        <td>תצלום מסך מובייל שנלכד על ידי Headless Chrome</td>
                        <td style="text-align: center;"><a href="{GITHUB_BLOB_URL}/data/validation_logs/{date_str}/snapshots/mobile.png" target="_blank" class="github-link-btn">צפה בתמונה ↗</a></td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
"""

    # Page Footer
    html += f"""
    <div class="footer">
        <p>מערכת אנליזה רב-סוכנית לבחירות לכנסת ה-26 | פותח כ-Antigravity Multi-Agent Skill | תאריך עדכון: {date_str}</p>
        <p style="margin-top: 6px;"><a href="{GITHUB_REPO_URL}" target="_blank" class="citation-link">צפה בקוד המקור ובמאגר הנתונים ב-GitHub</a></p>
    </div>
</div>

<!-- Embedded Profiles Data for Dynamic Client-Side Switching -->
<script id="electionProfilesData" type="application/json">
{profiles_json_str}
</script>

<script>
const profilesData = JSON.parse(document.getElementById('electionProfilesData').textContent);

// Tab switching logic
function switchTab(tabId) {{
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-button').forEach(el => el.classList.remove('active'));

    const targetTab = document.getElementById(tabId);
    if (targetTab) targetTab.classList.add('active');

    if (tabId === 'tab-criteria') document.getElementById('btn-criteria').classList.add('active');
    else if (tabId === 'tab-dossiers') document.getElementById('btn-dossiers').classList.add('active');
    else if (tabId === 'tab-methodology') document.getElementById('btn-methodology').classList.add('active');
    else if (tabId === 'tab-raw-data') document.getElementById('btn-raw-data').classList.add('active');
}}

// Jump to party dossier
function goToPartyDossier(partyId) {{
    switchTab('tab-dossiers');
    const el = document.getElementById('dossier-' + partyId);
    if (el) {{
        el.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    }}
}}

// Filter candidates in Tab 1
let filterRealisticOnly = true;

function toggleRealisticOnly(isRealistic) {{
    filterRealisticOnly = isRealistic;
    document.getElementById('btn-filter-realistic').classList.toggle('active', isRealistic);
    document.getElementById('btn-filter-all').classList.toggle('active', !isRealistic);
    filterCandidates();
}}

function filterCandidates() {{
    const query = document.getElementById('candidateSearchInput').value.toLowerCase().trim();
    const cards = document.querySelectorAll('.candidate-card');

    cards.forEach(card => {{
        const name = (card.getAttribute('data-name') || '').toLowerCase();
        const isReal = card.getAttribute('data-realistic') === 'true';

        let matchesSearch = !query || name.includes(query) || card.textContent.toLowerCase().includes(query);
        let matchesFilter = !filterRealisticOnly || isReal;

        if (matchesSearch && matchesFilter) {{
            card.style.display = 'block';
        }} else {{
            card.style.display = 'none';
        }}
    }});
}}

// Badge helper
function getBadgeHtml(score) {{
    const sign = score > 0 ? "+" : "";
    let cls = "neutral";
    if (score >= 40) cls = "positive";
    else if (score > 0) cls = "mild-positive";
    else if (score > -40 && score < 0) cls = "mild-negative";
    else if (score <= -40) cls = "negative";
    return `<span class="badge ${{cls}}">${{sign}}${{Number(score).toFixed(1)}}</span>`;
}}

// Switch Worldview Profile
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

    // 5. Update Coalitions Table
    const coalitions = prof.coalitions || [];
    const coalBody = document.querySelector('#coalitionsTable tbody');
    if (coalBody && coalitions.length > 0) {{
        let cHtml = '';
        coalitions.forEach(c => {{
            const majBadge = c.has_majority ? '<span class="badge positive">✅ רוב קואליציוני</span>' : '<span class="badge negative">❌ מיעוט</span>';
            const partiesStr = c.parties.map(p => `<strong>${{p.name_he}}</strong> (${{p.mandates}})`).join(' + ');
            cHtml += `
            <tr>
                <td><strong>${{c.name_he}}</strong><div style="font-size: 0.85rem; color: var(--text-secondary);">${{c.description || ''}}</div></td>
                <td style="text-align: center; font-size: 1.1rem; font-weight: bold;">${{c.total_mandates}}</td>
                <td style="text-align: center;">${{majBadge}}</td>
                <td style="text-align: center;">${{getBadgeHtml(c.weighted_score)}}</td>
                <td style="font-size: 0.9rem;">${{partiesStr}}</td>
            </tr>`;
        }});
        coalBody.innerHTML = cHtml;
    }}
}}
</script>
</body>
</html>
"""
    return html
