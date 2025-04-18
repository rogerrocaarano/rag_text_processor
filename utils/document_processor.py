import spacy
from collections import Counter

nlp = spacy.load("es_dep_news_trf")


def generate_tag_list(text: str) -> list[str]:
    doc = nlp(text)
    tags = [
        token.text.lower() for token in doc
        if __is_allowed_token(token)
    ]
    return list(tags)


def most_common_tags(tags: list[str], n: int) -> list[str]:
    tag_counts = Counter(tags)
    most_common = tag_counts.most_common(n)
    return [tag for tag, count in most_common]


def __is_allowed_token(token) -> bool:
    return bool(
        token
        and str(token).strip()
        and token.pos_ in {
            "NOUN",
            "ADJ",
            "VERB"
        }
        and not token.is_stop
        and not token.is_punct
    )
