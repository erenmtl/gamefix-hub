# -*- coding: utf-8 -*-
"""
AŞAMA 1: Yeniden Kullanılabilir Hata Kodu Sayfa Şablonu ve Üretim Motoru (error_page_builder.py)
Veri Kaynağı: data/hata_kodlari.json

Her hata kodu kaydı şu alanları taşır:
- slug (örn. "lol/van-185")
- oyun (örn. "League of Legends")
- oyun_hub_url (opsiyonel, varsayılan oyun adına göre hub sayfası, örn. "/lol-hata-cozumleri.html")
- hata_kodu (örn. "VAN 185")
- varyant_yazimlari (liste, örn. ["vanguard 185", "van 185", "van185", "lol vanguard hatası 185"])
- title (<= 60 karakter)
- meta_description (<= 160 karakter)
- h1 (tek H1)
- kisa_aciklama (hata kodunun ne anlama geldiği, 2-3 cümle)
- nedenler (liste)
- cozum_adimlari (liste: baslik, aciklama, komut [opsiyonel], komut_notu [opsiyonel: ne_yapar, risk, geri_alma], anakart_adimlari [opsiyonel], gorsel_yolu [opsiyonel], alt_metin [zorunlu])
- isle_yaramazsa (metin veya liste)
- resmi_kaynak_url (opsiyonel URL; boşsa yer tutucu kalır)
- sss (liste: soru, cevap)
- ilgili_hatalar (liste: url, oyun, hata_kodu, baslik)
- video_embed_url (opsiyonel; doluysa lazy-load iframe, boşsa gösterilmez)
- yazar (örn. "OyunÇöz Teknik Ekibi")
- tarih_yayin (YYYY-MM-DD)
- tarih_guncelleme (YYYY-MM-DD)
- test_edilen_surum (metin)
"""
import os
import re
import json
import html
from typing import Any, Dict, List, Tuple

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(ROOT_DIR, "data", "hata_kodlari.json")

REQUIRED_FIELDS = [
    "slug",
    "oyun",
    "hata_kodu",
    "varyant_yazimlari",
    "title",
    "meta_description",
    "h1",
    "kisa_aciklama",
    "nedenler",
    "cozum_adimlari",
    "isle_yaramazsa",
    "resmi_kaynak_url",
    "sss",
    "ilgili_hatalar",
    "video_embed_url",
    "yazar",
    "tarih_yayin",
    "tarih_guncelleme",
    "test_edilen_surum",
]

DEFAULT_GAME_HUB_MAP = {
    "League of Legends": "/lol-hata-cozumleri.html",
    "Valorant": "/valorant-hata-cozumleri.html",
    "Counter-Strike 2": "/cs2-hata-cozumleri.html",
    "GTA V": "/gtav-fivem-hata-cozumleri.html",
    "FiveM": "/gtav-fivem-hata-cozumleri.html",
    "Red Dead Redemption 2": "/red-dead-redemption-2-hata-cozumleri.html",
    "Mount & Blade II: Bannerlord": "/mount-and-blade-2-bannerlord-hata-cozumleri.html",
    "EA Sports FC 25": "/fc25-hata-cozumleri.html",
    "Black Myth: Wukong": "/black-myth-wukong-hata-cozumleri.html",
    "Minecraft": "/minecraft-hata-cozumleri.html",
}

FORBIDDEN_GUARANTEE_PATTERNS = [
    r"\bkesin\s+çözüm\b",
    r"\bgarantili\b",
    r"\bsaniyeler\s+içinde\b",
    r"%\s*9[0-9]\s*(?:başarı|oranında)",
]


def format_date_tr(iso_date: str) -> str:
    raw = (iso_date or "2026-11-17").strip()[:10]
    parts = raw.split("-")
    if len(parts) == 3 and len(parts[0]) == 4:
        return f"{parts[2]}.{parts[1]}.{parts[0]}"
    return raw


def normalize_video_embed_url(raw_url: str) -> str:
    """
    Stage 6.1: Converts YouTube watch/short/youtu.be or TikTok URLs into clean embed URLs,
    or returns already-formatted embed URLs unchanged. Returns '' if empty.
    """
    url = (raw_url or "").strip()
    if not url:
        return ""
    m_yt = re.search(r"(?:youtube\.com/(?:watch\?v=|shorts/)|youtu\.be/)([A-Za-z0-9_-]{6,})", url)
    if m_yt:
        return f"https://www.youtube-nocookie.com/embed/{m_yt.group(1)}"
    m_tt = re.search(r"tiktok\.com/.*/video/(\d+)", url)
    if m_tt:
        return f"https://www.tiktok.com/embed/v2/{m_tt.group(1)}"
    return url


def validate_record(record: Dict[str, Any]) -> List[str]:
    """
    Validates a single error code page record and prints/returns warnings if limits are exceeded.
    - Checks all required fields exist
    - Checks title <= 60 chars
    - Checks meta_description <= 160 chars
    - Checks mandatory alt_metin on each solution step
    - Checks against guarantee language ("kesin çözüm", "garantili", "saniyeler içinde")
    """
    warnings: List[str] = []
    slug = record.get("slug", "<bilinmeyen-slug>")

    for field in REQUIRED_FIELDS:
        if field not in record:
            warnings.append(f"[UYARI] ({slug}) Zorunlu alan eksik: '{field}'")

    title = str(record.get("title") or "")
    if len(title) > 60:
        warnings.append(
            f"[UYARI] ({slug}) 'title' 60 karakter sınırını aşıyor ({len(title)} karakter): \"{title}\""
        )
    if not title:
        warnings.append(f"[UYARI] ({slug}) 'title' boş bırakılamaz.")

    meta_desc = str(record.get("meta_description") or "")
    if len(meta_desc) > 160:
        warnings.append(
            f"[UYARI] ({slug}) 'meta_description' 160 karakter sınırını aşıyor ({len(meta_desc)} karakter): \"{meta_desc}\""
        )
    if not meta_desc:
        warnings.append(f"[UYARI] ({slug}) 'meta_description' boş bırakılamaz.")

    for idx, step in enumerate(record.get("cozum_adimlari") or [], start=1):
        alt_text = str(step.get("alt_metin") or "").strip()
        if not alt_text:
            warnings.append(
                f"[UYARI] ({slug}) Çözüm Adımı {idx} için 'alt_metin' alanı zorunludur ve boş bırakılamaz!"
            )

    combined_text = f"{title} {meta_desc} {record.get('h1', '')} {record.get('kisa_aciklama', '')}"
    for pat in FORBIDDEN_GUARANTEE_PATTERNS:
        if re.search(pat, combined_text, flags=re.IGNORECASE):
            warnings.append(
                f"[UYARI] ({slug}) Garanti dili tespit edildi ('{pat}'). Lütfen nötr ifade kullanın."
            )

    return warnings


def render_step_image_slot(step: Dict[str, Any], idx: int, game_name: str, error_code: str) -> str:
    """
    Renders the step image or a clean visual placeholder if gorsel_yolu is empty or file is not yet added.
    alt_metin is mandatory and always preserved.
    """
    img_path = str(step.get("gorsel_yolu") or "").strip()
    alt_text = html.escape(
        str(step.get("alt_metin") or f"{game_name} {error_code} Adım {idx} ekran görüntüsü").strip()
    )
    step_title = html.escape(str(step.get("baslik") or f"Adım {idx}"))

    # Check if image exists on disk when a path is provided
    disk_exists = False
    if img_path:
        rel_disk = img_path.lstrip("/")
        disk_exists = os.path.isfile(os.path.join(ROOT_DIR, rel_disk))

    if img_path and disk_exists:
        return f"""
          <figure class="step-screenshot-slot rounded-xl overflow-hidden border border-white/10 bg-[#121722] p-3 space-y-2">
            <img
              src="{html.escape(img_path)}"
              alt="{alt_text}"
              loading="lazy"
              decoding="async"
              width="720"
              height="380"
              class="w-full max-h-60 object-cover rounded-lg border border-white/10"
            />
            <figcaption class="text-[11px] text-gray-400 flex items-center justify-between gap-2">
              <span>📸 <strong>Adım {idx} Görseli:</strong> {alt_text}</span>
              <span class="text-[#88c0a8] font-mono">{html.escape(img_path)}</span>
            </figcaption>
          </figure>"""

    placeholder_path = html.escape(img_path if img_path else f"/static/screenshots/{game_name.lower().replace(' ', '-')}-{error_code.lower().replace(' ', '-')}-adim-{idx}.png")
    return f"""
          <figure class="step-screenshot-slot rounded-xl border border-dashed border-[#88c0a8]/35 bg-[#121722]/90 p-4 space-y-1.5" role="group" aria-label="{alt_text}">
            <div class="flex items-center justify-between gap-2 text-xs text-[#a3d9c6] font-semibold">
              <span>🖼️ Ekran Görüntüsü Alanı (Adım {idx}: {step_title})</span>
              <span class="text-[11px] font-mono text-gray-400">{placeholder_path}</span>
            </div>
            <figcaption class="text-[11px] text-gray-400">
              <strong>Alt Metin (Zorunlu):</strong> <span class="text-gray-300">{alt_text}</span>
            </figcaption>
          </figure>"""


def render_error_code_page(record: Dict[str, Any]) -> Tuple[str, List[str]]:
    """
    Renders a complete standalone HTML page for a single error code following the exact section order of Stage 1.
    Returns (html_content, warnings).
    """
    warnings = validate_record(record)

    slug = str(record["slug"]).strip("/")
    canonical_url = f"https://oyuncoz.com/{slug}"
    oyun = str(record["oyun"]).strip()
    oyun_hub_url = str(record.get("oyun_hub_url") or DEFAULT_GAME_HUB_MAP.get(oyun, "/hata-kodlari")).strip()
    hata_kodu = str(record["hata_kodu"]).strip()
    title_raw = str(record["title"]).strip()
    meta_desc_raw = str(record["meta_description"]).strip()
    h1_raw = str(record["h1"]).strip()
    kisa_aciklama_raw = str(record["kisa_aciklama"]).strip()
    yazar_raw = str(record.get("yazar") or "OyunÇöz Teknik Ekibi").strip()
    tarih_yayin = str(record.get("tarih_yayin") or "2026-03-01").strip()
    tarih_guncelleme = str(record.get("tarih_guncelleme") or "2026-11-17").strip()
    tarih_guncelleme_tr = format_date_tr(tarih_guncelleme)
    test_edilen_surum = str(record.get("test_edilen_surum") or "Windows 10 / 11 (64-bit)").strip()
    issue_id = int(record.get("issue_id") or 1)
    og_image_url = str(record.get("og_image") or "https://oyuncoz.com/static/og-banner.png").strip()

    # JSON-LD: ONLY TechArticle and BreadcrumbList (NO FAQPage, NO HowTo per Stage 1.4)
    schema_obj = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BreadcrumbList",
                "@id": f"{canonical_url}#breadcrumb",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "Ana Sayfa",
                        "item": "https://oyuncoz.com/",
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": oyun,
                        "item": f"https://oyuncoz.com{oyun_hub_url}" if oyun_hub_url.startswith("/") else oyun_hub_url,
                    },
                    {
                        "@type": "ListItem",
                        "position": 3,
                        "name": hata_kodu,
                        "item": canonical_url,
                    },
                ],
            },
            {
                "@type": "TechArticle",
                "@id": f"{canonical_url}#article",
                "headline": h1_raw,
                "description": meta_desc_raw,
                "inLanguage": "tr",
                "datePublished": tarih_yayin,
                "dateModified": tarih_guncelleme,
                "mainEntityOfPage": {
                    "@type": "WebPage",
                    "@id": canonical_url,
                },
                "author": {
                    "@type": "Organization",
                    "name": yazar_raw,
                    "url": "https://oyuncoz.com/hakkimizda.html",
                },
                "publisher": {
                    "@type": "Organization",
                    "@id": "https://oyuncoz.com/#organization",
                    "name": "OyunÇöz",
                    "url": "https://oyuncoz.com/",
                    "logo": {
                        "@type": "ImageObject",
                        "url": "https://oyuncoz.com/static/og-banner.png",
                        "width": 1200,
                        "height": 630,
                    },
                },
            },
        ],
    }
    schema_json_str = json.dumps(schema_obj, ensure_ascii=False, indent=2)

    # 4. "Bu hatanın nedenleri"
    nedenler_items = []
    for n in record.get("nedenler") or []:
        nedenler_items.append(f'          <li class="leading-relaxed">{html.escape(str(n))}</li>')
    nedenler_html = "\n".join(nedenler_items)

    # 5. "Adım adım çözüm"
    steps_blocks = []
    for idx, st in enumerate(record.get("cozum_adimlari") or [], start=1):
        st_title = html.escape(str(st.get("baslik") or f"Adım {idx}"))
        st_desc = html.escape(str(st.get("aciklama") or ""))
        cmd_raw = str(st.get("komut") or "").strip()
        cmd_note = st.get("komut_notu") or {}
        motherboard_tabs = st.get("anakart_bolumleri") or []

        cmd_html = ""
        if cmd_raw:
            cmd_esc = html.escape(cmd_raw)
            risk_box_html = ""
            if cmd_note and (cmd_note.get("ne_yapar") or cmd_note.get("risk") or cmd_note.get("geri_alma")):
                ne_yapar = html.escape(str(cmd_note.get("ne_yapar") or ""))
                risk_txt = html.escape(str(cmd_note.get("risk") or ""))
                geri_alma = html.escape(str(cmd_note.get("geri_alma") or ""))
                risk_box_html = f"""
            <div class="stage2-risky-cmd-note p-3.5 rounded-xl bg-[#141a24] border border-amber-400/35 text-xs space-y-2">
              <div class="font-bold text-amber-200">⚠️ Komut Güvenlik ve Geri Alma Notu:</div>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-2.5 text-[11px] leading-relaxed">
                <div class="p-2.5 rounded-lg bg-white/5 border border-white/5">
                  <strong class="text-[#88c0a8] block mb-0.5">🔍 Ne yapar?</strong>
                  <span class="text-gray-200">{ne_yapar}</span>
                </div>
                <div class="p-2.5 rounded-lg bg-white/5 border border-white/5">
                  <strong class="text-amber-300 block mb-0.5">⚡ Risk:</strong>
                  <span class="text-gray-200">{risk_txt}</span>
                </div>
                <div class="p-2.5 rounded-lg bg-white/5 border border-white/5">
                  <strong class="text-sky-300 block mb-0.5">↩️ Geri alma:</strong>
                  <span class="text-gray-200">{geri_alma}</span>
                </div>
              </div>
            </div>"""

            cmd_html = f"""
          <div class="space-y-2.5">
            <div class="bg-[#11161f] border border-[#88c0a8]/30 rounded-xl px-4 py-2.5 flex items-center justify-between gap-3">
              <code class="text-xs sm:text-sm font-mono text-[#a3d9c6] overflow-x-auto select-all">{cmd_esc}</code>
              <button type="button" data-cmd="{cmd_esc}" onclick="copyTemplateCmd(this)" class="px-3 py-1 rounded-lg bg-[#5e9c88]/25 hover:bg-[#5e9c88]/40 text-[#e2f1ec] text-xs font-bold shrink-0 transition">📋 Kopyala</button>
            </div>{risk_box_html}
          </div>"""

        mb_html = ""
        if motherboard_tabs:
            mb_cards = []
            for mb in motherboard_tabs:
                brand = html.escape(str(mb.get("marka") or ""))
                yol = html.escape(str(mb.get("adimlar") or ""))
                mb_alt = html.escape(str(mb.get("alt_metin") or f"{brand} BIOS ayar ekranı görüntüsü"))
                mb_cards.append(f"""
              <div class="p-3.5 rounded-xl bg-[#141923] border border-white/10 space-y-2">
                <div class="font-bold text-xs text-[#a3d9c6]">{brand} Anakart BIOS Adımları</div>
                <p class="text-xs text-gray-300 leading-relaxed">{yol}</p>
                <div class="text-[11px] text-gray-400 border border-dashed border-white/10 rounded-lg px-2.5 py-1.5 bg-[#10151e]">
                  🖼️ Görsel Alanı (Alt metin: <span class="text-gray-300">{mb_alt}</span>)
                </div>
              </div>""")
            mb_html = f"""
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
{"".join(mb_cards)}
          </div>"""

        img_slot_html = render_step_image_slot(st, idx, oyun, hata_kodu)

        steps_blocks.append(f"""
        <div class="bg-[#18202c] border border-white/10 rounded-2xl p-5 space-y-3.5">
          <div class="flex items-center gap-3">
            <span class="w-7 h-7 rounded-lg bg-[#5e9c88]/25 border border-[#88c0a8]/40 text-[#a3d9c6] font-extrabold text-xs flex items-center justify-center shrink-0">Adım {idx}</span>
            <h3 class="text-sm sm:text-base font-bold text-white">{st_title}</h3>
          </div>
          <p class="text-xs sm:text-sm text-gray-300 leading-relaxed">{st_desc}</p>{cmd_html}{mb_html}{img_slot_html}
        </div>""")
    steps_html = "\n".join(steps_blocks)

    # 6. "İşe yaramazsa" bölümü
    isle_yaramazsa_val = record.get("isle_yaramazsa") or record.get("ise_yaramazsa") or ""
    if isinstance(isle_yaramazsa_val, list):
        iy_items = "\n".join(
            f'          <li class="leading-relaxed">{html.escape(str(item))}</li>'
            for item in isle_yaramazsa_val
        )
        isle_yaramazsa_inner = f'<ul class="list-disc pl-5 text-xs sm:text-sm text-gray-300 space-y-2">\n{iy_items}\n        </ul>'
    else:
        isle_yaramazsa_inner = f'<p class="text-xs sm:text-sm text-gray-300 leading-relaxed">{html.escape(str(isle_yaramazsa_val))}</p>'

    # 7. Video (varsa - Stage 1.2 & Stage 6.1: lazy-loaded iframe only when video_embed_url is non-empty)
    video_embed_url = normalize_video_embed_url(str(record.get("video_embed_url") or ""))
    video_section_html = ""
    if video_embed_url:
        video_section_html = f"""
      <!-- Bölüm 6: Video Rehber (Varsa) -->
      <section id="video-rehber" class="bg-[#18202c] border border-white/10 rounded-2xl p-6 space-y-3">
        <h2 class="text-base sm:text-lg font-extrabold text-white">🎬 Video Çözüm Rehberi</h2>
        <div class="aspect-video w-full rounded-xl overflow-hidden border border-white/10 bg-black">
          <iframe
            src="{html.escape(video_embed_url)}"
            title="{html.escape(h1_raw)} Video Rehberi"
            loading="lazy"
            referrerpolicy="strict-origin-when-cross-origin"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen
            class="w-full h-full border-0"
          ></iframe>
        </div>
      </section>"""

    # 8. Resmi kaynak linki (resmi_kaynak_url)
    resmi_url = str(record.get("resmi_kaynak_url") or "").strip()
    resmi_etiket = html.escape(str(record.get("resmi_kaynak_baslik") or f"{oyun} Resmi Destek Sayfası"))
    if resmi_url:
        resmi_link_el = f"""
        <a href="{html.escape(resmi_url)}" target="_blank" rel="noopener noreferrer" class="px-4 py-2 rounded-xl text-xs font-bold bg-white/10 hover:bg-white/15 text-[#a3d9c6] border border-white/15 shrink-0 transition">
          🔗 {resmi_etiket} ↗
        </a>"""
    else:
        resmi_link_el = f"""
        <span class="px-3.5 py-2 rounded-xl text-xs font-mono bg-white/5 text-gray-400 border border-dashed border-white/15 shrink-0" data-official-url-slot="pending">
          🔗 Resmi destek bağlantısı eklenecek ({resmi_etiket})
        </span>"""

    # 9. SSS (Sıkça Sorulan Sorular)
    sss_blocks = []
    for qa in record.get("sss") or []:
        q_txt = html.escape(str(qa.get("soru") or ""))
        a_txt = html.escape(str(qa.get("cevap") or ""))
        sss_blocks.append(f"""
        <div class="bg-[#18202c] border border-white/10 rounded-xl p-4 space-y-1.5">
          <h3 class="text-xs sm:text-sm font-bold text-white">{q_txt}</h3>
          <p class="text-xs sm:text-sm text-gray-300 leading-relaxed">{a_txt}</p>
        </div>""")
    sss_html = "\n".join(sss_blocks)

    # 10. "İlgili hatalar" (iç linkler)
    ilgili_blocks = []
    for rel_item in record.get("ilgili_hatalar") or []:
        r_url = html.escape(str(rel_item.get("url") or "/hata-kodlari"))
        r_game = html.escape(str(rel_item.get("oyun") or oyun))
        r_code = html.escape(str(rel_item.get("hata_kodu") or ""))
        r_title = html.escape(str(rel_item.get("baslik") or ""))
        label_top = f"{r_game} • {r_code}" if r_code else r_game
        ilgili_blocks.append(f"""
          <a href="{r_url}" class="p-3.5 rounded-xl bg-[#141923] hover:bg-[#1e2636] border border-white/10 hover:border-[#88c0a8]/40 transition flex items-center justify-between gap-2 text-xs">
            <div>
              <span class="font-mono text-[#a3d9c6] font-bold block">{label_top}</span>
              <span class="text-gray-200 font-semibold">{r_title}</span>
            </div>
            <span class="text-[#88c0a8] font-bold shrink-0">→</span>
          </a>""")
    ilgili_html = "\n".join(ilgili_blocks)

    html_out = f"""<!DOCTYPE html>
<html lang="tr" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(title_raw)}</title>
  <meta name="description" content="{html.escape(meta_desc_raw)}" />
  <meta name="author" content="{html.escape(yazar_raw)}" />
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" />
  <meta name="googlebot" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" />
  <link rel="canonical" href="{canonical_url}" />
  <link rel="alternate" hreflang="tr-TR" href="{canonical_url}" />
  <link rel="icon" type="image/svg+xml" href="/static/favicon.svg" />
  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="OyunÇöz" />
  <meta property="og:locale" content="tr_TR" />
  <meta property="og:url" content="{canonical_url}" />
  <meta property="og:title" content="{html.escape(title_raw)}" />
  <meta property="og:description" content="{html.escape(meta_desc_raw)}" />
  <meta property="og:image" content="{html.escape(og_image_url)}" />
  <meta property="og:image:type" content="image/png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{html.escape(title_raw)}" />
  <meta name="twitter:description" content="{html.escape(meta_desc_raw)}" />
  <meta name="twitter:image" content="{html.escape(og_image_url)}" />
  <script type="application/ld+json">
{schema_json_str}
  </script>
  <style id="critical-css">
    :root{{--accent:#5e9c88;--bg-dark:#141923;--bg-panel:#1b2230;--bg-card:#202838;--text-main:#d8dee9;--text-muted:#94a3b8}}
    html,body{{background-color:#141923;color:#d8dee9;font-family:'Inter',-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;margin:0;padding:0}}
    .text-white{{color:#e6ecf5!important}}
  </style>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/static/styles.css" />
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="min-h-screen flex flex-col bg-[#141923] text-gray-100">
  <header class="sticky top-0 z-40 bg-[#141923]/95 backdrop-blur-md border-b border-white/10">
    <div class="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between gap-4">
      <a href="/" class="flex items-center gap-3">
        <img src="/static/logo.svg" alt="OyunÇöz Logo" loading="lazy" decoding="async" class="w-10 h-10 rounded-xl bg-[#18212f] p-1 border border-[#88c0a8]/40" />
        <div>
          <span class="font-extrabold text-lg text-white">Oyun<span class="text-[#88c0a8]">Çöz</span></span>
          <span class="block text-[11px] text-gray-400">Oyun Hata Kodları ve FPS Çözümleri</span>
        </div>
      </a>
      <nav aria-label="Üst Hızlı Menü" class="flex items-center gap-2.5 text-xs">
        <a href="/hata-kodlari" class="px-3 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-200 border border-white/10 font-semibold transition">🔎 Tüm Hata Kodları</a>
        <a href="{html.escape(oyun_hub_url)}" class="hidden sm:inline-block px-3 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-[#a3d9c6] border border-white/10 font-semibold transition">{html.escape(oyun)} Rehberleri</a>
      </nav>
    </div>
  </header>

  <main class="max-w-5xl mx-auto px-4 py-8 space-y-7 flex-1 w-full">
    <!-- 1. Breadcrumb (Ana Sayfa › Oyun › Hata Kodu) -->
    <nav aria-label="Breadcrumb" class="text-xs text-gray-400 flex flex-wrap items-center gap-2">
      <a href="/" class="hover:text-[#88c0a8] transition">Ana Sayfa</a>
      <span aria-hidden="true">›</span>
      <a href="{html.escape(oyun_hub_url)}" class="hover:text-[#88c0a8] transition">{html.escape(oyun)}</a>
      <span aria-hidden="true">›</span>
      <span class="text-white font-semibold" aria-current="page">{html.escape(hata_kodu)}</span>
    </nav>

    <article class="space-y-7">
      <!-- 2. H1 ve 3. Kısa Özet (Hatanın Anlamı, 2-3 Cümle) -->
      <section class="rounded-2xl p-6 sm:p-8 bg-gradient-to-br from-[#1d2534] to-[#141923] border border-white/15 space-y-4 shadow-xl">
        <div class="flex flex-wrap items-center gap-2 text-xs">
          <span class="px-3 py-1 rounded-full font-bold bg-[#5e9c88]/20 text-[#a3d9c6] border border-[#88c0a8]/30">{html.escape(oyun)}</span>
          <span class="px-3 py-1 rounded-full font-mono font-bold bg-white/10 text-amber-200 border border-white/15">Hata Kodu: {html.escape(hata_kodu)}</span>
          <span class="editor-verified-badge px-3 py-1 rounded-full bg-emerald-500/15 text-emerald-200 border border-emerald-400/30 font-semibold">✓ Editör kontrolünden geçti</span>
        </div>

        <h1 class="text-xl sm:text-3xl font-extrabold text-white leading-tight">{html.escape(h1_raw)}</h1>

        <p id="hata-anlami" class="text-xs sm:text-sm text-gray-200 leading-relaxed">
          {html.escape(kisa_aciklama_raw)}
        </p>
      </section>

      <!-- 4. Bu Hatanın Nedenleri -->
      <section id="hata-nedenleri" class="bg-[#18202c] border border-white/10 rounded-2xl p-6 space-y-3">
        <h2 class="text-base sm:text-lg font-extrabold text-white">⚙️ Bu Hatanın Nedenleri</h2>
        <ul class="list-disc pl-5 text-xs sm:text-sm text-gray-300 space-y-2">
{nedenler_html}
        </ul>
      </section>

      <!-- 5. Adım Adım Çözüm -->
      <section id="cozum-adimlari" class="space-y-4">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <h2 class="text-base sm:text-lg font-extrabold text-white">🛠️ Adım Adım Çözüm</h2>
          <span class="text-[11px] px-2.5 py-1 rounded-lg bg-amber-500/15 text-amber-200 border border-amber-400/30">
            🛡️ İşlem öncesi Sistem Geri Yükleme Noktası oluşturun: <code>Checkpoint-Computer -Description "OyunCoz_Yedek"</code>
          </span>
        </div>
{steps_html}
      </section>

      <!-- 6. İşe Yaramazsa Bölümü -->
      <section id="ise-yaramazsa" class="bg-[#18202c] border border-sky-400/30 rounded-2xl p-6 space-y-3">
        <h2 class="text-base sm:text-lg font-extrabold text-sky-200">🧭 İşe Yaramazsa Ne Yapmalısınız?</h2>
        {isle_yaramazsa_inner}
        <div class="pt-1 flex flex-wrap gap-3">
          <a href="/#tabContent-ai-lab" class="px-4 py-2 rounded-xl text-xs font-bold bg-[#5e9c88] hover:bg-[#4e8775] text-white transition">
            🤖 Crash Log (.log) Yükleyip AI ile Özel Teşhis Al →
          </a>
          <a href="/#tabContent-forum" class="px-4 py-2 rounded-xl text-xs font-semibold bg-white/5 hover:bg-white/10 text-gray-200 border border-white/10 transition">
            💬 Oyuncu Forumunda Konu Aç
          </a>
        </div>
      </section>{video_section_html}

      <!-- 8. Resmi Kaynak Linki -->
      <section id="resmi-kaynak" class="bg-[#18202c] border border-white/10 rounded-2xl p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 class="text-sm sm:text-base font-extrabold text-white">🌐 Resmi Destek ve Dokümantasyon Kaynağı</h2>
          <p class="text-xs text-gray-400 mt-0.5">Yayıncı ve geliştirici ekibin güncel destek dokümanını resmi kaynağından inceleyebilirsiniz.</p>
        </div>
{resmi_link_el}
      </section>

      <!-- 9. Sıkça Sorulan Sorular (SSS) -->
      <section id="sss" class="space-y-3">
        <h2 class="text-base sm:text-lg font-extrabold text-white">❓ Sıkça Sorulan Sorular (SSS)</h2>
{sss_html}
      </section>

      <!-- 10. İlgili Hatalar (İç Linkler) -->
      <section id="ilgili-hatalar" class="bg-[#18202c] border border-white/10 rounded-2xl p-6 space-y-4">
        <div class="flex items-center justify-between">
          <h2 class="text-base sm:text-lg font-extrabold text-white">🔗 İlgili Hatalar</h2>
          <a href="/hata-kodlari" class="text-xs font-semibold text-[#88c0a8] hover:underline">Tüm Hata Kodları →</a>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
{ilgili_html}
        </div>
      </section>

      <!-- 11. Yazar Kutusu, Son Güncelleme ve Test Edilen Sürüm -->
      <section aria-label="Yazar ve Sürüm Bilgisi" class="stage2-author-box p-5 rounded-2xl bg-[#151c27] border border-white/10 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-[#5e9c88]/20 border border-[#88c0a8]/40 text-[#a3d9c6] font-extrabold flex items-center justify-center shrink-0">
            OÇ
          </div>
          <div>
            <div class="text-white font-bold">
              Yazar: <a href="/hakkimizda.html" class="text-[#88c0a8] hover:underline">{html.escape(yazar_raw)}</a>
            </div>
            <div class="text-[11px] text-gray-400">Sistem &amp; Oyun Arıza Editörleri • Topluluk + Editör Kontrolü</div>
          </div>
        </div>
        <div class="flex flex-wrap items-center gap-2 text-[11px] text-gray-300">
          <span class="px-2.5 py-1 rounded-lg bg-white/5 border border-white/10">
            📅 Son güncelleme: <time datetime="{html.escape(tarih_guncelleme)}" class="font-semibold text-white">{html.escape(tarih_guncelleme_tr)}</time>
          </span>
          <span class="px-2.5 py-1 rounded-lg bg-white/5 border border-white/10">
            🧪 Test edilen sürüm: <strong class="text-[#a3d9c6]">{html.escape(test_edilen_surum)}</strong>
          </span>
        </div>
      </section>

      <!-- 12. Bu çözüm işe yaradı mı? Evet / Hayır Butonu -->
      <section id="stage2PageVoteSection" class="bg-[#18202c] border border-white/15 rounded-2xl p-5 space-y-3 shadow-lg">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div class="space-y-1">
            <h2 class="text-sm sm:text-base font-extrabold text-white">Bu çözüm işe yaradı mı?</h2>
            <p class="text-xs text-gray-400">Geri bildiriminiz veritabanına kaydedilir (istemci başına tek oy). Yeterli oy (20+) biriktiğinde gerçek işe yarama oranı gösterilir.</p>
          </div>
          <div class="flex flex-wrap items-center gap-2.5">
            <button
              type="button"
              id="staticVoteUpBtn"
              onclick="submitStaticPageVote({issue_id}, 'up')"
              class="px-4 py-2 rounded-xl border border-white/15 bg-white/5 hover:bg-[#5e9c88]/25 text-xs font-bold text-white flex items-center gap-1.5 transition"
            >
              <span>👍 Evet</span>
              <span id="staticVoteUpCount" class="hidden"></span>
            </button>
            <button
              type="button"
              id="staticVoteDownBtn"
              onclick="submitStaticPageVote({issue_id}, 'down')"
              class="px-4 py-2 rounded-xl border border-white/15 bg-white/5 hover:bg-red-500/20 text-xs font-bold text-gray-200 flex items-center gap-1.5 transition"
            >
              <span>👎 Hayır</span>
              <span id="staticVoteDownCount" class="hidden"></span>
            </button>
            <span id="staticVoteRateBadge" class="hidden text-xs font-bold px-3 py-1.5 rounded-xl bg-[#5e9c88]/15 text-[#a3d9c6] border border-[#5e9c88]/30"></span>
          </div>
        </div>
        <p id="staticVoteFeedbackMsg" class="hidden text-xs text-[#88c0a8] font-semibold"></p>
      </section>
      <script>
        function copyTemplateCmd(btn) {{
          var c = btn.getAttribute('data-cmd') || '';
          if (c && navigator.clipboard) {{
            navigator.clipboard.writeText(c).then(function() {{
              btn.textContent = '✓ Kopyalandı';
              setTimeout(function() {{ btn.textContent = '📋 Kopyala'; }}, 1800);
            }});
          }}
        }}
        (function() {{
          function getClientId() {{
            try {{
              var k = 'oyuncoz_client_id';
              var v = localStorage.getItem(k);
              if (!v) {{
                v = 'cid_' + Math.random().toString(36).slice(2) + Date.now().toString(36);
                localStorage.setItem(k, v);
              }}
              return v;
            }} catch (e) {{
              return 'cid_anon';
            }}
          }}
          function updateVoteUI(data) {{
            if (!data) return;
            var upCnt = Number(data.helpful_votes || 0);
            var downCnt = Number(data.unhelpful_votes || 0);
            var total = Number(data.total_votes || (upCnt + downCnt));
            var showRate = Boolean(data.show_success_rate && total >= 20 && data.success_rate != null);
            var upEl = document.getElementById('staticVoteUpCount');
            var downEl = document.getElementById('staticVoteDownCount');
            var rateEl = document.getElementById('staticVoteRateBadge');
            if (upEl) {{
              upEl.textContent = upCnt > 0 ? '(' + upCnt + ')' : '';
              upEl.classList.toggle('hidden', upCnt === 0);
            }}
            if (downEl) {{
              downEl.textContent = downCnt > 0 ? '(' + downCnt + ')' : '';
              downEl.classList.toggle('hidden', downCnt === 0);
            }}
            if (rateEl) {{
              rateEl.textContent = showRate ? ('✓ İşe yarama oranı: %' + data.success_rate + ' (' + total + ' Oy)') : '';
              rateEl.classList.toggle('hidden', !showRate);
            }}
          }}
          window.submitStaticPageVote = function(issueId, voteType) {{
            fetch('/api/issues/' + issueId + '/vote', {{
              method: 'POST',
              headers: {{ 'Content-Type': 'application/json', 'X-Client-Id': getClientId() }},
              body: JSON.stringify({{ vote_type: voteType, hardware_tag: 'Web' }})
            }}).then(function(r) {{ return r.ok ? r.json() : null; }}).then(function(d) {{
              if (!d) return;
              updateVoteUI(d);
              var msg = document.getElementById('staticVoteFeedbackMsg');
              if (msg) {{
                msg.classList.remove('hidden');
                msg.textContent = d.user_vote === 'up'
                  ? '👍 Geri bildiriminiz (Evet) kaydedildi. Teşekkürler!'
                  : (d.user_vote === 'down' ? '👎 Geri bildiriminiz (Hayır) kaydedildi.' : 'Oyunuz geri alındı.');
              }}
            }}).catch(function() {{}});
          }};
          fetch('/api/issues', {{ headers: {{ 'X-Client-Id': getClientId() }} }})
            .then(function(r) {{ return r.ok ? r.json() : []; }})
            .then(function(list) {{
              if (!Array.isArray(list)) return;
              var found = list.find(function(x) {{ return Number(x.id) === {issue_id}; }});
              if (found) updateVoteUI(found);
            }}).catch(function() {{}});
        }})();
      </script>
    </article>
  </main>

  <footer class="border-t border-white/10 bg-[#11161f] py-6 text-xs text-gray-400 mt-10">
    <div class="max-w-5xl mx-auto px-4 flex flex-col lg:flex-row items-center justify-between gap-3">
      <div>© 2026 <strong>OyunÇöz (oyuncoz.com)</strong> — Oyun Hata Kodları ve FPS Çözüm Rehberi.</div>
      <div class="flex flex-wrap items-center justify-center gap-2.5 text-[11px]">
        <a href="/hata-kodlari" class="hover:text-[#a3d9c6] transition">Hata Kodları Dizini</a>
        <span>•</span>
        <a href="/hakkimizda.html" class="hover:text-[#a3d9c6] transition">Hakkımızda</a>
        <span>•</span>
        <a href="/iletisim.html" class="hover:text-[#a3d9c6] transition">İletişim</a>
        <span>•</span>
        <a href="/kvkk-aydinlatma-metni.html" class="hover:text-[#a3d9c6] transition">KVKK Aydınlatma Metni</a>
        <span>•</span>
        <a href="/gizlilik-ve-cerez-politikasi.html" class="hover:text-[#a3d9c6] transition">Gizlilik ve Çerez Politikası</a>
        <span>•</span>
        <a href="/kullanim-kosullari.html" class="hover:text-[#a3d9c6] transition">Kullanım Koşulları</a>
        <span>•</span>
        <a href="/telif-ve-sorumluluk-reddi.html" class="hover:text-[#a3d9c6] transition">Telif ve Sorumluluk Reddi</a>
        <span>•</span>
        <a href="/sitemap.xml" class="hover:text-gray-200 transition">Site Haritası</a>
      </div>
    </div>
  </footer>
</body>
</html>
"""
    return html_out, warnings


def build_all_from_json(json_path: str = DATA_FILE) -> Tuple[int, List[str]]:
    """
    Reads data/hata_kodlari.json, validates and builds all pages defined in 'pages'.
    Writes each page to <ROOT_DIR>/<slug>/index.html.
    """
    if not os.path.isfile(json_path):
        raise FileNotFoundError(f"Veri dosyası bulunamadı: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    pages = payload.get("pages") or []
    all_warnings: List[str] = []
    built_count = 0

    for rec in pages:
        html_content, warnings = render_error_code_page(rec)
        for w in warnings:
            print(w)
            all_warnings.append(w)

        slug = str(rec["slug"]).strip("/")
        target_dir = os.path.join(ROOT_DIR, *slug.split("/"))
        os.makedirs(target_dir, exist_ok=True)
        out_file = os.path.join(target_dir, "index.html")
        with open(out_file, "w", encoding="utf-8") as wf:
            wf.write(html_content)
        built_count += 1

    return built_count, all_warnings


if __name__ == "__main__":
    cnt, warns = build_all_from_json()
    print(f"[error_page_builder] {cnt} hata kodu sayfası derlendi ({len(warns)} uyarı).")
