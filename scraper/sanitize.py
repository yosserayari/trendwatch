import re
import unicodedata


def sanitize_text(text: str, max_length: int = 200) -> str:
    if not isinstance(text, str):
        text = str(text)
    text = unicodedata.normalize("NFKC", text)
    text = "".join(
        ch for ch in text
        if unicodedata.category(ch)[0] != "C" or ch in ("\n", "\t")
    )
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = text.replace("|", "-")
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > max_length:
        text = text[:max_length - 1].rstrip() + "…"
    return text


def sanitize_url(url: str) -> str | None:
    if not isinstance(url, str):
        return None
    url = url.strip()
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return None


def sanitize_item(item: dict) -> dict | None:
    clean_url = sanitize_url(item.get("url", ""))
    if clean_url is None:
        return None
    return {
        "title": sanitize_text(item.get("title", "")),
        "url": clean_url,
        "source": sanitize_text(item.get("source", ""), max_length=50),
    }