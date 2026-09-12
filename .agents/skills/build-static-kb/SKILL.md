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
המאגר מפריד בצורה מוחלטת בין **מידע סטטי** (קבוע, היסטורי, מצעי מפלגות, רשימות מועמדים רשמיות 1..30+, קורות חיים, הצבעות היסטוריות, הישגים וכישלונות) לבין **מידע דינמי** (סקרי מנדטים עדכניים, אמירות וראיונות שבועיים, וציוני התאמה לפרופילי משתמש).

> ⚠️ **כלל מקור האמת הבלעדי לרשימות מועמדים: ועדת הבחירות המרכזית**  
> חל איסור מוחלט לבסס את רשימות המועמדים על הרכב הכנסת היוצאת (הכנסת ה-25), על ספקולציות תקשורתיות, או על זיכרון מודל.  
> **המקור הרשמי והמחייב היחיד הוא ועדת הבחירות המרכזית לכנסת ה-26**:  
> 🔗 **דף הרשימות והמועמדים הרשמי**: [https://www.gov.il/he/pages/candidates-lists-26](https://www.gov.il/he/pages/candidates-lists-26)  
> בדף זה כל רשימה מהווה קישור ישיר לדף רשימת המועמדים המלאה שהוגשה ואושרה. כל רשימת מועמדים ב-`candidates.json` חייבת להיות מעוגנת ומאומתת מול דף רשמי זה.

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
    │   ├── party.json        # פרטי מפלגה, יו״ר, אתר רשמי, קישור לסיעה בכנסת, קישור רשמי לוועדת הבחירות
    │   ├── candidates.json   # רשימת מועמדים רשמית מועדת הבחירות (1..20+), קו״ח, הישגים, כישלונות, הצבעות
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
- **description**: "Subagent that gathers verified static background data on Israeli political parties from official sources (Central Elections Committee candidates-lists-26, Knesset protocols, and official party platforms)"
- **enable_write_tools**: `true`
- **system_prompt**: קרא מתוך [.agents/skills/build-static-kb/references/static_researcher_prompt.md](references/static_researcher_prompt.md)

### 2. `static_kb_validator`
- **name**: `static_kb_validator`
- **description**: "Subagent that audits static party files, validates candidate rosters strictly against the Central Elections Committee official list (candidates-lists-26), checks schema compliance, and verifies factual sources"
- **enable_write_tools**: `true`
- **system_prompt**: קרא מתוך [.agents/skills/build-static-kb/references/static_validator_prompt.md](references/static_validator_prompt.md)

---

## 🚀 שלב 1: איסוף מקבילי של נתוני מפלגות ומועמדים מהמקור הרשמי

הפעל את סוכני המחקר המקביליים באמצעות `invoke_subagent` בקבוצות לפי גושים או מפלגות בודדות.  
**תהליך המחקר של הסוכן**:
1. **שליפת רשימת המועמדים הרשמית**: הסוכן ניגש לדף הרשמי של ועדת הבחירות המרכזית ב-[https://www.gov.il/he/pages/candidates-lists-26](https://www.gov.il/he/pages/candidates-lists-26), מאתר את הרשימה המתאימה ופותח את הקישור לרשימת המועמדים המלאה.
2. **קביעת סדר ומיקום המועמדים (1..N)**: שמות המועמדים ומיקומם נקבעים במדויק על פי ההגשה הרשמית בוועדת הבחירות.
3. **מחקר עומק קורות חיים (CV Dossiers)**: עבור המועמדים בטווח הריאלי (`is_realistic_zone: true` לפי `config/polls.yaml`), נאסף מידע עובדתי ומאומת מתוך פרוטוקולי הכנסת, מאגרי חקיקה ומידע ביוגרפי רשמי.

כל סוכן מחקר נדרש לייצר עבור המפלגה שלו שלושה קבצים בתוך `data/static/parties/<party_id>/`:
1. `party.json`:
   ```json
   {
     "id": "party_id",
     "name_he": "שם המפלגה הרשמי בבחירות",
     "ballot_letters": "אותיות הרשימה (למשל: מחל, פה, ט, אמת)",
     "leader": "שם ראש המפלגה",
     "leader_title": "תואר רשמי",
     "official_website": "https://...",
     "knesset_faction_url": "https://main.knesset.gov.il/...",
     "official_cec_url": "https://www.gov.il/he/pages/candidates-lists-26#<party>",
     "manifesto_status": "תיאור סטטוס המצע"
   }
   ```
2. `candidates.json`:
   רשימה של כל המועמדים הרשמיים שהוגשו לוועדת הבחירות המרכזית (מינימום עד מקום 20 או `realistic_cutoff + 5`). לכל מועמד:
   - `position`: מספר ברשימה הרשמית (1, 2, 3...)
   - `name`: שם המועמד המדויק כפי שמופיע ברישומי ועדת הבחירות
   - `is_realistic_zone`: בוליאני (האם בטווח הריאלי לפי `config/polls.yaml`)
   - `cv`: השכלה (`education`), קריירה אזרחית/צבאית (`career`), שירות ציבורי (`public_service`)
   - `key_votes`: רשימת הצבעות מפתח בכנסת (חקיקה, אי-אמון, סוגיות ליבה)
   - `major_achievements`: הישגים ציבוריים ומקצועיים בולטים
   - `notable_failures_or_controversies`: ביקורות, כשלים או מחלוקות ציבוריות מתועדות
3. `manifesto.md`:
   עיקרי המצע הרשמי ומסמכי המדיניות המחייבים של המפלגה לקראת הבחירות לכנסת ה-26.

---

## 🔍 שלב 2: אימות ובקרת איכות של המאגר הסטטי מול ועדת הבחירות

הפעל את כלי האימות האוטומטי:
```bash
python3 scripts/build_static_kb.py --verify
```
הכלי בודק:
1. קיומם של כל 14 תיקיות המפלגות הזכאיות.
2. תקינות סכמת JSON של `party.json` ו-`candidates.json` (כולל שדה `official_cec_url`).
3. עומק רשימות המועמדים (מוודא שאין רשימות ריקות או חסרות, ומספר המועמדים עומד בסף `realistic_cutoff + 5`).
4. התאמת שמות המועמדים וסדרם לרשימות המאושרות של ועדת הבחירות המרכזית.
5. קיומו ותקינותו של קטלוג הנושאים (`catalog.json`) ומחוון הקריטריונים (`criteria.json`).

---

## 🔄 שלב 3: הפעלת סקריפט סנכרון מהיר (Build All)

במידת הצורך לבנייה מחודשת מהירה או עדכון מרוכז מתוך קובץ מקור רשמי או מקוון:
```bash
# סנכרון מלא מול מאגר המפלגות הרשמי
python3 scripts/build_static_kb.py --build-all

# לחלופין, טעינת רשימות ישירות מקובץ מקור מעודכן של ועדת הבחירות
python3 scripts/build_static_kb.py --import-cec-source <path_or_url>
```
פקודה זו תסנכרן את רשימת המפלגות מ-`config/parties.yaml`, תעדכן את כל קורות החיים של המועמדים הרשמיים, ותריץ אימות מקיף.
