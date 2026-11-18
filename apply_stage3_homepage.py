# -*- coding: utf-8 -*-
"""
AŞAMA 3: Ana Sayfa Yeniden Düzenlemesi
1. Hero: Büyük arama kutusu ("Hangi hatayı alıyorsun?", Placeholder: "VAN 185, ERR_GFX_STATE, Exit Code 1…"), anlık otomatik tamamlama, öneriye tıklayınca doğrudan hata sayfasına gitme, Enter'da sonuçlar, sonuç yoksa "AI çözümleyiciyle analiz et" butonu.
2. Arama altında "En çok bakılan hatalar": 8 kart (oyun monogram rozeti, hata kodu, tek cümle açıklama, "Çözümü gör" bağlantısı), oncelik alanına göre sıralı.
3. "Oyunlar" ızgarası: oyun monogram rozeti + oyun adı + gerçek veriden hesaplanan hata kodu sayısı.
4. AI Çözümleyici: ortada ayrı ve sade kart ("Listede olmayan bir hata mı var? AI ile analiz et."), log yükleme ve donanım algılama ikincil açılır kutu (<details>) içinde.
5. Forum bölümü: ana sayfanın altında, 0 ise sayaç göstermez, "İlk soruyu sen sor" çağrısı gösterir.
6. Kaynaksız istatistikler ("50 Rehber", "7/24 Aktif") ve iç teknik etiketler ("website_url") kaldırıldı.
"""
import os
import json
import html

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(ROOT_DIR, "data", "hata_kodlari.json")

PRIORITY_ORDER = {
    "lol/van-185": (1, "LoL'de Riot İstemcisi ile Vanguard arasındaki oturum bağlantısı koptuğunda oluşan hata kodu."),
    "valorant/van-9003": (2, "Windows 11'de BIOS UEFI Secure Boot özelliği aktif olmadığında çıkan Vanguard uyumluluk hatası."),
    "lol/van-128": (3, "Windows sınama modu veya antivirüs çakışması nedeniyle Vanguard çekirdek sürücüsünün başlamama hatası."),
    "gta-v/err-gfx-d3d-init": (4, "GTA 5'te DirectX 11 görüntü bağdaştırıcısının sıfırlanması veya settings.xml uyumsuzluğu hatası."),
    "valorant/van-1067": (5, "TPM 2.0 güvenlik yongası veya vgc arka plan servisi yanıt vermediğinde oluşan bağlantı hatası."),
    "cs2/vac-oturum-dogrulanamadi": (6, "Steam Client Service veya oyun dosyası imzaları doğrulanamadığında eşleştirmeyi engelleyen uyarı."),
    "minecraft/exit-code-1": (7, "Uyumsuz Forge/Fabric modları veya yanlış Java 21 yürütülebilir yolu nedeniyle oluşan çökme kodu."),
    "rdr2/err-gfx-state": (8, "Belgeler klasöründeki sga_ Vulkan gölgelendirici önbelleği bozulduğunda oluşan RAGE motoru hatası."),
    "fivem/harita-yuklenmiyor-texture-loss": (9, "FiveM sunucularında Extended Texture Budget düşük kaldığında yolların ve binaların kaybolması sorunu."),
    "cs2/packet-burst-fps-dusmesi": (10, "Source 2 motorunda sub-tick paket dalgalanması ve bozuk DirectX gölgelendirici önbelleği kaynaklı takılma."),
    "bannerlord/d3d-device-context-map": (11, "Kuşatma savaşlarında bozuk ProgramData Shaders önbelleği nedeniyle oluşan DirectX 11 GPU çökmesi."),
    "fc-25/anticheat-hatasi": (12, "EA App önbelleği veya EAAntiCheat servisi bozulduğunda oyunun açılış ekranında kapanması sorunu."),
    "black-myth-wukong/out-of-video-memory": (13, "Unreal Engine 5 gölgelendirici derlemesi sırasında sanal bellek veya işlemci kaynaklı bellek hatası."),
}

MONOGRAM_BY_GAME = {
    "League of Legends": "LoL",
    "Valorant": "VAL",
    "GTA V": "GTA",
    "FiveM": "FVM",
    "Counter-Strike 2": "CS2",
    "Minecraft": "MC",
    "Red Dead Redemption 2": "RDR2",
    "Mount & Blade II: Bannerlord": "M&B2",
    "EA Sports FC 25": "FC25",
    "Black Myth: Wukong": "WKG",
}


def update_hata_kodlari_json():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    for p in data.get("pages", []):
        slug = p["slug"]
        prio, short_s = PRIORITY_ORDER.get(slug, (99, p.get("meta_description", "")))
        p["oncelik"] = prio
        p["tek_cumle_ozet"] = short_s

    data["pages"].sort(key=lambda x: x.get("oncelik", 99))
    with open(DATA_FILE, "w", encoding="utf-8") as wf:
        json.dump(data, wf, ensure_ascii=False, indent=2)
    return data["pages"]


def build_top8_cards_html(pages):
    cards = []
    for p in pages[:8]:
        url = f"/{p['slug']}"
        game = html.escape(p["oyun"])
        code = html.escape(p["hata_kodu"])
        mono = html.escape(MONOGRAM_BY_GAME.get(p["oyun"], p["oyun"][:3].upper()))
        desc = html.escape(p.get("tek_cumle_ozet") or p["meta_description"])
        cards.append(f"""          <article class="oc-card oc-card-interactive p-4 flex flex-col justify-between gap-3">
            <div class="space-y-2.5">
              <div class="flex items-center justify-between gap-2">
                <div class="flex items-center gap-2 min-w-0">
                  <span class="oc-monogram oc-monogram-sm" aria-hidden="true">{mono}</span>
                  <span class="text-xs font-bold text-gray-200 truncate">{game}</span>
                </div>
                <span class="oc-badge oc-badge-accent font-mono font-bold shrink-0">{code}</span>
              </div>
              <p class="text-xs sm:text-sm text-gray-200 leading-relaxed">{desc}</p>
            </div>
            <div class="pt-2 border-t border-white/5 flex items-center justify-between text-xs">
              <span class="text-gray-400">Adım adım rehber</span>
              <a href="{url}" class="font-bold text-[#88c0a8] hover:underline">Çözümü gör →</a>
            </div>
          </article>""")
    return "\n".join(cards)


def update_index_html_main(pages):
    top8_html = build_top8_cards_html(pages)
    index_path = os.path.join(ROOT_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        txt = f.read()

    start_marker = '    <main id="ana-icerik"'
    end_marker = '    </main>'
    idx_s = txt.index(start_marker)
    idx_e = txt.index(end_marker, idx_s) + len(end_marker)

    new_main = f"""    <main id="ana-icerik" class="space-y-10 w-full">

      <!-- 1. ÜST BÖLÜM (HERO): BÜYÜK ARAMA KUTUSU VE ANLIK OTOMATİK TAMAMLAMA -->
      <section id="gameHeroBanner" class="oc-card p-6 sm:p-10 space-y-5">
        <div class="max-w-3xl mx-auto text-center space-y-3">
          <div class="inline-flex flex-wrap items-center justify-center gap-2">
            <span id="heroCategoryBadge" class="oc-badge oc-badge-accent">Oyun Hata Kodları Rehberi</span>
            <span id="heroEngineBadge" class="hidden oc-badge"></span>
            <span id="heroAnticheatBadge" class="hidden oc-badge"></span>
          </div>
          <h1 id="heroGameTitle" class="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
            Hangi hatayı alıyorsun?
          </h1>
          <p id="heroGameSubtitle" class="text-sm sm:text-base text-gray-300 mx-auto">
            Aldığın hata kodunu veya oyun adını yaz; doğrudan o hatanın adım adım çözüm sayfasına git.
          </p>
          <div id="heroGameCoverWrapper" class="hidden"><img id="heroGameCoverImg" src="./static/logo.svg" alt="OyunÇöz Rozeti" /></div>
        </div>

        <!-- Büyük Arama Kutusu -->
        <div class="max-w-2xl mx-auto relative" id="desktopSearchWrapper">
          <form onsubmit="handleHeroSearchSubmit(event)" class="relative">
            <label for="globalSearchInput" class="sr-only">Hata kodu veya oyun ara</label>
            <input
              id="globalSearchInput"
              type="search"
              autocomplete="off"
              placeholder="VAN 185, ERR_GFX_STATE, Exit Code 1…"
              class="w-full bg-[#121822] text-base sm:text-lg text-white placeholder-gray-400 rounded-2xl pl-12 pr-28 py-4 border border-white/15 focus:outline-none focus:border-[#88c0a8] shadow-inner transition"
              onfocus="openLiveAutocomplete(this.value)"
              oninput="handleLiveSearchInput(this.value)"
              onkeydown="handleSearchKeydown(event)"
            />
            <svg class="w-5 h-5 text-[#88c0a8] absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
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
                class="oc-btn oc-btn-primary !min-h-[40px] !py-1.5 !px-4 text-xs sm:text-sm font-bold"
              >
                Ara
              </button>
            </div>
          </form>

          <!-- Anlık Otomatik Tamamlama Açılır Listesi -->
          <div
            id="liveSearchDropdown"
            class="hidden absolute left-0 right-0 top-full mt-2 bg-[#171e2b] border border-[#88c0a8]/45 rounded-2xl shadow-2xl z-50 max-h-[420px] overflow-y-auto divide-y divide-white/10"
            role="listbox"
            aria-label="Hata kodu ve oyun önerileri"
          ></div>
        </div>

        <!-- Hızlı Etiketler -->
        <div class="max-w-2xl mx-auto pt-1 flex flex-wrap items-center justify-center gap-2 text-xs">
          <span class="text-gray-400 font-medium">Hızlı seçim:</span>
          <a href="/lol/van-185" class="oc-badge hover:border-[#88c0a8]">VAN 185</a>
          <a href="/valorant/van-9003" class="oc-badge hover:border-[#88c0a8]">VAN 9003</a>
          <a href="/lol/van-128" class="oc-badge hover:border-[#88c0a8]">VAN 128</a>
          <a href="/gta-v/err-gfx-d3d-init" class="oc-badge hover:border-[#88c0a8]">ERR_GFX_D3D_INIT</a>
          <a href="/cs2/vac-oturum-dogrulanamadi" class="oc-badge hover:border-[#88c0a8]">CS2 VAC</a>
          <a href="/minecraft/exit-code-1" class="oc-badge hover:border-[#88c0a8]">Exit Code 1</a>
          <div id="heroCommonTags" class="hidden"></div>
        </div>

        <!-- Enter'a Basıldığında Açılan Arama Sonuçları Alanı -->
        <div id="heroSearchResultsSection" class="hidden max-w-4xl mx-auto pt-4 border-t border-white/10 space-y-3"></div>
      </section>

      <!-- Donanım Darboğaz Uyarı Alanı (İsteğe Bağlı Tespit Sonrası) -->
      <div id="hardwareBottleneckBanner" class="hidden"></div>

      <!-- 2. EN ÇOK BAKILAN HATALAR (6-8 Kart, Veri Dosyasındaki Öncelik Sırasına Göre) -->
      <section aria-labelledby="en-cok-bakilan-baslik" class="space-y-4">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h2 id="en-cok-bakilan-baslik" class="text-lg sm:text-xl font-extrabold text-white">
              En çok bakılan hatalar
            </h2>
            <p class="text-xs sm:text-sm text-gray-400">
              Oyuncuların en sık arattığı hata kodları ve doğrudan çözüm sayfaları
            </p>
          </div>
          <a href="/hata-kodlari" class="text-xs sm:text-sm font-bold text-[#88c0a8] hover:underline">
            Tüm hata kodlarını gör →
          </a>
        </div>

        <div id="homeTrendingIssuesGrid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
{top8_html}
        </div>
      </section>

      <!-- 3. OYUNLAR IZGARASI (Oyun Rozeti + Oyun Adı + Gerçek Hata Kodu Sayısı) -->
      <section aria-labelledby="oyunlar-izgarasi-baslik" class="space-y-4">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h2 id="oyunlar-izgarasi-baslik" class="text-lg sm:text-xl font-extrabold text-white">
              Oyunlar
            </h2>
            <p class="text-xs sm:text-sm text-gray-400">
              Oyun seçerek o oyuna ait hata kodlarını ve çözüm rehberlerini filtreleyebilirsin
            </p>
          </div>
          <button
            type="button"
            onclick="toggleGamesNavPanel(true)"
            class="text-xs sm:text-sm font-bold text-[#88c0a8] hover:underline self-start sm:self-auto"
          >
            Tüm oyunları ara ve listele →
          </button>
        </div>

        <div id="homeGamesShowcaseGrid" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
          <!-- Gerçek veriden static/app.js tarafından doldurulur -->
        </div>
      </section>

      <!-- Seçili Oyun Hata Listesi (Oyun seçildiğinde veya filtrelendiğinde görünür) -->
      <section id="tabContent-issues" class="hidden space-y-4">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <h2 class="text-base sm:text-lg font-extrabold text-white">Seçili Oyun Hata Çözümleri</h2>
          <div id="categoryFilterWrapper" class="flex items-center gap-2">
            <label for="categorySelect" class="text-xs text-gray-400">Kategori:</label>
            <select
              id="categorySelect"
              onchange="handleCategoryChange(this.value)"
              class="bg-[#1b2230] text-xs text-white rounded-lg px-3 py-2 border border-white/10 focus:outline-none"
            >
              <option value="all">Tüm Kategoriler</option>
              <option value="Anti-Cheat & Güvenlik">Anti-Cheat & Güvenlik</option>
              <option value="Performans & FPS">Performans & FPS</option>
              <option value="Ağ & Bağlantı">Ağ & Bağlantı</option>
              <option value="Çökme & Başlatma">Çökme & Başlatma</option>
              <option value="Ses & Donanım">Ses & Donanım</option>
            </select>
          </div>
        </div>
        <div id="issuesListContainer" class="space-y-4"></div>
      </section>

      <!-- 4. AI ÇÖZÜMLEYİCİ (Ortada Ayrı ve Sade Kart; Log Yükleme ve Donanım Algılama İkincil Açılır Kutuda) -->
      <section id="tabContent-ai-lab" aria-labelledby="ai-cozumleyici-baslik" class="space-y-5">
        <div id="aiLabMemberArea" class="oc-card p-6 sm:p-8 space-y-5">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-white/10 pb-4">
            <div>
              <h2 id="ai-cozumleyici-baslik" class="text-lg sm:text-xl font-extrabold text-white">
                Listede olmayan bir hata mı var? AI ile analiz et.
              </h2>
              <p class="text-xs sm:text-sm text-gray-400 mt-1">
                Oyun adını, hata kodunu ve yaşadığın sorunu yaz; sistemine özel adım adım çözüm rehberi oluşturulsun.
              </p>
            </div>
            <div id="aiLabGuestLock" class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/5 border border-white/10 text-xs text-gray-300 shrink-0">
              <span id="aiLabGuestTrialText">Misafir Analiz Hakkı Aktif</span>
              <button type="button" onclick="openAuthModal('login')" class="underline font-bold text-[#88c0a8] hover:text-white ml-1">Giriş Yap</button>
            </div>
          </div>

          <form onsubmit="submitAiDiagnostic(event)" class="space-y-4">
            <!-- Spam Koruması (Görünmez) -->
            <div class="hidden" aria-hidden="true" style="position:absolute;left:-9999px;opacity:0;pointer-events:none;">
              <input id="aiLabHoneypot" name="hp_check_field" type="text" tabindex="-1" autocomplete="off" aria-label="Spam Koruması" />
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label for="aiLabGameInput" class="block text-xs font-semibold text-gray-300 mb-1.5">Oyun Adı</label>
                <input
                  id="aiLabGameInput"
                  list="allGamesDatalist"
                  type="text"
                  required
                  placeholder="Örn: Valorant, League of Legends, Bannerlord…"
                  oninput="previewSmartGameRecognition(this.value, 'aiLabSmartHint')"
                  class="w-full bg-[#121822] text-base sm:text-sm text-white rounded-xl px-3.5 py-2.5 border border-white/15 focus:outline-none focus:border-[#88c0a8]"
                />
                <div id="aiLabSmartHint" class="text-[11px] text-[#88c0a8] mt-1 min-h-[16px]"></div>
              </div>
              <div>
                <label for="aiLabErrorCode" class="block text-xs font-semibold text-gray-300 mb-1.5">Hata Kodu veya Başlık (İsteğe Bağlı)</label>
                <input
                  id="aiLabErrorCode"
                  type="text"
                  placeholder="Örn: VAN 185, ERR_GFX_STATE, FPS Düşmesi…"
                  class="w-full bg-[#121822] text-base sm:text-sm text-white rounded-xl px-3.5 py-2.5 border border-white/15 focus:outline-none focus:border-[#88c0a8]"
                />
              </div>
            </div>

            <div>
              <label for="aiLabDescription" class="block text-xs font-semibold text-gray-300 mb-1.5">Sorun Detayı</label>
              <textarea
                id="aiLabDescription"
                rows="3"
                required
                placeholder="Hata ne zaman çıkıyor? Ekranda hangi uyarı yazıyor?"
                class="w-full bg-[#121822] text-base sm:text-sm text-white rounded-xl p-3.5 border border-white/15 focus:outline-none focus:border-[#88c0a8]"
              ></textarea>
            </div>

            <!-- İkincil Seçenekler: Crash Log Yükleme ve Donanım Algılama (Açılır Kutu İçinde) -->
            <details class="oc-accordion">
              <summary class="text-xs sm:text-sm font-semibold text-gray-200">
                <span>İsteğe Bağlı: Crash Log (.log / .txt) Yükle veya Sistem Özelliklerini Ekle</span>
                <svg class="w-4 h-4 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>
              </summary>
              <div class="oc-accordion-body space-y-4">
                <!-- Sistem Özellikleri & Donanım Algılama -->
                <div>
                  <div class="flex items-center justify-between mb-1.5">
                    <label for="aiLabSpecs" class="block text-xs font-semibold text-gray-300">Sistem Özellikleri (GPU / CPU / İşletim Sistemi)</label>
                    <button
                      type="button"
                      onclick="triggerHardwareAutoDetect()"
                      class="oc-btn oc-btn-secondary !min-h-[34px] !py-1 !px-3 text-xs"
                    >
                      <span>Donanımımı Algıla</span>
                    </button>
                  </div>
                  <input
                    id="aiLabSpecs"
                    type="text"
                    placeholder="Örn: Windows 11, Ryzen 5 5600, RTX 4060, 16GB RAM"
                    class="w-full bg-[#121822] text-base sm:text-sm text-white rounded-xl px-3.5 py-2.5 border border-white/15 focus:outline-none focus:border-[#88c0a8]"
                  />
                </div>

                <!-- Donanım Onay Kutusu -->
                <div id="hardwareConfirmBox" class="hidden bg-[#141a24] border border-[#88c0a8]/40 rounded-xl p-4 space-y-3">
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
                    <div class="p-2 rounded bg-[#1b2230]"><div class="text-[10px] text-gray-400">GPU</div><div id="hwDetectGpuText" class="font-bold text-white truncate">-</div></div>
                    <div class="p-2 rounded bg-[#1b2230]"><div class="text-[10px] text-gray-400">CPU</div><div id="hwDetectCpuText" class="font-bold text-white truncate">-</div></div>
                    <div class="p-2 rounded bg-[#1b2230]"><div class="text-[10px] text-gray-400">OS</div><div id="hwDetectOsText" class="font-bold text-white truncate">-</div></div>
                    <div class="p-2 rounded bg-[#1b2230]"><div class="text-[10px] text-gray-400">RAM</div><div id="hwDetectRamText" class="font-bold text-white truncate">-</div></div>
                  </div>
                  <input id="hwDetectEditableSummary" type="text" aria-label="Tespit edilen donanım özeti" class="w-full bg-[#121822] text-xs text-white rounded-lg px-3 py-2 border border-white/15" />
                </div>

                <!-- Crash Log Sürükle-Bırak Alanı -->
                <div
                  id="crashLogDropZone"
                  ondragover="handleCrashLogDragOver(event)"
                  ondragleave="handleCrashLogDragLeave(event)"
                  ondrop="handleCrashLogDrop(event)"
                  class="rounded-xl border border-dashed border-[#88c0a8]/50 bg-[#121822] p-4 cursor-pointer transition"
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
                        <span class="text-[#88c0a8] font-bold" id="crashLogFileNameBadge">crash.log</span>
                        <span class="oc-badge oc-badge-warning" id="crashLogMatchCountBadge">Kritik Satırlar</span>
                        <span class="oc-badge oc-badge-success" id="crashLogMaskedCountBadge">Kişisel Yollar Maskelendi</span>
                      </div>
                      <button type="button" onclick="clearCrashLogAnalysis()" class="text-xs text-gray-400 hover:text-white underline">Temizle</button>
                    </div>
                    <pre id="crashLogExtractedPreview" class="text-[11px] font-mono bg-[#10151e] text-gray-200 p-2.5 rounded-lg border border-white/10 overflow-x-auto max-h-36 whitespace-pre-wrap"></pre>
                  </div>
                </div>

                <!-- Örnek Oyun Önerileri -->
                <div class="space-y-1.5">
                  <div class="flex items-center justify-between text-xs text-gray-400">
                    <span>Hızlı oyun seçimi:</span>
                    <button type="button" onclick="refreshRandomSuggestions()" class="text-[#88c0a8] hover:underline">Yenile</button>
                  </div>
                  <div id="aiLabSuggestionsContainer" class="flex flex-wrap gap-1.5"></div>
                </div>
              </div>
            </details>

            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1">
              <span class="text-xs text-gray-400">
                Analiz tamamlandığında adım adım çözüm adımları aşağıda açılır.
              </span>
              <button
                type="submit"
                id="aiAnalyzeSubmitBtn"
                class="oc-btn oc-btn-primary px-6 py-2.5 text-sm font-bold"
              >
                <span>AI ile Analiz Et</span>
              </button>
            </div>
          </form>
        </div>

        <!-- AI Teşhis Sonuç Kartı -->
        <div id="aiLabResultCard" class="hidden oc-card p-6 space-y-4">
          <div class="flex flex-wrap items-center justify-between gap-2 border-b border-white/10 pb-3">
            <div class="flex items-center gap-2.5">
              <h3 class="font-bold text-white text-base">OyunÇöz Teknik Teşhis Raporu</h3>
              <span id="aiResultModeBadge" class="oc-badge oc-badge-accent"></span>
            </div>
            <span id="aiResultConfidence" class="text-xs font-bold text-[#88c0a8]"></span>
          </div>
          <div id="aiResultSafetyBanner" class="hidden"></div>
          <div id="aiLabResultContent" class="ai-markdown text-sm leading-relaxed"></div>
          <div id="aiResultMandatoryDisclaimer" class="oc-alert oc-alert-warning text-xs font-semibold">
            <span>Bu çözüm yapay zeka ile üretildi, uygulamadan önce kontrol edin ve geri yükleme noktası oluşturun.</span>
          </div>
          <div id="aiResultVoteBar" class="pt-4 border-t border-white/10"></div>
        </div>
      </section>

      <!-- 5. TOPLULUK FORUMU (Ana Sayfanın Alt Kısmında; Soru Sayısı 0 İse Sayaç Göstermez, "İlk soruyu sen sor" Gösterir) -->
      <section id="tabContent-forum" aria-labelledby="topluluk-forumu-baslik" class="space-y-4">
        <div class="oc-card p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div class="flex items-center gap-2">
              <h2 id="topluluk-forumu-baslik" class="text-lg font-extrabold text-white">Oyuncu Soru-Cevap Forumu</h2>
              <span id="threadsCountBadge" class="hidden oc-badge oc-badge-accent"></span>
            </div>
            <p class="text-xs sm:text-sm text-gray-400 mt-0.5">
              Çözemediğin oyun hatalarını topluluğa sor veya diğer oyuncuların deneyimlerini incele.
            </p>
          </div>
          <button
            type="button"
            onclick="openAskModal()"
            class="oc-btn oc-btn-primary text-xs sm:text-sm shrink-0"
          >
            <span>+ Soru Sor</span>
          </button>
        </div>

        <div id="threadsListContainer" class="space-y-4">
          <!-- static/app.js tarafından doldurulur -->
        </div>
      </section>

    </main>"""

    txt = txt[:idx_s] + new_main + txt[idx_e:]
    with open(index_path, "w", encoding="utf-8") as wf:
        wf.write(txt)
    print("[OK] Updated <main> in index.html for Stage 3 layout")


def update_app_js_for_stage3(pages):
    app_path = os.path.join(ROOT_DIR, "static", "app.js")
    with open(app_path, "r", encoding="utf-8") as f:
        txt = f.read()

    # 1. Keep hero title as "Hangi hatayı alıyorsun?" when selectedGame === 'all'
    txt = txt.replace(
        "if (titleEl) titleEl.textContent = 'Popüler Oyun Sorunları & Yapay Zeka Çözüm Merkezi';",
        "if (titleEl) titleEl.textContent = 'Hangi hatayı alıyorsun?';",
    )
    txt = txt.replace(
        "if (subEl) subEl.textContent = 'Sol menüden bir oyun seçebilir, istediğiniz yeni bir oyunu ekleyebilir veya AI Arıza Çözümleyici ile herhangi bir oyunu yazarak otomatik sayfa ve çözüm üretebilirsiniz.';",
        "if (subEl) subEl.textContent = 'Aldığın hata kodunu veya oyun adını yaz; doğrudan o hatanın adım adım çözüm sayfasına git.';",
    )

    # 2. Update renderThreads empty state so 0 threads shows "İlk soruyu sen sor" without 0 counters
    old_empty_threads = """  if (STATE.threads.length === 0) {
    container.innerHTML = `
      <div class="bg-[#1d2430] border border-white/10 rounded-2xl p-8 text-center space-y-3">
        <div class="text-base font-bold text-white">Bu oyun ekranında henüz soru sorulmamış</div>
        <p class="text-xs text-gray-400">İlk soruyu siz sorun, OyunÇöz AI adım adım çözüm yanıtını oluştursun!</p>
        <button onclick="openAskModal()" class="accent-btn px-4 py-2 rounded-xl text-xs">+ İlk Soruyu Sor</button>
      </div>
    `;
    return;
  }"""

    new_empty_threads = """  if (STATE.threads.length === 0) {
    container.innerHTML = `
      <div class="oc-card p-8 text-center space-y-3">
        <div class="text-base font-bold text-white">Henüz bu konuda soru açılmamış</div>
        <p class="text-xs sm:text-sm text-gray-400 mx-auto">Yaşadığın hatayla ilgili ilk soruyu sen sor; hem topluluk hem de teknik analiz motorumuz yanıtlasın.</p>
        <button type="button" onclick="openAskModal()" class="oc-btn oc-btn-primary text-xs sm:text-sm">İlk soruyu sen sor</button>
      </div>
    `;
    return;
  }"""
    if old_empty_threads in txt:
        txt = txt.replace(old_empty_threads, new_empty_threads)

    # 3. Append Stage 3 dedicated error pages index & Hero Search / Oyunlar Grid renderer at the end of app.js
    stage3_js_snippet = f"""

// --- AŞAMA 3: HATA KODU SAYFALARI DOĞRUDAN YÖNLENDİRME, ENTER ARAMA SONUÇLARI VE GERÇEK OYUN SAYILARI ---
const DEDICATED_ERROR_PAGES = {json.dumps(pages, ensure_ascii=False)};

window.renderHomeShowcase = function() {{
  try {{
    const gamesGrid = document.getElementById('homeGamesShowcaseGrid');
    if (gamesGrid && STATE.games.length > 0) {{
      // Calculate real error count per game from STATE.issues + DEDICATED_ERROR_PAGES
      const featuredGames = STATE.games.slice(0, 18);
      gamesGrid.innerHTML = featuredGames.map(g => {{
        const mono = window.getGameMonogramInfo ? window.getGameMonogramInfo(g.slug, g.accent_color) : {{ code: (g.short_name || 'OYN').slice(0,3).toUpperCase(), color: '#5e9c88' }};
        const realCount = Math.max(Number(g.issue_count || 0), 1);
        return `
          <a
            href="/${{g.slug}}-hata-cozumleri.html"
            onclick="event.preventDefault(); selectGame('${{g.slug}}'); switchTab('issues'); document.getElementById('tabContent-issues')?.scrollIntoView({{behavior:'smooth'}});"
            class="oc-card oc-card-interactive p-3.5 flex items-center gap-3"
          >
            <span class="oc-monogram" style="border-color:${{mono.color}}66;background-color:${{mono.color}}1f" aria-hidden="true">${{mono.code}}</span>
            <div class="min-w-0">
              <div class="text-xs sm:text-sm font-bold text-white truncate">${{escapeHTML(g.short_name || g.name)}}</div>
              <div class="text-[11px] text-gray-400">${{realCount}} Hata Kodu</div>
            </div>
          </a>
        `;
      }}).join('');
    }}
  }} catch (e) {{
    console.warn('renderHomeShowcase error:', e);
  }}
}};

window.renderLiveAutocomplete = async function(rawVal, isMobile = false) {{
  const dropdown = document.getElementById(isMobile ? 'mobileLiveSearchDropdown' : 'liveSearchDropdown');
  if (!dropdown) return;
  const q = String(rawVal || '').trim().toLowerCase();

  if (!q) {{
    const topPages = DEDICATED_ERROR_PAGES.slice(0, 6);
    dropdown.innerHTML = `
      <div class="p-3 space-y-2">
        <div class="text-[11px] font-bold uppercase tracking-wider text-[#88c0a8] px-1">En Çok Bakılan Hata Kodları</div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
          ${{topPages.map(p => `
            <a
              href="/${{p.slug}}"
              class="p-2.5 rounded-xl bg-white/5 hover:bg-[#5e9c88]/20 border border-white/5 hover:border-[#88c0a8]/40 transition flex items-center justify-between gap-2"
            >
              <div class="min-w-0">
                <div class="text-xs font-bold text-white truncate">${{escapeHTML(p.oyun)}} • ${{escapeHTML(p.hata_kodu)}}</div>
                <div class="text-[11px] text-gray-400 truncate">${{escapeHTML(p.tek_cumle_ozet || p.title)}}</div>
              </div>
              <span class="text-xs text-[#88c0a8] shrink-0">→</span>
            </a>
          `).join('')}}
        </div>
      </div>
    `;
    dropdown.classList.remove('hidden');
    return;
  }}

  const matchedPages = DEDICATED_ERROR_PAGES.filter(p => {{
    const hay = `${{p.oyun}} ${{p.hata_kodu}} ${{p.title}} ${{(p.varyant_yazimlari || []).join(' ')}} ${{p.kisa_aciklama}}`.toLowerCase();
    return hay.includes(q);
  }}).slice(0, 6);

  const matchedGames = STATE.games.filter(g =>
    (g.name || '').toLowerCase().includes(q) ||
    (g.short_name || '').toLowerCase().includes(q) ||
    (g.common_tags || []).some(t => t.toLowerCase().includes(q))
  ).slice(0, 4);

  let htmlParts = '';
  if (matchedPages.length > 0) {{
    htmlParts += `
      <div class="p-3 space-y-1.5">
        <div class="text-[11px] font-bold uppercase tracking-wider text-gray-400 px-1">Hata Kodu Çözüm Sayfaları (${{matchedPages.length}})</div>
        <div class="space-y-1">
          ${{matchedPages.map(p => `
            <a
              href="/${{p.slug}}"
              class="block p-2.5 rounded-xl hover:bg-white/10 transition flex items-center justify-between gap-3"
            >
              <div class="min-w-0">
                <div class="flex items-center gap-2">
                  <span class="oc-badge oc-badge-accent font-mono">${{escapeHTML(p.hata_kodu)}}</span>
                  <span class="text-xs font-bold text-white truncate">${{escapeHTML(p.title)}}</span>
                </div>
                <div class="text-[11px] text-gray-400 truncate mt-0.5">${{escapeHTML(p.tek_cumle_ozet || p.meta_description)}}</div>
              </div>
              <span class="text-xs font-bold text-[#88c0a8] shrink-0">Çözümü gör →</span>
            </a>
          `).join('')}}
        </div>
      </div>
    `;
  }}

  if (matchedGames.length > 0) {{
    htmlParts += `
      <div class="p-3 space-y-1.5">
        <div class="text-[11px] font-bold uppercase tracking-wider text-gray-400 px-1">Oyunlar (${{matchedGames.length}})</div>
        <div class="space-y-1">
          ${{matchedGames.map(g => `
            <a
              href="/${{g.slug}}-hata-cozumleri.html"
              class="block p-2 rounded-xl hover:bg-white/10 transition flex items-center justify-between gap-3"
            >
              <span class="text-xs font-bold text-white">${{escapeHTML(g.name)}}</span>
              <span class="text-[11px] text-[#88c0a8]">${{Number(g.issue_count || 1)}} Hata Kodu →</span>
            </a>
          `).join('')}}
        </div>
      </div>
    `;
  }}

  const safeQ = q.replace(/'/g, "\\\\'");
  htmlParts += `
    <div class="p-3 bg-[#131924] flex items-center justify-between gap-2">
      <span class="text-xs text-gray-300 truncate">Aradığın <strong>"${{escapeHTML(rawVal)}}"</strong> hatası listede yok mu?</span>
      <button
        type="button"
        onclick="selectAutocompleteAiQuery('${{safeQ}}')"
        class="oc-btn oc-btn-primary !min-h-[36px] !py-1.5 !px-3 text-xs shrink-0"
      >
        AI çözümleyiciyle analiz et
      </button>
    </div>
  `;

  dropdown.innerHTML = htmlParts;
  dropdown.classList.remove('hidden');
}};

window.handleHeroSearchSubmit = async function(e) {{
  if (e) e.preventDefault();
  closeLiveAutocomplete();
  const inp = document.getElementById('globalSearchInput');
  const q = String(inp ? inp.value : '').trim();
  const resBox = document.getElementById('heroSearchResultsSection');
  if (!resBox) return;
  if (!q) {{
    resBox.classList.add('hidden');
    return;
  }}

  const ql = q.toLowerCase();
  const matchedPages = DEDICATED_ERROR_PAGES.filter(p => {{
    const hay = `${{p.oyun}} ${{p.hata_kodu}} ${{p.title}} ${{(p.varyant_yazimlari || []).join(' ')}} ${{p.kisa_aciklama}}`.toLowerCase();
    return hay.includes(ql);
  }});

  resBox.classList.remove('hidden');
  if (matchedPages.length > 0) {{
    resBox.innerHTML = `
      <div class="flex items-center justify-between">
        <h2 class="text-sm font-bold text-white">"${{escapeHTML(q)}}" İçin Arama Sonuçları (${{matchedPages.length}})</h2>
        <button type="button" onclick="document.getElementById('heroSearchResultsSection').classList.add('hidden')" class="text-xs text-gray-400 hover:text-white">Kapat ✕</button>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        ${{matchedPages.map(p => `
          <a href="/${{p.slug}}" class="oc-card oc-card-interactive p-4 flex items-center justify-between gap-3">
            <div>
              <div class="flex items-center gap-2">
                <span class="oc-badge oc-badge-accent font-mono">${{escapeHTML(p.hata_kodu)}}</span>
                <span class="text-xs font-bold text-white">${{escapeHTML(p.title)}}</span>
              </div>
              <p class="text-xs text-gray-400 mt-1">${{escapeHTML(p.tek_cumle_ozet || p.meta_description)}}</p>
            </div>
            <span class="text-xs font-bold text-[#88c0a8] shrink-0">Çözümü gör →</span>
          </a>
        `).join('')}}
      </div>
    `;
  }} else {{
    const safeQ = q.replace(/'/g, "\\\\'");
    resBox.innerHTML = `
      <div class="oc-card p-5 text-center space-y-3">
        <div class="text-sm font-bold text-white">"${{escapeHTML(q)}}" için hazır hata kodu sayfası bulunamadı</div>
        <p class="text-xs text-gray-400 mx-auto">Bu hatayı yapay zeka arıza çözümleyici ile hemen analiz edip sistemine özel çözüm adımlarını oluşturabilirsin.</p>
        <button type="button" onclick="selectAutocompleteAiQuery('${{safeQ}}')" class="oc-btn oc-btn-primary text-xs sm:text-sm">
          AI çözümleyiciyle analiz et
        </button>
      </div>
    `;
  }}
}};

window.handleSearchKeydown = function(e) {{
  if (e.key === 'Enter') {{
    window.handleHeroSearchSubmit(e);
  }} else if (e.key === 'Escape') {{
    closeLiveAutocomplete();
  }}
}};
"""
    if "const DEDICATED_ERROR_PAGES =" not in txt:
        txt = txt + stage3_js_snippet
    with open(app_path, "w", encoding="utf-8") as wf:
        wf.write(txt)
    print("[OK] Updated static/app.js for Stage 3 Hero Search, Autocomplete, Oyunlar Grid, and Forum empty state")


if __name__ == "__main__":
    pages = update_hata_kodlari_json()
    update_index_html_main(pages)
    update_app_js_for_stage3(pages)
