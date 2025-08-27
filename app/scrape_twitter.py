# app/scrape_twitter.py
import os
import pandas as pd
from datetime import datetime, timedelta
import snscrape.modules.twitter as sntwitter

QUERY = '(swiggy OR zomato OR "uber eats") (delivery OR order OR packaging OR refund OR late)'
SINCE_DAYS = 14
MAX_TWEETS = 2000

start_date = datetime.utcnow() - timedelta(days=SINCE_DAYS)

rows = []

for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f'{QUERY} since:{start_date.date()}').get_items()):
    if i >= MAX_TWEETS:
        break
    rows.append({
        "platform": "twitter",
        "app": "mixed",
        "source": tweet.url,
        "reviewId": tweet.id,
        "userName": tweet.user.username,
        "score": None,
        "at": tweet.date,
        "content": tweet.content
    })

OUT_PATH = os.path.join("data", "raw", f"twitter_{datetime.now().strftime('%Y%m%d_%H%M')}.csv")
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
pd.DataFrame(rows).to_csv(OUT_PATH, index=False)
print(f"Saved: {OUT_PATH} | rows={len(rows)}")
