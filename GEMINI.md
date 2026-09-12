# Antigravity Instructions & Project Memory: Knesset 2026 Election Analysis System

## 1. Project Context & Purpose
This project is an automated, objective, evidence-based analysis system evaluating political parties, party leaders, and realistic candidates for the **2026 Israeli Knesset Elections** (taking place late 2026).
It is implemented using two dedicated **Antigravity Skills**:
1. **`run-election-round`** (`.agents/skills/run-election-round/SKILL.md`): The end-to-end execution skill orchestrating the full 4-phase multi-agent lifecycle.
2. **`election-analyst`** (`.agents/skills/election-analyst/SKILL.md`): The domain methodology and criteria evaluation skill.

> ⚠️ **STRICT MANDATE: NO MONOLITHIC SHORTCUTS**  
> Running an election analysis round (e.g. "run a full report round", "הרץ עדכון שבועי", "הרץ סבב רב-סוכנים מלא") MUST NEVER be executed as a monolithic local script or by copying past data.  
> You MUST activate the **`run-election-round`** skill and use Antigravity subagent tools (`define_subagent` and `invoke_subagent`) to actually launch the 4 specialized agent roles across their respective phases.

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

## 5. Multi-Agent Setup & Execution Lifecycle (`run-election-round`)

Whenever instructed to run an analysis round or weekly update, follow the **`run-election-round`** skill:

### Step 0: Ensure Subagents are Defined
Define the 4 subagent types using `define_subagent` if not already defined in the conversation:
1. `topic_researcher`: Equipped with `enable_write_tools: true`, prompt based on `references/researcher_prompt.md`.
2. `topic_validator`: Equipped with `enable_write_tools: true`, prompt based on `references/validator_prompt.md`.
3. `report_rebuilder`: Equipped with `enable_write_tools: true`, prompt based on `references/rebuilder_prompt.md`.
4. `ui_validator`: Equipped with `enable_write_tools: true`, prompt based on `references/ui_validator_prompt.md`.

### Phase 1: Parallel Information Gathering (9 Concurrent Agents)
- Update `config/polls.yaml` with the latest poll averages and cutoffs.
- Call `invoke_subagent` with 9 parallel `topic_researcher` agents (one per policy topic) investigating all qualifying parties.
- Each researcher saves to `data/staging/YYYY-MM-DD/topics/<topic_id>.json`.

### Phase 2: Two-Tier Cross-Validation & Feedback Loop
- Run Tier 1 automated link and schema verification (`scripts/validate_links.py`).
- Call `invoke_subagent` for `topic_validator` agents to cross-examine factual claims and rubric compliance.
- If defects/unverified links are flagged, send revision feedback to the research agent via `send_message` (max 1 revision round).
- Validated files saved to `data/validated/YYYY-MM-DD/topics/<topic_id>.json` and audit logs to `data/validation_logs/YYYY-MM-DD/`.

### Phase 3: Aggregation & Report Rebuilding
- Call `invoke_subagent` for `report_rebuilder` agent.
- Merges topic files into `data/evaluations/YYYY-MM-DD.json` (`scripts/merge_topics.py`).
- Runs scoring engine and generates Markdown and HTML (`scripts/run_analysis.py`).
- Prepares Hebrew Executive Synthesis.

### Phase 4: UI Validation & Deployment Gatekeeper
- Call `invoke_subagent` for `ui_validator` agent.
- Runs `scripts/validate_ui.py --date YYYY-MM-DD --strict` capturing desktop and mobile snapshots.
- Performs visual inspection (RTL layout, Hebrew typography, responsive cards).
- If rejected, sends structured Reject payload back to `report_rebuilder` (max 2 revision rounds).
- If approved (`status: "APPROVED"` in `ui_validation.json`), commits and deploys to GitHub Pages (`git push origin main`).

---

## 6. Project Files Structure
- `.agents/skills/`:
  - **`run-election-round/SKILL.md`**: Master execution skill orchestrating the 4-phase multi-agent round.
  - **`election-analyst/SKILL.md`**: Core methodology, policy profiles, and evaluation criteria.
  - `election-analyst/references/`:
    - `criteria_rubric.md`: Scoring rubric and weighting math.
    - `researcher_prompt.md`: Prompt template for parallel gathering agents.
    - `validator_prompt.md`: Prompt template for cross-validation agents.
    - `rebuilder_prompt.md`: Prompt template for report rebuilder.
    - `ui_validator_prompt.md`: Prompt template for UI validator and gatekeeper.
- `config/`:
  - `profiles/default.yaml`: 9 topics, stances, checklists, and weights.
  - `polls.yaml`: Current polling benchmarks and realistic seat cutoffs.
  - `parties.yaml`: Party registry, leadership, candidates, official links.
- `scripts/`:
  - `validate_links.py`: Fast concurrent HTTP link & schema validator.
  - `validate_ui.py`: Headless Chrome snapshot capturer and DOM validator.
  - `merge_topics.py`: Topic dataset merger & splitter.
  - `evaluator.py`: Mathematical 6-criteria evaluation engine.
  - `generate_report.py`: Markdown and HTML dashboard generator.
  - `run_analysis.py`: Scoring runner.
  - `orchestrate_analysis.py`: End-to-end pipeline orchestrator CLI.
- `data/`:
  - `staging/YYYY-MM-DD/topics/`: Raw research per topic.
  - `validated/YYYY-MM-DD/topics/`: Validated research per topic.
  - `validation_logs/YYYY-MM-DD/`: Audit trail, link checks, snapshots, and `ui_validation.json`.
  - `evaluations/YYYY-MM-DD.json`: Central merged evaluation files.
- `reports/YYYY-MM-DD/report.md`: Generated weekly Markdown reports.
- `docs/index.html`: Responsive RTL HTML dashboard deployed to GitHub Pages.
