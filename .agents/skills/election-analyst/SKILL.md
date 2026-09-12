---
name: election-analyst
description: >-
  System for analyzing political parties and candidates for the 2026 Israeli Knesset elections.
  Evaluates party platforms, leader track records, realistic candidates, and designated executive
  appointees against user policy profiles across 6 weighted criteria, using a 4-phase multi-agent
  architecture (topic gatherers, two-tier validators, report rebuilder, and UI validation gatekeeper).
---

# Election Analyst 2026 - מיומנות ניתוח בחירות לכנסת 2026 (ארכיטקטורת רב-סוכנים מקבילית)

מיומנות זו מנחה את סוכן Antigravity בהפעלת מערכת רב-סוכנים מקבילית (Parallel Multi-Agent System) לביצוע ניתוח שבועי מקיף, אובייקטיבי ומבוסס ראיות של המפלגות והמועמדים לקראת הבחירות לכנסת ה-26.

---

## 🏛️ ארכיטקטורת ארבע השכבות (Four-Phase Multi-Agent Pipeline)

המערכת פועלת באמצעות ארבעה סוגי סוכנים ושלבי עבודה מוגדרים:

```mermaid
flowchart TD
    subgraph Phase1["שלב 1: איסוף מידע מקבילי (9 סוכני נושא)"]
        A1["סוכן חינוך (education)"]
        A2["סוכן משטר וממשל (governance_reform)"]
        A3["סוכן תשתיות ומדע (future_infrastructure)"]
        A4["סוכן אסטרטגיה וביטחון (strategic_posture)"]
        A5["סוכן דת ומדינה (religion_and_state)"]
        A6["סוכן השבת יורדים (returning_residents)"]
        A7["סוכן שוק חופשי (open_market)"]
        A8["סוכן רווחה והעברות (welfare_reform)"]
        A9["סוכן צמצום ממשלה (government_downsizing)"]
    end

    A1 & A2 & A3 & A4 & A5 & A6 & A7 & A8 & A9 -->|שמירה ב-JSON| Staging["data/staging/YYYY-MM-DD/topics/*.json"]

    subgraph Phase2["שלב 2: אימות צולב דו-שלבי עם לולאת משוב"]
        T1["שלב 2א: אימות אוטומטי (validate_links.py - תקינות קישורים ומבנה)"]
        Staging --> T1
        T1 --> T2["שלב 2ב: סוכני אימות צולב (topic_validator)"]
        T2 -->|חריגות/ליקויים?| Feedback{"נדרש תיקון?"}
        Feedback -- "כן (עד סבב תיקון 1)" --> Revision["סבב עדכון ממוקד ע״י סוכן המחקר"]
        Revision --> T2
        Feedback -- "מאושר / סופי" --> Validated["data/validated/YYYY-MM-DD/topics/*.json"]
        T2 --> ValLog["data/validation_logs/YYYY-MM-DD/*_log.json"]
    end

    subgraph Phase3["שלב 3: מיזוג ובניית דוחות"]
        Merge["scripts/merge_topics.py (מיזוג 9 הנושאים לקובץ מרכזי)"]
        Validated --> Merge
        Merge --> EvalDataset["data/evaluations/YYYY-MM-DD.json"]
        EvalDataset --> Rebuilder["סוכן בניית דוחות (report_rebuilder)"]
        Rebuilder --> Scoring["scripts/evaluator.py (מנוע חישוב משקלים)"]
        Rebuilder --> Markdown["reports/YYYY-MM-DD/report.md"]
        Rebuilder --> Dashboard["docs/index.html (דשבורד GitHub Pages)"]
        Rebuilder --> ExecSummary["תקציר מנהלים שבועי בעברית"]
    end

    subgraph Phase4["שלב 4: אימות ממשק משתמש ושער פריסה (UI Validation Gate)"]
        Dashboard --> UICheck["scripts/validate_ui.py (תצלומי מסך ואימות DOM)"]
        UICheck --> Snapshots["data/validation_logs/YYYY-MM-DD/snapshots/*.png"]
        Snapshots & Dashboard --> UIAgent["סוכן אימות UI (ui_validator)"]
        UIAgent --> UILog["data/validation_logs/YYYY-MM-DD/ui_validation.json"]
        UIAgent --> UIGate{"סטטוס UI?"}
        UIGate -- "REJECTED (עד 2 סבבים)" --> UIRejection["הודעת דחייה + ליקויים וסלקטורים לתיקון"]
        UIRejection --> Rebuilder
        UIGate -- "APPROVED" --> GitPush["Git Commit & Push ל-origin/main (GitHub Pages)"]
        UIGate -- "REJECTED (לאחר 2 סבבים)" --> Halt["עצירת פריסה והתרעה למשתמש"]
    end
```

---

## 📂 מבנה התיקיות והנתונים

- `data/staging/YYYY-MM-DD/topics/<topic_id>.json`: ממצאי מחקר גולמיים מ-9 סוכני האיסוף.
- `data/validated/YYYY-MM-DD/topics/<topic_id>.json`: נתונים מאומתים לאחר בדיקת קישורים ואימות מחוון.
- `data/validation_logs/YYYY-MM-DD/`: יומני בקרה וביקורת עובדתיים ויומן `ui_validation.json`.
- `data/validation_logs/YYYY-MM-DD/snapshots/`: תצלומי מסך מ-Chrome Headless (`desktop.png`, `mobile.png`).
- `data/evaluations/YYYY-MM-DD.json`: מסד הנתונים השבועי המלא והממוזג.
- `reports/YYYY-MM-DD/report.md`: דו"ח Markdown מפורט.
- `docs/index.html`: אתר אינטראקטיבי RTL ל-GitHub Pages.

---

## 🤖 הגדרת הסוכנים ותפקידיהם

### 1. סוכן איסוף מידע לפי נושא (`topic_researcher`)
- **חלוקה מקבילית**: מופעלים 9 סוכנים במקביל באמצעות `invoke_subagent`. כל סוכן מקבל נושא בודד וחוקר את כל המפלגות שעברו את אחוז החסימה (לפי `config/polls.yaml`).
- **קריטריונים**: 6 קריטריונים לפי מחוון הניתוח (`c1_platform` עד `c6_designated_executive`).
- **ציטוטים**: חובת ציטוט ישיר, שם מקור וקישור URL פעיל.
- **תבנית הנחיה**: [researcher_prompt.md](./references/researcher_prompt.md).

### 2. סוכן אימות צולב עובדתי (`topic_validator`)
- **שלב ראשון (Automated Tier-1)**: הרצת `python3 scripts/validate_links.py` לבדיקת זמינות HTTP של כל הקישורים ותקינות מבנה ה-JSON.
- **שלב שני (Substantive Tier-2)**: בדיקת אמיתות הציטוטים, וידוא שהמועמדים המצוינים נמצאים בטווח המקומות הריאליים (`realistic_cutoff`), ובדיקת כיול ציונים הוגן מול המחוון.
- **לולאת משוב (Feedback Loop)**: במקרה של ליקוי, נשלחת הודעת משוב לסוכן המחקר (עד סבב תיקון אחד).
- **תבנית הנחיה**: [validator_prompt.md](./references/validator_prompt.md).

### 3. סוכן בניית דוחות (`report_rebuilder`)
- **מיזוג**: הרצת `python3 scripts/merge_topics.py` למיזוג 9 קובצי הנושאים המאומתים למסד נתונים מרכזי.
- **חישוב והפקה**: הרצת `python3 scripts/run_analysis.py` לחישוב הציונים והפקת `report.md` ו-`docs/index.html`.
- **תקציר מנהלים (Executive Synthesis)**: ניסוח סקירה תמציתית בעברית של לוח המובילים, שינויים שבועיים ופערים בין הגושים.
- **קבלת משוב ודחיות UI**: קבלת הודעות Reject מסוכן ה-UI, תיקון תבניות וסגנונות ב-`scripts/generate_report.py`, והפקה מחדש (עד 2 סבבי תיקון).
- **תבנית הנחיה**: [rebuilder_prompt.md](./references/rebuilder_prompt.md).

### 4. סוכן אימות ממשק משתמש ושער פריסה (`ui_validator`)
- **בדיקה אוטומטית ותצלומים**: הרצת `python3 scripts/validate_ui.py` ללכידת תצלומי מסך (Desktop 1280x800, Mobile 375x812) ובדיקת תקינות תגיות RTL, כרטיסי מובילים, וטבלאות קריטריונים.
- **בדיקה חזותית מולטימודלית**: בחינת תצלומי המסך לווידוא היעדר גלישה אופקית, תקינות פיסוק בעברית וניגודיות צבעי התגים.
- **לולאת דחיות (Rejection Loop)**: שליחת הודעת Reject מובנית לסוכן בניית הדוחות עם פירוט סלקטורים ותיקונים נדרשים (עד 2 סבבים).
- **שער פריסה קשיח (Deployment Gate)**: פריסה ל-GitHub Pages חסומה לחלוטין כל עוד סטטוס ה-UI אינו `APPROVED`.
- **תבנית הנחיה**: [ui_validator_prompt.md](./references/ui_validator_prompt.md).

---

## 🛠️ כלי CLI שימושיים
```bash
# אימות קישורים ומבנה (Staging או Validated)
python3 scripts/validate_links.py data/staging/YYYY-MM-DD/topics --skip-http

# מיזוג קובצי נושאים לקובץ מרכזי
python3 scripts/merge_topics.py --topics-dir data/validated/YYYY-MM-DD/topics --output data/evaluations/YYYY-MM-DD.json --date YYYY-MM-DD

# אימות UI ולכידת תצלומי מסך
python3 scripts/validate_ui.py --date YYYY-MM-DD --strict

# הפעלה כוללת או שלבית באמצעות האורקסטרטור
python3 scripts/orchestrate_analysis.py --date YYYY-MM-DD --stage all --skip-http
```
