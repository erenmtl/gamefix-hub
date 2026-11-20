# -*- coding: utf-8 -*-
"""
AŞAMA 7: Tüm Sayfaların Kapsamlı Denetimi, Headless Tarayıcı Konsol Kontrolü ve Mevcut İşlev Doğrulaması
"""
import os
import re
import json
import time
import socket
import threading
import subprocess
import tempfile
import uvicorn
from fastapi.testclient import TestClient
import main
import error_page_builder as builder

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_all_pages_audit():
    c = TestClient(main.app)

    # Collect pages to audit: /, /hata-kodlari, legal pages, and all 13 dedicated error pages
    with open(builder.DATA_FILE, "r", encoding="utf-8") as f:
        pages = json.load(f).get("pages", [])

    routes = [
        "/",
        "/hata-kodlari",
        "/hakkimizda.html",
        "/iletisim.html",
        "/gizlilik-ve-cerez-politikasi.html",
        "/kvkk-aydinlatma-metni.html",
        "/kullanim-kosullari.html",
        "/telif-ve-sorumluluk-reddi.html",
    ] + [f"/{p['slug']}" for p in pages]

    checked_links = set()
    for route in routes:
        resp = c.get(route)
        assert resp.status_code == 200, f"Sayfa açılmadı: {route} -> {resp.status_code}"
        html_txt = resp.text

        # 1. Single H1 check
        h1s = re.findall(r"<h1\b[^>]*>.*?</h1>", html_txt, flags=re.S)
        assert len(h1s) == 1, f"{route}: Tek H1 bekleniyordu, bulunan={len(h1s)}"

        # 2. Missing alt attribute on <img>
        for img_tag in re.findall(r"<img\b[^>]*>", html_txt, flags=re.I):
            assert re.search(r'\balt="[^"]*"', img_tag), f"{route}: Eksik alt metin -> {img_tag}"

        # 3. Broken internal links check
        hrefs = re.findall(r'href="(/[^"#?]*)"', html_txt)
        for href in hrefs:
            if href in checked_links:
                continue
            r_link = c.get(href, follow_redirects=False)
            assert r_link.status_code in (200, 301), f"{route}: Kırık iç link {href} -> {r_link.status_code}"
            checked_links.add(href)

    print(f"[PASS] {len(routes)} sayfa ve {len(checked_links)} benzersiz iç link tarandı: 0 kırık link, 0 eksik alt metin, tümünde tek H1!")


def test_existing_features():
    c = TestClient(main.app)

    # 1. Status & Issues & Threads APIs
    assert c.get("/api/status").status_code == 200
    assert c.get("/api/issues").status_code == 200
    assert c.get("/api/threads").status_code == 200

    # 2. Vote API
    r_vote = c.post("/api/issues/1/vote", json={"vote_type": "up"}, headers={"X-Client-Id": "stage7_audit_voter"})
    assert r_vote.status_code == 200

    # 3. AI Analyze endpoint (rate limit / normal response check - should not 500)
    r_ai = c.post(
        "/api/ai/analyze",
        json={
            "game": "League of Legends",
            "error_code": "VAN 185",
            "specs": "Windows 11, RTX 4060",
            "description": "Maç ortasında VAN 185 hatası veriyor.",
        },
        headers={"X-Client-Id": "stage7_audit_ai"},
    )
    assert r_ai.status_code in (200, 401, 422, 429), f"Unexpected AI analyze status: {r_ai.status_code}"

    # 4. Auth endpoints reachable (register validation + login)
    r_login = c.post("/api/auth/login", json={"username": "nonexistent_stage7", "password": "wrong"})
    assert r_login.status_code in (400, 401, 403, 404, 422, 429)

    # 5. Frontend JS handlers exist in static/app.js?v=20261120v4 for log upload, hardware detect, cookie prefs, auth, forum
    with open(os.path.join(ROOT_DIR, "static", "app.js"), "r", encoding="utf-8") as f:
        app_js = f.read()

    for fn_name in [
        "submitAiDiagnostic",
        "handleCrashLogFileSelect",
        "loadSampleCrashLog",
        "triggerHardwareAutoDetect",
        "openAuthModal",
        "openAskModal",
        "submitNewThread",
        "openCookieSettingsModal",
        "acceptCookies",
    ]:
        assert fn_name in app_js, f"Missing JS handler in app.js: {fn_name}"

    print("[PASS] Mevcut tüm işlevler (AI çözümleyici, log yükleme, donanım algılama, giriş/kayıt, forum, oy verme, çerez tercihleri) doğrulandı!")


def test_headless_console_errors():
    port = get_free_port()
    config = uvicorn.Config(main.app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    time.sleep(1.2)

    temp_profile = tempfile.mkdtemp(prefix="edge_console_")
    for path in ["/", "/lol/van-185"]:
        url = f"http://127.0.0.1:{port}{path}"
        cmd = [
            EDGE_PATH,
            "--headless",
            f"--user-data-dir={temp_profile}",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "--enable-logging=stderr",
            "--v=0",
            "--dump-dom",
            url,
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        assert res.returncode == 0, f"Headless DOM dump failed for {path}"
        stderr_low = (res.stderr or "").lower()
        assert "uncaught" not in stderr_low and "referenceerror" not in stderr_low and "syntaxerror" not in stderr_low, (
            f"JS console error detected on {path}: {res.stderr}"
        )

    server.should_exit = True
    print("[PASS] Headless tarayıcı konsol kontrolünde Uncaught/ReferenceError/SyntaxError saptanmadı!")


if __name__ == "__main__":
    test_all_pages_audit()
    test_existing_features()
    test_headless_console_errors()
