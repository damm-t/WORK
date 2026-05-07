try:
    from transformers import pipeline
except Exception as e:
    pipeline = None
    print(f"[finbert] Error: {e}")

finbert = None


def _get_finbert():
    try:
        global finbert

        if pipeline is None:
            return None

        if finbert is None:
            finbert = pipeline("text-classification", model="ProsusAI/finbert")

        return finbert
    except Exception as e:
        print(f"[finbert] Error: {e}")
        return None

def analyze_sentiment(article: dict) -> dict:
    try:
        article_data = dict(article or {})
        text = str(article_data.get("clean_text", ""))[:512]
        if not text:
            article_data["sentiment"] = "neutral"
            article_data["sentiment_score"] = 0.0
            return article_data

        finbert_model = _get_finbert()
        if finbert_model is None:
            article_data["sentiment"] = "neutral"
            article_data["sentiment_score"] = 0.0
            return article_data

        result = finbert_model(text)
        top = result[0] if result else {}
        article_data["sentiment"] = str(top.get("label", "neutral")).lower()
        article_data["sentiment_score"] = round(float(top.get("score", 0.0) or 0.0), 4)
        return article_data
    except Exception as e:
        print(f"[analyze_sentiment] Error: {e}")
        article_data = dict(article or {})
        article_data["sentiment"] = "neutral"
        article_data["sentiment_score"] = 0.0
        return article_data
