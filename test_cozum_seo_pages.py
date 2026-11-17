# -*- coding: utf-8 -*-
import os
import re
import json
import xml.etree.ElementTree as ET
from fastapi.testclient import TestClient
import main
import generate_cozum_seo_pages as gen


def run_tests():
    xml_str = main.regenerate_sitemap_xml()
    root = ET.fromstring(xml_str)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = {
        u.find("sm:loc", ns).text: u.find("sm:lastmod", ns).text
        for u in root.findall("sm:url", ns)
    }

    assert "https://oyuncoz.com/" in locs, "Missing homepage in sitemap.xml"
    assert locs["https://oyuncoz.com/"] == "2026-11-17"

    client = TestClient(main.app)
    r_home = client.get("/")
    assert r_home.status_code == 200
    home_html = r_home.text
    assert "Popüler Oyun Hataları ve Çözüm Rehberleri" in home_html

    for p in gen.PAGES:
        slug = p["slug"]
        fpath = os.path.join(main.ROOT_DIR, "cozum", slug)
        assert os.path.isfile(fpath), f"Missing {fpath}"
        with open(fpath, "r", encoding="utf-8") as f:
            txt = f.read()

        # Check relative paths (../ and ./)
        for rel in re.findall(r'(?:href|src)="(\.\.?/[^"]+)"', txt):
            clean_rel = rel.split("#")[0].split("?")[0]
            target = os.path.normpath(os.path.join(main.ROOT_DIR, "cozum", clean_rel))
            assert os.path.exists(target), f"Broken relative path {rel} in {slug} -> {target}"

        # Check JSON-LD FAQPage + TechArticle + BreadcrumbList
        m = re.search(
            r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>',
            txt,
            re.S,
        )
        assert m, f"Missing JSON-LD in {slug}"
        jd = json.loads(m.group(1))
        types = [item.get("@type") for item in jd.get("@graph", [])]
        assert "FAQPage" in types and "TechArticle" in types and "BreadcrumbList" in types

        # Check homepage link
        assert f"./cozum/{slug}" in home_html, f"Missing homepage link for {slug}"

        # Check sitemap entry & date
        full_url = f"https://oyuncoz.com/cozum/{slug}"
        assert full_url in locs, f"Missing {full_url} in sitemap.xml"
        assert locs[full_url] == "2026-11-17", f"Wrong lastmod for {full_url}"

        # Check FastAPI HTTP 200
        resp = client.get(f"/cozum/{slug}")
        assert resp.status_code == 200, f"HTTP {resp.status_code} for /cozum/{slug}"

    r_robots = client.get("/robots.txt")
    assert r_robots.status_code == 200
    assert "Sitemap: https://oyuncoz.com/sitemap.xml" in r_robots.text

    print(
        f"[PASS] All 30 /cozum/ static SEO pages, relative paths, JSON-LD FAQPage schemas, index.html directory, robots.txt, and sitemap.xml ({len(locs)} URLs) verified!"
    )


if __name__ == "__main__":
    run_tests()
