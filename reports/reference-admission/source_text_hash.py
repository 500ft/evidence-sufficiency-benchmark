"""Canonical visible-text hash v3 for the pinned Ansys HTML source pages.

It matches the Claude review's digests for these pages and parses tag variants
without an HTML-filtering regular expression. It does not guarantee permanence.
Usage: python3 reports/reference-admission/source_text_hash.py page.html [...]
"""

import hashlib
import html
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        elif not self.skip:
            self.parts.append(" ")

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1
        elif not self.skip:
            self.parts.append(" ")

    def handle_startendtag(self, tag, attrs):
        if not self.skip:
            self.parts.append(" ")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)

    def handle_entityref(self, name):
        if not self.skip:
            self.parts.append(f"&{name};")

    def handle_charref(self, name):
        if not self.skip:
            self.parts.append(f"&#{name};")

    def handle_comment(self, data):
        if not self.skip:
            self.parts.append(" ")


def canonical_text(raw):
    parser = VisibleText()
    parser.feed(raw.decode("utf-8", errors="replace"))
    return re.sub(r"\s+", " ", html.unescape("".join(parser.parts))).strip()


def digest(raw):
    return hashlib.sha256(canonical_text(raw).encode("utf-8")).hexdigest()


if __name__ == "__main__":
    for name in sys.argv[1:]:
        print(digest(Path(name).read_bytes()), name)
