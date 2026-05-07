from .preprocessor import preprocess
from .finbert      import analyze_sentiment
from .ner          import extract_entities


def analyze_sentiment_only(article: dict) -> dict:
    try:
        article_data = preprocess(article)
        if not article_data:
            return {}

        article_data = analyze_sentiment(article_data)
        return article_data if article_data else {}
    except Exception as e:
        print(f"[analyze_sentiment_only] Error: {e}")
        return {}


def analyze(article: dict) -> dict:
    try:
        article_data = analyze_sentiment_only(article)
        if not article_data:
            return {}

        article_data = extract_entities(article_data)
        return article_data if article_data else {}
    except Exception as e:
        print(f"[analyze] Error: {e}")
        return {}
