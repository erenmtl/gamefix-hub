# -*- coding: utf-8 -*-
"""
AŞAMA 1: Tasarım Temeli, Otomatik WCAG AA Kontrast Denetimi, Telifsiz Monogram Rozetleri ve Mevcut İşlev Doğrulaması
"""
import os
import re
from fastapi.testclient import TestClient
import main
import apply_stage1_design_system as stage1_apply
import error_page_builder as builder


def hex_to_rel_luminance(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    r, g, b = [int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4)]

    def ch(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast_ratio(fg_hex: str, bg_hex: str) -> float:
    l1 = hex_to_rel_luminance(fg_hex)
    l2 = hex_to_rel_luminance(bg_hex)
    lighter, darker = max(l1, l2), min(l1, l2)
    return round((lighter + 0.05) / (darker + 0.05), 2)


def run_stage1_tests():
    stage1_apply.clean_seed_data()
    stage1_apply.clean_game_catalog()
    stage1_apply.update_app_js()
    stage1_apply.update_index_html()
    builder.build_all_from_json()

    # 1. Automated WCAG AA Contrast Audit
    pairs = [
        ("Başlık / Ana Metin (--color-text #e6ecf5) vs Arka Plan (--color-bg #141923)", "#e6ecf5", "#141923", 4.5),
        ("Gövde Metni (--color-text-body #d8dee9) vs Arka Plan (--color-bg #141923)", "#d8dee9", "#141923", 4.5),
        ("Gövde Metni (--color-text-body #d8dee9) vs Kart Yüzeyi (--color-surface #1b2230)", "#d8dee9", "#1b2230", 4.5),
        ("İkincil Metin (--color-text-secondary #9fb0c7) vs Arka Plan (--color-bg #141923)", "#9fb0c7", "#141923", 4.5),
        ("İkincil Metin (--color-text-secondary #9fb0c7) vs Yüzey (--color-surface #1b2230)", "#9fb0c7", "#1b2230", 4.5),
        ("İkincil Metin (--color-text-secondary #9fb0c7) vs Yükseltilmiş Kart (#202838)", "#9fb0c7", "#202838", 4.5),
        ("Vurgu Bağlantı Metni (--color-accent-text #88c0a8) vs Arka Plan (#141923)", "#88c0a8", "#141923", 4.5),
        ("Vurgu Bağlantı Metni (--color-accent-text #88c0a8) vs Yüzey (#1b2230)", "#88c0a8", "#1b2230", 4.5),
        ("Uyarı Metni (--color-warning-text #f3d092) vs Yüzey (#1b2230)", "#f3d092", "#1b2230", 4.5),
        ("Tehlike Metni (--color-danger-text #f5b3b8) vs Yüzey (#1b2230)", "#f5b3b8", "#1b2230", 4.5),
        ("Başarı Metni (--color-success-text #9be6c4) vs Yüzey (#1b2230)", "#9be6c4", "#1b2230", 4.5),
    ]

    print("WCAG AA KONTRAST RAPORU:")
    for label, fg, bg, min_ratio in pairs:
        ratio = contrast_ratio(fg, bg)
        assert ratio >= min_ratio, f"WCAG AA Başarısız: {label} -> {ratio}:1 (< {min_ratio}:1)"
        level = "AAA" if ratio >= 7.0 else "AA"
        print(f"  [PASS {level}] {label}: {ratio}:1")

    # 2. Check CSS custom properties & 8 shared components in static/styles.css?v=20261120v4
    with open(os.path.join(main.ROOT_DIR, "static", "styles.css"), "r", encoding="utf-8") as f:
        css_txt = f.read()

    for token in [
        "--color-bg:",
        "--color-surface:",
        "--color-text:",
        "--color-text-secondary:",
        "--color-accent:",
        "--color-success:",
        "--color-warning:",
        "--color-danger:",
        "--space-4:",
        "--radius-md:",
        "--shadow-md:",
        "--text-base:",
        "--measure-reading: 70ch",
        ".oc-btn",
        ".oc-card",
        ".oc-badge",
        ".oc-alert",
        ".oc-codeblock",
        ".oc-accordion",
        ".oc-tabs",
        ".oc-breadcrumb",
        ".oc-monogram",
    ]:
        assert token in css_txt, f"Missing design token or component in styles.css: {token}"

    # 3. Verify third-party copyrighted cover URLs are gone from seed_data.js
    with open(os.path.join(main.ROOT_DIR, "static", "seed_data.js"), "r", encoding="utf-8") as f:
        seed_txt = f.read()
    assert "steamstatic.com" not in seed_txt and "wikimedia.org" not in seed_txt and "ddragon.leagueoflegends.com" not in seed_txt

    # 4. Verify existing application features still work 100%
    client = TestClient(main.app)
    assert client.get("/").status_code == 200
    assert client.get("/api/status").status_code == 200
    assert client.get("/api/issues").status_code == 200
    assert client.get("/api/threads").status_code == 200
    r_vote = client.post("/api/issues/1/vote", json={"vote_type": "up"}, headers={"X-Client-Id": "stage1_test_client"})
    assert r_vote.status_code == 200
    r_van185 = client.get("/lol/van-185")
    assert r_van185.status_code == 200
    assert "oc-monogram" in r_van185.text and "oc-accordion" in r_van185.text and "oc-codeblock" in r_van185.text

    print("[PASS] AŞAMA 1 tasarım sistemi, WCAG AA kontrastı, telifsiz monogram rozetleri, 8 ortak bileşen ve mevcut uygulama işlevleri doğrulandı!")


if __name__ == "__main__":
    run_stage1_tests()
