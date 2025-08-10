# date_utils.py
from dateutil import parser as dateparser
import re
import datetime

DATE_PATTERNS = [
    r'\b(?:\d{1,2}[\/\-\.\s]\d{1,2}[\/\-\.\s]\d{2,4})\b',
    r'\b(?:\d{4}[\/\-\.\s]\d{1,2}[\/\-\.\s]\d{1,2})\b',
    r'\b(?:exp|expiry|exp\.|exp:)\s*[:\-]?\s*([A-Za-z0-9 \-\/\.]+)\b',
]

def find_expiry_date(text_lines):
    """
    text_lines: list[str]
    returns: ISO date string (YYYY-MM-DD) or None
    """
    now = datetime.datetime.now()
    candidates = []
    for line in text_lines:
        # quick regex find likely date substrings
        for pat in DATE_PATTERNS:
            m = re.search(pat, line, flags=re.IGNORECASE)
            if m:
                date_str = m.group(0)
                try:
                    dt = dateparser.parse(date_str, fuzzy=True, dayfirst=True)
                    # plausible expiry: not too far in past, within 30 years future
                    if dt.year >= now.year - 1 and dt.year <= now.year + 30:
                        candidates.append(dt.date())
                except:
                    continue
        # also try parsing full line fuzzily
        try:
            dt = dateparser.parse(line, fuzzy=True, default=now)
            if dt.year >= now.year - 1 and dt.year <= now.year + 30:
                candidates.append(dt.date())
        except:
            pass

    if not candidates:
        return None
    # choose the earliest plausible date (often expiry)
    chosen = min(candidates)
    return chosen.isoformat()
