"""Social share images (1200x627 layout, rendered at 2x = 2400x1254) for Insights pages, rendered with headless Chrome.

Each image is named og-<hash>.png from its content, so editing a title or stat
produces a new URL and LinkedIn fetches a fresh preview instead of its cached one.
An image that already exists for the current content is never re-rendered, so
builds on a machine without Chrome still work as long as nothing changed.
"""
import glob, hashlib, json, os, shutil, subprocess, tempfile

VERSION = 2  # bump when the templates below change, to force new images
CHROME_PATHS = [os.environ.get('CHROME', ''), '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                'google-chrome', 'chromium', 'chromium-browser']

CSS = '''@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1200px;height:627px;overflow:hidden;font-family:Inter,system-ui,sans-serif;-webkit-font-smoothing:antialiased}
.card{position:relative;width:1200px;height:627px;padding:64px 72px;color:#F2F6FB;background:radial-gradient(ellipse 70% 90% at 0% 0%,rgba(0,180,179,.28),rgba(0,0,0,0) 65%),radial-gradient(ellipse 60% 70% at 100% 100%,rgba(0,180,179,.14),rgba(0,0,0,0) 70%),#0C1830}
.logo svg{height:44px;width:auto;display:block}
.eyebrow{font-size:20px;font-weight:700;letter-spacing:.16em;color:#5EEAD4}
.tag{display:inline-block;font-size:16px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#5EEAD4;background:rgba(0,180,179,.14);border-radius:8px;padding:7px 12px}
.url{font-size:20px;color:#A9B8CC;font-weight:500}
.grid{display:grid;grid-template-columns:470px 1fr;gap:56px;height:100%}
.left{display:flex;flex-direction:column;justify-content:space-between}
.n{font-size:@NSIZE@px;line-height:.95;font-weight:800;letter-spacing:-.05em;color:#5EEAD4;white-space:nowrap}
.l{margin-top:18px;font-size:28px;line-height:1.3;color:#C9D6E6;font-weight:500}
.right{display:flex;flex-direction:column;justify-content:center;border-left:2px solid rgba(255,255,255,.12);padding-left:56px}
h1{margin-top:22px;font-size:@TSIZE@px;line-height:1.15;font-weight:800;letter-spacing:-.02em}
.right .url{margin-top:30px}
.index h1{margin-top:70px;font-size:76px;line-height:1.05;letter-spacing:-.03em}
.index h1 span{color:#5EEAD4}
.index p{margin-top:26px;font-size:28px;line-height:1.4;color:#C9D6E6;max-width:900px}
.top{display:flex;align-items:center;gap:18px}.sep{width:2px;height:34px;background:rgba(255,255,255,.25)}
.foot{position:absolute;left:72px;bottom:56px}
.bar{position:absolute;left:0;right:0;bottom:0;height:8px;background:linear-gradient(90deg,#00848B,#00B4B3,#5EEAD4)}
'''


def _article_html(logo, title, stat, stat_label, tag):
    n = len(title)
    tsize = 44 if n <= 60 else 40 if n <= 85 else 36
    nsize = 150 if len(stat) <= 6 else 120
    css = CSS.replace('@NSIZE@', str(nsize)).replace('@TSIZE@', str(tsize))
    tag_html = '<div><span class="tag">%s</span></div>' % tag if tag else ''
    return ('<html><head><style>%s</style></head><body><div class="card"><div class="grid">'
            '<div class="left"><div class="logo">%s</div><div><div class="n">%s</div><div class="l">%s</div></div>'
            '<div class="eyebrow">GIVALGO INSIGHTS</div></div>'
            '<div class="right">%s<h1>%s</h1><div class="url">givalgo.ai/insights</div></div>'
            '</div></div></body></html>') % (css, logo, stat, stat_label, tag_html, title)


def _index_html(logo):
    css = CSS.replace('@NSIZE@', '150').replace('@TSIZE@', '44')
    return ('<html><head><style>%s</style></head><body><div class="card index">'
            '<div class="top"><div class="logo">%s</div><div class="sep"></div><div class="eyebrow">INSIGHTS</div></div>'
            '<h1>Data and analysis for<br><span>better grantmaking.</span></h1>'
            '<p>Research for grantmakers and nonprofits, built on IRS filings, grants data and compliance records.</p>'
            '<div class="foot url">givalgo.ai/insights</div><div class="bar"></div></div></body></html>') % (css, logo)


def _chrome():
    for p in CHROME_PATHS:
        if p and (os.path.isfile(p) or shutil.which(p)):
            return p
    return None


def render(out_dir, logo, article=None):
    """Write the share image for an article (or the index when article is None) into
    out_dir and return its file name, or None if it can't be rendered here."""
    if article:
        fields = [article['og_title'], article['stat'], article['stat_label'], article['og_tag']]
        html = _article_html(logo, *fields)
    else:
        fields = ['index']
        html = _index_html(logo)
    digest = hashlib.sha1(json.dumps([VERSION, fields, logo], ensure_ascii=False).encode('utf-8')).hexdigest()[:10]
    name = 'og-%s.png' % digest
    path = os.path.join(out_dir, name)
    os.makedirs(out_dir, exist_ok=True)
    if not os.path.exists(path):
        chrome = _chrome()
        if not chrome:
            print('  ! Chrome not found; share image not rendered for', out_dir)
            return None
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, 'og.html')
            open(src, 'w').write(html)
            subprocess.run([chrome, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1200,627', '--force-device-scale-factor=2',
                            '--virtual-time-budget=5000', '--screenshot=' + path, 'file://' + src],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print('  rendered', os.path.relpath(path))
    for old in glob.glob(os.path.join(out_dir, 'og-*.png')):
        if os.path.basename(old) != name:
            os.remove(old)
    return name
