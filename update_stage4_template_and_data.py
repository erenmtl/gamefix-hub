# -*- coding: utf-8 -*-
"""
AŞAMA 4: data/hata_kodlari.json içine 'hizli_cozum' ve çoklu senaryo olan sayfalara 'senaryolar' alanlarını ekler.
"""
import os
import json

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(ROOT_DIR, "data", "hata_kodlari.json")

QUICK_FIX_BY_SLUG = {
    "lol/van-185": {
        "baslik": "En Olası İlk Adım: Açık Riot Süreçlerini Kapatıp Oturumu Yenileyin",
        "aciklama": "Riot İstemcisi'nden 'Oturumu Kapat' diyerek çıkın, Görev Yöneticisi'nden RiotClientServices.exe ile vgtray.exe süreçlerini sonlandırıp istemciyi Yönetici olarak yeniden başlatın.",
        "komut": "taskkill /F /IM RiotClientServices.exe /IM LeagueClient.exe"
    },
    "lol/van-128": {
        "baslik": "En Olası İlk Adım: Windows Sınama Modunu Kapatıp Bilgisayarı Yeniden Başlatın",
        "aciklama": "Yönetici Komut İstemi'nde (CMD) sınama modunu ve bütünlük kontrolü devre dışı bayrağını kapatıp sistemi yeniden başlatın.",
        "komut": "bcdedit /set testsigning off && bcdedit /deletevalue nointegritychecks"
    },
    "valorant/van-9003": {
        "baslik": "En Olası İlk Adım: BIOS'ta CSM Kapatıp Secure Boot Anahtarlarını Yükleyin",
        "aciklama": "BIOS > Boot menüsünden CSM (Compatibility Support Module) ayarını Disabled yapın ve Secure Boot > Key Management altından 'Install Default Secure Boot Keys / Restore Factory Keys' seçeneğini onaylayın.",
        "komut": "powershell -Command \"Confirm-SecureBootUEFI\""
    },
    "valorant/van-1067": {
        "baslik": "En Olası İlk Adım: BIOS'tan TPM 2.0 (fTPM / PTT) Açıp vgc Servisini Başlatın",
        "aciklama": "tpm.msc ekranında TPM 2.0 hazır görünmüyorsa BIOS'tan AMD fTPM veya Intel PTT ayarını Enabled yapın; ardından Windows Hizmetleri'nde vgc servisini Otomatik moda alıp başlatın.",
        "komut": "sc config vgc start= auto && net start vgc"
    },
    "gta-v/err-gfx-d3d-init": {
        "baslik": "En Olası İlk Adım: settings.xml İçinde DirectX 11 (DX_Version = 2) Ayarlayın",
        "aciklama": "Belgeler\\Rockstar Games\\GTA V\\settings.xml dosyasını Not Defteri ile açıp <DX_Version value=\"2\" /> satırını 2 olarak kaydedin ve oyun klasöründeki eski d3d11.dll / dxgi.dll mod kalıntılarını silin.",
        "komut": ""
    },
    "fivem/harita-yuklenmiyor-texture-loss": {
        "baslik": "En Olası İlk Adım: Extended Texture Budget Çubuğunu %50-%65 Seviyesine Çekin",
        "aciklama": "FiveM Grafik ayarlarının en altındaki 'Extended Texture Budget' çubuğunu sıfırda bırakmayın; ekran kartı belleğinize göre orta seviyeye (%50-%65) yükseltin.",
        "komut": ""
    },
    "rdr2/err-gfx-state": {
        "baslik": "En Olası İlk Adım: Belgeler Klasöründeki Bozuk sga_ Dosyalarını Silin",
        "aciklama": "Belgeler\\Rockstar Games\\Red Dead Redemption 2\\Settings klasöründeki sga_vulkan_final_init ile başlayan 3 önbellek dosyasını silip oyunu yeniden başlatın.",
        "komut": ""
    },
    "bannerlord/d3d-device-context-map": {
        "baslik": "En Olası İlk Adım: ProgramData Altındaki Bozuk Shaders Klasörünü Silin",
        "aciklama": "C:\\ProgramData\\Mount and Blade II Bannerlord\\Shaders klasörünü tamamen silip Steam üzerinden oyun dosyalarının bütünlüğünü doğrulayın.",
        "komut": ""
    },
    "fc-25/anticheat-hatasi": {
        "baslik": "En Olası İlk Adım: EA App Recovery ile Önbelleği Temizleyip AntiCheat'i Onarın",
        "aciklama": "EA App > App Recovery > Clear Cache işlemini uygulayın ve FC 25 kurulum dizinindeki EAAntiCheat.Installer.exe aracıyla Uninstall All / Install yapın.",
        "komut": ""
    },
    "black-myth-wukong/out-of-video-memory": {
        "baslik": "En Olası İlk Adım: Sanal Belleği 16384 MB Yapın ve -dx11 Parametresiyle Başlatın",
        "aciklama": "Windows Sanal Bellek (Pagefile) boyutunu 16384 MB olarak ayarlayın ve Steam Başlatma Seçenekleri kutusuna -dx11 parametresini ekleyin.",
        "komut": "-dx11"
    },
    "cs2/vac-oturum-dogrulanamadi": {
        "baslik": "En Olası İlk Adım: SteamService.exe /repair Çalıştırıp Dosyaları Doğrulayın",
        "aciklama": "Steam'i kapatıp Yönetici CMD üzerinde SteamService.exe /repair komutunu çalıştırın, ardından Steam'i Yönetici olarak açıp CS2 dosya bütünlüğünü doğrulayın.",
        "komut": "\"C:\\Program Files (x86)\\Common Files\\Steam\\SteamService.exe\" /repair"
    },
    "cs2/packet-burst-fps-dusmesi": {
        "baslik": "En Olası İlk Adım: Oyun İçi Ağ Arabelleğini '1 Paket' Yapın ve Eski Kodları Silin",
        "aciklama": "CS2 Ayarlar > Oyun altından 'Paket kaybını / gecikmeyi dengelemek için arabelleğe alma' seçeneğini '1 Paket' yapın ve Steam başlatma seçeneklerindeki eski -threads / -high kodlarını silin.",
        "komut": ""
    },
    "minecraft/exit-code-1": {
        "baslik": "En Olası İlk Adım: Uyumsuz Modları Çıkarın ve Yerleşik Java 21 Yolunu Sıfırlayın",
        "aciklama": "%appdata%\\.minecraft\\mods klasöründeki uyumsuz .jar modlarını kontrol edin ve Minecraft Launcher > Yüklemeler > Düzenle altından Java Yürütülebilir Dosyası yolunu varsayılana sıfırlayın.",
        "komut": "java -version"
    }
}

SCENARIOS_BY_SLUG = {
    "valorant/van-9003": [
        {
            "id": "asus-msi",
            "etiket": "ASUS / MSI Anakart",
            "baslik": "ASUS ve MSI BIOS Üzerinden Secure Boot Aktifleştirme",
            "aciklama": "ASUS anakartlarda BIOS > Boot > CSM > Launch CSM: Disabled yapın; ardından Secure Boot > OS Type: Windows UEFI Mode seçip Key Management > Install Default Secure Boot Keys onaylayın. MSI anakartlarda Settings > Advanced > Windows OS Configuration > BIOS UEFI/CSM Mode: UEFI seçip Secure Boot > Enroll all Factory Default keys adımını uygulayın."
        },
        {
            "id": "gigabyte-asrock",
            "etiket": "Gigabyte / ASRock Anakart",
            "baslik": "Gigabyte ve ASRock BIOS Üzerinden Secure Boot Aktifleştirme",
            "aciklama": "Gigabyte anakartlarda BIOS > Boot > CSM Support: Disabled yapın; Secure Boot menüsünde durum 'Not Active' ise Secure Boot Mode'u Custom yapıp 'Restore Factory Keys' seçin. ASRock anakartlarda Boot > CSM: Disabled yapıp Security > Secure Boot > Install default Secure Boot keys seçeneğine tıklayın."
        }
    ],
    "valorant/van-1067": [
        {
            "id": "amd-ftpm",
            "etiket": "AMD Ryzen İşlemci (fTPM)",
            "baslik": "AMD Ryzen Sistemlerde BIOS fTPM 2.0 Açma",
            "aciklama": "BIOS'a girip Advanced > AMD fTPM Configuration menüsüne geçin ve 'AMD CPU fTPM' (veya Security Device Support) ayarını Enabled yaparak F10 ile kaydedin."
        },
        {
            "id": "intel-ptt",
            "etiket": "Intel Core İşlemci (PTT)",
            "baslik": "Intel Sistemlerde BIOS PTT (Platform Trust Technology) Açma",
            "aciklama": "BIOS'a girip Settings > Security > Trusted Computing (veya Peripherals) menüsüne geçin ve 'Intel Platform Trust Technology (PTT)' ayarını Enabled yaparak F10 ile kaydedin."
        }
    ],
    "black-myth-wukong/out-of-video-memory": [
        {
            "id": "amd-veya-genel",
            "etiket": "AMD Ryzen / Genel Sistemler",
            "baslik": "Sanal Bellek (16384 MB) ve -dx11 Başlatma Modu",
            "aciklama": "sysdm.cpl > Gelişmiş > Performans > Sanal Bellek altından Başlangıç ve En Büyük boyutu 16384 MB yapın ve Steam Başlatma Seçenekleri'ne -dx11 parametresini ekleyin."
        },
        {
            "id": "intel-13-14-nesil",
            "etiket": "Intel 13. / 14. Nesil (i7 / i9 K)",
            "baslik": "0x12B Mikro Kodlu BIOS Güncellemesi ve Geçici Güç Tasarrufu Modu",
            "aciklama": "13. veya 14. nesil Intel işlemcilerde Oodle gölgelendirici açma çökmesini önlemek için anakartınızın 0x12B microcode (Intel Default Settings) BIOS güncellemesini kurun veya ilk derleme sırasında Windows Güç Seçenekleri'nden geçici olarak 'Güç Tasarrufu' modunu seçin."
        }
    ]
}


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    for p in data.get("pages", []):
        slug = p["slug"]
        if slug in QUICK_FIX_BY_SLUG:
            p["hizli_cozum"] = QUICK_FIX_BY_SLUG[slug]
        if slug in SCENARIOS_BY_SLUG:
            p["senaryolar"] = SCENARIOS_BY_SLUG[slug]
        else:
            p.pop("senaryolar", None)

    with open(DATA_FILE, "w", encoding="utf-8") as wf:
        json.dump(data, wf, ensure_ascii=False, indent=2)
    print("[OK] Enriched data/hata_kodlari.json with hizli_cozum and senaryolar")


if __name__ == "__main__":
    main()
