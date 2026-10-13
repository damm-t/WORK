from .news_fetcher import fetch_news
from .twitter_fetcher import fetch_tweets
from .earnings_fetcher import fetch_earnings
from dotenv import load_dotenv

load_dotenv()

def fetch_all(ticker: str) -> list[dict]:
    try:
        results = []
        news = fetch_news(ticker)
        if news:
            results.extend(news)

        # Only query SEC filings if breaking news feed is sparse
        if len(results) < 3:
            earnings = fetch_earnings(ticker)
            if earnings:
                results.extend(earnings)

        tweets = fetch_tweets(ticker)
        if tweets:
            results.extend(tweets)

        return results
    except Exception as e:
        print(f"[fetch_all] Error for {ticker}: {e}")
        return []
