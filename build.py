#!/usr/bin/env python3
"""Fontletr static site builder. Reads pages.json + support-pages.json, emits dist/."""
import json, os, shutil, re, html, hashlib

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")
ASSETS_SRC = os.path.join(ROOT, "assets")

def _hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()[:8]
CSS_V = _hash(os.path.join(ASSETS_SRC, "styles.css"))
JS_V = _hash(os.path.join(ASSETS_SRC, "engine.js"))

with open(os.path.join(ROOT, "pages.json"), encoding="utf-8") as f:
    DATA = json.load(f)
with open(os.path.join(ROOT, "support-pages.json"), encoding="utf-8") as f:
    SUPPORT = json.load(f)["pages"]

SITE = DATA["site"]
GEN_PAGES = DATA["pages"]
BASE = SITE["baseUrl"].rstrip("/")
ADSENSE_CLIENT = (SITE.get("adsenseClient") or "").strip()  # e.g. "ca-pub-1234567890123456"
CONTACT_EMAIL = (SITE.get("contactEmail") or "").strip() or "hello@" + BASE.split("//")[-1].lstrip("www.")

# AdSense: when a client ID is configured, inject the loader in <head> and a real
# <ins class="adsbygoogle"> where the placeholder used to be. Until then, the slot
# stays a visible placeholder so dev/preview looks honest.
ADSENSE_HEAD = (
    f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>'
    if ADSENSE_CLIENT else ""
)
def ad_slot():
    if ADSENSE_CLIENT:
        return ('<div class="adslot"><ins class="adsbygoogle" style="display:block" '
                f'data-ad-client="{ADSENSE_CLIENT}" data-ad-slot="0000000000" '
                'data-ad-format="auto" data-full-width-responsive="true"></ins>'
                '<script>(adsbygoogle=window.adsbygoogle||[]).push({});</script></div>')
    return ('<div class="adslot">One ad unit lives here — below the fold. '
            'No popup, no interstitial, no notification prompt. Ever.</div>')

# ---- lookup maps ----
slug_to_h1 = {p["slug"]: p["h1"] for p in GEN_PAGES}
slug_to_kw = {p["slug"]: p["kw"] for p in GEN_PAGES}
slug_to_h1["/"] = "Fancy Text Generator"

STOP = {"text", "generator", "font", "fonts", "online", "free", "tool", "letters", "maker"}
def sample_word(kw):
    parts = [w for w in kw.split() if w.lower() not in STOP]
    s = " ".join(parts).strip()
    return s if s else "fancy text"

def esc(s): return html.escape(str(s), quote=True)

# ---- shared chunks ----
def topbar():
    return ('<div class="topbar">'
            '<span class="logo"><a href="/">Fontletr</a></span>'
            '<nav><a href="/">Generator</a><a href="/all-tools">All tools</a>'
            '<a href="/how-unicode-text-works">How it works</a></nav>'
            '<span class="spacer"></span>'
            '<button class="who" id="themeBtn" type="button">Theme: Light ▾</button>'
            '</div>')

GEN_FOOTER_LINKS = [(p["slug"], p["h1"]) for p in GEN_PAGES]
def footer():
    gens = "".join(f'<li><a href="{esc(s)}">{esc(t)}</a></li>' for s, t in GEN_FOOTER_LINKS)
    learn = ('<li><a href="/how-unicode-text-works">How Unicode text works</a></li>'
             '<li><a href="/does-fancy-text-work-on-instagram-tiktok-discord">Where it works (Instagram, TikTok, Discord...)</a></li>')
    site = ('<li><a href="/about">About</a></li><li><a href="/all-tools">All tools</a></li>'
            '<li><a href="/privacy">Privacy</a></li><li><a href="/contact">Contact</a></li>')
    return ('<footer><div class="footer-inner"><div class="footer-cols">'
            f'<div><h4>Generators</h4><ul>{gens}</ul></div>'
            f'<div><h4>Learn</h4><ul>{learn}</ul></div>'
            f'<div><h4>Site</h4><ul>{site}</ul></div>'
            '</div>'
            f'<div class="footer-note">{esc(SITE["footerNote"])}</div>'
            '</div></footer>')

def crumb(trail):  # trail = list of (href|None, label)
    out = []
    for href, label in trail:
        if href:
            out.append(f'<a href="{esc(href)}">{esc(label)}</a>')
        else:
            out.append(esc(label))
    return '<div class="crumb">' + " / ".join(out) + "</div>"

def head(title, desc, canonical, page_config=None, jsonld=None, extra_meta=""):
    cfg = ""
    if page_config is not None:
        cfg = "<script>window.PAGE_CONFIG=" + json.dumps(page_config) + ";</script>"
    ld = ""
    if jsonld:
        ld = "".join('<script type="application/ld+json">' + json.dumps(b) + "</script>" for b in jsonld)
    return ('<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{esc(title)}</title>'
            f'<meta name="description" content="{esc(desc)}">'
            f'<link rel="canonical" href="{esc(canonical)}">'
            f'<meta property="og:title" content="{esc(title)}">'
            f'<meta property="og:description" content="{esc(desc)}">'
            f'<meta property="og:type" content="website"><meta property="og:url" content="{esc(canonical)}">'
            '<meta name="robots" content="index,follow">'
            f'{extra_meta}{ADSENSE_HEAD}'
            f'<link rel="stylesheet" href="/assets/styles.css?v={CSS_V}">'
            f'{cfg}{ld}</head><body>')

def foot_scripts(with_engine=True):
    eng = f'<script src="/assets/engine.js?v={JS_V}" defer></script>' if with_engine else ""
    return f"{eng}</body></html>"

# ---- the tool block (shared by every generator page) ----
def tool_block(page):
    sample = esc(sample_word(page["kw"]))
    focus = page.get("focusStyles") or []
    right_label = page["h1"].replace(" Generator", "") if focus else "Result"
    parts = []
    # two-panel "translator": left = your text, right = chosen style
    parts.append(
        '<div class="translator">'
        '<div class="card panel"><div class="card-head">Your text</div><div class="card-body">'
        f'<textarea id="input" placeholder="Type or paste something…" autofocus>{sample}</textarea>'
        '<div class="field-meta"><span id="counter">0 characters</span>'
        '<button id="clearBtn" type="button">Clear</button></div>'
        '</div></div>'
        '<div class="swap" aria-hidden="true">→</div>'
        '<div class="card panel"><div class="card-head">'
        f'<span class="ch-label">{esc(right_label)}</span>'
        '<select id="styleSelect" class="style-select" aria-label="Choose a style"></select></div>'
        '<div class="card-body">'
        '<div id="bigOut" class="big-out"></div>'
        '<div class="out-actions"><button id="bigCopy" class="copy" type="button">Copy</button></div>'
        '</div></div>'
        '</div>')
    parts.append(ad_slot())
    if focus:
        parts.append(
            '<div class="card content" style="padding:14px 16px"><p style="margin:0">Pick the look you want above, then hit Copy. '
            'Want every option? <a href="/">Browse all 80+ text styles in the fancy text generator</a> — or see related ones below.</p></div>')
    else:
        parts.append(
            '<div class="card"><div class="card-head">Browse all styles <span class="count" id="styleCount">— styles</span>'
            '<span class="toggle" style="margin-left:14px">favorites only: <button id="favOnly" type="button"><b id="favState">Off</b></button></span></div>'
            '<div class="card-body tight" id="results"></div></div>')
    return "".join(parts)

# ---- content + faq + related (shared) ----
ST_LABEL = {"ok": "Works", "partial": "Partial", "no": "Won't render"}
def content_block(page):
    kw_heading = page["kw"][0].upper() + page["kw"][1:]
    intro = page["intro"]
    return (
        '<div class="card content">'
        f'<h2>{esc(kw_heading)}</h2><p>{intro}</p>'
        '<h2>How to use it</h2><p>Type in the box on the left. The style you’ve picked on the right updates as you type — no “generate” button. Click <strong>Copy</strong> and paste it wherever you need. On the home page you can also browse every style in the list below and click any row to load it into the panel.</p>'
        '</div>')

def where_block(page):
    w = page.get("where")
    if not w: return ""
    rows = ""
    for r in w.get("rows", []):
        st = r.get("status", "ok")
        rows += (f'<tr><td class="app">{esc(r["app"])}</td>'
                 f'<td class="fields">{esc(r.get("fields",""))}</td>'
                 f'<td><span class="st st-{esc(st)}">{esc(ST_LABEL.get(st,st))}</span></td>'
                 f'<td class="cnote">{esc(r.get("note",""))}</td></tr>')
    return (
        '<div class="card content"><h2>Where it renders, and where it breaks</h2>'
        f'<p>{esc(w.get("intro",""))}</p>'
        '<table class="compat"><thead><tr><th>App / platform</th><th>Where</th><th>Status</th><th>Notes</th></tr></thead>'
        f'<tbody>{rows}</tbody></table>'
        f'<p class="small-note">{esc(SITE["compatNoteShared"])} The full <a href="/does-fancy-text-work-on-instagram-tiktok-discord">cross-app compatibility page</a> goes wider.</p>'
        '</div>')

def examples_block(page):
    ex = page.get("examples")
    if not ex: return ""
    items = "".join(
        f'<li><strong>{esc(i["label"])}</strong> — {i["text"]}</li>' for i in ex.get("items", []))
    return (
        '<div class="card content"><h2>Examples &amp; use cases</h2>'
        f'<p>{esc(ex.get("intro",""))}</p><ul>{items}</ul></div>')

def pitfalls_block(page):
    p = page.get("pitfalls")
    if not p: return ""
    items = "".join(f'<li><strong>{esc(i["title"])}.</strong> {i["text"]}</li>' for i in p)
    return f'<div class="card content"><h2>Common mistakes</h2><ul>{items}</ul></div>'

def faq_block(faqs):
    if not faqs: return ""
    items = "".join(
        f'<details><summary>{esc(q["q"])}</summary><div class="a">{esc(q["a"])}</div></details>'
        for q in faqs)
    return f'<div class="card content"><h2>FAQ</h2><div class="faq">{items}</div></div>'

def related_block(slugs, header="Related generators"):
    if not slugs: return ""
    cells = []
    for s in slugs:
        label = slug_to_h1.get(s, s)
        kw = slug_to_kw.get(s, "")
        sub = f'<span>{esc(kw)}</span>' if kw and s != "/" else ('<span>all 80+ styles in one place</span>' if s == "/" else "")
        cells.append(f'<a href="{esc(s)}">{esc(label)}{sub}</a>')
    return f'<div class="card content"><h2>{esc(header)}</h2><div class="related-grid">{"".join(cells)}</div></div>'

def faq_jsonld(faqs, url):
    if not faqs: return None
    return {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q["q"],
                        "acceptedAnswer": {"@type": "Answer", "text": q["a"]}} for q in faqs]
    }

def breadcrumb_jsonld(trail, url):
    items = []
    pos = 1
    for href, label in trail:
        item = {"@type": "ListItem", "position": pos, "name": label}
        if href:
            item["item"] = BASE + (href if href != "/" else "/")
        items.append(item); pos += 1
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}

def webapp_jsonld(name, url, desc):
    return {"@context": "https://schema.org", "@type": "WebApplication", "name": name,
            "url": url, "description": desc, "applicationCategory": "UtilitiesApplication",
            "operatingSystem": "Any (browser)", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}}

# ---- write helpers ----
def out_path(slug):
    if slug == "/":
        return os.path.join(DIST, "index.html")
    return os.path.join(DIST, slug.strip("/"), "index.html")

def write(slug, htmlstr):
    p = out_path(slug)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(htmlstr)

# ---- build generator pages ----
def build_generator(page):
    slug = page["slug"]
    url = BASE + ("/" if slug == "/" else slug + "/")
    trail = [("/", "Fontletr")]
    if slug != "/":
        trail += [("/all-tools", "Tools"), (None, page["h1"])]
    else:
        trail = [(None, "Fontletr")]
    jsonld = [webapp_jsonld(page["h1"], url, page["metaDescription"])]
    fld = faq_jsonld(page.get("faqs"), url)
    if fld: jsonld.append(fld)
    if len(trail) > 1: jsonld.append(breadcrumb_jsonld(trail, url))
    body = (head(page["title"], page["metaDescription"], url,
                 page_config={"slug": slug, "focusStyles": page.get("focusStyles") or []},
                 jsonld=jsonld)
            + topbar()
            + '<div class="wrap">'
            + '<div class="pagehead">' + crumb(trail) + f'<h1>{esc(page["h1"])}</h1>'
            + (f'<p class="lede">{esc(page.get("lede",""))}</p>' if page.get("lede") else "")
            + '</div>'
            + tool_block(page)
            + content_block(page)
            + where_block(page)
            + examples_block(page)
            + pitfalls_block(page)
            + faq_block(page.get("faqs"))
            + related_block(page.get("related"))
            + '</div>'
            + footer()
            + foot_scripts(with_engine=True))
    write(slug, body)

# ---- build support pages ----
def build_support(page):
    slug = page["slug"]
    url = BASE + slug + "/"
    trail = [("/", "Fontletr"), (None, page.get("crumb", page["h1"]))]
    body_html = page["bodyHtml"].replace("{CONTACT_EMAIL}", esc(CONTACT_EMAIL))
    if page.get("renderToolsList"):
        cells = "".join(
            f'<a href="{esc(s)}">{esc(t)}<span>{esc(slug_to_kw.get(s,""))}</span></a>'
            for s, t in GEN_FOOTER_LINKS)
        body_html = body_html.replace('<div id="toolsList"></div>',
                                      f'<div class="related-grid">{cells}</div>')
    jsonld = [breadcrumb_jsonld(trail, url)]
    body = (head(page["title"], page["metaDescription"], url, page_config=None, jsonld=jsonld)
            + topbar()
            + '<div class="wrap">'
            + '<div class="pagehead">' + crumb(trail) + f'<h1>{esc(page["h1"])}</h1>'
            + (f'<p class="lede">{esc(page.get("lede",""))}</p>' if page.get("lede") else "")
            + '</div>'
            + f'<div class="card content">{body_html}</div>'
            + related_block([p["slug"] for p in GEN_PAGES[:8]], header="Popular generators")
            + '</div>'
            + footer()
            + foot_scripts(with_engine=False))
    write(slug, body)

# ---- 404 ----
def build_404():
    url = BASE + "/404"
    body = (head("Page not found — Fontletr", "That page doesn't exist. Here are the generators that do.", url, page_config=None)
            + topbar()
            + '<div class="wrap"><div class="pagehead"><h1>Page not found</h1>'
            '<p class="lede">That URL doesn’t exist (or doesn’t exist yet). The tools that do are below.</p></div>'
            + related_block([p["slug"] for p in GEN_PAGES], header="All generators")
            + '<div class="card content"><p><a href="/">← Back to the fancy text generator</a></p></div>'
            + '</div>' + footer() + foot_scripts(with_engine=False))
    with open(os.path.join(DIST, "404.html"), "w", encoding="utf-8") as f:
        f.write(body)

# ---- sitemap + robots ----
def build_sitemap(slugs):
    urls = []
    for s in slugs:
        loc = BASE + ("/" if s == "/" else s + "/")
        urls.append(f"<url><loc>{esc(loc)}</loc><changefreq>monthly</changefreq><priority>{'1.0' if s=='/' else '0.7'}</priority></url>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(urls) + "</urlset>")
    with open(os.path.join(DIST, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(xml)
    with open(os.path.join(DIST, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
    # ads.txt — only meaningful once a real AdSense publisher ID is set
    if ADSENSE_CLIENT.startswith("ca-pub-"):
        pub = ADSENSE_CLIENT.replace("ca-", "")  # "pub-1234567890123456"
        with open(os.path.join(DIST, "ads.txt"), "w", encoding="utf-8") as f:
            f.write(f"google.com, {pub}, DIRECT, f08c47fec0942fa0\n")

# ---- run ----
def main():
    # Clean dist/ contents without deleting the dir itself (Windows file locks on the
    # served folder make rmtree(DIST) fail while a local http.server is running).
    os.makedirs(DIST, exist_ok=True)
    for entry in os.listdir(DIST):
        p = os.path.join(DIST, entry)
        try:
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
        except PermissionError:
            pass  # in use; will be overwritten file-by-file below
    dst_assets = os.path.join(DIST, "assets")
    shutil.rmtree(dst_assets, ignore_errors=True)
    os.makedirs(dst_assets, exist_ok=True)
    for entry in os.listdir(ASSETS_SRC):
        shutil.copy2(os.path.join(ASSETS_SRC, entry), os.path.join(dst_assets, entry))
    all_slugs = []
    for p in GEN_PAGES:
        build_generator(p); all_slugs.append(p["slug"])
    for p in SUPPORT:
        build_support(p); all_slugs.append(p["slug"])
    build_404()
    build_sitemap(all_slugs)
    print(f"Built {len(GEN_PAGES)} generator pages + {len(SUPPORT)} support pages + 404 + sitemap.")
    print(f"Total indexable pages: {len(all_slugs)}")
    print(f"Output: {DIST}")
    for s in all_slugs:
        print("  " + (s if s != "/" else "/ (home)"))

if __name__ == "__main__":
    main()
