#!/usr/bin/env python3
"""Build a deployable index.html from the pristine Claude Design 'Southbaw' export.

The export is a design template: the portrait is real, everything else is
placeholder. This swaps in Brian's actual projects, drops the invented stats,
fixes the location, links the work cards, and supplies the footer the export
references via <dc-import> but never bundles.

Structure of the export:
  <head> ... </head>                      <- outer document
  <script type="__bundler/manifest">      <- JSON: gzipped fonts/textures
  <script type="__bundler/template">      <- JSON *string* holding the page HTML

Page edits are done on the DECODED template string and re-encoded with
json.dumps, so quoting can never be corrupted by hand.
"""
import base64, json, mimetypes, os, re, sys

HERE  = "/Users/briansonnier/Sites/briananthonysonnier.com"
SRC   = "/Users/briansonnier/Downloads/Southbaw Proper/Southbaw - Standalone.html"
STATE = "/Users/briansonnier/Downloads/Southbaw Proper/.image-slots.state.json"
OUT   = os.path.join(HERE, "index.html")

raw   = open(SRC, encoding="utf-8").read()
slots = json.load(open(STATE, encoding="utf-8"))
assert "__slotstate" not in raw, "SRC is not pristine - rebuild from the original export"

m = re.search(r'(<script type="__bundler/template"[^>]*>)(.*?)(</script>)', raw, re.S)
if not m:
    sys.exit("no __bundler/template block")
page = json.loads(m.group(2).strip())        # -> plain HTML, correctly unescaped
print("template decoded: %d chars" % len(page))

edits = []
def swap(old, new, label, count=1):
    global page
    if old not in page:
        sys.exit("MISSING: " + label)
    page = page.replace(old, new, count)
    edits.append(label)
    print("  ok   ", label)

# ---------------------------------------------------------------- projects
# Every live personal project. FET/Forum work tools, duplicate deploys, and
# RepDash (shows real behavioral-health client data) are deliberately out.
# Types come from each project's own title or on-screen copy - nothing invented.
PROJECTS = [
    # games
    ("1",  "01", "SUNSET RIDGE",     "IDLE RANCH GAME",           "game", "https://sunset-ridge-ranch-game.netlify.app/",           "sunsetridge.jpg"),
    ("2",  "02", "MONSTER MUNCH",    "ARCADE GAME",               "game", "https://monster-munch-bsonnier.netlify.app/",            "monstermunch.jpg"),
    ("3",  "03", "CRAWFISH KINGDOM", "BAYOU ADVENTURE",           "game", "https://crawfish-kingdom.netlify.app/",                  "crawfish.jpg"),
    ("4",  "04", "TANK TACTICS",     "RETRO TANK COMBAT",         "game", "https://tank-tactics-retro-reload.netlify.app/",         "tanktactics.jpg"),
    ("5",  "05", "SPELLCASTER SIEGE","SPELL DEFENSE",             "game", "https://spellcaster-siege.netlify.app/",                 "spellcaster.jpg"),
    ("6",  "06", "ORGANISM",         "CAVE DESCENT",              "game", "https://organism-game.netlify.app/",                     "organism.jpg"),
    ("7",  "07", "PLANET PARADE",    "SPACE EXPLORER",            "game", "https://planet-parade-explorer.netlify.app/",            "planetparade.jpg"),
    ("8",  "08", "GRID DEFENSE",     "ARCADE DEFENSE",            "game", "https://grid-defense.netlify.app/",                      "griddefense.jpg"),
    ("9",  "09", "DEEP VEIN",        "SPACE MINING",              "game", "https://deep-vein-bsonnier.netlify.app/",                "deepvein.jpg"),
    ("10", "10", "SPARKS",           "ELECTRICIAN SIDE-SCROLLER", "game", "https://sparks-electrician.netlify.app/",                "sparks.jpg"),
    ("12", "12", "BENNY'S BLACKBERRIES", "A STORY ABOUT SHARING", "game", "https://bennys-blackberries.netlify.app/",               "bennys.jpg"),
    ("13", "13", "LUKE'S ROAD TRIP", "DRIVING GAME",              "game", "https://lukes-road-trip-full-project.netlify.app/",      "lukes.jpg"),
    # hosted in this repo under aegis/ rather than on netlify
    ("26", "26", "AEGIS",            "ORBITAL DEFENSE",           "game", "https://briananthonysonnier.com/aegis/",                 "aegis.jpg"),
    ("27", "27", "WILDWOOD",         "FOREST SURVIVAL",           "game", "https://briananthonysonnier.com/wildwood/",              "wildwood.jpg"),
    ("28", "28", "BIOQUADICAL",      "MICROORGANISM SIM",         "game", "https://bioquadical-x2.bsonnier75.workers.dev/",         "bioquadical.jpg"),
    # apps and tools
    ("14", "14", "CAMPFIRE",         "PRIVATE SOCIAL APP",        "app",  "https://campfire-circles.netlify.app/",                  "campfire.jpg"),
    ("15", "15", "TIDAL PM",         "PROJECT MANAGEMENT",        "app",  "https://tidal-pm.netlify.app/",                          "tidal.jpg"),
    ("16", "16", "MTG LIFE COUNTER", "LIFE COUNTER",              "app",  "https://magicthegatheringlifecounter-southbaw.netlify.app/", "mtglife.jpg"),
    ("17", "17", "QSNAP",            "PHOTO TO QR",               "app",  "https://qsnap-app.netlify.app/",                         "qsnap.jpg"),
    ("18", "18", "ABIDE",            "APP",                       "app",  "https://abide-app-brian.netlify.app/",                   "abide.jpg"),
    ("20", "20", "VOXBOX",           "APP",                       "app",  "https://voxbox-app.netlify.app/",                        None),
    # sites
    ("21", "21", "THE LOOKING GLASS","ETCHED MIRROR STUDIO",      "web",  "https://looking-glass-studio.netlify.app/",              "lookingglass.jpg"),
    ("22", "22", "CASTAWAY PIZZA",   "RESTAURANT SITE",           "web",  "https://castaway-pizza-co.netlify.app/",                 "castaway.jpg"),
    ("23", "23", "LITTLE GLOW",      "ILLUSTRATED STORY",         "web",  "https://little-glow-story.netlify.app/",                 "littleglow.jpg"),
    ("24", "24", "MIRAGE",           "SHOP DEMO",                 "web",  "https://mirage-shop-demo.netlify.app/",                  "mirage.jpg"),
]

print("1. works array")
wm = re.search(r"const works = \[.*?\];", page, re.S)
if not wm:
    sys.exit("works array not found")
q = lambda s: s.replace("\\", "\\\\").replace("'", "\\'")   # BENNY'S / LUKE'S
rows = "\n".join(
    "      { id: '%s', n: '%s', title: '%s', type: '%s', year: 'LIVE', tag: '%s', url: '%s' },"
    % (i, n, q(t), q(ty), tag, url) for i, n, t, ty, tag, url, _ in PROJECTS)
page = page[:wm.start()] + "const works = [\n" + rows + "\n    ];" + page[wm.end():]
print("  ok    %d real projects" % len(PROJECTS))

# ---------------------------------------------------------------- card -> link
print("2. work cards link out")
swap('<div data-tilt="" style="background:#2b2926;border-radius:22px;padding:16px;',
     '<a href="{{ item.url }}" target="_blank" rel="noopener" data-tilt="" style="text-decoration:none;color:inherit;background:#2b2926;border-radius:22px;padding:16px;',
     "card open tag")
swap("""text-transform:uppercase;color:#b8ad97">{{ item.type }}</div>
        </div>
      </sc-for>""",
     """text-transform:uppercase;color:#b8ad97">{{ item.type }}</div>
        </a>
      </sc-for>""",
     "card close tag")

# ---------------------------------------------------------------- filters
print("3. filter tabs")
for old, new in [(">Motion<", ">Games<"), (">Identity<", ">Apps<"), (">Spatial<", ">Web<")]:
    swap(old, new, "tab " + new.strip("<>"))
for old, new in [('data-filter="film"', 'data-filter="game"'),
                 ('data-filter="book"', 'data-filter="app"'),
                 ('data-filter="series"', 'data-filter="web"')]:
    swap(old, new, "attr " + new)
swap("filter: 'film' }", "filter: 'game' }", "state film->game")
swap("filter: 'book' }", "filter: 'app' }",  "state book->app")
swap("filter: 'series' }", "filter: 'web' }", "state series->web")

# ---------------------------------------------------------------- stats out
print("4. remove invented stat cards")
i = page.find("<!-- swatch stat cards -->")
if i == -1:
    sys.exit("stat cards marker not found")
depth, end = 0, None
for mm in re.finditer(r"<div\b|</div>", page[i:]):
    depth += 1 if mm.group().startswith("<div") else -1
    if depth == 0:
        end = i + mm.end(); break
if end is None:
    sys.exit("could not balance stat cards")
cut = page[i:end]
assert len(re.findall(r"<div\b", cut)) == len(re.findall(r"</div>", cut)), "unbalanced cut"
page = page[:i] + page[end:]
print("  ok    removed %d divs, balanced" % len(re.findall(r"<div\b", cut)))

# ---------------------------------------------------------------- copy
print("5. copy")
swap("EST. 2019 — SOUTH BOSTON", "EST. MMXXV — SOUTH LOUISIANA", "location")
swap("The studio, the films, the ideas, the makers — an American design house, cataloged and kept like a worn record sleeve.",
     "Games, tools, and experiments — built at night in South Louisiana, cataloged and kept like a worn record sleeve.",
     "hero paragraph")

# ---------------------------------------------------------------- footer
print("6. footer")
FOOTER = """<footer style="border-top:1px solid rgba(242,237,227,.12);padding:60px 24px 50px;background:#1f1d1b">
  <div style="max-width:1180px;margin:0 auto;display:flex;flex-wrap:wrap;gap:30px;align-items:flex-start;justify-content:space-between">
    <div>
      <div style="font-family:'Gordan','Bai Jamjuree',sans-serif;font-size:32px;letter-spacing:.02em;color:#f2ede3">SOUTHBAW</div>
      <div style="font-family:'Space Mono',monospace;font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:#8a8073;margin-top:10px">Brian Anthony Sonnier &mdash; South Louisiana</div>
    </div>
    <div style="display:flex;flex-wrap:wrap;gap:14px">
      <a href="mailto:hello@briananthonysonnier.com" style="font-family:'Bai Jamjuree',sans-serif;font-weight:700;font-size:14px;letter-spacing:.06em;text-transform:uppercase;text-decoration:none;background:#c94e44;color:#2a1714;padding:15px 24px;border-radius:999px">Email me</a>
      <a href="https://github.com/SouthBaw75" target="_blank" rel="noopener" style="font-family:'Bai Jamjuree',sans-serif;font-weight:700;font-size:14px;letter-spacing:.06em;text-transform:uppercase;text-decoration:none;border:1px solid #c1ab85;color:#c1ab85;padding:15px 24px;border-radius:999px">GitHub</a>
    </div>
  </div>
  <div style="max-width:1180px;margin:36px auto 0;font-family:'Space Mono',monospace;font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:#6e675c">&copy; MMXXVI Brian Anthony Sonnier</div>
</footer>"""
swap('<dc-import name="SouthbawFooterRetro" hint-size="100%,360px"></dc-import>', FOOTER, "footer")

# ---------------------------------------------------------------- reassemble
# escape </ so an embedded </script> cannot terminate the host <script> tag
# (this is why the original export writes every / as /)
out = raw[:m.start(2)] + json.dumps(page).replace("</", "<\\/") + raw[m.end(2):]

# ---------------------------------------------------------------- image slots
print("7. image slots")
used = {"retro-poster": slots["retro-poster"]}
for i, n, t, ty, tag, url, img in PROJECTS:
    if img is None:                      # no usable screenshot; slot shows its title tile
        print("  --    retro-work-%s has no image (%s)" % (i, t))
        continue
    p = os.path.join(HERE, "img", img)
    if not os.path.exists(p):
        sys.exit("missing image " + p)
    mime = mimetypes.guess_type(p)[0] or "image/jpeg"
    b64 = base64.b64encode(open(p, "rb").read()).decode()
    used["retro-work-" + i] = {"u": "data:%s;base64,%s" % (mime, b64), "s": 1, "x": 0, "y": 0}
print("  ok    %d slots (%.1f MB of images)" % (len(used), sum(len(v["u"]) for v in used.values()) / 1e6))

patch = (
    '<script type="application/json" id="__slotstate">'
    + json.dumps(used, separators=(",", ":")).replace("</", "<\\/")
    + '</script>\n'
    '<script>(function(){var el=document.getElementById("__slotstate");'
    'var body=el?el.textContent:"{}";var of=window.fetch;'
    'window.fetch=function(u){try{if(String(u).indexOf(".image-slots.state.json")>-1){'
    'return Promise.resolve(new Response(body,{status:200,headers:{"Content-Type":"application/json"}}));'
    '}}catch(e){}return of.apply(this,arguments);};})();</script>\n'
)
META = (
    '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
    '<meta name="description" content="Southbaw - Brian Anthony Sonnier. Games, tools, and experiments built in South Louisiana.">\n'
    '<meta name="theme-color" content="#1F1D1B">\n'
    '<meta property="og:title" content="Southbaw - Brian Anthony Sonnier">\n'
    '<meta property="og:description" content="Games, tools, and experiments, built at night in South Louisiana.">\n'
    '<meta property="og:type" content="website">\n'
    '<meta property="og:url" content="https://briananthonysonnier.com/">\n'
)

# inject into the OUTER head only - it ends before the manifest script
head_end = out.find("</head>")
mani     = out.find('<script type="__bundler/manifest"')
assert 0 < head_end < mani, "outer </head> not where expected"
out = out[:head_end] + META + patch + out[head_end:]
out = out.replace("<title>Bundled Page</title>",
                  "<title>Southbaw — Brian Anthony Sonnier</title>", 1)
out = re.sub(r"<html>", '<html lang="en">', out, count=1)

# ---------------------------------------------------------------- verify
for kind, body in re.findall(r'<script type="(__bundler/[a-z_]+)"[^>]*>(.*?)</script>', out, re.S):
    json.loads(body.strip())
    print("  json ok:", kind)
json.loads(re.search(r'id="__slotstate">(.*?)</script>', out, re.S).group(1))
print("  json ok: __slotstate")

open(OUT, "w", encoding="utf-8").write(out)
print("\nwrote %s  (%.2f MB)  edits applied: %d" % (OUT, os.path.getsize(OUT) / 1e6, len(edits)))
