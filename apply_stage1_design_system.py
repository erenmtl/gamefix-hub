# -*- coding: utf-8 -*-
import os
import re

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def clean_seed_data():
    seed_path = os.path.join(ROOT_DIR, "static", "seed_data.js")
    with open(seed_path, "r", encoding="utf-8") as f:
        txt = f.read()

    # Replace third-party image_url / game_image_url with copyright-free monogram route
    txt = re.sub(
        r'"(image_url|game_image_url)"\s*:\s*"https?://[^"]+"',
        r'"\1": "./api/games/cover/monogram"',
        txt,
    )
    with open(seed_path, "w", encoding="utf-8") as wf:
        wf.write(txt)
    print("[OK] Removed third-party game cover URLs from static/seed_data.js")


def clean_game_catalog():
    cat_path = os.path.join(ROOT_DIR, "game_catalog.py")
    with open(cat_path, "r", encoding="utf-8") as f:
        txt = f.read()

    txt = re.sub(
        r'GAME_COVER_URLS\s*=\s*\{.*?\n\}',
        "GAME_COVER_URLS = {}",
        txt,
        flags=re.S,
    )
    with open(cat_path, "w", encoding="utf-8") as wf:
        wf.write(txt)
    print("[OK] Emptied third-party GAME_COVER_URLS in game_catalog.py")


def update_app_js():
    app_path = os.path.join(ROOT_DIR, "static", "app.js")
    with open(app_path, "r", encoding="utf-8") as f:
        txt = f.read()

    # Always resolve cover URLs to our copyright-free monogram SVG generator
    txt = re.sub(
        r"function resolveSafeCoverUrl\(rawUrl, slugOrName, accentColor, subtitle\)\s*\{.*?\n\}",
        "function resolveSafeCoverUrl(rawUrl, slugOrName, accentColor, subtitle) {\n  return fallbackCover(slugOrName, accentColor, subtitle);\n}",
        txt,
        flags=re.S,
    )
    txt = txt.replace(
        "const imgSrc = g.image_url || fallbackCover(g.slug, g.accent_color);",
        "const imgSrc = fallbackCover(g.short_name || g.name || g.slug, g.accent_color);",
    )
    txt = txt.replace(
        'src="${issue.game_image_url || fallbackCover(issue.game_slug, issue.accent_color)}"',
        'src="${fallbackCover(issue.game_short_name || issue.game_slug, issue.accent_color)}"',
    )
    txt = txt.replace(
        'src="${t.game_image_url || fallbackCover(t.game_slug, t.accent_color)}"',
        'src="${fallbackCover(t.game_short_name || t.game_slug, t.accent_color)}"',
    )

    with open(app_path, "w", encoding="utf-8") as wf:
        wf.write(txt)
    print("[OK] Updated static/app.js to use copyright-free monogram SVG badges everywhere")


def update_index_html():
    idx_path = os.path.join(ROOT_DIR, "index.html")
    with open(idx_path, "r", encoding="utf-8") as f:
        txt = f.read()

    if "ui_components.js" not in txt:
        txt = txt.replace(
            '<script src="./static/seed_data.js"></script>',
            '<script src="./static/ui_components.js"></script>\n  <script src="./static/seed_data.js"></script>',
        )
        with open(idx_path, "w", encoding="utf-8") as wf:
            wf.write(txt)
        print("[OK] Included static/ui_components.js in index.html")


if __name__ == "__main__":
    clean_seed_data()
    clean_game_catalog()
    update_app_js()
    update_index_html()
