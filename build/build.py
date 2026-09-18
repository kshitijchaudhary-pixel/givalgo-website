import os, re
B=os.path.dirname(os.path.abspath(__file__)); R=os.path.dirname(B)
rd=lambda n: open(os.path.join(B,n)).read()
CSS=open(os.path.join(B,'site.css')).read()
GA=rd('ga.html'); LOGO=rd('logo.svg').strip(); MODAL=rd('modal.html'); PRIVACY=rd('privacy.html'); SCRIPTS=rd('scripts.js'); LEGACY=rd('legacy.css'); ROOT=rd('root.css')
import hashlib
PHONE_FIX='''
/* ── Phone fixes for the legacy privacy page and modal (must come after the legacy rules) ── */
@media (max-width: 860px) {
  .privacy-layout { grid-template-columns: minmax(0, 1fr); padding: 0 1rem; }
  .privacy-sidebar { display: none; }
  .privacy-content-area { padding: 2rem 0 4rem; min-width: 0; }
  .privacy-section { overflow-wrap: anywhere; }
  .privacy-table { display: block; overflow-x: auto; max-width: 100%; }
  .privacy-hero .container { padding: 0 1rem; }
  .modal-box { width: calc(100% - 32px); max-width: 100%; }
}

'''
CSS_OUT=CSS+'\n/* ── Legacy: demo modal + privacy policy page (unchanged from the previous site) ── */\n'+ROOT+LEGACY+PHONE_FIX
open(os.path.join(R,'assets','site.css'),'w').write(CSS_OUT)

I={
 'search':'<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><path d="M20 20l-3.5-3.5"></path></svg>',
 'research':'<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><path d="M20 20l-3.5-3.5"></path><path d="M8 11h6M11 8v6"></path></svg>',
 'verify':'<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3l7 3v5c0 5-3.5 8.5-7 10-3.5-1.5-7-5-7-10V6l7-3z"></path><path d="M9 12l2 2 4-4"></path></svg>',
 'monitor':'<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 8a6 6 0 0 1 12 0v5l2 3H4l2-3V8z"></path><path d="M10 19a2 2 0 0 0 4 0"></path></svg>',
 'arrow':'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"></path></svg>',
 'check':'<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12l4 4 10-10"></path></svg>',
}
def li(items): return ''.join('<li><span class="tick">%s</span>%s</li>'%(I['check'],t) for t in items)

def head(title, desc, canonical, extra=''):
    ver=hashlib.sha1(CSS_OUT.encode('utf-8')).hexdigest()[:8]
    html=HEAD_TPL % dict(t=title, d=desc, c=canonical, ga=GA.rstrip('\n'), x=extra)
    return html.replace('/assets/site.css"', '/assets/site.css?v='+ver+'"')

HEAD_TPL='''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>%(t)s</title>
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
  <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
  <meta name="description" content="%(d)s" />
  <meta name="theme-color" content="#0C1830" />
  <link rel="canonical" href="%(c)s" />

  <!-- Open Graph / social sharing -->
  <meta property="og:site_name" content="Givalgo" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="%(c)s" />
  <meta property="og:title" content="%(t)s" />
  <meta property="og:description" content="%(d)s" />
  <meta property="og:image" content="https://givalgo.ai/givalgo-og.png" />
  <meta property="og:image:width" content="2203" />
  <meta property="og:image:height" content="847" />
  <meta property="og:image:alt" content="Givalgo — Research, verify, and monitor the nonprofits you fund" />

  <!-- Twitter / X card -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="%(t)s" />
  <meta name="twitter:description" content="%(d)s" />
  <meta name="twitter:image" content="https://givalgo.ai/givalgo-og.png" />

%(ga)s
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/assets/site.css" />
  <script type="application/ld+json">{"@context":"https://schema.org","@graph":[{"@type":"Organization","@id":"https://givalgo.ai/#org","name":"Givalgo","url":"https://givalgo.ai/","logo":"https://givalgo.ai/apple-touch-icon.png","sameAs":["https://www.linkedin.com/company/givalgo"]},{"@type":"WebSite","@id":"https://givalgo.ai/#site","url":"https://givalgo.ai/","name":"Givalgo","description":"Research, verify, and monitor grantees.","publisher":{"@id":"https://givalgo.ai/#org"}}]}</script>
%(x)s</head>
'''

CHEV='<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6 6-6"></path></svg>'
USECASE_LINKS=[('/for/daf-sponsors/','DAF sponsors &amp; community foundations','Verify every recommendation before it moves'),
               ('/for/platforms/','Grant management &amp; giving platforms','Embed verification and data in your product'),
               ('/for/foundations/','Private &amp; corporate foundations','Prospect, vet, and brief in one workspace')]
def nav(on_pricing=False, current=None):
    p='/' if (on_pricing or current) else ''
    products=('<div class="menu" id="productsMenu">'
              '<button type="button" class="menu-btn" aria-haspopup="true" aria-expanded="false" aria-controls="productsPanel" onclick="toggleMenu(event, this)">Products '+CHEV+'</button>'
              '<div class="menu-panel" id="productsPanel" role="menu">'
              '<a role="menuitem" href="'+p+'#discover"><b>Discover</b><span>The workspace for grantmaking teams</span></a>'
              '<a role="menuitem" href="'+p+'#apis"><b>APIs</b><span>Verify, Data, Research, and FaithVerify</span></a>'
              '</div></div>')
    usecases=('<div class="menu" id="usecasesMenu">'
              '<button type="button" class="menu-btn" aria-haspopup="true" aria-expanded="false" aria-controls="usecasesPanel" onclick="toggleMenu(event, this)">Use Cases '+CHEV+'</button>'
              '<div class="menu-panel" id="usecasesPanel" role="menu">'
              + ''.join('<a role="menuitem" href="%s"%s><b>%s</b><span>%s</span></a>'%(h, ' aria-current="page"' if h==current else '', t, d) for h,t,d in USECASE_LINKS) +
              '</div></div>')
    links=[('Docs','https://docs.givalgo.ai/'),('Pricing','/pricing/')]
    a=''.join('<a href="%s"%s>%s</a>'%(h,' aria-current="page"' if (t=='Pricing' and on_pricing) else '',t) for t,h in links)
    mobile=''.join('<a onclick="closeMobileNav()" href="%s">%s</a>'%(h,t) for t,h in [('Discover',p+'#discover'),('APIs',p+'#apis')]+[(t,h) for h,t,d in USECASE_LINKS]+[('Docs','https://docs.givalgo.ai/'),('Pricing','/pricing/')])
    return '''<a class="skip" href="#main">Skip to content</a>
<header class="nav" id="siteNav">
  <div class="container nav-inner">
    <a class="logo" href="/" aria-label="Givalgo home">@@LOGO@@</a>
    <nav class="nav-links" aria-label="Primary">%s%s%s</nav>
    <div class="nav-actions">
      <a class="nav-signin" href="https://discover.givalgo.ai">Sign in</a>
      <button type="button" class="btn btn-outline btn-sm" onclick="openModal()">Book a demo</button>
      <button type="button" class="hamburger" id="hamburger" aria-label="Open menu" aria-controls="mobileNav" aria-expanded="false" onclick="toggleMobileNav()"><span></span><span></span><span></span></button>
    </div>
  </div>
  <nav class="mobile-nav" id="mobileNav" aria-label="Mobile">%s<a href="https://discover.givalgo.ai">Sign in</a><button type="button" class="btn btn-primary" onclick="closeMobileNav(); openModal()">Book a demo</button></nav>
</header>
''' % (products, usecases, a, mobile)

FOOTER='''<footer class="footer" id="footer">
  <div class="container footer-grid">
    <div class="footer-brand">
      <a class="logo" href="/" aria-label="Givalgo home">@@LOGO@@</a>
      <p>Nonprofit intelligence for grantmakers. Available as the Discover app or as APIs.</p>
    </div>
    <div><h4>Products</h4><a href="https://discover.givalgo.ai">Discover</a><a href="/#apis">Verify API</a><a href="/#apis">Data API</a><a href="/#apis">FaithVerify API</a><a href="/pricing/">Pricing</a></div>
    <div><h4>Developers</h4><a href="https://docs.givalgo.ai/">API documentation</a><a href="https://docs.givalgo.ai/">Getting started</a><a href="#" onclick="openModal(); return false;">Book a demo</a></div>
    <div><h4>Company</h4><a href="#" onclick="openModal(); return false;">Contact us</a>%s<a href="https://www.linkedin.com/company/givalgo" target="_blank" rel="noopener">LinkedIn</a></div>
  </div>
  <div class="container footer-bottom">© 2026 Givalgo, Inc. All rights reserved. Data sourced from IRS public records.</div>
</footer>
'''
def footer(on_pricing=False):
    priv='<a href="/?page=privacy">Privacy policy</a>' if on_pricing else '<a href="/?page=privacy" onclick="showPrivacy(); return false;">Privacy policy</a>'
    return FOOTER % priv

LANDING='''<main id="main">
<section class="hero" id="top">
  <div class="container hero-inner">
    <div class="pill"><span class="dot"></span>LIVE · 1.9M ORGANIZATIONS INDEXED</div>
    <h1>Research, verify, and monitor<br><span>the nonprofits you fund.</span></h1>
    <p class="lead">Search 1.9M organizations, run compliance checks, and get alerted when something changes. Built on IRS and state data, sanctions lists, and the open web. Free to start.</p>
    <form class="search" id="heroSearch" action="https://discover.givalgo.ai/search" method="get" target="_blank" rel="noopener">
      <div class="tabs" role="tablist" aria-label="Search mode">
        <button type="button" class="tab on" role="tab" aria-selected="true" data-mode="search">%(search)s Search</button>
        <button type="button" class="tab" role="tab" aria-selected="false" data-mode="ask">Ask</button>
      </div>
      <label class="sr-only" for="q">Search nonprofits</label>
      <div class="bar">
        <span class="bar-icon">%(search)s</span>
        <input id="q" name="q" type="text" autocomplete="off" placeholder="EIN, org name, keywords, or cause and location" />
        <button type="submit" class="btn btn-primary">Search %(arrow)s</button>
      </div>
      <div class="chips"><span>Try:</span>
        <a href="https://discover.givalgo.ai/search?q=American%%20Red%%20Cross" target="_blank" rel="noopener">American Red Cross</a>
        <a href="https://discover.givalgo.ai/search?q=53-0196605" target="_blank" rel="noopener">53-0196605</a>
        <a href="https://discover.givalgo.ai/search?q=food%%20pantry%%20Brooklyn" target="_blank" rel="noopener">food pantry Brooklyn</a>
        <a href="https://discover.givalgo.ai/search?q=after%%20school%%20Texas" target="_blank" rel="noopener">after school Texas</a>
      </div>
      <p class="hint" id="searchHint">No account needed. 2 free searches, then sign up free. Opens in Discover.</p>
    </form>
  </div>
</section>

<section class="backed">
  <div class="container"><span class="eyebrow-xs">BACKED BY</span><a href="https://www.blackbaud.com/social-good-startup-program" target="_blank" rel="noopener">Blackbaud Social Good Startup Program</a></div>
</section>

<section class="sec" id="discover">
  <div class="container two-col">
    <div class="col-text">
      <div class="eyebrow">GIVALGO DISCOVER</div>
      <h2>The workspace for grantmaking teams.</h2>
      <p class="lead">Find the right organizations, vet them in one view, and keep watching them after the grant goes out. All in the browser, no integration needed.</p>
      <div class="features">
        <div class="feature"><span class="feature-icon">%(research)s</span><div><h3>Research</h3><p>Search 1.9M nonprofits and 151K funders by cause, geography, size, financials, and who funds whom. Ask in plain English and export shortlists.</p></div></div>
        <div class="feature"><span class="feature-icon">%(verify)s</span><div><h3>Verify</h3><p>IRS eligibility, auto-revocation, OFAC screening of the organization and its leaders, state registries, and governance signals. One view, before money moves.</p></div></div>
        <div class="feature"><span class="feature-icon">%(monitor)s</span><div><h3>Monitor</h3><p>Givalgo Watch tracks your portfolio across IRS filings, sanctions lists, and adverse media, and alerts you the moment something changes.</p></div></div>
      </div>
      <div class="cta-row"><a class="btn btn-primary" href="https://discover.givalgo.ai">Open Discover %(arrow)s</a><span class="hint">Free to start · Pro $20/mo · 14-day trial, no card</span></div>
    </div>
    <div class="col-media">
      <img class="product-gif" src="/assets/discover-flow.gif" srcset="/assets/discover-flow.gif 1x, /assets/discover-flow@2x.gif 2x" width="560" height="520" loading="lazy" alt="Givalgo Discover: searching for organizations in NYC that tackle food insecurity, opening Vinegar Hill Food Pantry, running verification checks, saving the report, and turning on monitoring" />
    </div>
  </div>
</section>

<section class="sec sec-alt" id="apis">
  <div class="container">
    <div class="eyebrow">GIVALGO API</div>
    <h2>Build nonprofit verification and data into your platform.</h2>
    <p class="lead lead-narrow">The same data behind Discover, delivered as REST APIs. Verify, enrich, and prospect inside your own product, refreshed nightly from IRS and sanctions sources.</p>
    <div class="tiles">
      <div class="tile"><h3>Verify API</h3><p class="tile-sub">Real-time eligibility and sanctions verification</p><ul>%(t0_li)s</ul></div>
      <div class="tile"><h3>Data API</h3><p class="tile-sub">Search, prospect, and profile any nonprofit</p><ul>%(t1_li)s</ul></div>
      <div class="tile"><h3>Research API</h3><p class="tile-sub">Autonomous due diligence, delivered as a brief</p><ul>%(t2_li)s</ul></div>
      <div class="tile"><h3>FaithVerify API</h3><p class="tile-sub">Denomination and religious-organization verification</p><ul>%(t3_li)s</ul></div>
    </div>
    <div class="api-bottom">
      <div class="code">
        <div class="code-head"><span>API.GIVALGO.AI · V1</span><span>&lt;100 MS</span></div>
        <div class="code-body">
          <div class="c-muted">// Verify any nonprofit in one call</div>
          <div><span class="c-teal">GET</span> /v1/verify?ein=87-3179766</div>
          <div class="c-dim">x-api-key: gvlg_live_••••••••</div>
          <div class="code-resp">
            <div><span>name</span><b>"Vinegar Hill Food Pantry"</b></div>
            <div><span>status</span><b class="c-teal">ELIGIBLE</b></div>
            <div><span>pub78_listed</span><b class="c-teal">true</b></div>
            <div><span>revoked</span><b class="c-teal">false</b></div>
            <div><span>ofac_org_screen</span><b class="c-teal">CLEAR</b></div>
            <div><span>ofac_leadership</span><b class="c-teal">CLEAR</b></div>
          </div>
        </div>
      </div>
      <div class="api-side">
        <div class="stats">
          <div><b>1.9M+</b><span>NONPROFITS VERIFIED</span></div>
          <div><b>3.6M+</b><span>GRANTS MAPPED</span></div>
          <div><b>1.3B+</b><span>STRUCTURED DATA POINTS</span></div>
          <div><b>&lt;100ms</b><span>AVG. API RESPONSE</span></div>
        </div>
        <div class="cta-row"><a class="btn btn-primary" href="https://docs.givalgo.ai/">Read the API docs %(arrow)s</a><a class="link" href="#" onclick="openModal(); return false;">Talk to sales</a></div>
      </div>
    </div>
  </div>
</section>

<section class="sec close" id="get-started">
  <div class="container">
    <h2>Start with Discover,<br>or build with the API.</h2>
    <div class="cta-row center"><a class="btn btn-primary" href="https://discover.givalgo.ai">Open Discover %(arrow)s</a><button type="button" class="btn btn-outline" onclick="openModal()">Talk to Sales</button></div>
    <p class="hint">Discover is free to start, no card required · API provisioned in less than 24 hours</p>
  </div>
</section>
</main>
''' % dict(I,
  t0_li=li(["Active 501(c)(3) status, Pub 78, group exemption", "IRS auto-revocation, California FTB and AG registries", "OFAC screening of the org and every officer and director", "Bulk Verify up to 20K EINs, plus a shareable Report API"]),
  t1_li=li(["Search by cause, place, size, financials, or funder, or Ask", "Profiles from every 990, 990-EZ, and 990-PF filing", "Grants made and received, funder-to-recipient mapping", "Data Pro API: 450+ fields on any single organization"]),
  t2_li=li(["A complete, citation-backed diligence brief in one call", "Financials, governance, risk flags, and peer benchmarks", "AI agents research the web, grounded against 990 filings", "Structured JSON with every claim sourced, ready to file"]),
  t3_li=li(["Status verification for over 90% of American churches", "IRS group exemption mapping and hierarchy", "Affiliation confirmed against denominational registers", "Built for DAFs, community foundations, workplace giving"]),
)

def tier(name, price, per, who, feats, cta_label, cta_href, primary, note, popular=False, price_id=None, note_id=None):
    return '''<div class="tier%s">
  <div class="tier-top"><span class="tier-name">%s</span>%s</div>
  <div class="tier-price"><span class="amount"%s>%s</span><span class="per">%s</span></div>
  <p class="tier-who">%s</p>
  <div class="tier-cta"><a class="btn %s" href="%s"%s>%s</a><span class="hint"%s>%s</span></div>
  <ul>%s</ul>
</div>''' % (' popular' if popular else '', name, '<span class="badge">MOST POPULAR</span>' if popular else '',
             ' id="%s"'%price_id if price_id else '', price, per, who,
             'btn-primary' if primary else 'btn-outline', cta_href, '' if cta_href.startswith('#') else ' target="_blank" rel="noopener"', cta_label,
             ' id="%s"'%note_id if note_id else '', note, li(feats))

PRICING='''<main id="main">
<section class="hero hero-sm">
  <div class="container hero-inner">
    <div class="eyebrow">PRICING</div>
    <h1>Start free. Scale when you are ready.</h1>
    <p class="lead">Discover is self-serve and free to start. APIs are priced for your volume and use case.</p>
  </div>
</section>

<section class="sec" id="discover-pricing">
  <div class="container">
    <div class="pricing-head">
      <div><div class="eyebrow">GIVALGO DISCOVER</div><h2>The workspace for grantmaking teams.</h2></div>
      <div class="billing">
        <div class="tabs" role="tablist" aria-label="Billing period">
          <button type="button" class="tab" role="tab" aria-selected="false" data-billing="monthly">Monthly</button>
          <button type="button" class="tab on" role="tab" aria-selected="true" data-billing="annual">Annual <span class="save">Save 20%%</span></button>
        </div>
        <span class="hint">Cancel anytime · No long-term contracts</span>
      </div>
    </div>
    <div class="tiers">
%(free)s
%(pro)s
%(adv)s
    </div>
  </div>
</section>

<section class="sec sec-alt" id="api-pricing">
  <div class="container">
    <div class="eyebrow">GIVALGO API</div>
    <h2>Build nonprofit verification and data into your platform.</h2>
    <div class="api-card">
      <div>
        <div class="tier-price"><span class="amount">Custom</span><span class="per">usage-based, scoped to your needs</span></div>
        <p class="lead">Built for DAF sponsors, community foundations, and the grant management and giving platforms that serve them.</p>
        <div class="cta-row"><button type="button" class="btn btn-primary" onclick="openModal()">Talk to Sales %(arrow)s</button><a class="link" href="https://docs.givalgo.ai/">Read the API docs</a></div>
        <p class="hint">API provisioned in less than 24 hours</p>
      </div>
      <ul>%(api_li)s</ul>
    </div>
  </div>
</section>
</main>
''' % dict(arrow=I['arrow'],
  free=tier("FREE","$0","","For occasional lookups.",["10 searches a day","Organization profile snapshot","Current-year financials","IRS status indicator"],"Get started","https://discover.givalgo.ai",False,""),
  pro=tier("PRO","$20","/ mo","For grantmakers and researchers.",["Unlimited searches","Discover Ask (plain-English prospecting)","5-year financial explorer and peer benchmarking","Full grants table","Unlimited Verify Now","Radar Bulk Verify (lists up to 100 EINs)","Givalgo Watch (monitor 3 organizations)","AI due-diligence briefs (5 a month) and AI summaries"],"Start Pro","https://discover.givalgo.ai",True,"Billed annually · 14-day free trial, no card",popular=True,price_id="proPrice",note_id="proNote"),
  adv=tier("ADVANCED","Custom","","For compliance and diligence teams.",["Everything in Pro","Organization accounts: multi-seat, shared workspace","AI due-diligence briefs at the volume you need","Givalgo Radar, sized to your portfolio: bulk verification and daily monitoring","Unlimited data export","Downloadable Verify reports","Priority support"],"Book a demo","#",False,""),
  api_li=li(["Verify API: IRS status, Pub 78, auto-revocation, state registries, OFAC on the org and its leaders","Data API: search, prospecting, and organization profiles from every 990","Data Pro API: 450+ extracted and computed fields on any single organization","Research API: a complete, citation-backed due-diligence brief in one call","FaithVerify API: denomination and religious-organization verification","Custom configurations and volume, with dedicated support and founder access"]))
PRICING=PRICING.replace('<a class="btn btn-outline" href="#">Book a demo</a>','<a class="btn btn-outline" href="#" onclick="openModal(); return false;">Book a demo</a>')

SITE_JS='''
  /* Hero search: Search vs Ask hands off to the matching Discover route. */
  (function () {
    var form = document.getElementById('heroSearch'); if (!form) return;
    var input = document.getElementById('q'), hint = document.getElementById('searchHint');
    var modes = {
      search: { action: 'https://discover.givalgo.ai/search', ph: 'EIN, org name, keywords, or cause and location', hint: 'No account needed. 2 free searches, then sign up free. Opens in Discover.' },
      ask:    { action: 'https://discover.givalgo.ai/ask',    ph: 'Ask in plain English: food banks in Chicago that got over $1M in grants', hint: 'Ask is part of Discover Pro. Opens Discover, where you can sign in or start a free trial.' }
    };
    form.querySelectorAll('.tab').forEach(function (tab) {
      tab.addEventListener('click', function () {
        var m = modes[tab.getAttribute('data-mode')];
        form.querySelectorAll('.tab').forEach(function (t) { t.classList.toggle('on', t === tab); t.setAttribute('aria-selected', t === tab ? 'true' : 'false'); });
        form.action = m.action; input.placeholder = m.ph; hint.textContent = m.hint; input.focus();
      });
    });
    form.addEventListener('submit', function () {
      if (window.GA_ENABLED && typeof gtag === 'function') {
        gtag('event', 'to_discover', { link_url: form.action, link_text: 'hero search: ' + (input.value || '').trim().slice(0, 80) });
      }
    });
  })();

  /* Pricing: Monthly / Annual toggle for Discover Pro. */
  (function () {
    var tabs = document.querySelectorAll('.billing .tab'); if (!tabs.length) return;
    var price = document.getElementById('proPrice'), note = document.getElementById('proNote');
    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        var annual = tab.getAttribute('data-billing') === 'annual';
        tabs.forEach(function (t) { t.classList.toggle('on', t === tab); t.setAttribute('aria-selected', t === tab ? 'true' : 'false'); });
        price.textContent = annual ? '$20' : '$25';
        note.textContent = annual ? 'Billed annually · 14-day free trial, no card' : 'Billed monthly · 14-day free trial, no card';
      });
    });
  })();

  /* Products menu: hover opens on desktop (CSS); click toggles for touch and keyboard. */
  function closeMenus(except) {
    document.querySelectorAll('.menu').forEach(function (m) { if (m !== except) { m.classList.remove('open'); m.querySelector('.menu-btn').setAttribute('aria-expanded', 'false'); } });
  }
  function toggleMenu(e, btn) {
    var m = (btn || e.target).closest('.menu'); closeMenus(m);
    var open = m.classList.toggle('open'); m.querySelector('.menu-btn').setAttribute('aria-expanded', open ? 'true' : 'false');
    if (e) e.stopPropagation();
  }
  (function () {
    if (!document.querySelector('.menu')) return;
    document.addEventListener('click', function (e) { if (!e.target.closest('.menu')) closeMenus(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeMenus(); });
    document.querySelectorAll('.menu-panel a').forEach(function (a) { a.addEventListener('click', function () { closeMenus(); }); });
  })();

  /* Nav: navy over the hero, light once the hero has scrolled out. */
  (function () {
    var nav = document.getElementById('siteNav'), hero = document.querySelector('.hero, .uc-hero'); if (!nav || !hero) return;
    if (!('IntersectionObserver' in window)) return;
    new IntersectionObserver(function (entries) {
      nav.classList.toggle('light', !entries[0].isIntersecting);
    }, { rootMargin: '-72px 0px 0px 0px', threshold: 0 }).observe(hero);
  })();

  /* Close the demo modal on Escape or on a backdrop click. */
  (function () {
    var overlay = document.getElementById('demoModal'); if (!overlay) return;
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && overlay.classList.contains('open')) closeModal(); });
    overlay.addEventListener('click', function (e) { if (e.target === overlay) closeModal(); });
  })();
'''

def scripts(with_privacy):
    js=SCRIPTS
    if not with_privacy:
        # pricing page has no privacy block: keep modal + mobile nav only
        js=js[:js.index('  function showPrivacy')]
    return '<script>\n'+js.rstrip('\n')+'\n'+SITE_JS+'</script>\n'

import hashlib
index=(head('Givalgo | Research, Verify and Monitor Grantees',
            'Research 1.9M nonprofits, verify IRS eligibility and sanctions in one call, and monitor grantees after the grant is paid. Built for grantmakers. Free to start.',
            'https://givalgo.ai/')
       +'<body>\n\n'+MODAL+'\n<!-- ══ MAIN SITE ══ -->\n<div id="main-site">\n'+nav()+LANDING+footer()+'</div><!-- end #main-site -->\n\n<!-- ══ PRIVACY POLICY PAGE ══ -->\n'+PRIVACY+'\n'+scripts(True)+'</body>\n</html>\n')
index=index.replace('@@LOGO@@',LOGO)
open(os.path.join(R,'index.html'),'w').write(index)
os.makedirs(os.path.join(R,'pricing'),exist_ok=True)
pricing=(head('Pricing | Givalgo','Givalgo Discover is free to start, with Pro at $20 a month billed annually. Verify, Data, and FaithVerify APIs are priced for your volume.','https://givalgo.ai/pricing/')
         +'<body>\n\n'+MODAL+'\n<div id="main-site">\n'+nav(True)+PRICING+footer(True)+'</div>\n'+scripts(False)+'</body>\n</html>\n')
pricing=pricing.replace('@@LOGO@@',LOGO)
open(os.path.join(R,'pricing','index.html'),'w').write(pricing)
print('index.html',len(index),'pricing/index.html',len(pricing),'site.css',os.path.getsize(os.path.join(R,'assets','site.css')))

# ---------------- Use-case pages ----------------
def uc_verify_card():
    rows=[("IRS status","Active"),("Pub 78","Listed"),("Auto-revocation","Not revoked"),("CA AG registry","Clear"),("OFAC · organization","Clear"),("OFAC · leadership","Clear · officers screened")]
    chk=''.join('<div class="chk"><b>%s</b><span>%s%s</span></div>'%(k,I['check'],v) for k,v in rows)
    return ('<div class="verify-card dark"><div class="code-head"><span>VERIFY · EIN 87-3179766</span><span>&lt;100 MS</span></div>'
            '<div class="verify-body"><div class="org">Vinegar Hill Food Pantry <span>· Brooklyn, NY</span></div>'+chk+
            '<div class="chk all">'+I['verify']+'Eligible · Report saved to the grant file</div></div></div>')
def uc_code_card():
    return ('<div class="code"><div class="code-head"><span>API.GIVALGO.AI · V1</span><span>&lt;100 MS</span></div><div class="code-body">'
            '<div class="c-muted">// Verify any nonprofit in one call</div><div><span class="c-teal">GET</span> /v1/verify?ein=87-3179766</div><div class="c-dim">x-api-key: gvlg_live_••••••••</div>'
            '<div class="code-resp"><div><span>name</span><b>"Vinegar Hill Food Pantry"</b></div><div><span>status</span><b class="c-teal">ELIGIBLE</b></div><div><span>pub78_listed</span><b class="c-teal">true</b></div><div><span>revoked</span><b class="c-teal">false</b></div><div><span>ofac_org_screen</span><b class="c-teal">CLEAR</b></div><div><span>ofac_leadership</span><b class="c-teal">CLEAR</b></div></div></div></div>')
def uc_gif():
    return '<img class="product-gif" src="/assets/discover-flow.gif" srcset="/assets/discover-flow.gif 1x, /assets/discover-flow@2x.gif 2x" width="560" height="520" loading="lazy" alt="Givalgo Discover: search, profile, verification, report, and monitoring" />'
DEMO_CTA='<button type="button" class="btn btn-primary" onclick="openModal()">Book a demo %s</button>' % I['arrow']
SALES_CTA=DEMO_CTA
UC_TPL='''<main id="main">
<section class="uc-hero dark" id="top">
  <div class="container">
    <div class="col-text"><div class="eyebrow">%(eyebrow)s</div><h1>%(h1)s</h1><p class="lead">%(sub)s</p><div class="cta-row">%(cta)s</div></div>
    <div class="uc-visual">%(visual)s</div>
  </div>
</section>
<section class="backed">
  <div class="container"><span class="eyebrow-xs">BACKED BY</span><a href="https://www.blackbaud.com/social-good-startup-program" target="_blank" rel="noopener">Blackbaud Social Good Startup Program</a><span class="hint">· %(trust)s</span></div>
</section>
<section class="sec" id="how">
  <div class="container">
    <div class="eyebrow">HOW IT WORKS</div>
    <h2>How Givalgo works for %(audience)s.</h2>
    <div class="how">%(steps)s</div>
    <div class="cta-row how-cta">%(cta)s</div>
  </div>
</section>
<section class="sec sec-alt" id="features">
  <div class="container">
    <div class="eyebrow">WHAT YOU USE</div>
    <h2>%(feat_title)s</h2>
    <p class="lead lead-narrow">%(feat_sub)s</p>
    <div class="uc-grid">%(tiles)s</div>
  </div>
</section>
<section class="sec close" id="get-started">
  <div class="container">
    <h2>%(close_h2)s</h2>
    <div class="cta-row center">%(close_cta)s</div>
    <p class="hint">%(close_note)s</p>
  </div>
</section>
</main>
'''
def uc_page(eyebrow, h1, sub, cta, visual, audience, trust, steps, feat_title, feat_sub, tiles, close_h2, close_cta, close_note):
    step_html=''.join('<div class="how-step"><span class="how-n">%d</span><div class="how-body"><h3>%s</h3><p>%s</p></div></div>'%(i,t,d) for i,(t,d) in enumerate(steps,1))
    tile_html=''.join('<div class="uc-tile"><span class="feature-icon">%s</span><h3>%s</h3><p>%s</p></div>'%(I[ic],n,d) for ic,n,d in tiles)
    return UC_TPL % dict(eyebrow=eyebrow,h1=h1,sub=sub,cta=cta,visual=visual,trust=trust,audience=audience,steps=step_html,feat_title=feat_title,feat_sub=feat_sub,tiles=tile_html,close_h2=close_h2,close_cta=close_cta,close_note=close_note)
def two_btn(a,b): return '<button type="button" class="btn btn-primary" onclick="openModal()">Book a demo</button>'
USECASES={
 'for/daf-sponsors': dict(title='For DAF Sponsors and Community Foundations | Givalgo',
   desc='Verify every grant recommendation before it moves: IRS eligibility, sanctions, state registries, and church verification in one call, with monitoring after the grant is paid.',
   page=uc_page("FOR DAF SPONSORS &amp; COMMUNITY FOUNDATIONS","Every grant recommendation, verified before it moves.",
     "Run IRS eligibility, sanctions, state registry, and church checks the moment a donor recommends a grant, then keep watching after it is paid. Built for the compliance and grants teams behind donor-advised funds.",
     SALES_CTA, uc_verify_card(), "DAF sponsors and community foundations", "Designed for DAF sponsors, community foundations, and the platforms that serve them",
     [('Verify at recommendation','One call checks active status, Pub 78, auto-revocation, state registries, and OFAC on the organization and its officers. Flagged grants go to review.'),
      ('Route churches via FaithVerify','Churches rarely file a 990. FaithVerify confirms affiliation against denominational registers and IRS group exemptions, so church grants clear fast.'),
      ('Re-screen your portfolio','Bulk Verify checks up to 20K EINs in one request, and the Report API drops a shareable verification record into the grant file for auditors.'),
      ('Monitor after payment','Watch tracks every grantee across IRS filings, sanctions lists, and adverse media, and alerts your team the moment something changes.')],
     "Compliance that runs itself.","The pieces most DAF sponsors and community foundations turn on, in the order they usually turn them on.",
     [("verify","Verify API","Six-step eligibility and sanctions check on any EIN, under 100 ms."),("verify","FaithVerify API","Verification for religious organizations that never file a 990."),("research","Bulk Verify","Screen an entire grantee list, up to 20K EINs, in one request."),("research","Report API","A shareable verification record for every approved grant."),("monitor","Givalgo Watch","Ongoing monitoring across IRS, sanctions, and adverse media."),("research","Discover for advisors","Research and profiles for donor-relations and philanthropic advisors.")],
     "See it on your own grant queue.", two_btn("Book a demo","Talk to Sales"), "30-minute call with a co-founder · No commitment")),
 'for/platforms': dict(title='For Grant Management and Giving Platforms | Givalgo',
   desc='Nonprofit verification, organization data, and on-demand diligence briefs built into your product with one REST integration.',
   page=uc_page("FOR GRANT MANAGEMENT &amp; GIVING PLATFORMS","Nonprofit verification and data, built into your product.",
     "One REST integration for eligibility checks, organization profiles, and on-demand diligence briefs. Refreshed nightly from IRS and sanctions sources, provisioned in less than 24 hours.",
     SALES_CTA, uc_code_card(), "grant management and giving platforms", "Built for grant management software, workplace and payroll giving, and donation rails",
     [('Verify at onboarding and payout','Gate nonprofit sign-ups, matching, and disbursements on a live eligibility and sanctions check that covers every officer and director.'),
      ('Enrich your UI with org data','Search and profiles from the Data API power lookups, autocomplete, and grantee pages. Data Pro adds 450+ fields per organization when you need depth.'),
      ('Generate briefs on demand','The Research API returns a citation-backed brief for any organization inside your workflow, so reviewers never have to leave your product.'),
      ('Stay current, no data team','Nightly refresh from IRS and sanctions sources, webhooks for status changes, and bulk endpoints for backfills, with no data team required.')],
     "Everything behind Discover, as APIs.","Pick the endpoints you need. Usage-based pricing, scoped to your volume.",
     [("verify","Verify API","Eligibility, revocation, state registries, and OFAC in one call."),("research","Data API","Search, prospecting, and profiles from every 990, 990-EZ, and 990-PF."),("research","Data Pro API","450+ extracted and computed fields on any single organization."),("monitor","Research API","A complete, citation-backed due-diligence brief on demand."),("verify","FaithVerify API","Verification for churches and religious organizations."),("monitor","Webhooks &amp; bulk","Status-change events and batch endpoints up to 20K EINs.")],
     "Get a sandbox key today.", two_btn("Talk to Sales","Book a demo"), "30-minute call with a co-founder · API provisioned in less than 24 hours")),
 'for/foundations': dict(title='For Private and Corporate Foundations | Givalgo',
   desc='Research, verification, and monitoring for 1.9M nonprofits in one workspace, with AI diligence briefs that turn a shortlist into a board-ready memo.',
   page=uc_page("FOR PRIVATE &amp; CORPORATE FOUNDATIONS","From prospect list to board-ready diligence, in one workspace.",
     "Discover gives program staff research, verification, and monitoring for 1.9M nonprofits, and AI briefs that turn a shortlist into a consistent diligence memo.",
     DEMO_CTA, uc_gif(), "private and corporate foundations", "Used by program officers, grants managers, and corporate giving teams",
     [('Prospect with Search and Ask','Find organizations by cause, geography, size, financials, and who funds whom, or describe what you want in plain English. Export the shortlist.'),
      ('Vet in one view',"Five-year financials, peer benchmarks, governance flags, and Verify Now sit together on the organization's profile, so vetting takes one screen."),
      ('Brief the board with AI','Diligence Briefs write the memo with every claim sourced to filings and the open web, in the same format for every grantee you review.'),
      ('Keep the portfolio monitored',"Watch alerts you when a grantee's IRS status, sanctions exposure, or news coverage changes, so renewals always start from current facts.")],
     "Discover, end to end.","What a foundation team uses week to week, plus the APIs for teams with a grants system to feed.",
     [("research","Search &amp; Ask","1.9M nonprofits and 151K funders, filters or plain English."),("research","Organization profiles","Financials, leadership, programs, grants, and governance from every 990."),("monitor","Diligence Briefs","AI-written, citation-backed memos, 5 a month on Pro and more on Advanced."),("research","Peer benchmarking","Compare any organization against its sector and size peers."),("monitor","Givalgo Watch","Portfolio monitoring across IRS, sanctions, and adverse media."),("verify","Research &amp; Data Pro APIs","Feed briefs and 450+ fields straight into your grants system.")],
     "Start with a conversation.", two_btn("Book a demo","Talk to Sales"), "30-minute call with a co-founder · No commitment")),
}
for path, uc in USECASES.items():
    os.makedirs(os.path.join(R, path), exist_ok=True)
    html=(head(uc['title'], uc['desc'], 'https://givalgo.ai/'+path+'/')
          +'<body>\n\n'+MODAL+'\n<div id="main-site">\n'+nav(current='/'+path+'/')+uc['page']+footer(True)+'</div>\n'+scripts(False)+'</body>\n</html>\n')
    html=html.replace('@@LOGO@@',LOGO)
    open(os.path.join(R, path, 'index.html'),'w').write(html)
    print(path, len(html))
