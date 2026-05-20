# tests/test_build.py
import os, json, importlib, sys, re, glob
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
BASE = "https://fontletr.com"
sys.path.insert(0, ROOT)

@pytest.fixture(scope="session", autouse=True)
def built_site():
    build = importlib.import_module("build")
    build.main()
    return DIST

def read(rel):
    with open(os.path.join(DIST, rel), encoding="utf-8") as f:
        return f.read()

# ---- EN regression guard ----
def test_en_home_built():
    html = read("index.html")
    assert '<html lang="en">' in html
    assert "<title>Fancy Text Generator" in html

def test_en_small_text_invariants():
    html = read("small-text-generator/index.html")
    assert '<html lang="en">' in html
    assert "Small Text Generator" in html
    assert '<link rel="canonical" href="https://fontletr.com/small-text-generator/">' in html
    assert "/assets/engine.js" in html

def test_en_footer_links_all_generators():
    html = read("index.html")
    for slug in ["/cursive-text-generator", "/bold-text-generator", "/zalgo-text-generator"]:
        assert f'href="{slug}"' in html

def test_en_pages_have_no_es_prefix_links_in_canonical():
    html = read("bold-text-generator/index.html")
    assert 'canonical" href="https://fontletr.com/bold-text-generator/"' in html

# ---- ES structure ----
def es_pages():
    p = os.path.join(ROOT, "pages-es.json")
    if not os.path.exists(p):
        return []
    return json.load(open(p, encoding="utf-8"))["pages"]

def _rel_for(slug):
    return "es/index.html" if slug == "/es/" else slug.strip("/") + "/index.html"

@pytest.mark.parametrize("page", es_pages(), ids=lambda p: p["slug"])
def test_es_page_structure(page):
    html = read(_rel_for(page["slug"]))
    assert '<html lang="es">' in html
    assert 'hreflang="es-419"' in html
    # English UI must not leak into the ES chrome
    for leak in ["Related generators", "How to use it", ">Copy<", "Your text", "Common mistakes"]:
        assert leak not in html, f"English UI leaked in {page['slug']}: {leak}"

def test_es_slugs_are_ascii():
    for p in es_pages():
        assert p["slug"].isascii(), p["slug"]

def test_gaming_page_has_no_en_alternate():
    if not any(p["slug"] == "/es/letras-para-nick/" for p in es_pages()):
        pytest.skip("gaming page not built yet")
    html = read("es/letras-para-nick/index.html")
    assert 'hreflang="en"' not in html
    assert 'hreflang="es-419"' in html

# ---- hreflang + canonical site-wide audit (the permanent guard) ----
def _scan_pages():
    pages = {}
    files = glob.glob(os.path.join(DIST, "**", "index.html"), recursive=True)
    for f in files:
        rel = os.path.relpath(f, DIST).replace(os.sep, "/").replace("index.html", "")
        url = BASE + "/" + rel
        if url != BASE + "/":
            url = url if url.endswith("/") else url + "/"
        html = open(f, encoding="utf-8").read()
        can = re.search(r'<link rel="canonical" href="([^"]+)"', html)
        alts = re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', html)
        pages[url] = {"canonical": can.group(1) if can else None, "alts": alts}
    return pages

def test_canonical_is_always_self():
    for url, p in _scan_pages().items():
        if p["canonical"]:
            assert p["canonical"] == url, f"{url} canonical -> {p['canonical']}"

def test_hreflang_is_reciprocal():
    pages = _scan_pages()
    altmap = {u: dict(p["alts"]) for u, p in pages.items()}
    for url, p in pages.items():
        for hl, href in p["alts"]:
            if hl == "x-default" or href == url:
                continue
            assert href in altmap, f"{url} -> {href} (target page not built)"
            assert url in altmap[href].values(), \
                f"non-reciprocal: {url} ({hl}) -> {href}, but {href} has no return tag back"

def test_hreflang_has_self_reference():
    for url, p in _scan_pages().items():
        if p["alts"]:  # if a page declares any alternates, one must point to itself
            assert any(hl != "x-default" and href == url for hl, href in p["alts"]), \
                f"{url} has alternates but no self-referencing hreflang"
