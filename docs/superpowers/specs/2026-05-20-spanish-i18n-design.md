# Spanish (es-419) Localization — Design

**Date:** 2026-05-20
**Status:** Approved (design), pending implementation plan
**Branch:** `es-i18n`

## Context & Goal

Fontletr (https://fontletr.com) is a static fancy-text generator site built by `build.py`
from `pages.json` (18 generator pages) + `support-pages.json` (6 support pages). It is ~1 week
old and currently English-only. Search Console shows strong impression volume on English style
keywords but few clicks (normal for a new domain ranking on page 2–4).

Goal: add a **fully localized Latin-American Spanish (es-419)** version of the entire site to
capture the large, less-competitive LatAm demand for fancy text (especially gaming-nick and
social-bio searches). This is **real localization targeting real Spanish search intent**, not
machine translation of the English pages.

## Decisions (locked)

| Decision | Choice |
|---|---|
| Target market / variant | **es-419** (Latin America), `hreflang="es-419"`, `og:locale="es_MX"` |
| Scope | **Full parity**: all 18 generators + 6 support pages, **+1 ES-only gaming page** = 19 ES generator pages + 6 ES support pages |
| Site coverage | **Whole site in ES** (generators + UI chrome + Learn pages + about/privacy/contact/all-tools) |
| Build architecture | **Approach A**: separate `pages-es.json` / `support-pages-es.json` + UI string table; locale-aware `build.py`; designed so adding FR later is copy-the-pattern |
| URL structure | `/es/` subdirectory, **Spanish slugs**, **ASCII only** (no accents/ñ) |

## Why young-domain + full ES is safe

The earlier indexing-risk caveat applies to **thin / auto-translated / doorway pages**, not to
genuinely localized content. Native es-419 content targeting distinct ES intent is legitimate new
content for a new audience. Consequence of doing it now: it takes the same ~2–3 months to earn
ranking trust, and indexing happens gradually (limited crawl budget) — patience, not risk.

## URL & Keyword Map (EN → ES)

Slug stored as full path including `/es/` prefix (home = `/es/`). `kw` = primary LatAm keyword.

| EN page | ES slug | Primary keyword (es-419) |
|---|---|---|
| `/` (home) | `/es/` | generador de letras (+ letras para nick / free fire) |
| cursive | `/es/letras-cursivas/` | letras cursivas |
| bold | `/es/letras-en-negrita/` | letras en negrita |
| small | `/es/letras-pequenas/` | letras pequeñas |
| zalgo | `/es/texto-zalgo/` | texto zalgo / texto glitch |
| upside-down | `/es/texto-al-reves/` | texto al revés (voltear texto) |
| cool | `/es/letras-bonitas/` | letras bonitas |
| italic | `/es/letras-italicas/` | letras itálicas |
| big | `/es/letras-grandes/` | letras grandes |
| stylish | `/es/letras-con-estilo/` | letras con estilo / estilosas |
| underline | `/es/texto-subrayado/` | texto subrayado |
| strikethrough | `/es/texto-tachado/` | texto tachado |
| bubble | `/es/letras-en-circulo/` | letras en círculo / burbuja |
| mirror | `/es/texto-en-espejo/` | texto en espejo / invertido |
| aesthetic | `/es/letras-esteticas/` | letras estéticas / aesthetic |
| old-english | `/es/letras-goticas/` | letras góticas |
| japanese | `/es/letras-japonesas/` | letras japonesas / chinas |
| superscript | `/es/superindice-y-subindice/` | superíndice / subíndice |
| *(ES-only, new)* | `/es/letras-para-nick/` | letras para nick / letras para free fire |

Support pages: `/es/todas-las-herramientas/`, `/es/acerca-de/`, `/es/privacidad/`,
`/es/contacto/`, `/es/como-funciona-el-texto-unicode/`,
`/es/donde-funcionan-las-letras-instagram-tiktok-discord/`.

### Language decisions (validated)

1. **cursiva vs itálica** — Colloquial LatAm "letras cursivas" = the loopy handwriting script
   (𝓼𝓬𝓻𝓲𝓹𝓽), so cursive → `letras-cursivas`; italic (slanted) → `letras-italicas`. The pages
   cross-link to disambiguate.
2. **al revés vs espejo** — upside-down → `texto-al-reves` (dominant gag term, "boca abajo");
   mirror → `texto-en-espejo` (mirror/invertido). Avoids cannibalization.
3. **Gaming page** — `/es/letras-para-nick/` is an ES-only page (no EN counterpart) targeting the
   huge LatAm `letras para nick` / `letras para free fire` commercial-intent queries. The home
   page also targets these. No `alt` (English alternate) for this page.

## Build Architecture (Approach A)

### New / changed files

- **`pages-es.json`** — mirror of `pages.json`: ES `site` block (tagline, footerNote,
  compatNoteShared in ES) + 19 ES generator pages. Each page has the same fields as EN
  (`slug`, `kw`, `secondaryKw`, `title`, `metaDescription`, `h1`, `lede`, `focusStyles`, `intro`,
  `where`, `examples`, `pitfalls`, `faqs`, `related`) **written natively in ES**, plus a new
  **`alt`** field = the EN counterpart slug for hreflang pairing (omitted on `letras-para-nick`).
  `focusStyles` and engine style IDs are unchanged (language-agnostic).
- **`support-pages-es.json`** — the 6 support pages in ES (same shape as `support-pages.json`,
  plus `alt`).
- **UI string table** in `build.py` — `STR = {"en": {...}, "es": {...}}` covering every hardcoded
  UI string: nav labels, footer headings, breadcrumb labels, button text (Copy/Clear),
  section headings ("How to use it", "Your text", "Result", "Browse all styles", "FAQ",
  "Related generators", "Examples & use cases", "Where it renders…", "Common mistakes"),
  textarea placeholder, character counter, theme button, ad-slot text, the focus-page blurb.

### `build.py` refactor (locale-aware, EN output unchanged)

- `head(...)`: add `lang` and `alternates` params → emit `<html lang="es">` and
  `<link rel="alternate" hreflang="...">` tags (self + counterpart + `x-default`→EN) + `og:locale`.
- Shared chunks (`topbar`, `footer`, `crumb`, `content_block`, `tool_block`, `where_block`,
  `examples_block`, `pitfalls_block`, `faq_block`, `related_block`) take the locale and read from
  `STR[loc]` instead of inline English.
- Per-locale lookup maps (`slug_to_h1`, `slug_to_kw`) so footer/related links resolve within the
  same locale.
- Routing: ES slugs are full paths (`/es/letras-cursivas/`); `out_path` writes to `dist/es/...`.
  Handle the `/es/` home special case → `dist/es/index.html`.
- hreflang pairing: build EN↔ES map from each ES page's `alt` field; emit alternates both ways.
- Sitemap: include all EN + ES URLs.

### `engine.js` change (minimal, zero EN regression)

- Style labels, category names, and UI strings ("Pin to top", "Copy", "Dark"/"Light",
  "characters", sample fallback) currently hardcoded. Make them read from
  `PAGE_CONFIG.labels` / `PAGE_CONFIG.groups` / `PAGE_CONFIG.ui` **with English fallback**:
  `PAGE_CONFIG.labels[key] || defaultName`.
- `build.py` injects translated `labels`/`groups`/`ui` into `PAGE_CONFIG` **only for ES pages**.
  EN pages omit them → fallback → identical EN output. ES dropdown + buttons render in Spanish.

## Content Localization Principles

- Each ES page written natively in **es-419**, targeting its ES keyword — not translated from EN.
- Same structure/depth as EN (intro ~150 words, 6 FAQ, 5 examples, compatibility table, 4 pitfalls).
- LatAm-anchored examples: Free Fire nicks, Instagram/TikTok bios, WhatsApp estados, group names.
- Tone: neutral "tú", no region-locked slang, vocabulary understood across LatAm.
- Home + `letras-para-nick`: strongest commercial-intent treatment.
- In-content disambiguation cross-links: cursivas↔itálicas, al revés↔espejo.
- Quality checks: title/meta length, no English leakage, ASCII slugs. A native spot-review before
  publication is recommended (optional).

## Execution Phasing

Infrastructure first, then content in priority waves (full parity is still the end state — this is
only the writing order, so the highest-volume pages are polished and shipped first).

1. **Infra** — `build.py` + `engine.js` refactor + `STR[es]` + structured `pages-es.json` scaffold.
   Build runs; ES UI functional.
2. **Wave 1 (money pages)** — home, letras-para-nick, letras-bonitas, letras-goticas,
   letras-cursivas, letras-pequenas.
3. **Wave 2** — negrita, italicas, al-reves, espejo, esteticas, grandes, con-estilo.
4. **Wave 3** — zalgo, subrayado, tachado, en-circulo, japonesas, superindice.
5. **Support** — the 6 ES support pages.

## Non-Goals / Out of Scope

- No French/Portuguese yet (architecture leaves the door open; not built now).
- No subdomain or ccTLD (single-domain `/es/` only).
- No changes to the text-transformation engine logic (Unicode mapping is language-agnostic).
- No new English pages.

## Risks

- **Translation quality** is the whole ballgame. Lazy ES = thin-content risk. Mitigation: native
  writing + optional human spot-review.
- **Gradual indexing** on a young domain — expected, not a defect.
- **build.py refactor regressions** on EN output — mitigation: EN must be byte-comparable (or
  diff-reviewed) before/after the refactor.
