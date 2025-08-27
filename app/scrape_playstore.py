# app/scrape_playstore.py
import os
import pandas as pd
from google_play_scraper import reviews, Sort
from datetime import datetime


APPS = {
"Swiggy": "in.swiggy.android",
"Zomato": "com.application.zomato",
"UberEats": "com.ubercab.eats" # may be inactive in India; included for global use
}


OUT_PATH = os.path.join("data", "raw", f"playstore_{datetime.now().strftime('%Y%m%d_%H%M')}.csv")
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)


all_rows = []


for app_name, app_id in APPS.items():
    try:
        batch, _ = reviews(
            app_id,
            lang='en',
            country='in',
            sort=Sort.NEWEST,
            count=2000 # keep small for demo; raise if needed
        )
        for r in batch:
            all_rows.append({
                "platform": "playstore",
                "app": app_name,
                "source": app_id,
                "reviewId": r.get("reviewId"),
                "userName": r.get("userName"),
                "score": r.get("score"),
                "at": r.get("at"),
                "content": r.get("content", "")
    })
    except Exception as e:
        print(f"[WARN] {app_name} failed: {e}")


pd.DataFrame(all_rows).to_csv(OUT_PATH, index=False)
print(f"Saved: {OUT_PATH}")