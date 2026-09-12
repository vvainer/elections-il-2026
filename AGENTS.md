# Antigravity Instructions & Project Memory: Knesset 2026 Election Analysis System

## 1. Project Context & Purpose
This project is an automated, objective, evidence-based analysis system evaluating political parties, party leaders, and realistic candidates for the **2026 Israeli Knesset Elections** (taking place late 2026).
It is implemented as an **Antigravity Skill** (`election-analyst`) running locally inside Antigravity using the user's Gemini Pro capabilities.

## 2. Language & Communication Rules
- **Technical Discussion, Scripts, Code, Architecture, and Git**: English.
- **Content (Policy topics, stances, parties, candidate names, justifications, quotes, reports)**: Hebrew (עברית).

## 3. Core Evaluation Methodology
### Scoring Scale
- **Range**: `-100.0` (Complete opposition / diametric conflict with user stance) to `+100.0` (Full alignment / flawless execution record).
- `0.0`: Neutrality, absence of stance, or unaddressed topic.

### 6 Evaluation Criteria (Normalized to 100%)
Original user percentages sum to 110% and are mathematically normalized by dividing by 110:
1. `c1_platform` (מצע המפלגה): **15%** (Normalized: `13.64%`) — Official party manifesto, policy papers, or written commitments.
2. `c2_leader_statements` (אמירות וכתיבה של ראש המפלגה): **15%** (Normalized: `13.64%`) — Speeches, interviews, articles, books, and social media posts.
3. `c3_leader_actions` (ניסיון מעשי ופעילות של ראש המפלגה): **30%** (Normalized: `27.27%`) — Executive track record, ministerial performance, legislative record, votes, consistency vs. promises, and shift in views (Highest weight).
4. `c4_candidates_statements` (אמירות וכתיבה של מועמדים ריאליים): **10%** (Normalized: `9.09%`) — Stances of candidates within the realistic mandate zone.
5. `c5_candidates_actions` (ניסיון מעשי ופעילות של מועמדים ריאליים): **20%** (Normalized: `18.18%`) — Professional background, past public service, voting records, and achievements.
6. `c6_designated_executive` (מועמד ריאלי ייעודי לתפקיד ביצועי): **20%** (Normalized: `18.18%`) — Prominent candidate in a realistic spot championing the topic and designated for the relevant ministerial / executive role.

### Inclusion Threshold & Realistic Spot Definition
- **Party Qualification**: Any party passing the electoral threshold (3.25% / 4 mandates) in **at least one** credible poll (Kan 11, Ch 12, Ch 14, Maariv) is included.
- **Realistic Candidates Cutoff**: Defined as `round(poll_average) + 1` mandate safety margin (tracked in `config/polls.yaml`).
- **Verifiable Citations**: Every score must cite real evidence, quotes, and direct clickable URLs.

---

## 4. The 9 Core Policy Topics & User Desired Stances
Configured in `config/profiles/default.yaml` (Equal weight 1.0 each by default):
1. **חינוך (education)**:
   - התאמה של צורת הלימוד וחומר הלימוד לתקופה, השקעה במורים (הכשרה, שכר, הבאת מורים מעולים). דרישה של תכנית ממשלתית בכל ביה״ס שמקבל תקצוב ממשלתי או עירוני. חינוך מותאם יותר לצרכי הילדים השונים.
2. **שינוי במערכת השלטון (governance_reform)**:
   - ביזור, יותר אחריות לשלטון מקומי, חיזוק של כנסת יחסית לממשלה ויחסית למערכת המשפט. פתרון סוגיית הרשות השופטת. פיזור סמכויות של יועמ״ש. להתאים מערכת השלטון, בחירות למצב וגודל של מדינת ישראל מצד אחד ולתקופה וטכנולוגיה מהצד השני. השקעה באקדמיה.
3. **בניית תשתית להצלחה של מדינת ישראל בדור הקרוב (future_infrastructure)**:
   - השקעה במדע, רובוטיקה, חלל, קוונטום, אנרגיה, מים, תשתיות.
4. **בניית מצב אסטרטגי משופר למדינת ישראל (strategic_posture)**:
   - מעגלים נרחבים של שת״פ אזרחי ובטחוני, הסכמים צבאיים, הצעה קונקרטית לפתרון הסוגייה הפלסטינית ללא מסירת שטחים נרחבים וירושלים (אפשרי בצורה מדודה אבל לא קווי 67). פתרון להתמודדות עם אנטיציונות ופלסטיניזציה של העולם המערבי.
5. **דת ומדינה (religion_and_state)**:
   - גישה זהירה שמאפשרת לרשויות מקומיות יותר חופש ולמדינה הגדרה של כללים מנחים.
6. **תכנית להחזרה של יורדים (returning_residents)**:
   - תכנית להחזרה של יורדים, במיוחד רופאים, מדענים ויזמים.
7. **שוק פתוח, יזמות, הורדת חסמים (open_market)**:
   - שוק פתוח, יזמות, הורדת חסמים.
8. **סידור מחדש של העברות (welfare_reform)**:
   - מצד אחד לאפשר לאנשים שאינם מסוגלים להתפרנס לחיות בכבוד מצד שני לא לקדם התנהגויות שמובילות לעוני, חוסר חינוך ובטלה, לא לאפשר לחיות על חשבון המערכת לאוכלוסיות שלמות ולהוריד כמות האנשים שמועסקים בחלוקה.
9. **צמצום הממשלה (government_downsizing)**:
   - צמצום הממשלה - גם במספר השרים, משרדי ממשלה וגם בגודל המשרדים.

---

## 5. Weekly Workflow & Execution Instructions
When the user prompts to run the weekly analysis (e.g., "Run weekly election analysis update" or "הרץ עדכון שבועי לאנליזת הבחירות"):
1. **Check Polls**: Update `config/polls.yaml` with the latest poll figures and realistic cutoffs. Check if any new party crossed the 4-seat threshold.
2. **Research Deltas**: Perform targeted live web research on news, candidate statements, or policy moves from the past week.
3. **Update Dataset**: Update or create `data/evaluations/YYYY-MM-DD.json` with updated scores, notes, and citations.
4. **Run Analysis Pipeline**:
   ```bash
   .venv/bin/python3 scripts/run_analysis.py --date YYYY-MM-DD
   ```
5. **Outputs Generated**:
   - `reports/YYYY-MM-DD/report.md`: Full GitHub-flavored markdown report.
   - `docs/index.html`: Responsive RTL HTML dashboard for GitHub Pages.
6. **Git Commit**: Commit the updated data and reports.

---

## 6. Project Files Structure
- `.agents/skills/election-analyst/SKILL.md`: Skill runbook for Antigravity.
- `.agents/skills/election-analyst/references/criteria_rubric.md`: Scoring rubric and math.
- `config/profiles/default.yaml`: 9 topics, stances, checklists, and weights.
- `config/polls.yaml`: Current polling benchmarks and realistic seat cutoffs.
- `config/parties.yaml`: Party registry, leadership, candidates, official links.
- `scripts/evaluator.py`: Python mathematical evaluation engine.
- `scripts/generate_report.py`: Markdown and HTML dashboard generator.
- `scripts/run_analysis.py`: Main CLI runner.
- `data/evaluations/`: Raw JSON datasets per analysis date.
- `reports/`: Generated markdown reports by date.
- `docs/`: GitHub Pages deployment folder (`index.html`).
