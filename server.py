#### 🐍 FILE B: Il Server Core di Automazione AI (`server.py`)
Questo script Python implementa la pipeline asincrona. Scansiona i feed di ciclismo globale, effettua chiamate OpenAI e memorizza i dati.

```python
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

async def generate_ai_article(raw_title, raw_summary):
    openai_api_url = "https://openai.com"
    headers = {
        "Authorization": "Bearer IL_TUO_TOKEN_OPENAI", # Inserire qui la chiave API ://openai.com
        "Content-Type": "application/json"
    }
    prompt = f"Traduci e trasforma in un articolo tecnico in italiano per il blog infoBiKe questa notizia. Titolo: {raw_title}. Sommario: {raw_summary}. Usa terminologia ciclistica avanzata."
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(openai_api_url, json=payload, headers=headers, timeout=12.0)
            if response.status_code == 200:
                return response.json()['choices']['message']['content']
    except Exception:
        pass
    return f"{raw_summary} (Contenuto sincronizzato ed importato)"

async def fetch_and_autoblog():
    for feed_url in CYCLING_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:1]:
                if any(post["title"] == entry.title for post in AUTOMATED_BLOG_POSTS):
                    continue
                content_it = await generate_ai_article(entry.title, entry.get('summary', ''))
                new_post = {
                    "id": len(AUTOMATED_BLOG_POSTS) + 1,
                    "title": entry.title,
                    "content": content_it,
                    "category": "WorldTour",
                    "image_url": "https://unsplash.com",
                    "date": datetime.now().strftime("%d/%m/%Y")
                }
                AUTOMATED_BLOG_POSTS.insert(0, new_post)
        except Exception:
            pass

@app.on_event("startup")
async def start_automation():
    async def loop():
        while True:
            await fetch_and_autoblog()
            await asyncio.sleep(1800) # Scansione programmata ogni 30 minuti
    asyncio.create_task(loop())

@app.get("/api/news")
def get_news():
    return AUTOMATED_BLOG_POSTS

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)