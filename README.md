# briananthonysonnier.com

Personal site. Single static page, no build step at serve time, no framework on the server.

- `index.html` — the whole site (a Claude Design bundle: styles, fonts and project
  screenshots are all embedded)
- `img/` — screenshots of the live projects, plus `og-card.jpg` (the 1200x630 link preview)
- `img-full/` — full-size originals, not shipped to the browser
- `CNAME` — the custom domain, do not delete
- `.nojekyll` — tells GitHub Pages to serve files as-is

## Scripts

`build-southbaw.py` rebuilds `index.html` from the pristine Claude Design export in
`~/Downloads/Southbaw Proper/`. It swaps in the real project list, links the cards,
renames the filter tabs and supplies the footer.

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
