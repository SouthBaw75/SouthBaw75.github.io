#!/usr/bin/env python3
"""Add one project card to a built index.html.

The works list lives in the page template (inside <script type="__bundler/template">)
and each card's screenshot lives base64-encoded in the <script id="__slotstate"> block,
keyed by the card's id. This adds an entry to both.

Same convention as build-southbaw.py: the template is decoded, edited, and re-encoded
with json.dumps, so quoting can never be corrupted by hand.

Usage:
    python3 add-project.py TITLE TYPE TAG URL [IMAGE]

    TITLE   card heading, e.g. "AEGIS"
    TYPE    the line under it, e.g. "ORBITAL DEFENSE"
    TAG     game | app | web  (which filter tab it belongs to)
    URL     where the card links
    IMAGE   file in img/ to use as the thumbnail; omit for a plain title tile

Example:
    python3 add-project.py "AEGIS" "ORBITAL DEFENSE" game \\
        "https://briananthonysonnier.com/aegis/" aegis.jpg

Refuses if a card with that title is already there, so it is safe to re-run.
"""
import base64, json, mimetypes, os, re, sys

if len(sys.argv) < 5:
    sys.exit(__doc__)
TITLE, TYPE, TAG, URL = sys.argv[1:5]
IMAGE = sys.argv[5] if len(sys.argv) > 5 else None
if TAG not in ("game", "app", "web"):
    sys.exit("TAG must be game, app or web")

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "index.html")
raw = open(PATH, encoding="utf-8").read()

m = re.search(r'(<script type="__bundler/template"[^>]*>)(.*?)(</script>)', raw, re.S)
if not m:
    sys.exit("no __bundler/template block")
page = json.loads(m.group(2).strip().replace("<\\/", "</"))

wm = re.search(r"const works = \[(.*?)\n    \];", page, re.S)
if not wm:
    sys.exit("works array not found")
rows = wm.group(1)
if "title: '%s'" % TITLE.replace("'", "\\'") in rows:
    sys.exit("%s is already on the site - nothing to do" % TITLE)

ids = [int(i) for i in re.findall(r"id: '(\d+)'", rows)]
new_id = max(ids) + 1
print("adding as card %d (%d already there)" % (new_id, len(ids)))

q = lambda s: s.replace("\\", "\\\\").replace("'", "\\'")
row = ("      { id: '%s', n: '%02d', title: '%s', type: '%s', year: 'LIVE', tag: '%s', url: '%s' },"
       % (new_id, new_id, q(TITLE), q(TYPE), TAG, URL))

# keep the groups together: land after the last row that already has this tag,
# so a new game sits with the games rather than below the websites
tagged = [t for t in re.finditer(r"^ *\{ id: '\d+'.*?tag: '%s'.*?\},$" % TAG, rows, re.M)]
if tagged:
    at = wm.start(1) + tagged[-1].end()
    print("  ok    placed after the last '%s' card" % TAG)
else:
    at = wm.end(1)
    print("  ok    no '%s' cards yet; placed at the end" % TAG)
page = page[:at] + "\n" + row + page[at:]

out = raw[:m.start(2)] + json.dumps(page).replace("</", "<\\/") + raw[m.end(2):]
print("  ok    works row")

if IMAGE:
    p = os.path.join(HERE, "img", IMAGE)
    if not os.path.exists(p):
        sys.exit("missing image " + p)
    sm = re.search(r'(id="__slotstate">)(.*?)(</script>)', out, re.S)
    if not sm:
        sys.exit("no __slotstate block")
    slots = json.loads(sm.group(2).replace("<\\/", "</"))
    mime = mimetypes.guess_type(p)[0] or "image/jpeg"
    b64 = base64.b64encode(open(p, "rb").read()).decode()
    slots["retro-work-%d" % new_id] = {"u": "data:%s;base64,%s" % (mime, b64), "s": 1, "x": 0, "y": 0}
    out = out[:sm.start(2)] + json.dumps(slots, separators=(",", ":")).replace("</", "<\\/") + out[sm.end(2):]
    print("  ok    thumbnail (%.2f MB of images in %d slots)"
          % (sum(len(v["u"]) for v in slots.values()) / 1e6, len(slots)))
else:
    print("  --    no image; the card shows a title tile")

for kind, body in re.findall(r'<script type="(__bundler/[a-z_]+)"[^>]*>(.*?)</script>', out, re.S):
    json.loads(body.strip())
    print("  json ok:", kind)
json.loads(re.search(r'id="__slotstate">(.*?)</script>', out, re.S).group(1))
print("  json ok: __slotstate")

open(PATH, "w", encoding="utf-8").write(out)
print("\nwrote %s  (%.2f MB)" % (PATH, os.path.getsize(PATH) / 1e6))
