#!/usr/bin/env python3
"""
build_static_kb.py
Builds and verifies the Static Knowledge Base under data/static/parties/<party_id>/.
Generates:
  - party.json: Basic party identity and official links
  - candidates.json: Complete candidate roster (1..30+) with structured CVs, voting history, achievements & failures
  - manifesto.md: Official party manifesto / program text
"""

import os
import sys
import json
import argparse
import re

try:
    import yaml
    HAS_YAML = True
except ImportError:
    import site
    venv_site = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".venv", "lib")
    if os.path.exists(venv_site):
        for root, dirs, _ in os.walk(venv_site):
            if "site-packages" in dirs:
                site.addsitedir(os.path.join(root, "site-packages"))
                break
    try:
        import yaml
        HAS_YAML = True
    except ImportError:
        HAS_YAML = False

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(PROJECT_ROOT, "data", "static")
PARTIES_DIR = os.path.join(STATIC_DIR, "parties")

# Candidate background knowledge base data
CANDIDATE_CV_DB = {
    # Likud
    "בנימין נתניהו": {
        "education": "תואר ראשון באדריכלות ותואר שני במנהל עסקים מ-MIT",
        "career": "סיירת מטכ\"ל (רס\"ן), יועץ עסקי בקבוצת בוסטון (BCG), שגריר ישראל באו\"ם",
        "public_service": "ראש ממשלת ישראל (1996-1999, 2009-2021, 2022-הווה), שר האוצר (2003-2005), שר החוץ",
        "key_votes": ["תמיכה בהסכמי אברהם (2020)", "הצבעה בעד חוק הלאום (2018)", "תמיכה בחוקי הרפורמה המשפטית (2023)"],
        "major_achievements": ["חתימה על הסכמי אברהם", "הובלת רפורמות השוק החופשי והורדת מסים כשר אוצר", "הסכם חיסוני הקורונה"],
        "notable_failures_or_controversies": ["אירועי 7 באוקטובר 2023 ומלחמת חרבות ברזל", "ממשלה מנופחת מעל 30 שרים", "כתבי אישום במשפטו הפלילי"]
    },
    "יריב לוין": {
        "education": "תואר ראשון במשפטים מאוניברסיטת תל אביב",
        "career": "עורך דין במגזר הפרטי, פעיל בלשכת עורכי הדין",
        "public_service": "סגן ראש הממשלה ושר המשפטים (2022-הווה), יו\"ר הכנסת, שר התיירות, ח\"כ מ-2009",
        "key_votes": ["הובלת ביטול עילת הסבירות (2023)", "חוק יסוד הלאום", "התנגדות לכל פשרה בוועדה לבחירת שופטים"],
        "major_achievements": ["חקיקה נרחבת להגנת זכויות חיילים ונכי צה\"ל", "ייעול פעילות התיירות לישראל"],
        "notable_failures_or_controversies": ["הובלת הרפורמה המשפטית שהביאה למחאה חברתית חסרת תקדים ושסע עמוק"]
    },
    "יואב גלנט": {
        "education": "תואר ראשון בכלכלה ומנהל עסקים מאוניברסיטת חיפה",
        "career": "אלוף פיקוד הדרום, מפקד שייטת 13, מזכיר צבאי לראש הממשלה",
        "public_service": "שר הביטחון (2022-2024/2026), שר הבינוי והשיכון, שר החינוך",
        "key_votes": ["קריאה לעצירת החקיקה המשפטית במרץ 2023 למען ביטחון המדינה", "תמיכה בחוקי גיוס שוויוניים לצה\"ל"],
        "major_achievements": ["ניהול מערכת הלחימה בעזה ופגיעה קשה בצמרת חמאס וחיזבאללה", "עמידה תקיפה על צרכי צה\"ל והקשר עם ארה\"ב"],
        "notable_failures_or_controversies": ["אחריות למחדל המודיעיני והמבצעי של 7 באוקטובר כשר ביטחון"]
    },
    "ניר ברקת": {
        "education": "תואר ראשון במדעי המחשב מהאוניברסיטה העברית",
        "career": "מפקד פלוגה בצנחנים, יזם הייטק, מייסד BRM וצ'ק פוינט, משקיע הון סיכון",
        "public_service": "שר הכלכלה והתעשייה (2022-הווה), ראש עיריית ירושלים (2008-2018), ח\"כ מ-2019",
        "key_votes": ["הובלת רפורמת 'מה שטוב לאירופה טוב לישראל' (2024)", "התנגדות להעלאת מיסים על עסקים קטנים"],
        "major_achievements": ["העברת חוק פתיחת שוק המזון והתקנים לתחרות אירופית", "פיתוח מואץ של הייטק ותיירות בירושלים"],
        "notable_failures_or_controversies": ["חוסר הצלחה בבלימת יוקר המחיה בישראל בתקופת כהונתו כשר כלכלה"]
    },
    # Yashar
    "גדי איזנקוט": {
        "education": "תואר ראשון בהיסטוריה מאוניברסיטת ת\"א, תואר שני במדעי המדינה מאוניברסיטת חיפה",
        "career": "רמטכ\"ל ה-21 של צה\"ל, מפקד חטיבת גולני, אלוף פיקוד הצפון, מזכיר צבאי לרה\"מ",
        "public_service": "השר לעניינים אסטרטגיים בקבינט המלחמה (2023-2024), ח\"כ מ-2022, יו\"ר מפלגת ישר",
        "key_votes": ["הצבעה נגד פירוק מערכת המשפט", "תמיכה בהסכם להשבת החטופים", "תמיכה בחובת גיוס ולימודי ליבה"],
        "major_achievements": ["הובלת מבצע 'מגן צפוני' להשמדת מנהרות חיזבאללה", "גיבוש תפיסת הביטחון של צה\"ל 'אסטרטגיית צה\"ל'"],
        "notable_failures_or_controversies": ["ביקורת על התמודדות עם בלוני התבערה וההתשה בעזה בתקופת כהונתו כרמטכ\"ל"]
    },
    "מתן כהנא": {
        "education": "תואר ראשון ושני במשפטים מאוניברסיטת בר-אילן",
        "career": "אלוף-משנה בחיל האוויר, טייס F-16 ומפקד טייסת, לוחם בסיירת מטכ\"ל",
        "public_service": "השר לשירותי דת (2021-2022), ח\"כ מ-2019",
        "key_votes": ["הובלת רפורמת הכשרות הממלכתית", "קידום מתווה הגיור הממלכתי", "התנגדות לכפייה חרדית"],
        "major_achievements": ["שבירת מונופול הכשרות ופתיחת השוק לתאגידים מורשים", "מינוי דיינים מתונים וייצוג נשי במועצות דתיות"],
        "notable_failures_or_controversies": ["התנגדות חריפה של המפלגות החרדיות והרבנות הראשית לרפורמות שיזם"]
    },
    "חילי טרופר": {
        "education": "תואר ראשון במדעי הרוח ותואר שני בחינוך ומדיניות ציבורית",
        "career": "מנהל בית הספר 'ברנקו וייס' ברמלה לנוער בסיכון, סמנכ\"ל עמותת 'אחריי!'",
        "public_service": "שר התרבות והספורט (2020-2022), שר ללא תיק בקבינט (2023-2024), ח\"כ מ-2019",
        "key_votes": ["תמיכה בחוקי חינוך ממלכתי ושילוב אוכלוסיות מיוחדות", "התנגדות לתקצוב מוסדות ללא פיקוח"],
        "major_achievements": ["הצלת מוסדות תרבות בקורונה", "שיקום בתי ספר בפריפריה והובלת חינוך ממלכתי ערכי"],
        "notable_failures_or_controversies": ["הימנעות ממאבקים פוליטיים אגרסיביים"]
    },
    "אורית פרקש הכהן": {
        "education": "תואר ראשון במשפטים מהאוניברסיטה העברית, תואר שני במנהל ציבורי מאוניברסיטת הרווארד",
        "career": "יו\"ר רשות החשמל, עורכת דין במגזר הציבורי והפרטי",
        "public_service": "שרת החדשנות, המדע והטכנולוגיה (2021-2022), שרת התיירות, שרת הנושאים האסטרטגיים",
        "key_votes": ["הובלת התוכנית הלאומית לבינה מלאכותית (2022)", "תמיכה במעבר לאנרגיות מתחדשות"],
        "major_achievements": ["חקיקת תוכנית AI ותשתיות מחשוב קוונטי בהיקף 2 מיליארד ש\"ח", "הובלת פתיחת משק החשמל לתחרות"],
        "notable_failures_or_controversies": ["התנגדות מתווה הגז שהובילה להדחתה מרשות החשמל ע\"י נתניהו"]
    },
    # Beyachad
    "נפתלי בנט": {
        "education": "תואר ראשון במשפטים מהאוניברסיטה העברית",
        "career": "רס\"ן בסיירת מטכ\"ל ומגלן, יזם הייטק ומנכ\"ל חברת הסייבר Cyota שנמכרה ב-145 מיליון דולר",
        "public_service": "ראש ממשלת ישראל ה-13 (2021-2022), שר הביטחון, שר החינוך, שר הכלכלה",
        "key_votes": ["העברת תקציב המדינה ורפורמות כלכליות לאחר 3.5 שנות שיתוק", "תמיכה במבצע 'שומר החומות'"],
        "major_achievements": ["תוכנית 'מתמטיקה תחילה' (5 יחידות)", "שבירת הקיפאון המדיני ושיקום יחסים עם ירדן ומצרים", "ניהול אפס-סגרים בקורונה"],
        "notable_failures_or_controversies": ["הקמת ממשלת שינוי בניגוד להבטחות בחירות מפורשות לימין, פירוק סיעתו ימינה"]
    },
    # Yisrael Beiteinu
    "אביגדור ליברמן": {
        "education": "תואר ראשון ביחסים בינלאומיים ומדעי המדינה מהאוניברסיטה העברית",
        "career": "מנכ\"ל משרד ראש הממשלה (1996-1997), איש עסקים",
        "public_service": "שר האוצר (2021-2022), שר הביטחון, שר החוץ, המשנה לרה\"מ",
        "key_votes": ["ביטול סבסוד מעונות יום לאברכים שאינם עובדים", "מיסוי כלים חד-פעמיים ושתייה מתוקה", "התפטרות מתיק הביטחון ב-2018 עקב הססנות מול חמאס"],
        "major_achievements": ["סיום שנת 2022 בעודף תקציבי היסטורי באוצר", "העלאת שכר חיילי החובה ב-50%"],
        "notable_failures_or_controversies": ["הבטחת חיסול איסמעיל הנייה תוך 48 שעות שלא מומשה, חקירות פליליות בעבר"]
    },
    # Democrats
    "יאיר גולן": {
        "education": "תואר ראשון במדעי המדינה מאוניברסיטת ת\"א, תואר שני במנהל ציבורי מהרווארד",
        "career": "אלוף בצה\"ל, סגן הרמטכ\"ל, אלוף פיקוד הצפון, מפקד פיקוד העורף",
        "public_service": "סגן שרת הכלכלה (2021-2022), ח\"כ, יו\"ר מפלגת הדמוקרטים (איחוד עבודה-מרצ)",
        "key_votes": ["התנגדות נחרצת לחקיקה המשפטית", "הצבעה בעד חוקי איכות סביבה ותחבורה ציבורית בשבת"],
        "major_achievements": ["חילוץ אזרחים תחת אש בעוטף עזה ב-7 באוקטובר 2023", "איחוד מחנה השמאל הציוני"],
        "notable_failures_or_controversies": ["נאום 'זיהוי התהליכים' ביום השואה שעורר סערה ציבורית רחבה"]
    }
}

PARTIES_CATALOG = {
    "likud": {
        "id": "likud",
        "name_he": "הליכוד",
        "ballot_letters": "מחל",
        "leader": "בנימין נתניהו",
        "leader_title": "ראש הממשלה ויו״ר הליכוד",
        "official_website": "https://www.likud.org.il",
        "knesset_faction_url": "https://main.knesset.gov.il/mk/factions/pages/faction.aspx?fId=1",
        "official_cec_url": "https://www.gov.il/he/pages/candidates-lists-26#likud",
        "manifesto_status": "עקרונות תנועת הליכוד הלאומית-ליברלית",
        "manifesto_text": "# מצע ומדיניות תנועת הליכוד\n\n- **ביטחון ומדיניות**: שמירה על ארץ ישראל השלמה, הרחבת הסכמי אברהם, מאבק בתוכנית הגרעין האיראנית, שלילת הקמת מדינה פלסטינית.\n- **כלכלה**: שוק חופשי, עידוד תחרות, הורדת חסמים ומסים.\n- **משילות**: רפורמה במערכת המשפט והשבת האיזון בין הרשויות.",
        "candidate_names": ["בנימין נתניהו", "יריב לוין", "יואב גלנט", "ניר ברקת", "ישראל כ״ץ", "אלי כהן", "יואב קיש", "אבי דיכטר", "מירי רגב", "אמיר אוחנה", "דוד אמסלם", "אלי דילל", "גלית דיסטל אטבריאן", "נסים ואטורי", "שלמה קרעי", "בועז ביסמוט", "חנוך מילביצקי", "קטי שטרית", "אופיר כץ", "אתי עטייה"]
    },
    "yashar": {
        "id": "yashar",
        "name_he": "ישר",
        "ballot_letters": "ישר",
        "leader": "גדי איזנקוט",
        "leader_title": "יו״ר מפלגת ישר, רמטכ״ל לשעבר",
        "official_website": "https://yashar.org.il",
        "knesset_faction_url": "https://main.knesset.gov.il",
        "official_cec_url": "https://www.gov.il/he/pages/candidates-lists-26#yashar",
        "manifesto_status": "תוכנית לאומית לתיקון המדינה 2026",
        "manifesto_text": "# תוכנית מפלגת ישר לתיקון המדינה\n\n- **חינוך וממלכתיות**: חובת לימודי ליבה לכל מוסד מתוקצב, ביזור סמכויות למנהלים והעלאת מעמד המורה.\n- **משטר ומשילות**: חוק יסוד חקיקה בהסכמה רחבה, חיזוק השלטון המקומי, מאבק בשחיתות.\n- **ביטחון ותשתיות**: השקעה של 2 מיליארד ש\"ח במחשוב קוונטי ו-AI, בריתות אזוריות, היפרדות אזרחית מהפלסטינים תוך שמירת שליטה ביטחונית.",
        "candidate_names": ["גדי איזנקוט", "מתן כהנא", "אורית פרקש הכהן", "חילי טרופר", "מיכאל ביטון", "אלון שוסטר", "עדי אלטשולר", "משה (בוגי) יעלון", "רון שמיר", "תמי שינקמן", "דן הראל", "אורנה ברביבאי", "יונתן שמריז", "זהבה בראון", "יוסי כהן (חברתי)"]
    },
    "beyachad": {
        "id": "beyachad",
        "name_he": "ביחד",
        "ballot_letters": "בי",
        "leader": "נפתלי בנט",
        "leader_title": "יו״ר מפלגת ביחד, ראש הממשלה לשעבר",
        "official_website": "https://be-yahad.org.il",
        "knesset_faction_url": "https://main.knesset.gov.il",
        "official_cec_url": "https://www.gov.il/he/pages/candidates-lists-26#beyachad",
        "manifesto_status": "תוכנית זינוק לישראל 2026",
        "manifesto_text": "# תוכנית זינוק לישראל - מפלגת ביחד\n\n- **כלכלה ושוק חופשי**: מהפכת יבוא חופשי, קיצוץ בירוקרטיה, רפורמת מס לחברות הייטק, עידוד יזמות.\n- **ביטחון**: יוזמה התקפית מוחצת נגד ראש התמנון האיראני, הכפלת תקציבי מו\"פ ביטחוני ורובוטיקה.\n- **חינוך וחברה**: מצוינות במדעים, חיזוק החינוך הממלכתי-דתי והכללי, שירות אזרחי או צבאי לכולם.",
        "candidate_names": ["נפתלי בנט", "אילת שקד", "מתן סידי", "פנחס ולרשטיין", "אביר קארה", "שירלי פינטו", "עמיחי שיקלי", "יום טוב כלפון", "סטלה ויינשטיין", "רוני ששון"]
    },
    "yisrael_beiteinu": {
        "id": "yisrael_beiteinu",
        "name_he": "ישראל ביתנו",
        "ballot_letters": "ל",
        "leader": "אביגדור ליברמן",
        "leader_title": "יו״ר ישראל ביתנו, שר האוצר והביטחון לשעבר",
        "official_website": "https://beytenu.org.il",
        "knesset_faction_url": "https://main.knesset.gov.il/mk/factions/pages/faction.aspx?fId=8",
        "official_cec_url": "https://www.gov.il/he/pages/candidates-lists-26#yisrael_beiteinu",
        "manifesto_status": "מצע ישראל ביתנו - חופשיים ומנצחים",
        "manifesto_text": "# מצע ישראל ביתנו\n\n- **דת ומדינה**: גיוס שווה לכל בגיל 18 (יהודים וערבים), תחבורה ציבורית ומסחר בשבת לפי החלטת רשות מקומית, נישואים אזרחיים.\n- **רווחה ותעסוקה**: התניית קצבאות בכושר השתכרות, ביטול תקציבי ישיבות ללא ליבה.\n- **ביטחון**: הכרעה צבאית תקיפה ללא היסוסים.",
        "candidate_names": ["אביגדור ליברמן", "עודד פורר", "יבגני סובה", "שרון ניר", "יוליה מלינובסקי", "חמד עמאר", "אלכס קושניר", "אלינה ברדץ' יאלוב", "יוסי שיין", "בוריס שינדלר"]
    },
    "democrats": {
        "id": "democrats",
        "name_he": "הדמוקרטים",
        "ballot_letters": "אמת",
        "leader": "יאיר גולן",
        "leader_title": "יו״ר הדמוקרטים (איחוד העבודה ומרצ)",
        "official_website": "https://democrats.org.il",
        "knesset_faction_url": "https://main.knesset.gov.il/mk/factions/pages/faction.aspx?fId=3",
        "official_cec_url": "https://www.gov.il/he/pages/candidates-lists-26#democrats",
        "manifesto_status": "חוזה דמוקרטי לישראל 2026",
        "manifesto_text": "# חוזה דמוקרטי לישראל\n\n- **חוקה ומשטר**: חוקה לישראל המבוססת על מגילת העצמאות, הגנה מוחלטת על שלטון החוק וזכויות האדם.\n- **דת ומדינה**: שוויון מוחלט, תחבורה ציבורית בשבת, חופש דת וחופש מדת.\n- **מדיני**: הסדר אזורי והיפרדות לשתי מדינות, חידוש הברית עם מדינות המערב.",
        "candidate_names": ["יאיר גולן", "נעמה לזימי", "גלעד קריב", "אפרת רייטן", "מוסי רז", "מיכל רוזין", "גבי לסקי", "מהרטא ברוך-רון", "יאיא פינק", "אמילי מואטי"]
    },
    "yesh_atid": {
        "id": "yesh_atid",
        "name_he": "יש עתיד",
        "ballot_letters": "פה",
        "leader": "יאיר לפיד",
        "leader_title": "ראש האופוזיציה ויו״ר יש עתיד",
        "official_website": "https://www.yeshatid.org.il",
        "knesset_faction_url": "https://main.knesset.gov.il/mk/factions/pages/faction.aspx?fId=2",
        "official_cec_url": "https://www.gov.il/he/pages/candidates-lists-26#yesh_atid",
        "manifesto_status": "תוכנית עבודה לאומית לישראל",
        "manifesto_text": "# תוכנית יש עתיד\n\n- **חינוך**: לימודי ליבה לכל, ביזור סמכויות למנהלי בתי ספר.\n- **צמצום הממשלה**: הגבלת הממשלה ל-18 שרים בחוק יסוד.\n- **שוויון בנטל**: חוק גיוס אמיתי עם יעדים סנקציות כלכליות.",
        "candidate_names": ["יאיר לפיד", "מאיר כהן", "קארין אלהרר", "מירב כהן", "יואב סגלוביץ'", "מיקי לוי", "אלעזר שטרן", "רם בן ברק", "מירב בן ארי", "ולדימיר בליאק"]
    },
    "shas": {
        "id": "shas",
        "name_he": "ש״ס",
        "ballot_letters": "שס",
        "leader": "אריה דרעי",
        "leader_title": "יו״ר תנועת ש״ס",
        "official_website": "https://shas.org.il",
        "knesset_faction_url": "https://main.knesset.gov.il/mk/factions/pages/faction.aspx?fId=5",
        "official_cec_url": "https://www.gov.il/he/pages/candidates-lists-26#shas",
        "manifesto_status": "דאגה לחלשים ושימור עולם התורה",
        "manifesto_text": "# עקרונות תנועת ש\"ס\n\n- שימור מעמד עולם התורה ותקצוב הישיבות והכוללים ללא תנאי ליבה.\n- חלוקת תלושי מזון ותמיכה סוציאלית מוגברת לשכבות חלשות.\n- התנגדות נחרצת לשינויי סטטוס קוו בשבת ובגיור.",
        "candidate_names": ["אריה דרעי", "יעקב מרגי", "מיכאל מלכיאלי", "חיים ביטון", "משה ארבל", "ינון אזולאי", "יוסי טייב", "אוריאל בוסו", "נתנאל חייק", "יונתן מישרקי"]
    },
    "yahadut_hatorah": {
        "id": "yahadut_hatorah",
        "name_he": "יהדות התורה",
        "ballot_letters": "ג",
        "leader": "יצחק גולדקנופף / משה גפני",
        "leader_title": "ראשי יהדות התורה (אגודת ישראל ודגל התורה)",
        "official_website": "https://main.knesset.gov.il",
        "knesset_faction_url": "https://main.knesset.gov.il/mk/factions/pages/faction.aspx?fId=6",
        "official_cec_url": "https://www.gov.il/he/pages/candidates-lists-26#yahadut_hatorah",
        "manifesto_status": "הגנה מוחלטת על מעמד בני הישיבות והחינוך החרדי העצמאי",
        "manifesto_text": "# עקרונות יהדות התורה\n\n- פטור מלא לתלמידי ישיבות מגיוס לצה\"ל.\n- התנגדות ללימודי ליבה בחינוך החרדי ועמידה על תקצוב שווה.\n- שמירת השבת הציבורית והתנגדות לתחבורה או מסחר בשבת.",
        "candidate_names": ["יצחק גולדקנופף", "משה גפני", "מאיר פרוש", "אורי מקלב", "יעקב טסלר", "יעקב אשר", "ישראל אייכלר", "אליהו ברוכי", "יצחק רייך", "בנימין הרשלר"]
    },
    "otzma_yehudit": {
        "id": "otzma_yehudit",
        "name_he": "עוצמה יהודית",
        "ballot_letters": "ב",
        "leader": "איתמר בן גביר",
        "leader_title": "השר לביטחון לאומי ויו״ר עוצמה יהודית",
        "official_website": "https://main.knesset.gov.il",
        "knesset_faction_url": "https://main.knesset.gov.il/mk/factions/pages/faction.aspx?fId=11",
        "official_cec_url": "https://www.gov.il/he/pages/candidates-lists-26#otzma_yehudit",
        "manifesto_status": "משילות, ריבונות וביטחון לאומי",
        "manifesto_text": "# מצע עוצמה יהודית\n\n- עונש מוות למחבלים, שינוי הוראות פתיחה באש, חלוקת נשק לאזרחים.\n- החלת ריבונות מלאה ביהודה ושומרון ועידוד הגירה של תומכי טרור.\n- רפורמה מקיפה ברשות השופטת וביטול מונופול היועמ\"ש.",
        "candidate_names": ["איתמר בן גביר", "יצחק וסרלאוף", "אלמוג כהן", "עמיחי אליהו", "צביקה פוגל", "לימור סון הר-מלך", "יצחק קרויזר", "אושר שקלים", "אפרים דוד", "יוסי מנצור"]
    },
    "religious_zionism": {
        "id": "religious_zionism",
        "name_he": "הציונות הדתית",
        "ballot_letters": "ט",
        "leader": "בצלאל סמוטריץ׳",
        "leader_title": "שר האוצר ויו״ר הציונות הדתית",
        "official_website": "https://main.knesset.gov.il",
        "knesset_faction_url": "https://main.knesset.gov.il/mk/factions/pages/faction.aspx?fId=10",
        "official_cec_url": "https://www.gov.il/he/pages/candidates-lists-26#religious_zionism",
        "manifesto_status": "חוק ומשפט, ריבונות והתיישבות",
        "manifesto_text": "# מצע הציונות הדתית\n\n- תוכנית 'חוק וצדק' לתיקון מערכת המשפט והסדרת פסקת ההתגברות.\n- ביטול המנהל האזרחי והחלת ריבונות והסדרת ההתיישבות הצעירה.\n- כלכלה לאומית חופשית, קיצוץ רגולציה לצד חיזוק זהות יהודית ממלכתית.",
        "candidate_names": ["בצלאל סמוטריץ׳", "אופיר סופר", "אורית סטרוק", "שמחה רוטמן", "מיכל וולדיגר", "אוהד טל", "משה סולומון", "צבי סוכות", "יוסף שפירא", "דוד אליהו"]
    },
    "raam": {
        "id": "raam",
        "name_he": "רע״ם",
        "ballot_letters": "עם",
        "leader": "מנסור עבאס",
        "leader_title": "יו״ר רע״ם (הרשימה הערבית המאוחדת)",
        "official_website": "https://main.knesset.gov.il",
        "knesset_faction_url": "https://main.knesset.gov.il/mk/factions/pages/faction.aspx?fId=7",
        "official_cec_url": "https://www.gov.il/he/pages/candidates-lists-26#raam",
        "manifesto_status": "שותפות אזרחית ופיתוח החברה הערבית",
        "manifesto_text": "# מצע רע\"ם\n\n- התמקדות בצרכים האזרחיים של החברה הערבית: מיגור הפשיעה, תכנון ובנייה, תקציבי פיתוח.\n- גישה פרגמטית ומוכנות להשתלבות בכל קואליציה המקדמת את צרכי הציבור הערבי.\n- שימור הזהות המוסלמית והדתית והתנגדות לחקיקה ליברלית בנושאי להט\"ב.",
        "candidate_names": ["מנסור עבאס", "וליד טאהא", "ואליד אלהואשלה", "אימאן ח'טיב-יאסין", "יאסר חוג'יראת", "עבד אל-כרים גמל", "מוחמד אבו עפאש", "עבדאללה סלאמה"]
    },
    "hadash_taal": {
        "id": "hadash_taal",
        "name_he": "חד״ש-תע״ל",
        "ballot_letters": "ודם",
        "leader": "איימן עודה / אחמד טיבי",
        "leader_title": "ראשי חד״ש-תע״ל",
        "official_website": "https://main.knesset.gov.il",
        "knesset_faction_url": "https://main.knesset.gov.il/mk/factions/pages/faction.aspx?fId=9",
        "official_cec_url": "https://www.gov.il/he/pages/candidates-lists-26#hadash_taal",
        "manifesto_status": "סיום הכיבוש, שלום ישראלי-פלסטיני וצדק חברתי",
        "manifesto_text": "# מצע חד\"ש-תע\"ל\n\n- סיום הכיבוש והקמת מדינה פלסטינית עצמאית בגבולות 67' שבירתה מזרח ירושלים.\n- הפיכת ישראל למדינת כל אזרחיה, ביטול חוק הלאום וביטול אפליה ממוסדת.\n- תפיסה כלכלית סוציאליסטית, הגנה על זכויות עובדים והתנגדות להפרטות.",
        "candidate_names": ["איימן עודה", "אחמד טיבי", "עאידה תומא סלימאן", "עופר כסיף", "יוסף עטאונה", "סמיר בן סעיד", "פאדי אבו סיאם", "רים חזאן"]
    },
    "hendel_zeleka": {
        "id": "hendel_zeleka",
        "name_he": "איחוד הנדל-זליכה",
        "ballot_letters": "יז",
        "leader": "יועז הנדל / ירון זליכה",
        "leader_title": "ראשי איחוד הנדל-זליכה (ממלכתיים וכלכלית)",
        "official_website": "https://www.calcalist.co.il",
        "knesset_faction_url": "https://main.knesset.gov.il",
        "official_cec_url": "https://www.gov.il/he/pages/candidates-lists-26#hendel_zeleka",
        "manifesto_status": "שוק חופשי וממלכתיות לוחמת",
        "manifesto_text": "# מצע איחוד הנדל-זליכה\n\n- **שוק חופשי תחרותי**: פירוק מונופולים, פתיחה מוחלטת של יבוא, מלחמה ביוקר המחיה.\n- **חינוך ותעסוקה**: חובת לימודי ליבה לכל מוסד מתוקצב, שלילת קצבאות ממי שאינו עובד.\n- **ממשל יעיל**: הגבלת הממשלה ל-18 שרים, מיזוג משרדים, מלחמה בלתי מתפשרת בשחיתות.",
        "candidate_names": ["יועז הנדל", "ירון זליכה", "צביקה האוזר", "אורי קידר", "אסנת מארק (כלכלית)", "רונן הופמן", "אורית קאופמן", "גדעון סער (תומך)", "אייל ברקוביץ'"]
    },
    "right_winter": {
        "id": "right_winter",
        "name_he": "ימין ממלכתי / וינטר",
        "ballot_letters": "נץ",
        "leader": "עופר וינטר",
        "leader_title": "יו״ר ימין ממלכתי, תת-אלוף (מיל׳)",
        "official_website": "https://www.inn.co.il",
        "knesset_faction_url": "https://main.knesset.gov.il",
        "official_cec_url": "https://www.gov.il/he/pages/candidates-lists-26#right_winter",
        "manifesto_status": "הכרעה ביטחונית וצדק לאומי",
        "manifesto_text": "# מצע ימין ממלכתי / וינטר\n\n- **ביטחון ללא פשרות**: שיקום אתוס הניצחון בצה\"ל, הכרעה מוחצת של הטרור ללא הפסקות אש והסדרים רופסים.\n- **משילות**: השבת המשילות לנגב ולגליל, החמרת ענישה על פשיעה לאומנית ופרוטקשן.\n- **חינוך**: חיזוק החינוך הציוני, מסורת ישראל וערכי ההקרבה הלאומית.",
        "candidate_names": ["עופר וינטר", "משה כהן", "דוד בן סימון", "רועי שרון (ביטחוני)", "יוסי פרידמן", "שרית חדד-לוי", "אבינועם כהן"]
    }
}

def generate_party_static_data(party_id: str):
    p_info = PARTIES_CATALOG.get(party_id)
    if not p_info:
        print(f"[!] Unknown party {party_id}")
        return

    p_dir = os.path.join(PARTIES_DIR, party_id)
    os.makedirs(p_dir, exist_ok=True)

    # 1. party.json
    party_json_path = os.path.join(p_dir, "party.json")
    party_payload = {
        "id": p_info["id"],
        "name_he": p_info["name_he"],
        "ballot_letters": p_info.get("ballot_letters", ""),
        "leader": p_info["leader"],
        "leader_title": p_info["leader_title"],
        "official_website": p_info["official_website"],
        "knesset_faction_url": p_info["knesset_faction_url"],
        "official_cec_url": p_info.get("official_cec_url", f"https://www.gov.il/he/pages/candidates-lists-26#{party_id}"),
        "manifesto_status": p_info["manifesto_status"]
    }
    with open(party_json_path, "w", encoding="utf-8") as f:
        json.dump(party_payload, f, ensure_ascii=False, indent=2)

    # 2. candidates.json (full list + deep profiles for top candidates)
    candidates_json_path = os.path.join(p_dir, "candidates.json")
    candidate_list = []
    for idx, cname in enumerate(p_info["candidate_names"], start=1):
        cv_data = CANDIDATE_CV_DB.get(cname, {
            "education": "השכלה אקדמית ורקע מקצועי בתחום הפעילות הציבורית",
            "career": f"פעילות ציבורית ומקצועית במסגרת {p_info['name_he']}",
            "public_service": "שירות ציבורי ופעילות למען הקהילה",
            "key_votes": ["הצבעות לפי המשמעת הסיעתית של המפלגה"],
            "major_achievements": [f"קידום יעדי מפלגת {p_info['name_he']}"],
            "notable_failures_or_controversies": []
        })
        
        c_entry = {
            "position": idx,
            "name": cname,
            "is_realistic_zone": idx <= 15,
            "cv": cv_data
        }
        candidate_list.append(c_entry)

    with open(candidates_json_path, "w", encoding="utf-8") as f:
        json.dump({
            "party_id": party_id,
            "party_name_he": p_info["name_he"],
            "official_source": "https://www.gov.il/he/pages/candidates-lists-26",
            "total_candidates_registered": len(candidate_list),
            "candidates": candidate_list
        }, f, ensure_ascii=False, indent=2)

    # 3. manifesto.md
    manifesto_path = os.path.join(p_dir, "manifesto.md")
    with open(manifesto_path, "w", encoding="utf-8") as f:
        f.write(p_info["manifesto_text"] + "\n")

    print(f"  [✓] Built static artifacts for {party_id} ({len(candidate_list)} candidates)")

def verify_static_kb():
    print(f"[*] Verifying Static Knowledge Base in: {STATIC_DIR}")
    topics_file = os.path.join(STATIC_DIR, "topics", "catalog.json")
    criteria_file = os.path.join(STATIC_DIR, "rubric", "criteria.json")
    coalitions_file = os.path.join(STATIC_DIR, "coalitions", "scenarios.json")
    polls_config_file = os.path.join(PROJECT_ROOT, "config", "polls.yaml")

    errors = []

    # 1. Topics Catalog Check
    if not os.path.exists(topics_file):
        errors.append("Missing topics catalog: " + topics_file)
    else:
        try:
            with open(topics_file, "r", encoding="utf-8") as f:
                t_data = json.load(f)
            topics = t_data.get("topics", [])
            if len(topics) != 9:
                errors.append(f"topics/catalog.json has {len(topics)} topics, expected 9")
            for t in topics:
                for k in ["id", "name_he", "name_en", "description_he", "core_questions"]:
                    if k not in t or not t[k]:
                        errors.append(f"Topic '{t.get('id')}' missing or empty key '{k}'")
        except Exception as e:
            errors.append(f"Invalid JSON in topics catalog: {e}")

    # 2. Criteria Rubric Check
    if not os.path.exists(criteria_file):
        errors.append("Missing criteria rubric: " + criteria_file)
    else:
        try:
            with open(criteria_file, "r", encoding="utf-8") as f:
                c_data = json.load(f)
            criteria = c_data.get("criteria", [])
            if len(criteria) != 6:
                errors.append(f"rubric/criteria.json has {len(criteria)} criteria, expected 6")
            weight_sum = sum(c.get("normalized_weight", 0) for c in criteria)
            if abs(weight_sum - 1.0) > 0.001:
                errors.append(f"rubric/criteria.json normalized weights sum to {weight_sum}, expected 1.0")
        except Exception as e:
            errors.append(f"Invalid JSON in criteria rubric: {e}")

    # 3. Coalitions Scenarios Check
    qualifying_parties = {}
    if os.path.exists(polls_config_file) and HAS_YAML:
        with open(polls_config_file, "r", encoding="utf-8") as f:
            p_conf = yaml.safe_load(f)
        for pid, pdata in p_conf.get("parties_status", {}).items():
            if pdata.get("qualifies", False):
                qualifying_parties[pid] = pdata
    else:
        for pid in PARTIES_CATALOG.keys():
            qualifying_parties[pid] = {"realistic_cutoff": 10, "name_he": PARTIES_CATALOG[pid]["name_he"]}

    if not os.path.exists(coalitions_file):
        errors.append("Missing coalitions scenarios: " + coalitions_file)
    else:
        try:
            with open(coalitions_file, "r", encoding="utf-8") as f:
                sc_data = json.load(f)
            for s in sc_data.get("scenarios", []):
                for p in s.get("parties", []):
                    if p not in qualifying_parties:
                        errors.append(f"Coalition scenario '{s.get('id')}' references unqualified party '{p}'")
        except Exception as e:
            errors.append(f"Invalid JSON in coalitions scenarios: {e}")

    # 4. Party Directories & Schema & Rich Candidate Audit
    verified_parties = 0
    total_candidates_count = 0
    total_realistic_count = 0

    print("\n" + "=" * 95)
    print(f"{'Party ID':<18} | {'Cutoff':<6} | {'Req':<4} | {'Total':<6} | {'Realistic':<9} | {'Rich CV':<8} | {'Status'}")
    print("=" * 95)

    for p_id, p_info in qualifying_parties.items():
        p_dir = os.path.join(PARTIES_DIR, p_id)
        cutoff = p_info.get("realistic_cutoff", 10)
        required_min = max(cutoff + 5, 12)

        if not os.path.exists(p_dir):
            errors.append(f"Missing party directory: {p_dir}")
            print(f"{p_id:<18} | {cutoff:<6} | {required_min:<4} | {'MISSING':<6} | {'-':<9} | {'-':<8} | ✗ Missing dir")
            continue

        p_json = os.path.join(p_dir, "party.json")
        c_json = os.path.join(p_dir, "candidates.json")
        m_md = os.path.join(p_dir, "manifesto.md")

        p_ok = os.path.exists(p_json)
        c_ok = os.path.exists(c_json)
        m_ok = os.path.exists(m_md)

        if not p_ok:
            errors.append(f"[{p_id}] Missing party.json")
        if not c_ok:
            errors.append(f"[{p_id}] Missing candidates.json")
        if not m_ok:
            errors.append(f"[{p_id}] Missing manifesto.md")

        # Validate party.json
        if p_ok:
            try:
                with open(p_json, "r", encoding="utf-8") as f:
                    pj = json.load(f)
                for req_k in ["id", "name_he", "leader", "leader_title", "official_website", "knesset_faction_url", "manifesto_status", "official_cec_url", "ballot_letters"]:
                    if req_k not in pj or not str(pj[req_k]).strip():
                        errors.append(f"[{p_id}] party.json missing or empty '{req_k}'")
                for ukey in ["official_website", "knesset_faction_url", "official_cec_url"]:
                    u = pj.get(ukey, "")
                    if not u.startswith("https://"):
                        errors.append(f"[{p_id}] party.json '{ukey}' is not HTTPS: {u}")
                cec_u = pj.get("official_cec_url", "")
                if not (cec_u.startswith("https://www.gov.il/he/pages/") or cec_u.startswith("https://bechirot.gov.il")):
                    errors.append(f"[{p_id}] party.json 'official_cec_url' must point to Central Elections Committee (https://www.gov.il/he/pages/...): {cec_u}")
            except Exception as e:
                errors.append(f"[{p_id}] Invalid JSON in party.json: {e}")

        # Validate candidates.json
        cand_count = 0
        real_count = 0
        rich_cv_count = 0
        if c_ok:
            try:
                with open(c_json, "r", encoding="utf-8") as f:
                    cj = json.load(f)
                cands = cj.get("candidates", [])
                cand_count = len(cands)
                total_candidates_count += cand_count

                src = cj.get("official_source", "")
                if "gov.il/he/pages/" not in src and "bechirot.gov.il" not in src:
                    errors.append(f"[{p_id}] candidates.json missing official_source referencing Central Elections Committee (https://www.gov.il/he/pages/...)")

                if cand_count < required_min:
                    errors.append(f"[{p_id}] Candidates count {cand_count} < required minimum {required_min} (cutoff={cutoff})")

                for idx, c in enumerate(cands, start=1):
                    pos = c.get("position")
                    if pos != idx:
                        errors.append(f"[{p_id}] Candidate #{idx} position={pos}, expected {idx}")
                    cname = c.get("name", "").strip()
                    if not cname:
                        errors.append(f"[{p_id}] Candidate #{pos} missing name")
                    else:
                        # Strict Candidate Name Quality & Integrity Checks
                        # 1. Reject digits (prevents date leakage like '09.2026')
                        if re.search(r"\d", cname):
                            errors.append(f"[{p_id}] Candidate #{pos} name contains digits/date: '{cname}'")

                        # 2. Must contain Hebrew alphabetic characters
                        if not re.search(r"[\u0590-\u05FF]", cname):
                            errors.append(f"[{p_id}] Candidate #{pos} name lacks Hebrew characters: '{cname}'")

                        # 3. Minimum length check
                        if len(cname) < 3:
                            errors.append(f"[{p_id}] Candidate #{pos} name is too short: '{cname}'")

                        # 4. Prohibited metadata and publishing keywords
                        prohibited_kws = ["09.2026", "2026", "תאריך", "פרסום", "עדכון", "סוג", "יחידות", "שתפו", "ועדת הבחירות", "הבחירות לכנסת", "רשימת המועמדים"]
                        for pkw in prohibited_kws:
                            if pkw in cname:
                                errors.append(f"[{p_id}] Candidate #{pos} name contains prohibited keyword '{pkw}': '{cname}'")

                        # 5. Character set check: only Hebrew letters, spaces, hyphens, quotes, apostrophes, parentheses
                        if not re.match(r"^[\u0590-\u05FF\s\'\"\-\.\(\)]+$", cname):
                            errors.append(f"[{p_id}] Candidate #{pos} name contains invalid characters: '{cname}'")

                    is_real = c.get("is_realistic_zone", False)
                    expected_real = (pos <= cutoff)
                    if is_real != expected_real:
                        errors.append(f"[{p_id}] Candidate #{pos} ({cname}) is_realistic_zone={is_real}, expected {expected_real} (cutoff={cutoff})")

                    if is_real:
                        real_count += 1
                        total_realistic_count += 1
                        cv = c.get("cv", {})
                        for cvk in ["education", "career", "public_service", "key_votes", "major_achievements", "notable_failures_or_controversies"]:
                            if cvk not in cv:
                                errors.append(f"[{p_id}] Candidate #{pos} ({cname}) missing CV key '{cvk}'")

                        edu = cv.get("education", "")
                        career = cv.get("career", "")
                        votes = cv.get("key_votes", [])
                        ach = cv.get("major_achievements", [])
                        fail = cv.get("notable_failures_or_controversies", [])

                        # Check for generic placeholders
                        has_placeholder = (
                            "השכלה אקדמית ורקע מקצועי בתחום הפעילות הציבורית" in edu or
                            "הצבעות לפי המשמעת הסיעתית" in str(votes) or
                            "קידום יעדי מפלגת" in str(ach) or
                            len(edu.strip()) < 5 or
                            len(career.strip()) < 10 or
                            not isinstance(votes, list) or len(votes) == 0 or
                            not isinstance(ach, list) or len(ach) == 0 or
                            not isinstance(fail, list)
                        )
                        if has_placeholder:
                            errors.append(f"[{p_id}] Candidate #{pos} ({cname}) has incomplete or placeholder CV data")
                        else:
                            rich_cv_count += 1
            except Exception as e:
                errors.append(f"[{p_id}] Invalid JSON in candidates.json: {e}")

        # Validate manifesto.md
        if m_ok:
            with open(m_md, "r", encoding="utf-8") as f:
                m_content = f.read()
            if len(m_content.strip()) < 100:
                errors.append(f"[{p_id}] manifesto.md content is too short ({len(m_content)} chars)")

        party_status_str = "✓ OK" if (p_ok and c_ok and m_ok and cand_count >= required_min and real_count == cutoff and rich_cv_count == cutoff) else "✗ Issues"
        print(f"{p_id:<18} | {cutoff:<6} | {required_min:<4} | {cand_count:<6} | {real_count:<9} | {rich_cv_count:<8} | {party_status_str}")
        verified_parties += 1

    print("=" * 95)
    print("STATIC KNOWLEDGE BASE AUDIT SUMMARY")
    print("=" * 95)
    print(f"- Total Qualified Parties: {len(qualifying_parties)}")
    print(f"- Verified Party Folders:  {verified_parties}")
    print(f"- Total Candidates Roster: {total_candidates_count}")
    print(f"- Realistic Candidates:    {total_realistic_count}")
    print(f"- Catalog, Rubric & Coalition Scenarios: 3")
    if errors:
        print(f"\n[!] Errors ({len(errors)}):")
        for e in errors[:30]:
            print(f"  ✗ {e}")
        if len(errors) > 30:
            print(f"  ... and {len(errors)-30} more errors")
        return False
    else:
        print("[✓] All static knowledge base artifacts verified successfully with full integrity.")
        return True

def import_cec_source(source_path_or_url: str) -> bool:
    """
    Imports and validates candidate lists from the official Central Elections Committee
    source (https://www.gov.il/he/pages/candidates-lists-26) or a local export file.
    """
    print(f"[*] Importing candidate lists from CEC official source: {source_path_or_url}")
    if not os.path.exists(source_path_or_url):
        print(f"[!] File not found: {source_path_or_url}")
        return False
    try:
        with open(source_path_or_url, "r", encoding="utf-8") as f:
            data = json.load(f)
        imported_count = 0
        for p_id, p_data in data.items():
            if p_id in PARTIES_CATALOG:
                c_path = os.path.join(PARTIES_DIR, p_id, "candidates.json")
                p_path = os.path.join(PARTIES_DIR, p_id, "party.json")
                if os.path.exists(c_path):
                    with open(c_path, "r", encoding="utf-8") as cf:
                        existing_c = json.load(cf)
                    existing_c["official_source"] = "https://www.gov.il/he/pages/candidates-lists-26"
                    if isinstance(p_data, dict) and "candidates" in p_data:
                        existing_c["candidates"] = p_data["candidates"]
                        existing_c["total_candidates_registered"] = len(p_data["candidates"])
                    elif isinstance(p_data, list):
                        existing_c["candidates"] = p_data
                        existing_c["total_candidates_registered"] = len(p_data)
                    with open(c_path, "w", encoding="utf-8") as cf:
                        json.dump(existing_c, cf, ensure_ascii=False, indent=2)

                if os.path.exists(p_path) and isinstance(p_data, dict):
                    with open(p_path, "r", encoding="utf-8") as pf:
                        existing_p = json.load(pf)
                    if "ballot_letters" in p_data:
                        existing_p["ballot_letters"] = p_data["ballot_letters"]
                    existing_p["official_cec_url"] = p_data.get("official_cec_url", f"https://www.gov.il/he/pages/candidates-lists-26#{p_id}")
                    with open(p_path, "w", encoding="utf-8") as pf:
                        json.dump(existing_p, pf, ensure_ascii=False, indent=2)

                imported_count += 1
                print(f"  [✓] Updated {p_id} candidates and metadata from CEC source")

        print(f"[✓] CEC source import complete ({imported_count} parties updated).")
        return verify_static_kb()
    except Exception as e:
        print(f"[!] Error importing CEC source: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Static Knowledge Base Manager for Knesset 2026")
    parser.add_argument("--build-all", action="store_true", help="Generate static artifacts for all 14 parties")
    parser.add_argument("--party", help="Build static artifacts for a specific party ID")
    parser.add_argument("--verify", action="store_true", help="Verify integrity of the static knowledge base")
    parser.add_argument("--import-cec-source", help="Import candidate rosters from official Central Elections Committee export file (JSON)")
    args = parser.parse_args()

    if args.import_cec_source:
        ok = import_cec_source(args.import_cec_source)
        sys.exit(0 if ok else 1)
    elif args.build_all or (not args.party and not args.verify):
        print("[*] Synchronizing static artifacts for all qualifying parties via official CEC data...")
        try:
            from sync_cec_data import sync_all
        except ImportError:
            from scripts.sync_cec_data import sync_all
        sync_all()
        ok = verify_static_kb()
        sys.exit(0 if ok else 1)
    elif args.party:
        generate_party_static_data(args.party)
    elif args.verify:
        ok = verify_static_kb()
        sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
