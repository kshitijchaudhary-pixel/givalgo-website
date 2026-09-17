# Site build

`index.html` and `pricing/index.html` are generated. Edit the sources here, then run:

```bash
python3 build/build.py
```

- `site.css` — the stylesheet (copied to `assets/site.css`, with the legacy modal and privacy rules appended)
- `build.py` — page templates: nav, hero, Discover, APIs, closing CTA, footer, pricing tiers
- `ga.html` — the GA4 block, carried over verbatim from the previous site
- `modal.html`, `privacy.html`, `scripts.js`, `legacy.css`, `root.css` — the demo modal and the privacy policy page, carried over unchanged

The Discover flow GIFs in `assets/` are rendered mock-ups of the Discover UI (not screen recordings).
