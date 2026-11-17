# -*- coding: utf-8 -*-
"""
AŞAMA 5: Mobil Öncelikli Düzen ve 5 Ekran Genişliğinde (360px, 390px, 768px, 1024px, 1440px) Headless Tarayıcı Testi
"""
import os
import time
import socket
import threading
import subprocess
import uvicorn
from fastapi.testclient import TestClient
import main

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOT_DIR = os.path.join(ROOT_DIR, "docs", "screenshots")
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.isfile(EDGE_PATH):
    EDGE_PATH = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

VIEWPORTS = [
    (360, 800),
    (390, 844),
    (768, 1024),
    (1024, 768),
    (1440, 900),
]


def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def capture_headless_screenshots():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    port = get_free_port()
    config = uvicorn.Config(main.app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    time.sleep(1.2)

    targets = [
        ("home", f"http://127.0.0.1:{port}/"),
        ("van185", f"http://127.0.0.1:{port}/lol/van-185"),
    ]

    import tempfile
    temp_profile = tempfile.mkdtemp(prefix="edge_headless_")
    captured = []
    for prefix, url in targets:
        for w, h in VIEWPORTS:
            out_png = os.path.join(SCREENSHOT_DIR, f"{prefix}-{w}px.png")
            cmd = [
                EDGE_PATH,
                "--headless",
                f"--user-data-dir={temp_profile}",
                "--disable-gpu",
                "--no-first-run",
                "--no-default-browser-check",
                "--hide-scrollbars",
                f"--window-size={w},{h}",
                f"--screenshot={out_png}",
                url,
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
            assert os.path.isfile(out_png) and os.path.getsize(out_png) > 1000, f"Screenshot failed: {out_png}"
            captured.append(out_png)
            print(f"  [SCREENSHOT OK] {os.path.basename(out_png)} ({w}x{h}px, {os.path.getsize(out_png)} bytes)")

    server.should_exit = True
    return captured


def verify_mobile_first_rules():
    with open(os.path.join(ROOT_DIR, "static", "styles.css"), "r", encoding="utf-8") as f:
        css = f.read()

    assert "overflow-x: hidden" in css
    assert "font-size: 16px !important" in css
    assert "min-height: 44px" in css
    assert "aspect-ratio: 16 / 9" in css

    with open(os.path.join(ROOT_DIR, "static", "app.js"), "r", encoding="utf-8") as f:
        app_js = f.read()

    # Verify WebGL hardware detection is NOT invoked inside DOMContentLoaded
    dom_loaded_idx = app_js.index("document.addEventListener('DOMContentLoaded'")
    dom_loaded_block = app_js[dom_loaded_idx : dom_loaded_idx + 1200]
    assert "triggerHardwareAutoDetect()" not in dom_loaded_block, "WebGL must only run when user clicks button!"

    c = TestClient(main.app)
    for route in ["/", "/lol/van-185", "/valorant/van-9003", "/hata-kodlari"]:
        r = c.get(route)
        assert r.status_code == 200
        assert 'name="viewport" content="width=device-width, initial-scale=1.0"' in r.text

    print("[PASS] AŞAMA 5 mobil öncelikli düzen kuralları, 5 çözünürlük ekran görüntüleri ve opt-in WebGL doğrulandı!")


if __name__ == "__main__":
    capture_headless_screenshots()
    verify_mobile_first_rules()
