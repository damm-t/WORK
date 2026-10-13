import logging
from datetime import datetime, timezone
import math
from zoneinfo import ZoneInfo

from .preprocessor import preprocess
from .finbert      import analyze_sentiment
from .ner          import extract_entities

logger = logging.getLogger(__name__)

# Default half-life for financial news sentiment (in hours).
# In active trading, market impact of breaking news decays by ~50% every 18 hours.
DEFAULT_HALF_LIFE_HOURS = 18.0


def compute_time_decay(published_at_value, half_life_hours: float = DEFAULT_HALF_LIFE_HOURS) -> tuple[float, float]:
    """
    Calculates the age in hours and exponential decay weight for a news article.

    Formula:
        w(t) = 2 ** (-age_hours / half_life_hours)
    
    Returns:
        (age_hours, decay_weight) where decay_weight is in (0.0, 1.0].
    """
    if not published_at_value:
        return 0.0, 1.0

    try:
        dt = None
        if isinstance(published_at_value, (int, float)):
            dt = datetime.fromtimestamp(float(published_at_value), tz=timezone.utc)
        elif isinstance(published_at_value, datetime):
            dt = published_at_value if published_at_value.tzinfo else published_at_value.replace(tzinfo=timezone.utc)
        elif isinstance(published_at_value, str):
            clean_str = published_at_value.strip()
            if not clean_str:
                return 0.0, 1.0
            # Handle ISO format with trailing 'Z'
            if clean_str.endswith("Z"):
                clean_str = clean_str[:-1] + "+00:00"
            try:
                dt = datetime.fromisoformat(clean_str)
                if not dt.tzinfo:
                    dt = dt.replace(tzinfo=timezone.utc)
            except Exception:
                # Fallback to dateutil / strptime formats
                for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
                    try:
                        dt = datetime.strptime(clean_str, fmt).replace(tzinfo=timezone.utc)
                        break
                    except Exception:
                        pass

        if not dt:
            return 0.0, 1.0

        now_utc = datetime.now(timezone.utc)
        delta_seconds = (now_utc - dt.astimezone(timezone.utc)).total_seconds()
        age_hours = max(0.0, delta_seconds / 3600.0)

        # Exponential decay: w = 2 ** (-age / half_life)
        hl = max(1.0, float(half_life_hours))
        decay_weight = max(0.001, min(1.0, 2.0 ** (-age_hours / hl)))
        return round(age_hours, 2), round(decay_weight, 4)

    except Exception as e:
        logger.debug(f"[compute_time_decay] Error parsing {published_at_value}: {e}")
        return 0.0, 1.0


def analyze_sentiment_only(article: dict, half_life_hours: float = DEFAULT_HALF_LIFE_HOURS) -> dict:
    try:
        article_data = preprocess(article)
        if not article_data:
            return {}

        article_data = analyze_sentiment(article_data)
        if not article_data:
            return {}

        # Apply Exponential Time Decay based on publication age
        pub_at = article_data.get("published_at")
        age_hours, decay_weight = compute_time_decay(pub_at, half_life_hours=half_life_hours)
        raw_score = float(article_data.get("sentiment_score", 0.0) or 0.0)
        decayed_score = round(raw_score * decay_weight, 4)

        article_data["age_hours"] = age_hours
        article_data["decay_weight"] = decay_weight
        article_data["raw_sentiment_score"] = raw_score
        article_data["decayed_sentiment_score"] = decayed_score
        # Update sentiment_score to reflect decayed conviction downstream
        article_data["sentiment_score"] = decayed_score

        return article_data
    except Exception as e:
        print(f"[analyze_sentiment_only] Error: {e}")
        return {}


def analyze(article: dict, half_life_hours: float = DEFAULT_HALF_LIFE_HOURS) -> dict:
    try:
        article_data = analyze_sentiment_only(article, half_life_hours=half_life_hours)
        if not article_data:
            return {}

        article_data = extract_entities(article_data)
        return article_data if article_data else {}
    except Exception as e:
        print(f"[analyze] Error: {e}")
        return {}


def directional_sentiment(article: dict, use_decay: bool = True) -> float:
    """
    Signed sentiment used for ranking: positive adds, negative subtracts,
    neutral = 0.
    """
    if use_decay:
        score = float(article.get("decayed_sentiment_score", article.get("sentiment_score", 0.0)) or 0.0)
    else:
        score = float(article.get("raw_sentiment_score", article.get("sentiment_score", 0.0)) or 0.0)

    label = str(article.get("sentiment", "neutral")).strip().lower()
    if label == "positive":
        return score
    if label == "negative":
        return -score
    return 0.0


def pick_best_article(articles: list, use_decay: bool = True) -> dict:
    """
    Strongest DIRECTIONAL headline for signal generation, taking into
    account temporal decay (fresh news takes precedence over stale news).

    Primary key   : directional_sentiment (+bull / -bear / 0 neutral with decay)
    Tie-breaker   : highest decayed score, then raw confidence
    """
    if not articles:
        return {}

    return max(
        articles,
        key=lambda a: (
            directional_sentiment(a, use_decay=use_decay),
            float(a.get("decayed_sentiment_score", a.get("sentiment_score", 0.0)) or 0.0),
            float(a.get("raw_sentiment_score", a.get("sentiment_score", 0.0)) or 0.0),
        ),
    )
