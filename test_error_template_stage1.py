# -*- coding: utf-8 -*-
import re
import json
from fastapi.testclient import TestClient
import main
import error_page_builder as builder


def test_stage1_template():
    sample_record = {
        "slug": "ornek-oyun/ornek-kod",
        "oyun": "League of Legends",
        "hata_kodu": "VAN 185",
        "varyant_yazimlari": ["vanguard 185", "van 185", "van185", "lol vanguard hatası 185"],
        "title": "LoL Vanguard VAN 185 Hatası Çözümü (Adım Adım)",
        "meta_description": "League of Legends VAN 185 bağlantı hatası için oturum yenileme, vgc servis kontrolü ve ağ sıfırlama adımlarını içeren teknik çözüm rehberi.",
        "h1": "League of Legends VAN 185 Hatası Nasıl Çözülür?",
        "kisa_aciklama": "League of Legends VAN 185 hatası, Riot İstemcisi ile Vanguard doğrulama servisi arasındaki oturum sinyalinin kesildiğini gösterir.",
        "nedenler": [
            "Arka planda açık kalan RiotClientServices.exe süreçlerinin oturum anahtarını kilitlemesi.",
            "Yerel ağ veya DNS önbelleğinde oluşan kısa süreli paket kayıpları."
        ],
        "cozum_adimlari": [
            {
                "baslik": "Açık Riot Süreçlerini Kapatın",
                "aciklama": "Görev Yöneticisi üzerinden tüm Riot süreçlerini sonlandırın.",
                "komut": "taskkill /F /IM RiotClientServices.exe",
                "komut_notu": {
                    "ne_yapar": "Asılı kalan Riot İstemcisi süreçlerini kapatır.",
                    "risk": "Açık istemci oturumu kapanır.",
                    "geri_alma": "Riot İstemcisini yeniden başlatmanız yeterlidir."
                },
                "gorsel_yolu": "",
                "alt_metin": "Görev Yöneticisi üzerinde RiotClientServices.exe işlemini sonlandırma adımı"
            }
        ],
        "isle_yaramazsa": "Sorun devam ederse League of Legends.exe uyumluluk ayarlarından tam ekran iyileştirmelerini devre dışı bırakın.",
        "resmi_kaynak_url": "",
        "sss": [
            {
                "soru": "VAN 185 hatası neden olur?",
                "cevap": "Riot İstemcisi ile Vanguard servisi arasındaki yerel bağlantının kopmasından kaynaklanır."
            }
        ],
        "ilgili_hatalar": [
            {
                "url": "/lol/van-128",
                "oyun": "League of Legends",
                "hata_kodu": "VAN 128",
                "baslik": "LoL Vanguard VAN 128 Hatası Çözümü"
            }
        ],
        "video_embed_url": "",
        "yazar": "OyunÇöz Teknik Ekibi",
        "tarih_yayin": "2026-03-01",
        "tarih_guncelleme": "2026-11-17",
        "test_edilen_surum": "Windows 10 / 11 (23H2 & 24H2)"
    }

    html_out, warns = builder.render_error_code_page(sample_record)
    assert len(warns) == 0, f"Beklenmeyen uyarılar: {warns}"

    # 1. Single H1 check
    h1_matches = re.findall(r"<h1\b[^>]*>.*?</h1>", html_out, flags=re.S)
    assert len(h1_matches) == 1, f"Sayfada tek H1 olmalı, bulunan: {len(h1_matches)}"

    # 2. Canonical self-reference & no meta keywords
    assert '<link rel="canonical" href="https://oyuncoz.com/ornek-oyun/ornek-kod" />' in html_out
    assert 'name="keywords"' not in html_out.lower()

    # 3. JSON-LD check: TechArticle + BreadcrumbList ONLY (No FAQPage, No HowTo)
    m_json = re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', html_out, flags=re.S)
    assert m_json, "JSON-LD bulunamadı"
    jd = json.loads(m_json.group(1))
    graph_types = [x.get("@type") for x in jd.get("@graph", [])]
    assert "TechArticle" in graph_types and "BreadcrumbList" in graph_types
    assert "FAQPage" not in graph_types and "HowTo" not in graph_types

    # 4. Exact order of sections check
    ordered_markers = [
        'aria-label="Breadcrumb"',
        "<h1",
        'id="hata-anlami"',
        'id="hata-nedenleri"',
        'id="cozum-adimlari"',
        'id="ise-yaramazsa"',
        'id="resmi-kaynak"',
        'id="sss"',
        'id="ilgili-hatalar"',
        'class="stage2-author-box',
        'id="stage2PageVoteSection"',
    ]
    positions = [html_out.index(mk) for mk in ordered_markers]
    assert positions == sorted(positions), f"Bölüm sıralaması hatalı: {positions}"

    # 5. Build warning check when title > 60 or meta_description > 160 or alt_metin empty
    over_record = dict(sample_record)
    over_record["title"] = "Bu Çok Uzun Bir Başlık Olup Altmış Karakter Sınırını Kesinlikle Aşmaktadır Deneme"
    over_record["meta_description"] = "A" * 170
    _, over_warns = builder.render_error_code_page(over_record)
    assert any("'title' 60 karakter" in w for w in over_warns)
    assert any("'meta_description' 160 karakter" in w for w in over_warns)

    # 6. Verify existing FastAPI app still serves homepage & endpoints cleanly
    client = TestClient(main.app)
    r = client.get("/")
    assert r.status_code == 200
    print("[PASS] AŞAMA 1 şablon, veri şeması, bölüm sıralaması, JSON-LD ve karakter sınırı kontrolleri doğrulandı!")


if __name__ == "__main__":
    test_stage1_template()
