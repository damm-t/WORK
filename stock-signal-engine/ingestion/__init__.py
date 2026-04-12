from .news_fetcher     import fetch_news
from .reddit_fetcher   import fetch_reddit
from .twitter_fetcher  import fetch_tweets
from .earnings_fetcher import fetch_earnings
from dotenv import load_dotenv

load_dotenv()

def fetch_all(ticker: str) -> list[dict]:
    """
    Fetch from all sources for a given ticker.
    Returns combined normalized list.
    """
    try :
        # declare a empty dict 
        results = []

        # fetching
        news = fetch_news(ticker)
        earning = fetch_earnings(ticker)
        reddit = fetch_reddit(ticker)
        tweets = fetch_tweets(ticker)

        # in case of empty part 
        for batch in [news, earning, reddit, tweets]:
            if batch :
                results.extend(batch)

        return results
        
    except Exception as e:
        print(f"[fetch_all] Error for {ticker}: {e}")
        return []
    # HINT: call all 4 fetchers and combine their lists
    # HINT: in Python you combine lists with +
    # e.g. [1,2] + [3,4] = [1,2,3,4]
    