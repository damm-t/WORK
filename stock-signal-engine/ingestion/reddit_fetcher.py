import os
import praw
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

# Read from .env — never hardcode credentials
REDDIT_CLIENT_ID     = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USERNAME      = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD      = os.getenv("REDDIT_PASSWORD")
REDDIT_USER_AGENT    = os.getenv("REDDIT_USER_AGENT", "stock-signal-bot/1.0")

# Subreddits we care about — like a constant list in C#
SUBREDDITS = ["wallstreetbets", "stocks", "investing"]


def fetch_reddit(ticker: str, max_posts: int = 20) -> list[dict]:
    """
    Search Reddit posts mentioning a ticker across finance subreddits.
    Returns normalized list of post dicts.
    """

    # PRAW handles the HTTP for you — no requests.get() needed
    # Think of this like: var client = new RedditClient(credentials)
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD,
        user_agent=REDDIT_USER_AGENT,
    )

    results = []  # like var results = new List<dict>()

    try:
        for subreddit_name in SUBREDDITS:
            subreddit = reddit.subreddit(subreddit_name)

            # .search() queries posts — like a LINQ .Where() on the subreddit
            for submission in subreddit.search(ticker, limit=max_posts):
                results.append(_normalize(submission, ticker))

    except Exception as e:
        print(f"[reddit_fetcher] Error fetching {ticker}: {e}")

    return results


def _unix_to_iso(unix_timestamp: float) -> str:
    """
    Convert Unix timestamp → ISO8601 UTC string.
    Reddit gives you created_utc as a float like 1714500000.0
    We want "2024-04-30T22:00:00+00:00"
    """
    # datetime.fromtimestamp with tz=UTC — like DateTimeOffset.FromUnixTimeSeconds in C#
    dt = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
    return dt.isoformat()


def _normalize(submission, ticker: str) -> dict:
    """Map a raw PRAW submission → our standard schema."""
    return {
        "source":       "reddit",
        "ticker":       ticker,
        "title":        submission.title,
        "body":         submission.selftext or "",   # selftext = post body, "" if link post
        "published_at": _unix_to_iso(submission.created_utc),
        "url":          f"https://reddit.com{submission.permalink}",
    }