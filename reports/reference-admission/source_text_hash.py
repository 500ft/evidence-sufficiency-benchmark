"""Canonical visible-text hash v2 for the pinned Ansys HTML source pages.

It matches the Claude review's digests for these pages and also removes uppercase
SCRIPT/STYLE tags. It is not a guarantee that the page will never change.
Usage: python3 reports/reference-admission/source_text_hash.py page.html [...]
"""

import hashlib
import html
import re
import sys
from pathlib import Path


def canonical_text(raw):
    text = raw.decode("utf-8", errors="replace")
    text = re.sub(r"<script.*?</script>|<style.*?</style>", "", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def digest(raw):
    return hashlib.sha256(canonical_text(raw).encode("utf-8")).hexdigest()


if __name__ == "__main__":
    for name in sys.argv[1:]:
        print(digest(Path(name).read_bytes()), name)
