#!/usr/bin/env python3
"""Patch index.html in place: responsive layout, real menu, working search, head tags.

build-southbaw.py needs the pristine Claude Design export (in ~/Downloads) to run.
This script needs nothing but index.html, so it can be re-run on any machine.

It edits the DECODED page template inside the <script type="__bundler/template">
block, the same way build-southbaw.py does, then re-encodes with json.dumps so
quoting can never be corrupted by hand.

Idempotent: if the patch marker is already present it exits without touching the
file. If you ever re-run build-southbaw.py, run this afterwards to reapply.

Usage:  python3 patch-southbaw.py [path/to/index.html]
"""
import json, os, re, sys

MARKER = "sbw-patch-v1"
PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")

raw = open(PATH, encoding="utf-8").read()
if MARKER in raw:
    sys.exit("already patched (%s present) - nothing to do" % MARKER)

m = re.search(r'(<script type="__bundler/template"[^>]*>)(.*?)(</script>)', raw, re.S)
if not m:
    sys.exit("no __bundler/template block")
page = json.loads(m.group(2).strip().replace("<\\/", "</"))
print("template decoded: %d chars" % len(page))

edits = []
def swap(old, new, label, count=1):
    global page
    if old not in page:
        sys.exit("MISSING: " + label)
    page = page.replace(old, new, count)
    edits.append(label)
    print("  ok   ", label)

# ------------------------------------------------------------ 1. layout hooks
print("1. layout hooks")
swap('<section style="max-width:1240px;margin:0 auto;padding:34px 30px 0">',
     '<section id="top" class="sbw-sec" style="max-width:1240px;margin:0 auto;padding:34px 30px 0">',
     "hero section id")
swap('<section style="max-width:1240px;margin:0 auto;padding:46px 30px 60px">',
     '<section id="work" class="sbw-sec" style="max-width:1240px;margin:0 auto;padding:46px 30px 60px">',
     "work section id")
swap('<div style="background:var(--teal);border-radius:30px;padding:clamp(28px,4vw,52px);display:grid;grid-template-columns:1.25fr 0.85fr;gap:44px;align-items:center">',
     '<div id="sbw-hero" style="background:var(--teal);border-radius:30px;padding:clamp(28px,4vw,52px);display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,.85fr);gap:44px;align-items:center">',
     "hero grid (minmax so columns can shrink)")
swap('<div style="background:var(--sand);border-radius:10px;padding:14px;box-shadow:0 22px 50px rgba(0,0,0,.45);animation:scFloat 6s ease-in-out infinite">',
     '<div id="sbw-poster" style="background:var(--sand);border-radius:10px;padding:14px;box-shadow:0 22px 50px rgba(0,0,0,.45);animation:scFloat 6s ease-in-out infinite">',
     "poster frame id")
swap('<div id="sbw-grid" style="display:grid;grid-template-columns:repeat(3,1fr);gap:22px">',
     '<div id="sbw-grid" style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px">',
     "work grid (minmax so cards can shrink)")

# ------------------------------------------------------------ 2. responsive css
print("2. responsive css")
CSS = """
/* ---- %s: responsive ---- */
html,body{max-width:100%%;overflow-x:hidden}
body{scroll-behavior:smooth}
#top,#work{scroll-margin-top:100px}
#sbw-search-empty{display:none}
@media (max-width:1080px){
  #sbw-grid{grid-template-columns:repeat(2,minmax(0,1fr))!important}
}
@media (max-width:860px){
  #sbw-hero{grid-template-columns:minmax(0,1fr)!important;gap:30px!important;border-radius:22px!important}
  #sbw-poster{max-width:340px;width:100%%;margin:0 auto}
  #sbw-header{padding:0 16px!important}
}
@media (max-width:640px){
  #sbw-grid{grid-template-columns:minmax(0,1fr)!important;gap:16px!important}
  .sbw-sec{padding-left:18px!important;padding-right:18px!important}
  #sbw-header{height:68px!important}
  #sbw-logo{font-size:22px!important}
  #sbw-poster image-slot{height:240px!important}
  #sbw-searchbar{padding:18px!important}
  #sbw-searchbar input{font-size:17px!important}
}
""" % MARKER
swap("</style>\n</helmet>", CSS + "</style>\n</helmet>", "append media queries to helmet style")

# ------------------------------------------------------------ 3. head tags
# The bundler rebuilds <head> at runtime, so the outer document's <title> and
# og: tags never survive into the live DOM. Anything inside <helmet> does.
print("3. head tags (title, favicon, og) inside helmet")
ICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
        "%3Crect width='64' height='64' rx='14' fill='%231F1D1B'/%3E"
        "%3Crect x='6' y='6' width='52' height='52' rx='11' fill='%233E6868'/%3E"
        "%3Ctext x='32' y='45' font-family='Helvetica,Arial,sans-serif' font-size='38' font-weight='700'"
        " text-anchor='middle' fill='%23EFE7D6'%3ES%3C/text%3E%3C/svg%3E")
HEAD = (
    '<title>Southbaw — Brian Anthony Sonnier</title>\n'
    '<link rel="icon" href="' + ICON + '">\n'
    '<link rel="apple-touch-icon" href="' + ICON + '">\n'
    '<meta name="description" content="Southbaw — Brian Anthony Sonnier. Games, tools, and experiments built at night in South Louisiana.">\n'
    '<meta name="theme-color" content="#1F1D1B">\n'
    '<meta name="author" content="Brian Anthony Sonnier">\n'
    '<link rel="canonical" href="https://briananthonysonnier.com/">\n'
    '<meta property="og:site_name" content="Southbaw">\n'
    '<meta property="og:title" content="Southbaw — Brian Anthony Sonnier">\n'
    '<meta property="og:description" content="Games, tools, and experiments, built at night in South Louisiana.">\n'
    '<meta property="og:type" content="website">\n'
    '<meta property="og:url" content="https://briananthonysonnier.com/">\n'
    '<meta property="og:image" content="https://briananthonysonnier.com/img/og-card.jpg">\n'
    '<meta property="og:image:width" content="1200">\n'
    '<meta property="og:image:height" content="630">\n'
    '<meta name="twitter:card" content="summary_large_image">\n'
    '<meta name="twitter:title" content="Southbaw — Brian Anthony Sonnier">\n'
    '<meta name="twitter:description" content="Games, tools, and experiments, built at night in South Louisiana.">\n'
    '<meta name="twitter:image" content="https://briananthonysonnier.com/img/og-card.jpg">\n'
)
swap("</style>\n</helmet>", "</style>\n" + HEAD + "</helmet>", "helmet head tags")

# ------------------------------------------------------------ 4. header ids
print("4. header")
swap('<div style="font-family:\'Modern Tokyo\',\'Bai Jamjuree\',sans-serif;font-size:30px;letter-spacing:.05em;color:#efe7d6;text-transform:uppercase;line-height:1">Southbaw</div>',
     '<a id="sbw-logo" href="#top" style="font-family:\'Modern Tokyo\',\'Bai Jamjuree\',sans-serif;font-size:30px;letter-spacing:.05em;color:#efe7d6;text-transform:uppercase;line-height:1;text-decoration:none">Southbaw</a>',
     "wordmark links home")

# ------------------------------------------------------------ 5. search works
print("5. search")
swap('<div style="max-width:1240px;margin:0 auto;display:flex;align-items:center;gap:18px">\n      <svg width="26" height="26"',
     '<div id="sbw-searchbar" style="max-width:1240px;margin:0 auto;display:flex;align-items:center;gap:18px">\n      <svg width="26" height="26"',
     "search bar id")
swap('<input placeholder="SEARCH THE WORLD OF SOUTHBAW"',
     '<input oninput="{{ setQuery }}" value="{{ q }}" autofocus placeholder="SEARCH PROJECTS — TRY “GAME”"',
     "search input is wired to state")

# a line under the grid for when a search matches nothing
swap('      </sc-for>\n    </div>',
     '      </sc-for>\n    </div>\n    <sc-if value="{{ noResults }}" hint-placeholder-val="{{ false }}">\n'
     '      <div style="font-family:\'Space Mono\',monospace;font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:#b8ad97;padding:30px 2px">Nothing matches that. Try a project name, or clear the search.</div>\n'
     '    </sc-if>',
     "empty-search message")

# ------------------------------------------------------------ 6. real menu
print("6. slide-out menu")
LINK = ("font-family:'Modern Tokyo','Bai Jamjuree',sans-serif;font-size:46px;letter-spacing:.01em;"
        "color:%s;text-decoration:none;cursor:pointer;line-height:.95;text-transform:uppercase;"
        "transition:color .25s ease,transform .3s cubic-bezier(.2,.7,.2,1)")
old_menu = re.search(r'<div style="margin-top:42px;display:flex;flex-direction:column;gap:16px">.*?</div>\n', page, re.S)
if not old_menu:
    sys.exit("MISSING: menu link block")
new_menu = (
    '<div style="margin-top:42px;display:flex;flex-direction:column;gap:16px">\n'
    '        <a href="#top" onclick="{{ closeMenu }}" style="' + LINK % "var(--cream)" + '" style-hover="color:var(--red);transform:translateX(10px)">HOME</a>\n'
    '        <a href="#work" onclick="{{ closeMenu }}" style="' + LINK % "var(--red)" + '" style-hover="transform:translateX(10px)">WORK</a>\n'
    '        <a href="https://github.com/SouthBaw75" target="_blank" rel="noopener" onclick="{{ closeMenu }}" style="' + LINK % "var(--cream)" + '" style-hover="color:var(--red);transform:translateX(10px)">GITHUB</a>\n'
    '        <a href="mailto:hello@briananthonysonnier.com" onclick="{{ closeMenu }}" style="' + LINK % "var(--cream)" + '" style-hover="color:var(--red);transform:translateX(10px)">EMAIL</a>\n'
    '      </div>\n')
page = page[:old_menu.start()] + new_menu + page[old_menu.end():]
edits.append("menu links go somewhere real")
print("   ok    menu links go somewhere real")

CAT = ("cursor:pointer;background:none;border:none;padding:0;font-family:'Space Mono',monospace;font-size:12px;"
       "letter-spacing:.14em;text-transform:uppercase;color:#b8ad97;transition:color .2s ease")
swap('<span style="cursor:pointer;transition:color .2s ease" style-hover="color:var(--red)">MOTION</span>\n'
     '          <span style="cursor:pointer;transition:color .2s ease" style-hover="color:var(--red)">IDENTITY</span>\n'
     '          <span style="cursor:pointer;transition:color .2s ease" style-hover="color:var(--red)">SPATIAL</span>',
     '<button onclick="{{ menuGames }}" style="' + CAT + '" style-hover="color:var(--red)">GAMES</button>\n'
     '          <button onclick="{{ menuApps }}" style="' + CAT + '" style-hover="color:var(--red)">APPS</button>\n'
     '          <button onclick="{{ menuWeb }}" style="' + CAT + '" style-hover="color:var(--red)">WEB</button>',
     "menu categories match the real filters")

# ------------------------------------------------------------ 7. component state
print("7. component state")
swap("state = { menuOpen: false, searchOpen: false, filter: 'all' };",
     "state = { menuOpen: false, searchOpen: false, filter: 'all', q: '' };",
     "add q to state")
swap("    const f = this.state.filter;\n"
     "    const worksFiltered = f === 'all' ? works : works.filter(w => w.tag === f);",
     "    const f = this.state.filter;\n"
     "    const q = (this.state.q || '').trim().toLowerCase();\n"
     "    let worksFiltered = f === 'all' ? works : works.filter(w => w.tag === f);\n"
     "    if (q) worksFiltered = worksFiltered.filter(w =>\n"
     "      (w.title + ' ' + w.type + ' ' + w.tag).toLowerCase().indexOf(q) > -1);",
     "filter by search query")
swap("      searchOpen: this.state.searchOpen,\n"
     "      toggleSearch: () => this.setState(s => ({ searchOpen: !s.searchOpen })),",
     "      searchOpen: this.state.searchOpen,\n"
     "      toggleSearch: () => this.setState(s => ({ searchOpen: !s.searchOpen, q: s.searchOpen ? '' : s.q })),\n"
     "      q: this.state.q,\n"
     "      setQuery: (e) => this.setState({ q: (e && e.target ? e.target.value : '') }),\n"
     "      noResults: worksFiltered.length === 0,\n"
     "      jumpToWork: () => { const el = document.getElementById('work');\n"
     "        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' }); },",
     "search + jump handlers")
swap("      setFilterSpatial: () => this.setState({ filter: 'web' }),",
     "      setFilterSpatial: () => this.setState({ filter: 'web' }),\n"
     "      menuGames: () => { this.setState({ filter: 'game', menuOpen: false }); setTimeout(() => {\n"
     "        const el = document.getElementById('work'); if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 60); },\n"
     "      menuApps: () => { this.setState({ filter: 'app', menuOpen: false }); setTimeout(() => {\n"
     "        const el = document.getElementById('work'); if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 60); },\n"
     "      menuWeb: () => { this.setState({ filter: 'web', menuOpen: false }); setTimeout(() => {\n"
     "        const el = document.getElementById('work'); if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 60); },",
     "menu category handlers")

# ------------------------------------------------------------ reassemble
out = raw[:m.start(2)] + json.dumps(page).replace("</", "<\\/") + raw[m.end(2):]

# belt and braces: keep the tab title even if the runtime clears <head> again
GUARD = ('<script>document.addEventListener("DOMContentLoaded",function(){'
         'setTimeout(function(){if(!document.title)document.title='
         '"Southbaw \\u2014 Brian Anthony Sonnier";},1200);});</script>\n')
head_end = out.find("</head>")
out = out[:head_end] + '<!-- ' + MARKER + ' -->\n' + GUARD + out[head_end:]

# verify every embedded JSON block still parses
for kind, body in re.findall(r'<script type="(__bundler/[a-z_]+)"[^>]*>(.*?)</script>', out, re.S):
    json.loads(body.strip())
    print("  json ok:", kind)
json.loads(re.search(r'id="__slotstate">(.*?)</script>', out, re.S).group(1))
print("  json ok: __slotstate")

open(PATH, "w", encoding="utf-8").write(out)
print("\nwrote %s  (%.2f MB)  edits applied: %d" % (PATH, os.path.getsize(PATH) / 1e6, len(edits)))
