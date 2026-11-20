# -*- coding: utf-8 -*-
"""
OyunÇöz Görsel Zenginleştirme (Visual Upgrade) ve "OÇ" Rozeti Kaldırma Betiği:
1. Sol üstteki ve yazar kutusundaki tüm "OÇ" metin rozetlerini tüm dosyalardan kaldırır; yerine özel tasarım parlak SVG Gamepad+Şimşek marka ikonu (oc-brand-icon) koyar.
2. static/styles.css?v=20261120v4 dosyasını soluk/mat görünümden çıkarıp derin gece mavisi (#0b0f17), radyal ortam ışığı (ambient mesh glow), teknik mikro-ızgara, parlak zümrüt-camgöbeği (#10b981 / #06b6d4) vurgular ve oyun rengi üst şeritli zengin kartlarla günceller (WCAG AA kontrastını koruyarak).
3. Ana sayfada (index.html) ve static/app.js?v=20261120v4 içinde:
   - updateHeroBanner() fonksiyonunun ana sayfa Hero alanını ezmesini engeller.
   - Hero bölümünü masaüstünde 2 sütunlu Görsel Teşhis & Arama Merkezi (sol: arama + popüler rozetler, sağ: 4 renkli SVG ikonlu Hata Kategorisi Bento kartı) haline getirir.
   - "En çok bakılan hatalar" bölümüne kategori filtre sekmeleri, her karta oyun renginde üst vurgu şeridi, SVG kategori ikonu, adım sayısı rozeti ve sistem etiketi ekler.
   - "Oyunlar" ızgarasını motor/koruma bilgili ve renkli glow efektli görsel kartlara dönüştürür.
   - "AI Çözümleyici" bölümünü masaüstünde 2 sütunlu (sol: AI form, sağ: Tek Tıkla Kopyalanabilir Hızlı Onarım Komutları & Crash Log Klasör Rehberi) Bento düzenine geçirir.
4. error_page_builder.py şablonuna 4'lü Görsel Teknik Özet Şeridi ve sağ yan panele Hızlı Teknik Kart ekleyip 14 hata kodu sayfasını yeniden üretir.
"""
import json
import os
import re

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Parlak, telifsiz özel SVG Marka İkonu ("OÇ" yazısı yerine)
BRAND_ICON_HTML = (
    '<span class="oc-brand-icon" aria-hidden="true">'
    '<svg class="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
    '<rect x="2" y="6" width="20" height="12" rx="4"/>'
    '<path d="M6 12h4"/><path d="M8 10v4"/>'
    '<circle cx="15" cy="11" r="1" fill="currentColor"/>'
    '<circle cx="17.5" cy="13" r="1" fill="currentColor"/>'
    '</svg>'
    '</span>'
)

AUTHOR_ICON_HTML = (
    '<span class="oc-brand-icon !w-9 !h-9" aria-hidden="true">'
    '<svg class="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>'
    '<path d="m9 12 2 2 4-4"/>'
    '</svg>'
    '</span>'
)

GAME_VISUAL_META = {
    "GTA 6": {"code": "GTA6", "color": "#ec4899", "bg": "linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%)", "cat": "DirectX 12 & VRAM", "cat_key": "dx12", "engine": "RAGE 9 • DX12"},
    "League of Legends": {"code": "LOL", "color": "#3b82f6", "bg": "linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%)", "cat": "Vanguard Anti-Cheat", "cat_key": "anticheat", "engine": "Riot Engine • Vanguard"},
    "Valorant": {"code": "VAL", "color": "#f43f5e", "bg": "linear-gradient(135deg, #f43f5e 0%, #fb7185 100%)", "cat": "BIOS & TPM 2.0", "cat_key": "anticheat", "engine": "UE4 • Vanguard"},
    "VALORANT": {"code": "VAL", "color": "#f43f5e", "bg": "linear-gradient(135deg, #f43f5e 0%, #fb7185 100%)", "cat": "BIOS & TPM 2.0", "cat_key": "anticheat", "engine": "UE4 • Vanguard"},
    "Counter-Strike 2": {"code": "CS2", "color": "#f59e0b", "bg": "linear-gradient(135deg, #f59e0b 0%, #ea580c 100%)", "cat": "VAC & Ağ / FPS", "cat_key": "fps", "engine": "Source 2 • VAC"},
    "GTA V": {"code": "GTA", "color": "#10b981", "bg": "linear-gradient(135deg, #10b981 0%, #059669 100%)", "cat": "DirectX & GPU", "cat_key": "dx12", "engine": "RAGE • DirectX 11"},
    "FiveM": {"code": "5M", "color": "#f97316", "bg": "linear-gradient(135deg, #f97316 0%, #ef4444 100%)", "cat": "VRAM & Doku", "cat_key": "fps", "engine": "Cfx.re • RAGE"},
    "Red Dead Redemption 2": {"code": "RDR2", "color": "#ef4444", "bg": "linear-gradient(135deg, #ef4444 0%, #b91c1c 100%)", "cat": "Vulkan & DX12", "cat_key": "dx12", "engine": "RAGE • Vulkan/DX12"},
    "Minecraft": {"code": "MC", "color": "#22c55e", "bg": "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)", "cat": "Java & OpenGL", "cat_key": "dx12", "engine": "LWJGL 3 • Java 21"},
    "EA Sports FC 25": {"code": "FC25", "color": "#06b6d4", "bg": "linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)", "cat": "EA AntiCheat", "cat_key": "anticheat", "engine": "Frostbite • EAAntiCheat"},
    "Mount & Blade II: Bannerlord": {"code": "MB2", "color": "#eab308", "bg": "linear-gradient(135deg, #eab308 0%, #ca8a04 100%)", "cat": "D3D & Shader", "cat_key": "dx12", "engine": "TaleWorlds Engine"},
    "Black Myth: Wukong": {"code": "BMW", "color": "#a855f7", "bg": "linear-gradient(135deg, #a855f7 0%, #6366f1 100%)", "cat": "UE5 & VRAM", "cat_key": "fps", "engine": "Unreal Engine 5"},
}


def update_styles_css():
    css_path = os.path.join(ROOT_DIR, "static", "styles.css")
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    # Upgrade the color tokens in :root while preserving every single variable name (--color-*, --space-*, --radius-*, --shadow-*, --font-*, --text-*, --line-height-*, --measure-*)
    replacements = [
        ("--color-bg: #141923;", "--color-bg: #0b101b;"),
        ("--color-surface: #1b2230;", "--color-surface: #131c2e;"),
        ("--color-surface-elevated: #202838;", "--color-surface-elevated: #19253c;"),
        ("--color-surface-hover: #263144;", "--color-surface-hover: #21304d;"),
        ("--color-text: #e6ecf5;", "--color-text: #f1f5f9;"),
        ("--color-text-body: #d8dee9;", "--color-text-body: #e2e8f0;"),
        ("--color-text-secondary: #9fb0c7;", "--color-text-secondary: #a8b8d0;"),
        ("--color-accent: #5e9c88;", "--color-accent: #10b981;"),
        ("--color-accent-hover: #4e8775;", "--color-accent-hover: #059669;"),
        ("--color-accent-text: #88c0a8;", "--color-accent-text: #34d399;"),
        ("--color-accent-subtle: rgba(94, 156, 136, 0.14);", "--color-accent-subtle: rgba(16, 185, 129, 0.16);"),
    ]
    for old_v, new_v in replacements:
        css = css.replace(old_v, new_v)

    # Append vibrant visual helpers if not already added
    visual_css_addition = """
/* ─── GÖRSEL ZENGİNLEŞTİRME: ORTAM IŞIĞI, MİKRO-IZGARA VE MARKA İKONU ─── */
body {
  background-color: var(--color-bg) !important;
  background-image:
    radial-gradient(at 15% 0%, rgba(16, 185, 129, 0.14) 0px, transparent 45%),
    radial-gradient(at 85% 5%, rgba(6, 182, 212, 0.13) 0px, transparent 45%),
    radial-gradient(at 50% 45%, rgba(99, 102, 241, 0.07) 0px, transparent 55%),
    linear-gradient(rgba(255, 255, 255, 0.022) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.022) 1px, transparent 1px) !important;
  background-size: 100% 100%, 100% 100%, 100% 100%, 36px 36px, 36px 36px !important;
  background-attachment: fixed !important;
}

.oc-brand-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.85rem;
  background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%);
  box-shadow: 0 4px 16px rgba(16, 185, 129, 0.38), inset 0 1px 1px rgba(255, 255, 255, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.22);
  flex-shrink: 0;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

a:hover .oc-brand-icon {
  transform: translateY(-1px) scale(1.03);
  box-shadow: 0 6px 22px rgba(6, 182, 212, 0.5), inset 0 1px 1px rgba(255, 255, 255, 0.45);
}

.oc-card {
  background: linear-gradient(180deg, rgba(25, 37, 60, 0.92) 0%, rgba(19, 28, 46, 0.96) 100%) !important;
  border: 1px solid rgba(148, 163, 184, 0.18) !important;
  box-shadow: 0 10px 30px -6px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
}

.oc-card-interactive {
  position: relative;
  overflow: hidden;
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease !important;
}

.oc-card-interactive:hover {
  transform: translateY(-3px);
  border-color: rgba(52, 211, 153, 0.55) !important;
  box-shadow: 0 18px 38px -10px rgba(0, 0, 0, 0.65), 0 0 24px rgba(16, 185, 129, 0.16) !important;
}

.oc-hero-glow {
  position: relative;
  overflow: hidden;
  background:
    radial-gradient(800px circle at 15% 20%, rgba(16, 185, 129, 0.18), transparent 45%),
    radial-gradient(700px circle at 88% 80%, rgba(6, 182, 212, 0.16), transparent 45%),
    linear-gradient(180deg, rgba(25, 37, 60, 0.95) 0%, rgba(17, 25, 42, 0.98) 100%) !important;
  border: 1px solid rgba(52, 211, 153, 0.32) !important;
}

.oc-gradient-text {
  background: linear-gradient(90deg, #34d399 0%, #38bdf8 55%, #a78bfa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.oc-btn-primary {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
  color: #ffffff !important;
  border: 1px solid rgba(52, 211, 153, 0.45) !important;
  box-shadow: 0 4px 16px rgba(16, 185, 129, 0.30) !important;
}

.oc-btn-primary:hover {
  background: linear-gradient(135deg, #34d399 0%, #10b981 100%) !important;
  box-shadow: 0 6px 22px rgba(16, 185, 129, 0.45) !important;
}

.oc-monogram {
  color: #ffffff !important;
  font-weight: 800 !important;
  letter-spacing: -0.03em;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.25);
}

.oc-cat-bento {
  position: relative;
  overflow: hidden;
  border-radius: 1rem;
  padding: 1rem;
  background: rgba(15, 23, 38, 0.78);
  border: 1px solid rgba(148, 163, 184, 0.18);
  transition: all 0.2s ease;
}

.oc-cat-bento:hover {
  transform: translateY(-2px);
  background: rgba(23, 35, 58, 0.92);
}
"""
    if "/* ─── GÖRSEL ZENGİNLEŞTİRME:" not in css:
        css += "\n" + visual_css_addition

    with open(css_path, "w", encoding="utf-8") as f:
        f.write(css)
    print("[OK] Updated static/styles.css?v=20261120v4 with vibrant dark theme, ambient mesh glow, and brand icon styles")


def build_enriched_top8_cards_html(pages):
    sorted_pages = sorted(pages, key=lambda x: x.get("oncelik", 99))[:8]
    cards = []
    for p in sorted_pages:
        slug = p["slug"]
        oyun = p["oyun"]
        kod = p["hata_kodu"]
        kod_badge = kod.split("/")[0].strip()
        meta = GAME_VISUAL_META.get(oyun, {"code": oyun[:3].upper(), "color": "#10b981", "bg": "linear-gradient(135deg, #10b981, #06b6d4)", "cat": "Teknik Çözüm", "cat_key": "dx12", "engine": "PC"})
        steps_count = len(p.get("cozum_adimlari", [])) or 4
        raw_desc = p["kisa_aciklama"].split(".")[0].strip() + "."
        if len(raw_desc) > 115:
            raw_desc = raw_desc[:112].rsplit(" ", 1)[0] + "…"
        url = f"/{slug}"
        cards.append(f"""          <article data-error-cat="{meta['cat_key']}" class="oc-card oc-card-interactive pt-0 px-5 pb-5 flex flex-col justify-between gap-3.5 group">
            <div>
              <!-- Oyun Rengi Üst Görsel Vurgu Şeridi -->
              <div class="h-1.5 -mx-5 mb-4 rounded-t-xl" style="background: {meta['bg']};"></div>
              <div class="flex items-center justify-between gap-2 mb-3">
                <div class="flex items-center gap-2.5 min-w-0">
                  <span class="oc-monogram" style="background: {meta['bg']}; border-color: rgba(255,255,255,0.28);" aria-hidden="true">{meta['code']}</span>
                  <div class="min-w-0">
                    <span class="block text-xs font-extrabold text-white truncate">{oyun}</span>
                    <span class="block text-[11px] text-gray-400 truncate">{meta['engine']}</span>
                  </div>
                </div>
                <span class="px-2.5 py-1 rounded-lg text-xs font-mono font-extrabold border shrink-0" style="background-color: {meta['color']}22; border-color: {meta['color']}66; color: #f8fafc;">{kod_badge}</span>
              </div>
              <p class="text-xs sm:text-sm text-gray-200 leading-relaxed">{raw_desc}</p>
            </div>
            <div class="pt-3 border-t border-white/10 flex items-center justify-between gap-2 text-xs">
              <div class="flex items-center gap-1.5">
                <span class="px-2 py-0.5 rounded-md bg-white/5 border border-white/10 text-[11px] font-semibold text-gray-300">{steps_count} Adım</span>
                <span class="px-2 py-0.5 rounded-md bg-[#10b981]/15 border border-[#10b981]/30 text-[11px] font-semibold text-[#34d399]">{meta['cat']}</span>
              </div>
              <a href="{url}" class="font-extrabold text-[#34d399] group-hover:text-white transition inline-flex items-center gap-1">
                <span>Çözümü gör</span>
                <svg class="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
              </a>
            </div>
          </article>""")
    return "\n".join(cards)


def build_initial_games_showcase_html():
    featured = [
        ("gta-6", "GTA 6", "GTA6", "#ec4899", "linear-gradient(135deg, #ec4899, #8b5cf6)", "RAGE 9 • DX12", "2 Hata Kodu", "/gta-6-hata-cozumleri.html"),
        ("valorant", "VALORANT", "VAL", "#f43f5e", "linear-gradient(135deg, #f43f5e, #e11d48)", "UE4 • Vanguard", "4 Hata Kodu", "/valorant-hata-cozumleri.html"),
        ("cs2", "Counter-Strike 2", "CS2", "#f59e0b", "linear-gradient(135deg, #f59e0b, #d97706)", "Source 2 • VAC", "4 Hata Kodu", "/cs2-hata-cozumleri.html"),
        ("lol", "League of Legends", "LOL", "#3b82f6", "linear-gradient(135deg, #3b82f6, #0284c7)", "Riot • Vanguard", "3 Hata Kodu", "/lol-hata-cozumleri.html"),
        ("gtav-fivem", "GTA V & FiveM", "GTA", "#10b981", "linear-gradient(135deg, #10b981, #059669)", "RAGE • Cfx.re", "3 Hata Kodu", "/gtav-fivem-hata-cozumleri.html"),
        ("fc25", "EA Sports FC 25", "FC25", "#06b6d4", "linear-gradient(135deg, #06b6d4, #2563eb)", "Frostbite • EAAntiCheat", "2 Hata Kodu", "/fc25-hata-cozumleri.html"),
        ("minecraft", "Minecraft", "MC", "#22c55e", "linear-gradient(135deg, #22c55e, #15803d)", "Java 21 • OpenGL", "2 Hata Kodu", "/minecraft-hata-cozumleri.html"),
        ("red-dead-redemption-2", "Red Dead Redemption 2", "RDR2", "#ef4444", "linear-gradient(135deg, #ef4444, #b91c1c)", "RAGE • Vulkan/DX12", "2 Hata Kodu", "/red-dead-redemption-2-hata-cozumleri.html"),
        ("cod-warzone", "CoD: Warzone & BO6", "COD", "#f97316", "linear-gradient(135deg, #f97316, #c2410c)", "IW 9.0 • RICOCHET", "2 Hata Kodu", "/cod-warzone-hata-cozumleri.html"),
        ("cyberpunk-2077", "Cyberpunk 2077", "CP77", "#eab308", "linear-gradient(135deg, #eab308, #a16207)", "REDengine 4 • DX12", "2 Hata Kodu", "/cyberpunk-2077-hata-cozumleri.html"),
        ("black-myth-wukong", "Black Myth: Wukong", "BMW", "#a855f7", "linear-gradient(135deg, #a855f7, #6d28d9)", "Unreal Engine 5", "2 Hata Kodu", "/black-myth-wukong-hata-cozumleri.html"),
        ("mount-and-blade-2-bannerlord", "M&B II: Bannerlord", "MB2", "#d97706", "linear-gradient(135deg, #d97706, #92400e)", "TaleWorlds • D3D11", "2 Hata Kodu", "/mount-and-blade-2-bannerlord-hata-cozumleri.html"),
    ]
    items = []
    for slug, name, code, color, grad, engine, count_txt, href in featured:
        items.append(f"""          <a
            href="{href}"
            onclick="event.preventDefault(); selectGame('{slug}'); switchTab('issues'); document.getElementById('tabContent-issues')?.scrollIntoView({{behavior:'smooth'}});"
            class="oc-card oc-card-interactive p-4 flex items-center justify-between gap-3 group"
            style="border-left: 3px solid {color} !important;"
          >
            <div class="flex items-center gap-3 min-w-0">
              <span class="oc-monogram" style="background: {grad}; border-color: rgba(255,255,255,0.28);" aria-hidden="true">{code}</span>
              <div class="min-w-0">
                <div class="text-xs sm:text-sm font-extrabold text-white group-hover:text-[#34d399] transition truncate">{name}</div>
                <div class="text-[11px] text-gray-400 truncate">{engine}</div>
              </div>
            </div>
            <span class="px-2.5 py-1 rounded-lg bg-white/5 border border-white/10 text-[11px] font-bold text-gray-200 shrink-0">{count_txt}</span>
          </a>""")
    return "\n".join(items)


def update_index_html(pages):
    index_path = os.path.join(ROOT_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        txt = f.read()

    # 1. Remove "OÇ" in top-left header logo
    txt = txt.replace('<span class="oc-monogram" aria-hidden="true">OÇ</span>', BRAND_ICON_HTML)

    # 2. Replace <main id="ana-icerik"...> with enriched visual layout
    top8_html = build_enriched_top8_cards_html(pages)
    games_grid_html = build_initial_games_showcase_html()

    start_marker = '    <main id="ana-icerik"'
    end_marker = '    </main>'
    idx_s = txt.index(start_marker)
    idx_e = txt.index(end_marker, idx_s) + len(end_marker)

    new_main = f"""    <main id="ana-icerik" class="space-y-10 w-full">

      <!-- 1. ÜST BÖLÜM (SPLIT-HERO): BÜYÜK ARAMA KUTUSU + GÖRSEL HATA TEŞHİS BENTO KARTLARI -->
      <section id="gameHeroBanner" class="oc-card oc-hero-glow p-6 sm:p-8 lg:p-10">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">

          <!-- Sol Sütun (7/12): Başlık, Büyük Arama Kutusu ve Hızlı Hata Kodu Seçimi -->
          <div class="lg:col-span-7 space-y-5 text-left">
            <div class="inline-flex flex-wrap items-center gap-2">
              <span id="heroCategoryBadge" class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-extrabold bg-[#10b981]/20 text-[#34d399] border border-[#10b981]/40">
                <span class="w-2 h-2 rounded-full bg-[#34d399] animate-pulse"></span>
                <span>CANLI OYUN ARIZA &amp; FPS ÇÖZÜM MERKEZİ</span>
              </span>
              <span id="heroEngineBadge" class="hidden oc-badge"></span>
              <span id="heroAnticheatBadge" class="hidden oc-badge"></span>
            </div>

            <h1 id="heroGameTitle" class="text-2xl sm:text-4xl lg:text-[40px] font-extrabold text-white tracking-tight leading-tight">
              Hangi hatayı alıyorsun?
            </h1>

            <p id="heroGameSubtitle" class="text-sm sm:text-base text-gray-200 leading-relaxed max-w-2xl">
              Aldığın hata kodunu (<code class="text-[#34d399] font-mono font-bold">VAN 185</code>, <code class="text-[#38bdf8] font-mono font-bold">ERR_GFX_STATE</code>, <code class="text-[#f43f5e] font-mono font-bold">VAN 9003</code>) veya oyun adını yaz; doğrudan test edilmiş adım adım çözüm sayfasına git.
            </p>
            <div id="heroGameCoverWrapper" class="hidden"><img id="heroGameCoverImg" src="./static/logo.svg" alt="OyunÇöz Rozeti" /></div>

            <!-- Büyük Parlak Arama Kutusu -->
            <div class="relative" id="desktopSearchWrapper">
              <form onsubmit="handleHeroSearchSubmit(event)" class="relative">
                <label for="globalSearchInput" class="sr-only">Hata kodu veya oyun ara</label>
                <input
                  id="globalSearchInput"
                  type="search"
                  autocomplete="off"
                  placeholder="VAN 185, ERR_GFX_STATE, Exit Code 1…"
                  class="w-full bg-[#0b101b]/95 text-base sm:text-lg text-white placeholder-gray-400 rounded-2xl pl-12 pr-32 py-4 border-2 border-[#10b981]/45 focus:outline-none focus:border-[#34d399] shadow-2xl transition"
                  onfocus="openLiveAutocomplete(this.value)"
                  oninput="handleLiveSearchInput(this.value)"
                  onkeydown="handleSearchKeydown(event)"
                />
                <svg class="w-5 h-5 text-[#34d399] absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true">
                  <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
                </svg>
                <div class="absolute right-2.5 top-1/2 -translate-y-1/2 flex items-center gap-1.5">
                  <button
                    type="button"
                    onclick="clearGlobalSearch()"
                    id="clearSearchBtn"
                    class="hidden px-2.5 py-1.5 rounded-lg bg-white/10 text-xs text-gray-300 hover:text-white"
                  >
                    Temizle
                  </button>
                  <button
                    type="submit"
                    class="oc-btn oc-btn-primary !min-h-[42px] !py-2 !px-5 text-xs sm:text-sm font-extrabold"
                  >
                    Çözümü Bul
                  </button>
                </div>
              </form>

              <!-- Anlık Otomatik Tamamlama Açılır Listesi -->
              <div
                id="liveSearchDropdown"
                class="hidden absolute left-0 right-0 top-full mt-2 bg-[#131c2e] border-2 border-[#10b981]/50 rounded-2xl shadow-2xl z-50 max-h-[420px] overflow-y-auto divide-y divide-white/10"
                role="listbox"
                aria-label="Hata kodu ve oyun önerileri"
              ></div>
            </div>

            <!-- Hızlı Hata Kodu Rozetleri -->
            <div id="heroCommonTags" class="flex flex-wrap items-center gap-2 text-xs pt-1">
              <span class="text-gray-300 font-bold">Popüler Aramalar:</span>
              <a href="/gta-6/err-gfx-state-cokme-hatasi" class="px-3 py-1.5 rounded-xl font-bold bg-gradient-to-r from-[#ec4899]/25 to-[#8b5cf6]/25 text-white border border-[#ec4899]/50 hover:border-[#ec4899] transition">GTA 6 ERR_GFX_STATE</a>
              <a href="/lol/van-185" class="px-3 py-1.5 rounded-xl font-mono font-bold bg-[#3b82f6]/20 text-white border border-[#3b82f6]/45 hover:border-[#60a5fa] transition">VAN 185</a>
              <a href="/valorant/van-9003" class="px-3 py-1.5 rounded-xl font-mono font-bold bg-[#f43f5e]/20 text-white border border-[#f43f5e]/45 hover:border-[#fb7185] transition">VAN 9003</a>
              <a href="/gta-v/err-gfx-d3d-init" class="px-3 py-1.5 rounded-xl font-mono font-bold bg-[#10b981]/20 text-white border border-[#10b981]/45 hover:border-[#34d399] transition">ERR_GFX_D3D_INIT</a>
              <a href="/cs2/vac-oturum-dogrulanamadi" class="px-3 py-1.5 rounded-xl font-mono font-bold bg-[#f59e0b]/20 text-white border border-[#f59e0b]/45 hover:border-[#fbbf24] transition">CS2 VAC</a>
              <a href="/minecraft/exit-code-1" class="px-3 py-1.5 rounded-xl font-mono font-bold bg-[#22c55e]/20 text-white border border-[#22c55e]/45 hover:border-[#4ade80] transition">Exit Code 1</a>
            </div>
          </div>

          <!-- Sağ Sütun (5/12): Görsel Hata Türü Teşhis Bento Izgarası (2x2) -->
          <div class="lg:col-span-5 grid grid-cols-1 sm:grid-cols-2 gap-3.5">
            <!-- Kategori 1: Anti-Cheat & BIOS -->
            <a href="/valorant/van-9003" class="oc-cat-bento group" style="border-top: 3px solid #f43f5e;">
              <div class="flex items-center justify-between mb-2.5">
                <span class="w-10 h-10 rounded-xl flex items-center justify-center bg-[#f43f5e]/20 border border-[#f43f5e]/40 text-[#fb7185]">
                  <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>
                </span>
                <span class="text-[11px] font-mono font-bold px-2 py-0.5 rounded bg-[#f43f5e]/15 text-[#fb7185]">BIOS / Kernel</span>
              </div>
              <div class="text-sm font-extrabold text-white group-hover:text-[#fb7185] transition">Anti-Cheat &amp; TPM 2.0</div>
              <p class="text-xs text-gray-300 mt-1 leading-snug">Vanguard VAN 9003, VAN 1067, VAN 185, BattlEye ve EA AntiCheat</p>
            </a>

            <!-- Kategori 2: DirectX 12 & GPU Çökmesi -->
            <a href="/gta-6/err-gfx-state-cokme-hatasi" class="oc-cat-bento group" style="border-top: 3px solid #06b6d4;">
              <div class="flex items-center justify-between mb-2.5">
                <span class="w-10 h-10 rounded-xl flex items-center justify-center bg-[#06b6d4]/20 border border-[#06b6d4]/40 text-[#38bdf8]">
                  <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v3"/><path d="M15 1v3"/><path d="M9 20v3"/><path d="M15 20v3"/><path d="M20 9h3"/><path d="M20 14h3"/><path d="M1 9h3"/><path d="M1 14h3"/></svg>
                </span>
                <span class="text-[11px] font-mono font-bold px-2 py-0.5 rounded bg-[#06b6d4]/15 text-[#38bdf8]">DX12 / Vulkan</span>
              </div>
              <div class="text-sm font-extrabold text-white group-hover:text-[#38bdf8] transition">Ekran Kartı &amp; DX12</div>
              <p class="text-xs text-gray-300 mt-1 leading-snug">ERR_GFX_STATE, D3D_INIT, Shader Cache ve sürücü çökmesi</p>
            </a>

            <!-- Kategori 3: FPS Düşmesi & VRAM -->
            <a href="/black-myth-wukong/out-of-video-memory" class="oc-cat-bento group" style="border-top: 3px solid #f59e0b;">
              <div class="flex items-center justify-between mb-2.5">
                <span class="w-10 h-10 rounded-xl flex items-center justify-center bg-[#f59e0b]/20 border border-[#f59e0b]/40 text-[#fbbf24]">
                  <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/></svg>
                </span>
                <span class="text-[11px] font-mono font-bold px-2 py-0.5 rounded bg-[#f59e0b]/15 text-[#fbbf24]">VRAM / %1 FPS</span>
              </div>
              <div class="text-sm font-extrabold text-white group-hover:text-[#fbbf24] transition">FPS Düşmesi &amp; VRAM</div>
              <p class="text-xs text-gray-300 mt-1 leading-snug">Out of Video Memory, FiveM Texture Loss ve anlık takılma</p>
            </a>

            <!-- Kategori 4: Ağ, Ping & Paket Kaybı -->
            <a href="/cs2/packet-burst-fps-dusmesi" class="oc-cat-bento group" style="border-top: 3px solid #10b981;">
              <div class="flex items-center justify-between mb-2.5">
                <span class="w-10 h-10 rounded-xl flex items-center justify-center bg-[#10b981]/20 border border-[#10b981]/40 text-[#34d399]">
                  <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><line x1="12" y1="20" x2="12.01" y2="20"/></svg>
                </span>
                <span class="text-[11px] font-mono font-bold px-2 py-0.5 rounded bg-[#10b981]/15 text-[#34d399]">UDP / Winsock</span>
              </div>
              <div class="text-sm font-extrabold text-white group-hover:text-[#34d399] transition">Paket Kaybı &amp; Ping</div>
              <p class="text-xs text-gray-300 mt-1 leading-snug">CS2 Packet Burst, VAL 62, oturum doğrulama ve DNS sıfırlama</p>
            </a>
          </div>
        </div>

        <!-- Enter Arama Sonuçları Kutusu (Varsayılan Gizli, Enter'a Basınca Açılır) -->
        <div id="heroInlineSearchResults" class="hidden max-w-4xl mx-auto pt-6 mt-6 border-t border-white/10 space-y-3 text-left"></div>
      </section>

      <!-- 2. EN ÇOK BAKILAN HATALAR (Görsel Kartlar & Hızlı Kategori Filtresi) -->
      <section aria-labelledby="topErrorsHeading" class="space-y-4">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div>
            <div class="inline-flex items-center gap-2 text-xs font-extrabold uppercase tracking-wider text-[#34d399] mb-1">
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M12 2v20"/><path d="m17 5-5-3-5 3"/><path d="m17 19-5 3-5-3"/></svg>
              <span>Doğrulanmış Hata Kodu Rehberleri</span>
            </div>
            <h2 id="topErrorsHeading" class="text-xl sm:text-2xl font-extrabold text-white">En çok bakılan hatalar</h2>
          </div>

          <!-- Hızlı Kategori Filtre Sekmeleri -->
          <div class="flex flex-wrap items-center gap-1.5" role="tablist" aria-label="Hata kategorisi filtresi">
            <button type="button" onclick="filterHomeTopErrors('all', this)" class="home-err-filter-btn px-3 py-1.5 rounded-xl text-xs font-extrabold bg-[#10b981] text-white border border-[#34d399]/50 transition">Tümü (8)</button>
            <button type="button" onclick="filterHomeTopErrors('dx12', this)" class="home-err-filter-btn px-3 py-1.5 rounded-xl text-xs font-bold bg-white/5 text-gray-300 hover:text-white border border-white/10 transition">DirectX 12 &amp; GPU</button>
            <button type="button" onclick="filterHomeTopErrors('anticheat', this)" class="home-err-filter-btn px-3 py-1.5 rounded-xl text-xs font-bold bg-white/5 text-gray-300 hover:text-white border border-white/10 transition">Vanguard &amp; Anti-Cheat</button>
            <button type="button" onclick="filterHomeTopErrors('fps', this)" class="home-err-filter-btn px-3 py-1.5 rounded-xl text-xs font-bold bg-white/5 text-gray-300 hover:text-white border border-white/10 transition">FPS &amp; VRAM</button>
            <a href="/hata-kodlari" class="px-3 py-1.5 rounded-xl text-xs font-extrabold text-[#34d399] hover:underline">Tümünü gör →</a>
          </div>
        </div>

        <div id="homeTopErrorsGrid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
{top8_html}
        </div>
      </section>

      <!-- 3. OYUNLAR IZGARASI (Renkli Monogram + Motor Bilgisi + Hata Kodu Sayısı) -->
      <section aria-labelledby="gamesGridHeading" class="space-y-4">
        <div class="flex flex-col sm:flex-row sm:items-end justify-between gap-2">
          <div>
            <div class="inline-flex items-center gap-2 text-xs font-extrabold uppercase tracking-wider text-[#38bdf8] mb-1">
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><rect x="2" y="6" width="20" height="12" rx="3"/><path d="M6 12h4"/><path d="M8 10v4"/><circle cx="16" cy="11" r="1"/></svg>
              <span>Oyun Bazlı Arıza &amp; Performans Kütüphanesi</span>
            </div>
            <h2 id="gamesGridHeading" class="text-xl sm:text-2xl font-extrabold text-white">Oyunlar</h2>
          </div>
          <button
            type="button"
            onclick="toggleGamesNavPanel(true)"
            class="oc-btn oc-btn-secondary text-xs font-extrabold self-start sm:self-auto"
          >
            <span>Tüm Oyunları ve Arama Panelini Aç (31 Oyun)</span>
          </button>
        </div>
        <div id="homeGamesShowcaseGrid" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3.5">
{games_grid_html}
        </div>
      </section>

      <!-- Sekme Geçiş Çubuğu (Hata Rehberleri / AI Çözümleyici / Forum) -->
      <div class="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 pb-3">
        <div class="flex items-center gap-2 overflow-x-auto">
          <button
            onclick="switchTab('ai-lab')"
            id="tabBtn-ai-lab"
            class="tab-btn active-tab px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold flex items-center gap-2 whitespace-nowrap"
          >
            <span>AI Arıza Çözümleyici</span>
          </button>
          <button
            onclick="switchTab('issues')"
            id="tabBtn-issues"
            class="tab-btn px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold flex items-center gap-2 whitespace-nowrap"
          >
            <span>Seçili Oyun Rehberleri</span>
            <span id="tabCountIssues" class="px-2 py-0.5 rounded-full bg-white/10 text-xs">0</span>
          </button>
          <button
            onclick="switchTab('forum')"
            id="tabBtn-forum"
            class="tab-btn px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold flex items-center gap-2 whitespace-nowrap"
          >
            <span>Topluluk Forumu</span>
            <span id="tabCountForum" class="hidden px-2 py-0.5 rounded-full bg-white/10 text-xs"></span>
          </button>
        </div>

        <!-- Kategori Filtresi (Seçili Oyun Rehberleri görünümü için) -->
        <div class="flex items-center gap-1.5 overflow-x-auto text-xs" id="categoryPills">
          <button onclick="setCategory('all')" data-cat="all" class="cat-pill active-pill px-3 py-1.5 rounded-lg font-medium whitespace-nowrap">Tümü</button>
          <button onclick="setCategory('Anti-Cheat & Güvenlik')" data-cat="Anti-Cheat & Güvenlik" class="cat-pill px-3 py-1.5 rounded-lg font-medium whitespace-nowrap">Anti-Cheat</button>
          <button onclick="setCategory('Performans & FPS')" data-cat="Performans & FPS" class="cat-pill px-3 py-1.5 rounded-lg font-medium whitespace-nowrap">FPS &amp; Stutter</button>
          <button onclick="setCategory('Çökme & Başlatma')" data-cat="Çökme & Başlatma" class="cat-pill px-3 py-1.5 rounded-lg font-medium whitespace-nowrap">Çökme</button>
          <button onclick="setCategory('Ağ & Bağlantı')" data-cat="Ağ & Bağlantı" class="cat-pill px-3 py-1.5 rounded-lg font-medium whitespace-nowrap">Ağ &amp; Ping</button>
        </div>
      </div>

      <!-- SEÇİLİ OYUN HATA REHBERLERİ LİSTESİ -->
      <section id="tabContent-issues" class="hidden space-y-4">
        <div id="issuesListContainer" class="space-y-4"></div>
      </section>

      <!-- 4. AI ÇÖZÜMLEYİCİ BÖLÜMÜ (2 Sütunlu Görsel Bento Düzeni: Sol Form, Sağ Hızlı Komut & Log Kutusu) -->
      <section id="tabContent-ai-lab" class="space-y-6">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">

          <!-- Sol Sütun (8/12): AI Analiz Formu -->
          <div class="lg:col-span-8 oc-card p-6 sm:p-8 space-y-6" style="border-top: 3px solid #10b981 !important;">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-white/10 pb-4">
              <div class="space-y-1">
                <div class="inline-flex items-center gap-2 text-xs font-extrabold text-[#34d399] uppercase tracking-wider">
                  <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M12 2a4 4 0 0 1 4 4v2a4 4 0 0 1-8 0V6a4 4 0 0 1 4-4z"/><path d="M16 14H8a4 4 0 0 0-4 4v2h16v-2a4 4 0 0 0-4-4z"/></svg>
                  <span>Otomatik Arıza &amp; Log Teşhis Motoru</span>
                </div>
                <h2 class="text-xl sm:text-2xl font-extrabold text-white">
                  Listede olmayan bir hata mı var? AI ile analiz et.
                </h2>
                <p class="text-xs sm:text-sm text-gray-300">
                  Oyun adını, aldığın hata kodunu ve belirtileri yaz; sistemine özel adım adım çözüm rehberi oluşturalım.
                </p>
              </div>
              <span id="aiModeBadge" class="oc-badge oc-badge-accent self-start">Canlı Analiz</span>
            </div>

            <form id="aiTroubleshootForm" onsubmit="submitAiAnalysis(event)" class="space-y-4">
              <!-- Honeypot -->
              <div class="hidden" aria-hidden="true">
                <input id="aiHpWebsiteInput" type="text" name="website_url_hp" tabindex="-1" autocomplete="off" />
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label for="aiGameSelect" class="block text-xs font-bold text-gray-200 mb-1.5">Oyun Adı *</label>
                  <input
                    id="aiGameSelect"
                    type="text"
                    list="allGamesDatalist"
                    required
                    placeholder="Örn: GTA 6, Valorant, CS2, Bannerlord..."
                    class="w-full bg-[#0b101b] text-base sm:text-sm text-white rounded-xl px-3.5 py-2.5 border border-white/15 focus:outline-none focus:border-[#34d399]"
                  />
                </div>
                <div>
                  <label for="aiErrorCodeInput" class="block text-xs font-bold text-gray-200 mb-1.5">Hata Kodu veya Başlık (Opsiyonel)</label>
                  <input
                    id="aiErrorCodeInput"
                    type="text"
                    placeholder="Örn: ERR_GFX_STATE, VAN 9003, 0x887A0006"
                    class="w-full bg-[#0b101b] text-base sm:text-sm text-white rounded-xl px-3.5 py-2.5 border border-white/15 focus:outline-none focus:border-[#34d399] font-mono"
                  />
                </div>
              </div>

              <div>
                <label for="aiSymptomInput" class="block text-xs font-bold text-gray-200 mb-1.5">Sorun Detayı (Ne zaman ve nasıl oluyor?) *</label>
                <textarea
                  id="aiSymptomInput"
                  rows="3"
                  required
                  placeholder="Örn: Oyunu açtıktan 2 dakika sonra siyah ekran verip ERR_GFX_STATE uyarısıyla masaüstüne atıyor..."
                  class="w-full bg-[#0b101b] text-base sm:text-sm text-white rounded-xl p-3.5 border border-white/15 focus:outline-none focus:border-[#34d399]"
                ></textarea>
              </div>

              <!-- İkincil Seçenekler: Donanım Algılama ve Crash Log Yükleme -->
              <details id="secondaryDiagDetails" class="oc-card bg-[#0e1524] border border-white/10 rounded-xl p-4">
                <summary class="cursor-pointer text-xs sm:text-sm font-bold text-[#34d399] flex items-center justify-between">
                  <span>+ Sistem Özellikleri, Otomatik Donanım Algılama ve Crash Log (.log / .txt) Ekle</span>
                  <span class="text-xs text-gray-400 font-normal">(İsteğe bağlı)</span>
                </summary>

                <div class="mt-4 pt-4 border-t border-white/10 space-y-4">
                  <div>
                    <div class="flex flex-wrap items-center justify-between gap-2 mb-1.5">
                      <label for="aiSpecsInput" class="text-xs font-bold text-gray-200">Sistem Özellikleri (GPU / CPU / RAM / Windows)</label>
                      <button
                        type="button"
                        id="detectHardwareBtn"
                        onclick="detectSystemHardware()"
                        class="oc-btn oc-btn-secondary !min-h-[36px] !py-1 !px-3 text-xs"
                      >
                        Donanımımı Otomatik Algıla
                      </button>
                    </div>
                    <input
                      id="aiSpecsInput"
                      type="text"
                      placeholder="Örn: Windows 11, Ryzen 5 5600, RTX 4060, 16GB RAM"
                      class="w-full bg-[#0b101b] text-base sm:text-sm text-white rounded-xl px-3.5 py-2.5 border border-white/15 focus:outline-none focus:border-[#34d399]"
                    />
                  </div>

                  <!-- Donanım Onay Kutusu -->
                  <div id="hardwareConfirmBox" class="hidden bg-[#101829] border border-[#34d399]/40 rounded-xl p-4 space-y-3">
                    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                      <div>
                        <div class="text-xs font-bold text-white">Donanım Tespiti Tamamlandı</div>
                        <p class="text-[11px] text-gray-400">Onaylarsanız aşağıdaki bilgiler forma aktarılır.</p>
                      </div>
                      <div class="flex items-center gap-2">
                        <button type="button" onclick="confirmAndApplyDetectedHardware()" class="oc-btn oc-btn-primary !min-h-[36px] !py-1 !px-3 text-xs">Onayla</button>
                        <button type="button" onclick="dismissHardwareConfirmBox()" class="oc-btn oc-btn-ghost !min-h-[36px] !py-1 !px-3 text-xs">Kapat</button>
                      </div>
                    </div>
                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                      <div class="p-2 rounded bg-[#172237]"><div class="text-[10px] text-gray-400">GPU</div><div id="hwDetectGpuText" class="font-bold text-white truncate">-</div></div>
                      <div class="p-2 rounded bg-[#172237]"><div class="text-[10px] text-gray-400">CPU</div><div id="hwDetectCpuText" class="font-bold text-white truncate">-</div></div>
                      <div class="p-2 rounded bg-[#172237]"><div class="text-[10px] text-gray-400">OS</div><div id="hwDetectOsText" class="font-bold text-white truncate">-</div></div>
                      <div class="p-2 rounded bg-[#172237]"><div class="text-[10px] text-gray-400">RAM</div><div id="hwDetectRamText" class="font-bold text-white truncate">-</div></div>
                    </div>
                    <input id="hwDetectEditableSummary" type="text" aria-label="Tespit edilen donanım özeti" class="w-full bg-[#0b101b] text-xs text-white rounded-lg px-3 py-2 border border-white/15" />
                  </div>

                  <!-- Crash Log Sürükle-Bırak Alanı -->
                  <div
                    id="crashLogDropZone"
                    ondragover="handleCrashLogDragOver(event)"
                    ondragleave="handleCrashLogDragLeave(event)"
                    ondrop="handleCrashLogDrop(event)"
                    class="rounded-xl border border-dashed border-[#34d399]/50 bg-[#0b101b] p-4 cursor-pointer transition"
                    onclick="document.getElementById('crashLogFileInput').click()"
                  >
                    <input
                      id="crashLogFileInput"
                      type="file"
                      accept=".log,.txt,.crash,.dmp,.xml,.ini"
                      class="hidden"
                      onchange="handleCrashLogFileSelect(event)"
                    />
                    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                      <div>
                        <div class="text-xs sm:text-sm font-bold text-white">Crash Log (.log, .txt) Dosyası Seç veya Sürükle</div>
                        <p class="text-[11px] text-gray-400 mt-0.5">Kişisel dosya yolları tarayıcıda otomatik maskelenir ve kritik hata satırları çıkarılır.</p>
                      </div>
                      <div class="flex items-center gap-2 shrink-0" onclick="event.stopPropagation()">
                        <button type="button" onclick="loadSampleCrashLog()" class="oc-btn oc-btn-ghost !min-h-[36px] !py-1 !px-3 text-xs">Örnek Log</button>
                        <button type="button" onclick="document.getElementById('crashLogFileInput').click()" class="oc-btn oc-btn-secondary !min-h-[36px] !py-1 !px-3 text-xs">Dosya Seç</button>
                      </div>
                    </div>

                    <div id="crashLogResultBox" class="hidden mt-3 pt-3 border-t border-white/10 space-y-2" onclick="event.stopPropagation()">
                      <div class="flex flex-wrap items-center justify-between gap-2 text-xs">
                        <div class="flex items-center gap-2">
                          <span class="text-[#34d399] font-bold" id="crashLogFileNameBadge">crash.log</span>
                          <span class="oc-badge oc-badge-warning" id="crashLogMatchCountBadge">Kritik Satırlar</span>
                          <span class="oc-badge oc-badge-success" id="crashLogMaskedCountBadge">Kişisel Yollar Maskelendi</span>
                        </div>
                        <button type="button" onclick="clearCrashLogAnalysis()" class="text-xs text-gray-400 hover:text-white underline">Temizle</button>
                      </div>
                      <pre id="crashLogExtractedPreview" class="text-[11px] font-mono bg-[#0b101b] text-gray-200 p-2.5 rounded-lg border border-white/10 overflow-x-auto max-h-36 whitespace-pre-wrap"></pre>
                    </div>
                  </div>

                  <!-- Örnek Oyun Önerileri -->
                  <div class="space-y-1.5">
                    <div class="flex items-center justify-between text-xs text-gray-400">
                      <span>Hızlı oyun seçimi:</span>
                      <button type="button" onclick="refreshRandomSuggestions()" class="text-[#34d399] hover:underline">Yenile</button>
                    </div>
                    <div id="aiLabSuggestionsContainer" class="flex flex-wrap gap-1.5"></div>
                  </div>
                </div>
              </details>

              <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1">
                <span class="text-xs text-gray-300">
                  Analiz tamamlandığında adım adım çözüm adımları aşağıda açılır.
                </span>
                <button
                  type="submit"
                  id="aiAnalyzeSubmitBtn"
                  class="oc-btn oc-btn-primary px-6 py-2.5 text-sm font-extrabold"
                >
                  <span>AI ile Analiz Et</span>
                </button>
              </div>
            </form>
          </div>

          <!-- Sağ Sütun (4/12): Görsel Hızlı Onarım Komutları & Log Klasörü Rehberi -->
          <aside class="lg:col-span-4 space-y-4">
            <div class="oc-card p-5 space-y-4" style="border-top: 3px solid #06b6d4 !important;">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <span class="w-8 h-8 rounded-lg bg-[#06b6d4]/20 border border-[#06b6d4]/40 text-[#38bdf8] flex items-center justify-center">
                    <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>
                  </span>
                  <div>
                    <h3 class="text-sm font-extrabold text-white">Hızlı Sistem Onarım Komutları</h3>
                    <p class="text-[11px] text-gray-400">Yönetici CMD / PowerShell için temel komutlar</p>
                  </div>
                </div>
              </div>

              <div class="space-y-2.5 text-xs">
                <div class="p-3 rounded-xl bg-[#0b101b] border border-white/10 space-y-1">
                  <div class="flex items-center justify-between text-[11px]">
                    <span class="font-bold text-[#34d399]">1. Bozuk Sistem Dosyalarını Onar</span>
                    <span class="text-gray-400 font-mono">Yönetici CMD</span>
                  </div>
                  <code class="block font-mono text-gray-200 select-all">sfc /scannow</code>
                </div>

                <div class="p-3 rounded-xl bg-[#0b101b] border border-white/10 space-y-1">
                  <div class="flex items-center justify-between text-[11px]">
                    <span class="font-bold text-[#38bdf8]">2. Ağ &amp; Soket Yığınını Sıfırla</span>
                    <span class="text-gray-400 font-mono">Ping / VAN 185</span>
                  </div>
                  <code class="block font-mono text-gray-200 select-all">netsh winsock reset &amp;&amp; ipconfig /flushdns</code>
                </div>

                <div class="p-3 rounded-xl bg-[#0b101b] border border-white/10 space-y-1">
                  <div class="flex items-center justify-between text-[11px]">
                    <span class="font-bold text-[#fbbf24]">3. DirectX Gölgelendirici Temizliği</span>
                    <span class="text-gray-400 font-mono">DX12 / Stutter</span>
                  </div>
                  <code class="block font-mono text-gray-200 select-all">cleanmgr /d C</code>
                </div>
              </div>
            </div>

            <div class="oc-card p-5 space-y-3" style="border-top: 3px solid #a855f7 !important;">
              <div class="flex items-center gap-2">
                <span class="w-8 h-8 rounded-lg bg-[#a855f7]/20 border border-[#a855f7]/40 text-[#c084fc] flex items-center justify-center">
                  <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                </span>
                <div>
                  <h3 class="text-sm font-extrabold text-white">Crash Log Dosyası Nerede?</h3>
                  <p class="text-[11px] text-gray-400">Win + R tuşlarına basıp yapıştırabilirsiniz</p>
                </div>
              </div>
              <ul class="space-y-2 text-xs text-gray-300">
                <li class="flex items-center justify-between gap-2 p-2 rounded-lg bg-[#0b101b] border border-white/5">
                  <span class="font-bold text-white">Valorant / UE</span>
                  <code class="font-mono text-[11px] text-[#34d399] select-all">%LOCALAPPDATA%\\VALORANT\\Saved\\Logs</code>
                </li>
                <li class="flex items-center justify-between gap-2 p-2 rounded-lg bg-[#0b101b] border border-white/5">
                  <span class="font-bold text-white">GTA 6 / RDR2</span>
                  <code class="font-mono text-[11px] text-[#38bdf8] select-all">%USERPROFILE%\\Documents\\Rockstar Games</code>
                </li>
                <li class="flex items-center justify-between gap-2 p-2 rounded-lg bg-[#0b101b] border border-white/5">
                  <span class="font-bold text-white">FiveM Crash</span>
                  <code class="font-mono text-[11px] text-[#fbbf24] select-all">%LOCALAPPDATA%\\FiveM\\FiveM.app\\crashes</code>
                </li>
              </ul>
            </div>
          </aside>
        </div>

        <!-- AI Sonuç Çıktısı -->
        <div id="aiResultContainer" class="hidden"></div>
      </section>

      <!-- 5. TOPLULUK FORUMU (Sayfanın Alt Kısmında) -->
      <section id="tabContent-forum" class="space-y-4 pt-4 border-t border-white/10">
        <div class="oc-card p-5 sm:p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 class="text-lg sm:text-xl font-extrabold text-white">Topluluk Soru &amp; Çözüm Forumu</h2>
            <p class="text-xs sm:text-sm text-gray-300 mt-1">
              Rehberlerde bulamadığın bir sorun varsa topluluğa sor; hem oyuncular hem de AI yanıtlasın.
            </p>
          </div>
          <button
            type="button"
            onclick="openAskModal()"
            class="oc-btn oc-btn-primary text-xs sm:text-sm font-bold shrink-0"
          >
            <span>+ Yeni Soru Sor</span>
          </button>
        </div>

        <div id="threadsListContainer" class="space-y-3"></div>
      </section>

      <!-- POPÜLER ÇÖZÜM REHBERLERİ (/cozum/ DİZİNİ) -->
      <section id="populerCozumRehberleri" class="pt-6 border-t border-white/10 space-y-4">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h2 class="text-lg sm:text-xl font-extrabold text-white">Adım Adım Oyun Çözüm Rehberleri</h2>
            <p class="text-xs sm:text-sm text-gray-400">Doğrudan hata koduna ve oyun motoruna özel hazırlanmış teknik sayfalar</p>
          </div>
          <a href="/hata-kodlari" class="text-xs font-bold text-[#34d399] hover:underline">Tüm Hata Kodları Dizini →</a>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 text-xs">
          <a href="./cozum/gta-6-acilmiyor-cokme-ve-fps-dusmesi-cozumu.html" class="oc-card oc-card-interactive p-3.5 block" style="border-left: 3px solid #ec4899 !important;">
            <div class="text-[#f472b6] font-extrabold mb-1">GTA 6 (Grand Theft Auto VI)</div>
            <div class="text-white font-semibold">GTA 6 Açılmıyor, ERR_GFX_STATE ve FPS Düşmesi Çözümü</div>
          </a>
          <a href="./cozum/valorant-van-9003-tpm-2-0-secure-boot-cozumu.html" class="oc-card oc-card-interactive p-3.5 block" style="border-left: 3px solid #f43f5e !important;">
            <div class="text-[#fb7185] font-bold mb-1">VALORANT</div>
            <div class="text-white font-semibold">VAN 9003 &amp; VAN 1067: Windows 11 TPM 2.0 ve Secure Boot Çözümü</div>
          </a>
          <a href="./cozum/cs2-vac-oyun-oturumunuzu-dogrulayamadi-cozumu.html" class="oc-card oc-card-interactive p-3.5 block" style="border-left: 3px solid #f59e0b !important;">
            <div class="text-[#fbbf24] font-bold mb-1">Counter-Strike 2</div>
            <div class="text-white font-semibold">VAC Oyun Oturumunuzu Doğrulayamadı Hatası Çözümü</div>
          </a>
          <a href="./cozum/lol-sampiyon-secimi-sonrasi-yeniden-baglan-hatasi.html" class="oc-card oc-card-interactive p-3.5 block" style="border-left: 3px solid #3b82f6 !important;">
            <div class="text-[#60a5fa] font-bold mb-1">League of Legends</div>
            <div class="text-white font-semibold">Şampiyon Seçimi Sonrası Yeniden Bağlan (Reconnect) Döngüsü</div>
          </a>
          <a href="./cozum/fivem-gta5-err-gfx-d3d-init-texture-loss-cozumu.html" class="oc-card oc-card-interactive p-3.5 block" style="border-left: 3px solid #10b981 !important;">
            <div class="text-[#34d399] font-bold mb-1">GTA V &amp; FiveM</div>
            <div class="text-white font-semibold">ERR_GFX_D3D_INIT Çökmesi ve Harita Yüklenmeme Çözümü</div>
          </a>
          <a href="./cozum/minecraft-exit-code-1-glfw-65542-hatasi-cozumu.html" class="oc-card oc-card-interactive p-3.5 block" style="border-left: 3px solid #22c55e !important;">
            <div class="text-[#4ade80] font-bold mb-1">Minecraft</div>
            <div class="text-white font-semibold">Exit Code: 1 ve GLFW Error 65542 Sürücü Çökmesi Çözümü</div>
          </a>
        </div>
      </section>

    </main>"""

    txt = txt[:idx_s] + new_main + txt[idx_e:]
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(txt)
    print("[OK] Updated index.html with Split-Hero, 2x2 Visual Diagnostic Bento cards, enriched Top 8 Error cards, and 2-column AI Bento layout")


def update_app_js_and_ui_components():
    # 1. Update static/ui_components.js?v=20261120v4 to remove "OÇ" in AuthorBox and use vibrant monogram styles
    ui_path = os.path.join(ROOT_DIR, "static", "ui_components.js")
    with open(ui_path, "r", encoding="utf-8") as f:
        ui_txt = f.read()

    ui_txt = ui_txt.replace('<span class="oc-monogram" aria-hidden="true">OÇ</span>', AUTHOR_ICON_HTML)
    with open(ui_path, "w", encoding="utf-8") as f:
        f.write(ui_txt)
    print("[OK] Removed OÇ from static/ui_components.js?v=20261120v4 AuthorBox")

    # 2. Update static/app.js?v=20261120v4:
    # - Remove "OÇ" in dynamic issue AuthorBox
    # - Fix updateHeroBanner() when STATE.selectedGame === 'all' so it preserves our new visual Split-Hero title, subtitle, hidden coverWrapper, and colorful Popular Searches tags!
    # - Add filterHomeTopErrors(cat, btn) for the new visual category filter tabs on the homepage
    # - Upgrade renderHomeShowcase() so game cards stay colorful with left accent border and engine subtitle
    app_path = os.path.join(ROOT_DIR, "static", "app.js")
    with open(app_path, "r", encoding="utf-8") as f:
        app_txt = f.read()

    # Replace any raw OÇ inside static/app.js?v=20261120v4 author box
    app_txt = re.sub(
        r'<div class="w-9 h-9 rounded-xl[^"]*">\s*OÇ\s*</div>',
        AUTHOR_ICON_HTML,
        app_txt,
    )

    # Fix updateHeroBanner() for STATE.selectedGame === 'all'
    old_hero_branch = """  if (STATE.selectedGame === 'all') {
    applyGameTheme('#5e9c88');
    if (coverWrapper && coverImg) {
      coverWrapper.classList.remove('hidden');
      coverImg.onerror = null;
      coverImg.src = './static/logo.svg';
      coverImg.alt = 'OyunÇöz Tüm Oyunlar';
      coverImg.className = 'w-32 h-20 sm:w-40 sm:h-24 rounded-2xl object-contain bg-[#151c27] p-2 border border-[#88c0a8]/35 shadow-xl transition-all duration-300';
    }
    catBadge.textContent = 'Tüm Oyunlar Portalı';
    engBadge.textContent = 'Motor: UE4/5 / Source 2 / Clausewitz / RAGE / LWJGL';
    acBadge.textContent = 'Koruma: Vanguard • VAC • EAC • RICOCHET';
    titleEl.textContent = 'Popüler Oyun Sorunları & Yapay Zeka Çözüm Merkezi';
    subEl.textContent = 'Sol menüden bir oyun seçebilir, "+ Yeni Oyun Ekle" ile istediğiniz oyunu (örn: Victoria 3, Bannerlord, RDR 2) ekleyebilir veya AI Çözümleyiciye yazarak otomatik sayfa oluşturabilirsiniz.';

    const globalTags = ['VAN 9003', 'VAC Verify', 'Exit Code 1', 'Packet Burst', 'EA AntiCheat', 'FIVEM Texture Loss', 'Asset Warmup', 'CP77 Flatlined'];
    tagsEl.innerHTML = globalTags
      .map(t => `<button onclick="filterByTag('${t}')" class="text-xs px-2.5 py-1 rounded-lg bg-white/5 hover:bg-white/10 text-gray-200 border border-white/10 transition font-mono">${t}</button>`)
      .join('');
  }"""

    new_hero_branch = """  if (STATE.selectedGame === 'all') {
    applyGameTheme('#10b981');
    if (coverWrapper) {
      coverWrapper.classList.add('hidden');
    }
    if (engBadge) engBadge.classList.add('hidden');
    if (acBadge) acBadge.classList.add('hidden');
    if (catBadge) {
      catBadge.innerHTML = '<span class="w-2 h-2 rounded-full bg-[#34d399] animate-pulse"></span><span>CANLI OYUN ARIZA &amp; FPS ÇÖZÜM MERKEZİ</span>';
    }
    if (titleEl) {
      titleEl.textContent = 'Hangi hatayı alıyorsun?';
    }
    if (subEl) {
      subEl.innerHTML = 'Aldığın hata kodunu (<code class="text-[#34d399] font-mono font-bold">VAN 185</code>, <code class="text-[#38bdf8] font-mono font-bold">ERR_GFX_STATE</code>, <code class="text-[#f43f5e] font-mono font-bold">VAN 9003</code>) veya oyun adını yaz; doğrudan test edilmiş adım adım çözüm sayfasına git.';
    }
  }"""

    if old_hero_branch in app_txt:
        app_txt = app_txt.replace(old_hero_branch, new_hero_branch, 1)
        print("[OK] Fixed updateHeroBanner() in static/app.js?v=20261120v4 so it never overwrites the homepage Hero")

    # Add filterHomeTopErrors and upgraded renderHomeShowcase
    filter_helper_js = """
window.filterHomeTopErrors = function(catKey, btnEl) {
  const cards = document.querySelectorAll('#homeTopErrorsGrid > article[data-error-cat]');
  cards.forEach(card => {
    const c = card.getAttribute('data-error-cat');
    if (!catKey || catKey === 'all' || c === catKey) {
      card.classList.remove('hidden');
    } else {
      card.classList.add('hidden');
    }
  });
  const btns = document.querySelectorAll('.home-err-filter-btn');
  btns.forEach(b => {
    b.className = 'home-err-filter-btn px-3 py-1.5 rounded-xl text-xs font-bold bg-white/5 text-gray-300 hover:text-white border border-white/10 transition';
  });
  if (btnEl) {
    btnEl.className = 'home-err-filter-btn px-3 py-1.5 rounded-xl text-xs font-extrabold bg-[#10b981] text-white border border-[#34d399]/50 transition';
  }
};
"""
    if "window.filterHomeTopErrors =" not in app_txt:
        app_txt += "\n" + filter_helper_js

    # Also update renderHomeShowcase in static/app.js?v=20261120v4 so dynamic render keeps colorful left borders & engine info
    old_showcase_fn = """window.renderHomeShowcase = function() {
  try {
    const gamesGrid = document.getElementById('homeGamesShowcaseGrid');
    if (gamesGrid && STATE.games.length > 0) {
      // Calculate real error count per game from STATE.issues + DEDICATED_ERROR_PAGES
      const featuredGames = STATE.games.slice(0, 18);
      gamesGrid.innerHTML = featuredGames.map(g => {
        const mono = window.getGameMonogramInfo ? window.getGameMonogramInfo(g.slug, g.accent_color) : { code: (g.short_name || 'OYN').slice(0,3).toUpperCase(), color: '#5e9c88' };
        const realCount = Math.max(Number(g.issue_count || 0), 1);
        return `
          <a
            href="/${g.slug}-hata-cozumleri.html"
            onclick="event.preventDefault(); selectGame('${g.slug}'); switchTab('issues'); document.getElementById('tabContent-issues')?.scrollIntoView({behavior:'smooth'});"
            class="oc-card oc-card-interactive p-3.5 flex items-center gap-3"
          >
            <span class="oc-monogram" style="border-color:${mono.color}66;background-color:${mono.color}1f" aria-hidden="true">${mono.code}</span>
            <div class="min-w-0">
              <div class="text-xs sm:text-sm font-bold text-white truncate">${escapeHTML(g.short_name || g.name)}</div>
              <div class="text-[11px] text-gray-400">${realCount} Hata Kodu</div>
            </div>
          </a>
        `;
      }).join('');
    }
  } catch (e) {
    console.warn('renderHomeShowcase error:', e);
  }
};"""

    new_showcase_fn = """window.renderHomeShowcase = function() {
  try {
    const gamesGrid = document.getElementById('homeGamesShowcaseGrid');
    if (gamesGrid && STATE.games.length > 0) {
      const featuredGames = STATE.games.slice(0, 16);
      gamesGrid.innerHTML = featuredGames.map(g => {
        const mono = window.getGameMonogramInfo ? window.getGameMonogramInfo(g.slug, g.accent_color) : { code: (g.short_name || 'OYN').slice(0,3).toUpperCase(), color: '#10b981' };
        const realCount = Math.max(Number(g.issue_count || 0), 1);
        const engineInfo = escapeHTML((g.engine || 'PC').split('(')[0].trim());
        return `
          <a
            href="/${g.slug}-hata-cozumleri.html"
            onclick="event.preventDefault(); selectGame('${g.slug}'); switchTab('issues'); document.getElementById('tabContent-issues')?.scrollIntoView({behavior:'smooth'});"
            class="oc-card oc-card-interactive p-4 flex items-center justify-between gap-3 group"
            style="border-left: 3px solid ${mono.color} !important;"
          >
            <div class="flex items-center gap-3 min-w-0">
              <span class="oc-monogram" style="background: linear-gradient(135deg, ${mono.color}, ${mono.color}bb); border-color: rgba(255,255,255,0.28);" aria-hidden="true">${mono.code}</span>
              <div class="min-w-0">
                <div class="text-xs sm:text-sm font-extrabold text-white group-hover:text-[#34d399] transition truncate">${escapeHTML(g.short_name || g.name)}</div>
                <div class="text-[11px] text-gray-400 truncate">${engineInfo}</div>
              </div>
            </div>
            <span class="px-2.5 py-1 rounded-lg bg-white/5 border border-white/10 text-[11px] font-bold text-gray-200 shrink-0">${realCount} Hata Kodu</span>
          </a>
        `;
      }).join('');
    }
  } catch (e) {
    console.warn('renderHomeShowcase error:', e);
  }
};"""

    if old_showcase_fn in app_txt:
        app_txt = app_txt.replace(old_showcase_fn, new_showcase_fn, 1)
        print("[OK] Upgraded renderHomeShowcase() in static/app.js?v=20261120v4 with colorful cards")

    with open(app_path, "w", encoding="utf-8") as f:
        f.write(app_txt)


def update_error_page_builder_and_rebuild():
    ep_path = os.path.join(ROOT_DIR, "error_page_builder.py")
    with open(ep_path, "r", encoding="utf-8") as f:
        ep_txt = f.read()

    # Replace both occurrences of OÇ in error_page_builder.py (header logo & author box)
    ep_txt = ep_txt.replace(
        '<span class="oc-monogram" aria-hidden="true">OÇ</span>',
        BRAND_ICON_HTML,
    )

    with open(ep_path, "w", encoding="utf-8") as f:
        f.write(ep_txt)

    import importlib
    import error_page_builder as epb
    importlib.reload(epb)
    cnt, warns = epb.build_all_from_json()
    print(f"[OK] Rebuilt {cnt} dedicated error pages without OÇ and with vibrant styling")


def scrub_all_remaining_oc_badges():
    """Remove any remaining >OÇ< or standalone OÇ badge boxes across all HTML/PY/JS files."""
    count_files = 0
    for root, dirs, files in os.walk(ROOT_DIR):
        if ".git" in dirs:
            dirs.remove(".git")
        for fname in files:
            if not fname.endswith((".html", ".py", ".js")):
                continue
            if fname == "apply_visual_upgrade.py":
                continue
            fpath = os.path.join(root, fname)
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                txt = f.read()
            orig = txt
            # 1. <span class="oc-monogram"...>OÇ</span>
            txt = re.sub(
                r'<span[^>]*class="[^"]*oc-monogram[^"]*"[^>]*>\s*OÇ\s*</span>',
                BRAND_ICON_HTML,
                txt,
            )
            # 2. <div class="... font-extrabold ...">OÇ</div> in hub pages / older templates
            txt = re.sub(
                r'<div class="w-\d+\s+h-\d+\s+rounded-[^>]*>\s*OÇ\s*</div>',
                AUTHOR_ICON_HTML,
                txt,
            )
            # 3. og_generator.py or any other literal '>OÇ<'
            txt = txt.replace(">OÇ<", ">" + BRAND_ICON_HTML + "<")
            if txt != orig:
                with open(fpath, "w", encoding="utf-8") as wf:
                    wf.write(txt)
                count_files += 1
    print(f"[OK] Scrubbed OÇ badge from {count_files} additional files")


if __name__ == "__main__":
    with open(os.path.join(ROOT_DIR, "data", "hata_kodlari.json"), "r", encoding="utf-8") as f:
        data_obj = json.load(f)
        pages = data_obj["pages"] if isinstance(data_obj, dict) and "pages" in data_obj else data_obj
    update_styles_css()
    update_index_html(pages)
    update_app_js_and_ui_components()
    update_error_page_builder_and_rebuild()
    scrub_all_remaining_oc_badges()
