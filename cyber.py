import string, random
from itertools import permutations
from math import ceil

# רשימת מילים: מהקובץ של המערכת אם קיים, אחרת רשימה קטנה של מילים נפוצות
try:
    WORDS = {w.strip().lower() for w in open("/usr/share/dict/words")}
except FileNotFoundError:
    WORDS = set("""the be to of and a in that have i it for not on with he as you do at this
    but his by from they we say her she or an will my one all would there their what so up out
    if about who get which go me when make can like time no just him know take into year your
    good some could them see other than then now look only come its over think also back after
    use two how our work first well way even new want because any these give day most us was
    were is are bus boat lake storm morning early small closed""".split())

def english_score(text):
    """אחוז המילים בטקסט שנמצאות ברשימת המילים (0..1)."""
    words = [w.strip(string.punctuation).lower() for w in text.split()]
    words = [w for w in words if w]
    if not words:
        return 0
    return sum(w in WORDS for w in words) / len(words)

# ---------- קיסר ----------
def caesar_shift(text, k):
    out = []
    for c in text:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            out.append(chr((ord(c) - base + k) % 26 + base))
        else:
            out.append(c)
    return "".join(out)

def crack_caesar(ct):
    return max(range(26), key=lambda k: english_score(caesar_shift(ct, k)))

# ---------- טרנספוזיציה של עמודות ----------
def columnar_decrypt(ct, perm):
    """perm[i] = מספר העמודה המקורית שנקראה במקום ה-i בהצפנה."""
    n, L = len(perm), len(ct)
    rows = ceil(L / n)
    full = L % n or n                      # כמה עמודות באורך מלא
    lens = {col: rows if col < full else rows - 1 for col in range(n)}
    cols, pos = {}, 0
    for col in perm:
        cols[col] = ct[pos:pos + lens[col]]
        pos += lens[col]
    return "".join(cols[c][r] for r in range(rows) for c in range(n) if r < len(cols[c]))

def crack_columnar(ct, max_cols=8):
    best, best_score, tried = None, -1, 0
    for n in range(2, max_cols + 1):
        for perm in permutations(range(n)):
            tried += 1
            pt = columnar_decrypt(ct, perm)
            s = english_score(pt)
            if s > best_score:
                best, best_score = (perm, pt), s
    return best, tried




# 1. למה השובר נכשל בטקסטים קצרים?

# השובר מנסה את 26 ההזזות ובוחר את זו שה-english_score שלה גבוה ביותר. הבעיה היא שבטקסט קצר הציון הזה לא מבדיל בין הזזות.

# רזולוציה נמוכה של הציון. בטקסט של 5 תווים יש מילה אחת או שתיים. הציון הוא אחוז מילים חוקיות, ולכן הוא יכול לקבל רק ערכים כמו 0, 0.5 או 1. כמה הזזות יכולות לקבל את אותו ציון 1.0.
# מילים שמתחלפות במילים. יש זוגות מילים שהם הזזה אחד של השני. למשל be ו-or (הזזה של 13), וגם ant ו-nag. אם הטקסט המקורי הוא “be”, גם ההזזה הנכונה וגם ההזזה השגויה נותנות מילה חוקית, ושתיהן מקבלות ציון מושלם.
# שוויון נפתר שרירותית. כש-max מוצא כמה מפתחות עם אותו ציון, הוא מחזיר את הראשון, כלומר את ההזזה הקטנה ביותר, בלי קשר לנכונות.
# רשימת מילים רחבה מדי. בקובץ המילים של המערכת יש הרבה מילים קצרות ושברי מילים, ולכן הסיכוי לפגוע במקרה בהזזה שגויה עולה.

# בטקסט ארוך זה כמעט לא קורה, כי סיכוי שעשרות מילים יצאו חוקיות במקרה בהזזה שגויה הוא זניח. הציון של המפתח הנכון מתרחק משאר הציונים.

# מה לעשות בהגשה: חפשו בניסוי שלכם מקרה אמיתי שנכשל בטקסט באורך 5, הדפיסו את הציון של כל ההזזות, והראו שכמה מהן שוות או קרובות. זו ה"הוכחה על סמך התוצאות". הגרף שלכם אמור להראות אחוז הצלחה שעולה עם האורך.

# 2. כמה מפתחות ניסה השובר בטרנספוזיציה?

# מפתח הוא סדר העמודות, כלומר תמורה של n עמודות, ולכן יש n! מפתחות אפשריים.

# השובר שלכם לא יודע את n, ולכן הוא עובר על n = 2, 3, …, m (בקוד max_cols). הסכום הוא:

# Σ n! עבור n מ-2 עד m

# עם ברירת המחדל m = 8 מקבלים 2 + 6 + 24 + 120 + 720 + 5040 + 40320 = 46,232 מפתחות. אפשר לאמת מול המשתנה tried בקוד.

# השאלה מבקשת "כתלות באורך ההודעה" L. הקשר הוא ש-n לא יכול לעלות על L, כי אי אפשר שיהיו יותר עמודות מתווים. לכן הסכום הוא עד min(m, L). אם אתם מרשים כל n אפשרי, הוא עד L, והמספר מתפוצץ מהר: כבר ב-n = 20 יש בערך 2.4×10¹⁸ מפתחות.

# 3. שינוי בצופן שהופך את השובר לחסר תועלת

# עליכם לבחור שינוי אחד, ולהסביר איזו הנחה של השובר הוא שובר. לשובר שלכם יש שתי הנחות מרכזיות:

# מרחב המפתחות קטן מספיק לעבור עליו. שינוי שמנפח אותו הופך את החיפוש לבלתי אפשרי. למשל, החלפה לצופן החלפה כללי (כל אות מוחלפת באות אחרת לפי טבלה): יש 26! ≈ 4×10²⁶ מפתחות, יותר מדי לכוח גס. אפשרות נוספת היא טרנספוזיציה עם מספר עמודות גדול בהרבה, או טרנספוזיציה כפולה.
# הפלט הנכון נראה כמו אנגלית עם רווחים בין מילים. שינוי שפוגע בזה מבלבל את english_score. למשל, הסרת הרווחים והסימנים מהטקסט המוצפן, או הוספת תווי "זבל" אקראיים. אז אפילו המפתח הנכון לא ייתן מילים שהשובר מזהה.