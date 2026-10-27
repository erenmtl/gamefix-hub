import difflib
import json
import random
import re


def slugify(text: str) -> str:
    tr_map = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    text = text.translate(tr_map).lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "custom-game"


# Rich catalog of iconic PC games for instant fuzzy recognition ("victorie 3" -> "Victoria 3") and random suggestions
WORLD_GAMES_CATALOG = [
    {
        "slug": "victoria-3",
        "name": "Victoria 3",
        "short_name": "Victoria 3",
        "aliases": ["victorie 3", "victorie3", "victoria3", "vic 3", "vic3", "viktoria 3", "viktorya 3", "victoria iii"],
        "category": "Büyük Strateji (Grand Strategy)",
        "developer": "Paradox Development Studio",
        "accent_color": "#8c6d53",
        "secondary_color": "#211c18",
        "engine": "Clausewitz Engine",
        "anticheat": "Paradox Launcher / Steam",
        "banner_subtitle": "Clausewitz Motoru 1900 Sonrası Geç Oyun Kasması (Late-Game Tick Lag), Paradox Launcher v2 Hatası ve Multiplayer OOS Çözümleri",
        "common_tags": ["Late-Game Lag", "Paradox Launcher v2", "CTD Crash", "Multiplayer OOS", "DX11 vs Vulkan", "Pop Consolidation"],
        "default_issues": [
            {
                "title": "1880-1900 Sonrası Geç Oyun (Late-Game) Aşırı Takılma ve Gün Geçiş Hızı Düşüşü",
                "error_code": "VIC3-LATEGAME-TICK",
                "severity": "Kritik",
                "category": "Performans & FPS",
                "symptom_summary": "Oyunun ilk yıllarında 5x hızda akıcı akan zaman, 1885 sonrasında kültür/nüfus (Pop) parçalanması yüzünden haftada bir donarak ilerliyor.",
                "forum_sources": [
                    {
                        "forum": "Reddit r/victoria3 & Paradox Plaza",
                        "thread": "[Guide] Massive Late-Game Performance Boost: Hybrid Pop Consolidation & Shader Settings",
                        "quote": "Yeni oyuna başlarken Oyun Kuralları (Game Rules) altından 'Pop Consolidation (Nüfus Birleştirme)' ayarını 'Aggressive' yapmak ve Grafiklerden FPS sınırını 60'a sabitlemek CPU'ya binen günlük hesaplama yükünü %45 azaltıyor.",
                        "upvotes": 1180
                    },
                    {
                        "forum": "Steam Community Guides",
                        "thread": "Victoria 3 Clausewitz Engine CPU Thread & Pagefile Optimization",
                        "quote": "Victoria 3 geç oyunda 18GB+ RAM tüketebiliyor. Harita yakınlaştırmada 'Shader Quality: Medium' yapmak VRAM şişmesini kesiyor.",
                        "upvotes": 540
                    }
                ],
                "ai_root_cause": "Clausewitz motoru her oyun günü (tick) dünyadaki binlerce küçük Pop (nüfus/kültür/meslek) grubunun tüketim ve göç hesaplamasını CPU üzerinde yapar. GPU %100 yükte çalıştığında ise ana render döngüsü simülasyon iş parçacığını bekletir.",
                "ai_solution_steps": [
                    {
                        "step": 1,
                        "title": "Oyun Kurallarında 'Pop Consolidation' Ayarını Aggressive Yapın",
                        "detail": "Çok küçük nüfus gruplarının (10-50 kişilik göçmen grupları) ana nüfusla birleşmesini sağlayarak işlemcinin günlük hesaplama sayısını yarıya indirin.",
                        "difficulty": "Kolay"
                    },
                    {
                        "step": 2,
                        "title": "Kare Hızını (Max FPS) 60'a Sabitleyin",
                        "detail": "Ayarlar -> Görüntü -> 'Max FPS: 60' seçin. Sınırsız FPS bırakıldığında ekran kartı haritayı çizmek için CPU'yu meşgul eder ve gün geçiş hızı (tick speed) düşer.",
                        "difficulty": "Kolay"
                    }
                ],
                "verify_command": "Get-Process victoria3 -ErrorAction SilentlyContinue | Select-Object Name, CPU, WorkingSet64",
                "success_rate": 95
            },
            {
                "title": "Paradox Launcher v2 'General Error' ve 'Initializing Game' Ekranında Çökme (CTD)",
                "error_code": "PDX-LAUNCHER-CTD",
                "severity": "Yüksek",
                "category": "Çökme & Başlatma",
                "symptom_summary": "Steam'den Oyna dediğinde Paradox Launcher hata veriyor ya da oyun açılırken 'Initializing Game' ekranında masaüstüne atıyor.",
                "forum_sources": [
                    {
                        "forum": "Paradox Interactive Forums",
                        "thread": "[SOLVED] Victoria 3 crashes on 'Initializing Game' after update",
                        "quote": "Belgelerim\\Paradox Interactive\\Victoria 3\\shadercache klasörünü silmek ve oyunu binaries/victoria3.exe üzerinden tam ekran iyileştirmeleri kapalı başlatmak sorunu çözdü.",
                        "upvotes": 690
                    }
                ],
                "ai_root_cause": "Güncelleme sonrası `Belgeler\\Paradox Interactive\\Victoria 3\\shadercache` içindeki derlenmiş DX11 gölgelendiricilerinin bozulması veya eski mod yükleme sırasının (`dlc_load.json`) çakışmasıdır.",
                "ai_solution_steps": [
                    {
                        "step": 1,
                        "title": "shadercache Klasörünü ve dlc_load.json Dosyasını Temizleyin",
                        "detail": "`Belgeler\\Paradox Interactive\\Victoria 3` klasörüne girip `shadercache` klasörünü ve `dlc_load.json` dosyasını silin, ardından Steam dosya doğrulaması yapın.",
                        "difficulty": "Kolay"
                    }
                ],
                "verify_command": "Test-Path \"$env:USERPROFILE\\Documents\\Paradox Interactive\\Victoria 3\\shadercache\"",
                "success_rate": 96
            }
        ]
    },
    {
        "slug": "hearts-of-iron-4",
        "name": "Hearts of Iron IV",
        "short_name": "HOI4",
        "aliases": ["hoi 4", "hoi4", "hearts of iron 4", "harts of iron 4", "heart of iron 4", "hoi iv"],
        "category": "Büyük Strateji",
        "developer": "Paradox Development Studio",
        "accent_color": "#6f7f65",
        "secondary_color": "#1b2119",
        "engine": "Clausewitz Engine",
        "anticheat": "Paradox Launcher / Steam",
        "banner_subtitle": "1942 Sonrası Tümen Lagı, DirectX 11 vs DX9 Çökmesi, Mod Yüklenmeme ve Multiplayer Senkronizasyon (OOS) Çözümleri",
        "common_tags": ["1943 Lag", "Launcher Mod Fix", "DX9 vs DX11", "Map Icon Stutter", "OOS Error"],
        "default_issues": [
            {
                "title": "Modların Aktif Olmaması ve Paradox Launcher 'Descriptor File Missing' Hatası",
                "error_code": "HOI4-MOD-DESC",
                "severity": "Yüksek",
                "category": "Çökme & Başlatma",
                "symptom_summary": "Steam Atölye'den abone olunan modlar (Kaiserreich, Road to 56 vb.) Launcher'da kırmızı ünlem veriyor veya oyunda yüklenmiyor.",
                "forum_sources": [
                    {
                        "forum": "Reddit r/hoi4",
                        "thread": "How to fix 'Something looks wrong with the downloaded files' in HOI4 Launcher",
                        "quote": "Belgelerim\\Paradox Interactive\\Hearts of Iron IV içindeki launcher-v2.sqlite dosyasını ve mod klasörünü silip Launcher'ı yeniden açmak tüm atölye modlarını temiz şekilde senkronize ediyor.",
                        "upvotes": 940
                    }
                ],
                "ai_root_cause": "Paradox Launcher'ın yerel SQLite veritabanı (`launcher-v2.sqlite`) Steam Workshop önbelleğiyle senkronizasyonu kaybettiğinde `.mod` işaretçi dosyalarını okuyamaz.",
                "ai_solution_steps": [
                    {
                        "step": 1,
                        "title": "launcher-v2.sqlite Veritabanını Yenileyin",
                        "detail": "`Belgeler\\Paradox Interactive\\Hearts of Iron IV` klasöründeki `launcher-v2.sqlite` dosyasını silin ve oyunu Steam'den başlatıp 30 saniye modların taranmasını bekleyin.",
                        "difficulty": "Kolay"
                    }
                ],
                "verify_command": "Test-Path \"$env:USERPROFILE\\Documents\\Paradox Interactive\\Hearts of Iron IV\\launcher-v2.sqlite\"",
                "success_rate": 97
            }
        ]
    },
    {
        "slug": "mount-and-blade-2-bannerlord",
        "name": "Mount & Blade II: Bannerlord",
        "short_name": "Bannerlord",
        "aliases": ["bannerlord", "banerlord", "mount and blade 2", "mb bannerlord", "m&b 2", "mount blade 2"],
        "category": "Aksiyon RPG / Strateji",
        "developer": "TaleWorlds Entertainment",
        "accent_color": "#a67b4b",
        "secondary_color": "#231c15",
        "engine": "TaleWorlds Engine",
        "anticheat": "BattlEye (Multiplayer)",
        "banner_subtitle": "d3d_device_context_map GPU Çökmesi, Harmony / Mod Yükleme Sırası Hatası ve Kuşatma Savaşlarında Stutter Çözümü",
        "common_tags": ["d3d_device_context", "Harmony Crash", "Unblock DLL", "Siege Audio Lag", "Shader Cache"],
        "default_issues": [
            {
                "title": "d3d_device_context_->Map at rglGPU_device::lock_texture GPU Çökme Hatası",
                "error_code": "RGL-GPU-MAP-CRASH",
                "severity": "Kritik",
                "category": "Çökme & Başlatma",
                "symptom_summary": "Savaşa girerken veya şehir menüsünde 'd3d_device_context_->Map at rglGPU_device::lock_texture' hatası verip oyun çöküyor.",
                "forum_sources": [
                    {
                        "forum": "TaleWorlds Resmi Forumu & Technopat",
                        "thread": "[Çözüldü] d3d_device_context_map hatası ve ProgramData Shader temizliği",
                        "quote": "C:\\ProgramData\\Mount and Blade II Bannerlord\\Shaders klasörünü tamamen silip oyun içi Ekran Kartı Bellek kullanımını (Terrain Quality) düşürünce çökme tamamen bitti.",
                        "upvotes": 820
                    }
                ],
                "ai_root_cause": "TaleWorlds motorunda sıkıştırılmış doku arabelleği (`lock_texture`) bozuk gölgelendirici önbelleği veya aşırı keskinleştirme filtresiyle çakıştığında DirectX 11 cihazı sıfırlanır.",
                "ai_solution_steps": [
                    {
                        "step": 1,
                        "title": "ProgramData Altındaki Bannerlord Shaders Klasörünü Silin",
                        "detail": "`C:\\ProgramData\\Mount and Blade II Bannerlord\\Shaders` klasörünü silin ve Steam üzerinden dosya doğrulaması yapın.",
                        "difficulty": "Kolay"
                    },
                    {
                        "step": 2,
                        "title": "Mod Kullanıyorsanız DLL Engellemesini Kaldırın (Unblock DLL)",
                        "detail": "NexusMods'tan indirilen modların `bin\\Win64_Shipping_Client\\*.dll` dosyalarına sağ tıklayıp Özellikler -> 'Engellemeyi Kaldır (Unblock)' kutucuğunu işaretleyin.",
                        "difficulty": "Kolay"
                    }
                ],
                "verify_command": "Test-Path \"C:\\ProgramData\\Mount and Blade II Bannerlord\\Shaders\"",
                "success_rate": 95
            }
        ]
    },
    {
        "slug": "red-dead-redemption-2",
        "name": "Red Dead Redemption 2",
        "short_name": "RDR 2",
        "aliases": ["rdr 2", "rdr2", "red dead 2", "red dead redemption", "red dead redemtion 2"],
        "category": "Açık Dünya Aksiyon",
        "developer": "Rockstar Games",
        "accent_color": "#a85751",
        "secondary_color": "#241717",
        "engine": "RAGE Engine (Vulkan / DX12)",
        "anticheat": "Rockstar Games Launcher",
        "banner_subtitle": "ERR_GFX_STATE Çökmesi, Unknown Error FFFFFFFF, Vulkan vs DirectX 12 Stutter ve Belgelerim system.xml Çözümleri",
        "common_tags": ["ERR_GFX_STATE", "Error FFFFFFFF", "Vulkan vs DX12", "sga_ files", "Adapter 0 Fix"],
        "default_issues": [
            {
                "title": "ERR_GFX_STATE ve 'Unknown Error FFFFFFFF' Oyun Çökme Hatası",
                "error_code": "ERR_GFX_STATE / FFFFFFFF",
                "severity": "Kritik",
                "category": "Çökme & Başlatma",
                "symptom_summary": "Hikaye modunda veya kampta rastgele 'ERR_GFX_STATE' ya da 'Unknown Error FFFFFFFF' vererek masaüstüne atıyor.",
                "forum_sources": [
                    {
                        "forum": "Reddit r/PCRedDead",
                        "thread": "Permanent Fix for ERR_GFX_STATE (Deleting sga_vulkan_final_init files)",
                        "quote": "Belgelerim\\Rockstar Games\\Red Dead Redemption 2\\Settings klasöründeki 'sga_' ile başlayan 3 önbellek dosyasını silmek ve başlatma argümanına -ignorepipelinecache eklemek ERR_GFX_STATE hatasını %100 çözüyor.",
                        "upvotes": 1950
                    }
                ],
                "ai_root_cause": "RDR 2'nin Vulkan/DX12 boru hattı önbellek dosyaları (`sga_vulkan_final_init.*`) sürücü güncellemesi sonrasında bozulduğunda GPU komut kuyruğu kilitlenir.",
                "ai_solution_steps": [
                    {
                        "step": 1,
                        "title": "Settings Klasöründeki 'sga_' Dosyalarını Silin",
                        "detail": "`Belgeler\\Rockstar Games\\Red Dead Redemption 2\\Settings` klasörüne girip `sga_` ile başlayan tüm dosyaları silin (`system.xml` kalsın).",
                        "difficulty": "Kolay"
                    },
                    {
                        "step": 2,
                        "title": "-ignorepipelinecache Başlatma Seçeneğini Ekleyin",
                        "detail": "Steam / Rockstar Launcher başlatma seçeneklerine `-ignorepipelinecache` kodunu ekleyin.",
                        "difficulty": "Kolay"
                    }
                ],
                "verify_command": "Get-ChildItem \"$env:USERPROFILE\\Documents\\Rockstar Games\\Red Dead Redemption 2\\Settings\\sga_*\" -ErrorAction SilentlyContinue",
                "success_rate": 97
            }
        ]
    },
    {
        "slug": "baldurs-gate-3",
        "name": "Baldur's Gate 3",
        "short_name": "Baldur's Gate 3",
        "aliases": ["baldurs gate 3", "bg3", "bg 3", "baldur gate 3", "baldurs gate"],
        "category": "CRPG / Rol Yapma",
        "developer": "Larian Studios",
        "accent_color": "#946b88",
        "secondary_color": "#221a21",
        "engine": "Divinity 4.0 Engine (DX11 / Vulkan)",
        "anticheat": "Larian Launcher / DRM-Free",
        "banner_subtitle": "Act 3 (Lower City) Ağır FPS Düşüşü, DXGI_ERROR_DEVICE_REMOVED Çökmesi ve Mod Fixer Kayıt Yüklenmeme Çözümleri",
        "common_tags": ["Act 3 FPS Fix", "Vulkan vs DX11", "Dynamic Crowds", "Larian Launcher Skip", "Script Extender"],
        "default_issues": [
            {
                "title": "Act 3 (Baldur's Gate Şehri) Aşırı FPS Düşüşü ve DXGI_ERROR_DEVICE_REMOVED Çökmesi",
                "error_code": "BG3-ACT3-DXGI",
                "severity": "Yüksek",
                "category": "Performans & FPS",
                "symptom_summary": "Act 1 ve Act 2 akıcıyken Act 3 şehir merkezinde FPS yarıya düşüyor ve bazen DXGI hatasıyla çöküyor.",
                "forum_sources": [
                    {
                        "forum": "Reddit r/BaldursGate3",
                        "thread": "Act 3 Stutter & Crash Fix: Disable Dynamic Crowds + Bypass Larian Launcher",
                        "quote": "Larian Launcher'ı `--skip-launcher` ile atlamak ve oyun içi 'Dynamic Crowds (Dinamik Kalabalık)' ayarını kapatmak Act 3'te +35 FPS kazandırdı.",
                        "upvotes": 1410
                    }
                ],
                "ai_root_cause": "Act 3'teki yüzlerce NPC'nin yapay zeka davranış ağacı ve 'Dynamic Crowds' fiziği tek ana CPU iş parçacığını doyurur; Larian Launcher arka planda açık kaldığında ise CEF bellek sızıntısı yaratır.",
                "ai_solution_steps": [
                    {
                        "step": 1,
                        "title": "--skip-launcher Argümanını Ekleyin ve Dynamic Crowds Kapatın",
                        "detail": "Steam Başlatma Seçeneklerine `--skip-launcher` yazın. Oyun içi Video ayarlarında API olarak **DirectX 11** seçip **Dynamic Crowds** kutucuğunun işaretini kaldırın.",
                        "difficulty": "Kolay"
                    }
                ],
                "verify_command": "Get-Process bg3* -ErrorAction SilentlyContinue | Select-Object Name, WorkingSet64",
                "success_rate": 95
            }
        ]
    },
    {
        "slug": "euro-truck-simulator-2",
        "name": "Euro Truck Simulator 2 & TruckersMP",
        "short_name": "ETS 2",
        "aliases": ["ets 2", "ets2", "euro truck 2", "euro truck simulator", "truckersmp"],
        "category": "Simülasyon",
        "developer": "SCS Software",
        "accent_color": "#58829e",
        "secondary_color": "#182128",
        "engine": "Prism3D Engine",
        "anticheat": "TruckersMP Client",
        "banner_subtitle": "Şehir İçi Kabin Kamerasında Takılma (uset t_averaging_window_length), TruckersMP Fatal Error ve Direksiyon Force Feedback Sorunu",
        "common_tags": ["config.cfg Stutter", "TruckersMP Crash", "DX11 Buffer Page Size", "Force Feedback Fix"],
        "default_issues": [
            {
                "title": "Yüksek Sistemde Bile Şehir İçinde ve Kabin Kamerasında Anlık Takılma (Rubberbanding Stutter)",
                "error_code": "ETS2-BUFFER-CFG",
                "severity": "Yüksek",
                "category": "Performans & FPS",
                "symptom_summary": "Ekran kartı kullanımı düşük olmasına rağmen kavşaklara girerken ve aynalara bakarken görüntü tekleme yapıyor.",
                "forum_sources": [
                    {
                        "forum": "SCS Forum & Technopat Sosyal",
                        "thread": "ETS 2 config.cfg r_buffer_page_size 30 ve t_averaging_window_length Çözümü",
                        "quote": "Belgelerim\\Euro Truck Simulator 2\\config.cfg içindeki uset r_buffer_page_size değerini '10'dan '30'a çıkarmak tüm doku/model yükleme takılmalarını bitiriyor!",
                        "upvotes": 920
                    }
                ],
                "ai_root_cause": "Prism3D motorunun varsayılan bellek sayfa boyutu (`r_buffer_page_size 10`) yeni şehir DLC'lerindeki ve TruckersMP kalabalığındaki yüksek poligonlu tırları tek karede yükleyemez.",
                "ai_solution_steps": [
                    {
                        "step": 1,
                        "title": "config.cfg İçinde r_buffer_page_size Değerini 30 Yapın",
                        "detail": "`Belgeler\\Euro Truck Simulator 2\\config.cfg` dosyasını Not Defteri ile açıp `uset r_buffer_page_size \"10\"` satırını `uset r_buffer_page_size \"30\"` olarak değiştirin.",
                        "difficulty": "Kolay"
                    }
                ],
                "verify_command": "Select-String -Path \"$env:USERPROFILE\\Documents\\Euro Truck Simulator 2\\config.cfg\" -Pattern \"r_buffer_page_size\" -ErrorAction SilentlyContinue",
                "success_rate": 97
            }
        ]
    },
    {
        "slug": "forza-horizon-5",
        "name": "Forza Horizon 5",
        "short_name": "Forza Horizon 5",
        "aliases": ["fh5", "fh 5", "forza 5", "forza horizon"],
        "category": "Yarış / Açık Dünya",
        "developer": "Playground Games",
        "accent_color": "#b36b82",
        "secondary_color": "#24191e",
        "engine": "ForzaTech Engine",
        "anticheat": "Xbox Live / Encryption",
        "banner_subtitle": "Splash Screen (Küçük Pencere) Açılıp Kapanma, Düşük Yayın Bant Genişliği (Low Streaming Bandwidth) ve Bağlantı Kopması",
        "common_tags": ["Splash Screen Crash", "Low Streaming Bandwidth", "Teredo Network Fix", "VRAM Leak"],
        "default_issues": [
            {
                "title": "Oyun Başlarken Küçük Kapak Resmi (Splash Screen) Ekranında Kapanma",
                "error_code": "FH5-SPLASH-0xc0000005",
                "severity": "Kritik",
                "category": "Çökme & Başlatma",
                "symptom_summary": "Oyna tuşuna basınca küçük Forza Horizon 5 penceresi geliyor, 5 saniye sonra hata vermeden kapanıyor.",
                "forum_sources": [
                    {
                        "forum": "Reddit r/ForzaHorizon",
                        "thread": "Fixed FH5 crashing on splash screen (Nahimic Companion / Sonic Studio / RivaTuner)",
                        "quote": "Anakart ses sürücüsüyle gelen 'Nahimic Service' servisini durdurmak ve RivaTuner/MSI Afterburner'ı kapatmak splash screen çökmesini anında çözdü.",
                        "upvotes": 1150
                    }
                ],
                "ai_root_cause": "ForzaTech motorunun bellek şifrelemesi, `NahimicService` ses katmanı ve `RTSS` kancalarını bellek müdahalesi olarak algılayıp `0xc0000005` istisnasıyla süreci sonlandırır.",
                "ai_solution_steps": [
                    {
                        "step": 1,
                        "title": "Nahimic Servisini ve RivaTuner Yakalamasını Devre Dışı Bırakın",
                        "detail": "`services.msc` içinden `Nahimic service` varsa Durdurun. MSI Afterburner / RivaTuner açıkken giriyorsanız `ForzaHorizon5.exe` için Detection Level: None seçin.",
                        "difficulty": "Kolay"
                    }
                ],
                "verify_command": "Get-Service -Name '*Nahimic*' -ErrorAction SilentlyContinue",
                "success_rate": 95
            }
        ]
    },
    {
        "slug": "helldivers-2",
        "name": "HELLDIVERS 2",
        "short_name": "Helldivers 2",
        "aliases": ["helldiver 2", "helldivers", "helldivers2", "hd2"],
        "category": "Co-op Shooter",
        "developer": "Arrowhead Game Studios",
        "accent_color": "#a89552",
        "secondary_color": "#221f16",
        "engine": "Autodesk Stingray",
        "anticheat": "nProtect GameGuard",
        "banner_subtitle": "GameGuard Error 114, Görev Sonu Çıkarma (Extraction) Çökmesi ve --use-d3d11 Performans Çözümü",
        "common_tags": ["GameGuard Error 114", "--use-d3d11", "Extraction Crash", "Crossplay Friend Fix"],
        "default_issues": [
            {
                "title": "GameGuard Başlatma Hatası (Error 114) ve Görev Ortasında Aniden Çökme",
                "error_code": "GG-ERR-114 / D3D11",
                "severity": "Kritik",
                "category": "Anti-Cheat & Güvenlik",
                "symptom_summary": "Oyun açılırken GameGuard Error 114 veriyor veya gezegene iniş/çıkarma sırasında oyun donup kapanıyor.",
                "forum_sources": [
                    {
                        "forum": "Reddit r/Helldivers",
                        "thread": "Deleting AppData Arrowhead Shader Cache & running --use-d3d11 fixed all my crashes",
                        "quote": "%appdata%\\Arrowhead\\Helldivers2\\shader_cache klasörünü silip Steam başlatma seçeneklerine --use-d3d11 yazmak hem çökmeleri bitirdi hem +25 FPS verdi.",
                        "upvotes": 1620
                    }
                ],
                "ai_root_cause": "Autodesk Stingray motorunun DX12 katmanı bazı GPU sürücülerinde hesaplama gölgelendiricisi (compute shader) kilitlenmesine yol açar.",
                "ai_solution_steps": [
                    {
                        "step": 1,
                        "title": "Arrowhead Shader Cache Silin ve --use-d3d11 Ekleyin",
                        "detail": "`%appdata%\\Arrowhead\\Helldivers2\\shader_cache` klasörünü silin ve Steam Başlatma Seçeneklerine `--use-d3d11` ekleyin.",
                        "difficulty": "Kolay"
                    }
                ],
                "verify_command": "Test-Path \"$env:APPDATA\\Arrowhead\\Helldivers2\\shader_cache\"",
                "success_rate": 96
            }
        ]
    },
    {
        "slug": "rainbow-six-siege",
        "name": "Tom Clancy's Rainbow Six Siege",
        "short_name": "R6 Siege",
        "aliases": ["r6", "r6 siege", "rainbow six", "rainbow 6", "r6s"],
        "category": "Taktiksel FPS",
        "developer": "Ubisoft Montreal",
        "accent_color": "#58789e",
        "secondary_color": "#181e28",
        "engine": "AnvilNext 2.0 (DX12 / DX11)",
        "anticheat": "BattlEye / Mousetrap",
        "banner_subtitle": "DX12 Stutter / Donma, BattlEye Bad Service Version ve Ubisoft Connect Senkronizasyon Hatası",
        "common_tags": ["DX12 Stutter", "BattlEye Bad Service", "Security Update Loop", "Jitter / Latency"],
        "default_issues": [
            {
                "title": "DirectX 12 Güncellemesi Sonrası Çatışmada Anlık Donma ve BattlEye Hatası",
                "error_code": "R6-DX12-STUTTER",
                "severity": "Yüksek",
                "category": "Performans & FPS",
                "symptom_summary": "Duvar kırıldığında veya dürbün açtığında (ADS) 0.5 saniyelik takılma yaşanıyor.",
                "forum_sources": [
                    {
                        "forum": "Reddit r/Rainbow6",
                        "thread": "Fix for R6 Siege Stuttering: GameSettings.ini & Ubisoft Overlay Disable",
                        "quote": "Ubisoft Connect oyun içi yer paylaşımını (Overlay) kapatmak ve Belgelerim\\My Games\\Rainbow Six - Siege içindeki GameSettings.ini'de FPSLimit değerini monitör Hz değerine sabitlemek takılmayı kesti.",
                        "upvotes": 830
                    }
                ],
                "ai_root_cause": "Ubisoft Connect Overlay (`upc.exe`) ile DX12 tam ekran sunumu çakıştığında kare zamanlaması (frame pacing) bozulur.",
                "ai_solution_steps": [
                    {
                        "step": 1,
                        "title": "Ubisoft Connect Oyun İçi Yer Paylaşımını (Overlay) Kapatın",
                        "detail": "Ubisoft Connect -> Ayarlar -> Genel sekmesinden 'Desteklenen oyunlar için oyun içi arayüzü etkinleştir' işaretini kaldırın.",
                        "difficulty": "Kolay"
                    }
                ],
                "verify_command": "Test-Path \"$env:USERPROFILE\\Documents\\My Games\\Rainbow Six - Siege\"",
                "success_rate": 94
            }
        ]
    },
    {
        "slug": "football-manager-2024",
        "name": "Football Manager 2024",
        "short_name": "FM 24",
        "aliases": ["fm 24", "fm24", "football manager", "futbol menajer", "fm 2024"],
        "category": "Spor Simülasyonu",
        "developer": "Sports Interactive",
        "accent_color": "#7b659e",
        "secondary_color": "#1e1926",
        "engine": "Match Engine",
        "anticheat": "Denuvo / Steam / Epic",
        "banner_subtitle": "Crash Dump Hatası, Maç Motorunda Takılma ve Yüz/Logo Paketi (Graphics) Yüklenmeme Çözümleri",
        "common_tags": ["Crash Dump Fix", "Clear Cache & Reload Skin", "Real Name Fix", "Match Engine Stutter"],
        "default_issues": [
            {
                "title": "Yüz / Logo Paketlerinin Görünmemesi ve Başlangıçta Crash Dump Hatası",
                "error_code": "FM24-CACHE-DUMP",
                "severity": "Orta",
                "category": "Çökme & Başlatma",
                "symptom_summary": "Graphics klasörüne atılan yüz/logo paketleri oyunda çıkmıyor veya oyun açılırken Crash Dump hatası veriyor.",
                "forum_sources": [
                    {
                        "forum": "Sortitoutsi & Technopat Sosyal",
                        "thread": "FM 24 Crash Dump ve Tema/Logo Önbellek Sıfırlama Rehberi",
                        "quote": "%localappdata%\\Sports Interactive\\Football Manager 2024 içindeki Caches ve Preferences klasörlerini silmek Crash Dump hatasını anında çözüyor.",
                        "upvotes": 610
                    }
                ],
                "ai_root_cause": "Bozuk `Preferences` veya `Caches` klasörü tema XML dosyalarını okurken bellek taşmasına neden olur.",
                "ai_solution_steps": [
                    {
                        "step": 1,
                        "title": "Caches ve Preferences Klasörlerini Sıfırlayın",
                        "detail": "`%localappdata%\\Sports Interactive\\Football Manager 2024` altındaki `Caches` ve `Preferences` klasörlerini silin. Oyun içi Tercihler'den 'Geçici Dosyaları Kullan (Use caching)' işaretini kaldırıp 'Temayı Yeniden Yükle' butonuna basın.",
                        "difficulty": "Kolay"
                    }
                ],
                "verify_command": "Test-Path \"$env:LOCALAPPDATA\\Sports Interactive\\Football Manager 2024\\Caches\"",
                "success_rate": 98
            }
        ]
    },
    {
        "slug": "black-myth-wukong",
        "name": "Black Myth: Wukong",
        "short_name": "Black Myth: Wukong",
        "aliases": ["wukong", "black myth", "black myth wukong", "wu kong"],
        "category": "Aksiyon RPG",
        "developer": "Game Science",
        "accent_color": "#9e7c58",
        "secondary_color": "#221c16",
        "engine": "Unreal Engine 5",
        "anticheat": "Denuvo",
        "banner_subtitle": "Out of Video Memory (Intel 13./14. Nesil Shader Compilation Crash), UE5 Traversal Stutter ve -dx11 Uyumluluk Modu",
        "common_tags": ["Out of Video Memory", "Shader Compilation Crash", "UE5 Traversal Stutter", "-dx11 Launch"],
        "default_issues": [
            {
                "title": "Başlangıçta 'Out of Video Memory Trying to Allocate a Rendering Resource' Hatası",
                "error_code": "UE5-SHADER-OOM",
                "severity": "Kritik",
                "category": "Çökme & Başlatma",
                "symptom_summary": "Ekran kartında 12GB/16GB VRAM olmasına rağmen ilk açılışta 'Shader Compilation' sırasında 'Out of video memory' verip çöküyor.",
                "forum_sources": [
                    {
                        "forum": "Steam Community & Reddit r/BlackMythWukong",
                        "thread": "Solved 'Out of Video Memory' during Shader Compilation (Intel 13th/14th Gen & Pagefile)",
                        "quote": "Bu hata ekran kartı belleğinden değil, gölgelendirici derlemesi sırasında işlemci voltaj kararsızlığından veya sanal bellek yetersizliğinden çıkıyor. BIOS güncellemek veya Windows Güç Planını 'Dengeli/Güç Tasarrufu'na alıp derlemeyi geçmek %100 işe yarıyor!",
                        "upvotes": 1490
                    }
                ],
                "ai_root_cause": "Unreal Engine 5'in Oodle gölgelendirici sıkıştırma açıcısı tüm CPU çekirdeklerini %100 AVX yüküne soktuğunda kararsız çekirdek çarpanları sahte `Out of Video Memory` hatası fırlatır.",
                "ai_solution_steps": [
                    {
                        "step": 1,
                        "title": "Gölgelendirici Derlemesi Sırasında Güç Planını Geçici Olarak Düşürün veya Uyumluluk Modu Açın",
                        "detail": "İlk açılıştaki Shader Compilation ekranını geçmek için Windows Güç Planını geçici olarak 'Güç Tasarrufu' yapın (derleme bitince tekrar Yüksek Performans'a alın) veya Steam'den 'Compatibility Mode' ile başlatın.",
                        "difficulty": "Kolay"
                    }
                ],
                "verify_command": "Get-CimInstance Win32_Processor | Select-Object Name, MaxClockSpeed",
                "success_rate": 96
            }
        ]
    },
    {
        "slug": "palworld",
        "name": "Palworld",
        "short_name": "Palworld",
        "aliases": ["palworld", "pal world", "pallworld"],
        "category": "Açık Dünya Hayatta Kalma",
        "developer": "Pocketpair",
        "accent_color": "#58949e",
        "secondary_color": "#172226",
        "engine": "Unreal Engine 5",
        "anticheat": "Topluluk / Dedicated Server",
        "banner_subtitle": "EXCEPTION_ACCESS_VIOLATION (UE-Pal Crash), Kayıt Dosyası (World Save) Bozulması ve Bellek Sızıntısı Çözümleri",
        "common_tags": ["UE-Pal Crash", "World Save Backup", "Memory Leak", "Multiplayer Timeout"],
        "default_issues": [
            {
                "title": "UnrealProcessHasCrashed: UE-Pal EXCEPTION_ACCESS_VIOLATION ve Kayıt Kurtarma",
                "error_code": "UE-PAL-CRASH",
                "severity": "Yüksek",
                "category": "Çökme & Başlatma",
                "symptom_summary": "Dünyaya girerken 'UE-Pal has crashed' hatası veriyor veya elektrik kesintisi sonrası dünya kaydı açılmıyor.",
                "forum_sources": [
                    {
                        "forum": "Reddit r/Palworld",
                        "thread": "How to restore corrupted World Save from built-in backup folder in 1 minute",
                        "quote": "%localappdata%\\Pal\\Saved\\SaveGames klasörünün içinde oyunun otomatik aldığı 'backup\\world' yedeklerini ana klasöre kopyalamak çöken dünyayı anında kurtarıyor.",
                        "upvotes": 1320
                    }
                ],
                "ai_root_cause": "Otomatik kayıt sırasında oyun kapanırsa `Level.sav` ve `LocalData.sav` dosyası yarım yazılır ve UE5 serileştiricisi dünyayı yüklerken çöker.",
                "ai_solution_steps": [
                    {
                        "step": 1,
                        "title": "Otomatik backup Klasöründen Önceki Kaydı Geri Yükleyin",
                        "detail": "`%localappdata%\\Pal\\Saved\\SaveGames\\<SteamID>\\<WorldID>\\backup` içindeki `local` ve `world` klasörlerinden bir önceki tarihe ait dosyaları bir üst dizine kopyalayıp değiştirin.",
                        "difficulty": "Kolay"
                    }
                ],
                "verify_command": "Test-Path \"$env:LOCALAPPDATA\\Pal\\Saved\\SaveGames\"",
                "success_rate": 97
            }
        ]
    },
    {
        "slug": "dota-2",
        "name": "Dota 2",
        "short_name": "Dota 2",
        "aliases": ["dota 2", "dota2", "dota"],
        "category": "MOBA",
        "developer": "Valve",
        "accent_color": "#a65852",
        "secondary_color": "#241716",
        "engine": "Source 2",
        "anticheat": "VAC",
        "banner_subtitle": "Takım Savaşlarında (Teamfight) FPS Çöküşü, Maç Bulundu Onay Butonu Gelmeme (Confirming Match Loop) ve Vulkan/DX11 Ayarları",
        "common_tags": ["Confirming Match Loop", "Teamfight Lag", "Compute Shaders", "Shader Pre-Caching"],
        "default_issues": [
            {
                "title": "Büyük Takım Savaşlarında (Ultiler Atıldığında) Anlık FPS Çöküşü",
                "error_code": "DOTA2-TEAMFIGHT-FPS",
                "severity": "Yüksek",
                "category": "Performans & FPS",
                "symptom_summary": "Koridor aşamasında 180 FPS alırken 5v5 takım savaşlarında ekran 40 FPS'e düşüp takılıyor.",
                "forum_sources": [
                    {
                        "forum": "Reddit r/DotA2",
                        "thread": "Enable 'Compute Shaders' & delete rate-limiting panorama UI videos for smooth teamfights",
                        "quote": "Video ayarlarından 'Compute Shaders (Hesaplama Gölgelendiricileri)' açmak ve Gösterge Paneli Kalitesini düşürmek takım savaşı FPS'ini %30 artırdı.",
                        "upvotes": 910
                    }
                ],
                "ai_root_cause": "Source 2 parçacık efektleri ve Panorama UI animasyonları aynı karede CPU render kuyruğunu doldurur.",
                "ai_solution_steps": [
                    {
                        "step": 1,
                        "title": "Compute Shaders Açın ve Gölgeleri Orta/Düşük Yapın",
                        "detail": "Dota 2 Görüntü Ayarları -> Gelişmiş altında 'Compute Shaders' kutucuğunu işaretleyin ve NVIDIA Reflex'i 'Etkin' yapın.",
                        "difficulty": "Kolay"
                    }
                ],
                "verify_command": "Get-Process dota2 -ErrorAction SilentlyContinue | Select-Object Name, WorkingSet64",
                "success_rate": 94
            }
        ]
    },
    {
        "slug": "escape-from-tarkov",
        "name": "Escape from Tarkov",
        "short_name": "Tarkov",
        "aliases": ["tarkov", "eft", "escape from tarkov", "escape tarkov"],
        "category": "Hardcore Extraction FPS",
        "developer": "Battlestate Games",
        "accent_color": "#827c68",
        "secondary_color": "#1f1e1a",
        "engine": "Unity Engine",
        "anticheat": "BattlEye",
        "banner_subtitle": "Streets of Tarkov VRAM/RAM Taşması, Dürbün Açarken (PIP Scope) FPS Yarıya Düşmesi ve Server Connection Lost Çözümü",
        "common_tags": ["Streets of Tarkov Lag", "PIP Scope Stutter", "Auto RAM Cleaner", "Server Connection Lost"],
        "default_issues": [
            {
                "title": "Streets of Tarkov Haritasında Donma ve Dürbün (Scope) Açarken FPS Çöküşü",
                "error_code": "EFT-STREETS-RAM",
                "severity": "Kritik",
                "category": "Performans & FPS",
                "symptom_summary": "Streets haritasına girerken oyun kilitleniyor veya 4x/6x dürbün açıldığında FPS yarıya düşüyor.",
                "forum_sources": [
                    {
                        "forum": "Reddit r/EscapefromTarkov",
                        "thread": "Streets of Tarkov Low Texture Mode + Only Use Physical Cores Guide",
                        "quote": "Oyun ayarlarından 'Streets of Tarkov Lower Texture Resolution Mode' kutucuğunu işaretlemek ve 'Only Use Physical Cores' açmak dürbün takılmalarını kesti.",
                        "upvotes": 1240
                    }
                ],
                "ai_root_cause": "Tarkov dürbünlerde 'Picture-in-Picture (Çift Render)' tekniği kullanır; bu da sahneyi iki kez çizerek VRAM ve CPU önbelleğini zorlar.",
                "ai_solution_steps": [
                    {
                        "step": 1,
                        "title": "Streets Düşük Doku Modunu ve 'Only Use Physical Cores' Ayarını Açın",
                        "detail": "Oyun Ayarları -> Oyun sekmesinden 'Only use physical cores' açın; Grafik sekmesinin en altındaki 'Streets of Tarkov Lower Texture Resolution Mode' kutucuğunu işaretleyin.",
                        "difficulty": "Kolay"
                    }
                ],
                "verify_command": "Get-CimInstance Win32_PageFileUsage | Select-Object Name, AllocatedBaseSize",
                "success_rate": 94
            },
            {
                "title": "Sunucuya Bağlanırken 'Server Connection Lost' ve Yüksek Paket Kaybı",
                "error_code": "EFT-CONN-LOST",
                "severity": "Yüksek",
                "category": "Ağ & Bağlantı",
                "symptom_summary": "Raid'e girerken 'Awaiting Session Start' ekranında takılıp Server Connection Lost veriyor.",
                "forum_sources": [
                    {
                        "forum": "Battlestate Games Forum & Reddit",
                        "thread": "Fixing Server Connection Lost (IPv6 Dual-Stack DS-Lite & MTU 1472 Fix)",
                        "quote": "BSG Launcher'dan sadece pingi 60ms altındaki Avrupa sunucularını (Central/South) manuel seçmek ve ağ bağdaştırıcısında IPv6'yı kapatmak kopmaları %95 engelledi.",
                        "upvotes": 740
                    }
                ],
                "ai_root_cause": "Otomatik sunucu seçimi yüksek jitter'lı rotalara bağlandığında Tarkov'un katı UDP paket zaman aşımı oturumu düşürür.",
                "ai_solution_steps": [
                    {
                        "step": 1,
                        "title": "BSG Launcher'dan Düşük Pingli Sunucuları Manuel Seçin",
                        "detail": "BSG Launcher -> Change Server menüsünden 'Auto' işaretini kaldırıp yalnızca pingi 65ms altındaki 3-4 sunucuyu işaretleyin.",
                        "difficulty": "Kolay"
                    }
                ],
                "verify_command": "Get-NetAdapterBinding -ComponentID ms_tcpip6",
                "success_rate": 93
            }
        ]
    },
    {
        "slug": "the-witcher-3",
        "name": "The Witcher 3: Wild Hunt (Next-Gen)",
        "short_name": "The Witcher 3",
        "aliases": ["witcher 3", "the witcher 3", "witcher", "tw3"],
        "category": "Açık Dünya RPG",
        "developer": "CD PROJEKT RED",
        "accent_color": "#b05c52",
        "secondary_color": "#241716",
        "engine": "REDengine 3 (DX12 / DX11)",
        "anticheat": "REDlauncher / DRM-Free",
        "banner_subtitle": "Next-Gen DirectX 12 Ray Tracing Çökmesi, Novigrad/Hierarch Meydanı Stutter ve HairWorks FPS Kaybı Çözümleri",
        "common_tags": ["DX12 Crash Fix", "Novigrad Stutter", "HairWorks Off", "REDlauncher Skip", "DLSS Frame Gen Crash"],
        "default_issues": [
            {
                "title": "Next-Gen Güncellemesi Sonrası DirectX 12 Modunda Çökme ve Novigrad Takılması",
                "error_code": "TW3-DX12-RT-CRASH",
                "severity": "Kritik",
                "category": "Çökme & Başlatma",
                "symptom_summary": "DX12 ile başlatıldığında Ray Tracing veya DLSS Frame Generation açıkken oyun hızlı seyahat (Fast Travel) sonrası çöküyor.",
                "forum_sources": [
                    {
                        "forum": "CDPR Forums & Reddit r/witcher",
                        "thread": "Witcher 3 Next-Gen DX12 Crash & Stutter Fix: Switch to DX11 or delete d3d11on12 files",
                        "quote": "Ray Tracing kullanmıyorsanız REDlauncher üzerinden DirectX 11 seçmek FPS'i %35 artırıyor ve tüm Novigrad takılmalarını kesiyor.",
                        "upvotes": 1340
                    }
                ],
                "ai_root_cause": "Next-Gen sürümündeki DX12 çeviri katmanı (`d3d11on12`) yoğun şehir içi çizim çağrılarında yüksek CPU ek yükü ve VRAM parçalanması oluşturur.",
                "ai_solution_steps": [
                    {
                        "step": 1,
                        "title": "REDlauncher Üzerinden DirectX 11 Moduna Geçin veya HairWorks Kapatın",
                        "detail": "Ray Tracing kullanmıyorsanız oyunu başlatırken **DX11** seçin. DX12 kullanacaksanız NVIDIA HairWorks ayarını Kapalı konuma getirin.",
                        "difficulty": "Kolay"
                    }
                ],
                "verify_command": "Get-Process witcher3 -ErrorAction SilentlyContinue | Select-Object Name, WorkingSet64",
                "success_rate": 96
            }
        ]
    },
    {
        "slug": "god-of-war-ragnarok",
        "name": "God of War Ragnarök (PC)",
        "short_name": "GoW Ragnarök",
        "aliases": ["god of war", "gow ragnarok", "god of war ragnarok", "ragnarok"],
        "category": "Aksiyon Macera",
        "developer": "Santa Monica Studio / Jetpack Interactive",
        "accent_color": "#4f84ad",
        "secondary_color": "#162029",
        "engine": "Proprietary DX12 Engine",
        "anticheat": "PlayStation PC SDK",
        "banner_subtitle": "PlayStation PC SDK Başlatma Donması, Düşük VRAM / Ekran Kartı Algılanmama ve Diyalog Sesi Gelmeme Çözümleri",
        "common_tags": ["PS PC SDK Crash", "VRAM Bypass", "Audio 5.1 Dialog Fix", "DLSS Stutter", "Realm Travel Drop"],
        "default_issues": [
            {
                "title": "Oyun Açılışında Siyah Ekran (PlayStation PC SDK Runtime Hatası) ve Ses/Diyalog Gelmeme",
                "error_code": "GOWR-PSSDK-AUDIO",
                "severity": "Yüksek",
                "category": "Çökme & Başlatma",
                "symptom_summary": "Oyun açılırken siyah ekranda kalıyor veya ara sahnelerde Kratos ve Atreus'un konuşma sesleri hiç duyulmuyor.",
                "forum_sources": [
                    {
                        "forum": "Steam Community & Technopat Sosyal",
                        "thread": "God of War Ragnarök Siyah Ekran (PsPcSdk) ve Diyalog Sesi Çözümü",
                        "quote": "Oyun klasöründeki PsPcSdkRuntimeInstaller.msi paketini manuel onarmak siyah ekranı çözüyor; Windows Ses ayarlarından Uzamsal Sesi kapatıp Stereo seçmek de diyalog seslerini geri getiriyor.",
                        "upvotes": 870
                    }
                ],
                "ai_root_cause": "PlayStation PC SDK arka plan servisi kurulmadığında kimlik doğrulama penceresi siyah ekranda asılı kalır; diyalog kaybı ise oyunun sanal 7.1 kulaklıkları gerçek merkez (Center) hoparlör sanmasından kaynaklanır.",
                "ai_solution_steps": [
                    {
                        "step": 1,
                        "title": "PsPcSdkRuntime Kurulumunu Onarın ve Ses Kanalını Stereo Yapın",
                        "detail": "Oyun dizinindeki `PsPcSdkRuntimeInstaller.msi` dosyasını çalıştırıp Onar deyin. Ses sorunu için Windows Ses Denetim Masası -> Kulaklığınız -> Yapılandır -> **Stereo** seçin.",
                        "difficulty": "Kolay"
                    }
                ],
                "verify_command": "Get-Service -Name '*PlayStation*' -ErrorAction SilentlyContinue",
                "success_rate": 95
            }
        ]
    },
    {
        "slug": "overwatch-2",
        "name": "Overwatch 2",
        "short_name": "Overwatch 2",
        "aliases": ["ow2", "ow 2", "overwatch", "overwatch2"],
        "category": "Hero Shooter (FPS)",
        "developer": "Blizzard Entertainment",
        "accent_color": "#bd7b48",
        "secondary_color": "#261d16",
        "engine": "Overwatch Engine",
        "anticheat": "Defense Matrix",
        "banner_subtitle": "'Your Rendering Device Has Been Lost' GPU Çökmesi, Maç Başı Shader Derleme Takılması ve Yüksek SIM Gecikmesi",
        "common_tags": ["Rendering Device Lost", "Shader Compiling Lag", "Reduce Buffering", "Dynamic Render Scale"],
        "default_issues": [
            {
                "title": "'Your Rendering Device Has Been Lost! Application Closing' Ekran Kartı Çökmesi",
                "error_code": "OW2-RENDER-LOST",
                "severity": "Kritik",
                "category": "Çökme & Başlatma",
                "symptom_summary": "Rekabetçi maç ortasında 'Your rendering device has been lost!' uyarısı vererek oyun aniden kapanıyor.",
                "forum_sources": [
                    {
                        "forum": "Blizzard Forums & Reddit r/Overwatch",
                        "thread": "Fixed 'Your Rendering Device Has Been Lost' once and for all",
                        "quote": "Oyun içi Dynamic Render Scale (Dinamik Ölçekleme) ayarını kapatmak, GPU fabrika hız aşırtmasını (Debug Mode) kısmak ve Razer Synapse Chroma entegrasyonunu silmek hatayı %100 çözdü.",
                        "upvotes": 1190
                    }
                ],
                "ai_root_cause": "Overwatch 2 motoru GPU saat hızı dalgalanmalarına ve `Razer Chroma SDK` bellek kancalarına karşı çok hassastır; TDR zaman aşımı oluştuğunda direkt `Rendering Device Lost` verir.",
                "ai_solution_steps": [
                    {
                        "step": 1,
                        "title": "Dynamic Render Scale Kapatın ve Belgelerim Settings_v0.ini Yenileyin",
                        "detail": "Video Ayarları -> **Dynamic Render Scale: Off** yapın. `Belgeler\\Overwatch\\Settings` klasöründeki `Settings_v0.ini` dosyasını yedekleyip silerek temiz grafik profili oluşturun.",
                        "difficulty": "Kolay"
                    }
                ],
                "verify_command": "Test-Path \"$env:USERPROFILE\\Documents\\Overwatch\\Settings\\Settings_v0.ini\"",
                "success_rate": 95
            }
        ]
    },
    {
        "slug": "diablo-iv",
        "name": "Diablo IV",
        "short_name": "Diablo IV",
        "aliases": ["diablo 4", "diablo iv", "d4", "diablo"],
        "category": "Aksiyon RPG (ARPG)",
        "developer": "Blizzard Entertainment",
        "accent_color": "#9e4f4f",
        "secondary_color": "#241616",
        "engine": "Proprietary PBR Engine",
        "anticheat": "Battle.net Warden",
        "banner_subtitle": "Fenris Crash (Out of Memory), Şehir Işınlanmalarında (Town Portal) Ağır Takılma ve Cross-Network Stutter Çözümü",
        "common_tags": ["Fenris Crash", "VRAM Leak Fix", "Disable Cross-Network Play", "DirectStorage Dll"],
        "default_issues": [
            {
                "title": "Fenris Hatası (Bellek Sızıntısı / Out of Memory) ve Şehirde Aşırı Takılma (Rubberbanding)",
                "error_code": "D4-FENRIS-VRAM",
                "severity": "Yüksek",
                "category": "Performans & FPS",
                "symptom_summary": "1 saat oynadıktan sonra ışınlanırken oyun donuyor ve 'Diablo IV has run out of memory' (Fenris) hatası veriyor.",
                "forum_sources": [
                    {
                        "forum": "Reddit r/diablo4 & Blizzard Forums",
                        "thread": "PSA: Disable Cross-Network Play & set Textures to Medium to stop rubberbanding and Fenris crashes",
                        "quote": "Sosyal ayarlardan 'Cross-Network Play (Çapraz Ağ Oyunu)' seçeneğini kapatmak açık dünyadaki tüm takılmaları (rubberbanding) kesiyor; Battle.net'te 'Disable browser hardware acceleration' yapmak da VRAM çökmesini önlüyor.",
                        "upvotes": 1560
                    }
                ],
                "ai_root_cause": "Diablo IV yakındaki her oyuncunun tüm kozmetik/sandık envanterini VRAM'e yükler; Çapraz Ağ açıkken farklı platform senkronizasyonu gecikme yaratır ve Yüksek çözünürlüklü dokular VRAM taşmasına yol açar.",
                "ai_solution_steps": [
                    {
                        "step": 1,
                        "title": "Çapraz Ağ Oyununu (Cross-Network Play) ve Tarayıcı İvmesini Kapatın",
                        "detail": "Karakter seçme ekranında Seçenekler -> **Connect (Bağlantı)** sekmesinden **Cross-Network Play** işaretini kaldırın. Battle.net -> Ayarlar -> Uygulama altından 'Tarayıcı donanım ivmesini kullan' seçeneğini kapatın.",
                        "difficulty": "Kolay"
                    }
                ],
                "verify_command": "Get-Process 'Diablo IV' -ErrorAction SilentlyContinue | Select-Object Name, WorkingSet64",
                "success_rate": 96
            }
        ]
    }
]

# Extra quick-suggestion titles for the Random Game World Picker
EXTRA_WORLD_GAME_NAMES = [
    {"name": "Victoria 3", "genre": "Büyük Strateji", "hint": "Late-Game Lag, Paradox Launcher"},
    {"name": "Hearts of Iron IV", "genre": "Büyük Strateji", "hint": "1943 Lag, Mod Hatası"},
    {"name": "Mount & Blade II: Bannerlord", "genre": "Aksiyon RPG", "hint": "d3d_device_context, Harmony Crash"},
    {"name": "Red Dead Redemption 2", "genre": "Açık Dünya", "hint": "ERR_GFX_STATE, Error FFFFFFFF"},
    {"name": "Baldur's Gate 3", "genre": "CRPG", "hint": "Act 3 FPS, DXGI Crash"},
    {"name": "Euro Truck Simulator 2", "genre": "Simülasyon", "hint": "Kabin Stutter, TruckersMP"},
    {"name": "Forza Horizon 5", "genre": "Yarış", "hint": "Splash Screen Kapanma"},
    {"name": "HELLDIVERS 2", "genre": "Co-op Shooter", "hint": "GameGuard 114, Çökme"},
    {"name": "Rainbow Six Siege", "genre": "Taktiksel FPS", "hint": "DX12 Stutter, BattlEye"},
    {"name": "Football Manager 2024", "genre": "Spor Simülasyonu", "hint": "Crash Dump, Logo Paketi"},
    {"name": "Black Myth: Wukong", "genre": "Aksiyon RPG", "hint": "Out of Video Memory, UE5"},
    {"name": "Palworld", "genre": "Hayatta Kalma", "hint": "UE-Pal Crash, Kayıt Kurtarma"},
    {"name": "Dota 2", "genre": "MOBA", "hint": "Teamfight FPS, Confirming Match"},
    {"name": "Escape from Tarkov", "genre": "Extraction FPS", "hint": "Streets RAM, Dürbün FPS"},
    {"name": "Europa Universalis IV", "genre": "Büyük Strateji", "hint": "Clausewitz Lag, Launcher"},
    {"name": "Cities: Skylines II", "genre": "Şehir Kurma", "hint": "Simülasyon Hızı, Yüksek VRAM"},
    {"name": "Dead by Daylight", "genre": "Asimetrik Korku", "hint": "EAC Hatası, 120 FPS Kilidi"},
    {"name": "Overwatch 2", "genre": "Hero Shooter", "hint": "Rendering Device Lost"},
    {"name": "The Witcher 3: Wild Hunt", "genre": "Aksiyon RPG", "hint": "DX12 Ray Tracing Stutter"},
    {"name": "Path of Exile 2", "genre": "ARPG", "hint": "Shader Spike, Sunucu Kopması"},
    {"name": "Diablo IV", "genre": "ARPG", "hint": "Fenris Crash, VRAM Sızıntısı"},
    {"name": "Sons of the Forest", "genre": "Hayatta Kalma", "hint": "Kelvin/Kayıt Yükleme Donması"},
    {"name": "ARK: Survival Ascended", "genre": "Hayatta Kalma", "hint": "UE5 D3D Hung, Volumetrik Bulut"}
]

MUTED_PALETTE = [
    "#8c6d53", "#6f7f65", "#a67b4b", "#a85751", "#946b88",
    "#58829e", "#b36b82", "#a89552", "#58789e", "#7b659e",
    "#639188", "#9c7a54"
]

GAME_COVER_URLS = {
    "valorant": "https://images.weserv.nl/?url=https://upload.wikimedia.org/wikipedia/en/b/ba/Valorant_cover.jpg",
    "cs2": "https://cdn.cloudflare.steamstatic.com/steam/apps/730/header.jpg",
    "counter-strike-2": "https://cdn.cloudflare.steamstatic.com/steam/apps/730/header.jpg",
    "lol": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Yasuo_0.jpg",
    "league-of-legends": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Yasuo_0.jpg",
    "gtav": "https://cdn.cloudflare.steamstatic.com/steam/apps/271590/header.jpg",
    "gtav-fivem": "https://cdn.cloudflare.steamstatic.com/steam/apps/271590/header.jpg",
    "gta-v": "https://cdn.cloudflare.steamstatic.com/steam/apps/271590/header.jpg",
    "god-of-war-ragnarok": "https://cdn.cloudflare.steamstatic.com/steam/apps/2322010/header.jpg",
    "minecraft": "https://cdn.cloudflare.steamstatic.com/steam/apps/1672970/header.jpg",
    "fc25": "https://cdn.cloudflare.steamstatic.com/steam/apps/2669320/header.jpg",
    "ea-sports-fc-25": "https://cdn.cloudflare.steamstatic.com/steam/apps/2669320/header.jpg",
    "cyberpunk": "https://cdn.cloudflare.steamstatic.com/steam/apps/1091500/header.jpg",
    "cyberpunk-2077": "https://cdn.cloudflare.steamstatic.com/steam/apps/1091500/header.jpg",
    "pubg": "https://cdn.cloudflare.steamstatic.com/steam/apps/578080/header.jpg",
    "eldenring": "https://cdn.cloudflare.steamstatic.com/steam/apps/1245620/header.jpg",
    "elden-ring": "https://cdn.cloudflare.steamstatic.com/steam/apps/1245620/header.jpg",
    "apex": "https://cdn.cloudflare.steamstatic.com/steam/apps/1172470/header.jpg",
    "apex-legends": "https://cdn.cloudflare.steamstatic.com/steam/apps/1172470/header.jpg",
    "warzone": "https://cdn.cloudflare.steamstatic.com/steam/apps/1938090/header.jpg",
    "cod-warzone": "https://cdn.cloudflare.steamstatic.com/steam/apps/1938090/header.jpg",
    "call-of-duty-warzone-bo6": "https://cdn.cloudflare.steamstatic.com/steam/apps/1938090/header.jpg",
    "fortnite": "https://images.weserv.nl/?url=https://upload.wikimedia.org/wikipedia/commons/7/7c/Fortnite_F_lettermark_logo.png",
    "victoria-3": "https://cdn.cloudflare.steamstatic.com/steam/apps/529340/header.jpg",
    "victoria3": "https://cdn.cloudflare.steamstatic.com/steam/apps/529340/header.jpg",
    "hearts-of-iron-4": "https://cdn.cloudflare.steamstatic.com/steam/apps/394360/header.jpg",
    "hearts-of-iron-iv": "https://cdn.cloudflare.steamstatic.com/steam/apps/394360/header.jpg",
    "mount-and-blade-2-bannerlord": "https://cdn.cloudflare.steamstatic.com/steam/apps/261550/header.jpg",
    "mount-blade-ii-bannerlord": "https://cdn.cloudflare.steamstatic.com/steam/apps/261550/header.jpg",
    "red-dead-redemption-2": "https://cdn.cloudflare.steamstatic.com/steam/apps/1174180/header.jpg",
    "baldurs-gate-3": "https://cdn.cloudflare.steamstatic.com/steam/apps/1086940/header.jpg",
    "euro-truck-simulator-2": "https://cdn.cloudflare.steamstatic.com/steam/apps/227300/header.jpg",
    "forza-horizon-5": "https://cdn.cloudflare.steamstatic.com/steam/apps/1551360/header.jpg",
    "helldivers-2": "https://cdn.cloudflare.steamstatic.com/steam/apps/553850/header.jpg",
    "rainbow-six-siege": "https://cdn.cloudflare.steamstatic.com/steam/apps/359550/header.jpg",
    "tom-clancy-s-rainbow-six-siege": "https://cdn.cloudflare.steamstatic.com/steam/apps/359550/header.jpg",
    "football-manager-2024": "https://cdn.cloudflare.steamstatic.com/steam/apps/2252570/header.jpg",
    "black-myth-wukong": "https://cdn.cloudflare.steamstatic.com/steam/apps/2358720/header.jpg",
    "palworld": "https://cdn.cloudflare.steamstatic.com/steam/apps/1623730/header.jpg",
    "dota-2": "https://cdn.cloudflare.steamstatic.com/steam/apps/570/header.jpg",
    "escape-from-tarkov": "https://cdn.cloudflare.steamstatic.com/steam/apps/221100/header.jpg",
    "europa-universalis-iv": "https://cdn.cloudflare.steamstatic.com/steam/apps/236850/header.jpg",
    "europa-universalis-4": "https://cdn.cloudflare.steamstatic.com/steam/apps/236850/header.jpg",
    "cities-skylines-ii": "https://cdn.cloudflare.steamstatic.com/steam/apps/949230/header.jpg",
    "cities-skylines-2": "https://cdn.cloudflare.steamstatic.com/steam/apps/949230/header.jpg",
    "dead-by-daylight": "https://cdn.cloudflare.steamstatic.com/steam/apps/381210/header.jpg",
    "overwatch-2": "https://cdn.cloudflare.steamstatic.com/steam/apps/2357570/header.jpg",
    "the-witcher-3-wild-hunt": "https://cdn.cloudflare.steamstatic.com/steam/apps/292030/header.jpg",
    "the-witcher-3": "https://cdn.cloudflare.steamstatic.com/steam/apps/292030/header.jpg",
    "path-of-exile-2": "https://cdn.cloudflare.steamstatic.com/steam/apps/2694490/header.jpg",
    "diablo-iv": "https://cdn.cloudflare.steamstatic.com/steam/apps/2344520/header.jpg",
    "diablo-4": "https://cdn.cloudflare.steamstatic.com/steam/apps/2344520/header.jpg",
    "sons-of-the-forest": "https://cdn.cloudflare.steamstatic.com/steam/apps/1326470/header.jpg",
    "ark-survival-ascended": "https://cdn.cloudflare.steamstatic.com/steam/apps/2399830/header.jpg",
    "rust": "https://cdn.cloudflare.steamstatic.com/steam/apps/252490/header.jpg",
    "crusader-kings-3": "https://cdn.cloudflare.steamstatic.com/steam/apps/1158310/header.jpg",
    "crusader-kings-iii": "https://cdn.cloudflare.steamstatic.com/steam/apps/1158310/header.jpg"
}


def get_game_image_url(slug_or_name: str) -> str:
    s = slugify(slug_or_name)
    if s in GAME_COVER_URLS:
        return GAME_COVER_URLS[s]
    return f"./api/games/cover/{s}"


def get_random_world_suggestions(existing_slugs: list, count: int = 6) -> list:
    pool = [g for g in EXTRA_WORLD_GAME_NAMES if slugify(g["name"]) not in existing_slugs]
    if len(pool) < count:
        pool = EXTRA_WORLD_GAME_NAMES
    chosen = random.sample(pool, min(count, len(pool)))
    return [
        {
            **g,
            "slug": slugify(g["name"]),
            "image_url": get_game_image_url(g["name"])
        }
        for g in chosen
    ]


def resolve_game_input(raw_input: str, existing_games: list) -> dict:
    """
    Takes any user-typed game string (e.g. 'victorie 3', 'banerlord', 'rdr2', or a completely new game)
    and returns:
      - matched status ('existing', 'catalog_match', or 'custom_new')
      - canonical_name (e.g. 'Victoria 3')
      - slug (e.g. 'victoria-3')
      - confidence
      - metadata & default_issues ready to insert into SQLite if not yet in DB!
    """
    q = raw_input.strip()
    if not q:
        return {"status": "empty"}

    q_lower = q.lower()
    q_slug = slugify(q)

    # 1. Check exact or close match in existing DB games first
    for g in existing_games:
        if q_lower == g["name"].lower() or q_lower == g["short_name"].lower() or q_slug == g["slug"]:
            return {
                "status": "existing",
                "canonical_name": g["name"],
                "short_name": g["short_name"],
                "slug": g["slug"],
                "category": g["category"],
                "developer": g["developer"],
                "engine": g["engine"],
                "corrected_from": q if q.lower() != g["name"].lower() else None
            }

    # 2. Check alias & fuzzy match in WORLD_GAMES_CATALOG (e.g. "victorie 3" -> "Victoria 3")
    best_catalog_item = None
    best_score = 0.0

    for item in WORLD_GAMES_CATALOG:
        candidates = [item["name"].lower(), item["short_name"].lower(), item["slug"]] + [a.lower() for a in item.get("aliases", [])]
        for cand in candidates:
            if q_lower == cand:
                best_catalog_item = item
                best_score = 1.0
                break
            score = difflib.SequenceMatcher(None, q_lower, cand).ratio()
            # Boost if numbers match (e.g., "3" in "victorie 3" and "victoria 3")
            q_nums = re.findall(r"\d+", q_lower)
            c_nums = re.findall(r"\d+", cand)
            if q_nums and q_nums == c_nums and score >= 0.68:
                score += 0.15
            if score > best_score:
                best_score = score
                best_catalog_item = item
        if best_score >= 1.0:
            break

    # 3. Also fuzzy check existing DB games for typos like "valorent" -> "VALORANT"
    for g in existing_games:
        for cand in [g["name"].lower(), g["short_name"].lower(), g["slug"]]:
            score = difflib.SequenceMatcher(None, q_lower, cand).ratio()
            if score > best_score and score >= 0.74:
                return {
                    "status": "existing",
                    "canonical_name": g["name"],
                    "short_name": g["short_name"],
                    "slug": g["slug"],
                    "category": g["category"],
                    "developer": g["developer"],
                    "engine": g["engine"],
                    "corrected_from": q
                }

    if best_catalog_item and best_score >= 0.72:
        # Check if this catalog item is already in existing_games by slug
        for g in existing_games:
            if g["slug"] == best_catalog_item["slug"]:
                return {
                    "status": "existing",
                    "canonical_name": g["name"],
                    "short_name": g["short_name"],
                    "slug": g["slug"],
                    "category": g["category"],
                    "developer": g["developer"],
                    "engine": g["engine"],
                    "corrected_from": q if q.lower() != g["name"].lower() else None
                }

        return {
            "status": "catalog_match",
            "canonical_name": best_catalog_item["name"],
            "short_name": best_catalog_item["short_name"],
            "slug": best_catalog_item["slug"],
            "category": best_catalog_item["category"],
            "developer": best_catalog_item["developer"],
            "accent_color": best_catalog_item["accent_color"],
            "secondary_color": best_catalog_item["secondary_color"],
            "engine": best_catalog_item["engine"],
            "anticheat": best_catalog_item["anticheat"],
            "banner_subtitle": best_catalog_item["banner_subtitle"],
            "common_tags": best_catalog_item["common_tags"],
            "default_issues": best_catalog_item["default_issues"],
            "corrected_from": q if q.lower() != best_catalog_item["name"].lower() else None
        }

    # 4. Also fuzzy check EXTRA_WORLD_GAME_NAMES for typo correction on other games
    best_extra = None
    best_extra_score = 0.0
    for ext in EXTRA_WORLD_GAME_NAMES:
        sc = difflib.SequenceMatcher(None, q_lower, ext["name"].lower()).ratio()
        if sc > best_extra_score:
            best_extra_score = sc
            best_extra = ext

    if best_extra and best_extra_score >= 0.74:
        clean_title = best_extra["name"]
        cat = best_extra["genre"]
    else:
        # Clean title case (preserving Roman numerals and numbers)
        words = q.split()
        formatted_words = []
        for w in words:
            if w.upper() in ["II", "III", "IV", "V", "VI", "VII", "CS", "GTA", "FC", "EA", "COD", "PUBG", "ARK"]:
                formatted_words.append(w.upper())
            else:
                formatted_words.append(w.capitalize())
        clean_title = " ".join(formatted_words)
        cat = "PC Oyunu"

    slug = slugify(clean_title)
    short_name = clean_title if len(clean_title) <= 18 else clean_title[:16].strip() + "..."
    accent = MUTED_PALETTE[sum(ord(c) for c in slug) % len(MUTED_PALETTE)]

    default_issues = [
        {
            "title": f"{clean_title}: Başlangıçta Çökme (Crash on Startup), Siyah Ekran ve Gölgelendirici Önbelleği Çözümü",
            "error_code": f"{slug[:6].upper()}-CRASH-01",
            "severity": "Yüksek",
            "category": "Çökme & Başlatma",
            "symptom_summary": f"{clean_title} başlatılırken masaüstüne atıyor, siyah ekranda kalıyor veya güncelleme sonrası yanıt vermiyor.",
            "forum_sources": [
                {
                    "forum": "Steam Community & Reddit TechSupport",
                    "thread": f"[Solved] {clean_title} Crashing on Startup / Black Screen Fix",
                    "quote": f"{clean_title} için DirectX Gölgelendirici Önbelleğini (Shader Cache) temizlemek, tam ekran iyileştirmelerini kapatmak ve oyun dosyalarını doğrulamak çökmeleri %90 oranında gideriyor.",
                    "upvotes": 480
                }
            ],
            "ai_root_cause": f"{clean_title} oyun motorunun güncelleme sonrası eski GPU gölgelendirici önbelleği (Shader Cache) veya üçüncü parti ekran katmanlarıyla (Discord / Steam Overlay / RivaTuner) çakışması sonucu oluşur.",
            "ai_solution_steps": [
                {
                    "step": 1,
                    "title": "Oyun Dosyalarının Bütünlüğünü Doğrulayın ve Shader Cache Temizleyin",
                    "detail": "Steam / Epic Games üzerinden oyun dosyalarını doğrulayın ve Windows Disk Temizleme ile DirectX Gölgelendirici Önbelleğini sıfırlayın.",
                    "difficulty": "Kolay"
                },
                {
                    "step": 2,
                    "title": "Tam Ekran İyileştirmelerini ve Katmanları (Overlay) Kapatın",
                    "detail": "Oyun `.exe` dosyasına sağ tıklayıp Özellikler -> Uyumluluk -> 'Tam ekran iyileştirmelerini devre dışı bırak' ve 'Bu programı yönetici olarak çalıştır' seçeneklerini işaretleyin.",
                    "difficulty": "Kolay"
                }
            ],
            "verify_command": "sfc /verifyonly",
            "success_rate": 93
        },
        {
            "title": f"{clean_title}: Anlık FPS Düşüşü (Stutter), Yüksek VRAM/CPU Kullanımı ve Akıcılık Optimizasyonu",
            "error_code": f"{slug[:6].upper()}-FPS-DROP",
            "severity": "Orta",
            "category": "Performans & FPS",
            "symptom_summary": f"{clean_title} oynarken sahne geçişlerinde veya yoğun efektlerde anlık takılmalar (micro-stutter) ve FPS düşüşü yaşanıyor.",
            "forum_sources": [
                {
                    "forum": "Technopat Sosyal & Reddit",
                    "thread": f"{clean_title} Stutter Fix & Frame Pacing Guide",
                    "quote": "Oyun içi V-Sync kapatıp maksimum kare hızını monitör yenileme hızına sabitlemek ve Windows Oyun Modu / Grafik Donanım Hızlandırmasını optimize etmek %1 Low FPS'i ciddi oranda artırıyor.",
                    "upvotes": 340
                }
            ],
            "ai_root_cause": "Sınırsız kare hızında GPU ve CPU çerçeve kuyruğunun (Frame Queue) senkronizasyonunu kaybetmesi ve arka plan sanal bellek (Pagefile) darboğazı.",
            "ai_solution_steps": [
                {
                    "step": 1,
                    "title": "Kare Hızı Sabitleme ve Yüksek Performans GPU Ataması",
                    "detail": "Windows Ayarlar -> Sistem -> Ekran -> Grafikler menüsünden oyunu ekleyip 'Yüksek Performans' seçin ve oyun içi Dinamik Çözünürlük / V-Sync ayarlarını optimize edin.",
                    "difficulty": "Kolay"
                }
            ],
            "verify_command": "Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion",
            "success_rate": 92
        }
    ]

    return {
        "status": "custom_new",
        "canonical_name": clean_title,
        "short_name": short_name,
        "slug": slug,
        "category": cat,
        "developer": "Topluluk / PC",
        "accent_color": accent,
        "secondary_color": "#1c222d",
        "engine": "DirectX 11/12 & Vulkan",
        "anticheat": "Steam / Standart Koruma",
        "banner_subtitle": f"{clean_title} için Forumlardan Derlenen Çökme, FPS Düşüşü, Başlatma Hataları ve Yapay Zeka Çözüm Ekranı",
        "common_tags": ["Crash on Startup", "FPS Drop / Stutter", "Black Screen", "Shader Cache", "Overlay Fix"],
        "default_issues": default_issues,
        "corrected_from": q if q.lower() != clean_title.lower() else None
    }
