"""Text cleaning utilities for downstream processing."""

import re

def clean_text(text: str) -> str:
    """Normalize and clean text for parsing or embedding.

    Steps might include: lowercasing, trimming, removing excessive whitespace,
    and optionally stripping PII or markup.
    """
    if text is None:
        return ""
    s = text.strip()
    s = s.replace("\r", " ").replace("\n", " ")
    s = re.sub(r"\s+", " ", s)
    return s
