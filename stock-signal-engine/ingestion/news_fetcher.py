import os 
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2/everything"

def fetch_news(ticker: str, max_articles: int = 20 ) -> list[dict]:
    """
    fetching the recent news article for a given stock ticker.
    Return a list of normalized article dicts.
    """

    param = {
        "q" : f"{ticker} stock OR earnings Or revenue",
        "apiKey" : NEWS_API_KEY,
        "language" : "en",
        "sortBy" : "publishAt",
        "pageSize" : "max_articles"
    }
    
    try :
        response = requests.get(BASE_URL, params = param)    
        response.raise_for_status() # throw error such as 400 or 500 
        data = response.json()

        articles = data.get("articles", []) # .get() = safe access, return [] if missing
        # same as the logic of ?? "" 

        #listing the comprehension - Python's compact way to loop + filter into a list 
        return [
            _normalize(articles, ticker)
            for article in articles
            if article.get("title") != "[Removed]" #skip the deleted articles 
        ]

    except Exception as e :
        #dont crash the whole prgrammes when error, so we returning empty or error 
        print(f"[news_fetcher] Error Fetching {ticker} : {e}")
        return [] # in trading system, silent failures -> crashes 

def _normalize(article : dict, ticker: str) -> dict :
    """
    Maps a raw NewsAPI article into -> standard scheme in our system 
    """

    # dict literal - like new Dictionary <string, object> in C#
    return {
        "source":       "newsapi",
        "ticker":       ticker,
        "title ":       article.get("title", ""),
        "body":         article.get("content") or article.get("description") or "",
        "publish_At":   article.get("publishAt", ""),
        "url":          article.get("url", "")
    }