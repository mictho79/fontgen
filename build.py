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

# ---- UI strings per locale. EN values mirror the literals previously hardcoded. ----
STR = {
  "en": {
    "lang": "en", "og_locale": "en_US", "hreflang": "en",
    "nav_generator": "Generator", "nav_all_tools": "All tools", "nav_how": "How it works",
    "footer_h_generators": "Generators", "footer_h_learn": "Learn", "footer_h_site": "Site",
    "learn_how": "How Unicode text works",
    "learn_where": "Where it works (Instagram, TikTok, Discord...)",
    "site_about": "About", "site_all_tools": "All tools", "site_privacy": "Privacy", "site_contact": "Contact",
    "crumb_home": "Fontletr", "crumb_tools": "Tools",
    "tool_your_text": "Your text", "tool_placeholder": "Type or paste something…",
    "tool_result": "Result", "tool_copy": "Copy", "tool_clear": "Clear",
    "tool_browse": "Browse all styles", "tool_count_suffix": "styles",
    "tool_fav_only": "favorites only:", "tool_fav_off": "Off",
    "tool_focus_blurb_pre": "Pick the look you want above, then hit Copy. Want every option? ",
    "tool_focus_link": "Browse all 80+ text styles in the fancy text generator",
    "tool_focus_blurb_post": " — or see related ones below.",
    "ad_slot": "One ad unit lives here — below the fold. No popup, no interstitial, no notification prompt. Ever.",
    "content_how_h": "How to use it",
    "content_how_p": "Type in the box on the left. The style you’ve picked on the right updates as you type — no “generate” button. Click <strong>Copy</strong> and paste it wherever you need. On the home page you can also browse every style in the list below and click any row to load it into the panel.",
    "where_h": "Where it renders, and where it breaks",
    "where_th_app": "App / platform", "where_th_where": "Where", "where_th_status": "Status", "where_th_notes": "Notes",
    "st_ok": "Works", "st_partial": "Partial", "st_no": "Won't render",
    "where_full_pre": "The full ", "where_full_link": "cross-app compatibility page", "where_full_post": " goes wider.",
    "examples_h": "Examples & use cases", "pitfalls_h": "Common mistakes",
    "faq_h": "FAQ", "related_h": "Related generators", "related_all": "all 80+ styles in one place",
    "home_h1": "Fancy Text Generator",
    "theme_btn": "Theme: Light ▾",
    "counter_zero": "0 characters",
  },
  "es": {
    "lang": "es", "og_locale": "es_MX", "hreflang": "es-419",
    "nav_generator": "Generador", "nav_all_tools": "Todas las herramientas", "nav_how": "Cómo funciona",
    "footer_h_generators": "Generadores", "footer_h_learn": "Aprende", "footer_h_site": "Sitio",
    "learn_how": "Cómo funciona el texto Unicode",
    "learn_where": "Dónde funciona (Instagram, TikTok, Discord...)",
    "site_about": "Acerca de", "site_all_tools": "Todas las herramientas", "site_privacy": "Privacidad", "site_contact": "Contacto",
    "crumb_home": "Fontletr", "crumb_tools": "Herramientas",
    "tool_your_text": "Tu texto", "tool_placeholder": "Escribe o pega algo…",
    "tool_result": "Resultado", "tool_copy": "Copiar", "tool_clear": "Borrar",
    "tool_browse": "Explorar todos los estilos", "tool_count_suffix": "estilos",
    "tool_fav_only": "solo favoritos:", "tool_fav_off": "No",
    "tool_focus_blurb_pre": "Elige el estilo que quieras arriba y toca Copiar. ¿Quieres todas las opciones? ",
    "tool_focus_link": "Explora los más de 80 estilos en el generador de letras",
    "tool_focus_blurb_post": " — o mira los relacionados abajo.",
    "ad_slot": "Aquí va una sola unidad de anuncio, debajo del pliegue. Sin pop-ups, sin intersticiales, sin pedir notificaciones. Nunca.",
    "content_how_h": "Cómo usarlo",
    "content_how_p": "Escribe en el cuadro de la izquierda. El estilo que elegiste a la derecha se actualiza mientras escribes — sin botón de «generar». Toca <strong>Copiar</strong> y pégalo donde lo necesites. En la página de inicio también puedes explorar todos los estilos de la lista y tocar cualquier fila para cargarlo en el panel.",
    "where_h": "Dónde funciona y dónde falla",
    "where_th_app": "App / plataforma", "where_th_where": "Dónde", "where_th_status": "Estado", "where_th_notes": "Notas",
    "st_ok": "Funciona", "st_partial": "Parcial", "st_no": "No se ve",
    "where_full_pre": "La ", "where_full_link": "página de compatibilidad entre apps", "where_full_post": " entra en más detalle.",
    "examples_h": "Ejemplos y usos", "pitfalls_h": "Errores comunes",
    "faq_h": "Preguntas frecuentes", "related_h": "Generadores relacionados", "related_all": "los más de 80 estilos en un solo lugar",
    "home_h1": "Generador de Letras",
    "theme_btn": "Tema: Claro ▾",
    "counter_zero": "0 caracteres",
  },
}

# engine.js label/UI overrides injected into PAGE_CONFIG for non-EN locales
ENGINE_ES = {
  "labels": {
    "bold-sans": "Negrita (sans)", "bold-serif": "Negrita (serif)", "italic": "Itálica",
    "bold-italic": "Itálica negrita", "sans-italic": "Itálica sans", "sans-serif": "Sans-serif",
    "script-cursive": "Cursiva · script", "bold-script": "Cursiva negrita",
    "fraktur": "Gótica (Old English)", "bold-fraktur": "Gótica negrita", "small-caps": "Versalitas",
    "double-struck": "Doble trazo", "monospace": "Monoespaciada", "full-width": "Ancho completo",
    "circled": "En círculo (burbuja)", "circled-negative": "En círculo (relleno)", "squared": "En cuadro",
    "parenthesized": "Entre paréntesis", "bracketed": "Entre corchetes ⟦x⟧",
    "superscript": "Superíndice", "subscript": "Subíndice", "spaced": "Espaciada", "dotted": "Con puntos",
    "upside-down": "Al revés", "reversed": "En espejo", "strikethrough": "Tachada",
    "underline": "Subrayada", "double-underline": "Doble subrayado", "slashed": "Barrada", "zalgo": "Zalgo (glitch)",
  },
  "groups": {"bold": "Peso", "callig": "Caligráfica", "outline": "Contorno", "deco": "Decorativa", "fx": "Efecto", "fun": "Varios"},
  "ui": {
    "charOne": "carácter", "charMany": "caracteres", "sample": "letras bonitas",
    "pinned": "★ Fijados", "allStyles": "Todos los estilos", "pinTitle": "Fijar arriba",
    "copy": "Copiar", "copied": "✓ Copiado",
    "noFavs": "Aún no hay favoritos — toca la estrella junto a cualquier estilo para fijarlo aquí.",
    "styles": "estilos", "theme": "Tema: ", "dark": "Oscuro", "light": "Claro", "on": "Sí", "off": "No",
  },
}

# AdSense: when a client ID is configured, inject the loader in <head> and a real
# <ins class="adsbygoogle"> where the placeholder used to be. Until then, the slot
# stays a visible placeholder so dev/preview looks honest.
ADSENSE_HEAD = (
    f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>'
    if ADSENSE_CLIENT else ""
)
def ad_slot(loc="en"):
    if ADSENSE_CLIENT:
        return ('<div class="adslot"><ins class="adsbygoogle" style="display:block" '
                f'data-ad-client="{ADSENSE_CLIENT}" data-ad-slot="0000000000" '
                'data-ad-format="auto" data-full-width-responsive="true"></ins>'
                '<script>(adsbygoogle=window.adsbygoogle||[]).push({});</script></div>')
    return f'<div class="adslot">{esc(STR[loc]["ad_slot"])}</div>' 

# ---- lookup maps ----
slug_to_h1 = {p["slug"]: p["h1"] for p in GEN_PAGES}
slug_to_kw = {p["slug"]: p["kw"] for p in GEN_PAGES}
slug_to_h1["/"] = "Fancy Text Generator"

# Module-level placeholders — populated in main() once ES data is loaded.
ES_PAGES = []
SITE_FOR = {"en": SITE}
H1_FOR = {"en": {**slug_to_h1}}
KW_FOR = {"en": {p["slug"]: p["kw"] for p in GEN_PAGES}}
EN2ES = {}
ES2EN = {}

def loc_url(en_slug, loc):
    """Map an EN support/generator slug to the same page in loc. Falls back to EN slug."""
    if loc == "en":
        return en_slug
    return EN2ES.get(en_slug, en_slug)

def alternates_for(slug, loc):
    """Return [(hreflang, abs_url), ...] incl. self + counterpart + x-default(EN)."""
    out = []
    def absu(s):
        return BASE + (s if s.endswith("/") else s + "/")
    if loc == "en":
        en_slug, es_slug = slug, EN2ES.get(slug)
    else:
        es_slug, en_slug = slug, ES2EN.get(slug)
    if en_slug is not None:
        out.append((STR["en"]["hreflang"], absu(en_slug)))
    if es_slug is not None:
        out.append((STR["es"]["hreflang"], absu(es_slug)))
    if en_slug is not None:
        out.append(("x-default", absu(en_slug)))
    return out

STOP = {"text", "generator", "font", "fonts", "online", "free", "tool", "letters", "maker"}
def sample_word(kw):
    parts = [w for w in kw.split() if w.lower() not in STOP]
    s = " ".join(parts).strip()
    return s if s else "fancy text"

def esc(s): return html.escape(str(s), quote=True)

# ---- shared chunks ----
def topbar(loc="en"):
    s = STR[loc]
    home = "/" if loc == "en" else "/es/"
    return ('<div class="topbar">'
            f'<span class="logo"><a href="{home}">Fontletr</a></span>'
            f'<nav><a href="{home}">{esc(s["nav_generator"])}</a>'
            f'<a href="{loc_url("/all-tools", loc)}">{esc(s["nav_all_tools"])}</a>'
            f'<a href="{loc_url("/how-unicode-text-works", loc)}">{esc(s["nav_how"])}</a></nav>'
            '<span class="spacer"></span>'
            f'<button class="who" id="themeBtn" type="button">{esc(s.get("theme_btn","Theme: Light ▾"))}</button>'
            '</div>')

GEN_FOOTER_LINKS = [(p["slug"], p["h1"]) for p in GEN_PAGES]
def footer(loc="en"):
    s = STR[loc]
    pages = ES_PAGES if loc == "es" else GEN_PAGES
    gens = "".join(f'<li><a href="{esc(p["slug"])}">{esc(p["h1"])}</a></li>' for p in pages)
    learn = (f'<li><a href="{loc_url("/how-unicode-text-works", loc)}">{esc(s["learn_how"])}</a></li>'
             f'<li><a href="{loc_url("/does-fancy-text-work-on-instagram-tiktok-discord", loc)}">{esc(s["learn_where"])}</a></li>')
    site = (f'<li><a href="{loc_url("/about", loc)}">{esc(s["site_about"])}</a></li>'
            f'<li><a href="{loc_url("/all-tools", loc)}">{esc(s["site_all_tools"])}</a></li>'
            f'<li><a href="{loc_url("/privacy", loc)}">{esc(s["site_privacy"])}</a></li>'
            f'<li><a href="{loc_url("/contact", loc)}">{esc(s["site_contact"])}</a></li>')
    return ('<footer><div class="footer-inner"><div class="footer-cols">'
            f'<div><h4>{esc(s["footer_h_generators"])}</h4><ul>{gens}</ul></div>'
            f'<div><h4>{esc(s["footer_h_learn"])}</h4><ul>{learn}</ul></div>'
            f'<div><h4>{esc(s["footer_h_site"])}</h4><ul>{site}</ul></div>'
            '</div>'
            f'<div class="footer-note">{esc(SITE_FOR[loc]["footerNote"])}</div>'
            '</div></footer>')

def crumb(trail, loc="en"):  # trail = list of (href|None, label)
    out = []
    for href, label in trail:
        if href:
            out.append(f'<a href="{esc(href)}">{esc(label)}</a>')
        else:
            out.append(esc(label))
    return '<div class="crumb">' + " / ".join(out) + "</div>"

def head(title, desc, canonical, loc="en", alternates=None, page_config=None, jsonld=None, extra_meta=""):
    s = STR[loc]
    cfg = ""
    if page_config is not None:
        cfg = "<script>window.PAGE_CONFIG=" + json.dumps(page_config) + ";</script>"
    ld = ""
    if jsonld:
        ld = "".join('<script type="application/ld+json">' + json.dumps(b) + "</script>" for b in jsonld)
    alts = ""
    for hl, href in (alternates or []):
        alts += f'<link rel="alternate" hreflang="{esc(hl)}" href="{esc(href)}">'
    return ('<!DOCTYPE html><html lang="' + esc(s["lang"]) + '"><head><meta charset="UTF-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">'
            '<link rel="apple-touch-icon" href="/assets/favicon.svg">'
            f'<title>{esc(title)}</title>'
            f'<meta name="description" content="{esc(desc)}">'
            f'<link rel="canonical" href="{esc(canonical)}">'
            f'<meta property="og:title" content="{esc(title)}">'
            f'<meta property="og:description" content="{esc(desc)}">'
            f'<meta property="og:type" content="website"><meta property="og:url" content="{esc(canonical)}">'
            f'<meta property="og:locale" content="{esc(s["og_locale"])}">'
            '<meta name="robots" content="index,follow">'
            f'{alts}{extra_meta}{ADSENSE_HEAD}'
            f'<link rel="stylesheet" href="/assets/styles.css?v={CSS_V}">'
            f'{cfg}{ld}</head><body>')

def foot_scripts(with_engine=True):
    eng = f'<script src="/assets/engine.js?v={JS_V}" defer></script>' if with_engine else ""
    return f"{eng}</body></html>"

# ---- the tool block (shared by every generator page) ----
def tool_block(page, loc="en"):
    s = STR[loc]
    home = "/" if loc == "en" else "/es/"
    sample = esc(sample_word(page["kw"]))
    focus = page.get("focusStyles") or []
    right_label = page["h1"].replace(" Generator", "") if focus else s["tool_result"]
    parts = []
    # two-panel translator: left = your text, right = chosen style
    parts.append(
        '<div class="translator">'
        f'<div class="card panel"><div class="card-head">{esc(s["tool_your_text"])}</div><div class="card-body">'
        f'<textarea id="input" placeholder="{esc(s["tool_placeholder"])}" autofocus>{sample}</textarea>'
        f'<div class="field-meta"><span id="counter">{esc(s["counter_zero"])}</span>'
        f'<button id="clearBtn" type="button">{esc(s["tool_clear"])}</button></div>'
        '</div></div>'
        '<div class="swap" aria-hidden="true">→</div>'
        '<div class="card panel"><div class="card-head">'
        f'<span class="ch-label">{esc(right_label)}</span>'
        '<select id="styleSelect" class="style-select" aria-label="Choose a style"></select></div>'
        '<div class="card-body">'
        '<div id="bigOut" class="big-out"></div>'
        f'<div class="out-actions"><button id="bigCopy" class="copy" type="button">{esc(s["tool_copy"])}</button></div>'
        '</div></div>'
        '</div>')
    parts.append(ad_slot(loc))
    if focus:
        parts.append(
            f'<div class="card content" style="padding:14px 16px"><p style="margin:0">{esc(s["tool_focus_blurb_pre"])}'
            f'<a href="{home}">{esc(s["tool_focus_link"])}</a>{esc(s["tool_focus_blurb_post"])}</p></div>')
    else:
        parts.append(
            f'<div class="card"><div class="card-head">{esc(s["tool_browse"])} <span class="count" id="styleCount">— {esc(s["tool_count_suffix"])}</span>'
            f'<span class="toggle" style="margin-left:14px">{esc(s["tool_fav_only"])} <button id="favOnly" type="button"><b id="favState">{esc(s["tool_fav_off"])}</b></button></span></div>'
            '<div class="card-body tight" id="results"></div></div>')
    return "".join(parts)

# ---- content + faq + related (shared) ----
def content_block(page, loc="en"):
    s = STR[loc]
    kw_heading = page["kw"][0].upper() + page["kw"][1:]
    intro = page["intro"]
    return (
        '<div class="card content">'
        f'<h2>{esc(kw_heading)}</h2><p>{intro}</p>'
        f'<h2>{esc(s["content_how_h"])}</h2><p>{s["content_how_p"]}</p>'
        '</div>')

def where_block(page, loc="en"):
    s = STR[loc]
    w = page.get("where")
    if not w: return ""
    st_label = {"ok": s["st_ok"], "partial": s["st_partial"], "no": s["st_no"]}
    rows = ""
    for r in w.get("rows", []):
        st = r.get("status", "ok")
        rows += (f'<tr><td class="app">{esc(r["app"])}</td>'
                 f'<td class="fields">{esc(r.get("fields",""))}</td>'
                 f'<td><span class="st st-{esc(st)}">{esc(st_label.get(st,st))}</span></td>'
                 f'<td class="cnote">{esc(r.get("note",""))}</td></tr>')
    compat_url = loc_url("/does-fancy-text-work-on-instagram-tiktok-discord", loc)
    return (
        f'<div class="card content"><h2>{esc(s["where_h"])}</h2>'
        f'<p>{esc(w.get("intro",""))}</p>'
        f'<table class="compat"><thead><tr><th>{esc(s["where_th_app"])}</th><th>{esc(s["where_th_where"])}</th><th>{esc(s["where_th_status"])}</th><th>{esc(s["where_th_notes"])}</th></tr></thead>'
        f'<tbody>{rows}</tbody></table>'
        f'<p class="small-note">{esc(SITE_FOR[loc]["compatNoteShared"])} {s["where_full_pre"]}<a href="{compat_url}">{esc(s["where_full_link"])}</a>{s["where_full_post"]}</p>'
        '</div>')

def examples_block(page, loc="en"):
    s = STR[loc]
    ex = page.get("examples")
    if not ex: return ""
    items = "".join(
        f'<li><strong>{esc(i["label"])}</strong> — {i["text"]}</li>' for i in ex.get("items", []))
    return (
        f'<div class="card content"><h2>{esc(s["examples_h"])}</h2>'
        f'<p>{esc(ex.get("intro",""))}</p><ul>{items}</ul></div>')

def pitfalls_block(page, loc="en"):
    s = STR[loc]
    p = page.get("pitfalls")
    if not p: return ""
    items = "".join(f'<li><strong>{esc(i["title"])}.</strong> {i["text"]}</li>' for i in p)
    return f'<div class="card content"><h2>{esc(s["pitfalls_h"])}</h2><ul>{items}</ul></div>'

def faq_block(faqs, loc="en"):
    s = STR[loc]
    if not faqs: return ""
    items = "".join(
        f'<details><summary>{esc(q["q"])}</summary><div class="a">{esc(q["a"])}</div></details>'
        for q in faqs)
    return f'<div class="card content"><h2>{esc(s["faq_h"])}</h2><div class="faq">{items}</div></div>'

def related_block(slugs, loc="en", header=None):
    s = STR[loc]
    if header is None:
        header = s["related_h"]
    if not slugs: return ""
    h1_map = H1_FOR.get(loc, H1_FOR["en"])
    kw_map = KW_FOR.get(loc, KW_FOR["en"])
    home_slug = "/es/" if loc == "es" else "/"
    cells = []
    for slug in slugs:
        label = h1_map.get(slug, slug)
        kw = kw_map.get(slug, "")
        if slug == home_slug:
            sub = f'<span>{esc(s["related_all"])}</span>'
        elif kw:
            sub = f'<span>{esc(kw)}</span>'
        else:
            sub = ""
        cells.append(f'<a href="{esc(slug)}">{esc(label)}{sub}</a>')
    return ('<div class="card content"><h2>' + esc(header) + '</h2><div class="related-grid">' + "".join(cells) + '</div></div>')
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
def build_generator(page, loc="en"):
    s = STR[loc]
    slug = page["slug"]
    home = "/" if loc == "en" else "/es/"
    url = BASE + (slug if slug.endswith("/") else slug + "/")
    all_tools_url = loc_url("/all-tools", loc)
    if slug in ("/", "/es/"):
        trail = [(None, s["crumb_home"])]
    else:
        trail = [(home, s["crumb_home"]), (all_tools_url, s["crumb_tools"]), (None, page["h1"])]
    jsonld = [webapp_jsonld(page["h1"], url, page["metaDescription"])]
    fld = faq_jsonld(page.get("faqs"), url)
    if fld: jsonld.append(fld)
    if len(trail) > 1: jsonld.append(breadcrumb_jsonld(trail, url))
    page_config = {"slug": slug, "focusStyles": page.get("focusStyles") or []}
    if loc == "es":
        page_config.update(ENGINE_ES)
    body = (head(page["title"], page["metaDescription"], url,
                 loc=loc,
                 alternates=alternates_for(slug, loc),
                 page_config=page_config,
                 jsonld=jsonld)
            + topbar(loc=loc)
            + '<div class="wrap">'
            + '<div class="pagehead">' + crumb(trail) + f'<h1>{esc(page["h1"])}</h1>'
            + (f'<p class="lede">{esc(page.get("lede",""))}</p>' if page.get("lede") else "")
            + '</div>'
            + tool_block(page, loc=loc)
            + content_block(page, loc=loc)
            + where_block(page, loc=loc)
            + examples_block(page, loc=loc)
            + pitfalls_block(page, loc=loc)
            + faq_block(page.get("faqs"), loc=loc)
            + related_block(page.get("related"), loc=loc, header=s["related_h"])
            + '</div>'
            + footer(loc=loc)
            + foot_scripts(with_engine=True))
    write(slug, body)

# ---- build support pages ----
def build_support(page, loc="en"):
    s = STR[loc]
    slug = page["slug"]
    home = "/" if loc == "en" else "/es/"
    url = BASE + slug + "/"
    trail = [(home, s["crumb_home"]), (None, page.get("crumb", page["h1"]))]
    body_html = page["bodyHtml"].replace("{CONTACT_EMAIL}", esc(CONTACT_EMAIL))
    if page.get("renderToolsList"):
        pages = ES_PAGES if loc == "es" else GEN_PAGES
        kw_map = KW_FOR.get(loc, KW_FOR["en"])
        cells = "".join(
            f'<a href="{esc(p["slug"])}">{esc(p["h1"])}<span>{esc(kw_map.get(p["slug"],""))}</span></a>'
            for p in pages)
        body_html = body_html.replace('<div id="toolsList"></div>',
                                      f'<div class="related-grid">{cells}</div>')
    jsonld = [breadcrumb_jsonld(trail, url)]
    body = (head(page["title"], page["metaDescription"], url,
                 loc=loc,
                 alternates=alternates_for(slug, loc),
                 page_config=None,
                 jsonld=jsonld)
            + topbar(loc=loc)
            + '<div class="wrap">'
            + '<div class="pagehead">' + crumb(trail) + f'<h1>{esc(page["h1"])}</h1>'
            + (f'<p class="lede">{esc(page.get("lede",""))}</p>' if page.get("lede") else "")
            + '</div>'
            + f'<div class="card content">{body_html}</div>'
            + related_block([p["slug"] for p in (ES_PAGES if loc == "es" else GEN_PAGES)[:8]],
                            loc=loc, header="Popular generators" if loc == "en" else "Generadores populares")
            + '</div>'
            + footer(loc=loc)
            + foot_scripts(with_engine=False))
    write(slug, body)

# ---- 404 ----
def build_404():
    url = BASE + "/404"
    lede_p = "<p class=\"lede\">That URL doesn't exist (or doesn't exist yet). The tools that do are below.</p></div>"
    body = (head("Page not found — Fontletr", "That page doesn't exist. Here are the generators that do.", url,
                 loc="en", page_config=None)
            + topbar(loc="en")
            + '<div class="wrap"><div class="pagehead"><h1>Page not found</h1>'
            + lede_p
            + related_block([p["slug"] for p in GEN_PAGES], loc="en", header="All generators")
            + '<div class="card content"><p><a href="/">← Back to the fancy text generator</a></p></div>'
            + '</div>' + footer(loc="en") + foot_scripts(with_engine=False))
    with open(os.path.join(DIST, "404.html"), "w", encoding="utf-8") as f:
        f.write(body)

# ---- sitemap + robots ----
def build_sitemap(items):
    urls = []
    for loc_code, s in items:
        loc_path = s if s.endswith("/") else s + "/"
        loc_url_abs = BASE + loc_path
        prio = "1.0" if s in ("/", "/es/") else "0.7"
        urls.append(f"<url><loc>{esc(loc_url_abs)}</loc><changefreq>monthly</changefreq><priority>{prio}</priority></url>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(urls) + "</urlset>")
    with open(os.path.join(DIST, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(xml)
    with open(os.path.join(DIST, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nAllow: /\nSitemap: " + BASE + "/sitemap.xml\n")
    # ads.txt - only meaningful once a real AdSense publisher ID is set
    if ADSENSE_CLIENT.startswith("ca-pub-"):
        pub = ADSENSE_CLIENT.replace("ca-", "")
        with open(os.path.join(DIST, "ads.txt"), "w", encoding="utf-8") as f:
            f.write(f"google.com, {pub}, DIRECT, f08c47fec0942fa0\n")

# ---- run ----
def main():
    global ES_PAGES, SITE_FOR, H1_FOR, KW_FOR, EN2ES, ES2EN
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

    # Load ES data if available. Each locale file is independent: generators build
    # from pages-es.json even before support-pages-es.json exists.
    es_json_path = os.path.join(ROOT, "pages-es.json")
    support_es_json_path = os.path.join(ROOT, "support-pages-es.json")
    DATA_ES = None
    SUPPORT_ES = []
    if os.path.exists(es_json_path):
        with open(es_json_path, encoding="utf-8") as f:
            DATA_ES = json.load(f)
        ES_PAGES = DATA_ES["pages"]
    if os.path.exists(support_es_json_path):
        with open(support_es_json_path, encoding="utf-8") as f:
            SUPPORT_ES = json.load(f)["pages"]
    if DATA_ES is not None:
        SITE_ES = DATA_ES["site"]
        SITE_FOR = {"en": SITE, "es": SITE_ES}
        H1_FOR = {
            "en": {**{p["slug"]: p["h1"] for p in GEN_PAGES}, "/": "Fancy Text Generator"},
            "es": {**{p["slug"]: p["h1"] for p in ES_PAGES}, "/es/": "Generador de Letras"},
        }
        KW_FOR = {"en": {p["slug"]: p["kw"] for p in GEN_PAGES},
                  "es": {p["slug"]: p["kw"] for p in ES_PAGES}}
        EN2ES = {p["alt"]: p["slug"] for p in ES_PAGES if p.get("alt")}
        EN2ES_SUPPORT = {p["alt"]: p["slug"] for p in SUPPORT_ES if p.get("alt")}
        EN2ES.update(EN2ES_SUPPORT)
        ES2EN = {v: k for k, v in EN2ES.items()}

    all_slugs = []
    for p in GEN_PAGES:
        build_generator(p, "en"); all_slugs.append(("en", p["slug"]))
    for p in SUPPORT:
        build_support(p, "en"); all_slugs.append(("en", p["slug"]))
    for p in ES_PAGES:
        build_generator(p, "es"); all_slugs.append(("es", p["slug"]))
    for p in SUPPORT_ES:
        build_support(p, "es"); all_slugs.append(("es", p["slug"]))
    build_404()
    build_sitemap(all_slugs)
    en_count = len(GEN_PAGES)
    es_count = len(ES_PAGES)
    print(f"Built {en_count} EN generator + {len(SUPPORT)} EN support + {es_count} ES generator + {len(SUPPORT_ES)} ES support + 404 + sitemap.")
    print(f"Total indexable pages: {len(all_slugs)}")
    print(f"Output: {DIST}")

if __name__ == "__main__":
    main()
