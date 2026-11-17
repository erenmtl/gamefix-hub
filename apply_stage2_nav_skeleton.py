# -*- coding: utf-8 -*-
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def update_cookie_banner_in_app_js():
    app_path = os.path.join(ROOT_DIR, "static", "app.js")
    with open(app_path, "r", encoding="utf-8") as f:
        txt = f.read()

    old_str = 'max-w-5xl mx-auto bg-[#18202d]/95 backdrop-blur-md border border-[#88c0a8]/35 rounded-2xl p-4 sm:p-5 shadow-2xl'
    new_str = 'max-w-5xl mx-auto max-h-[22vh] overflow-y-auto bg-[#18202d]/95 backdrop-blur-md border border-[#88c0a8]/35 rounded-2xl p-3 sm:p-4 shadow-2xl'
    if old_str in txt:
        txt = txt.replace(old_str, new_str)
        with open(app_path, "w", encoding="utf-8") as wf:
            wf.write(txt)
        print("[OK] Updated cookieConsentBanner to max-h-[22vh] (< 25% mobile viewport height)")


def update_hata_kodlari_skip_link():
    hk_path = os.path.join(ROOT_DIR, "hata-kodlari.html")
    with open(hk_path, "r", encoding="utf-8") as f:
        txt = f.read()

    if "oc-skip-link" not in txt:
        txt = txt.replace(
            '<body class="min-h-screen flex flex-col bg-[#141923] text-gray-100">',
            '<body class="min-h-screen flex flex-col bg-[#141923] text-gray-100">\n  <a href="#ana-icerik" class="oc-skip-link">İçeriğe geç</a>',
        )
        txt = txt.replace(
            '<main class="max-w-6xl mx-auto px-4 py-8 space-y-6 flex-1 w-full">',
            '<main id="ana-icerik" class="max-w-6xl mx-auto px-4 py-8 space-y-6 flex-1 w-full">',
        )
        with open(hk_path, "w", encoding="utf-8") as wf:
            wf.write(txt)
        print("[OK] Added skip-to-content link and #ana-icerik to hata-kodlari.html")


if __name__ == "__main__":
    update_cookie_banner_in_app_js()
    update_hata_kodlari_skip_link()
