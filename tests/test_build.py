# tests/test_build.py
import os, json, importlib, sys
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
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
