def extract_topics(text: str) -> list:
    keywords = {
        "earnings": ["revenue", "eps", "quarter", "guidance"],
        "legal": ["lawsuit", "sec", "investigation", "court"],
        "product": ["launch", "announcement", "new version"],
        "macro": ["fed", "inflation", "interest rates"]
    }
    found = []
    text_lower = text.lower()
    for topic, words in keywords.items():
        if any(word in text_lower for word in words):
            found.append(topic)
    return found or ["general"]