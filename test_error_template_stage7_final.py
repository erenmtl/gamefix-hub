# -*- coding: utf-8 -*-
"""
AŞAMA 7: Tüm 13 Yeni Hata Kodu Sayfası Son Kontrol ve Denetim Betiği
Kontroller:
1. Tek <h1>
2. title <= 60 karakter
3. meta description <= 160 karakter
4. Canonical doğru (https://oyuncoz.com/<slug>)
5. JSON-LD geçerli (TechArticle + BreadcrumbList, FAQPage/HowTo yok)
6. Breadcrumb çalışıyor (tüm breadcrumb linkleri HTTP 200)
7. İç linkler kırık değil (sayfadaki tüm iç linkler HTTP 200)
8. sitemap.xml içinde yer alıyor (gerçek lastmod ile)
9. noindex yok
"""
import os
import re
import html
import json
import xml.etree.ElementTree as ET
from fastapi.testclient import TestClient
import main
import error_page_builder as builder


def run_stage7_audit():
    with open(builder.DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    pages = data.get("pages", [])
    assert len(pages) == 13, f"Expected 13 pages, got {len(pages)}"

    xml_str = main.regenerate_sitemap_xml()
    root = ET.fromstring(xml_str)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_locs = {
        u.find("sm:loc", ns).text: u.find("sm:lastmod", ns).text
        for u in root.findall("sm:url", ns)
    }

    client = TestClient(main.app)
    report_rows = []

    for p in pages:
        slug = p["slug"]
        url_path = f"/{slug}"
        expected_canonical = f"https://oyuncoz.com/{slug}"

        resp = client.get(url_path)
        assert resp.status_code == 200, f"{url_path} returned {resp.status_code}"
        html_txt = resp.text

        # 1. Single H1
        h1_list = re.findall(r"<h1\b[^>]*>(.*?)</h1>", html_txt, flags=re.S)
        assert len(h1_list) == 1, f"{slug}: Expected 1 H1, found {len(h1_list)}"

        # 2. Title <= 60
        m_title = re.search(r"<title>(.*?)</title>", html_txt, flags=re.S)
        assert m_title, f"{slug}: Missing <title>"
        title_txt = html.unescape(m_title.group(1))
        assert len(title_txt) <= 60, f"{slug}: Title > 60 chars ({len(title_txt)}): {title_txt}"

        # 3. Meta description <= 160
        m_desc = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', html_txt)
        assert m_desc, f"{slug}: Missing meta description"
        desc_txt = html.unescape(m_desc.group(1))
        assert len(desc_txt) <= 160, f"{slug}: Description > 160 chars ({len(desc_txt)})"

        # 4. Canonical exact match
        m_can = re.search(r'<link\s+rel="canonical"\s+href="([^"]*)"', html_txt)
        assert m_can and m_can.group(1) == expected_canonical, f"{slug}: Bad canonical {m_can.group(1) if m_can else None}"

        # 5. JSON-LD valid (TechArticle + BreadcrumbList, no FAQPage/HowTo)
        m_json = re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', html_txt, flags=re.S)
        assert m_json, f"{slug}: Missing JSON-LD"
        jd = json.loads(m_json.group(1))
        types = [item.get("@type") for item in jd.get("@graph", [])]
        assert "TechArticle" in types and "BreadcrumbList" in types
        assert "FAQPage" not in types and "HowTo" not in types

        # 6. Breadcrumb present and working
        m_bc = re.search(r'<nav aria-label="Breadcrumb".*?</nav>', html_txt, flags=re.S)
        assert m_bc, f"{slug}: Missing Breadcrumb nav"
        bc_links = re.findall(r'href="([^"]+)"', m_bc.group(0))
        for bcl in bc_links:
            r_bc = client.get(bcl)
            assert r_bc.status_code == 200, f"{slug}: Broken breadcrumb link {bcl} ({r_bc.status_code})"

        # 7. Internal links check (no broken internal links)
        all_hrefs = re.findall(r'href="(/[^"#?]*)"', html_txt)
        for href in set(all_hrefs):
            r_link = client.get(href)
            assert r_link.status_code == 200, f"{slug}: Broken internal link {href} ({r_link.status_code})"

        # 8. Present in sitemap.xml
        assert expected_canonical in sitemap_locs, f"{slug}: Missing from sitemap.xml"

        # 9. No noindex
        assert "noindex" not in html_txt.lower(), f"{slug}: Found noindex!"
        assert 'name="keywords"' not in html_txt.lower(), f"{slug}: Found meta keywords!"

        report_rows.append(
            f"| `/{slug}` | {len(title_txt)} kr | {len(desc_txt)} kr | 1 adet | Geçerli | Tamamı 200 OK | Evet (`{sitemap_locs[expected_canonical]}`) | Yok (`index, follow`) |"
        )

    print("AŞAMA 7 DENETİM TABLOSU:")
    for row in report_rows:
        print(row)
    print(f"[PASS] 13/13 yeni hata kodu sayfası tüm 9 kriterden %100 başarıyla geçti!")


if __name__ == "__main__":
    run_stage7_audit()
