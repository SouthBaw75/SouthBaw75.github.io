#!/usr/bin/env python3
"""Remove one project card from a built index.html (the counterpart to add-project.py).

Drops the card's row from the works list in the page template and its thumbnail from
the __slotstate block, so no orphaned image is left behind. Other cards keep their ids.

Usage:
    python3 remove-project.py "SCAVENGE RABBIT"

Matches the card title exactly (case-insensitive). Refuses if it isn't there.
"""
import json, os, re, sys

if len(sys.argv) != 2:
    sys.exit(__doc__)
TITLE = sys.argv[1].strip()

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "index.html")
raw = open(PATH, encoding="utf-8").read()

m = re.search(r'(<script type="__bundler/template"[^>]*>)(.*?)(</script>)', raw, re.S)
if not m:
    sys.exit("no __bundler/template block")
page = json.loads(m.group(2).strip().replace("<\\/", "</"))

rows = list(re.finditer(r"^ *\{ id: '(\d+)', n: '\d+', title: '((?:[^'\\]|\\.)*)'.*?\},\n", page, re.M))
hit = [r for r in rows if r.group(2).replace("\\'", "'").upper() == TITLE.upper()]
if not hit:
    sys.exit("%s is not on the site - nothing to do" % TITLE)
row = hit[0]
card_id = row.group(1)
page = page[:row.start()] + page[row.end():]
print("  ok    removed works row (card %s, %d left)" % (card_id, len(rows) - 1))

out = raw[:m.start(2)] + json.dumps(page).replace("</", "<\\/") + raw[m.end(2):]

sm = re.search(r'(id="__slotstate">)(.*?)(</script>)', out, re.S)
slots = json.loads(sm.group(2).replace("<\\/", "</"))
if slots.pop("retro-work-%s" % card_id, None) is not None:
    out = out[:sm.start(2)] + json.dumps(slots, separators=(",", ":")).replace("</", "<\\/") + out[sm.end(2):]
    print("  ok    removed thumbnail retro-work-%s" % card_id)
else:
    print("  --    card had no thumbnail")

for kind, body in re.findall(r'<script type="(__bundler/[a-z_]+)"[^>]*>(.*?)</script>', out, re.S):
    json.loads(body.strip())
    print("  json ok:", kind)
json.loads(re.search(r'id="__slotstate">(.*?)</script>', out, re.S).group(1))
print("  json ok: __slotstate")

open(PATH, "w", encoding="utf-8").write(out)
print("\nwrote %s  (%.2f MB)" % (PATH, os.path.getsize(PATH) / 1e6))
