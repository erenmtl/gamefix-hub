# -*- coding: utf-8 -*-
"""
AŞAMA 5: Oyun Hub Sayfaları, İç Linkler, /hata-kodlari Dizini, Ana Sayfa Linkleri ve Sitemap Güncelleyici
"""
import os
import re

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

URL_REPLACEMENTS = {
    "/cs2/vac-oturum-dogrulama": "/cs2/vac-oturum-dogrulanamadi",
    "/cs2/packet-burst": "/cs2/packet-burst-fps-dusmesi",
    "/gtav-fivem/err-gfx-d3d-init": "/gta-v/err-gfx-d3d-init",
    "/gtav-fivem/fivem-texture-loss": "/fivem/harita-yuklenmiyor-texture-loss",
    "/bannerlord/d3d-device-context": "/bannerlord/d3d-device-context-map",
    "/fc25/ea-anticheat": "/fc-25/anticheat-hatasi",
    "/wukong/out-of-video-memory": "/black-myth-wukong/out-of-video-memory",
}


def replace_old_urls_in_text(text: str) -> str:
    # Sort by length descending so /bannerlord/d3d-device-context doesn't match /bannerlord/d3d-device-context-map
    for old_u, new_u in sorted(URL_REPLACEMENTS.items(), key=lambda x: -len(x[0])):
        pattern = re.escape(old_u) + r'(?=["\'#\s>])'
        text = re.sub(pattern, new_u, text)
    return text


def main():
    updated_files = 0

    # 1. Update all root .html files (hubs, hata-kodlari.html, index.html)
    for fname in sorted(os.listdir(ROOT_DIR)):
        if not fname.endswith(".html"):
            continue
        fpath = os.path.join(ROOT_DIR, fname)
        if not os.path.isfile(fpath):
            continue
        with open(fpath, "r", encoding="utf-8") as f:
            orig = f.read()
        updated = replace_old_urls_in_text(orig)
        if updated != orig:
            with open(fpath, "w", encoding="utf-8") as wf:
                wf.write(updated)
            updated_files += 1

    # 2. Update all nested <game>/<error>/index.html files so no internal link points to a redirected path
    excluded_dirs = {"static", "cozum", ".git", ".venv", "__pycache__", ".pytest_cache", "data"}
    for dname in sorted(os.listdir(ROOT_DIR)):
        if dname in excluded_dirs or dname.startswith("."):
            continue
        dpath = os.path.join(ROOT_DIR, dname)
        if not os.path.isdir(dpath):
            continue
        for subname in sorted(os.listdir(dpath)):
            sub_index = os.path.join(dpath, subname, "index.html")
            if not os.path.isfile(sub_index):
                continue
            with open(sub_index, "r", encoding="utf-8") as f:
                orig = f.read()
            updated = replace_old_urls_in_text(orig)
            if updated != orig:
                with open(sub_index, "w", encoding="utf-8") as wf:
                    wf.write(updated)
                updated_files += 1

    # 3. Update index.html footer "En Çok Aranan Hata Kodları" so each error code has its own clean link
    index_path = os.path.join(ROOT_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        idx_html = f.read()

    old_footer_block = """        <!-- Top Searched Error Codes (1-Click Search) -->
        <div class="md:col-span-4 space-y-2">
          <h2 class="text-xs font-bold uppercase tracking-wider text-gray-300">En Çok Aranan Hata Kodları</h2>
          <div class="flex flex-wrap gap-1.5 text-xs">
            <a href="/valorant/van-9003" class="px-2.5 py-1 rounded-lg bg-[#1d2430] hover:bg-[#263040] text-[#a3d9c6] border border-[#5e9c88]/25 transition">VAN 9003 / VAN 1067</a>
            <a href="/cs2/vac-oturum-dogrulanamadi" class="px-2.5 py-1 rounded-lg bg-[#1d2430] hover:bg-[#263040] text-[#a3d9c6] border border-[#5e9c88]/25 transition">CS2 VAC Doğrulama</a>
            <a href="/cs2/packet-burst-fps-dusmesi" class="px-2.5 py-1 rounded-lg bg-[#1d2430] hover:bg-[#263040] text-[#a3d9c6] border border-[#5e9c88]/25 transition">Packet Burst & Jitter</a>
            <a href="/lol/van-128" class="px-2.5 py-1 rounded-lg bg-[#1d2430] hover:bg-[#263040] text-[#a3d9c6] border border-[#5e9c88]/25 transition">LoL VAN 128 / 185</a>
            <a href="/minecraft/exit-code-1" class="px-2.5 py-1 rounded-lg bg-[#1d2430] hover:bg-[#263040] text-[#a3d9c6] border border-[#5e9c88]/25 transition">Exit Code 1 & GLFW</a>
            <a href="/gta-v/err-gfx-d3d-init" class="px-2.5 py-1 rounded-lg bg-[#1d2430] hover:bg-[#263040] text-[#a3d9c6] border border-[#5e9c88]/25 transition">ERR_GFX_STATE / D3D</a>
            <a href="/black-myth-wukong/out-of-video-memory" class="px-2.5 py-1 rounded-lg bg-[#1d2430] hover:bg-[#263040] text-[#a3d9c6] border border-[#5e9c88]/25 transition">Out of Video Memory</a>
            <a href="/bannerlord/d3d-device-context-map" class="px-2.5 py-1 rounded-lg bg-[#1d2430] hover:bg-[#263040] text-[#a3d9c6] border border-[#5e9c88]/25 transition">d3d_device_context</a>
          </div>
        </div>"""

    new_footer_block = """        <!-- Top Searched Error Codes (1-Click Dedicated Error Pages) -->
        <div class="md:col-span-4 space-y-2">
          <h2 class="text-xs font-bold uppercase tracking-wider text-gray-300">En Çok Aranan Hata Kodları</h2>
          <div class="flex flex-wrap gap-1.5 text-xs">
            <a href="/lol/van-185" class="px-2.5 py-1 rounded-lg bg-[#1d2430] hover:bg-[#263040] text-[#a3d9c6] border border-[#5e9c88]/25 transition">LoL VAN 185</a>
            <a href="/lol/van-128" class="px-2.5 py-1 rounded-lg bg-[#1d2430] hover:bg-[#263040] text-[#a3d9c6] border border-[#5e9c88]/25 transition">LoL VAN 128</a>
            <a href="/valorant/van-9003" class="px-2.5 py-1 rounded-lg bg-[#1d2430] hover:bg-[#263040] text-[#a3d9c6] border border-[#5e9c88]/25 transition">Valorant VAN 9003</a>
            <a href="/valorant/van-1067" class="px-2.5 py-1 rounded-lg bg-[#1d2430] hover:bg-[#263040] text-[#a3d9c6] border border-[#5e9c88]/25 transition">Valorant VAN 1067</a>
            <a href="/gta-v/err-gfx-d3d-init" class="px-2.5 py-1 rounded-lg bg-[#1d2430] hover:bg-[#263040] text-[#a3d9c6] border border-[#5e9c88]/25 transition">GTA 5 ERR_GFX_D3D_INIT</a>
            <a href="/fivem/harita-yuklenmiyor-texture-loss" class="px-2.5 py-1 rounded-lg bg-[#1d2430] hover:bg-[#263040] text-[#a3d9c6] border border-[#5e9c88]/25 transition">FiveM Texture Loss</a>
            <a href="/cs2/vac-oturum-dogrulanamadi" class="px-2.5 py-1 rounded-lg bg-[#1d2430] hover:bg-[#263040] text-[#a3d9c6] border border-[#5e9c88]/25 transition">CS2 VAC Doğrulanamadı</a>
            <a href="/cs2/packet-burst-fps-dusmesi" class="px-2.5 py-1 rounded-lg bg-[#1d2430] hover:bg-[#263040] text-[#a3d9c6] border border-[#5e9c88]/25 transition">CS2 Packet Burst</a>
            <a href="/rdr2/err-gfx-state" class="px-2.5 py-1 rounded-lg bg-[#1d2430] hover:bg-[#263040] text-[#a3d9c6] border border-[#5e9c88]/25 transition">RDR2 ERR_GFX_STATE</a>
            <a href="/bannerlord/d3d-device-context-map" class="px-2.5 py-1 rounded-lg bg-[#1d2430] hover:bg-[#263040] text-[#a3d9c6] border border-[#5e9c88]/25 transition">d3d_device_context_map</a>
            <a href="/fc-25/anticheat-hatasi" class="px-2.5 py-1 rounded-lg bg-[#1d2430] hover:bg-[#263040] text-[#a3d9c6] border border-[#5e9c88]/25 transition">FC 25 AntiCheat</a>
            <a href="/black-myth-wukong/out-of-video-memory" class="px-2.5 py-1 rounded-lg bg-[#1d2430] hover:bg-[#263040] text-[#a3d9c6] border border-[#5e9c88]/25 transition">Out of Video Memory</a>
            <a href="/minecraft/exit-code-1" class="px-2.5 py-1 rounded-lg bg-[#1d2430] hover:bg-[#263040] text-[#a3d9c6] border border-[#5e9c88]/25 transition">Minecraft Exit Code 1</a>
          </div>
        </div>"""

    if old_footer_block in idx_html:
        idx_html = idx_html.replace(old_footer_block, new_footer_block, 1)
        with open(index_path, "w", encoding="utf-8") as wf:
            wf.write(idx_html)

    print(f"[update_stage5_hubs_and_links] Updated internal links across {updated_files} files.")


if __name__ == "__main__":
    main()
