from .preprocessor import preprocess
from .finbert      import analyze_sentiment
from .ner          import extract_entities


def analyze(article: dict) -> dict:
    """
    Run full NLP pipeline on a single article.
    preprocessor → finbert → ner
    Returns fully enriched article dict.
    """

    try :

        article = preprocess(article)
        article = analyze_sentiment(article)
        article = extract_entities(article)
        

        return article

    except Exception as e :
        print(f"[fetch_all] Error for {article}: {e}")
        return []
    

    # HINT: same pattern as fetch_all in Layer 1
    # call each function, passing the result of the previous one
    # each function takes a dict and returns an enriched dict
    # wrap in try/except and return article unchanged if anything fails