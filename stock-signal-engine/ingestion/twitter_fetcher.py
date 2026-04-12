import os
import tweepy
from datetime import timezone
from dotenv import load_dotenv

load_dotenv()

# Bearer token is all you need for read-only search
# Add to your .env: TWITTER_BEARER_TOKEN=your_token_here
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")


def fetch_tweets(ticker: str, max_tweets: int = 20) -> list[dict]:
    """
    Search recent tweets mentioning a stock ticker as a cashtag.
    e.g. ticker="AAPL" searches for "$AAPL"
    Returns normalized list of tweet dicts.
    """

    # tweepy.Client handles HTTP for you — same idea as praw.Reddit()
    client = tweepy.Client(bearer_token=BEARER_TOKEN)

    try:
        # Cashtag format: $AAPL — that's how traders tag stocks on Twitter
        query = f"${ticker} lang:en -is:retweet"  # exclude retweets, English only

        # tweet_fields tells the API what extra data to return
        # created_at and author_id are not included by default — you must ask
        response = client.search_recent_tweets(
            query=query,
            max_results=max_tweets,
            tweet_fields=["created_at", "text", "author_id"]
        )

        # If no tweets found, response.data is None — not an empty list!
        # This is a common tweepy gotcha
        if not response.data:
            return []

        return [_normalize(tweet, ticker) for tweet in response.data]

    except Exception as e:
        print(f"[twitter_fetcher] Error fetching {ticker}: {e}")
        return []


def _normalize(tweet, ticker: str) -> dict:
    """Map a raw tweepy Tweet object → our standard schema."""
    return {
        "source":       "twitter",
        "ticker":       ticker,
        "title":        "",   # tweets have no title — empty string keeps schema consistent
        "body":         tweet.text,
        "published_at": tweet.created_at.isoformat(),  # already a datetime object, unlike Reddit
        "url":          f"https://twitter.com/i/web/status/{tweet.id}",
    }