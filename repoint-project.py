#!/usr/bin/env python3
"""Change where one project card links, in both index.html and build-southbaw.py.

Used when moving a project from Netlify/Cloudflare into this repo.

Usage:
    python3 repoint-project.py OLD_URL NEW_URL

Example:
    python3 repoint-project.py https://tank-tactics-retro-reload.netlify.app/ \\
        https://briananthonysonnier.com/tank-tactics/

Refuses unless OLD_URL appears exactly once in each file.
"""
import json, os, re, sys

if len(sys.argv) != 3:
    sys.exit(__doc__)
OLD, NEW = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))

# ---- index.html: edit the decoded page template, re-encode safely
p = os.path.join(HERE, "index.html")
raw = open(p, encoding="utf-8").read()
m = re.search(r'(<script type="__bundler/template"[^>]*>)(.*?)(</script>)', raw, re.S)
if not m:
    sys.exit("no __bundler/template block")
page = json.loads(m.group(2).strip().replace("<\\/", "</"))
n = page.count("url: '%s'" % OLD)
if n != 1:
    sys.exit("index.html: expected 1 card with url %s, found %d" % (OLD, n))
page = page.replace("url: '%s'" % OLD, "url: '%s'" % NEW)
out = raw[:m.start(2)] + json.dumps(page).replace("</", "<\\/") + raw[m.end(2):]
for kind, body in re.findall(r'<script type="(__bundler/[a-z_]+)"[^>]*>(.*?)</script>', out, re.S):
    json.loads(body.strip())
json.loads(re.search(r'id="__slotstate">(.*?)</script>', out, re.S).group(1))
open(p, "w", encoding="utf-8").write(out)
print("  ok    index.html card now links to", NEW)

# ---- build-southbaw.py: keep a rebuild from undoing the move
b = os.path.join(HERE, "build-southbaw.py")
s = open(b, encoding="utf-8").read()
n = s.count('"%s"' % OLD)
if n != 1:
    sys.exit("build-southbaw.py: expected 1 entry with url %s, found %d" % (OLD, n))
open(b, "w", encoding="utf-8").write(s.replace('"%s"' % OLD, '"%s"' % NEW))
print("  ok    build-southbaw.py updated")
