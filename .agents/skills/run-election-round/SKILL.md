---
name: run-election-round
description: >-
  Executes the complete end-to-end 4-phase multi-agent election analysis round for the 2026 Israeli Knesset Elections.
  Orchestrates the 4 specialized Antigravity subagents: defines subagent roles via define_subagent,
  concurrently launches 9 topic researchers via invoke_subagent (Phase 1), runs two-tier cross-validation
  with researcher feedback loops (Phase 2), rebuilds reports and executive synthesis (Phase 3),
  and enforces strict UI validation with headless Chrome desktop/mobile snapshots before GitHub Pages deployment (Phase 4).
  Activate whenever the user requests to run a full report round, execute the multi-agent election cycle, or perform a weekly update.
---

# Run Election Round - מיומנות הרצת סבב רב-סוכנים מלא (Knesset 2026)

מיומנות זו מנחה את סוכן Antigravity בביצוע מחזור ניתוח שלם, מקבילי ומבוסס ראיות לקראת הבחירות לכנסת ה-26.  
המיומנות מפעילה סוכני משנה עצמאיים באמצעות הכלים המובנים של Antigravity (`define_subagent`, `invoke_subagent`, `send_message`).

> ⚠️ **איסור קיצורי דרך (Mandatory Rule)**  
> סבב זה **חייב** להתבצע באמצעות הפעלת סוכני המשנה בזה אחר זה על פני ארבעת השלבים. אין להריץ סקריפטים מונוליטיים העוקפים את סוכני המחקר או להעתיק נתונים קודמים ללא ביצוע שלבי האימות וה-UI.

---

## 📅 שלב הכנה: תאריך, מאגר סטטי ונתוני סקרים
1. קבע את תאריך הסבב הנוכחי (`DATE = YYYY-MM-DD`, לדוגמה: `2026-09-12`).
2. ודא כי מאגר המידע הסטטי מאומת ותקין: `python3 scripts/build_static_kb.py --verify`. (במידת הצורך השתמש במיומנות `build-static-kb`).
3. ודא כי קובץ `config/polls.yaml` מעודכן בסקרי השבוע האחרון (ממוצע מנדטים וסף מקומות ריאליים).
4. ודא כי תיקיות היעד קיימות:
   - `data/staging/{DATE}/topics/`
   - `data/validated/{DATE}/topics/`
   - `data/validation_logs/{DATE}/snapshots/`

---

## 🛠️ שלב 0: הגדרת סוכני המשנה (`define_subagent`)

אם סוכני המשנה טרם הוגדרו בשיחה, יש לקרוא ל-`define_subagent` עבור כל אחד מ-4 התפקידים:

### 1. `topic_researcher`
- **name**: `topic_researcher`
- **description**: "Subagent that performs deep web research and evidence gathering for a single policy topic across all qualifying parties"
- **enable_write_tools**: `true`
- **system_prompt**: קרא מתוך [.agents/skills/election-analyst/references/researcher_prompt.md](../election-analyst/references/researcher_prompt.md)

### 2. `topic_validator`
- **name**: `topic_validator`
- **description**: "Subagent that cross-validates topic findings against the 6-criteria rubric and checks citation authenticity"
- **enable_write_tools**: `true`
- **system_prompt**: קרא מתוך [.agents/skills/election-analyst/references/validator_prompt.md](../election-analyst/references/validator_prompt.md)

### 3. `report_rebuilder`
- **name**: `report_rebuilder`
- **description**: "Subagent that merges validated datasets, calculates weighted scores, writes the Hebrew executive synthesis, and produces reports"
- **enable_write_tools**: `true`
- **system_prompt**: קרא מתוך [.agents/skills/election-analyst/references/rebuilder_prompt.md](../election-analyst/references/rebuilder_prompt.md)

### 4. `ui_validator`
- **name**: `ui_validator`
- **description**: "Subagent that verifies HTML DOM, RTL rendering, responsive layouts, captures browser snapshots, and gates deployment"
- **enable_write_tools**: `true`
- **system_prompt**: קרא מתוך [.agents/skills/election-analyst/references/ui_validator_prompt.md](../election-analyst/references/ui_validator_prompt.md)

---

## 🚀 שלב 1: איסוף מידע מקבילי (9 סוכני נושא)

בצע קריאה **אחת** ל-`invoke_subagent` המכילה את כל 9 הנושאים להפעלה מקבילית:

```json
{
  "Subagents": [
    {
      "TypeName": "topic_researcher",
      "Role": "Researcher: Education",
      "Prompt": "Investigate topic 'education' (חינוך) across all qualifying parties for {DATE}. Evaluate 6 criteria per party using config/profiles/default.yaml rubric. Cite verified sources and save JSON to data/staging/{DATE}/topics/education.json."
    },
    {
      "TypeName": "topic_researcher",
      "Role": "Researcher: Governance Reform",
      "Prompt": "Investigate topic 'governance_reform' (שינוי במערכת השלטון) across all qualifying parties for {DATE}. Evaluate 6 criteria per party using config/profiles/default.yaml rubric. Cite verified sources and save JSON to data/staging/{DATE}/topics/governance_reform.json."
    },
    {
      "TypeName": "topic_researcher",
      "Role": "Researcher: Future Infrastructure",
      "Prompt": "Investigate topic 'future_infrastructure' (תשתיות עתיד ומדע) across all qualifying parties for {DATE}. Evaluate 6 criteria per party using config/profiles/default.yaml rubric. Cite verified sources and save JSON to data/staging/{DATE}/topics/future_infrastructure.json."
    },
    {
      "TypeName": "topic_researcher",
      "Role": "Researcher: Strategic Posture",
      "Prompt": "Investigate topic 'strategic_posture' (מצב אסטרטגי וביטחון) across all qualifying parties for {DATE}. Evaluate 6 criteria per party using config/profiles/default.yaml rubric. Cite verified sources and save JSON to data/staging/{DATE}/topics/strategic_posture.json."
    },
    {
      "TypeName": "topic_researcher",
      "Role": "Researcher: Religion & State",
      "Prompt": "Investigate topic 'religion_and_state' (דת ומדינה) across all qualifying parties for {DATE}. Evaluate 6 criteria per party using config/profiles/default.yaml rubric. Cite verified sources and save JSON to data/staging/{DATE}/topics/religion_and_state.json."
    },
    {
      "TypeName": "topic_researcher",
      "Role": "Researcher: Returning Residents",
      "Prompt": "Investigate topic 'returning_residents' (החזרת יורדים) across all qualifying parties for {DATE}. Evaluate 6 criteria per party using config/profiles/default.yaml rubric. Cite verified sources and save JSON to data/staging/{DATE}/topics/returning_residents.json."
    },
    {
      "TypeName": "topic_researcher",
      "Role": "Researcher: Open Market",
      "Prompt": "Investigate topic 'open_market' (שוק פתוח ויזמות) across all qualifying parties for {DATE}. Evaluate 6 criteria per party using config/profiles/default.yaml rubric. Cite verified sources and save JSON to data/staging/{DATE}/topics/open_market.json."
    },
    {
      "TypeName": "topic_researcher",
      "Role": "Researcher: Welfare Reform",
      "Prompt": "Investigate topic 'welfare_reform' (סידור מחדש של העברות) across all qualifying parties for {DATE}. Evaluate 6 criteria per party using config/profiles/default.yaml rubric. Cite verified sources and save JSON to data/staging/{DATE}/topics/welfare_reform.json."
    },
    {
      "TypeName": "topic_researcher",
      "Role": "Researcher: Government Downsizing",
      "Prompt": "Investigate topic 'government_downsizing' (צמצום הממשלה) across all qualifying parties for {DATE}. Evaluate 6 criteria per party using config/profiles/default.yaml rubric. Cite verified sources and save JSON to data/staging/{DATE}/topics/government_downsizing.json."
    }
  ]
}
```

*אל תבצע פולינג בלולאה.* המערכת תודיע אוטומטית כאשר כל סוכן יסיים את פעולתו.

---

## 🔍 שלב 2: אימות צולב דו-שלבי ולולאת משוב

### 2.1 אימות טכני מקדים (Tier 1)
הרץ את בודק הקישורים והסכמה:
```bash
python3 scripts/validate_links.py data/staging/{DATE}/topics --report data/validation_logs/{DATE}/tier1_summary.json
```

### 2.2 אימות מהותי (Tier 2)
הפעל סוכני `topic_validator` באמצעות `invoke_subagent` לבדיקת 9 הקבצים:
- וידוא כי מועמדים שנותחו ב-`c4`, `c5`, `c6` מצויים בטווח המנדטים הריאלי לפי `config/polls.yaml`.
- בדיקת תאימות של הציטוטים לטענות ולהנמקות.
- כיול ציונים מול המחוון (`-100` עד `+100`).

### 2.3 לולאת משוב (Feedback Loop)
- אם נמצא ליקוי מהותי או קישור שבור: המאמת שולח הודעה מובנית לסוכן המחקר באמצעות `send_message`.
- סוכן המחקר מתקן ושומר את הקובץ המעודכן ב-`data/staging/{DATE}/topics/`.
- מוגבל ל-**סבב תיקון אחד (1 round)**. אם עדיין לא תוקן, המאמת מבצע התאמה סופית ומעדכן מקור מאומת.
- הקבצים המאושרים נשמרים ב:
  `data/validated/{DATE}/topics/<topic_id>.json`
- יומן הביקורת נשמר ב:
  `data/validation_logs/{DATE}/`

---

## 📊 שלב 3: מיזוג ובניית דוחות מרובי-פרופילים (`report_rebuilder`)

הפעל את סוכן `report_rebuilder` באמצעות `invoke_subagent`:
1. **מיזוג**: הרצת `python3 scripts/merge_topics.py` למיזוג כל 9 הקבצים המאומתים למסד נתונים מרכזי:
   ```bash
   python3 scripts/merge_topics.py --topics-dir data/validated/{DATE}/topics --output data/evaluations/{DATE}.json --date {DATE}
   ```
2. **חישוב ציונים והפקת דוחות עבור כל פרופילי עולם הערכים**:
   ```bash
   python3 scripts/run_analysis.py --date {DATE}
   ```
   הסקריפט:
   - מאתר ומעריך את כל הפרופילים המוגדרים ב-`config/profiles/*.yaml` (למשל ברירת מחדל, ליברלי-כלכלי, ופרופילים אישיים שנוצרו במיומנות `interview-worldview`).
   - מצליב ומטמיע את נתוני הרקע הסטטיים של המועמדים (קו״ח, הצבעות, הישגים) מתוך `data/static/parties/`.
   - מייצר דוחות Markdown מפורטים לכל פרופיל: `reports/{DATE}/<profile_stem>.md` ו-`reports/{DATE}/report.md`.
   - מייצר דשבורד RTL רספונסיבי ב-`docs/index.html` הכולל בורר פרופילים דינמי (`<select id="profileSelect">`) המעדכן את לוח התוצאות, המטריצה והציונים בזמן אמת.
3. **תקציר מנהלים בעברית**:
   ניסוח סקירה תמציתית (Executive Synthesis) הכוללת את לוח המובילים, פערים עיקריים בין הגושים ותובנות מפתח. הסקירה מוטמעת בראש `report.md`.

---

## 🛡️ שלב 4: אימות ממשק משתמש ושער פריסה (`ui_validator`)

הפעל את סוכן `ui_validator` באמצעות `invoke_subagent`:
1. **בדיקת DOM ולכידת תצלומים**:
   ```bash
   python3 scripts/validate_ui.py --date {DATE} --strict
   ```
   הסקריפט לוכד:
   - Desktop snapshot: `data/validation_logs/{DATE}/snapshots/desktop.png` (1280x800)
   - Mobile snapshot: `data/validation_logs/{DATE}/snapshots/mobile.png` (375x812)
   ומוודא תקינות מלאה של כרטיסי מובילים, טבלאות, כיווניות RTL ותגיות עברית.

2. **בחינה חזותית מולטימודלית**:
   הסוכן בוחן את תצלומי המסך לוודא שאין גלישת רוחב, חיתוך טקסט או בעיות ניגודיות.

3. **לולאת דחיות (UI Rejection Loop)**:
   - אם נמצאו ליקויים: הסוכן שולח הודעת Reject מובנית לסוכן `report_rebuilder` (עד 2 סבבי תיקון).
   - סוכן `report_rebuilder` מתקן את התבנית ב-`scripts/generate_report.py`, מפיק מחדש את הדשבורד, ומבקש אימות חוזר.

4. **שער פריסה קשיח (Deployment Gatekeeper)**:
   - פריסה ל-GitHub Pages חסומה לחלוטין כל עוד `status != "APPROVED"` בקובץ `data/validation_logs/{DATE}/ui_validation.json`.
   - ברגע שהתקבל אישור (`APPROVED`):
     ```bash
     git add data/ reports/ docs/
     git commit -m "Weekly election analysis update: {DATE} [UI Validated]"
     git push origin main
     ```
   - הסוכן מציג למשתמש את לוח המובילים, קישור לדוח ה-Markdown, תצלומי המסך, והדשבורד החי:
     `https://vvainer.github.io/elections-il-2026/`
