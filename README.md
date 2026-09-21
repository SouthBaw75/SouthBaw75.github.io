# briananthonysonnier.com

Personal site. Single static page, no build step at serve time, no framework on the server.

- `index.html` — the whole site (a Claude Design bundle: styles, fonts and project
  screenshots are all embedded)
- `img/` — screenshots of the live projects, plus `og-card.jpg` (the 1200x630 link preview)
- `aegis/` — AEGIS: Orbital Defense, served from this repo at /aegis/ rather than netlify.
  Its source of truth is `~/Library/Mobile Documents/com~apple~CloudDocs/Aegis`; only
  `index.html`, `assets/` and `audio/` are copied here (the top-level `music/` and
  `sounds/` folders there are older duplicates the game no longer loads)
- `img-full/` — full-size originals, not shipped to the browser
- `CNAME` — the custom domain, do not delete
- `.nojekyll` — tells GitHub Pages to serve files as-is

## Scripts

`build-southbaw.py` rebuilds `index.html` from the pristine Claude Design export in
`~/Downloads/Southbaw Proper/`. It swaps in the real project list, links the cards,
renames the filter tabs and supplies the footer.

`add-project.py` adds one card to a built `index.html` (works row plus the base64
thumbnail), dropping it in with the others of its kind:

    python3 add-project.py "AEGIS" "ORBITAL DEFENSE" game \
        "https://briananthonysonnier.com/aegis/" aegis.jpg

`remove-project.py` takes a card off by title, along with its thumbnail:

    python3 remove-project.py "SCAVENGE RABBIT"

Also delete the project's line from `PROJECTS` in `build-southbaw.py`, or a rebuild
brings it back.

`patch-southbaw.py` applies the fixes that came after that export — responsive layout,
working search, real menu links, and the `<title>`/favicon/og tags the bundler's runtime
would otherwise drop. It only needs `index.html`, so it runs anywhere, and it refuses to
run twice on the same file.

**If you ever re-run `build-southbaw.py`, run `patch-southbaw.py` right after it**, or the
site goes back to being unusable on a phone:

    python3 build-southbaw.py && python3 patch-southbaw.py

## Updating

Edit, then:

    git add -A && git commit -m "your message" && git push

Live at https://briananthonysonnier.com within about a minute.

Previous HTML5 UP version is kept at tag `v1-massively`.
