import feedparser
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import asyncio

app = FastAPI(title="infoBiKe Server Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AUTOMATED_BLOG_POSTS = []
CYCLING_FEEDS = [
    "https://bicycleretailer.com",
    "https://cyclingweekly.com"
]

async def fetch_and_autoblog():
    print("infoBiKe System: Scansione feed e aggiornamento notizie...")
    for feed_url in CYCLING_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:2]:
                if any(post["title"] == entry.title for post in AUTOMATED_BLOG_POSTS):
                    continue
                
                summary_clean = entry.get('summary', 'Clicca per leggere i dettagli dell\'hardware.')
                if len(summary_clean) > 200:
                    summary_clean = summary_clean[:200] + "..."

                new_post = {
                    "id": len(AUTOMATED_BLOG_POSTS) + 1,
                    "title": entry.title,
                    "content": summary_clean,
                    "category": "WorldTour",
                    "image_url": "https://unsplash.com",
                    "date": datetime.now().strftime("%d/%m/%Y - %H:%M")
                }
                AUTOMATED_BLOG_POSTS.insert(0, new_post)
                print(f"Nuova notizia caricata: {entry.title}")
        except Exception as e:
            print(f"Errore scansione: {e}")

@app.on_event("startup")
async def start_automation():
    async def loop():
        while True:
            await fetch_and_autoblog()
            await asyncio.sleep(600)
    asyncio.create_task(loop())

@app.get("/api/news")
def get_news():
    return AUTOMATED_BLOG_POSTS

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
