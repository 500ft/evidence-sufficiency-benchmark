"""Canonical visible-text hash v1 for the pinned Ansys HTML source pages.

This deliberately matches the method used for the Claude review's text hashes.
It is a content comparison, not a guarantee that the page will never change.
Usage: python3 reports/reference-admission/source_text_hash.py page.html [...]
"""

import hashlib
import html
import re
import sys
from pathlib import Path


def canonical_text(raw):
    text = raw.decode("utf-8", errors="replace")
    text = re.sub(r"<script.*?</script>|<style.*?</style>", "", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def digest(raw):
    return hashlib.sha256(canonical_text(raw).encode("utf-8")).hexdigest()


if __name__ == "__main__":
    for name in sys.argv[1:]:
        print(digest(Path(name).read_bytes()), name)
