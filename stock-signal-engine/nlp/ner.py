import re

try:
    import spacy
except Exception as e:
    spacy = None
    print(f"[ner] Error: {e}")

nlp = None
TICKER_PATTERN = re.compile(r'\$?[A-Z]{2,5}\b')


def _get_nlp():
    try:
        global nlp

        if spacy is None:
            return None

        if nlp is None:
            nlp = spacy.load("en_core_web_sm")

        return nlp
    except Exception as e:
        print(f"[ner] Error: {e}")
        return None


def extract_entities(article: dict) -> dict:
    try:
        article_data = dict(article or {})
        title = str(article_data.get("title", ""))
        body = str(article_data.get("body", ""))
        raw_text = f"{title} {body}".strip()
        entities = []

        nlp_model = _get_nlp()
        if nlp_model is not None and raw_text:
            doc = nlp_model(raw_text)
            for ent in doc.ents:
                if ent.label_ in ["ORG", "GPE"]:
                    entities.append(ent.text)

        for match in TICKER_PATTERN.findall(raw_text):
            entities.append(match)

        article_data["entities"] = list(dict.fromkeys([entity for entity in entities if entity]))
        return article_data
    except Exception as e:
        print(f"[extract_entities] Error: {e}")
        article_data = dict(article or {})
        article_data["entities"] = []
        return article_data
