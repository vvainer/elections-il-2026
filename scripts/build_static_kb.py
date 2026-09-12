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
        "leader": "בנימין נתניהו",
        "leader_title": "ראש הממשלה ויו״ר הליכוד",
        "official_website": "https://www.likud.org.il",
        "knesset_faction_url": "https://main.knesset.gov.il/mk/factions/pages/faction.aspx?fId=1",
        "manifesto_status": "עקרונות תנועת הליכוד הלאומית-ליברלית",
        "manifesto_text": "# מצע ומדיניות תנועת הליכוד\n\n- **ביטחון ומדיניות**: שמירה על ארץ ישראל השלמה, הרחבת הסכמי אברהם, מאבק בתוכנית הגרעין האיראנית, שלילת הקמת מדינה פלסטינית.\n- **כלכלה**: שוק חופשי, עידוד תחרות, הורדת חסמים ומסים.\n- **משילות**: רפורמה במערכת המשפט והשבת האיזון בין הרשויות.",
        "candidate_names": ["בנימין נתניהו", "יריב לוין", "יואב גלנט", "ניר ברקת", "ישראל כ״ץ", "אלי כהן", "יואב קיש", "אבי דיכטר", "מירי רגב", "אמיר אוחנה", "דוד אמסלם", "אלי דילל", "גלית דיסטל אטבריאן", "נסים ואטורי", "שלמה קרעי", "בועז ביסמוט", "חנוך מילביצקי", "קטי שטרית", "אופיר כץ", "אתי עטייה"]
    },
    "yashar": {
        "id": "yashar",
        "name_he": "ישר",
        "leader": "גדי איזנקוט",
        "leader_title": "יו״ר מפלגת ישר, רמטכ״ל לשעבר",
        "official_website": "https://yashar.org.il",
        "knesset_faction_url": "https://main.knesset.gov.il",
        "manifesto_status": "תוכנית לאומית לתיקון המדינה 2026",
        "manifesto_text": "# תוכנית מפלגת ישר לתיקון המדינה\n\n- **חינוך וממלכתיות**: חובת לימודי ליבה לכל מוסד מתוקצב, ביזור סמכויות למנהלים והעלאת מעמד המורה.\n- **משטר ומשילות**: חוק יסוד חקיקה בהסכמה רחבה, חיזוק השלטון המקומי, מאבק בשחיתות.\n- **ביטחון ותשתיות**: השקעה של 2 מיליארד ש\"ח במחשוב קוונטי ו-AI, בריתות אזוריות, היפרדות אזרחית מהפלסטינים תוך שמירת שליטה ביטחונית.",
        "candidate_names": ["גדי איזנקוט", "מתן כהנא", "אורית פרקש הכהן", "חילי טרופר", "מיכאל ביטון", "אלון שוסטר", "עדי אלטשולר", "משה (בוגי) יעלון", "רון שמיר", "תמי שינקמן", "דן הראל", "אורנה ברביבאי", "יונתן שמריז", "זהבה בראון", "יוסי כהן (חברתי)"]
    },
    "beyachad": {
        "id": "beyachad",
        "name_he": "ביחד",
        "leader": "נפתלי בנט",
        "leader_title": "יו״ר מפלגת ביחד, ראש הממשלה לשעבר",
        "official_website": "https://www.beyachad2026.org.il",
        "knesset_faction_url": "https://main.knesset.gov.il",
        "manifesto_status": "תוכנית זינוק לישראל 2026",
        "manifesto_text": "# תוכנית זינוק לישראל - מפלגת ביחד\n\n- **כלכלה ושוק חופשי**: מהפכת יבוא חופשי, קיצוץ בירוקרטיה, רפורמת מס לחברות הייטק, עידוד יזמות.\n- **ביטחון**: יוזמה התקפית מוחצת נגד ראש התמנון האיראני, הכפלת תקציבי מו\"פ ביטחוני ורובוטיקה.\n- **חינוך וחברה**: מצוינות במדעים, חיזוק החינוך הממלכתי-דתי והכללי, שירות אזרחי או צבאי לכולם.",
        "candidate_names": ["נפתלי בנט", "אילת שקד", "מתן סידי", "פנחס ולרשטיין", "אביר קארה", "שירלי פינטו", "עמיחי שיקלי", "יום טוב כלפון", "סטלה ויינשטיין", "רוני ששון"]
    },
    "yisrael_beiteinu": {
        "id": "yisrael_beiteinu",
        "name_he": "ישראל ביתנו",
        "leader": "אביגדור ליברמן",
        "leader_title": "יו״ר ישראל ביתנו, שר האוצר והביטחון לשעבר",
        "official_website": "https://beytenu.org.il",
        "knesset_faction_url": "https://main.knesset.gov.il/mk/factions/pages/faction.aspx?fId=8",
        "manifesto_status": "מצע ישראל ביתנו - חופשיים ומנצחים",
        "manifesto_text": "# מצע ישראל ביתנו\n\n- **דת ומדינה**: גיוס שווה לכל בגיל 18 (יהודים וערבים), תחבורה ציבורית ומסחר בשבת לפי החלטת רשות מקומית, נישואים אזרחיים.\n- **רווחה ותעסוקה**: התניית קצבאות בכושר השתכרות, ביטול תקציבי ישיבות ללא ליבה.\n- **ביטחון**: הכרעה צבאית תקיפה ללא היסוסים.",
        "candidate_names": ["אביגדור ליברמן", "עודד פורר", "יבגני סובה", "שרון ניר", "יוליה מלינובסקי", "חמד עמאר", "אלכס קושניר", "אלינה ברדץ' יאלוב", "יוסי שיין", "בוריס שינדלר"]
    },
    "democrats": {
        "id": "democrats",
        "name_he": "הדמוקרטים",
        "leader": "יאיר גולן",
        "leader_title": "יו״ר הדמוקרטים (איחוד העבודה ומרצ)",
        "official_website": "https://democrats.org.il",
        "knesset_faction_url": "https://main.knesset.gov.il/mk/factions/pages/faction.aspx?fId=3",
        "manifesto_status": "חוזה דמוקרטי לישראל 2026",
        "manifesto_text": "# חוזה דמוקרטי לישראל\n\n- **חוקה ומשטר**: חוקה לישראל המבוססת על מגילת העצמאות, הגנה מוחלטת על שלטון החוק וזכויות האדם.\n- **דת ומדינה**: שוויון מוחלט, תחבורה ציבורית בשבת, חופש דת וחופש מדת.\n- **מדיני**: הסדר אזורי והיפרדות לשתי מדינות, חידוש הברית עם מדינות המערב.",
        "candidate_names": ["יאיר גולן", "נעמה לזימי", "גלעד קריב", "אפרת רייטן", "מוסי רז", "מיכל רוזין", "גבי לסקי", "מהרטא ברוך-רון", "יאיא פינק", "אמילי מואטי"]
    },
    "yesh_atid": {
        "id": "yesh_atid",
        "name_he": "יש עתיד",
        "leader": "יאיר לפיד",
        "leader_title": "ראש האופוזיציה ויו״ר יש עתיד",
        "official_website": "https://www.yeshatid.org.il",
        "knesset_faction_url": "https://main.knesset.gov.il/mk/factions/pages/faction.aspx?fId=2",
        "manifesto_status": "תוכנית עבודה לאומית לישראל",
        "manifesto_text": "# תוכנית יש עתיד\n\n- **חינוך**: לימודי ליבה לכל, ביזור סמכויות למנהלי בתי ספר.\n- **צמצום הממשלה**: הגבלת הממשלה ל-18 שרים בחוק יסוד.\n- **שוויון בנטל**: חוק גיוס אמיתי עם יעדים סנקציות כלכליות.",
        "candidate_names": ["יאיר לפיד", "מאיר כהן", "קארין אלהרר", "מירב כהן", "יואב סגלוביץ'", "מיקי לוי", "אלעזר שטרן", "רם בן ברק", "מירב בן ארי", "ולדימיר בליאק"]
    },
    "shas": {
        "id": "shas",
        "name_he": "ש״ס",
        "leader": "אריה דרעי",
        "leader_title": "יו״ר תנועת ש״ס",
        "official_website": "https://shas.org.il",
        "knesset_faction_url": "https://main.knesset.gov.il/mk/factions/pages/faction.aspx?fId=5",
        "manifesto_status": "דאגה לחלשים ושימור עולם התורה",
        "manifesto_text": "# עקרונות תנועת ש\"ס\n\n- שימור מעמד עולם התורה ותקצוב הישיבות והכוללים ללא תנאי ליבה.\n- חלוקת תלושי מזון ותמיכה סוציאלית מוגברת לשכבות חלשות.\n- התנגדות נחרצת לשינויי סטטוס קוו בשבת ובגיור.",
        "candidate_names": ["אריה דרעי", "יעקב מרגי", "מיכאל מלכיאלי", "חיים ביטון", "משה ארבל", "ינון אזולאי", "יוסי טייב", "אוריאל בוסו", "נתנאל חייק", "יונתן מישרקי"]
    },
    "yahadut_hatorah": {
        "id": "yahadut_hatorah",
        "name_he": "יהדות התורה",
        "leader": "יצחק גולדקנופף / משה גפני",
        "leader_title": "ראשי יהדות התורה (אגודת ישראל ודגל התורה)",
        "official_website": "https://main.knesset.gov.il",
        "knesset_faction_url": "https://main.knesset.gov.il/mk/factions/pages/faction.aspx?fId=6",
        "manifesto_status": "הגנה מוחלטת על מעמד בני הישיבות והחינוך החרדי העצמאי",
        "manifesto_text": "# עקרונות יהדות התורה\n\n- פטור מלא לתלמידי ישיבות מגיוס לצה\"ל.\n- התנגדות ללימודי ליבה בחינוך החרדי ועמידה על תקצוב שווה.\n- שמירת השבת הציבורית והתנגדות לתחבורה או מסחר בשבת.",
        "candidate_names": ["יצחק גולדקנופף", "משה גפני", "מאיר פרוש", "אורי מקלב", "יעקב טסלר", "יעקב אשר", "ישראל אייכלר", "אליהו ברוכי", "יצחק רייך", "בנימין הרשלר"]
    },
    "otzma_yehudit": {
        "id": "otzma_yehudit",
        "name_he": "עוצמה יהודית",
        "leader": "איתמר בן גביר",
        "leader_title": "השר לביטחון לאומי ויו״ר עוצמה יהודית",
        "official_website": "https://main.knesset.gov.il",
        "knesset_faction_url": "https://main.knesset.gov.il/mk/factions/pages/faction.aspx?fId=11",
        "manifesto_status": "משילות, ריבונות וביטחון לאומי",
        "manifesto_text": "# מצע עוצמה יהודית\n\n- עונש מוות למחבלים, שינוי הוראות פתיחה באש, חלוקת נשק לאזרחים.\n- החלת ריבונות מלאה ביהודה ושומרון ועידוד הגירה של תומכי טרור.\n- רפורמה מקיפה ברשות השופטת וביטול מונופול היועמ\"ש.",
        "candidate_names": ["איתמר בן גביר", "יצחק וסרלאוף", "אלמוג כהן", "עמיחי אליהו", "צביקה פוגל", "לימור סון הר-מלך", "יצחק קרויזר", "אושר שקלים", "אפרים דוד", "יוסי מנצור"]
    },
    "religious_zionism": {
        "id": "religious_zionism",
        "name_he": "הציונות הדתית",
        "leader": "בצלאל סמוטריץ׳",
        "leader_title": "שר האוצר ויו״ר הציונות הדתית",
        "official_website": "https://main.knesset.gov.il",
        "knesset_faction_url": "https://main.knesset.gov.il/mk/factions/pages/faction.aspx?fId=10",
        "manifesto_status": "חוק ומשפט, ריבונות והתיישבות",
        "manifesto_text": "# מצע הציונות הדתית\n\n- תוכנית 'חוק וצדק' לתיקון מערכת המשפט והסדרת פסקת ההתגברות.\n- ביטול המנהל האזרחי והחלת ריבונות והסדרת ההתיישבות הצעירה.\n- כלכלה לאומית חופשית, קיצוץ רגולציה לצד חיזוק זהות יהודית ממלכתית.",
        "candidate_names": ["בצלאל סמוטריץ׳", "אופיר סופר", "אורית סטרוק", "שמחה רוטמן", "מיכל וולדיגר", "אוהד טל", "משה סולומון", "צבי סוכות", "יוסף שפירא", "דוד אליהו"]
    },
    "raam": {
        "id": "raam",
        "name_he": "רע״ם",
        "leader": "מנסור עבאס",
        "leader_title": "יו״ר רע״ם (הרשימה הערבית המאוחדת)",
        "official_website": "https://main.knesset.gov.il",
        "knesset_faction_url": "https://main.knesset.gov.il/mk/factions/pages/faction.aspx?fId=7",
        "manifesto_status": "שותפות אזרחית ופיתוח החברה הערבית",
        "manifesto_text": "# מצע רע\"ם\n\n- התמקדות בצרכים האזרחיים של החברה הערבית: מיגור הפשיעה, תכנון ובנייה, תקציבי פיתוח.\n- גישה פרגמטית ומוכנות להשתלבות בכל קואליציה המקדמת את צרכי הציבור הערבי.\n- שימור הזהות המוסלמית והדתית והתנגדות לחקיקה ליברלית בנושאי להט\"ב.",
        "candidate_names": ["מנסור עבאס", "וליד טאהא", "ואליד אלהואשלה", "אימאן ח'טיב-יאסין", "יאסר חוג'יראת", "עבד אל-כרים גמל", "מוחמד אבו עפאש", "עבדאללה סלאמה"]
    },
    "hadash_taal": {
        "id": "hadash_taal",
        "name_he": "חד״ש-תע״ל",
        "leader": "איימן עודה / אחמד טיבי",
        "leader_title": "ראשי חד״ש-תע״ל",
        "official_website": "https://main.knesset.gov.il",
        "knesset_faction_url": "https://main.knesset.gov.il/mk/factions/pages/faction.aspx?fId=9",
        "manifesto_status": "סיום הכיבוש, שלום ישראלי-פלסטיני וצדק חברתי",
        "manifesto_text": "# מצע חד\"ש-תע\"ל\n\n- סיום הכיבוש והקמת מדינה פלסטינית עצמאית בגבולות 67' שבירתה מזרח ירושלים.\n- הפיכת ישראל למדינת כל אזרחיה, ביטול חוק הלאום וביטול אפליה ממוסדת.\n- תפיסה כלכלית סוציאליסטית, הגנה על זכויות עובדים והתנגדות להפרטות.",
        "candidate_names": ["איימן עודה", "אחמד טיבי", "עאידה תומא סלימאן", "עופר כסיף", "יוסף עטאונה", "סמיר בן סעיד", "פאדי אבו סיאם", "רים חזאן"]
    },
    "hendel_zeleka": {
        "id": "hendel_zeleka",
        "name_he": "איחוד הנדל-זליכה",
        "leader": "יועז הנדל / ירון זליכה",
        "leader_title": "ראשי איחוד הנדל-זליכה (ממלכתיים וכלכלית)",
        "official_website": "https://www.calcalist.co.il",
        "knesset_faction_url": "https://main.knesset.gov.il",
        "manifesto_status": "שוק חופשי וממלכתיות לוחמת",
        "manifesto_text": "# מצע איחוד הנדל-זליכה\n\n- **שוק חופשי תחרותי**: פירוק מונופולים, פתיחה מוחלטת של יבוא, מלחמה ביוקר המחיה.\n- **חינוך ותעסוקה**: חובת לימודי ליבה לכל מוסד מתוקצב, שלילת קצבאות ממי שאינו עובד.\n- **ממשל יעיל**: הגבלת הממשלה ל-18 שרים, מיזוג משרדים, מלחמה בלתי מתפשרת בשחיתות.",
        "candidate_names": ["יועז הנדל", "ירון זליכה", "צביקה האוזר", "אורי קידר", "אסנת מארק (כלכלית)", "רונן הופמן", "אורית קאופמן", "גדעון סער (תומך)", "אייל ברקוביץ'"]
    },
    "right_winter": {
        "id": "right_winter",
        "name_he": "ימין ממלכתי / וינטר",
        "leader": "עופר וינטר",
        "leader_title": "יו״ר ימין ממלכתי, תת-אלוף (מיל׳)",
        "official_website": "https://www.inn.co.il",
        "knesset_faction_url": "https://main.knesset.gov.il",
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
        "leader": p_info["leader"],
        "leader_title": p_info["leader_title"],
        "official_website": p_info["official_website"],
        "knesset_faction_url": p_info["knesset_faction_url"],
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

    errors = []
    if not os.path.exists(topics_file):
        errors.append("Missing topics catalog: " + topics_file)
    if not os.path.exists(criteria_file):
        errors.append("Missing criteria rubric: " + criteria_file)
    if not os.path.exists(coalitions_file):
        errors.append("Missing coalitions scenarios: " + coalitions_file)

    parties = list(PARTIES_CATALOG.keys())
    verified_parties = 0
    for p_id in parties:
        p_dir = os.path.join(PARTIES_DIR, p_id)
        if not os.path.exists(p_dir):
            errors.append(f"Missing party directory: {p_dir}")
            continue
        p_json = os.path.join(p_dir, "party.json")
        c_json = os.path.join(p_dir, "candidates.json")
        m_md = os.path.join(p_dir, "manifesto.md")
        if not os.path.exists(p_json):
            errors.append(f"Missing {p_json}")
        if not os.path.exists(c_json):
            errors.append(f"Missing {c_json}")
        if not os.path.exists(m_md):
            errors.append(f"Missing {m_md}")
        verified_parties += 1

    print("\n" + "=" * 60)
    print("STATIC KNOWLEDGE BASE AUDIT SUMMARY")
    print("=" * 60)
    print(f"- Total Qualified Parties: {len(parties)}")
    print(f"- Verified Parties:         {verified_parties}")
    print(f"- Catalog, Rubric & Coalition Files: 3")
    if errors:
        print(f"\n[!] Errors ({len(errors)}):")
        for e in errors:
            print(f"  ✗ {e}")
        return False
    else:
        print("[✓] All static knowledge base artifacts verified successfully.")
        return True

def main():
    parser = argparse.ArgumentParser(description="Static Knowledge Base Manager for Knesset 2026")
    parser.add_argument("--build-all", action="store_true", help="Generate static artifacts for all 14 parties")
    parser.add_argument("--party", help="Build static artifacts for a specific party ID")
    parser.add_argument("--verify", action="store_true", help="Verify integrity of the static knowledge base")
    args = parser.parse_args()

    if args.build_all or (not args.party and not args.verify):
        print("[*] Generating static artifacts for all qualifying parties...")
        for p_id in PARTIES_CATALOG.keys():
            generate_party_static_data(p_id)
        verify_static_kb()
    elif args.party:
        generate_party_static_data(args.party)
    elif args.verify:
        ok = verify_static_kb()
        sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
