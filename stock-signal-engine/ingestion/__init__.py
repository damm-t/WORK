from .news_fetcher import fetch_news
from .twitter_fetcher import fetch_tweets
from .earnings_fetcher import fetch_earnings
from dotenv import load_dotenv

load_dotenv()

def fetch_all(ticker: str) -> list[dict]:
    try:
        results = []
        news = fetch_news(ticker)
        earnings = fetch_earnings(ticker)
        tweets = fetch_tweets(ticker)

        for batch in [news, earnings, tweets]:
            if batch:
                results.extend(batch)

        return results
    except Exception as e:
        print(f"[fetch_all] Error for {ticker}: {e}")
        return []
