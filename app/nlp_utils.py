# app/nlp_utils.py
import re, emoji
from unidecode import unidecode
from nltk.sentiment import SentimentIntensityAnalyzer
from collections import Counter
from datetime import datetime


_sia = SentimentIntensityAnalyzer()

# Regex patterns
URL_RE = re.compile(r"https?://\S+|www\.\S+")
USER_RE = re.compile(r"@[A-Za-z0-9_]+")
HASH_RE = re.compile(r"#[A-Za-z0-9_]+")
WS_RE = re.compile(r"\s+")

# Stop words
STOP = set('''a an the is are was were be been being to of in for on with at by 
and or if from it this that these those i me my we our you your he she they them 
their not no it's im i'm rt via'''.split())


def clean_text(t: str) -> str:
    if not t:
        return ""
    t = unidecode(t)
    t = emoji.replace_emoji(t, replace=" ")
    t = URL_RE.sub(" ", t)
    t = USER_RE.sub(" ", t)
    t = HASH_RE.sub(" ", t)
    t = re.sub(r"[^a-zA-Z0-9\s]", " ", t)
    t = t.lower()
    t = WS_RE.sub(" ", t).strip()
    return t


ISSUE_KEYWORDS = {
    "late_delivery": ["late", "delay", "delayed", "time", "hours", "waiting"],
    "wrong_order": ["wrong", "incorrect", "missing", "item missing", "different"],
    "cold_food": ["cold", "stale", "not fresh"],
    "rude_support": ["support", "customer care", "helpdesk", "rude", "unhelpful"],
    "packaging": ["package", "packaging", "leak", "spill", "spilled", "sealed"],
    "refund": ["refund", "refunded", "refunds", "reimburse", "cashback"],
    "high_fees": ["expensive", "charges", "fees", "delivery fee", "surge", "taxes"],
}


def label_issue(text: str):
    hits = []
    for label, kws in ISSUE_KEYWORDS.items():
        for k in kws:
            if k in text:
                hits.append(label)
                break
    return hits or ["other"]


def sentiment_score(text: str) -> float:
    return _sia.polarity_scores(text)["compound"]


def sentiment_label(score: float) -> str:
    if score >= 0.05:
        return "positive"
    elif score <= -0.05:
        return "negative"
    else:
        return "neutral"
