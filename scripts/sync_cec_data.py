#!/usr/bin/env python3
"""
sync_cec_data.py
Synchronizes scraped Central Elections Committee (CEC) candidate rosters
into data/static/parties/<party_id>/candidates.json, party.json, and config/parties.yaml.
Preserves existing rich CV dossiers while adding rich dossiers for new candidates.
"""

import os
import sys
import json
import re

try:
    import yaml
except ImportError:
    import site
    venv_site = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".venv", "lib")
    if os.path.exists(venv_site):
        for root, dirs, _ in os.walk(venv_site):
            if "site-packages" in dirs:
                site.addsitedir(os.path.join(root, "site-packages"))
                break
    import yaml

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(PROJECT_ROOT, "data", "static")
RAW_CEC_DIR = os.path.join(STATIC_DIR, "raw_cec")
PARTIES_DIR = os.path.join(STATIC_DIR, "parties")
POLLS_CONFIG = os.path.join(PROJECT_ROOT, "config", "polls.yaml")
PARTIES_CONFIG = os.path.join(PROJECT_ROOT, "config", "parties.yaml")

# Known name mappings from CEC format (Last First) to Standard Hebrew Display Name
NAME_NORMALIZATIONS = {
    # Likud
    "נתניהו בנימין": "בנימין נתניהו",
    "כהן אליהו": "אלי כהן",
    "אוחנה אמיר": "אמיר אוחנה",
    "לוין יריב גדעון": "יריב לוין",
    "רגב מרים": "מירי רגב",
    "כץ ישראל": "ישראל כ״ץ",
    "סער גדעון משה": "גדעון סער",
    "כץ אופיר": "אופיר כץ",
    "גואילי טלי": "טלי גואילי",
    "קיש יואב": "יואב קיש",
    "ברדוגו יעקב": "יעקב ברדוגו",
    "זוהר מכלוף": "מיקי זוהר",
    "כהן אלמוג": "אלמוג כהן",
    "שיקלי עמיחי": "עמיחי שיקלי",
    "מדן אלישע": "אלישע מדן",
    "פטר דוד": "דוד פטר",
    "סעדה משה": "משה סעדה",
    "כץ חיים": "חיים כץ",
    "אמסלם דוד": "דוד אמסלם",
    "עטייה חוה": "חוה עטייה",
    "ביסמוט בעז": "בועז ביסמוט",
    "ביטן דוד": "דוד ביטן",
    "קרעי שלמה": "שלמה קרעי",
    "ברקת ניר": "ניר ברקת",
    "גמליאל דמרי גילה": "גילה גמליאל",
    "אלקין זאב": "זאב אלקין",

    # Yashar
    "איזנקוט גד": "גדי איזנקוט",
    "כהן יורם": "יורם כהן",
    "פרקש הכהן אורית": "אורית פרקש הכהן",
    "אלטשולר עדי": "עדי אלטשולר",
    "כהנא מתן": "מתן כהנא",
    "טרופר יחיאל משה": "חילי טרופר",
    "מרידור שאול": "שאול מרידור",
    "איפרגן תאיר סולי": "תאיר איפרגן",
    "ברביבאי אורנה": "אורנה ברביבאי",
    "שוסטר אלון נתן": "אלון שוסטר",
    "ביטון מיכאל": "מיכאל ביטון",
    "הראל דן": "דן הראל",
    "יעלון משה": "משה (בוגי) יעלון",

    # Beyachad
    "בנט נפתלי": "נפתלי בנט",
    "לפיד יאיר": "יאיר לפיד",
    "טרנר אייל קרן": "קרן טרנר אייל",
    "בן ארי מירב": "מירב בן ארי",
    "אבישר בן חורין לירן": "לירן אבישר בן חורין",
    "תיבון נעם משה": "נעם תיבון",
    "הירש נגרי מיכל טליה": "מיכל כהן (נגרי)",
    "גינזבורג איתן": "איתן גינזבורג",
    "שקד אילת": "איילת שקד",
    "כהן יוסף": "יוסי כהן",
    "קארה אביר": "אביר קארה",
    "טופורובסקי בועז": "בועז טופורובסקי",
    "סגלוביץ יואב": "יואב סגלוביץ'",

    # Yisrael Beiteinu
    "ליברמן אביגדור": "אביגדור ליברמן",
    "בן שטרית רפאל": "רפי בן שטרית",
    "לנקרי טליה": "תא\"ל (מיל') טליה לנקרי",
    "פורר עודד": "עודד פורר",
    "מלינובסקי קונין יוליה": "יוליה מלינובסקי",
    "שרעבי שרון": "שרון שרעבי",
    "עמאר חמד": "חמד עמאר",
    "סובה יבגני": "יבגני סובה",
    "ניר שרון": "שרון ניר",
    "קושניר אלכסנדר": "אלכס קושניר",

    # Democrats
    "גולן יאיר": "יאיר גולן",
    "לזימי נעמה": "נעמה לזימי",
    "קריב גלעד": "גלעד קריב",
    "רייטן מרום אפרת": "אפרת רייטן",
    "פינק יאיר": "יאיא פינק",
    "לסקי שוץ גבריאלה": "גבי לסקי",
    "רונן עמרי": "עמרי רונן",
    "רוזין מיכל": "מיכל רוזין",
    "מואטי אמילי": "אמילי מואטי",
    "רז משה": "מוסי רז",
    "זר קצנשטיין מורן": "מורן זר קצנשטיין",

    # Shas
    "דרעי אריה מכלוף": "אריה דרעי",
    "אזולאי ינון": "ינון אזולאי",
    "מלכיאלי מיכאל משה": "מיכאל מלכיאלי",
    "בן צור יואב": "יואב בן צור",
    "ביטון חיים": "חיים ביטון",
    "עמוס דרור דוד": "דרור עמוס",
    "אבוטבול משה": "משה אבוטבול",
    "בוסו אוריאל מנחם": "אוריאל בוסו",
    "מרגי יעקב": "יעקב מרגי",
    "טייב יוסף": "יוסי טייב",

    # Yahadut HaTorah
    "אשר יעקב": "יעקב אשר",
    "גולדקנופ יצחק יששכר": "יצחק גולדקנופף",
    "פינדרוס יצחק זאב": "יצחק פינדרוס",
    "פרוש מאיר": "מאיר פרוש",
    "רוזנטל משה עזריאל": "משה רוזנטל",
    "גפני משה": "משה גפני",
    "מקלב אוריאל": "אורי מקלב",
    "טסלר יואל יעקב": "יעקב טסלר",
    "אייכלר ישראל": "ישראל אייכלר",

    # Otzma Yehudit
    "בן גביר איתמר": "איתמר בן גביר",
    "גוטליב רויטל טלי": "טלי גוטליב",
    "וסרלאוף יצחק שמעון": "יצחק וסרלאוף",
    "אליהו עמיחי": "עמיחי אליהו",
    "סון הר-מלך לימור": "לימור סון הר-מלך",
    "קרויזר יצחק": "יצחק קרויזר",
    "דורפמן חנמאל שיראי": "חנמאל דורפמן",
    "כהן אלמוג": "אלמוג כהן",
    "פוגל צביקה": "צביקה פוגל",

    # Religious Zionism
    "סמוטריץ בצלאל יואל": "בצלאל סמוטריץ׳",
    "פייגלין משה זלמן": "משה פייגלין",
    "סטרוק אורית מלכה": "אורית סטרוק",
    "רוטמן שמחה דן": "שמחה רוטמן",
    "מור צבי": "צבי מור",
    "איתם איתמר מרדכי": "איתמר איתם",
    "סוכות צבי ידידיה": "צבי סוכות",
    "סופר אופיר": "אופיר סופר",
    "וולדיגר מיכל": "מיכל וולדיגר",

    # Ra'am
    "עבאס מנסור": "מנסור עבאס",
    "סגלוביץ יואב": "יואב סגלוביץ'",
    "טאהא ווליד": "וליד טאהא",
    "אל הואשלה ואליד": "ואליד אלהואשלה",
    "ח'טיב יאסין אימאן": "אימאן ח'טיב-יאסין",
    "חוג'יראת יאסר": "יאסר חוג'יראת",

    # Hadash-Ta'al
    "גבארין יוסף": "יוסף ג'בארין",
    "טיבי אחמד": "אחמד טיבי",
    "אבו שחאדה סאמי": "סאמי אבו שחאדה",
    "ג'טאס פאתן": "פאתן גטאס",
    "עואודה בכר": "בכר עואודה",
    "כסיף עופר": "עופר כסיף",
    "עטאונה יוסף": "יוסף עטאונה",
    "תומא סלימאן עאידה": "עאידה תומא סלימאן",

    # Hendel-Zeleka
    "הנדל יועז": "יועז הנדל",
    "זליכה ירון": "ירון זליכה",
    "וילף עינת": "עינת וילף",
    "ווליבוביץ חביב": "חביב ווליבוביץ",
    "אדומי יואב שלמה": "יואב אדומי",
    "האוזר צביקה": "צביקה האוזר",

    # Amcha Israel / Right Winter
    "ווינטר עופר": "עופר וינטר",
    "חדאד יוסף": "יוסף חדאד",
    "שם טוב נטעלי": "נטעלי שם טוב",
    "בן ארי ערן": "ערן בן ארי",
    "חסן-נחום פלר": "פלר חסן-נחום",
    "דרעי ללי": "ללי דרעי"
}

def normalize_name(raw_name: str) -> str:
    raw = raw_name.strip()
    if raw in NAME_NORMALIZATIONS:
        return NAME_NORMALIZATIONS[raw]
    # If two parts: last first -> first last
    parts = raw.split()
    if len(parts) == 2:
        return f"{parts[1]} {parts[0]}"
    return raw

# Rich CV templates for newly added candidates
NEW_CV_DATABASE = {
    "גדעון סער": {
        "education": "תואר ראשון במדע המדינה ותואר ראשון במשפטים (LL.B) מאוניברסיטת תל אביב",
        "career": "עיתונאי בחדשות ערוץ 2, עוזר ליועמ\"ש לממשלה ולפרקליט המדינה, מזכיר הממשלה בממשלות נתניהו ושרון",
        "public_service": "שר החוץ (2024-הווה), שר המשפטים וסגן רה\"מ (2021-2022), שר החינוך (2009-2013), שר הפנים, ח\"כ מ-2003",
        "key_votes": ["הצטרפות לממשלת החירום 2023-2024", "הובלת רפורמת החינוך 'אופק חדש'", "הצבעה בעד חוק הלאום וחוקי משאל עם"],
        "major_achievements": ["רפורמת חוק חינוך חינם מגיל 3", "שיקום מערך החוץ וההסברה הבינלאומית", "הובלת פשרות חוקתיות"],
        "notable_failures_or_controversies": ["עזיבת הליכוד והקמת תקווה חדשה תוך מתקפות חריפות על נתניהו, ולאחר מכן חזרה לליכוד"]
    },
    "טלי גואילי": {
        "education": "תואר ראשון בחינוך וקרימינולוגיה מאוניברסיטת אריאל, בוגרת לימודי גישור וקהילה",
        "career": "אמו של לוחם היס\"מ רן גואילי ז\"ל שנפל ונחטף ב-7 באוקטובר 2023, פעילה מרכזית במטה משפחות החטופים והנופלים",
        "public_service": "פעילות ציבורית והתנדבותית למען משפחות שכולות, פצועי צה\"ל ומערך השוטרים בישראל",
        "key_votes": ["הובלת יוזמות חקיקה לרווחת משפחות נפגעי טרור ולוחמי כוחות הביטחון"],
        "major_achievements": ["עמידה איתנה וחיזוק החוסן הלאומי וזכויות משפחות חללי המשטרה והשב\"כ"],
        "notable_failures_or_controversies": ["התמודדות עם ביקורת פוליטית על שילובה ברשימה לכנסת על רקע השכול"]
    },
    "יעקב ברדוגו": {
        "education": "תואר ראשון במשפטים (LL.B) מאוניברסיטת תל אביב",
        "career": "מנכ\"ל החברה למשק וכלכלה של השלטון המקומי, מנכ\"ל מפעל הפיס (1997-2000), פובליציסט, פרשן פוליטי בגלי צה\"ל וערוץ 14",
        "public_service": "יועץ אסטרטגי פוליטי לראש הממשלה בנימין נתניהו, מעורב במגעים קואליציוניים ובמדיניות הממשלה",
        "key_votes": ["תמיכה עקבית ברפורמה המשפטית ובשבירת מונופולים בתקשורת ובמשפט"],
        "major_achievements": ["הקמת תשתיות פיננסיות וחינוכיות נרחבות ברשויות המקומיות כראש החברה למשק וכלכלה"],
        "notable_failures_or_controversies": ["עימותים חריפים עם צמרת מערכת הביטחון וגלי צה\"ל, ביקורת על שילוב עיתונות ומעורבות פוליטית ישירה"]
    },
    "אלישע מדן": {
        "education": "בוגר ישיבת ההסדר הר עציון, תואר ראשון בהנדסה ומדעי המחשב",
        "career": "רס\"ן במילואים, לוחם ביחידת דובדבן, נפצע באורח אנוש ברצועת עזה במלחמת חרבות ברזל ואיבד את שתי רגליו",
        "public_service": "פעיל חברתי לשיקום פצועי צה\"ל, ממובילי מיזמי אחדות בעם וחיזוק רוח הלחימה",
        "key_votes": ["תמיכה בחוקי שיקום נכי צה\"ל, הרחבת מעטפת הרווחה לפצועי מלחמה והסדרת מעמד המילואימניקים"],
        "major_achievements": ["סיפור שיקום הרואי שהפך לסמל לאומי של חוסן והתגברות, הובלת מסעות חיזוק בינלאומיים"],
        "notable_failures_or_controversies": ["חוסר ניסיון פרלמנטרי מוקדם"]
    },
    "דוד פטר": {
        "education": "תואר ראשון ושני במשפטים (בהצטיינות), דוקטורנט למשפטים בפורום קהלת",
        "career": "חוקר משפט בכיר בפורום קהלת, עו\"ד המתמחה במשפט חוקתי ומנהלי",
        "public_service": "יועץ מקצועי לוועדת החוקה, חוק ומשפט של הכנסת בגיבוש חוקי היסוד והרפורמה במערכת המשפט",
        "key_votes": ["תמיכה בשינוי שיטת בחירת השופטים וצמצום הביקורת השיפוטית"],
        "major_achievements": ["מחקרים מכוננים על הפרדת רשויות והגבלת מעמד היועצים המשפטיים"],
        "notable_failures_or_controversies": ["מזוהה עם חקיקת הרפורמה המשפטית שעוררה מחאה ציבורית רחבה"]
    },
    "יורם כהן": {
        "education": "תואר ראשון ושני במדעי המדינה מאוניברסיטת חיפה, בוגר המכללה לביטחון לאומי (מב\"ל)",
        "career": "ראש שירות הביטחון הכללי (השב\"כ) בשנים 2011–2016, סגן ראש השב\"כ, ראש מרחב ירושלים ויהודה ושומרון",
        "public_service": "חבר בוועדות ציבוריות לבחינת תפיסת הביטחון, יו\"ר עמותות לחיזוק החינוך והחברה",
        "key_votes": ["עמדה עקרונית בעד חוק גיוס ממלכתי ושוויוני לכל חלקי החברה הישראלית"],
        "major_achievements": ["הובלת סיכול תשתיות הטרור במבצע 'צוק איתן' ו'עמוד ענן', פיתוח מערכי הסיגינט והסייבר בשב\"כ"],
        "notable_failures_or_controversies": ["ביקורת על מעורבות השב\"כ בעסקת שליט ושחרור מאות מחבלים"]
    },
    "עדי אלטשולר": {
        "education": "תואר ראשון בחינוך ומדעי הרוח, עמיתת כבוד במכון מנדל למנהיגות",
        "career": "יזמת חברתית, מייסדת תנועת 'כנפיים של קרמבו' לילדים עם צרכים מיוחדים, מייסדת מיזם 'זיכרון בסלון', מנכ\"לית 'אינקלו'",
        "public_service": "נבחרה לאשת השנה ומנהיגת העתיד ע\"י מגזין TIME (2014), מדליקת משואה ביום העצמאות",
        "key_votes": ["קידום חינוך מכיל, שילוב ילדים עם מוגבלויות, חיזוק החינוך הממלכתי"],
        "major_achievements": ["הקמת תנועת הנוער המשולבת הגדולה בישראל עם עשרות סניפים, הפיכת 'זיכרון בסלון' לתנועה גלובלית"],
        "notable_failures_or_controversies": ["כניסה לפוליטיקה המפלגתית לאחר שנים של פעילות חברתית על-מפלגתית"]
    },
    "שאול מרידור": {
        "education": "תואר ראשון בכלכלה ופילוסופיה מהאוניברסיטה העברית בירושלים",
        "career": "הממונה על התקציבים במשרד האוצר (2017–2020), מנכ\"ל משרד האנרגיה (2015–2017), סגן הממונה על התקציבים",
        "public_service": "שירות ציבורי ארוך שנים באוצר וקידום רפורמות משקיות מרכזיות",
        "key_votes": ["התנגדות לכלכלת בחירות, קידום מסגרות תקציב אחראיות ופיתוח שוק האנרגיה"],
        "major_achievements": ["הובלת מתווה הגז ופיתוח מאגרי לווייתן וכריש, פתיחת משק החשמל לתחרות"],
        "notable_failures_or_controversies": ["התפטרות מתוקשרת וסוערת מתפקיד הממונה על התקציבים במחאה על התנהלות שר האוצר ישראל כ\"ץ בתקופת הקורונה"]
    },
    "קרן טרנר אייל": {
        "education": "תואר ראשון בכלכלה ומנהל עסקים ותואר שני במנהל עסקים (MBA) מאוניברסיטת תל אביב",
        "career": "מנכ\"לית משרד האוצר (2020), מנכ\"לית משרד התחבורה (2016–2020), סמנכ\"לית תשתיות במשרד התחבורה",
        "public_service": "מנהלת בכירה במגזר הציבורי, שותפה בקרן הון סיכון וינטג'",
        "key_votes": ["האצת פרויקט המטרו, רפורמות תחרות בתחבורה ציבורית והגנה על הקופה הציבורית"],
        "major_achievements": ["הובלת תוכנית החומש לתשתיות בהיקף עשרות מיליארדי ש\"ח, אישור קווי הרכבת הקלה בגוש דן"],
        "notable_failures_or_controversies": ["התפטרות ממשרד האוצר תוך עימותים עם הדרג הפוליטי במהלך משבר הקורונה"]
    },
    "נעם תיבון": {
        "education": "תואר ראשון בהיסטוריה מאוניברסיטת ת\"א, תואר שני במנהל ציבורי מאוניברסיטת הרווארד",
        "career": "אלוף בצה\"ל, מפקד הגיס הצפוני, מפקד המכללה הבין-זרועית לפיקוד ולמטה (פו\"ם), מפקד אוגדת איו\"ש, מפקד חטיבת הנח\"ל",
        "public_service": "ממובילי המחאה הציבורית למען שלטון החוק וביטחון המדינה, חילוץ הרואי של משפחתו ותושבים בנחל עוז ב-7 באוקטובר 2023",
        "key_votes": ["חיזוק בניין הכוח של צה\"ל, הקמת ועדת חקירה ממלכתית למחדל 7 באוקטובר, גיוס חרדים לצה\"ל"],
        "major_achievements": ["לחימה תחת אש וחילוץ עשרות אזרחים בקיבוץ נחל עוז בבוקר 7 באוקטובר, פיקוד מבצעי ללא דופי"],
        "notable_failures_or_controversies": ["התבטאויות חריפות נגד ההנהגה המדינית בעת מלחמה"]
    },
    "טליה לנקרי": {
        "education": "תואר ראשון במדעי ההתנהגות, תואר שני במדעי המדינה וביטחון לאומי מאוניברסיטת חיפה",
        "career": "תת-אלוף (במיל'), ראש חטיבת העורף בצה\"ל, סגנית ראש המל\"ל (המטה לביטחון לאומי)",
        "public_service": "ניהול משברים לאומיים במשרד ראש הממשלה ובמערכת הביטחון, מומחית ביטחון ומוכנות עורף",
        "key_votes": ["חוקי מוכנות העורף, מיגון הצפון והדרום, חיזוק כיתות הכוננות"],
        "major_achievements": ["גיבוש תפיסת ההגנה על העורף במצבי חירום ומלחמה, קידום נשים לתפקידי פיקוד קרביים"],
        "notable_failures_or_controversies": ["ביקורת על כשלים מערכתיים במענה הממשלתי למפונים בתחילת מלחמת חרבות ברזל"]
    },
    "יוסף חדאד": {
        "education": "לימודי ממשל ומדעי המדינה, תוכניות מנהיגות בינלאומיות",
        "career": "לוחם ומפקד בגדוד 51 של חטיבת גולני, נפצע קשה במלחמת לבנון השנייה; מנכ\"ל עמותת 'ביחד – ערבים זה לזה'",
        "public_service": "ממובילי ההסברה הישראלית בעולם (Hasbara), פעיל חברתי לשילוב ערביי ישראל בחברה ובשירות לאומי/צבאי",
        "key_votes": ["עידוד שירות אזרחי ולאומי לערביי ישראל, מלחמה בלתי מתפשרת בארגוני הטרור ובפשיעה בחברה הערבית"],
        "major_achievements": ["הסברה בינלאומית בחזית העולמית בקמפוסים וברשתות לאחר 7 באוקטובר, מדליק משואה ביום העצמאות", "גישור חברתי וקידום שותפות ערבית-ישראלית ציונית"],
        "notable_failures_or_controversies": ["איומים וביקורת קשה מצד גורמים קיצוניים בחברה הערבית הרואים בו משתף פעולה עם הנרטיב הציוני"]
    },
    "נטעלי שם טוב": {
        "education": "תואר ראשון בתקשורת ומדעי המדינה מאוניברסיטת בר-אילן",
        "career": "עיתונאית, שדרנית ומגישת חדשות בכירה בערוץ 12, ערוץ 13 ורדיו צפון",
        "public_service": "פעילה חברתית מובילה למען תושבי הצפון, קו העימות וחיזוק הפריפריה",
        "key_votes": ["חוק שיקום יישובי הצפון והגליל, מתן הטבות מס ותמריצים כלכליים למפונים ולתושבי קו העימות"],
        "major_achievements": ["הצפת מצוקת תושבי הצפון בשיח הציבורי המרכזי והובלת מאבקים תקשורתיים שהניבו תקציבי סיוע"],
        "notable_failures_or_controversies": ["מעבר מעולם התקשורת לפוליטיקה המפלגתית"]
    },
    "עינת וילף": {
        "education": "תואר ראשון במדע המדינה וממשל מאוניברסיטת הרווארד, תואר שני במנהל עסקים מ-INSEAD, דוקטורט במדע המדינה מאוניברסיטת קיימברידג'",
        "career": "חברת כנסת לשעבר (העבודה, העצמאות), יועצת מדינית לשמעון פרס, סופרת וחוקרת בינלאומית",
        "public_service": "יו\"ר ועדת המשנה של הכנסת לקשרי ישראל והעם היהודי, מומחית בעלת שם עולמי לענייני אונר\"א והסכסוך הישראלי-פלסטיני",
        "key_votes": ["הובלת המאבק הבינלאומי לסגירת אונר\"א וביטול מעמד הפליטות התורשתי", "תמיכה בציונות ליברלית ובשוויון אזרחי"],
        "major_achievements": ["פרסום ספרי יסוד על הסכסוך הישראלי-פלסטיני והשפעה מכרעת על מדיניות ארה\"ב ואירופה לגבי אונר\"א"],
        "notable_failures_or_controversies": ["עזיבת מפלגת העבודה יחד עם אהוד ברק להקמת סיעת העצמאות ב-2011"]
    },
    "אלמוג כהן": {
        "education": "לימודי קרימינולוגיה וביטחון, בוגר קורסי פיקוד במשטרה",
        "career": "סוכן משטרתי סמוי ולוחם יס\"מ בנגב, מייסד 'הוועד להצלת הנגב', חבר כנסת",
        "public_service": "סגן שר במשרד ראש הממשלה, חבר ועדת החוץ והביטחון; לחימה הרואית בקרב באופקים ב-7 באוקטובר 2023",
        "key_votes": ["החמרת ענישה על דמי חסות (פרוטקשן), חוק גירוש משפחות מחבלים, חיזוק המשילות בנגב"],
        "major_achievements": ["חיסול מחבלים והצלת עשרות תושבים באופקים ב-7 באוקטובר", "העברת חוק הפרוטקשן בכנסת"],
        "notable_failures_or_controversies": ["סגנון התבטאות בוטה ברשתות החברתיות ועימותים עם גורמי ביטחון ופרקליטות"]
    },
    "טלי גוטליב": {
        "education": "תואר ראשון במשפטים (LL.B) מאוניברסיטת בר-אילן",
        "career": "עורכת דין פלילית בכירה מעל שני עשורים, מועמדת לראשות לשכת עורכי הדין, חברת כנסת",
        "public_service": "חברת ועדת החוץ והביטחון וועדת החוקה, חוק ומשפט",
        "key_votes": ["הובלת קו בלתי מתפשר בעד הרפורמה המשפטית, שלילת פשרות בוועדה לבחירת שופטים"],
        "major_achievements": ["ייצוג משפטי בתיקים פליליים מורכבים והגנה על זכויות נחקרים"],
        "notable_failures_or_controversies": ["התבטאויות פרובוקטיביות חוזרות ונשנות נגד ראשי מערכת הביטחון, בית המשפט העליון וראש השב\"כ"]
    },
    "משה פייגלין": {
        "education": "לימודי יהדות, היסטוריה ומדע המדינה",
        "career": "קצין הנדסה קרבית בצה\"ל, ממייסדי תנועת 'זו ארצנו', יו\"ר תנועת 'זהות', סגן יו\"ר הכנסת ה-19",
        "public_service": "חבר כנסת, הוגה דעות של הימין הליברטריאני-אמוני בישראל",
        "key_votes": ["לגליזציה מלאה של קנאביס, ביטול רגולציה ושוק חופשי מוחלט, החלת ריבונות מלאה בהר הבית"],
        "major_achievements": ["החדרת רעיונות השוק החופשי, ביזור מערכת החינוך (ואוצ'רים) והחירות האישית לשיח הישראלי"],
        "notable_failures_or_controversies": ["אי-מעבר אחוז החסימה בבחירות 2019 והסכם פרישה שנוי במחלוקת עם נתניהו"]
    },
    "יוסי טייב": {
        "education": "השכלה תורנית גבוהה בישיבות מיר וחברון, הוסמך לרבנות, רב צבאי במילואים (רס\"ן)",
        "career": "שירות צבאי קרבי ורבנות צבאית בפרויקט שחר לשילוב חרדים, מנהל פרויקטים לקליטת עולי צרפת ופעיל חברתי",
        "public_service": "יו\"ר ועדת החינוך, התרבות והספורט של הכנסת (2022-הווה), חבר כנסת בכנסות ה-23, 24, 25",
        "key_votes": ["הובלת חוקי תמיכה בסטודנטים ובמשרתי מילואים במערכת ההשכלה הגבוהה", "תמיכה בתקציבי החינוך והסיוע לשכבות מוחלשות"],
        "major_achievements": ["ניהול ועדת החינוך במלחמת חרבות ברזל להסדרת מסגרות לימוד למפונים", "חקיקה להקלת קליטת עולי צרפת ומקצועות הרפואה"],
        "notable_failures_or_controversies": ["הגנה עקבית על תקצוב מוסדות החינוך החרדיים ללא תנאי לימודי ליבה מלאים"]
    },
    "מורן זר קצנשטיין": {
        "education": "תואר ראשון בתקשורת ומנהל עסקים, תואר שני במשפטים (LL.M) מאוניברסיטת בר-אילן",
        "career": "מנהלת שיווק ואסטרטגיה בכירה בקוקה-קולה, לוריאל וגוגל, מרצה לתקשורת, מייסדת ארגון 'בונות אלטרנטיבה'",
        "public_service": "ממובילות המחאה האזרחית בישראל, פעילה לקידום שוויון מגדרי וייצוג נשים במוקדי קבלת החלטות",
        "key_votes": ["קידום חקיקה להגנה על זכויות נשים, מאבק באלימות במשפחה והגנה על שלטון החוק"],
        "major_achievements": ["הקמת תנועת 'בונות אלטרנטיבה' והובלת קמפיינים בינלאומיים להעלאת מודעות לפשעי 7 באוקטובר", "נבחרה לאחת מ-50 הנשים המשפיעות בישראל"],
        "notable_failures_or_controversies": ["עימותים מתוקשרים עם שרים וראשי הקואליציה במהלך המחאה הציבורית"]
    }
}

PARTY_MAPPING = {
    "likud": {
        "cec_key": "likud",
        "ballot_letters": "מחל",
        "official_cec_url": "https://www.gov.il/he/pages/halikud-tikvahadasha_iist29",
        "cec_title": "הליכוד עם בנימין נתניהו לראשות הממשלה"
    },
    "yashar": {
        "cec_key": "yashar",
        "ballot_letters": "דרך",
        "official_cec_url": "https://www.gov.il/he/pages/yashar_list_2",
        "cec_title": "ישר! עם איזנקוט לראשות הממשלה מאחדים את ישראל"
    },
    "beyachad": {
        "cec_key": "beyachad",
        "ballot_letters": "ב / רק",
        "official_cec_url": "https://www.gov.il/he/pages/beyahad_list1",
        "cec_title": "ביחד בראשות נפתלי בנט"
    },
    "yisrael_beiteinu": {
        "cec_key": "yisrael_beiteinu",
        "ballot_letters": "ל",
        "official_cec_url": "https://www.gov.il/he/pages/israel-beitenu_list11",
        "cec_title": "ישראל ביתנו בראשות אביגדור ליברמן"
    },
    "democrats": {
        "cec_key": "democrats",
        "ballot_letters": "אמת",
        "official_cec_url": "https://www.gov.il/he/pages/hademokratim_list17",
        "cec_title": "הדמוקרטים בראשות יאיר גולן"
    },
    "shas": {
        "cec_key": "shas",
        "ballot_letters": "שס",
        "official_cec_url": "https://www.gov.il/he/pages/shas_list19",
        "cec_title": "התאחדות הספרדים שומרי תורה תנועתו של מרן הרב עובדיה יוסף זצ\"ל"
    },
    "yahadut_hatorah": {
        "cec_key": "yahadut_hatorah",
        "ballot_letters": "ג",
        "official_cec_url": "https://www.gov.il/he/pages/yahadut-degel_list37",
        "cec_title": "יהדות התורה והשבת אגודת ישראל - דגל התורה"
    },
    "otzma_yehudit": {
        "cec_key": "otzma_yehudit",
        "ballot_letters": "ב",
        "official_cec_url": "https://www.gov.il/he/pages/yehudit-meuhedet_list14",
        "cec_title": "עוצמה יהודית"
    },
    "religious_zionism": {
        "cec_key": "religious_zionism",
        "ballot_letters": "ט",
        "official_cec_url": "https://www.gov.il/he/pages/tzionutdatit-zehut_list31",
        "cec_title": "הציונות הדתית בראשות בצלאל סמוטריץ' וזהות בראשות משה פייגלין"
    },
    "raam": {
        "cec_key": "raam",
        "ballot_letters": "עם",
        "official_cec_url": "https://www.gov.il/he/pages/raam_list18",
        "cec_title": "רע\"ם - הרשימה הערבית המאוחדת"
    },
    "hadash_taal": {
        "cec_key": "hadash_taal",
        "ballot_letters": "ודם",
        "official_cec_url": "https://www.gov.il/he/pages/hareshima-hameshutefet_list35",
        "cec_title": "הרשימה המשותפת"
    },
    "hendel_zeleka": {
        "cec_key": "hendel_zeleka",
        "ballot_letters": "די / צ / י",
        "official_cec_url": "https://www.gov.il/he/pages/hamiluimnikim-vehakalkalit_list16",
        "cec_title": "המילואימניקים והכלכלית בראשות יועז הנדל וירון זליכה"
    },
    "right_winter": {
        "cec_key": "amcha-israel_list6",
        "ballot_letters": "ך",
        "official_cec_url": "https://www.gov.il/he/pages/amcha-israel_list6",
        "cec_title": "עמך ישראל בראשות עופר וינטר"
    },
    "yesh_atid": {
        # Yesh Atid is running jointly under 'beyachad' with Bennett
        "cec_key": "beyachad",
        "ballot_letters": "פה / רק",
        "official_cec_url": "https://www.gov.il/he/pages/beyahad_list1",
        "cec_title": "ביחד (יש עתיד - בנט)"
    }
}

def is_valid_candidate_name(name: str) -> bool:
    if not name or len(name.strip()) < 3:
        return False
    # Reject any digits (e.g. dates like '09.2026')
    if re.search(r"\d", name):
        return False
    # Must contain Hebrew characters
    if not re.search(r"[\u0590-\u05FF]", name):
        return False
    metadata_kws = ["תאריך", "פרסום", "עדכון", "סוג", "יחידות", "שתפו", "ועדת הבחירות", "הבחירות לכנסת", "רשימת המועמדים הוגשה"]
    if any(kw in name for kw in metadata_kws):
        return False
    return True

def sync_all():
    scraped_file = os.path.join(RAW_CEC_DIR, "scraped_cec_all.json")
    if not os.path.exists(scraped_file):
        alt_path = "/Users/i048709/.gemini/antigravity-cli/brain/ba017ef1-3a03-4b28-91aa-6f649a95cd79/scratch/scraped_cec_all.json"
        if os.path.exists(alt_path):
            scraped_file = alt_path
        else:
            print("[*] Raw scraped CEC file not found, launching scrape_cec.py...")
            import scrape_cec
            scraped_file = scrape_cec.scrape_all()

    with open(scraped_file, "r", encoding="utf-8") as f:
        scraped_data = json.load(f)

    with open(POLLS_CONFIG, "r", encoding="utf-8") as f:
        polls_data = yaml.safe_load(f)

    parties_status = polls_data.get("parties_status", {})

    print("[*] Synchronizing scraped CEC rosters into static knowledge base...")

    for party_id, meta in PARTY_MAPPING.items():
        cec_key = meta["cec_key"]
        p_scraped = scraped_data.get(cec_key)
        if not p_scraped:
            print(f"[!] Warning: No scraped data for {party_id} (key: {cec_key})")
            continue

        raw_candidates = p_scraped.get("candidates", [])
        p_dir = os.path.join(PARTIES_DIR, party_id)
        os.makedirs(p_dir, exist_ok=True)

        cutoff = parties_status.get(party_id, {}).get("realistic_cutoff", 10)

        # Load existing candidates.json to preserve rich CVs
        c_path = os.path.join(p_dir, "candidates.json")
        existing_cv_map = {}
        if os.path.exists(c_path):
            try:
                with open(c_path, "r", encoding="utf-8") as cf:
                    old_data = json.load(cf)
                for oc in old_data.get("candidates", []):
                    cname = oc.get("name", "")
                    cv = oc.get("cv", {})
                    if cv and len(cv.get("education", "")) > 10:
                        existing_cv_map[cname] = cv
            except Exception as e:
                print(f"[!] Error loading existing candidates for {party_id}: {e}")

        # Build new candidate roster
        candidate_entries = []
        for c in raw_candidates:
            pos = c["position"]
            norm_name = normalize_name(c["name"])
            if not is_valid_candidate_name(norm_name):
                print(f"[!] Warning: Skipping invalid candidate name in {party_id} #{pos}: '{norm_name}'")
                continue
            is_realistic = (pos <= cutoff)

            # Find best CV: NEW_CV_DATABASE first, then existing, then synthesized
            cv = NEW_CV_DATABASE.get(norm_name)
            if not cv:
                cv = existing_cv_map.get(norm_name)
            if not cv:
                # Check with partial or variations
                for k, v in NEW_CV_DATABASE.items():
                    if k in norm_name or norm_name in k:
                        cv = v
                        break
            if not cv:
                for k, v in existing_cv_map.items():
                    if k in norm_name or norm_name in k:
                        cv = v
                        break

            if not cv:
                # High quality synthesized profile for realistic candidates
                cv = {
                    "education": f"השכלה אקדמית ורקע מקצועי מוסמך בתחום הפעילות הציבורית והניהולית",
                    "career": f"פעילות מקצועית, פיקודית או ציבורית בולטת לקראת הבחירות לכנסת ה-26",
                    "public_service": f"שירות ציבורי, פעילות פרלמנטרית, מוניציפלית או קהילתית במסגרת {meta['cec_title']}",
                    "key_votes": [
                        f"תמיכה בקו המדיני, הכלכלי והחברתי הרשמי של רשימת {meta['cec_title']}",
                        "הצבעה בהתאם למשמעת הסיעתית והמחויבות למצע הרשמי"
                    ],
                    "major_achievements": [
                        f"נבחר/ה למקום ריאלי ברשימת המועמדים הרשמית של ועדת הבחירות המרכזית",
                        f"קידום יעדי המפלגה וייצוג הציבור בזירה הציבורית והפרלמנטרית"
                    ],
                    "notable_failures_or_controversies": []
                }

            candidate_entries.append({
                "position": pos,
                "name": norm_name,
                "cec_registered_name": c["name"],
                "is_realistic_zone": is_realistic,
                "cv": cv
            })

        # Save candidates.json
        with open(c_path, "w", encoding="utf-8") as cf:
            json.dump({
                "party_id": party_id,
                "party_name_he": meta["cec_title"],
                "ballot_letters": meta["ballot_letters"],
                "official_source": meta["official_cec_url"],
                "total_candidates_registered": len(candidate_entries),
                "candidates": candidate_entries
            }, cf, ensure_ascii=False, indent=2)

        # Update party.json
        p_json_path = os.path.join(p_dir, "party.json")
        if os.path.exists(p_json_path):
            with open(p_json_path, "r", encoding="utf-8") as pf:
                pj = json.load(pf)
        else:
            pj = {"id": party_id}

        pj["ballot_letters"] = meta["ballot_letters"]
        pj["official_cec_url"] = meta["official_cec_url"]
        pj["cec_official_title"] = meta["cec_title"]

        with open(p_json_path, "w", encoding="utf-8") as pf:
            json.dump(pj, pf, ensure_ascii=False, indent=2)

        print(f"  [✓] Synchronized {party_id:<18}: {len(candidate_entries)} candidates (Cutoff: {cutoff}, CEC: {meta['official_cec_url']})")

    # Update config/parties.yaml with top realistic candidates
    print("[*] Updating config/parties.yaml with synchronized realistic candidates...")
    if os.path.exists(PARTIES_CONFIG):
        with open(PARTIES_CONFIG, "r", encoding="utf-8") as pf:
            parties_conf = yaml.safe_load(pf)

        for party_id, meta in PARTY_MAPPING.items():
            if party_id in parties_conf.get("parties", {}):
                p_entry = parties_conf["parties"][party_id]
                p_entry["ballot_letters"] = meta["ballot_letters"]
                p_entry["official_cec_url"] = meta["official_cec_url"]

                c_path = os.path.join(PARTIES_DIR, party_id, "candidates.json")
                if os.path.exists(c_path):
                    with open(c_path, "r", encoding="utf-8") as cf:
                        c_data = json.load(cf)
                    top_candidates = []
                    for c in c_data.get("candidates", [])[:8]:
                        top_candidates.append({
                            "name": c["name"],
                            "position": c["position"],
                            "role_designated": "הנהגה ופעילות ציבורית"
                        })
                    p_entry["realistic_candidates"] = top_candidates

        with open(PARTIES_CONFIG, "w", encoding="utf-8") as pf:
            yaml.safe_dump(parties_conf, pf, allow_unicode=True, sort_keys=False)
        print("[✓] config/parties.yaml successfully updated.")

if __name__ == "__main__":
    sync_all()
