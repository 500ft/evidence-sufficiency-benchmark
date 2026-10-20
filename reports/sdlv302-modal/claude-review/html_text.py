"""Extract visible text inside top-level <section> elements of a downloaded HTML page (stdlib only)."""
import sys
from html.parser import HTMLParser

class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.depth = 0; self.out = []; self.skip = 0
    def handle_starttag(self, t, a):
        a = dict(a)
        if t in ("script", "style"): self.skip += 1
        if t == "section": self.depth += 1
        if not self.depth: return
        if t in ("p", "br", "tr", "li", "h1", "h2", "h3", "h4", "div", "table"): self.out.append("\n")
        if t in ("td", "th"): self.out.append(" | ")
        if t == "img": self.out.append(f"[img alt={a.get('alt','')!r} src={a.get('src','')}]")
    def handle_endtag(self, t):
        if t in ("script", "style"): self.skip -= 1
        if t == "section": self.depth -= 1
    def handle_data(self, d):
        if self.depth and not self.skip: self.out.append(d)

p = P(); p.feed(open(sys.argv[1], encoding="utf-8").read())
print("\n".join(l.rstrip() for l in "".join(p.out).splitlines() if l.strip()))
