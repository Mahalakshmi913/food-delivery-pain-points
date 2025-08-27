# app/scrape_reddit.py
import os
import pandas as pd
from datetime import datetime
import praw
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Environment variables
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "food-delivery-painpoints/0.1 by mahal")

# Subreddits & query
SUBS = ["india", "bangalore", "mumbai", "hyderabad", "fooddelivery", "swiggy", "zomato"]
QUERY = "swiggy OR zomato OR \"uber eats\""
LIMIT_PER_SUB = 300

# Reddit client
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
)

# Collect posts
rows = []
for sub in SUBS:
    for post in reddit.subreddit(sub).search(QUERY, sort="new", time_filter="month", limit=LIMIT_PER_SUB):
        rows.append({
            "platform": "reddit",
            "app": "mixed",
            "source": f"r/{sub}",
            "reviewId": post.id,
            "userName": str(post.author) if post.author else None,
            "score": post.score,
            "at": datetime.fromtimestamp(post.created_utc),
            "content": f"{post.title}\n{post.selftext or ''}".strip()
        })

# Save output
OUT_PATH = os.path.join("data", "raw", f"reddit_{datetime.now().strftime('%Y%m%d_%H%M')}.csv")
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
pd.DataFrame(rows).to_csv(OUT_PATH, index=False)
print(f"Saved: {OUT_PATH} | rows={len(rows)}")
