import re

def preprocess(article: dict) -> dict:
    """
    Takes a raw article dict from Layer 1.
    Adds "clean_text" key and returns the enriched dict.
    """

    # Step 1: combine title + body
    # article["title"] not dict.title — article is your variable, dict is the type
    text = article["title"] + " " + article["body"]

    # Step 2: lowercase — must SAVE the result back
    text = text.lower()

    # Step 3: remove URLs
    text = re.sub(r"http\S+", "", text)

    # Step 4: remove special characters — keep only letters, numbers, spaces
    text = re.sub(r"[^a-z0-9\s]", "", text)

    # Step 5: collapse extra whitespace
    # "hello   world" → "hello world"
    text = " ".join(text.split())

    # Step 6: add clean_text to article dict and return
    # dict["key"] = value — like dict.Add("key", value) in C#
    article["clean_text"] = text
    return article