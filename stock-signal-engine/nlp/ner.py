import spacy

# Load spacy model once — same singleton pattern as FinBERT
nlp = spacy.load("en_core_web_sm")

# Common ticker-like patterns to look for
# e.g. "$AAPL" in tweets, "AAPL" in news
import re
TICKER_PATTERN = re.compile(r'\$?[A-Z]{2,5}\b')

def extract_entities(article: dict) -> dict:
    """
    Takes an article dict with "clean_text".
    Adds "entities" key — list of company names and tickers found.
    Returns enriched dict.
    """
    raw_text = article["title"] + " " + article["body"]
    doc = nlp(raw_text)

    entities = []

    #spacy entities - org and company
    for ent in doc.ents:
        if ent.label_ in ["ORG", "GPE"]:
            entities.append(ent.text)

    # regex matching with the ticker
    for match in TICKER_PATTERN.findall(clean_text):
        entities.append(match)

    article["entities"] = list(set(entities))


    # HINT: run spacy on the original title+body, not clean_text
    # (clean_text is lowercased — NER needs proper casing to work)
    # HINT: use article["title"] + " " + article["body"]

    # HINT: spacy gives you doc.ents — loop through them
    # each ent has ent.text and ent.label_
    # we only want label_ == "ORG" (organisations) or "GPE" (companies)

    # HINT: also find ticker patterns using TICKER_PATTERN.findall(text)
    # combine both into one list, remove duplicates with list(set(...))

    return article