# app/analyze.py
import os
import glob
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from app.nlp_utils import clean_text, sentiment_score, sentiment_label, label_issue


RAW = os.path.join("data", "raw", "*.csv")
OUT_CLEAN = os.path.join("data", "clean", "reviews_clean.csv")
os.makedirs(os.path.dirname(OUT_CLEAN), exist_ok=True)


# 1) Merge raw CSVs
paths = glob.glob(RAW)
if not paths:
    raise FileNotFoundError("No raw CSV files found in data/raw/")

frames = [pd.read_csv(p) for p in paths]
df = pd.concat(frames, ignore_index=True)


# 2) Basic cleaning
for col in ["content"]:
    if col not in df.columns:
        raise KeyError(f"Expected column '{col}' not found in CSV files")
    df[col] = df[col].astype(str)
    df["clean"] = df[col].apply(clean_text)


# 3) Drop empties
df = df[df["clean"].str.len() > 0].copy()


# 4) Sentiment analysis
df["sent_score"] = df["clean"].apply(sentiment_score)
df["sent_label"] = df["sent_score"].apply(sentiment_label)


# 5) Issue labels (multi-label → pipe-joined)
df["issues"] = df["clean"].apply(lambda t: "|".join(label_issue(t)))


# 6) Save clean dataset
df.to_csv(OUT_CLEAN, index=False)
print(f"✅ Saved clean dataset: {OUT_CLEAN} | rows={len(df)}")


# 7) Word Cloud (focus on negative reviews, fallback = all reviews)
neg_texts = df.loc[df["sent_label"] == "negative", "clean"].tolist()
text_for_wc = " ".join(neg_texts if neg_texts else df["clean"].tolist())

wc = WordCloud(
    width=1200,
    height=600,
    background_color="white",
    colormap="Reds"
).generate(text_for_wc)

plt.figure(figsize=(12, 6))
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
plt.tight_layout()
wc_path = os.path.join("data", "clean", "wordcloud_negative.png")
plt.savefig(wc_path, dpi=300)
print(f"✅ Saved wordcloud: {wc_path}")


# 8) Sentiment distribution plot
sent_counts = df["sent_label"].value_counts()
plt.figure(figsize=(6, 4))
sent_counts.plot(kind="bar", rot=0)
plt.title("Sentiment Distribution")
plt.ylabel("Count")
plt.xlabel("Sentiment")
plt.tight_layout()
bar_path = os.path.join("data", "clean", "sentiment_bar.png")
plt.savefig(bar_path, dpi=300)
print(f"✅ Saved sentiment bar chart: {bar_path}")


# 9) Quick summary stats
print("\n📊 Sentiment Breakdown:")
print(sent_counts.to_string())

print("\n📌 Top 10 Issues:")
print(df["issues"].value_counts().head(10).to_string())
