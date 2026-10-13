import os
from dotenv import load_dotenv

try:
    import tweepy
except Exception as e:
    tweepy = None
    print(f"[twitter_fetcher] Error: {e}")

load_dotenv()

# Bearer token is all you need for read-only search
# Add to your .env: TWITTER_BEARER_TOKEN=your_token_here
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "").strip()


def _is_valid_token(token: str) -> bool:
    if not token or len(token) < 30:
        return False
    lower = token.lower()
    if any(p in lower for p in ["your_", "token", "default", "dummy", "placeholder", "optional"]):
        return False
    return True


def fetch_tweets(ticker: str, max_tweets: int = 20) -> list[dict]:
    try:
        if tweepy is None:
            return []

        if not _is_valid_token(BEARER_TOKEN):
            # Not configured or placeholder — skip silently without errors
            return []

        client = tweepy.Client(bearer_token=BEARER_TOKEN)
        query = f"${ticker} lang:en -is:retweet"
        response = client.search_recent_tweets(
            query=query,
            max_results=max_tweets,
            tweet_fields=["created_at", "text", "author_id"]
        )

        if not response.data:
            return []

        return [_normalize(tweet, ticker) for tweet in response.data]

    except Exception as e:
        print(f"[twitter_fetcher] Error fetching {ticker}: {e}")
        return []


def _normalize(tweet, ticker: str) -> dict:
    try:
        created_at = getattr(tweet, "created_at", None)
        return {
            "source":       "twitter",
            "ticker":       ticker,
            "title":        "",
            "body":         getattr(tweet, "text", ""),
            "published_at": created_at.isoformat() if created_at else "",
            "url":          f"https://twitter.com/i/web/status/{getattr(tweet, 'id', '')}",
        }
    except Exception as e:
        print(f"[twitter_fetcher] Error: {e}")
        return {}
