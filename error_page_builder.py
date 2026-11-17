# -*- coding: utf-8 -*-
"""
AŞAMA 1 & AŞAMA 4: Yeniden Kullanılabilir Hata Kodu Sayfa Şablonu ve Üretim Motoru (error_page_builder.py)
Veri Kaynağı: data/hata_kodlari.json
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

GAME_MONOGRAM_CODES = {
    "League of Legends": "LoL",
    "Valorant": "VAL",
    "Counter-Strike 2": "CS2",
    "GTA V": "GTA",
    "FiveM": "FVM",
    "Red Dead Redemption 2": "RDR2",
    "Mount & Blade II: Bannerlord": "M&B2",
    "EA Sports FC 25": "FC25",
    "Black Myth: Wukong": "WKG",
    "Minecraft": "MC",
}

LUCIDE_SVG = {
    "alert-triangle": '<svg class="w-4 h-4 shrink-0 inline-block" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>',
    "check-circle": '<svg class="w-4 h-4 shrink-0 inline-block" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/></svg>',
    "copy": '<svg class="w-3.5 h-3.5 shrink-0 inline-block" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>',
    "shield": '<svg class="w-4 h-4 shrink-0 inline-block" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/></svg>',
    "external-link": '<svg class="w-4 h-4 shrink-0 inline-block" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/></svg>',
    "chevron-down": '<svg class="w-4 h-4 shrink-0 inline-block text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>',
    "terminal": '<svg class="w-4 h-4 shrink-0 inline-block" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="4 17 10 11 4 5"/><line x1="12" x2="20" y1="19" y2="19"/></svg>',
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
    Stage 4.2 & 4.9: Renders the step image ONLY if gorsel_yolu is provided and exists on disk.
    If gorsel_yolu is empty, renders NOTHING (no empty placeholder box!).
    """
    img_path = str(step.get("gorsel_yolu") or "").strip()
    if not img_path:
        return ""
    alt_text = html.escape(
        str(step.get("alt_metin") or f"{game_name} {error_code} Adım {idx} ekran görüntüsü").strip()
    )
    rel_disk = img_path.lstrip("/")
    if not os.path.isfile(os.path.join(ROOT_DIR, rel_disk)):
        return ""

    return f"""
          <figure class="step-screenshot-slot rounded-xl overflow-hidden border border-white/10 bg-[#121722] p-3 space-y-2 aspect-video">
            <img
              src="{html.escape(img_path)}"
              alt="{alt_text}"
              loading="lazy"
              decoding="async"
              width="720"
              height="405"
              class="w-full h-full object-cover rounded-lg border border-white/10"
            />
            <figcaption class="text-xs text-gray-400">{alt_text}</figcaption>
          </figure>"""


def render_error_code_page(record: Dict[str, Any]) -> Tuple[str, List[str]]:
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
    editor_verified = record.get("editor_verified", True)

    # JSON-LD: ONLY TechArticle and BreadcrumbList
    schema_obj = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BreadcrumbList",
                "@id": f"{canonical_url}#breadcrumb",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Ana Sayfa", "item": "https://oyuncoz.com/"},
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": oyun,
                        "item": f"https://oyuncoz.com{oyun_hub_url}" if oyun_hub_url.startswith("/") else oyun_hub_url,
                    },
                    {"@type": "ListItem", "position": 3, "name": hata_kodu, "item": canonical_url},
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
                "mainEntityOfPage": {"@type": "WebPage", "@id": canonical_url},
                "author": {"@type": "Organization", "name": yazar_raw, "url": "https://oyuncoz.com/hakkimizda.html"},
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

    # Stage 6.2: Content status badge
    if editor_verified:
        status_badge_html = f'<span class="editor-verified-badge oc-badge oc-badge-success font-semibold">{LUCIDE_SVG["check-circle"]}<span>Editör kontrolünden geçti</span></span>'
    else:
        status_badge_html = f'<span class="ai-generated-badge oc-badge oc-badge-warning font-semibold">{LUCIDE_SVG["alert-triangle"]}<span>Yapay zeka ile üretildi, uygulamadan önce kontrol edin</span></span>'

    # Stage 4.1: "Hızlı çözüm" box right under the summary (Above the fold)
    steps_list = record.get("cozum_adimlari") or []
    total_steps = len(steps_list)
    hizli = record.get("hizli_cozum")
    if not hizli and steps_list:
        hizli = {
            "baslik": f"En Olası İlk Adım: {steps_list[0].get('baslik', '')}",
            "aciklama": steps_list[0].get("aciklama", ""),
            "komut": steps_list[0].get("komut", ""),
        }

    quick_fix_html = ""
    if hizli and (hizli.get("baslik") or hizli.get("aciklama")):
        qf_title = html.escape(str(hizli.get("baslik") or "Hızlı Çözüm"))
        qf_desc = html.escape(str(hizli.get("aciklama") or ""))
        qf_cmd = str(hizli.get("komut") or "").strip()
        qf_cmd_html = ""
        if qf_cmd:
            qf_cmd_esc = html.escape(qf_cmd)
            qf_cmd_html = f"""
          <div class="oc-codeblock flex items-center justify-between gap-3 mt-2">
            <code class="text-xs sm:text-sm font-mono text-[#a3d9c6] overflow-x-auto select-all">{qf_cmd_esc}</code>
            <button type="button" data-cmd="{qf_cmd_esc}" onclick="copyTemplateCmd(this)" class="oc-btn oc-btn-secondary !min-h-[36px] !py-1 !px-3 text-xs shrink-0">{LUCIDE_SVG['copy']}<span>Kopyala</span></button>
          </div>"""
        quick_fix_html = f"""
        <div id="hizli-cozum" class="p-4 sm:p-5 rounded-xl bg-[#162228] border border-[#5e9c88]/45 space-y-2">
          <div class="flex items-center justify-between gap-2">
            <span class="oc-badge oc-badge-accent font-extrabold uppercase tracking-wider">Hızlı Çözüm (İlk Adım)</span>
            <a href="#cozum-adimlari" class="text-xs font-bold text-[#88c0a8] hover:underline">Tüm adımlara in ({total_steps} adım) ↓</a>
          </div>
          <h2 class="text-sm sm:text-base font-extrabold text-white">{qf_title}</h2>
          <p class="text-xs sm:text-sm text-gray-200 leading-relaxed">{qf_desc}</p>{qf_cmd_html}
        </div>"""

    # Stage 4.1 & 6.1: Video (only when video_embed_url is non-empty, placed right below summary/quick-fix)
    video_embed_url = normalize_video_embed_url(str(record.get("video_embed_url") or ""))
    video_section_html = ""
    if video_embed_url:
        video_section_html = f"""
        <div id="video-rehber" class="pt-2 space-y-2">
          <div class="text-xs font-bold uppercase tracking-wider text-[#88c0a8]">Video Çözüm Rehberi</div>
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
        </div>"""

    # 4. "Bu hatanın nedenleri" (only if non-empty)
    nedenler_list = record.get("nedenler") or []
    nedenler_section_html = ""
    if nedenler_list:
        nedenler_items = "\n".join(
            f'          <li class="leading-relaxed">{html.escape(str(n))}</li>' for n in nedenler_list
        )
        nedenler_section_html = f"""
      <!-- 4. Bu Hatanın Nedenleri -->
      <section id="hata-nedenleri" class="oc-card p-6 space-y-3">
        <h2 class="text-base sm:text-lg font-extrabold text-white">Bu Hatanın Nedenleri</h2>
        <ul class="list-disc pl-5 text-xs sm:text-sm text-gray-300 space-y-2">
{nedenler_items}
        </ul>
      </section>"""

    # Stage 4.5: "Hangisi senin durumun?" Scenario Tabs (ONLY if 'senaryolar' is defined in data)
    scenarios = record.get("senaryolar") or []
    scenarios_html = ""
    if scenarios:
        tab_btns = []
        tab_panels = []
        for s_idx, sc in enumerate(scenarios):
            s_id = html.escape(str(sc.get("id") or f"sc-{s_idx}"))
            s_label = html.escape(str(sc.get("etiket") or f"Senaryo {s_idx+1}"))
            s_title = html.escape(str(sc.get("baslik") or s_label))
            s_desc = html.escape(str(sc.get("aciklama") or ""))
            is_first = s_idx == 0
            active_cls = "active" if is_first else ""
            aria_sel = "true" if is_first else "false"
            hidden_cls = "" if is_first else "hidden"
            tab_btns.append(
                f'<button type="button" role="tab" aria-selected="{aria_sel}" data-scenario-target="scenarioPanel-{s_id}" onclick="switchPageScenario(this, \'scenarioPanel-{s_id}\')" class="oc-tab-btn {active_cls}">{s_label}</button>'
            )
            tab_panels.append(
                f'<div id="scenarioPanel-{s_id}" role="tabpanel" class="scenario-panel {hidden_cls} p-4 rounded-xl bg-[#141923] border border-white/10 space-y-1.5">'
                f'<h3 class="text-sm font-bold text-[#a3d9c6]">{s_title}</h3>'
                f'<p class="text-xs sm:text-sm text-gray-200 leading-relaxed">{s_desc}</p>'
                f'</div>'
            )
        scenarios_html = f"""
        <div id="senaryo-secici" class="oc-card p-5 space-y-3">
          <div class="text-xs sm:text-sm font-bold text-white">Hangisi senin durumun? (Sistemine Göre Seç)</div>
          <div class="oc-tabs" role="tablist" aria-label="Sistem senaryosu seçimi">
            {"".join(tab_btns)}
          </div>
          <div>
            {"".join(tab_panels)}
          </div>
        </div>"""

    # 5. "Adım adım çözüm" (Numaralı kartlar + "Bu adımı tamamladım" + İlerleme Göstergesi)
    steps_blocks = []
    for idx, st in enumerate(steps_list, start=1):
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
            <div class="stage2-risky-cmd-note oc-alert oc-alert-warning flex-col space-y-2 text-xs">
              <div class="font-bold text-amber-200 flex items-center gap-1.5">{LUCIDE_SVG['alert-triangle']}<span>Komut Güvenlik Bilgisi:</span></div>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-2.5 text-xs leading-relaxed w-full">
                <div class="p-2.5 rounded-lg bg-white/5 border border-white/5">
                  <strong class="text-[#88c0a8] block mb-0.5">Ne yapar?</strong>
                  <span class="text-gray-200">{ne_yapar}</span>
                </div>
                <div class="p-2.5 rounded-lg bg-white/5 border border-white/5">
                  <strong class="text-amber-300 block mb-0.5">Risk:</strong>
                  <span class="text-gray-200">{risk_txt}</span>
                </div>
                <div class="p-2.5 rounded-lg bg-white/5 border border-white/5">
                  <strong class="text-sky-300 block mb-0.5">Geri alma:</strong>
                  <span class="text-gray-200">{geri_alma}</span>
                </div>
              </div>
            </div>"""

            cmd_html = f"""
          <div class="space-y-2.5">
            <div class="flex items-center justify-between text-xs text-gray-400 px-1">
              <span class="inline-flex items-center gap-1.5 font-mono text-[#a3d9c6]">{LUCIDE_SVG['terminal']}<span>Komut İstemi / PowerShell</span></span>
              <span class="oc-badge oc-badge-warning">Yönetici olarak çalıştırın</span>
            </div>
            <div class="oc-codeblock flex items-center justify-between gap-3">
              <code class="text-xs sm:text-sm font-mono text-[#a3d9c6] overflow-x-auto select-all">{cmd_esc}</code>
              <button type="button" data-cmd="{cmd_esc}" onclick="copyTemplateCmd(this)" class="oc-btn oc-btn-secondary !min-h-[38px] !py-1.5 !px-3 text-xs shrink-0">{LUCIDE_SVG['copy']}<span>Kopyala</span></button>
            </div>{risk_box_html}
          </div>"""

        mb_html = ""
        if motherboard_tabs:
            mb_cards = []
            for mb in motherboard_tabs:
                brand = html.escape(str(mb.get("marka") or ""))
                yol = html.escape(str(mb.get("adimlar") or ""))
                mb_cards.append(f"""
              <div class="oc-card p-3.5 space-y-1.5">
                <div class="font-bold text-xs text-[#a3d9c6]">{brand} Anakart BIOS Adımları</div>
                <p class="text-xs text-gray-300 leading-relaxed">{yol}</p>
              </div>""")
            mb_html = f"""
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
{"".join(mb_cards)}
          </div>"""

        img_slot_html = render_step_image_slot(st, idx, oyun, hata_kodu)

        steps_blocks.append(f"""
        <div id="adim-{idx}" class="step-card oc-card p-5 space-y-3.5 transition">
          <div class="flex items-start justify-between gap-3">
            <div class="flex items-center gap-3">
              <span class="oc-badge oc-badge-accent font-extrabold shrink-0">Adım {idx}</span>
              <h3 class="text-sm sm:text-base font-bold text-white">{st_title}</h3>
            </div>
          </div>
          <p class="oc-step-desc text-xs sm:text-sm text-gray-300 leading-relaxed">{st_desc}</p>{cmd_html}{mb_html}{img_slot_html}
          <div class="pt-2 border-t border-white/5 flex items-center justify-between">
            <label class="inline-flex items-center gap-2.5 cursor-pointer min-h-[44px] text-xs sm:text-sm font-semibold text-gray-300 hover:text-white select-none">
              <input type="checkbox" class="step-check-input w-4 h-4 rounded accent-[#5e9c88]" onchange="toggleStepCompleted(this, {total_steps})" />
              <span>Bu adımı tamamladım</span>
            </label>
            <span class="step-done-pill hidden oc-badge oc-badge-success">Tamamlandı</span>
          </div>
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

    # 8. Resmi kaynak linki (Stage 4.9: Veri alanı boşsa bölümü hiç gösterme!)
    resmi_url = str(record.get("resmi_kaynak_url") or "").strip()
    resmi_etiket = html.escape(str(record.get("resmi_kaynak_baslik") or f"{oyun} Resmi Destek Sayfası"))
    resmi_section_html = ""
    if resmi_url:
        resmi_section_html = f"""
      <!-- Resmi Kaynak Linki -->
      <section id="resmi-kaynak" class="oc-card p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 class="text-sm sm:text-base font-extrabold text-white">Resmi Destek ve Dokümantasyon Kaynağı</h2>
          <p class="text-xs text-gray-400 mt-0.5">Yayıncı ve geliştirici ekibin güncel destek dokümanını resmi kaynağından inceleyebilirsiniz.</p>
        </div>
        <a href="{html.escape(resmi_url)}" target="_blank" rel="noopener noreferrer" class="oc-btn oc-btn-secondary text-xs shrink-0">
          {LUCIDE_SVG['external-link']}<span>{resmi_etiket}</span>
        </a>
      </section>"""

    # 9. SSS (Sıkça Sorulan Sorular - Accordion bileşeni ile)
    sss_list = record.get("sss") or []
    sss_section_html = ""
    if sss_list:
        sss_blocks = []
        for idx_q, qa in enumerate(sss_list, start=1):
            q_txt = html.escape(str(qa.get("soru") or ""))
            a_txt = html.escape(str(qa.get("cevap") or ""))
            open_attr = " open" if idx_q == 1 else ""
            sss_blocks.append(f"""
        <details class="oc-accordion"{open_attr}>
          <summary>
            <h3 class="text-xs sm:text-sm font-bold text-white">{q_txt}</h3>
            {LUCIDE_SVG['chevron-down']}
          </summary>
          <div class="oc-accordion-body">
            <p class="text-xs sm:text-sm text-gray-300 leading-relaxed">{a_txt}</p>
          </div>
        </details>""")
        sss_section_html = f"""
      <!-- 9. Sıkça Sorulan Sorular (SSS) -->
      <section id="sss" class="space-y-3">
        <h2 class="text-base sm:text-lg font-extrabold text-white">Sıkça Sorulan Sorular (SSS)</h2>
{"".join(sss_blocks)}
      </section>"""

    # 10. "İlgili hatalar" (iç linkler)
    ilgili_list = record.get("ilgili_hatalar") or []
    ilgili_section_html = ""
    if ilgili_list:
        ilgili_blocks = []
        for rel_item in ilgili_list:
            r_url = html.escape(str(rel_item.get("url") or "/hata-kodlari"))
            r_game = html.escape(str(rel_item.get("oyun") or oyun))
            r_code = html.escape(str(rel_item.get("hata_kodu") or ""))
            r_title = html.escape(str(rel_item.get("baslik") or ""))
            label_top = f"{r_game} • {r_code}" if r_code else r_game
            ilgili_blocks.append(f"""
          <a href="{r_url}" class="oc-card oc-card-interactive p-3.5 flex items-center justify-between gap-2 text-xs">
            <div>
              <span class="font-mono text-[#a3d9c6] font-bold block">{label_top}</span>
              <span class="text-gray-200 font-semibold">{r_title}</span>
            </div>
            <span class="text-[#88c0a8] font-bold shrink-0">→</span>
          </a>""")
        ilgili_section_html = f"""
      <!-- 10. İlgili Hatalar (İç Linkler) -->
      <section id="ilgili-hatalar" class="oc-card p-6 space-y-4">
        <div class="flex items-center justify-between">
          <h2 class="text-base sm:text-lg font-extrabold text-white">İlgili Hatalar</h2>
          <a href="/hata-kodlari" class="text-xs font-semibold text-[#88c0a8] hover:underline">Tüm Hata Kodları →</a>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
{"".join(ilgili_blocks)}
        </div>
      </section>"""

    # Stage 4.7: Table of Contents ("Bu sayfada" mobile accordion + desktop sticky sidebar on pages with >= 3 steps)
    show_toc = total_steps >= 3
    toc_links = [
        ('<li><a href="#hizli-cozum" class="block py-1 text-gray-300 hover:text-[#88c0a8] transition">Hızlı Çözüm</a></li>' if quick_fix_html else ""),
        ('<li><a href="#hata-nedenleri" class="block py-1 text-gray-300 hover:text-[#88c0a8] transition">Bu Hatanın Nedenleri</a></li>' if nedenler_section_html else ""),
        f'<li><a href="#cozum-adimlari" class="block py-1 text-gray-300 hover:text-[#88c0a8] transition">Adım Adım Çözüm ({total_steps} Adım)</a></li>',
        '<li><a href="#ise-yaramazsa" class="block py-1 text-gray-300 hover:text-[#88c0a8] transition">İşe Yaramazsa</a></li>',
        ('<li><a href="#sss" class="block py-1 text-gray-300 hover:text-[#88c0a8] transition">Sıkça Sorulan Sorular</a></li>' if sss_section_html else ""),
        ('<li><a href="#ilgili-hatalar" class="block py-1 text-gray-300 hover:text-[#88c0a8] transition">İlgili Hatalar</a></li>' if ilgili_section_html else ""),
        '<li><a href="#stage2PageVoteSection" class="block py-1 text-gray-300 hover:text-[#88c0a8] transition">Çözüm Değerlendirme</a></li>',
    ]
    toc_links_html = "\n".join(x for x in toc_links if x)

    mobile_toc_html = ""
    desktop_toc_aside_html = ""
    if show_toc:
        mobile_toc_html = f"""
      <!-- Mobil İçindekiler ("Bu sayfada") -->
      <details class="oc-accordion lg:hidden">
        <summary class="text-xs sm:text-sm font-bold text-white">
          <span>Bu sayfada (İçindekiler)</span>
          {LUCIDE_SVG['chevron-down']}
        </summary>
        <div class="oc-accordion-body">
          <ul class="space-y-1 text-xs">
{toc_links_html}
          </ul>
        </div>
      </details>"""

        desktop_toc_aside_html = f"""
      <!-- Masaüstü Yapışkan İçindekiler Yan Paneli -->
      <aside aria-label="Sayfa İçindekiler" class="hidden lg:block lg:col-span-3">
        <div class="oc-card p-4 sticky top-20 space-y-3 text-xs">
          <div class="font-extrabold uppercase tracking-wider text-[#88c0a8]">Bu Sayfada</div>
          <ul class="space-y-1 border-l border-white/10 pl-3">
{toc_links_html}
          </ul>
          <div class="pt-3 border-t border-white/10 space-y-2">
            <div class="text-[11px] text-gray-400">İlerleme Durumu:</div>
            <div id="sidebarStepProgressText" class="font-bold text-white">0/{total_steps} adım tamamlandı</div>
          </div>
        </div>
      </aside>"""

    monogram_code = html.escape(GAME_MONOGRAM_CODES.get(oyun, oyun[:3].upper()))
    grid_wrapper_open = '<div class="grid grid-cols-1 lg:grid-cols-12 gap-7 items-start"><div class="lg:col-span-9 space-y-7">' if show_toc else '<div class="space-y-7">'
    grid_wrapper_close = f'</div>{desktop_toc_aside_html}</div>' if show_toc else '</div>'

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
    :root{{--accent:#5e9c88;--bg-dark:#141923;--bg-panel:#1b2230;--bg-card:#202838;--text-main:#d8dee9;--text-muted:#9fb0c7}}
    html,body{{background-color:#141923;color:#d8dee9;font-family:'Inter',-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;margin:0;padding:0;line-height:1.65}}
    .text-white{{color:#e6ecf5!important}}
  </style>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/static/styles.css" />
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="/static/ui_components.js" defer></script>
</head>
<body class="min-h-screen flex flex-col bg-[#141923] text-gray-100 pb-20 lg:pb-0">
  <a href="#ana-icerik" class="oc-skip-link">İçeriğe geç</a>
  <header class="sticky top-0 z-40 bg-[#141923]/95 backdrop-blur-md border-b border-white/10">
    <div class="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between gap-4">
      <a href="/" class="flex items-center gap-3">
        <span class="oc-monogram" aria-hidden="true">OÇ</span>
        <div>
          <span class="font-extrabold text-lg text-white">Oyun<span class="text-[#88c0a8]">Çöz</span></span>
          <span class="block text-[11px] text-gray-400">Oyun Hata Kodları ve FPS Çözümleri</span>
        </div>
      </a>
      <nav aria-label="Üst Gezinme Menüsü" class="flex items-center gap-2 text-xs">
        <a href="/hata-kodlari" class="oc-btn oc-btn-secondary !min-h-[40px] !py-1.5 !px-3 text-xs">Hata Kodları</a>
        <a href="{html.escape(oyun_hub_url)}" class="hidden sm:inline-flex oc-btn oc-btn-ghost !min-h-[40px] !py-1.5 !px-3 text-xs text-[#a3d9c6]">{html.escape(oyun)}</a>
        <a href="/#tabContent-ai-lab" class="hidden md:inline-flex oc-btn oc-btn-ghost !min-h-[40px] !py-1.5 !px-3 text-xs">AI Çözümleyici</a>
        <a href="/#tabContent-forum" class="hidden md:inline-flex oc-btn oc-btn-ghost !min-h-[40px] !py-1.5 !px-3 text-xs">Forum</a>
      </nav>
    </div>
  </header>

  <main id="ana-icerik" class="max-w-6xl mx-auto px-4 py-7 space-y-6 flex-1 w-full">
    <!-- 1. Breadcrumb (Ana Sayfa › Oyun › Hata Kodu) -->
    <nav aria-label="Breadcrumb" class="oc-breadcrumb">
      <a href="/" class="hover:text-[#88c0a8] transition">Ana Sayfa</a>
      <span aria-hidden="true">›</span>
      <a href="{html.escape(oyun_hub_url)}" class="hover:text-[#88c0a8] transition">{html.escape(oyun)}</a>
      <span aria-hidden="true">›</span>
      <span class="text-white font-semibold" aria-current="page">{html.escape(hata_kodu)}</span>
    </nav>

    {grid_wrapper_open}
    <article class="space-y-7 oc-prose">
      <!-- 2. Üst Bölüm (Kaydırmadan Görünen Kısım: Rozetler, H1, Bu Hata Ne Anlama Geliyor, Hızlı Çözüm, Video) -->
      <section class="oc-card p-6 sm:p-8 space-y-4">
        <div class="flex flex-wrap items-center gap-2.5 text-xs">
          <span class="oc-monogram oc-monogram-sm" aria-hidden="true">{monogram_code}</span>
          <span class="oc-badge oc-badge-accent font-bold">{html.escape(oyun)}</span>
          <span class="oc-badge font-mono font-bold">Hata Kodu: {html.escape(hata_kodu)}</span>
          {status_badge_html}
        </div>

        <h1 class="text-xl sm:text-3xl font-extrabold text-white leading-tight">{html.escape(h1_raw)}</h1>

        <div class="space-y-1">
          <div class="text-xs font-bold uppercase tracking-wider text-[#88c0a8]">Bu hata ne anlama geliyor?</div>
          <p id="hata-anlami" class="text-sm sm:text-base text-gray-200 leading-relaxed">
            {html.escape(kisa_aciklama_raw)}
          </p>
        </div>

{quick_fix_html}{video_section_html}
      </section>

{mobile_toc_html}{nedenler_section_html}{scenarios_html}

      <!-- 5. Adım Adım Çözüm (İlerleme Göstergesi + Geri Yükleme Uyarı Kutusu + Numaralı Kartlar) -->
      <section id="cozum-adimlari" class="space-y-4">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <h2 class="text-base sm:text-lg font-extrabold text-white">Adım Adım Çözüm</h2>
          <span id="stepProgressBadge" class="oc-badge oc-badge-accent font-bold">İlerleme: 0/{total_steps} adım</span>
        </div>

        <!-- Sarı Uyarı Kutusu (Alert): Sistem ayarı değiştiren adımlardan önce Geri yükleme noktası uyarısı -->
        <div class="oc-alert oc-alert-warning text-xs sm:text-sm">
          {LUCIDE_SVG['shield']}
          <div>
            <strong class="font-bold">Geri yükleme noktası oluşturun:</strong> Sistem veya servis ayarlarını değiştirmeden önce Windows'ta bir Sistem Geri Yükleme Noktası (<code>Checkpoint-Computer -Description "OyunCoz_Yedek"</code>) oluşturmanız önerilir.
          </div>
        </div>
{steps_html}
      </section>

      <!-- 6. İşe Yaramazsa Bölümü -->
      <section id="ise-yaramazsa" class="oc-card p-6 space-y-3">
        <h2 class="text-base sm:text-lg font-extrabold text-white">İşe Yaramazsa Ne Yapmalısınız?</h2>
        {isle_yaramazsa_inner}
        <div class="pt-2 flex flex-wrap gap-3">
          <a href="/#tabContent-ai-lab" class="oc-btn oc-btn-primary text-xs sm:text-sm">
            <span>AI ile analiz et</span>
          </a>
          <a href="/#tabContent-forum" class="oc-btn oc-btn-secondary text-xs sm:text-sm">
            <span>Foruma sor</span>
          </a>
        </div>
      </section>{resmi_section_html}{sss_section_html}{ilgili_section_html}

      <!-- 11. Yazar Kutusu, Son Güncelleme ve Test Edilen Sürüm -->
      <section aria-label="Yazar ve Sürüm Bilgisi" class="stage2-author-box oc-card p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
        <div class="flex items-center gap-3">
          <span class="oc-monogram" aria-hidden="true">OÇ</span>
          <div>
            <div class="text-white font-bold">
              Yazar: <a href="/hakkimizda.html" class="text-[#88c0a8] hover:underline">{html.escape(yazar_raw)}</a>
            </div>
            <div class="text-xs text-gray-400">Sistem ve Oyun Arıza Editörleri • <a href="/hakkimizda.html" class="underline hover:text-white">Hakkımızda ve Metodoloji</a></div>
          </div>
        </div>
        <div class="flex flex-wrap items-center gap-2 text-xs text-gray-300">
          <span class="oc-badge">
            Son güncelleme: <time datetime="{html.escape(tarih_guncelleme)}" class="font-semibold text-white">{html.escape(tarih_guncelleme_tr)}</time>
          </span>
          <span class="oc-badge">
            Test edilen sürüm: <strong class="text-[#a3d9c6]">{html.escape(test_edilen_surum)}</strong>
          </span>
        </div>
      </section>

      <!-- 12. Bu çözüm işe yaradı mı? Evet / Hayır Butonu -->
      <section id="stage2PageVoteSection" class="oc-card p-5 space-y-3">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div class="space-y-1">
            <h2 class="text-sm sm:text-base font-extrabold text-white">Bu çözüm işe yaradı mı?</h2>
            <p class="text-xs text-gray-400">Oylar sunucuda tutulur (istemci başına tek oy). 20+ oy biriktiğinde gerçek işe yarama oranı gösterilir.</p>
          </div>
          <div class="flex flex-wrap items-center gap-2.5">
            <button
              type="button"
              id="staticVoteUpBtn"
              onclick="submitStaticPageVote({issue_id}, 'up')"
              class="oc-btn oc-btn-secondary text-xs font-bold"
            >
              <span>Evet</span>
              <span id="staticVoteUpCount" class="hidden"></span>
            </button>
            <button
              type="button"
              id="staticVoteDownBtn"
              onclick="submitStaticPageVote({issue_id}, 'down')"
              class="oc-btn oc-btn-ghost text-xs font-bold"
            >
              <span>Hayır</span>
              <span id="staticVoteDownCount" class="hidden"></span>
            </button>
            <span id="staticVoteRateBadge" class="hidden oc-badge oc-badge-accent font-bold"></span>
          </div>
        </div>
        <p id="staticVoteFeedbackMsg" class="hidden text-xs text-[#88c0a8] font-semibold"></p>
      </section>
    </article>
    {grid_wrapper_close}
  </main>

  <!-- Mobilde Alt Sabit Çubuk (İşe Yaradı & Foruma Sor - İçeriği Örtmez) -->
  <div id="mobileStickyActionBar" class="lg:hidden fixed bottom-0 inset-x-0 z-30 bg-[#141923]/95 backdrop-blur-md border-t border-white/15 px-4 py-2.5 flex items-center justify-between gap-3">
    <button
      type="button"
      onclick="submitStaticPageVote({issue_id}, 'up'); document.getElementById('stage2PageVoteSection')?.scrollIntoView({{behavior:'smooth'}});"
      class="oc-btn oc-btn-primary flex-1 !min-h-[44px] text-xs font-bold"
    >
      <span>İşe yaradı</span>
    </button>
    <a
      href="/#tabContent-forum"
      class="oc-btn oc-btn-secondary flex-1 !min-h-[44px] text-xs font-bold"
    >
      <span>Foruma sor</span>
    </a>
  </div>

  <footer class="border-t border-white/10 bg-[#11161f] py-6 text-xs text-gray-400 mt-10">
    <div class="max-w-6xl mx-auto px-4 flex flex-col lg:flex-row items-center justify-between gap-3">
      <div>© 2026 <strong>OyunÇöz (oyuncoz.com)</strong> — Oyun Hata Kodları ve FPS Çözüm Rehberi.</div>
      <div class="flex flex-wrap items-center justify-center gap-2.5 text-xs">
        <a href="/hata-kodlari" class="hover:text-[#a3d9c6] transition">Hata Kodları</a>
        <span>•</span>
        <a href="/hakkimizda.html" class="hover:text-[#a3d9c6] transition">Hakkımızda</a>
        <span>•</span>
        <a href="/iletisim.html" class="hover:text-[#a3d9c6] transition">İletişim</a>
        <span>•</span>
        <a href="/gizlilik-ve-cerez-politikasi.html" class="hover:text-[#a3d9c6] transition">Gizlilik ve Çerez</a>
        <span>•</span>
        <a href="/kvkk-aydinlatma-metni.html" class="hover:text-[#a3d9c6] transition">KVKK</a>
        <span>•</span>
        <a href="/kullanim-kosullari.html" class="hover:text-[#a3d9c6] transition">Kullanım Koşulları</a>
        <span>•</span>
        <a href="/telif-ve-sorumluluk-reddi.html" class="hover:text-[#a3d9c6] transition">Telif ve Sorumluluk Reddi</a>
        <span>•</span>
        <a href="/sitemap.xml" class="hover:text-gray-200 transition">Site Haritası</a>
      </div>
    </div>
  </footer>

  <script>
    function copyTemplateCmd(btn) {{
      var c = btn.getAttribute('data-cmd') || '';
      if (!c) return;
      var done = function() {{
        var span = btn.querySelector('span');
        if (span) span.textContent = 'Kopyalandı';
        else btn.textContent = 'Kopyalandı';
        setTimeout(function() {{
          if (span) span.textContent = 'Kopyala';
          else btn.textContent = 'Kopyala';
        }}, 1800);
      }};
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(c).then(done).catch(function() {{ fallbackCopy(c, done); }});
      }} else {{
        fallbackCopy(c, done);
      }}
    }}
    function fallbackCopy(text, cb) {{
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      try {{ document.execCommand('copy'); cb(); }} catch (e) {{}}
      document.body.removeChild(ta);
    }}
    function toggleStepCompleted(checkbox, totalSteps) {{
      var card = checkbox.closest('.step-card');
      var pill = card ? card.querySelector('.step-done-pill') : null;
      if (card) {{
        card.classList.toggle('border-[#5e9c88]', checkbox.checked);
      }}
      if (pill) {{
        pill.classList.toggle('hidden', !checkbox.checked);
      }}
      var allChecked = document.querySelectorAll('.step-check-input:checked').length;
      var badge = document.getElementById('stepProgressBadge');
      var sideTxt = document.getElementById('sidebarStepProgressText');
      if (badge) badge.textContent = 'İlerleme: ' + allChecked + '/' + totalSteps + ' adım';
      if (sideTxt) sideTxt.textContent = allChecked + '/' + totalSteps + ' adım tamamlandı';
    }}
    function switchPageScenario(btn, targetId) {{
      var parent = btn.closest('#senaryo-secici');
      if (!parent) return;
      parent.querySelectorAll('[role="tab"]').forEach(function(b) {{
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      }});
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');
      parent.querySelectorAll('.scenario-panel').forEach(function(p) {{
        p.classList.toggle('hidden', p.id !== targetId);
      }});
    }}
    (function() {{
      var pageSessionClientId = 'cid_' + Math.random().toString(36).slice(2) + Date.now().toString(36);
      function getConsentSafeClientId() {{
        try {{
          var consentRaw = localStorage.getItem('oyuncoz_cookie_consent');
          if (consentRaw) {{
            var k = 'oyuncoz_client_id';
            var v = localStorage.getItem(k);
            if (!v) {{
              v = pageSessionClientId;
              localStorage.setItem(k, v);
            }}
            return v;
          }}
        }} catch (e) {{}}
        return pageSessionClientId;
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
          rateEl.textContent = showRate ? ('İşe yarama oranı: %' + data.success_rate + ' (' + total + ' Oy)') : '';
          rateEl.classList.toggle('hidden', !showRate);
        }}
      }}
      window.submitStaticPageVote = function(issueId, voteType) {{
        fetch('/api/issues/' + issueId + '/vote', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json', 'X-Client-Id': getConsentSafeClientId() }},
          body: JSON.stringify({{ vote_type: voteType, hardware_tag: 'Web' }})
        }}).then(function(r) {{ return r.ok ? r.json() : null; }}).then(function(d) {{
          if (!d) return;
          updateVoteUI(d);
          var msg = document.getElementById('staticVoteFeedbackMsg');
          if (msg) {{
            msg.classList.remove('hidden');
            msg.textContent = d.user_vote === 'up'
              ? 'Geri bildiriminiz (Evet) kaydedildi. Teşekkürler!'
              : (d.user_vote === 'down' ? 'Geri bildiriminiz (Hayır) kaydedildi.' : 'Oyunuz geri alındı.');
          }}
        }}).catch(function() {{}});
      }};
      fetch('/api/issues', {{ headers: {{ 'X-Client-Id': getConsentSafeClientId() }} }})
        .then(function(r) {{ return r.ok ? r.json() : []; }})
        .then(function(list) {{
          if (!Array.isArray(list)) return;
          var found = list.find(function(x) {{ return Number(x.id) === {issue_id}; }});
          if (found) updateVoteUI(found);
        }}).catch(function() {{}});
    }})();
  </script>
</body>
</html>
"""
    return html_out, warnings


def build_all_from_json(json_path: str = DATA_FILE) -> Tuple[int, List[str]]:
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
