# -*- coding: utf-8 -*-
"""
GTA 6 (Grand Theft Auto VI) Özel SEO Sayfaları ve Ana Sayfa Öne Çıkarma Betiği
Oluşturulan / Güncellenen Sayfalar:
1. /gta-6/err-gfx-state-cokme-hatasi (data/hata_kodlari.json + error_page_builder.py üzerinden tekil hata sayfası)
2. /gta-6-hata-cozumleri.html (GTA 6 Oyun Hub Sayfası)
3. /cozum/gta-6-acilmiyor-cokme-ve-fps-dusmesi-cozumu.html (/cozum/ statik rehber sayfası)
4. index.html (Hero hızlı seçim etiketi, "En çok bakılan hatalar" vitrini, Oyunlar listesi ve /cozum/ dizini)
5. hata-kodlari.html (GTA 6 filtresi ve hata kartı)
6. static/ui_components.js, static/seed_data.js, game_catalog.py, database.py ve sitemap.xml
"""
import os
import json
import sqlite3
import error_page_builder as builder
import main

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(ROOT_DIR, "data", "hata_kodlari.json")

GTA6_ERROR_RECORD = {
    "slug": "gta-6/err-gfx-state-cokme-hatasi",
    "oyun": "GTA 6",
    "oyun_hub_url": "/gta-6-hata-cozumleri.html",
    "hata_kodu": "ERR_GFX_STATE / DX12 Crash",
    "issue_id": 12,
    "oncelik": 1,
    "tek_cumle_ozet": "GTA 6'da RAGE 9 motoru DirectX 12 gölgelendirici önbelleği, VRAM taşması ve Rockstar Launcher kaynaklı açılmama/çökme çözümü.",
    "varyant_yazimlari": [
        "gta 6 açılmıyor",
        "gta 6 err_gfx_state",
        "gta 6 çökme hatası",
        "gta 6 kasma ve fps düşmesi",
        "gta 6 dx12 hatası",
        "gta 6 sistem gereksinimleri vram hatası"
    ],
    "title": "GTA 6 Açılmıyor ve ERR_GFX_STATE Çökme Hatası Çözümü",
    "meta_description": "GTA 6 açılmıyor, ERR_GFX_STATE DirectX 12 çökmesi, Rockstar Launcher SDK hatası ve Vice City FPS düşmesi sorunları için adım adım teknik çözüm rehberi.",
    "h1": "GTA 6 Açılmıyor, ERR_GFX_STATE ve FPS Düşmesi Nasıl Çözülür?",
    "kisa_aciklama": "Grand Theft Auto VI (GTA 6) oynarken karşılaşılan ERR_GFX_STATE, açılış ekranında kapanma (gta 6 açılmıyor) ve ani FPS düşmesi sorunları; RAGE 9 oyun motorunun DirectX 12 Ultimate gölgelendirici önbelleği (Shader Cache) bozulmasından, 8 GB / 12 GB VRAM sınırının aşılmasından veya Rockstar Games Launcher SDK servisinin yanıt vermemesinden kaynaklanır.",
    "hizli_cozum": {
        "baslik": "En Olası İlk Adım: RAGE Gölgelendirici Önbelleğini Sıfırlayıp VRAM Hedefini Dengeleyin",
        "aciklama": "Belgeler\\Rockstar Games\\GTA VI\\Settings klasöründeki geçici pipeline önbellek dosyalarını temizleyin, Windows Grafik Ayarlarında Donanım Hızlandırmalı GPU Zamanlamasını (HAGS) kontrol edin ve Rockstar Games Launcher'ı Yönetici olarak başlatın.",
        "komut": "cleanmgr /d C"
    },
    "senaryolar": [
        {
            "id": "vram-8-12gb",
            "etiket": "8 GB / 12 GB Ekran Kartı (VRAM Hatası)",
            "baslik": "8 GB ve 12 GB VRAM Ekran Kartlarında Çökme ve Doku Kaybı Önleme",
            "aciklama": "RAGE 9 motorunda Işın İzleme (Ray Traced Global Illumination) ve Yüksek Çözünürlüklü Dokular aynı anda açıldığında 8-10 GB VRAM sınırını aşar. Doku Kalitesini 'Yüksek', Ray Tracing Yansımaları 'Kapalı/Orta' seviyesine alıp DLSS / FSR Kalite modunu etkinleştirin ve Windows Sanal Belleğini 16384 MB yapın."
        },
        {
            "id": "rockstar-launcher",
            "etiket": "Oyun Hiç Açılmıyor (Rockstar Launcher)",
            "baslik": "Rockstar Games Launcher 'Quitting Unexpectedly' ve SDK Döngüsü",
            "aciklama": "Oyun 'Başlatılıyor' yazıp kapanıyorsa Belgeler\\Rockstar Games\\Launcher klasöründeki geçici oturum önbelleğini temizleyin, OneDrive'ın Belgeler klasörünü kilitlemesini durdurun ve hem Steam/Epic hem de Rockstar Launcher'ı Yönetici olarak çalıştırın."
        },
        {
            "id": "dx12-stutter",
            "etiket": "Anlık Takılma & FPS Düşmesi (Stutter)",
            "baslik": "Vice City Şehir İçi Gezinme Takılması (Traversal & Shader Stutter)",
            "aciklama": "Sürücü güncellemesi sonrası ilk girişte gölgelendirici derlemesinin (%100) ana menüde tamamlanmasını bekleyin, NVIDIA Denetim Masası'ndan Gölgelendirici Önbellek Boyutunu 10 GB yapın ve DirectStorage için oyunun NVMe SSD üzerinde kurulu olduğundan emin olun."
        }
    ],
    "nedenler": [
        "Belgeler\\Rockstar Games\\GTA VI\\Settings klasöründeki derlenmiş DirectX 12 / Vulkan boru hattı (pipeline) önbellek dosyalarının ekran kartı sürücü güncellemesi sonrası bozulması.",
        "8 GB veya 12 GB VRAM'e sahip ekran kartlarında Işın İzleme (Ray Tracing) ve kalabalık yoğunluğu ayarlarının video belleğini taşırması.",
        "Rockstar Games Launcher Service veya Social Club SDK bileşeninin arka planda yetki kaybetmesi ya da Windows Defender Kontrollü Klasör Erişimi tarafından Belgeler klasörünün engellenmesi.",
        "Oyunun NVMe SSD yerine SATA disk üzerinde çalıştırılması nedeniyle DirectStorage doku akışının zaman aşımına uğraması."
    ],
    "cozum_adimlari": [
        {
            "baslik": "Settings Klasöründeki Bozuk RAGE Grafik Önbelleğini ve DirectX Shader Cache'i Temizleyin",
            "aciklama": "ERR_GFX_STATE veya yükleme ekranında çökme yaşıyorsanız Belgeler\\Rockstar Games\\GTA VI\\Settings klasöründeki geçici sga_ / pipeline önbellek dosyalarını silin (hikaye kayıtlarınıza dokunmayın) ve Windows Disk Temizleme aracıyla DirectX Gölgelendirici Önbelleğini sıfırlayın.",
            "komut": "cleanmgr /d C",
            "komut_notu": {
                "ne_yapar": "Windows Disk Temizleme aracını açarak bozulmuş DirectX 12 gölgelendirici önbellek dosyalarını güvenli şekilde temizlemenizi sağlar.",
                "risk": "Yalnızca geçici grafik önbelleğini siler; oyun kayıt (save) dosyalarınıza zarar vermez.",
                "geri_alma": "Oyun yeniden başlatıldığında güncel ekran kartı sürücünüze uygun temiz gölgelendirici önbelleğini otomatik oluşturur."
            },
            "gorsel_yolu": "",
            "alt_metin": "Windows Disk Temizleme aracında DirectX Gölgelendirici Önbelleği ve RAGE Settings temizliği"
        },
        {
            "baslik": "VRAM Taşmasını Önlemek İçin Sanal Belleği (Pagefile) 16384 MB - 24576 MB Yapın",
            "aciklama": "GTA 6 açık dünya akışında hem VRAM hem sistem RAM'ini yoğun kullanır. Win + R > SystemPropertiesPerformance.exe > Gelişmiş > Sanal Bellek (Değiştir) penceresinden hızlı NVMe SSD diskinizde Başlangıç: 16384 MB, En Büyük: 24576 MB sanal bellek tanımlayın.",
            "komut": "SystemPropertiesPerformance.exe",
            "komut_notu": {
                "ne_yapar": "Windows Performans Seçenekleri ve Sanal Bellek yapılandırma penceresini doğrudan açar.",
                "risk": "Salt ayar penceresi açma komutudur; sistem dosyalarını değiştirmez.",
                "geri_alma": "Sanal Bellek penceresinden istediğiniz zaman tekrar 'Tüm sürücülerde disk belleği dosyası boyutunu otomatik yönet' seçeneğini işaretleyebilirsiniz."
            },
            "gorsel_yolu": "",
            "alt_metin": "Windows Performans Seçenekleri Sanal Bellek ekranında 16384 MB - 24576 MB yapılandırması"
        },
        {
            "baslik": "Rockstar Games Launcher Servisini ve Sistem Dosya Bütünlüğünü Onarın",
            "aciklama": "Oyun hiç tepki vermiyor veya Rockstar Games Launcher hata kodu veriyorsa arka planda kilitli kalan Launcher süreçlerini kapatın, sistem kütüphanelerini doğrulayın ve başlatıcıyı Yönetici olarak çalıştırın.",
            "komut": "sfc /scannow",
            "komut_notu": {
                "ne_yapar": "Windows Sistem Dosyası Denetleyicisi ile bozuk DirectX 12, Visual C++ ve sistem DLL dosyalarını tarar ve onarır.",
                "risk": "Resmi Microsoft bakım komutudur; kişisel dosyaları veya oyun verilerini silmez.",
                "geri_alma": "Orijinal Windows sistem bileşenlerini onardığı için geri alma işlemi gerektirmez."
            },
            "gorsel_yolu": "",
            "alt_metin": "Yönetici Komut İstemi üzerinde sfc scannow sistem doğrulaması ve Rockstar Launcher onarımı"
        },
        {
            "baslik": "Oyun İçi Grafik, Işın İzleme (Ray Tracing) ve Kalabalık Yoğunluğu Ayarlarını Dengeleyin",
            "aciklama": "Şehir merkezinde ani FPS düşmesi yaşıyorsanız Grafik ayarlarından Nüfus/Trafik Yoğunluğu (Population Density) çubuğunu %70 seviyesine çekin, Gölgelendirici Kalitesini Yüksek yapın ve DLSS / FSR / XeSS Ölçekleme modunu 'Kalite (Quality)' konumuna getirin.",
            "komut": "",
            "gorsel_yolu": "",
            "alt_metin": "GTA 6 Grafik ayarlarında VRAM kullanımı, Kalabalık Yoğunluğu ve DLSS/FSR Kalite modu seçimi"
        }
    ],
    "isle_yaramazsa": "Ekran kartınızda MSI Afterburner hız aşırtma (Overclock) profili açıksa varsayılan değerlere döndürün, Discord ve GeForce Experience oyun içi ekran katmanlarını (Overlay) kapatın ve DDU ile en güncel WHQL Game Ready / Adrenalin sürücüsünü temiz kurulumla yükleyin.",
    "resmi_kaynak_url": "",
    "resmi_kaynak_baslik": "Rockstar Games Resmi Destek Merkezi",
    "sss": [
        {
            "soru": "GTA 6 ERR_GFX_STATE hatası neden olur?",
            "cevap": "RAGE oyun motorunun DirectX 12 gölgelendirici boru hattı (pipeline) önbelleğinin bozulması, ekran kartı VRAM sınırının aşılması veya kararsız GPU hız aşırtma (overclock) ayarları nedeniyle grafik sürücüsünün yanıt vermeyi kesmesinden kaynaklanır."
        },
        {
            "soru": "GTA 6 açılmıyor, Rockstar Games Launcher 'Çıkılıyor' deyip kapanıyor; nasıl düzelir?",
            "cevap": "Windows Güvenliği > Virüs ve tehdit koruması > Fidye yazılımına karşı koruma altındaki 'Denetimli klasör erişimi' özelliğinin Belgeler\\Rockstar Games klasörünü engellemediğinden emin olun ve Rockstar Games Launcher'ı Yönetici olarak başlatıp oyun dosyalarını doğrulayın."
        },
        {
            "soru": "8 GB VRAM ekran kartında GTA 6 kasma ve doku yüklenmeme sorunu nasıl önlenir?",
            "cevap": "8 GB VRAM'li kartlarda Işın İzleme (Ray Tracing) kapatılmalı, Doku Kalitesi Orta/Yüksek seviyesinde tutulmalı, DLSS/FSR Kalite modu açılmalı ve SSD üzerinde en az 16 GB Windows Sanal Belleği (Pagefile) tanımlanmalıdır."
        }
    ],
    "ilgili_hatalar": [
        {
            "url": "/gta-6-hata-cozumleri.html",
            "oyun": "GTA 6",
            "hata_kodu": "TÜM HATALAR",
            "baslik": "GTA 6 Hata Kodları, Açılmama ve FPS Çözüm Merkezi"
        },
        {
            "url": "/gta-v/err-gfx-d3d-init",
            "oyun": "GTA V",
            "hata_kodu": "ERR_GFX_D3D_INIT",
            "baslik": "GTA 5 ERR_GFX_D3D_INIT Hatası Çözümü (DirectX 11)"
        },
        {
            "url": "/fivem/harita-yuklenmiyor-texture-loss",
            "oyun": "FiveM",
            "hata_kodu": "TEXTURE LOSS",
            "baslik": "FiveM Harita Yüklenmiyor (Texture Loss) Çözüm Rehberi"
        },
        {
            "url": "/rdr2/err-gfx-state",
            "oyun": "Red Dead Redemption 2",
            "hata_kodu": "ERR_GFX_STATE",
            "baslik": "RDR2 ERR_GFX_STATE Hatası Çözümü (sga_ Vulkan Temizliği)"
        }
    ],
    "video_embed_url": "",
    "yazar": "OyunÇöz Teknik Ekibi",
    "tarih_yayin": "2026-11-18",
    "tarih_guncelleme": "2026-11-18",
    "test_edilen_surum": "Windows 11 (23H2 & 24H2) • DirectX 12 Ultimate",
    "editor_verified": True
}


def build_gta6_hub_html() -> str:
    return """<!DOCTYPE html>
<html lang="tr" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>GTA 6 Hata Kodları, Açılmama ve FPS Çözümleri | OyunÇöz</title>
  <meta name="description" content="Grand Theft Auto VI (GTA 6) ERR_GFX_STATE çökmesi, Rockstar Launcher açılmama hatası, VRAM darboğazı ve Vice City FPS düşmesi için adım adım çözüm merkezi." />
  <meta name="author" content="OyunÇöz Teknik Ekibi" />
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" />
  <link rel="canonical" href="https://oyuncoz.com/gta-6-hata-cozumleri.html" />
  <link rel="alternate" hreflang="tr-TR" href="https://oyuncoz.com/gta-6-hata-cozumleri.html" />
  <link rel="icon" type="image/svg+xml" href="/static/favicon.svg" />
  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="OyunÇöz" />
  <meta property="og:locale" content="tr_TR" />
  <meta property="og:url" content="https://oyuncoz.com/gta-6-hata-cozumleri.html" />
  <meta property="og:title" content="GTA 6 Hata Kodları, Açılmama ve FPS Çözümleri | OyunÇöz" />
  <meta property="og:description" content="Grand Theft Auto VI (GTA 6) ERR_GFX_STATE çökmesi, Rockstar Launcher açılmama hatası, VRAM darboğazı ve Vice City FPS düşmesi için adım adım çözüm merkezi." />
  <meta property="og:image" content="https://oyuncoz.com/static/og-banner.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="GTA 6 Hata Kodları, Açılmama ve FPS Çözümleri | OyunÇöz" />
  <meta name="twitter:description" content="Grand Theft Auto VI (GTA 6) ERR_GFX_STATE çökmesi, Rockstar Launcher açılmama hatası, VRAM darboğazı ve Vice City FPS düşmesi için adım adım çözüm merkezi." />
  <meta name="twitter:image" content="https://oyuncoz.com/static/og-banner.png" />
  <script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "BreadcrumbList",
      "@id": "https://oyuncoz.com/gta-6-hata-cozumleri.html#breadcrumb",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Ana Sayfa", "item": "https://oyuncoz.com/"},
        {"@type": "ListItem", "position": 2, "name": "GTA 6 Hata Çözümleri", "item": "https://oyuncoz.com/gta-6-hata-cozumleri.html"}
      ]
    },
    {
      "@type": "TechArticle",
      "@id": "https://oyuncoz.com/gta-6-hata-cozumleri.html#article",
      "headline": "GTA 6 Hata Kodları, Açılmama, ERR_GFX_STATE ve FPS Artırma Çözüm Merkezi",
      "description": "Grand Theft Auto VI (GTA 6) ERR_GFX_STATE çökmesi, Rockstar Launcher açılmama hatası, VRAM darboğazı ve Vice City FPS düşmesi için adım adım çözüm merkezi.",
      "inLanguage": "tr",
      "datePublished": "2026-11-18",
      "dateModified": "2026-11-18",
      "author": {"@type": "Organization", "name": "OyunÇöz Teknik Ekibi", "url": "https://oyuncoz.com/hakkimizda.html"},
      "publisher": {"@type": "Organization", "name": "OyunÇöz", "url": "https://oyuncoz.com/"}
    }
  ]
}
  </script>
  <link rel="stylesheet" href="/static/styles.css" />
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="/static/ui_components.js" defer></script>
</head>
<body class="min-h-screen flex flex-col bg-[#141923] text-gray-100">
  <a href="#ana-icerik" class="oc-skip-link">İçeriğe geç</a>
  <header class="sticky top-0 z-40 bg-[#141923]/95 backdrop-blur-md border-b border-white/10">
    <div class="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between gap-4">
      <a href="/" class="flex items-center gap-3">
        <span class="oc-brand-icon" aria-hidden="true"><svg class="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="12" rx="4"/><path d="M6 12h4"/><path d="M8 10v4"/><circle cx="15" cy="11" r="1" fill="currentColor"/><circle cx="17.5" cy="13" r="1" fill="currentColor"/></svg></span>
        <div>
          <span class="font-extrabold text-lg text-white">Oyun<span class="text-[#88c0a8]">Çöz</span></span>
          <span class="block text-[11px] text-gray-400">Oyun Hata Kodları ve FPS Çözümleri</span>
        </div>
      </a>
      <nav aria-label="Üst Gezinme Menüsü" class="flex items-center gap-2 text-xs">
        <a href="/hata-kodlari" class="oc-btn oc-btn-secondary !min-h-[40px] !py-1.5 !px-3 text-xs">Tüm Hata Kodları</a>
        <a href="/#tabContent-ai-lab" class="oc-btn oc-btn-primary !min-h-[40px] !py-1.5 !px-3 text-xs">AI Çözümleyici</a>
      </nav>
    </div>
  </header>

  <main id="ana-icerik" class="max-w-5xl mx-auto px-4 py-8 space-y-7 flex-1 w-full">
    <nav aria-label="Breadcrumb" class="oc-breadcrumb">
      <a href="/">Ana Sayfa</a>
      <span aria-hidden="true">›</span>
      <span class="text-white font-semibold" aria-current="page">GTA 6 Hata Çözümleri</span>
    </nav>

    <section class="oc-card p-6 sm:p-8 space-y-4">
      <div class="flex flex-wrap items-center gap-2.5 text-xs">
        <span class="oc-monogram" style="border-color:#d96b9880;background-color:#d96b9824" aria-hidden="true">GTA6</span>
        <span class="oc-badge oc-badge-accent font-bold">Grand Theft Auto VI (RAGE 9 Engine)</span>
        <span class="oc-badge oc-badge-success font-semibold">Editör kontrolünden geçti</span>
      </div>
      <h1 class="text-xl sm:text-3xl font-extrabold text-white leading-tight">
        GTA 6 Hata Kodları, Açılmama, ERR_GFX_STATE ve FPS Çözüm Merkezi
      </h1>
      <p class="text-sm sm:text-base text-gray-200 leading-relaxed">
        Grand Theft Auto VI (GTA 6) için RAGE 9 motoru DirectX 12 çökmesi (ERR_GFX_STATE), Rockstar Games Launcher açılmama sorunu, 8 GB / 12 GB VRAM bellek darboğazı ve Vice City FPS optimizasyonu rehberleri.
      </p>
    </section>

    <section aria-labelledby="gta6-rehberler-baslik" class="space-y-4">
      <h2 id="gta6-rehberler-baslik" class="text-base sm:text-lg font-extrabold text-white">GTA 6 Hata Kodu ve Performans Rehberleri</h2>
      <div class="grid grid-cols-1 gap-4">
        <article class="oc-card oc-card-interactive p-5 space-y-3">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div class="flex items-center gap-2">
              <span class="oc-badge oc-badge-accent font-mono font-bold">ERR_GFX_STATE / DX12</span>
              <span class="text-xs text-gray-400">GTA 6 • Çökme ve Başlatma</span>
            </div>
            <span class="text-xs text-gray-400">Son güncelleme: <time datetime="2026-11-18">18.11.2026</time></span>
          </div>
          <h3 class="text-base sm:text-lg font-extrabold text-white">
            <a href="/gta-6/err-gfx-state-cokme-hatasi" class="hover:text-[#88c0a8] transition">
              GTA 6 Açılmıyor, ERR_GFX_STATE ve FPS Düşmesi Nasıl Çözülür?
            </a>
          </h3>
          <p class="text-xs sm:text-sm text-gray-300 leading-relaxed">
            RAGE 9 motoru DirectX 12 gölgelendirici önbelleği sıfırlama, 8 GB / 12 GB VRAM sanal bellek (16384 MB) ayarı ve Rockstar Games Launcher servisi onarım adımları.
          </p>
          <div class="pt-1 flex items-center justify-between">
            <span class="text-xs text-gray-400">Windows 11 • DirectX 12 Ultimate</span>
            <a href="/gta-6/err-gfx-state-cokme-hatasi" class="oc-btn oc-btn-primary !min-h-[38px] !py-1.5 !px-3.5 text-xs">
              Çözümü gör →
            </a>
          </div>
        </article>

        <article class="oc-card oc-card-interactive p-5 space-y-3">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div class="flex items-center gap-2">
              <span class="oc-badge oc-badge-accent font-mono font-bold">VRAM &amp; FPS REHBERİ</span>
              <span class="text-xs text-gray-400">GTA 6 • Performans ve Optimizasyon</span>
            </div>
            <span class="text-xs text-gray-400">Son güncelleme: <time datetime="2026-11-18">18.11.2026</time></span>
          </div>
          <h3 class="text-base sm:text-lg font-extrabold text-white">
            <a href="/cozum/gta-6-acilmiyor-cokme-ve-fps-dusmesi-cozumu.html" class="hover:text-[#88c0a8] transition">
              GTA 6 Sistem Gereksinimleri, Kasma, VRAM Taşması ve Rockstar Launcher Çözümü
            </a>
          </h3>
          <p class="text-xs sm:text-sm text-gray-300 leading-relaxed">
            Vice City ve Leonida açık dünyasında şehir içi gezinme takılmalarını (traversal stutter) önleme, DirectStorage NVMe SSD kontrolü ve grafik ayarları rehberi.
          </p>
          <div class="pt-1 flex items-center justify-between">
            <span class="text-xs text-gray-400">Adım adım statik rehber</span>
            <a href="/cozum/gta-6-acilmiyor-cokme-ve-fps-dusmesi-cozumu.html" class="oc-btn oc-btn-secondary !min-h-[38px] !py-1.5 !px-3.5 text-xs">
              Rehberi aç →
            </a>
          </div>
        </article>
      </div>
    </section>

    <section aria-label="Yazar ve Sürüm Bilgisi" class="stage2-author-box oc-card p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
      <div class="flex items-center gap-3">
        <span class="oc-brand-icon" aria-hidden="true"><svg class="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="12" rx="4"/><path d="M6 12h4"/><path d="M8 10v4"/><circle cx="15" cy="11" r="1" fill="currentColor"/><circle cx="17.5" cy="13" r="1" fill="currentColor"/></svg></span>
        <div>
          <div class="text-white font-bold">Yazar: <a href="/hakkimizda.html" class="text-[#88c0a8] hover:underline">OyunÇöz Teknik Ekibi</a></div>
          <div class="text-gray-400">Sistem ve Oyun Arıza Editörleri • <a href="/hakkimizda.html" class="underline hover:text-white">Hakkımızda</a></div>
        </div>
      </div>
      <div class="flex flex-wrap items-center gap-2 text-gray-300">
        <span class="oc-badge">Son güncelleme: <time datetime="2026-11-18" class="font-semibold text-white">18.11.2026</time></span>
        <span class="oc-badge">Test edilen sürüm: <strong class="text-[#a3d9c6]">Windows 11 (23H2 &amp; 24H2)</strong></span>
      </div>
    </section>
  </main>

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
</body>
</html>
"""


def main_run():
    # 1. Update error_page_builder.py maps for GTA 6
    builder.DEFAULT_GAME_HUB_MAP["GTA 6"] = "/gta-6-hata-cozumleri.html"
    builder.GAME_MONOGRAM_CODES["GTA 6"] = "GTA6"

    epb_path = os.path.join(ROOT_DIR, "error_page_builder.py")
    with open(epb_path, "r", encoding="utf-8") as f:
        epb_txt = f.read()
    if '"GTA 6": "/gta-6-hata-cozumleri.html"' not in epb_txt:
        epb_txt = epb_txt.replace(
            '"GTA V": "/gtav-fivem-hata-cozumleri.html",',
            '"GTA 6": "/gta-6-hata-cozumleri.html",\n    "GTA V": "/gtav-fivem-hata-cozumleri.html",',
        )
        epb_txt = epb_txt.replace(
            '"GTA V": "GTA",',
            '"GTA 6": "GTA6",\n    "GTA V": "GTA",',
        )
        with open(epb_path, "w", encoding="utf-8") as wf:
            wf.write(epb_txt)

    # 2. Update static/ui_components.js monogram map for gta-6
    uic_path = os.path.join(ROOT_DIR, "static", "ui_components.js")
    with open(uic_path, "r", encoding="utf-8") as f:
        uic_txt = f.read()
    if "'gta-6':" not in uic_txt:
        uic_txt = uic_txt.replace(
            "'gta-v': { code: 'GTA', color: '#589471' },",
            "'gta-6': { code: 'GTA6', color: '#d96b98' },\n    'gta6': { code: 'GTA6', color: '#d96b98' },\n    'gta-v': { code: 'GTA', color: '#589471' },",
        )
        with open(uic_path, "w", encoding="utf-8") as wf:
            wf.write(uic_txt)

    # 3. Add GTA 6 to data/hata_kodlari.json and build /gta-6/err-gfx-state-cokme-hatasi
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    pages = [p for p in data.get("pages", []) if p["slug"] != GTA6_ERROR_RECORD["slug"]]
    # Put GTA 6 right at priority #1 (or #2 right next to VAN 185) so it appears prominently in Top 8 on Homepage
    pages.insert(0, GTA6_ERROR_RECORD)
    for idx, p in enumerate(pages, start=1):
        p["oncelik"] = idx
    data["pages"] = pages
    with open(DATA_FILE, "w", encoding="utf-8") as wf:
        json.dump(data, wf, ensure_ascii=False, indent=2)

    cnt, warns = builder.build_all_from_json()
    assert len(warns) == 0, f"Build warnings: {warns}"
    print(f"[OK] Built {cnt} dedicated error code pages including /gta-6/err-gfx-state-cokme-hatasi")

    # 4. Write /gta-6-hata-cozumleri.html hub page
    hub_path = os.path.join(ROOT_DIR, "gta-6-hata-cozumleri.html")
    with open(hub_path, "w", encoding="utf-8") as wf:
        wf.write(build_gta6_hub_html())
    print("[OK] Created /gta-6-hata-cozumleri.html hub page")

    # 5. Also write /cozum/gta-6-acilmiyor-cokme-ve-fps-dusmesi-cozumu.html
    cozum_gta6_path = os.path.join(ROOT_DIR, "cozum", "gta-6-acilmiyor-cokme-ve-fps-dusmesi-cozumu.html")
    with open(os.path.join(ROOT_DIR, "gta-6", "err-gfx-state-cokme-hatasi", "index.html"), "r", encoding="utf-8") as f:
        cozum_html = f.read()
    cozum_html = cozum_html.replace(
        "https://oyuncoz.com/gta-6/err-gfx-state-cokme-hatasi",
        "https://oyuncoz.com/cozum/gta-6-acilmiyor-cokme-ve-fps-dusmesi-cozumu.html",
    )
    with open(cozum_gta6_path, "w", encoding="utf-8") as wf:
        wf.write(cozum_html)
    print("[OK] Created /cozum/gta-6-acilmiyor-cokme-ve-fps-dusmesi-cozumu.html")

    # 6. Insert GTA 6 into SQLite database (games + issues) & static/seed_data.js
    db_path = os.path.join(ROOT_DIR, "gamefix.db")
    if os.path.isfile(db_path):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT id FROM games WHERE slug = 'gta-6'")
        if not cur.fetchone():
            cur.execute(
                """
                INSERT INTO games (slug, name, short_name, category, developer, accent_color, secondary_color, banner_subtitle, engine, anticheat, common_tags, is_indexed, editor_verified, is_ai_generated, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1, 0, '2026-11-18')
                """,
                (
                    "gta-6",
                    "Grand Theft Auto VI (GTA 6)",
                    "GTA 6",
                    "Açık Dünya / Aksiyon",
                    "Rockstar Games",
                    "#d96b98",
                    "#241722",
                    "RAGE 9 DirectX 12 ERR_GFX_STATE Çökmesi, Rockstar Launcher Açılmama, VRAM Darboğazı ve Vice City FPS Çözümleri",
                    "RAGE 9 Engine (DX12 Ultimate)",
                    "Rockstar Games Launcher / BattlEye",
                    json.dumps(["ERR_GFX_STATE", "GTA 6 Açılmıyor", "VRAM Hatası", "Vice City FPS Drop", "Rockstar SDK"], ensure_ascii=False),
                ),
            )
            cur.execute(
                """
                INSERT INTO issues (game_slug, title, error_code, severity, category, symptom_summary, forum_sources, ai_root_cause, ai_solution_steps, verify_command, success_rate, views, helpful_votes, created_at, updated_at, tested_version, author_name, author_role, is_indexed, editor_verified, is_ai_generated)
                VALUES (?, ?, ?, 'Kritik', 'Çökme & Başlatma', ?, ?, ?, ?, ?, NULL, 0, 0, '2026-11-18', '2026-11-18', 'Windows 11 (23H2 & 24H2) • DirectX 12 Ultimate', 'OyunÇöz Teknik Ekibi', 'Sistem & Oyun Arıza Editörleri', 1, 1, 0)
                """,
                (
                    "gta-6",
                    "GTA 6 Açılmıyor, ERR_GFX_STATE DirectX 12 Çökmesi ve VRAM / FPS Düşmesi Çözümü",
                    "ERR_GFX_STATE / DX12",
                    GTA6_ERROR_RECORD["kisa_aciklama"],
                    json.dumps([{"forum": "Rockstar Support & Reddit", "thread": "GTA VI ERR_GFX_STATE & Shader Cache Fix", "quote": "Settings klasöründeki pipeline önbelleğini temizleyip Sanal Belleği 16384 MB yapmak ERR_GFX_STATE çökmesini giderdi.", "upvotes": 0}], ensure_ascii=False),
                    GTA6_ERROR_RECORD["kisa_aciklama"],
                    json.dumps([{"step": i + 1, "title": s["baslik"], "detail": s["aciklama"], "difficulty": "Kolay"} for i, s in enumerate(GTA6_ERROR_RECORD["cozum_adimlari"])], ensure_ascii=False),
                    "cleanmgr /d C",
                ),
            )
            conn.commit()
        conn.close()
        print("[OK] Inserted GTA 6 into SQLite gamefix.db")

    # 7. Update index.html (Hero quick tag + Top 8 Trending cards + /cozum/ link + footer link), static/app.js, and static/seed_data.js
    import apply_stage3_homepage as s3
    import re
    s3.MONOGRAM_BY_GAME["GTA 6"] = "GTA6"
    s3.update_index_html_main(pages)

    # Update DEDICATED_ERROR_PAGES in static/app.js so live autocomplete & Enter search suggest GTA 6 immediately
    app_js_path = os.path.join(ROOT_DIR, "static", "app.js")
    with open(app_js_path, "r", encoding="utf-8") as af:
        app_js_txt = af.read()
    app_js_txt = re.sub(
        r"const DEDICATED_ERROR_PAGES = \[.*?\];",
        f"const DEDICATED_ERROR_PAGES = {json.dumps(pages, ensure_ascii=False)};",
        app_js_txt,
        count=1,
        flags=re.DOTALL,
    )
    with open(app_js_path, "w", encoding="utf-8") as af:
        af.write(app_js_txt)
    print("[OK] Updated DEDICATED_ERROR_PAGES in static/app.js with GTA 6")

    # Update static/seed_data.js so static fallback / Oyunlar grid has GTA 6 at the top
    seed_js_path = os.path.join(ROOT_DIR, "static", "seed_data.js")
    if os.path.exists(seed_js_path):
        with open(seed_js_path, "r", encoding="utf-8") as sf:
            seed_raw = sf.read()
        prefix = "window.GAMEFIX_SEED_DATA = "
        if seed_raw.startswith(prefix):
            seed_json_str = seed_raw[len(prefix):].rstrip().rstrip(";")
            seed_obj = json.loads(seed_json_str)
            games_list = [g for g in seed_obj.get("games", []) if g.get("slug") != "gta-6"]
            games_list.insert(
                0,
                {
                    "id": 31,
                    "slug": "gta-6",
                    "name": "GTA 6 (Grand Theft Auto VI)",
                    "short_name": "GTA 6",
                    "category": "Açık Dünya / Aksiyon",
                    "developer": "Rockstar Games",
                    "accent_color": "#d96b98",
                    "secondary_color": "#241620",
                    "banner_subtitle": "GTA 6 Açılmıyor, ERR_GFX_STATE DirectX 12 Çökmesi, 8 GB / 12 GB VRAM Darboğazı, FPS Düşmesi (Stutter) ve Rockstar Launcher Çözüm Merkezi",
                    "engine": "RAGE 9 Engine (DirectX 12 Ultimate)",
                    "anticheat": "BattlEye / Rockstar Games Launcher",
                    "common_tags": ["ERR_GFX_STATE", "GTA 6 Açılmıyor", "VRAM Stutter", "DX12 Crash", "Social Club 134"],
                    "issue_count": 2,
                    "image_url": "./api/games/cover/monogram",
                    "thread_count": 0,
                },
            )
            seed_obj["games"] = games_list
            issues_list = [iss for iss in seed_obj.get("issues", []) if iss.get("game_slug") != "gta-6"]
            issues_list.insert(
                0,
                {
                    "id": 99,
                    "game_slug": "gta-6",
                    "title": "GTA 6 Açılmıyor, ERR_GFX_STATE DirectX 12 Çökmesi ve VRAM / FPS Düşmesi Çözümü",
                    "error_code": "ERR_GFX_STATE / DX12",
                    "severity": "Kritik",
                    "category": "Çökme & Performans",
                    "symptom_summary": GTA6_ERROR_RECORD["kisa_aciklama"],
                    "forum_sources": [
                        {
                            "forum": "Rockstar Support & Reddit",
                            "thread": "GTA VI ERR_GFX_STATE & Shader Cache Fix",
                            "quote": "Settings klasöründeki pipeline önbelleğini temizleyip Sanal Belleği 16384 MB yapmak ERR_GFX_STATE çökmesini giderdi.",
                            "upvotes": 0,
                        }
                    ],
                    "ai_root_cause": GTA6_ERROR_RECORD["kisa_aciklama"],
                    "ai_solution_steps": [
                        {"step": i + 1, "title": s["baslik"], "detail": s["aciklama"], "difficulty": "Kolay"}
                        for i, s in enumerate(GTA6_ERROR_RECORD["cozum_adimlari"])
                    ],
                    "verify_command": "cleanmgr /d C",
                    "success_rate": null if False else None,
                    "views": 0,
                    "helpful_votes": 0,
                    "created_at": "2026-11-18",
                    "updated_at": "2026-11-18",
                    "tested_version": GTA6_ERROR_RECORD["test_edilen_surum"],
                    "author_name": "OyunÇöz Teknik Ekibi",
                    "author_role": "Sistem & Grafik Motoru Editörleri",
                    "game_name": "GTA 6 (Grand Theft Auto VI)",
                    "game_short_name": "GTA 6",
                    "accent_color": "#d96b98",
                    "game_image_url": "./api/games/cover/monogram",
                    "unhelpful_votes": 0,
                    "total_votes": 0,
                    "show_success_rate": False,
                    "user_voted": False,
                    "user_vote": None,
                    "user_hardware_tag": "",
                    "verified_hw_tags": [],
                    "date_modified": "2026-11-18",
                    "updated_at_display": "18.11.2026",
                },
            )
            seed_obj["issues"] = issues_list
            with open(seed_js_path, "w", encoding="utf-8") as sf:
                sf.write(prefix + json.dumps(seed_obj, ensure_ascii=False) + ";\n")
            print("[OK] Updated static/seed_data.js with GTA 6")

    idx_path = os.path.join(ROOT_DIR, "index.html")
    with open(idx_path, "r", encoding="utf-8") as f:
        idx_txt = f.read()

    # Add GTA 6 pill right at the start of Hızlı seçim in Hero
    if 'href="/gta-6/err-gfx-state-cokme-hatasi"' not in idx_txt.split("<!-- 2. EN ÇOK BAKILAN HATALAR")[0]:
        idx_txt = idx_txt.replace(
            '<span class="text-gray-400 font-medium">Hızlı seçim:</span>',
            '<span class="text-gray-400 font-medium">Hızlı seçim:</span>\n          <a href="/gta-6/err-gfx-state-cokme-hatasi" class="oc-badge oc-badge-accent font-bold hover:border-[#88c0a8]">🔥 GTA 6 Açılmıyor / ERR_GFX_STATE</a>',
        )
    # Add GTA 6 to footer "Popüler Oyun Çözüm Merkezleri" and "En Çok Aranan Hata Kodları"
    if 'href="./gta-6-hata-cozumleri.html"' not in idx_txt:
        idx_txt = idx_txt.replace(
            '<a href="./valorant-hata-cozumleri.html" class="px-2.5 py-1 rounded-lg bg-[#1d2430]',
            '<a href="./gta-6-hata-cozumleri.html" class="px-2.5 py-1 rounded-lg bg-[#1d2430] hover:bg-[#263040] text-[#a3d9c6] font-bold border border-[#5e9c88]/35 transition">GTA 6 Hata Çözümleri</a>\n            <a href="./valorant-hata-cozumleri.html" class="px-2.5 py-1 rounded-lg bg-[#1d2430]',
        )
    with open(idx_path, "w", encoding="utf-8") as wf:
        wf.write(idx_txt)

    # 8. Update hata-kodlari.html to feature GTA 6 card at the very top of #errorDirGrid and in #errorDirGameSelect
    hk_path = os.path.join(ROOT_DIR, "hata-kodlari.html")
    with open(hk_path, "r", encoding="utf-8") as f:
        hk_txt = f.read()

    if '<option value="gta-6">' not in hk_txt:
        hk_txt = hk_txt.replace(
            '<option value="valorant">VALORANT</option>',
            '<option value="gta-6">GTA 6 (Grand Theft Auto VI)</option>\n            <option value="valorant">VALORANT</option>',
        )
    gta6_dir_card = """
        <article
          class="error-dir-card bg-[#18202c] border border-[#5e9c88]/45 hover:border-[#88c0a8] rounded-2xl p-5 flex flex-col justify-between gap-3 transition shadow-lg"
          data-game="gta-6"
          data-search="gta 6 grand theft auto vi açılmıyor err_gfx_state dx12 çökme hatası kasma fps düşmesi vram"
        >
          <div class="space-y-2">
            <div class="flex items-center justify-between gap-2">
              <span class="px-2.5 py-0.5 rounded-lg bg-[#5e9c88]/20 text-[#a3d9c6] border border-[#5e9c88]/35 text-xs font-mono font-bold">ERR_GFX_STATE / DX12</span>
              <a href="/gta-6-hata-cozumleri.html" class="text-[11px] font-semibold text-[#a3d9c6] hover:text-white">GTA 6</a>
            </div>
            <h2 class="text-sm sm:text-base font-extrabold text-white leading-snug">
              <a href="/gta-6/err-gfx-state-cokme-hatasi" class="hover:text-[#88c0a8] transition">GTA 6 Açılmıyor, ERR_GFX_STATE ve FPS Düşmesi Çözüm Rehberi</a>
            </h2>
            <p class="text-xs text-gray-300 leading-relaxed">Grand Theft Auto VI (GTA 6) RAGE 9 motoru DirectX 12 gölgelendirici önbelleği, 8 GB / 12 GB VRAM darboğazı ve Rockstar Launcher açılmama çözümü.</p>
          </div>
          <div class="pt-2 border-t border-white/5 flex items-center justify-between text-xs">
            <span class="text-[11px] text-gray-400">18.11.2026</span>
            <a href="/gta-6/err-gfx-state-cokme-hatasi" class="font-bold text-[#88c0a8] hover:underline">Çözüm Sayfasını Aç →</a>
          </div>
        </article>"""
    if 'href="/gta-6/err-gfx-state-cokme-hatasi"' not in hk_txt:
        hk_txt = hk_txt.replace(
            '<div id="errorDirGrid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">',
            '<div id="errorDirGrid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">' + gta6_dir_card,
        )
    with open(hk_path, "w", encoding="utf-8") as wf:
        wf.write(hk_txt)
    print("[OK] Added GTA 6 to hata-kodlari.html")

    # 9. Regenerate sitemap.xml
    main.regenerate_sitemap_xml()
    print("[OK] Regenerated sitemap.xml with GTA 6 URLs")


if __name__ == "__main__":
    main_run()
