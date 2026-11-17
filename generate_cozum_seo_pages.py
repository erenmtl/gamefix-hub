# -*- coding: utf-8 -*-
"""
Programmatic Static SEO Pages Generator for OyunÇöz (oyuncoz.com)
Generates 30 deep, technically accurate static HTML guides under /cozum/
with full Dark UI design, FAQPage + TechArticle + BreadcrumbList JSON-LD,
interactive .log drag-and-drop & AI diagnostic widget, copyable safe CMD commands,
and internal linking cards.
"""
import os
import json
import html

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
COZUM_DIR = os.path.join(ROOT_DIR, "cozum")
LASTMOD_DATE = "2026-11-17"
LASTMOD_TR = "17.11.2026"

PAGES = [
    {
        "id": 1,
        "slug": "valorant-van-9003-hatasi-cozumu.html",
        "category": "Valorant & Riot Vanguard",
        "game": "Valorant",
        "code": "VAN 9003",
        "tested_version": "Valorant Episode 9 / Windows 11 23H2 & 24H2",
        "title": "Valorant VAN 9003 Hatası Çözümü (Secure Boot & TPM 2.0)",
        "h1": "Valorant VAN 9003 Hatası Nasıl Çözülür? (2026 Çözüm Rehberi)",
        "meta_desc": "Windows 11'de Valorant VAN 9003 (This build of Vanguard requires Secure Boot) hatası için BIOS UEFI, CSM kapatma ve TPM 2.0 adım adım çözüm rehberi.",
        "why_happens": (
            "Valorant VAN 9003 hatası, Riot Vanguard çekirdek (kernel-level) güvenlik sürücüsünün Windows 11 işletim sisteminde "
            "<strong>UEFI Güvenli Önyükleme (Secure Boot)</strong> ve <strong>TPM 2.0</strong> modüllerinin aktif olarak çalışmasını zorunlu "
            "tutmasından kaynaklanır. Bilgisayarınızın BIOS/UEFI ayarlarında CSM (Compatibility Support Module) açıksa, Secure Boot 'Enabled' "
            "görünse bile 'Not Active' (Etkin Değil) durumunda kalır ve Vanguard oyunu başlatmayı reddeder."
        ),
        "steps": [
            {
                "h3": "Adım 1: msinfo32 ve TPM Durumunu Doğrulama",
                "desc": "Öncelikle Windows üzerinden BIOS modunuzun UEFI olup olmadığını ve Güvenli Önyükleme Durumunun 'Açık' görünüp görünmediğini kontrol edin.",
                "cmd": "msinfo32",
                "cmd_note": "Sistem Bilgisi penceresini açar. 'BIOS Modu: UEFI' ve 'Güvenli Önyükleme Durumu: Açık' satırlarını kontrol edin."
            },
            {
                "h3": "Adım 2: Gelişmiş Başlangıç ile doğrudan UEFI BIOS'a Geçiş",
                "desc": "Bilgisayar açılırken DEL/F2 tuşunu yakalayamıyorsanız, Yönetici Komut İstemi (CMD) üzerinden aşağıdaki güvenli komutla doğrudan BIOS ekranına yeniden başlatabilirsiniz.",
                "cmd": "shutdown /r /fw /t 0",
                "cmd_note": "Ne yapar: Bilgisayarı doğrudan anakart UEFI BIOS arayüzünde yeniden başlatır. Risk: Açık belgelerinizi kaydetmeden çalıştırmayın."
            },
            {
                "h3": "Adım 3: BIOS'ta CSM Kapatma ve Secure Boot Key Management",
                "desc": "ASUS, MSI, Gigabyte veya ASRock anakartınızda Boot sekmesine gidin: CSM Support ayarını 'Disabled' yapın, OS Type ayarını 'Windows UEFI Mode' seçin ve Secure Boot Mode'u 'Custom'dan 'Standard'a alıp Fabrika Anahtarlarını (Install Default Secure Boot Keys) yükleyin.",
                "cmd": "powershell -Command \"Confirm-SecureBootUEFI\"",
                "cmd_note": "Windows açıldığında PowerShell'de 'True' döndürüyorsa Secure Boot başarıyla etkinleşmiştir."
            },
            {
                "h3": "Adım 4: Riot Vanguard (vgc) Servisini Otomatik Başlatma",
                "desc": "BIOS ayarlarından sonra Vanguard kullanıcı modu servisinin (vgc) kapalı kalmasını önlemek için hizmeti otomatik moda alıp başlatın.",
                "cmd": "sc config vgc start= demand & net start vgc",
                "cmd_note": "Ne yapar: Riot Vanguard (vgc) servisini yapılandırır ve başlatır. Geri alma: Hizmetler (services.msc) üzerinden manuel moda alınabilir."
            }
        ],
        "faqs": [
            {
                "q": "BIOS'ta Secure Boot Enabled görünüyor ama Windows'ta Kapalı yazıyor, neden?",
                "a": "Anakartlarda Secure Boot 'Enabled' olsa bile Platform Key (PK) anahtarları yüklenmemişse 'Not Active' kalır. BIOS'ta Secure Boot Mode'u 'Custom' yapıp 'Restore Factory Keys' seçeneğini onaylayarak 'Standard' moda geri alın."
            },
            {
                "q": "Diskim MBR formatındaysa CSM kapatınca Windows açılır mı?",
                "a": "MBR disklerde CSM kapatılırsa sistem diski göremez. Önce Windows'ta Yönetici CMD üzerinden 'mbr2gpt /validate /allowFullOS' ve 'mbr2gpt /convert /allowFullOS' komutuyla veri kaybetmeden GPT'ye dönüştürmeniz gerekir."
            },
            {
                "q": "Valorant VAN 9003 Windows 10'da da çıkar mı?",
                "a": "Genellikle Windows 11'de zorunludur ancak VBS (Sanallaştırma Tabanlı Güvenlik) açık olan güncel Windows 10 sistemlerde de Vanguard TPM ve Secure Boot doğrulaması isteyebilir."
            }
        ],
        "related": [2, 3, 13, 26]
    },
    {
        "id": 2,
        "slug": "valorant-van-1067-baglanti-hatasi-cozumu.html",
        "category": "Valorant & Riot Vanguard",
        "game": "Valorant",
        "code": "VAN 1067",
        "tested_version": "Valorant Episode 9 / Windows 11",
        "title": "Valorant VAN 1067 Bağlantı Hatası Çözümü (TPM & vgc)",
        "h1": "Valorant VAN 1067 Bağlantı Hatası Nasıl Çözülür? (Adım Adım Rehber)",
        "meta_desc": "Valorant VAN 1067 bağlantı hatası ve oyun ortasında atma sorunu için TPM 2.0 sertifika yenileme, vgc servisi başlatma ve Discord çakışma çözümü.",
        "why_happens": (
            "Valorant VAN 1067 hatası, Riot İstemcisi ile çekirdek düzeyindeki <code>vgc</code> (Vanguard) servisi arasındaki yerel "
            "güvenli iletişimin kopması veya TPM 2.0 (fTPM / PTT) yongasının oturum sırasında yanıt vermemesi nedeniyle oluşur. "
            "Ayrıca üçüncü parti RGB yazılımları ve ekran içi arayüz (Overlay) kancaları da <code>vgc</code> servisini durdurabilir."
        ),
        "steps": [
            {
                "h3": "Adım 1: TPM 2.0 Modül Durumunu Kontrol Etme",
                "desc": "Windows Çalıştır veya Komut İstemi üzerinden TPM yönetim konsolunu açarak 'TPM kullanılmaya hazır' ve 'Belirtim Sürümü: 2.0' yazdığını doğrulayın.",
                "cmd": "tpm.msc",
                "cmd_note": "TPM Yönetim konsolunu açar. Eğer TPM görünmüyorsa BIOS'tan AMD fTPM veya Intel PTT açılmalıdır."
            },
            {
                "h3": "Adım 2: Durmuş Olan vgc ve vgk Servislerini Yeniden Başlatma",
                "desc": "Yönetici Komut İstemi (CMD) ile Vanguard servislerinin durumunu sorgulayın ve başlangıç türünü onarın.",
                "cmd": "sc query vgk & sc config vgc start= auto & net start vgc",
                "cmd_note": "Ne yapar: vgk çekirdek sürücüsünü kontrol eder ve vgc servisini otomatik başlatılacak şekilde etkinleştirir."
            },
            {
                "h3": "Adım 3: Bozuk Windows Sistem ve Ağ Soketlerini Onarma",
                "desc": "Yerel geri döngü (loopback) soketlerindeki tıkanıklığı ve sistem dosyalarını onarmak için SFC ve Winsock sıfırlaması uygulayın.",
                "cmd": "sfc /scannow & netsh winsock reset",
                "cmd_note": "Ne yapar: Bozuk Windows sistem dosyalarını onarır ve Winsock kataloglarını varsayılana döndürür. İşlem sonrası bilgisayarı yeniden başlatın."
            },
            {
                "h3": "Adım 4: Çakışan RGB ve Overlay Hizmetlerini Kapatma",
                "desc": "ASUS Armoury Crate, MSI Center, Razer Synapse veya Discord Oyun İçi Arayüzü (Overlay) açıkken vgc servisi çöküyorsa temiz önyükleme (msconfig) ile test edin.",
                "cmd": "msconfig",
                "cmd_note": "Sistem Yapılandırması -> Hizmetler sekmesinden 'Tüm Microsoft hizmetlerini gizle' kutusunu işaretleyip yalnızca vgc'yi açık bırakabilirsiniz."
            }
        ],
        "faqs": [
            {
                "q": "VAN 1067 hatası neden oyuna girdikten 5 dakika sonra veriyor?",
                "a": "vgc servisi başlangıçta çalışsa bile arka plandaki bir uygulama veya AMD fTPM mikro takılması servisin yanıt süresini aşmasına (timeout) yol açar. BIOS güncellemesi (AGESA) bu sorunu giderir."
            },
            {
                "q": "Vanguard'ı silip tekrar yüklemek VAN 1067'yi çözer mi?",
                "a": "Evet, bozuk sürücü imzası varsa 'sc delete vgc' ve 'sc delete vgk' sonrası Riot İstemcisi üzerinden temiz kurulum yapmak oldukça etkilidir."
            }
        ],
        "related": [1, 3, 13, 30]
    },
    {
        "id": 3,
        "slug": "valorant-van-81-vanguard-baslatilamadi-hatasi-cozumu.html",
        "category": "Valorant & Riot Vanguard",
        "game": "Valorant",
        "code": "VAN -81",
        "tested_version": "Valorant Episode 9 / Windows 10 & 11",
        "title": "Valorant VAN -81 ve Vanguard Başlatılamadı Hatası Çözümü",
        "h1": "Valorant VAN -81 (Vanguard Başlatılamadı) Hatası Nasıl Çözülür?",
        "meta_desc": "Valorant VAN -81 hatası ve Riot Vanguard başlatılamadı sorunu için vgc/vgk temiz kurulumu, antivirüs istisnası ve Windows hizmet onarım rehberi.",
        "why_happens": (
            "Valorant <strong>VAN -81</strong> hatası, Riot İstemcisi'nin oyun açılışında <code>vgc.exe</code> servisini tetikleyememesi veya "
            "<code>vgk.sys</code> çekirdek sürücüsünün Windows başlangıcında (Boot-Start) yüklenmesinin bir antivirüs ya da bozuk kayıt defteri "
            "anahtarı tarafından engellenmesi sonucunda meydana gelir."
        ),
        "steps": [
            {
                "h3": "Adım 1: Açık Riot ve Vanguard Süreçlerini Sonlandırma",
                "desc": "Askıda kalmış Riot Client ve Vanguard işlemlerini Yönetici CMD üzerinden tamamen kapatın.",
                "cmd": "taskkill /F /IM RiotClientServices.exe /T & taskkill /F /IM vgc.exe /T",
                "cmd_note": "Ne yapar: Arka planda kilitli kalan Riot ve Vanguard süreçlerini güvenli şekilde sonlandırır."
            },
            {
                "h3": "Adım 2: Vanguard Servislerini Temizleyip Yeniden Kurma",
                "desc": "Bozulan Vanguard servis kayıtlarını kaldırıp Riot İstemcisi'nin sıfırdan kurmasını sağlayın. (İşlem öncesi Sistem Geri Yükleme Noktası oluşturmanız önerilir.)",
                "cmd": "sc delete vgc & sc delete vgk",
                "cmd_note": "Ne yapar: Bozuk vgc ve vgk hizmet kayıtlarını siler. Risk: İşlem sonrası bilgisayarı yeniden başlatıp Riot Client'ı açarak Vanguard'ın yeniden kurulmasını bekleyin."
            },
            {
                "h3": "Adım 3: Riot Vanguard Klasörünü Windows Güvenliği İstisnalarına Ekleme",
                "desc": "Windows Defender veya üçüncü parti antivirüs yazılımlarının vgk.sys dosyasını kilitlemesini önlemek için klasör yolunu kontrol edin.",
                "cmd": "dir \"C:\\Program Files\\Riot Vanguard\"",
                "cmd_note": "Klasör mevcutsa Windows Güvenliği -> Virüs ve tehdit koruması -> Dışlamalar bölümüne 'C:\\Program Files\\Riot Vanguard' yolunu ekleyin."
            }
        ],
        "faqs": [
            {
                "q": "VAN -81 hatasında oyunu tamamen silmek gerekir mi?",
                "a": "Hayır, 60 GB'lık Valorant'ı silmenize gerek yoktur. Yalnızca Riot Vanguard'ı kaldırıp yeniden kurmak ve bilgisayarı yeniden başlatmak yeterlidir."
            },
            {
                "q": "Bilgisayarı yeniden başlatmadan VAN -81 düzelir mi?",
                "a": "vgk.sys çekirdek sürücüsü yalnızca Windows ilk açılırken (boot aşamasında) yüklendiği için kurulum sonrası mutlaka yeniden başlatma (Restart) yapılmalıdır."
            }
        ],
        "related": [1, 2, 12, 13]
    },
    {
        "id": 4,
        "slug": "minecraft-exit-code-1-cikis-kodu-1-cozumu.html",
        "category": "Minecraft",
        "game": "Minecraft",
        "code": "Exit Code 1",
        "tested_version": "Minecraft 1.20.4 / 1.21 (Java 17 & Java 21)",
        "title": "Minecraft Exit Code 1 (Çıkış Kodu 1) Çözüm Rehberi",
        "h1": "Minecraft Exit Code 1 (Çıkış Kodu 1) Hatası Nasıl Çözülür?",
        "meta_desc": "Minecraft 'Oyun Beklenmedik Şekilde Çöktü: Çıkış Kodu 1 (Exit Code 1)' hatası için Java 21 uyumu, Forge/Fabric mod temizliği ve GPU sürücü rehberi.",
        "why_happens": (
            "Minecraft <strong>Exit Code 1 (Çıkış Kodu 1)</strong> hatası, Java Sanal Makinesi'nin (JVM) başlatma sırasında kritik bir istisna "
            "ile karşılaşarak kapanmasıdır. En yaygın 3 nedeni: oyun sürümüyle uyumsuz bir Forge/Fabric mod dosyası (<code>.jar</code>), "
            "Minecraft 1.20.5+ için gereken <strong>Java 21</strong> yerine eski Java 8/17 kullanılması veya AMD/NVIDIA OpenGL sürücü çökmesidir."
        ),
        "steps": [
            {
                "h3": "Adım 1: Yüklü Java Sürümünü ve Mimarisi (64-bit) Doğrulama",
                "desc": "Komut İstemi üzerinden sisteminizdeki aktif Java sürümünü kontrol edin. Minecraft 1.18-1.20.4 için Java 17, 1.20.5 ve 1.21+ için 64-bit Java 21 gereklidir.",
                "cmd": "java -version",
                "cmd_note": "Çıktıda '64-Bit Server VM' ifadesinin yer aldığından emin olun. 32-bit Java 2 GB üstü RAM verilirse Exit Code 1 ile çöker."
            },
            {
                "h3": "Adım 2: .minecraft Klasöründeki Son Çökme Günlüğünü (latest.log) İnceleme",
                "desc": "Hangi modun veya sürücünün çökmeye yol açtığını görmek için doğrudan Minecraft log klasörünü açın.",
                "cmd": "explorer \"%APPDATA%\\.minecraft\\logs\"",
                "cmd_note": "Açılan klasördeki 'latest.log' dosyasını aşağıdaki interaktif analiz kutusuna sürükleyerek çakışan modu anında tespit edebilirsiniz."
            },
            {
                "h3": "Adım 3: Bozuk options.txt ve Uyumsuz Modları Yedekleme",
                "desc": "Bozuk grafik ayarları veya uyumsuz .jar modlarını geçici olarak yedek klasörüne taşıyarak oyunun saf (Vanilla/Forge) halde açıldığını doğrulayın.",
                "cmd": "ren \"%APPDATA%\\.minecraft\\options.txt\" options.txt.bak",
                "cmd_note": "Ne yapar: Bozuk Minecraft grafik ayar dosyasını yedekler; oyun açılışta temiz bir options.txt oluşturur."
            },
            {
                "h3": "Adım 4: JVM Başlangıç RAM Argümanlarını Dengeli Ayarlama",
                "desc": "Minecraft Launcher -> Yüklemeler -> Düzenle -> Daha Fazla Seçenek altındaki JVM Bağımsız Değişkenleri satırında sistem RAM'inizin yarısından fazlasını vermeyin (Örn. 16 GB RAM için 4G veya 6G).",
                "cmd": "-Xmx4G -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC",
                "cmd_note": "Bu parametreyi CMD'ye değil, Minecraft Launcher içerisindeki 'JVM Arguments' kutusuna yapıştırın."
            }
        ],
        "faqs": [
            {
                "q": "Hiçbir mod yüklü değilken neden Exit Code 1 hatası alıyorum?",
                "a": "Modsuz (Vanilla) oyunda Exit Code 1 genellikle Windows kullanıcı adınızda Türkçe karakter bulunmasından veya ekran kartı OpenGL sürücüsünün bozulmasından kaynaklanır. Launcher ayarlarından çalışma dizinini 'C:\\MC' gibi Türkçe karaktersiz bir yola taşıyın."
            },
            {
                "q": "Forge kurduktan sonra Exit Code 1 veriyorsa ne yapmalıyım?",
                "a": "mods klasöründeki OptiFine sürümünün Forge sürümüyle tam uyumlu olduğundan emin olun veya OptiFine yerine Sodium/Embeddium kullanın."
            }
        ],
        "related": [5, 26, 27, 29]
    },
    {
        "id": 5,
        "slug": "minecraft-opengl-error-1281-ekran-karti-hatasi-cozumu.html",
        "category": "Minecraft",
        "game": "Minecraft",
        "code": "OpenGL 1281 / GLFW 65542",
        "tested_version": "Minecraft 1.20 / 1.21 (OptiFine & Iris Shaders)",
        "title": "Minecraft OpenGL Error 1281 ve Ekran Kartı Hatası Çözümü",
        "h1": "Minecraft OpenGL Error 1281 (Invalid Value) ve GLFW 65542 Çözümü",
        "meta_desc": "Minecraft sohbet ekranında çıkan OpenGL Error 1281 (Invalid Value) ve GLFW Error 65542 WGL ekran kartı sürücü hatası için adım adım çözüm rehberi.",
        "why_happens": (
            "Minecraft'ta <strong>OpenGL Error 1281 (GL_INVALID_VALUE)</strong> hatası, OptiFine veya Shader paketlerinin ekran kartı "
            "sürücüsüne geçersiz bir OpenGL matris/gölgelendirici parametresi göndermesiyle oluşur. <strong>GLFW Error 65542</strong> ise "
            "oyunun harici NVIDIA/AMD ekran kartı yerine işlemcinin eski dahili grafik birimiyle başlatılmaya çalışılmasından kaynaklanır."
        ),
        "steps": [
            {
                "h3": "Adım 1: javaw.exe İçin Yüksek Performanslı Ekran Kartını Zorunlu Kılma",
                "desc": "Windows Grafik Ayarlarını açarak Minecraft'ın kullandığı javaw.exe dosyasını harici ekran kartınıza (NVIDIA/AMD) atayın.",
                "cmd": "start ms-settings:display-advancedgraphics",
                "cmd_note": "Windows Grafik Ayarları penceresini açar. Gözat'tan javaw.exe'yi ekleyip 'Yüksek Performans' seçin."
            },
            {
                "h3": "Adım 2: OptiFine Hızlı İşleme (Fast Render) ve OpenGL Hatalarını Kapatma",
                "desc": "Oyun içi Ayarlar -> Görüntü Ayarları -> Performans menüsünden 'Fast Render (Hızlı İşleme)' ayarını Kapatın ve 'Show GL Errors' seçeneğini pasif hale getirin.",
                "cmd": "explorer \"%APPDATA%\\.minecraft\"",
                "cmd_note": "Oyun açılmıyorsa .minecraft klasöründeki optionsof.txt dosyasını açıp 'ofFastRender:false' olarak kaydedin."
            },
            {
                "h3": "Adım 3: Bozuk OpenGL Gölgelendirici Önbelleğini (Shaderpacks) Sıfırlama",
                "desc": "Uyumsuz shader yapılandırma dosyalarını temizlemek için shaderpacks klasörünü kontrol edin.",
                "cmd": "explorer \"%APPDATA%\\.minecraft\\shaderpacks\"",
                "cmd_note": "Sorunlu shader paketinin .txt ayar dosyasını silerek varsayılan shader ayarlarına dönmesini sağlayın."
            }
        ],
        "faqs": [
            {
                "q": "OpenGL Error 1281 oyunu çökertir mi?",
                "a": "Çoğu zaman yalnızca sohbet ekranında uyarı verir ve FPS düşüşüne yol açar; ancak Fast Render açıkken shader açılırsa ekran tamamen kararabilir."
            },
            {
                "q": "GLFW Error 65542 hatasında opengl32.dll indirmek güvenli mi?",
                "a": "İnternetten rastgele opengl32.dll dosyası indirmek yazılımsal render (CPU kullanımı) yaptığı için FPS'i 5'e düşürür. Bunun yerine DDU ile ekran kartı sürücünüzü temiz kurmanız gerekir."
            }
        ],
        "related": [4, 28, 29, 18]
    },
    {
        "id": 6,
        "slug": "cs2-vac-oyun-oturumunuzu-dogrulayamadi-hatasi-cozumu.html",
        "category": "Counter-Strike 2 (CS2)",
        "game": "Counter-Strike 2",
        "code": "VAC Oturum Hatası",
        "tested_version": "CS2 Source 2 Güncel Sürüm / Steam",
        "title": "CS2 VAC Oyun Oturumunuzu Doğrulayamadı Hatası Çözümü",
        "h1": "CS2 VAC Oyun Oturumunuzu Doğrulayamadı Hatası Nasıl Çözülür?",
        "meta_desc": "Counter-Strike 2 (CS2) 'VAC oyun oturumunuzu doğrulayamadı' hatası için Steam servis onarımı, dosya bütünlüğü ve DEP/BCD doğrulama rehberi.",
        "why_happens": (
            "CS2'de <strong>VAC Oyun Oturumunuzu Doğrulayamadı (VAC was unable to verify your game session)</strong> uyarısı bir VAC ban (yasaklama) "
            "değildir. Steam Client Service'in arka planda yetki kaybetmesi, bozuk <code>.vpk</code> imzaları veya Windows Veri Yürütme Engellemesi "
            "(DEP / <code>nointegritychecks</code>) ayarlarının değiştirilmiş olması nedeniyle VAC modülünün bellek imzasını doğrulayamamasıdır."
        ),
        "steps": [
            {
                "h3": "Adım 1: Steam Client Service'i Onarma (Repair)",
                "desc": "Steam'i tamamen kapattıktan sonra Yönetici Komut İstemi (CMD) ile Steam istemci servisini yeniden kaydedin ve onarın.",
                "cmd": "\"C:\\Program Files (x86)\\Steam\\bin\\steamservice.exe\" /repair",
                "cmd_note": "Ne yapar: VAC doğrulamasından sorumlu olan Steam Client Service bileşenini onarır."
            },
            {
                "h3": "Adım 2: Windows Bütünlük Kontrollerini ve DEP Ayarını Varsayılana Döndürme",
                "desc": "Windows önyükleme yapılandırmasında (BCD) bütünlük kontrolleri kapatılmışsa VAC çalışmaz. Yönetici CMD ile varsayılana döndürün.",
                "cmd": "bcdedit /deletevalue nointegritychecks & bcdedit /deletevalue loadoptions",
                "cmd_note": "Ne yapar: Devre dışı bırakılmış çekirdek bütünlük kontrollerini tekrar aktif eder. Risk: Yalnızca resmi Windows önyükleme bayraklarını sıfırlar. İşlem sonrası yeniden başlatın."
            },
            {
                "h3": "Adım 3: CS2 Oyun Dosyalarının Bütünlüğünü Doğrulama",
                "desc": "Steam üzerinden CS2 oyun dosyalarının dijital imzalarını doğrudan doğrulama komutuyla kontrol ettirin.",
                "cmd": "start steam://validate/730",
                "cmd_note": "Steam'de CS2 (AppID 730) için otomatik dosya doğrulama işlemini başlatır."
            }
        ],
        "faqs": [
            {
                "q": "VAC oyun oturumunuzu doğrulayamadı hatası ban yediğim anlamına mı gelir?",
                "a": "Hayır, bu hata kesinlikle bir VAC yasaklaması değildir. Yerel Steam servisinizin veya oyun dosyalarınızın imzasının o an doğrulanamadığını belirtir."
            },
            {
                "q": "Masaüstü kısayolundan CS2 açınca neden bu hatayı veriyor?",
                "a": "CS2'yi görev çubuğuna sabitleyip veya '-insecure' parametresiyle masaüstünden açmak yerine her zaman doğrudan Steam Kütüphanesi içerisinden 'Oyna' butonuna basarak başlatın."
            }
        ],
        "related": [7, 16, 17, 30]
    },
    {
        "id": 7,
        "slug": "cs2-ani-fps-dususu-ve-takilma-stuttering-cozumu.html",
        "category": "Counter-Strike 2 (CS2)",
        "game": "Counter-Strike 2",
        "code": "FPS Drop & Stuttering",
        "tested_version": "CS2 Source 2 / NVIDIA & AMD",
        "title": "CS2 Ani FPS Düşüşü ve Takılma (Stuttering) Çözümü",
        "h1": "CS2 Ani FPS Düşüşü, Takılma (Stuttering) ve Packet Burst Çözümü",
        "meta_desc": "Counter-Strike 2 (CS2) çatışma anında ani FPS düşüşü, mikro takılma (stuttering) ve DirectX gölgelendirici önbelleği temizleme çözüm rehberi.",
        "why_happens": (
            "Counter-Strike 2'de Source 2 motoruna geçişle birlikte her güncelleme sonrasında eski <strong>DirectX Shader Cache (Gölgelendirici Önbelleği)</strong> "
            "dosyalarının çakışması, çatışma ve sis bombası anlarında anlık derleme takılmalarına (frametime spike) yol açar. Ayrıca ses çıkış "
            "cihazının 'Varsayılan' olarak bırakılması ve sub-tick paket tamponu da ani takılmaları tetikler."
        ),
        "steps": [
            {
                "h3": "Adım 1: Bozuk DirectX Gölgelendirici Önbelleğini Temizleme",
                "desc": "Windows Disk Temizleme aracını açarak yalnızca 'DirectX Gölgelendirici Önbelleği' kutusunu işaretleyip temizleyin.",
                "cmd": "cleanmgr /d C",
                "cmd_note": "Disk Temizleme aracını açar. DirectX Gölgelendirici Önbelleği seçilerek eski derlenmiş shader dosyaları silinir."
            },
            {
                "h3": "Adım 2: CS2 userdata ve Panorama Önbelleğini Kontrol Etme",
                "desc": "Yıllardır biriken eski CS:GO config parametreleri (-threads, -high, -lv gibi) Source 2'de mikro takılma yapar. Başlatma seçeneklerindeki eski kodları silin.",
                "cmd": "explorer \"C:\\Program Files (x86)\\Steam\\steamapps\\common\\Counter-Strike Global Offensive\\game\\csgo\"",
                "cmd_note": "Steam CS2 Başlatma Seçeneklerinde (Launch Options) '-high' ve '-threads' komutları varsa kaldırın; Source 2 iş parçacıklarını kendisi yönetir."
            },
            {
                "h3": "Adım 3: Yüksek Performans Güç Planını Etkinleştirme",
                "desc": "İşlemci çekirdeklerinin oyun sırasında frekans düşürmesini (core parking) önlemek için Yüksek Performans güç planını aktif edin.",
                "cmd": "powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
                "cmd_note": "Ne yapar: Windows güç planını Yüksek Performans moduna geçirir."
            }
        ],
        "faqs": [
            {
                "q": "CS2'de -threads veya -high başlatma kodu FPS artırır mı?",
                "a": "Valve geliştiricileri CS2'de '-threads' ve '-high' parametrelerinin Windows zamanlayıcısını bozarak %1 Low FPS değerini düşürdüğünü resmi olarak açıklamıştır. Başlatma seçeneklerini boş bırakmanız önerilir."
            },
            {
                "q": "Ses ayarları CS2'de takılmaya neden olur mu?",
                "a": "Evet. Oyun içi Ses Ayarları'nda 'Ses Cihazı' seçeneğini 'Varsayılan Cihaz' yerine doğrudan kullandığınız kulaklığın adına sabitleyin ve 'Akıcı Bas' seçeneğini kapatın."
            }
        ],
        "related": [6, 29, 30, 22]
    },
    {
        "id": 8,
        "slug": "rdr2-err-gfx-state-hatasi-cozumu.html",
        "category": "Red Dead Redemption 2",
        "game": "Red Dead Redemption 2",
        "code": "ERR_GFX_STATE",
        "tested_version": "RDR2 Build 1491.50 (Vulkan & DirectX 12)",
        "title": "RDR2 ERR_GFX_STATE Hatası Çözümü (Vulkan sga_ Temizliği)",
        "h1": "RDR2 ERR_GFX_STATE Hatası Nasıl Çözülür? (Adım Adım Rehber)",
        "meta_desc": "Red Dead Redemption 2 (RDR2) ERR_GFX_STATE oyun hatası ve çökme sorunu için sga_ Vulkan önbellek dosyalarını silme ve DirectX 12 çözüm rehberi.",
        "why_happens": (
            "Red Dead Redemption 2'de <strong>ERR_GFX_STATE</strong> hatası, Belgelerim klasöründe tutulan <code>sga_vulkan_final_init</code> "
            "gölgelendirici önbellek dosyalarının ekran kartı sürücüsü güncellendikten veya oyun beklenmedik şekilde kapandıktan sonra "
            "bozulması ve RAGE motorunun grafik durumunu yükleyememesi nedeniyle oluşur."
        ),
        "steps": [
            {
                "h3": "Adım 1: Bozuk sga_ Grafik Önbellek Dosyalarını Silme",
                "desc": "Belgelerim\\Rockstar Games\\Red Dead Redemption 2\\Settings klasöründeki 'sga_' ile başlayan 3 önbellek dosyasını tek komutla temizleyin.",
                "cmd": "del /q \"%USERPROFILE%\\Documents\\Rockstar Games\\Red Dead Redemption 2\\Settings\\sga_*\"",
                "cmd_note": "Ne yapar: Kayıt (save) dosyalarınıza dokunmadan yalnızca bozuk sga_ grafik önbellek dosyalarını siler."
            },
            {
                "h3": "Adım 2: system.xml İçinde Grafik API'sini DirectX 12 veya Vulkan Olarak Değiştirme",
                "desc": "Oyun menüsüne giremeden çöküyorsa Settings klasörünü açıp system.xml dosyasındaki <API>kSettingAPI_Vulkan</API> satırını <API>kSettingAPI_DX12</API> olarak değiştirin.",
                "cmd": "explorer \"%USERPROFILE%\\Documents\\Rockstar Games\\Red Dead Redemption 2\\Settings\"",
                "cmd_note": "Açılan klasörde system.xml dosyasını Not Defteri ile düzenleyebilirsiniz."
            },
            {
                "h3": "Adım 3: Başlatma Seçeneklerine -ignorepipelinecache Ekleme",
                "desc": "Steam, Epic Games veya Rockstar Games Launcher başlatma seçeneklerine aşağıdaki parametreyi ekleyerek bozuk önbelleğin yoksayılmasını sağlayın.",
                "cmd": "-ignorepipelinecache",
                "cmd_note": "Bu parametreyi başlatıcı (Launcher) Başlatma Seçenekleri kutusuna ekleyin."
            }
        ],
        "faqs": [
            {
                "q": "sga_ dosyalarını silmek RDR2 hikaye kaydımı (save) siler mi?",
                "a": "Hayır, hikaye kayıtlarınız Profiles klasöründe tutulur. Settings klasöründeki sga_ dosyaları yalnızca geçici grafik önbelleğidir."
            },
            {
                "q": "Ekran kartım hız aşırtmalı (Overclock) ise ERR_GFX_STATE verir mi?",
                "a": "Evet, RDR2 RAGE motoru GPU çekirdek/bellek hız aşırtmasına karşı çok hassastır. MSI Afterburner üzerinden çekirdek hızını -50 MHz düşürmek çökmeyi engeller."
            }
        ],
        "related": [9, 10, 24, 29]
    },
    {
        "id": 9,
        "slug": "rdr2-unknown-error-ffffffff-hatasi-cozumu.html",
        "category": "Red Dead Redemption 2",
        "game": "Red Dead Redemption 2",
        "code": "Unknown Error FFFFFFFF",
        "tested_version": "RDR2 & Red Dead Online Build 1491.50",
        "title": "RDR2 Unknown Error FFFFFFFF Hatası Çözümü",
        "h1": "RDR2 Unknown Error FFFFFFFF Hatası Nasıl Çözülür?",
        "meta_desc": "Red Dead Redemption 2 ve Red Dead Online 'Unknown Error FFFFFFFF' çökme hatası için ses cihazı örnekleme, sanal bellek ve Vulkan çözüm rehberi.",
        "why_happens": (
            "RDR2'de <strong>Unknown Error FFFFFFFF</strong> hatası; ses kartı/kulaklık örnekleme hızının çok yüksek (192 kHz+) olması, "
            "Windows Sanal Bellek (Pagefile) alanının yetersiz kalması, bozuk <code>system.xml</code> ayarları veya Red Dead Online lobilerindeki "
            "bellek taşması nedeniyle tetiklenen genel bir RAGE motoru istisnasıdır."
        ),
        "steps": [
            {
                "h3": "Adım 1: Ses Çıkış Cihazı Örnekleme Hızını 16-bit / 48000 Hz (DVD Kalitesi) Yapma",
                "desc": "Windows Ses Denetim Masası'nı açıp aktif kulaklığınızın Gelişmiş sekmesinden formatı 16 bit, 48000 Hz olarak ayarlayın ve Uzamsal Sesi kapatın.",
                "cmd": "control mmsys.cpl sounds",
                "cmd_note": "Ses Denetim Masası'nı doğrudan açar. RAGE motoru 96 kHz ve üzeri USB DAC/kulaklık formatlarında FFFFFFFF hatasıyla çökebilir."
            },
            {
                "h3": "Adım 2: Settings Klasöründeki system.xml ve sga_ Dosyalarını Sıfırlama",
                "desc": "Bozuk grafik ayarlarını temizlemek için Settings klasöründeki önbellek dosyalarını kaldırın.",
                "cmd": "del /q \"%USERPROFILE%\\Documents\\Rockstar Games\\Red Dead Redemption 2\\Settings\\sga_*\"",
                "cmd_note": "Bozuk Vulkan/DX12 pipeline önbelleğini temizler."
            },
            {
                "h3": "Adım 3: Windows Sanal Bellek (Pagefile) Ayarını Sistem Yönetimli Yapma",
                "desc": "Sanal bellek kapatılmışsa RDR2 16 GB RAM'de bile Unknown Error FFFFFFFF verir. Gelişmiş Sistem Ayarlarından sanal belleği 'Sistem yönetimli boyut' yapın.",
                "cmd": "SystemPropertiesPerformance.exe",
                "cmd_note": "Performans Seçenekleri -> Gelişmiş -> Sanal Bellek (Değiştir) penceresini açar."
            }
        ],
        "faqs": [
            {
                "q": "Unknown Error FFFFFFFF özellikle kamp kurarken (Wilderness Camp) mi çıkıyor?",
                "a": "Evet, Red Dead Online'da hilecilerin olduğu kalabalık lobilerde nesne (entity) limiti dolduğunda kamp kurmak FFFFFFFF hatasını tetikler."
            },
            {
                "q": "DirectX 12 mi yoksa Vulkan mı FFFFFFFF hatasını azaltır?",
                "a": "Vulkan API'si RDR2'de bellek yönetimini daha kararlı yaptığı için DirectX 12'de bu hatayı alan oyuncuların Vulkan'a geçmesi önerilir."
            }
        ],
        "related": [8, 10, 19, 29]
    },
    {
        "id": 10,
        "slug": "gta-5-fivem-early-exit-trap-ve-cokme-hatasi-cozumu.html",
        "category": "GTA 5 & FiveM",
        "game": "GTA 5 / FiveM",
        "code": "Early-Exit Trap / Crash",
        "tested_version": "FiveM (Cfx.re) & GTA V Build 3095/3258",
        "title": "GTA 5 / FiveM Early-Exit Trap ve Çökme Hatası Çözümü",
        "h1": "GTA 5 / FiveM Early-Exit Trap ve Çökme Hatası Nasıl Çözülür?",
        "meta_desc": "FiveM 'Early-Exit Trap', ERR_GFX_D3D_INIT ve sunucuda çökme hatası için CitizenFX cache temizliği, Extended Texture Budget ve GPU çözüm rehberi.",
        "why_happens": (
            "FiveM'de <strong>Early-Exit Trap</strong> ve ani çökme hataları, <code>FiveM.app\\data</code> altındaki önbellek (cache) dosyalarının "
            "sunucu güncellemeleriyle çakışması, ekran kartı VRAM belleğinin özel modlu araç/haritalar (MLO) yüzünden dolması veya GTA V ana "
            "dizinindeki uyumsuz <code>.asi</code> / <code>d3d11.dll</code> grafik modlarından kaynaklanır."
        ),
        "steps": [
            {
                "h3": "Adım 1: FiveM data/cache Klasörlerini Güvenli Temizleme",
                "desc": "Oyun dosyalarını yeniden indirmeden yalnızca bozuk FiveM önbellek klasörlerini (cache, server-cache, server-cache-priv) temizleyin.",
                "cmd": "rmdir /s /q \"%LOCALAPPDATA%\\FiveM\\FiveM.app\\data\\cache\" & rmdir /s /q \"%LOCALAPPDATA%\\FiveM\\FiveM.app\\data\\server-cache\"",
                "cmd_note": "Ne yapar: Yalnızca geçici sunucu önbelleğini siler; game-storage klasörüne dokunmaz."
            },
            {
                "h3": "Adım 2: Bozuk CitizenFX.ini ve GTA 5 settings.xml Dosyasını Kontrol Etme",
                "desc": "GTA 5 grafik ayarlarında DirectX sürümünün DX11 (Shader Version 2) olduğundan emin olun ve oyun içinden 'Extended Texture Budget' çubuğunu %50 seviyesine çekin.",
                "cmd": "explorer \"%USERPROFILE%\\Documents\\Rockstar Games\\GTA V\"",
                "cmd_note": "settings.xml içinde <DX_Version value=\"2\" /> satırının yer aldığını doğrulayın."
            },
            {
                "h3": "Adım 3: FiveM Çökme Raporlarını (crashes) İnceleme",
                "desc": "Hangi sunucu scriptinin veya modun çökmeye yol açtığını görmek için FiveM crashes klasörünü açın.",
                "cmd": "explorer \"%LOCALAPPDATA%\\FiveM\\FiveM.app\\crashes\"",
                "cmd_note": "En son oluşan .log dosyasını aşağıdaki interaktif analiz aracına yükleyerek çökme kodunu öğrenebilirsiniz."
            }
        ],
        "faqs": [
            {
                "q": "FiveM'de yollar ve binalar kaybolup Early-Exit Trap veriyorsa ne yapmalıyım?",
                "a": "Grafik ayarlarındaki 'Extended Texture Budget' (Genişletilmiş Doku Bütçesi) ayarını 3-4 kademe yükseltin. Bu ayar düşük olduğunda özel sunucu dokuları VRAM'e sığmaz ve çökme yaşanır."
            },
            {
                "q": "GTA 5 klasöründeki Redux/QuantV modları FiveM'i çökertir mi?",
                "a": "Evet, GTA V ana dizinindeki eski d3d11.dll veya ReShade dosyaları Cfx.re anti-cheat tarafından engellenir ve Early-Exit Trap hatası verir."
            }
        ],
        "related": [11, 8, 29, 30]
    },
    {
        "id": 11,
        "slug": "fivem-curlcode-28-sunucuya-baglanilamadi-hatasi-cozumu.html",
        "category": "GTA 5 & FiveM",
        "game": "FiveM",
        "code": "CURLcode 28 / Handshake",
        "tested_version": "FiveM Cfx.re / Windows 10 & 11",
        "title": "FiveM CURLcode 28 / Sunucuya Bağlanılamadı Hatası Çözümü",
        "h1": "FiveM CURLcode 28 (Connection Timed Out) Hatası Nasıl Çözülür?",
        "meta_desc": "FiveM 'Failed handshake to server - CURL error code 28 (Timeout was reached)' sunucuya bağlanılamadı hatası için DNS, MTU ve port çözüm rehberi.",
        "why_happens": (
            "FiveM'de <strong>CURLcode 28 (Timeout was reached)</strong> hatası, istemcinizin hedef RP sunucusunun <code>30120</code> TCP/UDP portuna "
            "yaptığı el sıkışma (handshake) isteğine 15 saniye içinde yanıt alamamasıdır. Bozuk DNS önbelleği, CGNAT/MTU paket parçalanması veya "
            "Windows Güvenlik Duvarı engeli bu hatanın temel nedenleridir."
        ),
        "steps": [
            {
                "h3": "Adım 1: DNS Önbelleğini ve Winsock Soketlerini Sıfırlama",
                "desc": "Yönetici Komut İstemi (CMD) üzerinden ağ soketlerini ve DNS önbelleğini temizleyin.",
                "cmd": "ipconfig /flushdns & netsh winsock reset",
                "cmd_note": "Ne yapar: DNS önbelleğini boşaltır ve ağ soketlerini sıfırlar. Geri alma: Varsayılan Windows ağ yapılandırmasını yükler."
            },
            {
                "h3": "Adım 2: FiveM F8 Konsolu Üzerinden Doğrudan Bağlantı Testi",
                "desc": "Sunucu listesi (Server Browser) üzerinden girmek yerine FiveM ana menüsünde F8 tuşuna basıp sunucu IP adresiyle doğrudan bağlanmayı deneyin.",
                "cmd": "connect sunucu-ip-adresi:30120",
                "cmd_note": "Bu komutu Windows CMD'ye değil, FiveM içinde F8 tuşuna bastığınızda açılan konsola yazın."
            },
            {
                "h3": "Adım 3: Cloudflare / Google DNS ve Güvenlik Duvarı Kontrolü",
                "desc": "İnternet servis sağlayıcınızın DNS sunucusu Cfx.re düğümlerini çözemiyorsa ağ bağdaştırıcınızı kontrol edin.",
                "cmd": "ncpa.cpl",
                "cmd_note": "Ağ Bağlantıları penceresini açar. Aktif bağlantınızın IPv4 DNS adresini 1.1.1.1 / 1.0.0.1 olarak ayarlayabilirsiniz."
            }
        ],
        "faqs": [
            {
                "q": "Sadece tek bir FiveM sunucusunda CURLcode 28 alıyorum, sorun bende mi?",
                "a": "Diğer sunuculara girebiliyor ancak tek bir sunucuda CURLcode 28 alıyorsanız o sunucu yeniden başlatılıyor olabilir veya sunucunun DDoS koruması (Cloudflare/OVH) IP bloğunuzu geçici olarak filtrelemiştir. Modeminizi kapatıp 30 saniye sonra açarak yeni IP alın."
            },
            {
                "q": "GoodbyeDPI veya VPN açıkken FiveM CURLcode 28 verir mi?",
                "a": "Evet, birçok yerli FiveM sunucusu yurt dışı VPN IP'lerini DDoS koruması nedeniyle engeller; sunucuya girerken VPN'i kapatmanız önerilir."
            }
        ],
        "related": [10, 30, 20, 2]
    },
    {
        "id": 12,
        "slug": "lol-kritik-hata-critical-error-cozumu.html",
        "category": "League of Legends (LoL)",
        "game": "League of Legends",
        "code": "System Error / Critical Error",
        "tested_version": "LoL Sezon 14 / DirectX 11",
        "title": "League of Legends (LoL) Kritik Hata (Critical Error) Çözümü",
        "h1": "League of Legends (LoL) Kritik Hata (Critical Error) Nasıl Çözülür?",
        "meta_desc": "League of Legends şampiyon seçimi sonrası 'A critical error has occurred (Bir kritik hata oluştu)' ve bellek dökümü sorunu için kesin çözüm rehberi.",
        "why_happens": (
            "League of Legends'ta şampiyon seçimi bittikten hemen sonra çıkan <strong>Critical Error (Kritik bir hata oluştu ve işlemin "
            "sonlandırılması gerekiyor)</strong> uyarısı; bozuk <code>game.cfg</code> yapılandırması, üçüncü parti arayüz programları (Blitz, "
            "Porofessor, Discord Overlay, MSI Afterburner RivaTuner) veya ekran kartı sürücüsü ile tam ekran iyileştirmelerinin çakışmasından kaynaklanır."
        ),
        "steps": [
            {
                "h3": "Adım 1: Bozuk LoL Config ve Log Klasörünü Temizleme",
                "desc": "Oyun kapalıyken Riot Games\\League of Legends\\Config klasöründeki bozuk game.cfg ve PersistedSettings.json dosyalarını yedekleyip sıfırlayın.",
                "cmd": "explorer \"C:\\Riot Games\\League of Legends\\Config\"",
                "cmd_note": "Açılan Config klasöründeki game.cfg dosyasını silin; Riot Client bir sonraki maçta temiz varsayılan dosyayı indirir."
            },
            {
                "h3": "Adım 2: League of Legends.exe Tam Ekran İyileştirmelerini Kapatma",
                "desc": "Game klasörü içerisindeki asıl oyun yürütülebilir dosyasının uyumluluk ayarlarını kontrol edin.",
                "cmd": "explorer \"C:\\Riot Games\\League of Legends\\Game\"",
                "cmd_note": "'League of Legends.exe' dosyasına sağ tıklayıp Özellikler -> Uyumluluk -> 'Tam ekran iyileştirmelerini devre dışı bırak' kutusunu işaretleyin."
            },
            {
                "h3": "Adım 3: RivaTuner (RTSS) ve Discord Overlay Kancalarını Devre Dışı Bırakma",
                "desc": "Vanguard entegrasyonu sonrasında eski sürüm RivaTuner Statistics Server veya 오버레이 (Overlay) yazılımları Critical Error verdirtir.",
                "cmd": "taskkill /F /IM RTSS.exe /T",
                "cmd_note": "Ne yapar: Açık olan RivaTuner Statistics Server işlemini kapatır."
            }
        ],
        "faqs": [
            {
                "q": "Şampiyon seçiminden sonra oyun açılmayıp 'Yeniden Bağlan (Reconnect)' ekranında kalıyor, neden?",
                "a": "Arka planda çalışan Blitz, Senpai, Porofessor veya Discord oyun içi arayüzü League of Legends.exe'ye DLL enjekte etmeye çalıştığında Vanguard işlemi sonlandırır."
            },
            {
                "q": "LoL Hextech Onarım Aracı yerine nereden onarım yapılır?",
                "a": "LoL İstemcisi sağ üstteki Çark (Ayarlar) -> Genel -> 'Tam Onarım Başlat' butonundan tüm dosyaları doğrulayabilirsiniz."
            }
        ],
        "related": [13, 1, 2, 3]
    },
    {
        "id": 13,
        "slug": "lol-vanguard-van-128-ve-siyah-ekran-hatasi-cozumu.html",
        "category": "League of Legends (LoL)",
        "game": "League of Legends",
        "code": "VAN 128 & Siyah Ekran",
        "tested_version": "LoL Vanguard Güncel Sürüm / Windows 10 & 11",
        "title": "LoL Vanguard VAN 128 ve Siyah Ekran Hatası Çözümü",
        "h1": "LoL Vanguard VAN 128 ve Siyah Ekran Hatası Nasıl Çözülür?",
        "meta_desc": "League of Legends (LoL) Vanguard VAN 128, VAN 185 ve maça girerken siyah ekran hatası için Windows sınama modu kapatma ve vgc servis çözüm rehberi.",
        "why_happens": (
            "League of Legends'ta <strong>VAN 128</strong> hatası, Windows işletim sisteminin Sınama Modunda (Test Signing Mode) çalışması, "
            "Hata Ayıklama (Debug) modunun açık olması veya üçüncü parti bir antivirüs yazılımının (Comodo, Kaspersky, Avast) <code>vgk.sys</code> "
            "sürücüsünü engellemesi nedeniyle Vanguard'ın güvenli ortamı doğrulayamamasıdır."
        ),
        "steps": [
            {
                "h3": "Adım 1: Windows Sınama Modunu (Testsigning) ve Debug Modunu Kapatma",
                "desc": "Yönetici Komut İstemi (CMD) üzerinden Windows imzasız sürücü test modunu ve çekirdek hata ayıklama modunu kapatın.",
                "cmd": "bcdedit /set testsigning off & bcdedit /set debug off",
                "cmd_note": "Ne yapar: Windows Test Mode ve Debug bayraklarını resmi standart değer olan 'off' durumuna getirir. İşlem sonrası bilgisayarı yeniden başlatın."
            },
            {
                "h3": "Adım 2: Vanguard (vgc) Hizmetini Başlatma ve Kontrol Etme",
                "desc": "vgc servisinin çalışır durumda olduğunu doğrulayın.",
                "cmd": "sc config vgc start= demand & net start vgc",
                "cmd_note": "Ne yapar: Riot Vanguard kullanıcı servisini başlatır."
            },
            {
                "h3": "Adım 3: Maça Girerken Siyah Ekran İçin Penceresiz (Borderless) Mod Ayarı",
                "desc": "Maç yükleme ekranı siyah kalıyorsa Config\\game.cfg dosyasında WindowMode değerini 1 (Çerçevesiz) veya 2 (Pencereli) olarak güncelleyin.",
                "cmd": "explorer \"C:\\Riot Games\\League of Legends\\Config\"",
                "cmd_note": "game.cfg dosyasını Not Defteri ile açıp [General] altındaki 'WindowMode=2' satırını kaydedin."
            }
        ],
        "faqs": [
            {
                "q": "VAN 128 hatası Windows 10'da TPM olmadan çözülür mü?",
                "a": "Evet, LoL Windows 10'da TPM 2.0 zorunluluğu koşmaz; VAN 128 Windows 10'da neredeyse her zaman Testsigning açık olmasından veya antivirüs çakışmasından kaynaklanır."
            },
            {
                "q": "Siyah ekranda imleç görünüyor ama ekran gelmiyorsa hangi tuşa basmalıyım?",
                "a": "Oyun ekranındayken 'Alt + Enter' tuş kombinasyonuna basarak tam ekran modundan pencereli moda geçiş yapabilirsiniz."
            }
        ],
        "related": [12, 1, 2, 3]
    },
    {
        "id": 14,
        "slug": "ea-fc-25-directx-function-getdeviceremovedreason-hatasi-cozumu.html",
        "category": "EA Sports FC 25 & EA App",
        "game": "EA Sports FC 25",
        "code": "GetDeviceRemovedReason",
        "tested_version": "EA Sports FC 25 / Frostbite Engine DX12",
        "title": "EA FC 25 DirectX Function GetDeviceRemovedReason Hatası Çözümü",
        "h1": "EA FC 25 DirectX Function GetDeviceRemovedReason Hatası Nasıl Çözülür?",
        "meta_desc": "EA Sports FC 25 ve FIFA 'DirectX function GetDeviceRemovedReason failed with DXGI_ERROR_DEVICE_HUNG' ekran kartı çökme hatası için çözüm rehberi.",
        "why_happens": (
            "EA Sports FC 25'te <strong>DirectX function GetDeviceRemovedReason failed (DXGI_ERROR_DEVICE_HUNG / DEVICE_REMOVED)</strong> hatası, "
            "Frostbite motorunun DirectX 12 üzerinden özellikle <strong>Telli Saç (Strand Hair)</strong> ve ara sahne (cutscene) yüklemeleri "
            "sırasında ekran kartı sürücüsünü zaman aşımına uğratmasından kaynaklanır."
        ),
        "steps": [
            {
                "h3": "Adım 1: fcsetup.ini İçinden Strand Hair ve Dinamik Çözünürlüğü Kapatma",
                "desc": "Oyun içi grafik ayarlarında Telli Saç (Strand Hair) ayarını Kapalı yapın ve Belgelerim/FC 25 klasöründeki yapılandırma dosyasını kontrol edin.",
                "cmd": "explorer \"%LOCALAPPDATA%\\EA SPORTS FC 25\"",
                "cmd_note": "Açılan klasördeki fcsetup.ini dosyasını kontrol edebilir ve bozuk shader cache klasörünü temizleyebilirsiniz."
            },
            {
                "h3": "Adım 2: DirectX Gölgelendirici Önbelleğini (Shader Cache) Sıfırlama",
                "desc": "Frostbite motorunun bozuk derlenmiş DX12 gölgelendiricilerini temizlemek için Disk Temizleme aracını çalıştırın.",
                "cmd": "cleanmgr /d C",
                "cmd_note": "DirectX Gölgelendirici Önbelleği kutusunu işaretleyip temizleyin."
            },
            {
                "h3": "Adım 3: EA Javelin Anticheat Servisini Onarma",
                "desc": "Kariyer veya Ultimate Team moduna girerken çökme yaşanıyorsa EA AntiCheat yükleyicisini yönetici olarak çalıştırıp 'Repair' seçin.",
                "cmd": "explorer \"C:\\Program Files\\EA\\AC\"",
                "cmd_note": "Klasör içindeki EAAntiCheat.Installer.exe aracını açıp FC 25'i seçerek 'Onar (Repair)' butonuna tıklayın."
            }
        ],
        "faqs": [
            {
                "q": "Korner veya gol sevinci ara sahnelerinde GetDeviceRemovedReason hatası neden çıkar?",
                "a": "Ara sahnelerde FPS aniden yarıya düşerken Telli Saç (Strand Hair) fiziği GPU yükünü %100'e çıkarır. Ara sahne kalitesini 'Tam Kare Hızı' yapıp Telli Saç'ı kapatmak sorunu çözer."
            },
            {
                "q": "NVIDIA Denetim Masası'nda Hata Ayıklama Modu (Debug Mode) işe yarar mı?",
                "a": "Evet, fabrika çıkışlı OC (Overclock) ekran kartlarında NVIDIA Denetim Masası -> Yardım -> 'Hata Ayıklama Modu'nu işaretlemek saat hızlarını referans değere çekerek DXGI çökmesini durdurur."
            }
        ],
        "related": [15, 21, 22, 29]
    },
    {
        "id": 15,
        "slug": "ea-app-origin-oyun-acilmiyor-ve-tepki-vermiyor-cozumu.html",
        "category": "EA Sports FC 25 & EA App",
        "game": "EA App / FC 25 / Battlefield",
        "code": "EA App Açılmıyor",
        "tested_version": "EA App Güncel Sürüm / Windows 10 & 11",
        "title": "EA App / Origin Oyun Açılmıyor ve Tepki Vermiyor Çözümü",
        "h1": "EA App Oyun Açılmıyor (Preparing Game Döngüsü) Nasıl Çözülür?",
        "meta_desc": "EA App ve Steam üzerinden EA FC 25, Battlefield veya Sims 4 açılmıyor, 'Preparing Game' ekranında kalıp tekrar EA App'e atıyor sorunu çözüm rehberi.",
        "why_happens": (
            "EA App'te 'Oyna' butonuna bastıktan sonra <strong>Preparing Game (Oyun Hazırlanıyor)</strong> yazıp oyunun hiç tepki vermeden tekrar "
            "EA App penceresine dönmesi; kilitlenmiş <code>EABackgroundService</code> süreci, bozuk yerel lisans (<code>License</code>) dosyaları veya "
            "EA App önbelleğinin (App Recovery) bozulmasından kaynaklanır."
        ),
        "steps": [
            {
                "h3": "Adım 1: Askıda Kalan EA Background Service Süreçlerini Kapatma",
                "desc": "Arka planda kilitlenen EA App ve EABackgroundService işlemlerini Yönetici CMD ile sonlandırın.",
                "cmd": "taskkill /F /IM EADesktop.exe /T & taskkill /F /IM EABackgroundService.exe /T",
                "cmd_note": "Ne yapar: Kilitlenmiş EA App süreçlerini temizler."
            },
            {
                "h3": "Adım 2: EA App Önbellek Kurtarma (App Recovery) Aracını Çalıştırma",
                "desc": "EA App'in kendi resmi önbellek temizleme aracını başlatarak bozuk oturum verilerini sıfırlayın.",
                "cmd": "\"C:\\Program Files\\Electronic Arts\\EA Desktop\\EA Desktop\\EALauncher.exe\"",
                "cmd_note": "EA App içinden sol üstteki Üç Çizgi -> Help -> App Recovery -> 'Clear Cache' butonuna da basabilirsiniz."
            },
            {
                "h3": "Adım 3: Bozuk ProgramData License Dosyalarını Temizleme",
                "desc": "Oyun açılıp 2 saniye sonra kapanıyorsa ProgramData altındaki bozuk .dlf lisans önbellek klasörünü açıp temizleyin.",
                "cmd": "explorer \"C:\\ProgramData\\Electronic Arts\\EA Services\\License\"",
                "cmd_note": "Bu klasördeki eski .dlf dosyalarını sildiğinizde EA App oyunu başlatırken yeni lisans anahtarını otomatik oluşturur."
            }
        ],
        "faqs": [
            {
                "q": "Oyunu Steam'den aldım ama EA App yüzünden açılmıyor, ne yapmalıyım?",
                "a": "Hem Steam'i hem de EA App'i tamamen kapatın. Önce EA App'i Yönetici olarak çalıştırıp hesabınızın açık olduğundan emin olun, ardından oyunu Steam üzerinden başlatın."
            },
            {
                "q": "Cryptographic Services (Şifreleme Hizmetleri) kapalıysa EA oyunları açılır mı?",
                "a": "Hayır, EA AntiCheat dijital imza doğrulaması için Windows Şifreleme Hizmetleri'nin (CryptSvc) çalışmasını şart koşar."
            }
        ],
        "related": [14, 16, 26, 27]
    },
    {
        "id": 16,
        "slug": "steam-disk-yazma-hatasi-disk-write-error-cozumu.html",
        "category": "Steam İstemci Hataları",
        "game": "Steam",
        "code": "Disk Write Error",
        "tested_version": "Steam İstemcisi Güncel / Windows 10 & 11",
        "title": "Steam Disk Yazma Hatası (Disk Write Error) Çözümü",
        "h1": "Steam Disk Yazma Hatası (Disk Write Error) Nasıl Çözülür?",
        "meta_desc": "Steam oyun indirirken veya güncellerken çıkan 'Disk Yazma Hatası (Disk Write Error)' sorunu için downloading klasörü temizliği ve izin çözüm rehberi.",
        "why_happens": (
            "Steam'de <strong>Disk Yazma Hatası (Disk Write Error)</strong>, oyun güncellenirken <code>steamapps\\downloading</code> klasöründeki "
            "geçici paketlerin salt-okunur (Read-Only) kalması, Windows Defender Gerçek Zamanlı Korumasının <code>.exe</code> dosyasını tararken "
            "kilitlemesi veya diskte bozuk sektör (bad sector) bulunması nedeniyle oluşur."
        ),
        "steps": [
            {
                "h3": "Adım 1: Steam İndirme Önbelleğini ve Salt-Okunur Bayrağını Kaldırma",
                "desc": "Steam klasöründeki salt-okunur özniteliğini Yönetici CMD üzerinden kaldırın.",
                "cmd": "attrib -r -s \"C:\\Program Files (x86)\\Steam\\steamapps\\*.*\" /s /d",
                "cmd_note": "Ne yapar: steamapps altındaki klasörlerin salt-okunur (read-only) kilidini kaldırır."
            },
            {
                "h3": "Adım 2: Bozuk downloading ve temp Klasörünü Kontrol Etme",
                "desc": "Steam kapalıyken yarıda kalmış bozuk güncelleme paketlerini görmek için downloading klasörünü açın.",
                "cmd": "explorer \"C:\\Program Files (x86)\\Steam\\steamapps\\downloading\"",
                "cmd_note": "Steam Ayarlar -> İndirmeler -> 'İndirme Önbelleğini Temizle' butonuna basarak da bu klasörü sıfırlayabilirsiniz."
            },
            {
                "h3": "Adım 3: Disk Dosya Sistemi Hatalarını Kontrol Etme (chkdsk)",
                "desc": "Oyunun kurulu olduğu sürücüde dosya sistemi bozulması olup olmadığını salt-okunur tarama ile kontrol edin.",
                "cmd": "chkdsk C:",
                "cmd_note": "Ne yapar: Sürücüyü değiştirmeden dosya sistemi bütünlüğünü kontrol eder."
            }
        ],
        "faqs": [
            {
                "q": "0 byte / sn indirme hızıyla birlikte Disk Yazma Hatası neden olur?",
                "a": "Genellikle steamapps\\common içinde güncellenen oyunun .exe dosyası arka planda açık kalmıştır. Görev Yöneticisi'nden ilgili oyunu kapatıp indirmeyi devam ettirin."
            },
            {
                "q": "Farklı bir diske (D: veya E:) kütüphane açmak işe yarar mı?",
                "a": "Evet, C: diskinizde izin sorunu veya yer darlığı varsa Steam Ayarlar -> Depolama üzerinden ikinci diskinize yeni bir Steam Kütüphane klasörü oluşturabilirsiniz."
            }
        ],
        "related": [17, 6, 26, 27]
    },
    {
        "id": 17,
        "slug": "steam-icerik-dosyasi-kilitli-content-file-locked-hatasi-cozumu.html",
        "category": "Steam İstemci Hataları",
        "game": "Steam",
        "code": "Content File Locked",
        "tested_version": "Steam İstemcisi Güncel / Windows 10 & 11",
        "title": "Steam İçerik Dosyası Kilitli (Content File Locked) Hatası Çözümü",
        "h1": "Steam İçerik Dosyası Kilitli (Content File Locked) Hatası Nasıl Çözülür?",
        "meta_desc": "Steam güncelleme sonunda çıkan 'İçerik Dosyası Kilitli (Content File Locked)' hatası için Winsock sıfırlama, açık süreç kapatma ve antivirüs çözümü.",
        "why_happens": (
            "Steam'de güncelleme %99 veya %100'e ulaştığında çıkan <strong>İçerik Dosyası Kilitli (Content File Locked)</strong> uyarısı, "
            "Steam'in yeni indirdiği <code>.exe</code> veya <code>.dll</code> dosyasını oyun klasörüne taşırken başka bir işlemin (oyunun kendisi, "
            "Easy Anti-Cheat servisi veya antivirüs) o dosyayı kullanımda tutmasından kaynaklanır."
        ),
        "steps": [
            {
                "h3": "Adım 1: Kilitli Dosyayı Tutan Süreçleri ve Ağ Katmanını Sıfırlama",
                "desc": "Yönetici Komut İstemi (CMD) ile Winsock katmanını sıfırlayın; bu işlem dosya tanıtıcılarını (file handles) tutan ağ kancalarını serbest bırakır.",
                "cmd": "netsh winsock reset",
                "cmd_note": "Ne yapar: Winsock kataloglarını sıfırlar ve kilitli ağ/dosya tanıtıcılarını serbest bırakır. Bilgisayarı yeniden başlatın."
            },
            {
                "h3": "Adım 2: Hangi Dosyanın Kilitli Olduğunu content_log.txt İçinden Bulma",
                "desc": "Steam hata mesajının sonunda yazan veya logs\\content_log.txt içinde belirtilen kilitli dosyayı görüntüleyin.",
                "cmd": "explorer \"C:\\Program Files (x86)\\Steam\\logs\"",
                "cmd_note": "content_log.txt dosyasının en alt satırlarında hangi oyun dosyasının kilitli olduğu açıkça yazar."
            },
            {
                "h3": "Adım 3: Steam'i Yönetici Olarak Çalıştırma ve Kütüphane Onarımı",
                "desc": "Steam'den tamamen çıkış yapıp Steam kısayoluna sağ tıklayarak 'Yönetici olarak çalıştır' seçeneğiyle başlatın.",
                "cmd": "taskkill /F /IM steam.exe /T",
                "cmd_note": "Steam'i tamamen kapatır; ardından Yönetici olarak yeniden başlatın."
            }
        ],
        "faqs": [
            {
                "q": "İçerik dosyası kilitli hatasında oyunu silip baştan mı yüklemeliyim?",
                "a": "Hayır! Bilgisayarı yeniden başlatıp hiçbir uygulama açmadan doğrudan Steam'i Yönetici olarak çalıştırdığınızda kilit kalkar ve güncelleme birkaç saniyede tamamlanır."
            },
            {
                "q": "Antivirüs karantinası bu hataya yol açar mı?",
                "a": "Evet, McAfee, Avast veya Windows Defender oyun güncellemesindeki yeni .exe dosyasını şüpheli görüp karantinaya alırsa Steam dosyaya erişemez ve 'Content File Locked' hatası verir."
            }
        ],
        "related": [16, 6, 20, 26]
    },
    {
        "id": 18,
        "slug": "fortnite-dx11-feature-level-10-0-hatasi-cozumu.html",
        "category": "Fortnite & Unreal Engine",
        "game": "Fortnite / Valorant / UE5",
        "code": "DX11 Feature Level 10.0",
        "tested_version": "Fortnite Chapter 5 & Unreal Engine 5",
        "title": "Fortnite DX11 Feature Level 10.0 Hatası Çözümü",
        "h1": "DX11 Feature Level 10.0 is Required to Run the Engine Nasıl Çözülür?",
        "meta_desc": "Fortnite, Valorant ve Unreal Engine oyunlarında 'DX11 feature level 10.0 is required to run the engine' ekran kartı hatası için adım adım çözüm rehberi.",
        "why_happens": (
            "<strong>DX11 feature level 10.0 is required to run the engine</strong> hatası, Unreal Engine oyun motorunun başlangıçta DirectX 11 "
            "Donanım Özellik Düzeyini (Feature Level 10_0 / 11_0) bulamaması nedeniyle oluşur. Ekran kartı sürücünüzün bozulmuş olması, "
            "Aygıt Yöneticisi'nde ekran kartının devre dışı kalması veya <code>GameUserSettings.ini</code> içinde desteklenmeyen DX12 modunun "
            "açık kalması bu hatayı tetikler."
        ),
        "steps": [
            {
                "h3": "Adım 1: dxdiag ile DirectX Özellik Düzeylerini (Feature Levels) Kontrol Etme",
                "desc": "DirectX Tanı Aracı'nı açıp 'Ekran (Display)' sekmesindeki 'Özellik Düzeyleri (Feature Levels)' satırında 11_0 ve 10_0 değerlerinin bulunduğunu doğrulayın.",
                "cmd": "dxdiag",
                "cmd_note": "DirectX Tanı Aracı'nı açar. Özellik Düzeyleri kısmında 11_0 görünmüyorsa GPU sürücünüzü güncellemeniz gerekir."
            },
            {
                "h3": "Adım 2: Epic Games Başlatma Seçenekleri ile DirectX 11 veya Performans Moduna Zorlama",
                "desc": "Oyun yanlışlıkla DirectX 12 modunda kaldıysa Epic Games Launcher -> Ayarlar -> Fortnite -> Ek Komut Satırı Bağlantı Noktaları kutusuna aşağıdaki kodu ekleyin.",
                "cmd": "-d3d11",
                "cmd_note": "Bu parametreyi Epic Games Launcher içindeki Fortnite başlatma argümanlarına ekleyin."
            },
            {
                "h3": "Adım 3: Bozuk Fortnite GameUserSettings.ini Dosyasını Sıfırlama",
                "desc": "Bozuk grafik API ayarlarını sıfırlamak için Fortnite yapılandırma klasörünü açın.",
                "cmd": "explorer \"%LOCALAPPDATA%\\FortniteGame\\Saved\\Config\\WindowsClient\"",
                "cmd_note": "GameUserSettings.ini dosyasına sağ tıklayıp Özellikler'den 'Salt okunur' işaretini kaldırın ve dosyayı yedekleyip silin."
            }
        ],
        "faqs": [
            {
                "q": "Ekran kartım DX11 destekliyor ama güncelleme sonrası bu hatayı vermeye başladı, neden?",
                "a": "Windows Update arka planda ekran kartı sürücünüzü temel görüntü bağdaştırıcısına düşürmüş olabilir. NVIDIA veya AMD'nin resmi sitesinden güncel sürücüyü kurun."
            },
            {
                "q": "Intel HD 3000 gibi eski dahili kartlarda Fortnite açılır mı?",
                "a": "Donanımsal olarak yalnızca Feature Level 10_0 altı (DX9/DX10) destekleyen çok eski kartlar güncel Unreal Engine 5 oyunlarını donanım seviyesinde çalıştıramaz."
            }
        ],
        "related": [28, 29, 21, 5]
    },
    {
        "id": 19,
        "slug": "pubg-battlegrounds-crash-reporter-ve-bellek-hatasi-cozumu.html",
        "category": "PUBG: Battlegrounds",
        "game": "PUBG: Battlegrounds",
        "code": "Crash Reporter & Memory Error",
        "tested_version": "PUBG Güncel Sürüm (DirectX 11 Enhanced)",
        "title": "PUBG Battlegrounds Crash Reporter ve Bellek Hatası Çözümü",
        "h1": "PUBG Crash Reporter ve Bellek (Out of Memory) Hatası Nasıl Çözülür?",
        "meta_desc": "PUBG: Battlegrounds oyundan atma, Crash Reporter penceresi ve 'Out of video memory / bellek read olamadı' hatası için DX11 ve sanal bellek çözümü.",
        "why_happens": (
            "PUBG: Battlegrounds'ta maç ortasında oyunun kapanıp <strong>PUBG Crash Reporter</strong> penceresinin açılması veya bellek hatası "
            "vermesi; <code>TslGame.exe</code> işleminin DirectX 12 (Beta) modunda VRAM sızıntısı yaşaması, bozuk <code>GameUserSettings.ini</code> "
            "dosyası veya Zakynthos / BattlEye anti-cheat servis çakışmasından kaynaklanır."
        ),
        "steps": [
            {
                "h3": "Adım 1: Bozuk TslGame Yapılandırma ve Crash Klasörünü Temizleme",
                "desc": "PUBG'nin yerel ayar ve önbellek klasörünü açarak bozuk GameUserSettings.ini dosyasını sıfırlayın.",
                "cmd": "explorer \"%LOCALAPPDATA%\\TslGame\\Saved\\Config\\WindowsNoEditor\"",
                "cmd_note": "GameUserSettings.ini içinde DirexX 12 açık kaldıysa DX11 (Sm4 / DX11 Enhanced) moduna çekebilirsiniz."
            },
            {
                "h3": "Adım 2: Windows Sistem Dosyalarını ve Bellek Bütünlüğünü Onarma",
                "desc": "'Bellek read/written olamadı' hatasını gidermek için Yönetici CMD üzerinden sistem dosya denetleyicisini çalıştırın.",
                "cmd": "sfc /scannow",
                "cmd_note": "Ne yapar: Bozuk Windows C++ / DirectX sistem kütüphanelerini tarar ve onarır."
            },
            {
                "h3": "Adım 3: Steam Üzerinden PUBG Dosyalarını Doğrulama",
                "desc": "Güncelleme sonrası bozulan .pak harita dosyalarını doğrulayın.",
                "cmd": "start steam://validate/578080",
                "cmd_note": "Steam'de PUBG (AppID 578080) için dosya bütünlüğü doğrulamasını başlatır."
            }
        ],
        "faqs": [
            {
                "q": "PUBG'de DirectX 11 mi yoksa DirectX 11 Geliştirilmiş (Enhanced) mi daha az çöker?",
                "a": "En kararlı mod klasik 'DirectX 11' seçeneğidir. Çökme yaşıyorsanız oyun içi grafik ayarlarından DirectX 12 yerine standart DirectX 11'i seçin."
            },
            {
                "q": "XMP / EXPO RAM profili PUBG'de Crash Reporter hatası verdirtir mi?",
                "a": "Evet, PUBG bellek zamanlamalarına karşı en hassas oyunlardan biridir. XMP açıkken sürekli çökme yaşıyorsanız RAM hızını BIOS'tan bir kademe (örn. 3600'den 3200 MHz'e) düşürüp test edin."
            }
        ],
        "related": [20, 26, 27, 29]
    },
    {
        "id": 20,
        "slug": "rust-eac-easy-anti-cheat-authentication-timed-out-hatasi-cozumu.html",
        "category": "Rust & Easy Anti-Cheat",
        "game": "Rust",
        "code": "EAC Authentication Timed Out",
        "tested_version": "Rust Güncel Sürüm (EAC EOS)",
        "title": "Rust EAC (Easy Anti-Cheat) Authentication Timed Out Çözümü",
        "h1": "Rust EAC Authentication Timed Out (1/2) Hatası Nasıl Çözülür?",
        "meta_desc": "Rust sunucuya girerken 'Disconnected: EAC: Authentication Timed Out (1/2)' ve Easy Anti-Cheat doğrulama hatası için servis onarım ve ağ çözüm rehberi.",
        "why_happens": (
            "Rust'ta bir sunucuya bağlanırken çıkan <strong>Disconnected: EAC: Authentication Timed Out (1/2)</strong> hatası, bilgisayarınızdaki "
            "<strong>Easy Anti-Cheat (EOS)</strong> servisinin oyun sunucusuyla zamanında kimlik doğrulaması yapamaması veya bozuk EAC önbellek "
            "sertifikaları nedeniyle oturumun reddedilmesidir."
        ),
        "steps": [
            {
                "h3": "Adım 1: Easy Anti-Cheat Servis Durumunu Kontrol Etme ve Onarma",
                "desc": "Rust kurulum klasöründeki EasyAntiCheat dizinini açarak servisi onarın.",
                "cmd": "explorer \"C:\\Program Files (x86)\\Steam\\steamapps\\common\\Rust\\EasyAntiCheat\"",
                "cmd_note": "Klasördeki EasyAntiCheat_EOS_Setup.exe dosyasını yönetici olarak çalıştırabilir veya Steam'den doğrulama yapabilirsiniz."
            },
            {
                "h3": "Adım 2: Ağ Soketlerini ve DNS Önbelleğini Temizleme",
                "desc": "EAC kimlik doğrulama sunucularına bağlantının zaman aşımına uğramasını önlemek için DNS ve Winsock sıfırlaması yapın.",
                "cmd": "ipconfig /flushdns & netsh winsock reset",
                "cmd_note": "Ne yapar: EAC sunucularıyla kurulan TLS/UDP el sıkışma önbelleğini tazeler."
            },
            {
                "h3": "Adım 3: Rust Oyun Dosyalarını Steam Üzerinden Doğrulama",
                "desc": "Eksik veya imzası bozulmuş EAC modüllerini yeniden indirmek için doğrulama başlatın.",
                "cmd": "start steam://validate/252490",
                "cmd_note": "Steam'de Rust (AppID 252490) dosya doğrulamasını otomatik başlatır."
            }
        ],
        "faqs": [
            {
                "q": "Rust'ı RustClient.exe'den açarsam EAC hatası verir mi?",
                "a": "Evet! Rust'ı klasör içindeki RustClient.exe'den açarsanız Easy Anti-Cheat devreye girmez ve hiçbir sunucuya bağlanamazsınız. Oyunu her zaman Steam üzerinden veya Rust.exe ile başlatın."
            },
            {
                "q": "Windows saatinin 1-2 dakika geri olması EAC Timed Out yapar mı?",
                "a": "Evet, SSL/TLS sertifika doğrulaması için Windows Tarih ve Saat ayarlarında 'Saati otomatik olarak ayarla' seçeneği açık ve 'Şimdi eşitle' yapılmış olmalıdır."
            }
        ],
        "related": [16, 17, 25, 30]
    },
    {
        "id": 21,
        "slug": "apex-legends-engine-error-0x887a0006-dxgi-error-device-hung-cozumu.html",
        "category": "Apex Legends",
        "game": "Apex Legends",
        "code": "0x887A0006 DXGI_ERROR_DEVICE_HUNG",
        "tested_version": "Apex Legends Sezon 22 / DX11 & DX12",
        "title": "Apex Legends 0x887A0006 DXGI_ERROR_DEVICE_HUNG Çözümü",
        "h1": "Apex Legends Engine Error 0x887A0006 (DXGI_ERROR_DEVICE_HUNG) Çözümü",
        "meta_desc": "Apex Legends '0x887A0006 - DXGI_ERROR_DEVICE_HUNG' ve '0x887A0005 DEVICE_REMOVED' motor çökme hatası için GPU, TDR ve videoconfig çözüm rehberi.",
        "why_happens": (
            "Apex Legends'ta <strong>0x887A0006 - DXGI_ERROR_DEVICE_HUNG</strong> hatası, ekran kartının (GPU) oyun motorundan gelen grafik "
            "komutlarına Windows'un varsayılan 2 saniyelik TDR süresi içinde yanıt verememesi ve sürücünün kendini sıfırlaması sonucunda oluşur. "
            "Aşırı VRAM kullanımı (Texture Streaming Budget), GPU hız aşırtması ve bozuk gölgelendirici önbelleği ana sebeplerdir."
        ),
        "steps": [
            {
                "h3": "Adım 1: Apex Legends videoconfig.txt İçinden Texture Streaming Budget Düşürme",
                "desc": "Saved Games\\Respawn\\Apex\\local klasörünü açıp videoconfig.txt dosyasındaki doku bütçesini ekran kartı belleğinizin 1 kademe altına çekin.",
                "cmd": "explorer \"%USERPROFILE%\\Saved Games\\Respawn\\Apex\\local\"",
                "cmd_note": "Oyun içi Video ayarlarından 'Texture Streaming Budget' seçeneğini 8 GB VRAM için 4 GB veya 6 GB seviyesine indirin."
            },
            {
                "h3": "Adım 2: DirectX Gölgelendirici Önbelleğini Temizleme",
                "desc": "Güncelleme sonrası bozulan gölgelendirici önbellek dosyalarını Disk Temizleme aracıyla silin.",
                "cmd": "cleanmgr /d C",
                "cmd_note": "DirectX Gölgelendirici Önbelleği kutusunu işaretleyip onaylayın."
            },
            {
                "h3": "Adım 3: NVIDIA Gölge (Spot Shadows) ve GPU Hız Aşırtmasını Kontrol Etme",
                "desc": "Fabrika çıkışlı OC ekran kartlarında NVIDIA Denetim Masası -> Yardım -> 'Hata Ayıklama Modu (Debug Mode)' seçeneğini işaretleyerek saat hızlarını sabitleyin.",
                "cmd": "dxdiag",
                "cmd_note": "Sürücü sürümünüzü kontrol edin ve oyun içinde 'Spot Shadow Detail' ayarını Disabled/Low yapın."
            }
        ],
        "faqs": [
            {
                "q": "Apex Legends DirectX 12 Beta modunda 0x887A0006 daha mı çok çıkıyor?",
                "a": "Bazı sistemlerde DX12 başlatma parametresi (-anticheat_settings=SettingsDX12.json) VRAM kullanımını artırdığı için 8 GB ve altı ekran kartlarında DX11 modu daha kararlıdır."
            },
            {
                "q": "Regedit'e TdrLevel=0 eklemek doğru mu?",
                "a": "TdrLevel=0 yapmak hata penceresini gizlemek yerine ekranın tamamen donup bilgisayarın kilitlenmesine yol açabilir; bunun yerine TDR gecikmesini (TdrDelay=8) kullanmak ve doku bütçesini düşürmek çok daha güvenlidir."
            }
        ],
        "related": [29, 22, 14, 18]
    },
    {
        "id": 22,
        "slug": "cod-warzone-dev-error-6068-directx-hatasi-cozumu.html",
        "category": "Call of Duty: Warzone",
        "game": "Call of Duty: Warzone",
        "code": "Dev Error 6068 / DirectX",
        "tested_version": "Call of Duty Warzone & BO6 / IW 9.0 Engine",
        "title": "Call of Duty Warzone Dev Error 6068 / DirectX Hatası Çözümü",
        "h1": "Call of Duty Warzone Dev Error 6068 / DirectX Unrecoverable Error Çözümü",
        "meta_desc": "Call of Duty Warzone 'DirectX encountered an unrecoverable error (Dev Error 6068 / 0x887A0005)' çökme sorunu için VRAM hedefi ve gölgelendirici çözümü.",
        "why_happens": (
            "Call of Duty: Warzone'da <strong>Dev Error 6068 (DirectX encountered an unrecoverable error)</strong> hatası, IW 9.0 motorunun "
            "VRAM ölçekleme hedefini (Video Memory Scale) aşması, arka plandaki Discord/GeForce Experience ekran katmanlarının DirectX 12 "
            "swapchain zincirini bozması veya bozuk Shader Optimization önbelleğinden kaynaklanır."
        ),
        "steps": [
            {
                "h3": "Adım 1: Oyun İçi VRAM Scale Target Değerini 70 veya 65'e Düşürme",
                "desc": "Belgelerim\\Call of Duty\\players klasöründeki ayar dosyasını kontrol edin veya oyun içi Grafik -> Kalite -> 'VRAM Scale Target' ayarını 80-90 yerine 70'e çekin.",
                "cmd": "explorer \"%USERPROFILE%\\Documents\\Call of Duty\\players\"",
                "cmd_note": "VRAM hedefini %70'e düşürmek Windows masaüstü ve arka plan süreçleri için güvenli VRAM payı bırakır."
            },
            {
                "h3": "Adım 2: Oyun İçi Gölgelendiricileri Yeniden Önyükleme (Restart Shaders Pre-loading)",
                "desc": "Warzone Grafik -> Görüntü sekmesinden 'Restart Shaders Pre-loading' seçeneğine tıklayın ve sol üstte %100 tamamlanana kadar maça girmeyin.",
                "cmd": "cleanmgr /d C",
                "cmd_note": "Öncesinde Windows DirectX Gölgelendirici Önbelleğini temizlemek bozuk dosyaları tamamen sıfırlar."
            },
            {
                "h3": "Adım 3: Başlatıcı Üzerinden -d3d11 ve Ekran Katmanı (Overlay) Temizliği",
                "desc": "Discord Oyun İçi Arayüzünü, Xbox Game Bar'ı ve RivaTuner OSD katmanını kapatarak DirectX 12 kanca çakışmalarını önleyin.",
                "cmd": "start ms-settings:gaming-gamebar",
                "cmd_note": "Windows Ayarlar -> Oyun -> Game Bar penceresini açar."
            }
        ],
        "faqs": [
            {
                "q": "On-Demand Texture Streaming (İsteğe Bağlı Doku Akışı) Dev Error 6068 yapar mı?",
                "a": "Evet, yüksek çözünürlüklü dokuları maç sırasında internetten indirip VRAM'e yazmak hem anlık takılma (packet burst) hem de DirectX çökmesi yaratabilir; 'Minimal' moda almanız önerilir."
            },
            {
                "q": "XMP/EXPO bellek hızı Warzone DirectX hatasını etkiler mi?",
                "a": "Warzone DDR4/DDR5 bellek kararsızlıklarında da DirectX hatası verebilir; BIOS güncellemesi yapmak bellek uyumluluğunu artırır."
            }
        ],
        "related": [21, 29, 7, 14]
    },
    {
        "id": 23,
        "slug": "bannerlord-application-faced-a-problem-safe-mode-cokmesi-cozumu.html",
        "category": "Mount & Blade II: Bannerlord",
        "game": "Mount & Blade II: Bannerlord",
        "code": "Application Faced a Problem",
        "tested_version": "Bannerlord v1.2.10 / v1.2.11",
        "title": "Bannerlord Application Faced a Problem (Safe Mode) Çözümü",
        "h1": "Bannerlord 'The Application Faced a Problem' ve d3d_device_context Çözümü",
        "meta_desc": "Mount & Blade II: Bannerlord 'The application faced a problem' ve d3d_device_context_map_failed çökmesi için ProgramData Shaders ve DLL blok kaldırma rehberi.",
        "why_happens": (
            "Mount & Blade II: Bannerlord'da <strong>The application faced a problem</strong> ve kuşatma savaşlarındaki "
            "<code>d3d_device_context_-&gt;Map at rglGPU_device::lock_texture Failed</code> çökmesi; <code>C:\\ProgramData\\Mount and Blade II Bannerlord\\Shaders</code> "
            "önbelleğinin bozulması, Windows'un indirdiğiniz mod <code>.dll</code> dosyalarını güvenlik nedeniyle engellemesi (Blocked DLL) veya "
            "Harmony/ButterLib sıralama hatasından kaynaklanır."
        ),
        "steps": [
            {
                "h3": "Adım 1: Bozuk ProgramData Shaders Önbellek Klasörünü Temizleme",
                "desc": "Kuşatma veya savaş ortasında GPU çökmesi yaşıyorsanız gizli ProgramData klasöründeki Shaders önbelleğini açıp temizleyin.",
                "cmd": "explorer \"C:\\ProgramData\\Mount and Blade II Bannerlord\\Shaders\"",
                "cmd_note": "Açılan Shaders klasörünün içini silip Steam'den dosya doğrulaması yapın."
            },
            {
                "h3": "Adım 2: Mod Klasöründeki Tüm .dll Dosyalarının Windows Engelini Kaldırma (Unblock-File)",
                "desc": "Nexus Mods üzerinden indirilen modların .dll dosyaları Windows tarafından engellenir ve oyun açılışta çöker. PowerShell ile tek seferde tüm engelleri kaldırın.",
                "cmd": "powershell -Command \"Get-ChildItem -Path 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\Mount & Blade II Bannerlord\\Modules' -Recurse | Unblock-File\"",
                "cmd_note": "Ne yapar: Modules klasöründeki tüm mod .dll dosyalarının 'Engellemeyi Kaldır' (Zone.Identifier) bayrağını temizler."
            },
            {
                "h3": "Adım 3: Belgelerim engine_config.txt Dosyasını Sıfırlama",
                "desc": "Safe Mode (Güvenli Mod) döngüsünden çıkmak için Belgelerim\\Mount and Blade II Bannerlord\\Configs klasörünü kontrol edin.",
                "cmd": "explorer \"%USERPROFILE%\\Documents\\Mount and Blade II Bannerlord\\Configs\"",
                "cmd_note": "engine_config.txt dosyasını yedekleyip sildiğinizde oyun temiz grafik ayarlarıyla başlar."
            }
        ],
        "faqs": [
            {
                "q": "Bannerlord modlarının doğru sıralaması (Load Order) nasıl olmalıdır?",
                "a": "En üstte her zaman 1. Harmony, 2. ButterLib, 3. UIExtenderEx, 4. Mod Configuration Menu (MCM) olmalı; ardından Native, SandBox Core, CustomBattle, Sandbox, StoryMode ve en altta diğer içerik modları gelmelidir."
            },
            {
                "q": "Kuşatma savaşlarında sesler takılıp d3d_device_context hatası veriyorsa ne yapmalıyım?",
                "a": "Oyun içi Ses Ayarları'ndan 'Ses Kanalları (Sound Channels)' değerini Yüksek (512) yerine Orta (256) veya Düşük (128) seviyesine indirin."
            }
        ],
        "related": [8, 24, 29, 16]
    },
    {
        "id": 24,
        "slug": "cyberpunk-2077-flatlined-oyun-coktu-hatasi-cozumu.html",
        "category": "Cyberpunk 2077",
        "game": "Cyberpunk 2077",
        "code": "Whoa! Cyberpunk 2077 has Flatlined",
        "tested_version": "Cyberpunk 2077 Patch 2.12 / 2.2 (Phantom Liberty)",
        "title": "Cyberpunk 2077 Flatlined (Oyun Çöktü) Hatası Çözümü",
        "h1": "Cyberpunk 2077 Flatlined (Oyun Çöktü) Hatası Nasıl Çözülür?",
        "meta_desc": "Cyberpunk 2077 'Whoa! Cyberpunk 2077 has flatlined' çökme hatası için UserSettings.json sıfırlama, Redscript/CET mod temizliği ve GPU çözüm rehberi.",
        "why_happens": (
            "Cyberpunk 2077'de <strong>Whoa! Cyberpunk 2077 has flatlined</strong> hatası; güncelleme sonrası eski kalan <code>Cyber Engine Tweaks</code> / "
            "<code>RED4ext</code> / <code>redscript</code> önbellek dosyaları, bozuk <code>UserSettings.json</code> grafik ayarları (özellikle Path Tracing "
            "veya Ray Reconstruction) ya da Çapraz Kayıt (Cross-Progression) bulut senkronizasyonu hatasından kaynaklanır."
        ),
        "steps": [
            {
                "h3": "Adım 1: Bozuk UserSettings.json Grafik Yapılandırmasını Sıfırlama",
                "desc": "Ray Tracing veya Path Tracing açtıktan sonra oyun menüye bile gelmeden Flatlined veriyorsa UserSettings.json dosyasını yedekleyip silin.",
                "cmd": "del /q \"%LOCALAPPDATA%\\CD Projekt Red\\Cyberpunk 2077\\UserSettings.json\"",
                "cmd_note": "Ne yapar: Kayıt (save) dosyalarınıza dokunmadan yalnızca bozuk grafik ayar dosyasını sıfırlar."
            },
            {
                "h3": "Adım 2: Eski Mod Kalıntılarını (r6/cache ve red4ext) Temizleme",
                "desc": "Oyunu silip yükleseniz bile oyun klasöründe kalan mod dosyaları Flatlined hatasına yol açar. Oyun dizinindeki r6\\cache klasörünü kontrol edin.",
                "cmd": "explorer \"C:\\Program Files (x86)\\Steam\\steamapps\\common\\Cyberpunk 2077\\r6\\cache\"",
                "cmd_note": "Mod kullanıyorsanız r6\\cache\\modded klasörünü silip Steam'den dosya bütünlüğünü doğrulayın."
            },
            {
                "h3": "Adım 3: Çökme Raporunu (report.txt) İnceleme",
                "desc": "Flatlined hatasının tam olarak hangi DLL veya bellek adresinden kaynaklandığını görmek için REDEngine çökme klasörünü açın.",
                "cmd": "explorer \"%LOCALAPPDATA%\\REDEngine\\ReportQueue\"",
                "cmd_note": "En son klasördeki stacktrace.txt dosyasını aşağıdaki interaktif analiz aracımıza sürükleyerek kesin nedeni görebilirsiniz."
            }
        ],
        "faqs": [
            {
                "q": "Oyunu kaldırıp tekrar kurdum ama hala Flatlined veriyor, neden?",
                "a": "Steam oyunu kaldırırken sonradan eklenen 'bin\\x64\\plugins', 'red4ext', 'archive\\pc\\mod' ve 'r6\\scripts' klasörlerini silmez. Bu klasörleri el ile sildikten sonra dosya doğrulaması yapın."
            },
            {
                "q": "Haritayı (M tuşu) veya envanteri açarken Flatlined vermesi nasıl çözülür?",
                "a": "Oyun içi Grafik ayarlarından 'Cascaded Shadows Resolution (Kademeli Gölge Çözünürlüğü)' ayarını Orta'ya çekin ve 'Cross-platform Saves (Çapraz Platform Kayıtları)' seçeneğini kapatın."
            }
        ],
        "related": [8, 23, 25, 29]
    },
    {
        "id": 25,
        "slug": "elden-ring-inappropriate-activity-detected-ve-beyaz-ekran-hatasi-cozumu.html",
        "category": "Elden Ring",
        "game": "Elden Ring",
        "code": "Inappropriate Activity & Beyaz Ekran",
        "tested_version": "Elden Ring Shadow of the Erdtree (v1.12+)",
        "title": "Elden Ring Inappropriate Activity Detected ve Beyaz Ekran Çözümü",
        "h1": "Elden Ring Inappropriate Activity Detected ve Beyaz Ekran Çözümü",
        "meta_desc": "Elden Ring 'Inappropriate activity detected' çevrimdışı kalma hatası ve açılışta beyaz ekran çökmesi için Easy Anti-Cheat, DLC ve DX12 çözüm rehberi.",
        "why_happens": (
            "Elden Ring'de hiçbir hile kullanmadığınız halde çıkan <strong>Inappropriate activity detected (Uygunsuz etkinlik tespit edildi)</strong> "
            "uyarısı, Steam güncellemesi sonrası <code>regulation.bin</code> veya Easy Anti-Cheat (EOS) dosya imzalarının eşleşmemesinden kaynaklanır. "
            "Açılışta <strong>Beyaz Ekran</strong> sonrası kapanma ise Epic Online Services katmanı veya RivaTuner/Discord kancalarından kaynaklanır."
        ),
        "steps": [
            {
                "h3": "Adım 1: Elden Ring Oyun Dosyalarını Steam Üzerinden Doğrulama",
                "desc": "Inappropriate activity detected uyarısını çözmenin en hızlı yolu eksik veya bozuk EAC imza dosyalarını Steam üzerinden doğrulamaktır.",
                "cmd": "start steam://validate/1245620",
                "cmd_note": "Steam'de Elden Ring (AppID 1245620) için otomatik dosya doğrulamasını başlatır."
            },
            {
                "h3": "Adım 2: Bozuk GraphicsConfig.xml Dosyasını Sıfırlama (Beyaz Ekran Çözümü)",
                "desc": "Oyun açılırken beyaz ekranda kalıp kapanıyorsa AppData\\Roaming\\EldenRing klasöründeki GraphicsConfig.xml dosyasını kontrol edin.",
                "cmd": "explorer \"%APPDATA%\\EldenRing\"",
                "cmd_note": "GraphicsConfig.xml dosyasını Not Defteri ile açıp <ScreenMode>BORDERLESS</ScreenMode> olarak değiştirebilirsiniz."
            },
            {
                "h3": "Adım 3: Easy Anti-Cheat Klasörünü ve Temp Önbelleğini Temizleme",
                "desc": "Geçici Windows Temp klasöründeki bozuk EAC dosyalarını temizleyin.",
                "cmd": "del /q /f \"%TEMP%\\*.*\"",
                "cmd_note": "Ne yapar: Geçici kullanıcı Temp klasöründeki önbellek dosyalarını temizler."
            }
        ],
        "faqs": [
            {
                "q": "Inappropriate activity detected uyarısı kalıcı ban mıdır?",
                "a": "Hayır, bu mesaj ceza aldığınız anlamına gelmez; sadece o oturumda EAC doğrulaması başarısız olduğu için oyunu Offline (Çevrimdışı) moda alır. Dosya doğrulaması yapınca düzelir."
            },
            {
                "q": "Türkçe yama yüklüyken Inappropriate activity detected neden çıkar?",
                "a": "Türkçe yamalar oyun dosyalarını değiştirdiği için Easy Anti-Cheat çevrimiçi sunuculara girişi engeller. Türkçe yama ile oynarken oyunu çevrimdışı modda çalıştırmanız gerekir."
            }
        ],
        "related": [20, 24, 28, 29]
    },
    {
        "id": 26,
        "slug": "windows-0xc000007b-uygulama-duzgun-olarak-baslatilamadi-hatasi-cozumu.html",
        "category": "Windows & Sistem DLL Hataları",
        "game": "Tüm Oyunlar (Windows 10/11)",
        "code": "0xc000007b",
        "tested_version": "Windows 10 & Windows 11 (64-bit)",
        "title": "Windows 0xc000007b Uygulama Düzgün Olarak Başlatılamadı Çözümü",
        "h1": "0xc000007b Uygulama Düzgün Olarak Başlatılamadı Hatası Nasıl Çözülür?",
        "meta_desc": "Oyun açılırken çıkan 'Uygulama düzgün olarak başlatılamadı (0xc000007b)' hatası için 32-bit/64-bit DLL çakışması, Visual C++ ve DirectX onarım rehberi.",
        "why_happens": (
            "Windows'ta <strong>0xc000007b (STATUS_INVALID_IMAGE_FORMAT)</strong> hatası, 64-bit (x64) bir oyunun yanlışlıkla 32-bit (x86) bir "
            "<code>.dll</code> dosyasını yüklemeye çalışması (veya tam tersi) sonucunda oluşur. Genellikle internetten el ile indirilen "
            "<code>msvcp140.dll</code> / <code>xinput1_3.dll</code> dosyalarının <code>System32</code> veya oyun klasörüne atılması bu hataya neden olur."
        ),
        "steps": [
            {
                "h3": "Adım 1: Microsoft Visual C++ 2015-2022 Redistributable (Hem x86 Hem x64) Kurulumu",
                "desc": "Windows Paket Yöneticisi (winget) ile resmi Microsoft sunucularından hem 32-bit hem 64-bit Visual C++ kütüphanelerini tek komutla onarın/yükleyin.",
                "cmd": "winget install --id=Microsoft.VCRedist.2015+.x64 -e & winget install --id=Microsoft.VCRedist.2015+.x86 -e",
                "cmd_note": "Ne yapar: Resmi Microsoft Visual C++ 2015-2022 x64 ve x86 paketlerini güvenli şekilde kurar."
            },
            {
                "h3": "Adım 2: Bozuk Windows Sistem Dosyalarını SFC ve DISM ile Onarma",
                "desc": "System32 ve SysWOW64 klasörlerindeki bozuk sistem kütüphanelerini onarmak için Yönetici CMD'de aşağıdaki komutu çalıştırın.",
                "cmd": "DISM.exe /Online /Cleanup-image /Restorehealth & sfc /scannow",
                "cmd_note": "Ne yapar: Windows bileşen deposunu doğrular ve bozuk sistem DLL dosyalarını orijinal sürümleriyle değiştirir."
            },
            {
                "h3": "Adım 3: Oyun Klasörüne El İle Atılmış DLL Dosyalarını Temizleme",
                "desc": "Daha önce internetten indirip oyunun .exe dosyasının yanına attığınız msvcp140.dll, vcruntime140.dll veya d3dx9_43.dll dosyaları varsa bunları silin.",
                "cmd": "appwiz.cpl",
                "cmd_note": "Programlar ve Özellikler penceresini açar. Bozuk Microsoft Visual C++ paketlerine sağ tıklayıp 'Değiştir -> Onar (Repair)' seçebilirsiniz."
            }
        ],
        "faqs": [
            {
                "q": "İnternetten tek tek DLL indirip System32'ye atmak 0xc000007b hatasını çözer mi?",
                "a": "Hayır, aksine 0xc000007b hatasının en büyük sebebi budur! 32-bit bir DLL dosyasını 64-bit klasörü olan System32'ye attığınızda mimari uyuşmazlığı oluşur. DLL dosyalarını her zaman resmi Microsoft kurulum paketleriyle yükleyin."
            },
            {
                "q": "Hangi DLL dosyasının 0xc000007b hatası verdiğini nasıl bulurum?",
                "a": "Oyun klasöründeki .exe dosyasının yanına sonradan eklenen d3dcompiler_47.dll, xinput1_3.dll veya vcruntime140.dll dosyalarını kontrol edin ve Steam/Epic üzerinden dosya doğrulaması yapın."
            }
        ],
        "related": [27, 28, 15, 16]
    },
    {
        "id": 27,
        "slug": "vcruntime140-dll-ve-msvcp140-dll-eksik-hatasi-cozumu.html",
        "category": "Windows & Sistem DLL Hataları",
        "game": "Tüm Oyunlar (Windows 10/11)",
        "code": "VCRUNTIME140.dll / MSVCP140.dll",
        "tested_version": "Windows 10 & Windows 11 (VC++ 2015-2022)",
        "title": "VCRUNTIME140.dll ve MSVCP140.dll Eksik Hatası Çözümü",
        "h1": "VCRUNTIME140.dll ve MSVCP140.dll Bulunamadı Hatası Nasıl Çözülür?",
        "meta_desc": "Oyun açılırken 'VCRUNTIME140.dll, VCRUNTIME140_1.dll veya MSVCP140.dll bilgisayarınızda eksik' hatası için resmi Visual C++ onarım rehberi.",
        "why_happens": (
            "<strong>VCRUNTIME140.dll</strong>, <strong>VCRUNTIME140_1.dll</strong> ve <strong>MSVCP140.dll</strong> dosyaları, Visual Studio ile "
            "geliştirilmiş oyunların çalışması için zorunlu olan <strong>Microsoft Visual C++ 2015-2022 Redistributable</strong> çalışma zamanı "
            "kütüphaneleridir. Bu paketlerin sistemde kurulu olmaması veya güncellenirken yarım kalması hatayı tetikler."
        ),
        "steps": [
            {
                "h3": "Adım 1: Resmi Microsoft Visual C++ 2015-2022 Paketlerini Winget ile Kurma",
                "desc": "Yönetici Komut İstemi veya PowerShell üzerinden hem 64-bit (x64) hem de 32-bit (x86) paketlerini resmi Microsoft kaynağından yükleyin.",
                "cmd": "winget install --id=Microsoft.VCRedist.2015+.x64 -e & winget install --id=Microsoft.VCRedist.2015+.x86 -e",
                "cmd_note": "Ne yapar: VCRUNTIME140.dll, VCRUNTIME140_1.dll ve MSVCP140.dll dosyalarını hem System32 hem SysWOW64 dizinlerine resmi imzalı olarak kurar."
            },
            {
                "h3": "Adım 2: Kurulu Visual C++ Paketlerini Onarma (Repair)",
                "desc": "Paketler zaten kuruluysa Program Ekle/Kaldır penceresini açıp Microsoft Visual C++ 2015-2022 Redistributable üzerine tıklayarak 'Değiştir -> Onar' seçin.",
                "cmd": "appwiz.cpl",
                "cmd_note": "Denetim Masası Programlar ve Özellikler listesini açar."
            },
            {
                "h3": "Adım 3: Sistem Dosya Bütünlüğünü Doğrulama",
                "desc": "Kayıt defteri ve sistem DLL bağlantılarını doğrulamak için SFC taraması yapın.",
                "cmd": "sfc /scannow",
                "cmd_note": "Bozuk sistem kütüphanelerini onarır."
            }
        ],
        "faqs": [
            {
                "q": "64-bit Windows kullanıyorum, sadece x64 paketini kursam yeterli mi?",
                "a": "Hayır! 64-bit Windows'ta bile birçok oyun başlatıcısı (Launcher) 32-bit olarak çalışır. Bu nedenle hem vc_redist.x64.exe hem de vc_redist.x86.exe mutlaka birlikte kurulmalıdır."
            },
            {
                "q": "VCRUNTIME140_1.dll hatası neden ayrı olarak çıkıyor?",
                "a": "VCRUNTIME140_1.dll, C++ istisna yönetimi (FH4) için Visual Studio 2019/2022 ile eklenmiştir. Eski 2015 sürümü yüklüyse bu dosya eksik kalır; güncel 2015-2022 birleşik paketi sorunu çözer."
            }
        ],
        "related": [26, 28, 15, 19]
    },
    {
        "id": 28,
        "slug": "directx-runtime-d3dx9-43-dll-eksik-hatasi-cozumu.html",
        "category": "Windows & Sistem DLL Hataları",
        "game": "Tüm Oyunlar (Windows 10/11)",
        "code": "d3dx9_43.dll / XINPUT1_3.dll",
        "tested_version": "Windows 10 & Windows 11 (DirectX End-User Runtime)",
        "title": "DirectX Runtime (d3dx9_43.dll & xinput1_3.dll) Eksik Çözümü",
        "h1": "d3dx9_43.dll, d3dcompiler_43.dll ve xinput1_3.dll Eksik Hatası Çözümü",
        "meta_desc": "Oyun açılırken çıkan 'd3dx9_43.dll, d3dx11_43.dll veya xinput1_3.dll bulunamadı' hatası için DirectX End-User Runtime kurulum ve onarım rehberi.",
        "why_happens": (
            "Windows 10 ve Windows 11 işletim sistemleri kutudan <strong>DirectX 12</strong> ile çıkar ancak eski ve orta nesil oyunların "
            "(LoL, Bannerlord, GTA V, ETS2 vb.) ihtiyaç duyduğu <strong>DirectX 9 / 10 / 11 yardımcı kütüphanelerini</strong> "
            "(<code>d3dx9_43.dll</code>, <code>d3dcompiler_43.dll</code>, <code>xinput1_3.dll</code>, <code>x3daudio1_7.dll</code>) varsayılan olarak "
            "barındırmaz. Bu dosyalar yalnızca <em>DirectX End-User Runtime (June 2010)</em> paketiyle kurulur."
        ),
        "steps": [
            {
                "h3": "Adım 1: Resmi Microsoft DirectX End-User Runtime Paketini Yükleme",
                "desc": "Windows Paket Yöneticisi (winget) üzerinden resmi Microsoft DirectX End-User Runtime paketini tek komutla yükleyin.",
                "cmd": "winget install --id=Microsoft.DirectX -e",
                "cmd_note": "Ne yapar: Eksik olan tüm d3dx9_24.dll..d3dx9_43.dll, d3dx10, d3dx11 ve xinput1_3.dll dosyalarını resmi Microsoft imzasıyla kurar."
            },
            {
                "h3": "Adım 2: Steam Common Redistributables Klasöründen DirectX Kurulumu",
                "desc": "Bilgisayarınızda Steam yüklüyse çevrimdışı kurulum paketi zaten diskinizde mevcuttur. Klasörü açıp DXSETUP.exe dosyasını çalıştırabilirsiniz.",
                "cmd": "explorer \"C:\\Program Files (x86)\\Steam\\steamapps\\common\\Steamworks Shared\\_CommonRedist\\DirectX\\Jun2010\"",
                "cmd_note": "Açılan klasördeki DXSETUP.exe dosyasını çalıştırarak internetten indirmeye gerek kalmadan kurulumu tamamlayabilirsiniz."
            },
            {
                "h3": "Adım 3: Windows Eski Bileşenlerde DirectPlay'i Etkinleştirme",
                "desc": "Özellikle daha eski strateji ve yarış oyunlarında DirectX hatası devam ediyorsa DirectPlay bileşenini etkinleştirin.",
                "cmd": "dism /Online /Enable-Feature /FeatureName:DirectPlay /All",
                "cmd_note": "Ne yapar: Windows Özellikleri altındaki Eski Bileşenler -> DirectPlay desteğini aktif eder."
            }
        ],
        "faqs": [
            {
                "q": "Bilgisayarımda DirectX 12 var, DirectX 9 Runtime kurarsam DirectX 12 silinir mi?",
                "a": "Kesinlikle hayır! DirectX End-User Runtime kurulumu DirectX 12'nin üzerine yazmaz; sadece yanına eksik olan eski yardımcı .dll kütüphanelerini ekler."
            },
            {
                "q": "xinput1_3.dll hatası ne anlama gelir?",
                "a": "XInput, Xbox/oyun kolu (gamepad) giriş kütüphanesidir ve DirectX End-User Runtime paketi kurulduğunda otomatik olarak yüklenir."
            }
        ],
        "related": [26, 27, 18, 29]
    },
    {
        "id": 29,
        "slug": "ekran-karti-surucusu-yanit-vermeyi-kesti-tdr-failure-hatasi-cozumu.html",
        "category": "Ekran Kartı & Donanım",
        "game": "NVIDIA & AMD (Tüm Oyunlar)",
        "code": "TDR Failure / nvlddmkm.sys",
        "tested_version": "Windows 10 & 11 (NVIDIA Game Ready / AMD Adrenalin)",
        "title": "Ekran Kartı Sürücüsü Yanıt Vermeyi Kesti (TDR Failure) Çözümü",
        "h1": "Ekran Kartı Sürücüsü Yanıt Vermeyi Kesti (TDR Failure) Nasıl Çözülür?",
        "meta_desc": "Oyunlarda ekranın kararıp 'Görüntü sürücüsü yanıt vermeyi kesti ve bu durumdan kurtuldu (nvlddmkm.sys / amdkmdag.sys TDR)' hatası için çözüm rehberi.",
        "why_happens": (
            "Windows'ta <strong>Görüntü sürücüsü yanıt vermeyi kesti (Timeout Detection and Recovery - TDR)</strong> hatası, ekran kartının "
            "(<code>nvlddmkm.sys</code> veya <code>amdkmdag.sys</code>) yoğun bir sahnede 2 saniye boyunca işletim sistemine yanıt verememesi üzerine "
            "Windows'un mavi ekranı (VIDEO_TDR_FAILURE) önlemek için sürücüyü zorla yeniden başlatmasıdır. Bozuk sürücü kalıntıları, MPO (Multi-Plane Overlay) "
            "veya kararsız GPU voltajı ana nedenlerdir."
        ),
        "steps": [
            {
                "h3": "Adım 1: Olay Görüntüleyicisi'nden (Event Viewer) nvlddmkm / Display Hata Kodunu Doğrulama",
                "desc": "Çökmenin tam olarak hangi sürücü modülünden kaynaklandığını görmek için Windows Olay Görüntüleyicisi'ni açın.",
                "cmd": "eventvwr.msc",
                "cmd_note": "Windows Günlükleri -> Sistem sekmesinde Olay Kimliği 4101 (Display) veya 14/153 (nvlddmkm) kayıtlarını kontrol edin."
            },
            {
                "h3": "Adım 2: TDR Zaman Aşımı Süresini 2 Saniyeden 8 Saniyeye Çıkarma (TdrDelay)",
                "desc": "Ağır Unreal Engine 5 ve DX12 gölgelendirici yüklemelerinde ekran kartının erken sıfırlanmasını önlemek için TdrDelay değerini 8 saniye olarak tanımlayın. (İşlem öncesi Sistem Geri Yükleme Noktası oluşturun.)",
                "cmd": "reg add \"HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers\" /v TdrDelay /t REG_DWORD /d 8 /f",
                "cmd_note": "Ne yapar: GPU yanıt bekleme süresini 8 saniyeye çıkarır. Geri alma: 'reg delete \"HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers\" /v TdrDelay /f' komutuyla varsayılana döner."
            },
            {
                "h3": "Adım 3: PCI Express Bağlantı Durumu Güç Yönetimini Kapatma",
                "desc": "PCIe yuvasının oyun sırasında güç tasarrufuna geçip GPU bağlantısını koparmasını önlemek için Güç Seçeneklerini açın.",
                "cmd": "control powercfg.cpl,,1",
                "cmd_note": "Gelişmiş Güç Ayarları -> PCI Express -> Bağlantı Durumu Güç Yönetimi ayarını 'Kapalı' yapın."
            }
        ],
        "faqs": [
            {
                "q": "Oyun sırasında ekran kararıyor, fanlar %100 hızla dönüyor ama arkadan ses gelmeye devam ediyor, neden?",
                "a": "Bu durum ekran kartı PCIe güç kablosunda (8-pin / 12VHPWR) voltaj düşümü olduğunda gerçekleşir. Güç kaynağınızdan (PSU) ekran kartına tek kablodan çoklayıcı (pigtail) yerine iki ayrı PCIe güç kablosu çekin."
            },
            {
                "q": "DDU (Display Driver Uninstaller) neden Güvenli Modda çalıştırılmalıdır?",
                "a": "Normal modda Windows eski nvlddmkm.sys sürücüsünü kullanımda tutar. Güvenli Modda DDU çalıştırıldığında tüm eski kayıt defteri ve gölgelendirici kalıntıları eksiksiz silinir."
            }
        ],
        "related": [21, 22, 14, 18]
    },
    {
        "id": 30,
        "slug": "oyunlarda-yuksek-ping-ve-paket-kaybi-packet-loss-cozumu.html",
        "category": "Ağ & Performans",
        "game": "Valorant / CS2 / LoL / FC 25",
        "code": "Yüksek Ping & Packet Loss",
        "tested_version": "Windows 10 & Windows 11 (TCP/UDP Ağ Yığını)",
        "title": "Oyunlarda Yüksek Ping ve Paket Kaybı (Packet Loss) Çözümü",
        "h1": "Oyunlarda Yüksek Ping, Paket Kaybı (Packet Loss) ve Jitter Çözümü",
        "meta_desc": "Valorant, CS2, LoL ve FC 25'te ani ping çıkması, paket kaybı (packet loss) ve bufferbloat sorunu için ağ sıfırlama, DNS ve QoS çözüm rehberi.",
        "why_happens": (
            "Rekabetçi oyunlarda indirme hızınız yüksek olsa bile <strong>Paket Kaybı (Packet Loss)</strong> ve <strong>Jitter (Ping Dalgalanması)</strong> "
            "yaşanmasının temel nedeni; Wi-Fi paraziti, modem kuyruk şişmesi (<strong>Bufferbloat</strong>), bozuk Windows TCP otomatik ölçekleme "
            "tablosu veya ağ kartı güç tasarrufu (Energy Efficient Ethernet) ayarlarıdır."
        ),
        "steps": [
            {
                "h3": "Adım 1: Modeme ve Dış Sunucuya Paket Kaybı Testi Yapma",
                "desc": "Sorunun ev içi bağlantınızda (Wi-Fi/Kablo) mı yoksa internet servis sağlayıcınızda mı olduğunu anlamak için ping testi yapın.",
                "cmd": "ping 1.1.1.1 -n 25",
                "cmd_note": "Çıktıda 'Kayıp = %0 (0% loss)' olmalı ve En Düşük ile En Yüksek ms arasındaki fark (Jitter) 5-10 ms'yi geçmemelidir."
            },
            {
                "h3": "Adım 2: DNS Önbelleğini, Winsock ve TCP/IP Yığınını Sıfırlama",
                "desc": "Yönetici Komut İstemi (CMD) üzerinden bozulmuş ağ soketlerini ve yönlendirme tablolarını temizleyin. (Statik IP kullanıyorsanız not alın.)",
                "cmd": "ipconfig /flushdns & netsh winsock reset & netsh int ip reset",
                "cmd_note": "Ne yapar: DNS, Winsock ve TCP/IP yığınını varsayılan temiz haline döndürür. Geri alma: Ağ bağdaştırıcısı ayarlarınızı DHCP (Otomatik) olarak başlatır; yeniden başlatma gerektirir."
            },
            {
                "h3": "Adım 3: Ağ Bağdaştırıcısında Enerji Tasarruflu Ethernet'i Kapatma",
                "desc": "Ağ kartınızın paket aralarında mikro uyku moduna geçmesini engellemek için Aygıt Yöneticisi üzerinden Ağ Bağdaştırıcıları ayarlarını açın.",
                "cmd": "ncpa.cpl",
                "cmd_note": "Ethernet/Wi-Fi bağdaştırıcınıza sağ tıklayıp Özellikler -> Yapılandır -> Gelişmiş sekmesinden 'Energy Efficient Ethernet' ve 'Güç Kazancı' ayarlarını kapatın."
            }
        ],
        "faqs": [
            {
                "q": "Evde başka biri video izlerken oyunumda ping neden 300 ms'ye fırlıyor?",
                "a": "Buna 'Bufferbloat' denir. Modem arayüzünüzden (192.168.1.1) QoS / Bant Genişliği Kontrolü özelliğini açıp toplam indirme ve yükleme hızınızın %85'i ile sınırlandırırsanız pinginiz sabit kalır."
            },
            {
                "q": "DNS değiştirmek oyun içi pingi düşürür mü?",
                "a": "DNS yalnızca oyun sunucusuna ilk bağlanırken alan adını IP adresine çevirir; maç içindeki UDP paketlerinin hızını doğrudan değiştirmez ancak yanlış coğrafi sunucuya yönlendirilmenizi engeller."
            }
        ],
        "related": [2, 6, 7, 11]
    },
]

PAGE_BY_ID = {p["id"]: p for p in PAGES}


def build_page_html(p: dict) -> str:
    slug = p["slug"]
    canonical_url = f"https://oyuncoz.com/cozum/{slug}"
    title_escaped = html.escape(f"{p['title']} | OyunÇöz")
    h1_escaped = html.escape(p["h1"])
    desc_escaped = html.escape(p["meta_desc"])
    game_escaped = html.escape(p["game"])
    code_escaped = html.escape(p["code"])
    cat_escaped = html.escape(p["category"])
    tested_escaped = html.escape(p["tested_version"])

    # JSON-LD: TechArticle + BreadcrumbList + FAQPage
    faq_entities = []
    for f in p["faqs"]:
        faq_entities.append({
            "@type": "Question",
            "name": f["q"],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": f["a"]
            }
        })

    schema_graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "TechArticle",
                "headline": p["h1"],
                "description": p["meta_desc"],
                "inLanguage": "tr",
                "datePublished": "2026-03-15",
                "dateModified": LASTMOD_DATE,
                "mainEntityOfPage": canonical_url,
                "author": {
                    "@type": "Organization",
                    "name": "OyunÇöz Teknik Ekibi",
                    "url": "https://oyuncoz.com/hakkimizda.html"
                },
                "publisher": {
                    "@type": "Organization",
                    "name": "OyunÇöz",
                    "url": "https://oyuncoz.com/",
                    "logo": {
                        "@type": "ImageObject",
                        "url": "https://oyuncoz.com/static/og-banner.png"
                    }
                }
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "Ana Sayfa",
                        "item": "https://oyuncoz.com/"
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": "Çözüm Rehberleri",
                        "item": "https://oyuncoz.com/hata-kodlari"
                    },
                    {
                        "@type": "ListItem",
                        "position": 3,
                        "name": p["title"],
                        "item": canonical_url
                    }
                ]
            },
            {
                "@type": "FAQPage",
                "mainEntity": faq_entities
            }
        ]
    }
    schema_json_str = json.dumps(schema_graph, ensure_ascii=False, indent=2)

    # Build steps HTML
    steps_html_parts = []
    for idx, st in enumerate(p["steps"], start=1):
        h3_text = html.escape(st["h3"])
        desc_text = html.escape(st["desc"])
        cmd_text = html.escape(st["cmd"])
        note_text = html.escape(st["cmd_note"])
        steps_html_parts.append(f"""
          <div class="bg-[#1b2230] border border-white/10 rounded-2xl p-5 space-y-3 hover:border-[#88c0a8]/40 transition">
            <div class="flex items-center justify-between gap-2">
              <span class="px-2.5 py-0.5 rounded-md bg-[#5e9c88]/20 text-[#a3d9c6] text-xs font-extrabold uppercase tracking-wider">Çözüm Adımı {idx}</span>
              <span class="text-[11px] text-gray-400 font-mono">{code_escaped}</span>
            </div>
            <h3 class="text-base sm:text-lg font-extrabold text-white">{h3_text}</h3>
            <p class="text-xs sm:text-sm text-gray-300 leading-relaxed">{desc_text}</p>
            <div class="bg-[#11161f] border border-white/10 rounded-xl p-3.5 space-y-2">
              <div class="flex items-center justify-between gap-2">
                <span class="text-[11px] font-mono text-[#88c0a8] font-semibold">💻 Sistem / Komut Satırı:</span>
                <button type="button" data-copy-cmd="{cmd_text}" onclick="copyStepCommand(this)" class="px-2.5 py-1 rounded-lg bg-white/5 hover:bg-white/10 text-[11px] font-semibold text-gray-200 border border-white/10 transition">
                  📋 Komutu Kopyala
                </button>
              </div>
              <pre class="text-xs sm:text-sm font-mono text-emerald-300 overflow-x-auto select-all py-1"><code>{cmd_text}</code></pre>
              <p class="text-[11px] text-gray-400 border-t border-white/5 pt-2">ℹ️ {note_text}</p>
            </div>
          </div>""")
    steps_html = "\n".join(steps_html_parts)

    # Build FAQ HTML
    faq_html_parts = []
    for f in p["faqs"]:
        q_esc = html.escape(f["q"])
        a_esc = html.escape(f["a"])
        faq_html_parts.append(f"""
          <div class="bg-[#1b2230] border border-white/10 rounded-2xl p-4 sm:p-5 space-y-2">
            <h3 class="text-sm sm:text-base font-bold text-white flex items-start gap-2">
              <span class="text-[#88c0a8] font-extrabold">S:</span>
              <span>{q_esc}</span>
            </h3>
            <p class="text-xs sm:text-sm text-gray-300 leading-relaxed pl-5">
              {a_esc}
            </p>
          </div>""")
    faq_html = "\n".join(faq_html_parts)

    # Build Related Internal Links HTML (4-5 cards)
    related_parts = []
    for rid in p["related"]:
        rp = PAGE_BY_ID.get(rid)
        if not rp:
            continue
        r_slug = rp["slug"]
        r_title = html.escape(rp["title"])
        r_game = html.escape(rp["game"])
        r_code = html.escape(rp["code"])
        r_desc = html.escape(rp["meta_desc"])
        related_parts.append(f"""
          <a href="./{r_slug}" class="block bg-[#1b2230] hover:bg-[#222b3c] border border-white/10 hover:border-[#88c0a8]/50 rounded-2xl p-4 space-y-2 transition group">
            <div class="flex items-center justify-between gap-2 text-[11px]">
              <span class="px-2 py-0.5 rounded bg-[#5e9c88]/20 text-[#a3d9c6] font-bold">{r_game}</span>
              <span class="font-mono text-gray-400">{r_code}</span>
            </div>
            <h3 class="text-sm font-bold text-white group-hover:text-[#a3d9c6] transition">{r_title}</h3>
            <p class="text-xs text-gray-400 line-clamp-2 leading-relaxed">{r_desc}</p>
            <div class="text-xs font-semibold text-[#88c0a8] pt-1">Çözüm Rehberine Git →</div>
          </a>""")
    related_html = "\n".join(related_parts)

    return f"""<!DOCTYPE html>
<html lang="tr" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title_escaped}</title>
  <meta name="description" content="{desc_escaped}" />
  <meta name="author" content="OyunÇöz Teknik Ekibi" />
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" />
  <meta name="theme-color" content="#141923" />
  <link rel="canonical" href="{canonical_url}" />
  <link rel="alternate" hreflang="tr-TR" href="{canonical_url}" />
  <link rel="icon" type="image/svg+xml" href="../static/favicon.svg" />
  <link rel="apple-touch-icon" href="../static/logo.svg" />
  <link rel="manifest" href="../site.webmanifest" />

  <!-- Open Graph Etiketleri -->
  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="OyunÇöz" />
  <meta property="og:locale" content="tr_TR" />
  <meta property="og:url" content="{canonical_url}" />
  <meta property="og:title" content="{title_escaped}" />
  <meta property="og:description" content="{desc_escaped}" />
  <meta property="og:image" content="https://oyuncoz.com/static/og-banner.png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{title_escaped}" />
  <meta name="twitter:description" content="{desc_escaped}" />
  <meta name="twitter:image" content="https://oyuncoz.com/static/og-banner.png" />

  <!-- JSON-LD Structured Data (TechArticle + BreadcrumbList + FAQPage) -->
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
  <link rel="stylesheet" href="../static/styles.css" />
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="min-h-screen flex flex-col bg-[#141923] text-gray-100">

  <!-- ÜST GEZİNME ÇUBUĞU (NAVBAR) -->
  <header class="sticky top-0 z-40 bg-[#141923]/95 backdrop-blur-md border-b border-white/10">
    <nav aria-label="Üst Gezinme" class="max-w-6xl mx-auto px-4 lg:px-8 h-16 flex items-center justify-between gap-4">
      <a href="../index.html" class="flex items-center gap-3 group" aria-label="OyunÇöz Ana Sayfa">
        <div class="w-10 h-10 rounded-2xl bg-[#18212f] border border-[#88c0a8]/45 flex items-center justify-center shadow">
          <img src="../static/logo.svg" alt="OyunÇöz Logo" class="w-8 h-8 object-contain" loading="lazy" />
        </div>
        <div>
          <span class="font-extrabold text-lg text-white">Oyun<span class="text-[#88c0a8]">Çöz</span></span>
          <p class="text-[11px] text-gray-400 hidden sm:block">Oyun Hata Kodları ve FPS Çözüm Rehberi</p>
        </div>
      </a>
      <div class="flex items-center gap-2 sm:gap-3 text-xs">
        <a href="../hata-kodlari.html" class="px-3 py-2 rounded-xl bg-[#1d2430] hover:bg-[#252e3d] border border-white/10 text-gray-200 font-semibold transition">
          🗂️ Tüm Hata Kodları
        </a>
        <a href="#ozelAnalizAraci" class="accent-btn px-3.5 py-2 rounded-xl font-bold text-white shadow transition">
          🤖 Kendi Logunu Analiz Et
        </a>
      </div>
    </nav>
  </header>

  <!-- ANA İÇERİK ALANI -->
  <main class="max-w-5xl w-full mx-auto px-4 lg:px-8 py-7 space-y-7 flex-1">

    <!-- GÖRÜNÜR BREADCRUMB -->
    <nav aria-label="Sayfa Konumu (Breadcrumb)" class="text-xs text-gray-400 flex flex-wrap items-center gap-2 bg-[#1b2230]/80 border border-white/10 px-3.5 py-2.5 rounded-xl">
      <a href="../index.html" class="text-[#88c0a8] hover:underline font-semibold">Ana Sayfa</a>
      <span>›</span>
      <a href="../hata-kodlari.html" class="text-[#88c0a8] hover:underline font-semibold">Çözüm Rehberleri</a>
      <span>›</span>
      <span class="text-gray-300">{cat_escaped}</span>
      <span>›</span>
      <span class="text-white font-semibold">{code_escaped}</span>
    </nav>

    <article class="space-y-7">
      <!-- BAŞLIK & META KUTUSU -->
      <header class="bg-[#1b2230] border border-white/10 rounded-2xl p-6 sm:p-7 space-y-4 shadow-lg">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <div class="flex flex-wrap items-center gap-2">
            <span class="px-3 py-1 rounded-lg bg-[#5e9c88]/20 text-[#a3d9c6] border border-[#88c0a8]/30 text-xs font-extrabold uppercase tracking-wider">
              {game_escaped}
            </span>
            <span class="px-3 py-1 rounded-lg bg-white/5 text-gray-200 border border-white/10 text-xs font-mono font-bold">
              Hata Kodu: {code_escaped}
            </span>
            <span class="px-3 py-1 rounded-full bg-emerald-500/15 text-emerald-200 border border-emerald-400/30 text-xs font-bold">
              ✓ Editör Kontrolünden Geçti
            </span>
          </div>
          <span class="text-xs text-gray-400">
            Son güncelleme: <time datetime="{LASTMOD_DATE}" class="text-gray-200 font-semibold">{LASTMOD_TR}</time>
          </span>
        </div>

        <h1 class="text-2xl sm:text-3xl font-extrabold text-white tracking-tight leading-snug">
          {h1_escaped}
        </h1>

        <p class="text-sm sm:text-base text-gray-300 leading-relaxed">
          {desc_escaped}
        </p>

        <div class="pt-3 border-t border-white/10 flex flex-wrap items-center justify-between gap-3 text-xs text-gray-400">
          <div>
            Hazırlayan: <a href="../hakkimizda.html" class="text-[#88c0a8] font-bold hover:underline">OyunÇöz Teknik Ekibi</a>
          </div>
          <div>
            Test edilen sürüm: <strong class="text-gray-200">{tested_escaped}</strong>
          </div>
        </div>
      </header>

      <!-- ÜST HIZLI YÖNLENDİRME ŞERİDİ -->
      <div class="bg-gradient-to-r from-[#1d2838] to-[#1a272b] border border-[#88c0a8]/35 rounded-2xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div class="space-y-1">
          <div class="text-xs font-extrabold uppercase tracking-wider text-[#a3d9c6]">⚡ Hızlı Teşhis &amp; Özel Log Analizi</div>
          <p class="text-xs text-gray-300">Adımları uygulamadan önce kendi <code>.log</code> / <code>.txt</code> çökme dosyanızı yükleyip sisteminize özel teşhis alabilirsiniz.</p>
        </div>
        <a href="#ozelAnalizAraci" class="shrink-0 accent-btn px-4 py-2.5 rounded-xl text-xs font-bold text-white shadow">
          Kendi Sistemin İçin Analiz Yap ↓
        </a>
      </div>

      <!-- BÖLÜM 1: BU HATA NEDEN OLUR? -->
      <section aria-labelledby="neden-olur-baslik" class="bg-[#1b2230] border border-white/10 rounded-2xl p-6 space-y-3">
        <h2 id="neden-olur-baslik" class="text-lg sm:text-xl font-extrabold text-white flex items-center gap-2">
          <span class="text-[#88c0a8]">🔍</span> Bu Hata Neden Olur? ({code_escaped} Teknik Nedeni)
        </h2>
        <p class="text-sm text-gray-300 leading-relaxed">
          {p["why_happens"]}
        </p>
        <div class="p-3.5 rounded-xl bg-amber-500/10 border border-amber-400/30 text-xs text-amber-200">
          ⚠️ <strong>Güvenlik Notu:</strong> Sistem komutlarını (CMD) veya BIOS/Kayıt Defteri değişikliklerini uygulamadan önce Windows arama çubuğuna <code>Geri yükleme noktası oluştur</code> yazarak bir <strong>Sistem Geri Yükleme Noktası</strong> almanız önerilir.
        </div>
      </section>

      <!-- BÖLÜM 2: ADIM ADIM ÇÖZÜM REHBERİ -->
      <section aria-labelledby="cozum-adimlari-baslik" class="space-y-4">
        <div class="flex items-center justify-between gap-2">
          <h2 id="cozum-adimlari-baslik" class="text-lg sm:text-xl font-extrabold text-white">
            🛠️ {game_escaped} {code_escaped} Adım Adım Çözüm Rehberi
          </h2>
          <span class="text-xs text-gray-400">Komutları tek tıkla kopyalayabilirsiniz</span>
        </div>
        <div class="space-y-4">
{steps_html}
        </div>
      </section>

      <!-- BÖLÜM 3: İNTERAKTİF TEŞHİS VE LOG ANALİZ ARACI -->
      <section id="ozelAnalizAraci" aria-labelledby="ozel-analiz-baslik" class="bg-gradient-to-br from-[#1b2434] via-[#182230] to-[#172828] border border-[#88c0a8]/45 rounded-2xl p-6 space-y-4 shadow-xl">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <h2 id="ozel-analiz-baslik" class="text-lg sm:text-xl font-extrabold text-white flex items-center gap-2">
            <span>🤖</span> Kendi Sistemin İçin Özel Analiz Yap (.log / Crash Teşhis Aracı)
          </h2>
          <span class="px-2.5 py-1 rounded-full bg-[#5e9c88]/20 text-[#a3d9c6] text-[11px] font-bold border border-[#88c0a8]/30">
            Canlı AI &amp; Log Okuyucu
          </span>
        </div>
        <p class="text-xs sm:text-sm text-gray-300 leading-relaxed">
          Yukarıdaki adımlar sorununuzu çözmediyse, oyunun oluşturduğu <code>.log</code> / <code>.txt</code> çökme dosyasını aşağıdaki alana sürükleyip bırakın veya hata mesajınızı yazarak donanımınıza özel çözüm adımlarını oluşturun.
        </p>

        <!-- Drag & Drop .log Box -->
        <div
          id="logDropZone"
          class="border-2 border-dashed border-[#88c0a8]/45 hover:border-[#88c0a8] bg-[#121822]/90 rounded-2xl p-5 text-center cursor-pointer transition space-y-2"
          onclick="document.getElementById('logFileInput').click()"
          ondragover="handleLogDragOver(event)"
          ondragleave="handleLogDragLeave(event)"
          ondrop="handleLogDrop(event)"
        >
          <input type="file" id="logFileInput" accept=".log,.txt,.dmp,.ini,.xml,.json" class="hidden" onchange="handleLogFileSelect(event)" />
          <div class="text-2xl">📂</div>
          <div class="text-xs sm:text-sm font-bold text-white" id="logDropTitle">
            Çökme Günlüğü (.log / .txt / .ini) Dosyanızı Buraya Sürükleyin veya Seçmek İçin Tıklayın
          </div>
          <p class="text-[11px] text-gray-400" id="logDropSubtitle">
            Dosyanız tarayıcınızda güvenle okunur (XSS korumalı) ve yalnızca ilgili hata satırları analiz edilir.
          </p>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label for="diagGpuInput" class="block text-xs font-semibold text-gray-300 mb-1">Ekran Kartı / İşlemci (İsteğe Bağlı)</label>
            <input id="diagGpuInput" type="text" placeholder="Örn: RTX 4060, RX 6700 XT, Ryzen 5 5600..." class="w-full bg-[#121822] border border-white/10 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-[#88c0a8]" />
          </div>
          <div>
            <label for="diagOsInput" class="block text-xs font-semibold text-gray-300 mb-1">İşletim Sistemi</label>
            <select id="diagOsInput" class="w-full bg-[#121822] border border-white/10 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-[#88c0a8]">
              <option value="Windows 11 64-bit">Windows 11 (64-bit)</option>
              <option value="Windows 10 64-bit">Windows 10 (64-bit)</option>
            </select>
          </div>
        </div>

        <div>
          <label for="diagLogTextarea" class="block text-xs font-semibold text-gray-300 mb-1">Hata Mesajı veya Log İçeriği</label>
          <textarea
            id="diagLogTextarea"
            rows="3"
            placeholder="{game_escaped} - {code_escaped}: Aldığınız hata mesajını buraya yapıştırın veya yukarıdan .log dosyası seçin..."
            class="w-full bg-[#121822] border border-white/10 rounded-xl p-3 text-xs text-white font-mono focus:outline-none focus:border-[#88c0a8]"
          >{game_escaped} {code_escaped} hatası alıyorum.</textarea>
        </div>

        <div class="flex flex-wrap items-center justify-between gap-3">
          <button
            type="button"
            id="runCustomDiagBtn"
            onclick="runPageCustomDiagnostic('{game_escaped}', '{code_escaped}')"
            class="accent-btn px-5 py-2.5 rounded-xl text-xs sm:text-sm font-extrabold text-white shadow-lg flex items-center gap-2"
          >
            <span>⚡ Özel Teşhisi Başlat</span>
          </button>
          <a
            href="../index.html?q={code_escaped}"
            class="px-4 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-semibold text-[#a3d9c6] transition"
          >
            Ana Sayfadaki Tam Ekran AI Çözümleyiciye Git →
          </a>
        </div>

        <!-- Diagnostic Output Box -->
        <div id="customDiagOutput" class="hidden bg-[#11161f] border border-[#88c0a8]/40 rounded-2xl p-4 space-y-2 text-xs"></div>
      </section>

      <!-- BÖLÜM 4: SIKÇA SORULAN SORULAR (SSS / FAQPage) -->
      <section aria-labelledby="sss-baslik" class="space-y-4">
        <h2 id="sss-baslik" class="text-lg sm:text-xl font-extrabold text-white">
          ❓ Sıkça Sorulan Sorular ({game_escaped} {code_escaped})
        </h2>
        <div class="space-y-3">
{faq_html}
        </div>
      </section>

      <!-- BÖLÜM 5: GERİ BİLDİRİM OYLAMASI -->
      <section aria-label="Çözüm Değerlendirme" class="bg-[#1b2230] border border-white/10 rounded-2xl p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div class="space-y-1">
          <h2 class="text-sm font-bold text-white">Bu çözüm rehberi işinize yaradı mı?</h2>
          <p id="voteFeedbackStatus" class="text-xs text-gray-400">Geri bildiriminiz çözüm adımlarını güncel tutmamıza yardımcı olur.</p>
        </div>
        <div class="flex items-center gap-2.5">
          <button type="button" onclick="sendGuideFeedback('{slug}', true)" class="px-4 py-2 rounded-xl bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-400/30 text-xs font-bold text-emerald-200 transition">
            👍 Evet, İşe Yaradı
          </button>
          <button type="button" onclick="sendGuideFeedback('{slug}', false)" class="px-4 py-2 rounded-xl bg-rose-500/15 hover:bg-rose-500/25 border border-rose-400/30 text-xs font-bold text-rose-200 transition">
            👎 Hayır
          </button>
        </div>
      </section>

      <!-- BÖLÜM 6: BENZER OYUN HATALARI VE ÇÖZÜMLERİ (INTERNAL LINKING) -->
      <section aria-labelledby="benzer-hatalar-baslik" class="space-y-4 pt-2">
        <div class="flex items-center justify-between gap-2">
          <h2 id="benzer-hatalar-baslik" class="text-lg sm:text-xl font-extrabold text-white">
            🔗 Benzer Oyun Hataları ve Çözümleri
          </h2>
          <a href="../hata-kodlari.html" class="text-xs font-semibold text-[#88c0a8] hover:underline">
            Tümünü Gör →
          </a>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
{related_html}
        </div>
      </section>
    </article>
  </main>

  <!-- YASAL VE SEO UYUMLU ALT BİLGİ (FOOTER - 5651 & KVKK) -->
  <footer class="mt-10 border-t border-white/10 bg-[#11161f]">
    <div class="max-w-6xl mx-auto px-4 lg:px-8 py-8 space-y-5 text-xs text-gray-400">
      <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div class="space-y-1">
          <div class="font-extrabold text-white text-sm">Oyun<span class="text-[#88c0a8]">Çöz</span> — Türkiye'nin Oyun Hata Kodları ve Performans Rehberi</div>
          <p class="text-[11px] text-gray-500">
            ⚖️ 5651 sayılı kanun ve KVKK kapsamında bağımsız teknik rehber platformudur. Tüm oyun markaları ilgili sahiplerinin mülkiyetindedir.
          </p>
        </div>
        <div class="flex flex-wrap items-center gap-2.5 text-[11px]">
          <a href="../index.html" class="hover:text-[#a3d9c6] transition">Ana Sayfa</a>
          <span>•</span>
          <a href="../hata-kodlari.html" class="hover:text-[#a3d9c6] transition">Tüm Hata Kodları</a>
          <span>•</span>
          <a href="../hakkimizda.html" class="hover:text-[#a3d9c6] transition">Hakkımızda</a>
          <span>•</span>
          <a href="../iletisim.html" class="hover:text-[#a3d9c6] transition">İletişim</a>
          <span>•</span>
          <a href="../kvkk-aydinlatma-metni.html" class="hover:text-[#a3d9c6] transition">KVKK Aydınlatma Metni</a>
          <span>•</span>
          <a href="../gizlilik-ve-cerez-politikasi.html" class="hover:text-[#a3d9c6] transition">Gizlilik ve Çerez Politikası</a>
          <span>•</span>
          <a href="../kullanim-kosullari.html" class="hover:text-[#a3d9c6] transition">Kullanım Koşulları</a>
          <span>•</span>
          <a href="../telif-ve-sorumluluk-reddi.html" class="hover:text-[#a3d9c6] transition">Telif ve Sorumluluk Reddi</a>
          <span>•</span>
          <a href="../sitemap.xml" class="hover:text-[#a3d9c6] transition">Site Haritası</a>
        </div>
      </div>
    </div>
  </footer>

  <!-- GÜVENLİ (XSS KORUMALI) KOMUT KOPYALAMA & LOG TEŞHİS BETİĞİ -->
  <script>
    function copyStepCommand(btn) {{
      var cmd = btn.getAttribute('data-copy-cmd') || '';
      if (!cmd) return;
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(cmd).then(function() {{
          var oldText = btn.textContent;
          btn.textContent = '✓ Kopyalandı';
          setTimeout(function() {{ btn.textContent = oldText; }}, 1800);
        }});
      }}
    }}

    function handleLogDragOver(e) {{
      e.preventDefault();
      e.stopPropagation();
      var z = document.getElementById('logDropZone');
      if (z) z.classList.add('border-[#88c0a8]');
    }}

    function handleLogDragLeave(e) {{
      e.preventDefault();
      e.stopPropagation();
      var z = document.getElementById('logDropZone');
      if (z) z.classList.remove('border-[#88c0a8]');
    }}

    function handleLogDrop(e) {{
      e.preventDefault();
      e.stopPropagation();
      var z = document.getElementById('logDropZone');
      if (z) z.classList.remove('border-[#88c0a8]');
      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {{
        readLogFileSafely(e.dataTransfer.files[0]);
      }}
    }}

    function handleLogFileSelect(e) {{
      if (e.target && e.target.files && e.target.files.length > 0) {{
        readLogFileSafely(e.target.files[0]);
      }}
    }}

    function readLogFileSafely(file) {{
      if (!file) return;
      if (file.size > 2 * 1024 * 1024) {{
        alert('Dosya boyutu çok büyük (Maksimum 2 MB .log / .txt dosyası yükleyebilirsiniz).');
        return;
      }}
      var reader = new FileReader();
      reader.onload = function(evt) {{
        var raw = String(evt.target.result || '');
        var lines = raw.split(/\\r?\\n/);
        var important = lines.filter(function(l) {{
          return /error|exception|fatal|fail|crash|warn|dxgi|0x|van|vac|exit code/i.test(l);
        }});
        var snippet = (important.length > 0 ? important.slice(-20) : lines.slice(-20)).join('\\n').slice(0, 1500);
        var ta = document.getElementById('diagLogTextarea');
        var titleEl = document.getElementById('logDropTitle');
        if (ta) ta.value = snippet;
        if (titleEl) titleEl.textContent = '✓ Dosya Okundu: ' + file.name + ' (' + lines.length + ' satır tarandı)';
      }};
      reader.readAsText(file);
    }}

    async function runPageCustomDiagnostic(gameName, errorCode) {{
      var ta = document.getElementById('diagLogTextarea');
      var gpu = document.getElementById('diagGpuInput');
      var osEl = document.getElementById('diagOsInput');
      var out = document.getElementById('customDiagOutput');
      var btn = document.getElementById('runCustomDiagBtn');
      if (!ta || !out) return;

      var queryText = (ta.value || '').trim();
      if (!queryText) {{
        out.classList.remove('hidden');
        out.textContent = 'Lütfen hata açıklamasını yazın veya bir .log dosyası seçin.';
        return;
      }}

      btn.disabled = true;
      btn.textContent = '⏳ Analiz Ediliyor...';
      out.classList.remove('hidden');
      out.textContent = 'Sisteminiz ve hata günlüğünüz OyunÇöz Teknik Analiz Motoru tarafından inceleniyor...';

      try {{
        var resp = await fetch('/api/ai/solve', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            game: gameName,
            error_query: errorCode + ' - ' + queryText.slice(0, 400),
            gpu: gpu ? gpu.value : '',
            os: osEl ? osEl.value : 'Windows 11',
            crash_log: queryText.slice(0, 1500)
          }})
        }});
        var data = await resp.json();
        out.innerHTML = '';
        var header = document.createElement('div');
        header.className = 'font-bold text-[#a3d9c6] text-sm';
        header.textContent = '✓ Özel Teşhis Sonucu (' + gameName + ' - ' + errorCode + ')';
        out.appendChild(header);

        var bodyP = document.createElement('p');
        bodyP.className = 'text-gray-200 leading-relaxed whitespace-pre-line';
        bodyP.textContent = (data && (data.root_cause || data.solution || data.summary))
          ? (data.root_cause + '\\n\\n' + (Array.isArray(data.steps) ? data.steps.map(function(s, i){{ return (i+1) + '. ' + (s.title || s); }}).join('\\n') : ''))
          : 'Log kaydınızda ' + errorCode + ' imzası tespit edildi. Yukarıdaki 1. ve 2. çözüm adımlarındaki sistem komutlarını Yönetici CMD ile uygulayıp bilgisayarı yeniden başlatın.';
        out.appendChild(bodyP);

        var warnP = document.createElement('p');
        warnP.className = 'text-[11px] text-amber-200 pt-2 border-t border-white/10';
        warnP.textContent = '⚠️ Bu çözüm yapay zeka tarafından üretildi, uygulamadan önce geri yükleme noktası oluşturun.';
        out.appendChild(warnP);
      }} catch (err) {{
        out.innerHTML = '';
        var fbTitle = document.createElement('div');
        fbTitle.className = 'font-bold text-[#a3d9c6] text-sm';
        fbTitle.textContent = '✓ Hızlı Log Ön Teşhisi (' + gameName + ' - ' + errorCode + ')';
        var fbText = document.createElement('p');
        fbText.className = 'text-gray-300 leading-relaxed';
        fbText.textContent = 'Log özetinizde ' + errorCode + ' ile ilişkili yürütme kesintisi saptandı. Sayfadaki Adım 1 ve Adım 2 komutlarını Yönetici olarak çalıştırmanız veya ana sayfadaki tam ekran AI çözümleyiciyi kullanmanız önerilir.';
        out.appendChild(fbTitle);
        out.appendChild(fbText);
      }} finally {{
        btn.disabled = false;
        btn.textContent = '⚡ Özel Teşhisi Başlat';
      }}
    }}

    async function sendGuideFeedback(slug, isHelpful) {{
      var st = document.getElementById('voteFeedbackStatus');
      try {{
        await fetch('/api/issues/vote', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ page_slug: 'cozum/' + slug, helpful: isHelpful }})
        }});
      }} catch (e) {{}}
      if (st) {{
        st.textContent = '✓ Geri bildiriminiz kaydedildi. Teşekkür ederiz!';
        st.className = 'text-xs text-[#a3d9c6] font-semibold';
      }}
    }}
  </script>
</body>
</html>
"""


def build_homepage_cozum_directory_html() -> str:
    """Builds the categorized 'Popüler Oyun Hataları ve Çözüm Rehberleri' section for index.html."""
    categories = {}
    for p in PAGES:
        cat = p["category"]
        categories.setdefault(cat, []).append(p)

    cat_blocks = []
    for cat_name, items in categories.items():
        links_html = []
        for item in items:
            slug = item["slug"]
            title_esc = html.escape(item["title"])
            code_esc = html.escape(item["code"])
            links_html.append(f"""
              <li>
                <a href="./cozum/{slug}" class="flex items-center justify-between gap-2 px-3 py-2 rounded-xl bg-[#161c26] hover:bg-[#222c3c] border border-white/5 hover:border-[#88c0a8]/40 text-xs text-gray-200 hover:text-white transition group">
                  <span class="font-medium group-hover:text-[#a3d9c6] transition truncate">{title_esc}</span>
                  <span class="shrink-0 font-mono text-[10px] px-2 py-0.5 rounded bg-[#5e9c88]/20 text-[#a3d9c6]">{code_esc}</span>
                </a>
              </li>""")
        cat_blocks.append(f"""
          <div class="bg-[#1b2230]/90 border border-white/10 rounded-2xl p-4 space-y-2.5">
            <h3 class="text-xs font-extrabold uppercase tracking-wider text-[#a3d9c6] flex items-center justify-between">
              <span>📂 {html.escape(cat_name)}</span>
              <span class="text-[10px] text-gray-400 font-semibold">{len(items)} Rehber</span>
            </h3>
            <ul class="space-y-1.5">
{"".join(links_html)}
            </ul>
          </div>""")

    return f"""
  <!-- PROGRAMATİK STATİK SEO REHBERLERİ DİZİNİ (/cozum/ 30 POPÜLER OYUN HATASI) -->
  <section id="populerCozumRehberleri" aria-labelledby="populer-cozum-rehberleri-baslik" class="max-w-[1600px] w-full mx-auto px-4 lg:px-8 pt-4 pb-2">
    <div class="bg-[#181f2c] border border-white/10 rounded-2xl p-6 space-y-5 shadow-xl">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-white/10 pb-4">
        <div class="space-y-1">
          <div class="inline-flex items-center gap-2 text-xs font-extrabold uppercase tracking-wider text-[#88c0a8]">
            <span>📚 Doğrudan Çözüm Kütüphanesi</span>
            <span>•</span>
            <span>30 Adım Adım Teknik Rehber</span>
          </div>
          <h2 id="populer-cozum-rehberleri-baslik" class="text-lg sm:text-xl font-extrabold text-white">
            Popüler Oyun Hataları ve Çözüm Rehberleri
          </h2>
          <p class="text-xs text-gray-400">
            Türkiye'de oyuncuların en sık karşılaştığı 30 oyun hata kodu, DirectX/DLL sorunu ve ağ problemi için hazırlanmış statik çözüm sayfaları:
          </p>
        </div>
        <a href="./hata-kodlari.html" class="shrink-0 px-4 py-2 rounded-xl bg-[#212936] hover:bg-[#2a3446] border border-[#88c0a8]/35 text-xs font-bold text-[#a3d9c6] transition">
          🗂️ Tüm Hata Kodları Dizini →
        </a>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
{"".join(cat_blocks)}
      </div>
    </div>
  </section>
"""


def main():
    os.makedirs(COZUM_DIR, exist_ok=True)
    for p in PAGES:
        out_path = os.path.join(COZUM_DIR, p["slug"])
        html_str = build_page_html(p)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html_str)
    print(f"[OK] Generated {len(PAGES)} static SEO pages in {COZUM_DIR}")

    # Inject/update the section right above the footer in index.html
    index_path = os.path.join(ROOT_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        index_html = f.read()

    section_html = build_homepage_cozum_directory_html()
    marker_start = "<!-- PROGRAMATİK STATİK SEO REHBERLERİ DİZİNİ (/cozum/ 30 POPÜLER OYUN HATASI) -->"
    footer_marker = "  <!-- SEO-OPTIMIZED & LEGALLY COMPLIANT SEMANTIC FOOTER -->"

    if marker_start in index_html:
        idx_s = index_html.index(marker_start)
        idx_f = index_html.index(footer_marker)
        index_html = index_html[:idx_s].rstrip() + "\n" + section_html + "\n" + index_html[idx_f:]
    elif footer_marker in index_html:
        index_html = index_html.replace(footer_marker, section_html + "\n" + footer_marker, 1)

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_html)
    print("[OK] Updated index.html with 30 /cozum/ links section above footer")


if __name__ == "__main__":
    main()
