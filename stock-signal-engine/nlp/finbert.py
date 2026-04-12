from transformers import pipeline

# Load FinBERT once at module level — expensive to load, do it only once
# Think of this like a static singleton in C#
finbert = pipeline("text-classification", model="ProsusAI/finbert")

def analyze_sentiment(article: dict) -> dict:
    """
    Takes an article dict that already has "clean_text" from preprocessor.
    Adds "sentiment" and "sentiment_score" keys.
    Returns enriched dict.
    """

    # Step 1: truncate FIRST before passing to FinBERT
    # FinBERT crashes on input longer than 512 tokens
    text = article["clean_text"][:512]

    # Step 2: call FinBERT — returns a list like:
    # [{"label": "positive", "score": 0.92}]
    result = finbert(text)

    # Step 3: grab index [0] — we passed one text, we get one result
    # result is a list, result[0] is the dict inside
    top = result[0]

    # Step 4: extract label and score
    # FinBERT returns plain dicts — use ["key"] not .key
    sentiment = top["label"]         # "positive" / "negative" / "neutral"
    score     = top["score"]         # float like 0.92

    # Step 5: add to article dict — like dict["key"] = value
    article["sentiment"]       = sentiment
    article["sentiment_score"] = round(score, 4)   # round to 4 decimal places

    return article