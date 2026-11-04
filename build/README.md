# Site build

`index.html` and `pricing/index.html` are generated. Edit the sources here, then run:

```bash
python3 build/build.py
```

- `site.css` — the stylesheet (copied to `assets/site.css`, with the legacy modal and privacy rules appended)
- `build.py` — page templates: nav, hero, Discover, APIs, closing CTA, footer, pricing tiers
- `ga.html` — the GA4 block, carried over verbatim from the previous site
- `modal.html`, `privacy.html`, `scripts.js`, `legacy.css`, `root.css` — the demo modal and the privacy policy page, carried over unchanged

## Insights

`insights/index.html` and `insights/<slug>/index.html` are generated from `build/insights/*.html`. Each source file is a JSON front-matter block between `---` lines, then the article body as HTML:

```
---
{"title": "...", "dek": "...", "slug": "url-slug", "date": "2026-11-04", "audience": "grantmakers | nonprofits | both",
 "tags": ["For grantmakers", "Compliance"], "featured": false, "byline": "Givalgo Research",
 "stat": "~4,000", "stat_label": "the headline number shown on the card"}
---
<p>Body…</p>
```

To publish a new piece, add a source file and run the build. It appears on the index (newest first, `featured` gets the large card), gets its own page with Article metadata, and is added to `sitemap.xml`. Each page also gets its own share image for LinkedIn and other previews (`og-<hash>.png`, 2400×1254: the stat, the title and the first topic tag), rendered by `build/insights_og.py` with headless Chrome. Set `og_title` to use a shorter title on the image. Images are only re-rendered when their content changes, and the new file name makes LinkedIn fetch a fresh preview.

Body building blocks: `.ins-stats` / `.ins-stat` (number tiles), `.ins-callout`, `<table>` + `<figcaption>`, `ol.ins-check`, `.ins-cta` (gets an Open Discover button) and `.ins-sources`.

The Discover flow GIFs in `assets/` are rendered mock-ups of the Discover UI (not screen recordings).

`bbcon/` (the bbcon lucky-draw form and booth page) is hand-written, not generated — see `build/bbcon/README.md`.
