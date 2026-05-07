import re


def preprocess(article: dict) -> dict:
    try:
        article_data = dict(article or {})
        title = str(article_data.get("title", ""))
        body = str(article_data.get("body", ""))
        text = f"{title} {body}".strip().lower()
        text = re.sub(r"http\S+", "", text)
        text = re.sub(r"[^a-z0-9\s]", "", text)
        text = " ".join(text.split())
        article_data["clean_text"] = text
        return article_data
    except Exception as e:
        print(f"[preprocessor] Error: {e}")
        return {}
