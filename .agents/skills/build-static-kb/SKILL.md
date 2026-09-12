---
name: build-static-kb
description: >-
  Gathers and maintains the static knowledge base for the 2026 Israeli Knesset Elections.
  Orchestrates parallel Antigravity subagents (static_party_researcher and static_kb_validator)
  to build complete party rosters (positions 1..30+), candidate background profiles (CVs, key votes,
  major achievements, failures/controversies), party manifestos/principles, policy topics catalog,
  and evaluation rubric criteria into data/static/parties/<party_id>/, data/static/topics/, and data/static/rubric/.
  Activate whenever new parties qualify, candidate lists change, or static candidate data needs updating.
---

# Build Static Knowledge Base - מיומנות איסוף וניהול מאגר המידע הסטטי (Knesset 2026)

מיומנות זו מנחה את סוכן Antigravity בבנייה, עדכון ואימות של מאגר המידע הסטטי המלא לקראת הבחירות לכנסת ה-26.  
המאגר מפריד בצורה מוחלטת בין **מידע סטטי** (קבוע, היסטורי, מצעי מפלגות, רשימות מועמדים מלאות 1..30+, קורות חיים, הצבעות היסטוריות, הישגים וכישלונות) לבין **מידע דינמי** (סקרי מנדטים עדכניים, אמירות וראיונות שבועיים, וציוני התאמה לפרופילי משתמש).

> ⚠️ **עקרון ההפרדה והשמירה בארטיפקטים בלבד**  
> שום מידע פוליטי, שמות מועמדים או מצעים אינם נכתבים במסמכי המערכת או ההנחיות (`AGENTS.md`, `GEMINI.md`).  
> כל המידע הסטטי נשמר אך ורק בתיקיית `data/static/` בקבצים מודולריים הניתנים לבנייה מחדש.

---

## 🏛️ מבנה מאגר המידע הסטטי (`data/static/`)

```
data/static/
├── topics/
│   └── catalog.json          # קטלוג 9 נושאי המדיניות (מזהים, שמות בעברית ובאנגלית, שאלות מנחות)
├── rubric/
│   └── criteria.json         # 6 קריטריוני ההערכה ומשקולות מנורמלות (110% מנורמל ל-100%)
└── parties/
    ├── likud/
    │   ├── party.json        # פרטי מפלגה, יו״ר, אתר רשמי, קישור לסיעה בכנסת
    │   ├── candidates.json   # רשימת מועמדים מלאה (1..20+), קו״ח, הישגים, כישלונות, הצבעות
    │   └── manifesto.md      # מצע המפלגה, עקרונות תנועה ומסמכי מדיניות רשמיים
    ├── yashar/
    ├── beyachad/
    └── ... (כל 14 המפלגות העוברות את אחוז החסימה)
```

---

## 🛠️ שלב 0: הגדרת סוכני המשנה (`define_subagent`)

אם סוכני המשנה טרם הוגדרו בשיחה:

### 1. `static_party_researcher`
- **name**: `static_party_researcher`
- **description**: "Subagent that performs thorough web and Knesset research on a political party: complete candidate roster (1..30+), CVs, achievements, voting records, and official manifesto"
- **enable_write_tools**: `true`
- **system_prompt**: קרא מתוך [.agents/skills/build-static-kb/references/static_researcher_prompt.md](references/static_researcher_prompt.md)

### 2. `static_kb_validator`
- **name**: `static_kb_validator`
- **description**: "Subagent that audits static party files, validates schema compliance, checks candidate completeness, and verifies factual sources"
- **enable_write_tools**: `true`
- **system_prompt**: קרא מתוך [.agents/skills/build-static-kb/references/static_validator_prompt.md](references/static_validator_prompt.md)

---

## 🚀 שלב 1: איסוף מקבילי של נתוני מפלגות ומועמדים

הפעל את סוכני המחקר המקביליים באמצעות `invoke_subagent` בקבוצות לפי גושים או מפלגות בודדות.  
כל סוכן מחקר נדרש לייצר עבור המפלגה שלו שלושה קבצים בתוך `data/static/parties/<party_id>/`:
1. `party.json`:
   ```json
   {
     "id": "party_id",
     "name_he": "שם המפלגה",
     "leader": "שם ראש המפלגה",
     "leader_title": "תואר רשמי",
     "official_website": "https://...",
     "knesset_faction_url": "https://main.knesset.gov.il/...",
     "manifesto_status": "תיאור סטטוס המצע"
   }
   ```
2. `candidates.json`:
   רשימה של כל המועמדים הידועים (מינימום עד מקום 20 או `realistic_cutoff + 5`). לכל מועמד:
   - `position`: מספר ברשימה (1, 2, 3...)
   - `name`: שם המועמד
   - `is_realistic_zone`: בוליאני (האם בטווח הריאלי לפי סקרים אחרונים)
   - `cv`: השכלה (`education`), קריירה אזרחית/צבאית (`career`), שירות ציבורי (`public_service`)
   - `key_votes`: רשימת הצבעות מפתח בכנסת
   - `major_achievements`: הישגים ציבוריים ומקצועיים בולטים
   - `notable_failures_or_controversies`: ביקורות, כשלים או מחלוקות ציבוריות ידועות
3. `manifesto.md`:
   עיקרי המצע הרשמי ומסמכי המדיניות המחייבים של המפלגה.

---

## 🔍 שלב 2: אימות ובקרת איכות של המאגר הסטטי

הפעל את כלי האימות האוטומטי:
```bash
python3 scripts/build_static_kb.py --verify
```
הכלי בודק:
1. קיומם של כל 14 תיקיות המפלגות הזכאיות.
2. תקינות סכמת JSON של `party.json` ו-`candidates.json`.
3. עומק רשימות המועמדים (מוודא שאין רשימות ריקות או חסרות).
4. קיומו ותקינותו של קטלוג הנושאים (`catalog.json`) ומחוון הקריטריונים (`criteria.json`).

---

## 🔄 שלב 3: הפעלת סקריפט סנכרון מהיר (Build All)

במידת הצורך לבנייה מחודשת מהירה או תיקון מרוכז:
```bash
python3 scripts/build_static_kb.py --build-all
```
פקודה זו תסנכרן את רשימת המפלגות מ-`config/parties.yaml`, תמלא את כל קורות החיים המעודכנים של המועמדים, ותריץ אימות מקיף.
