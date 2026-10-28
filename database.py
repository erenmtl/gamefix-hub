import sqlite3
import json
import os
import hashlib
import secrets

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gamefix.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str, salt: str = None) -> str:
    if not salt:
        salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
    return f"{salt}${pwd_hash}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, pwd_hash = stored_hash.split("$", 1)
        check = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
        return secrets.compare_digest(pwd_hash, check)
    except Exception:
        return False


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        avatar_initials TEXT NOT NULL,
        system_specs TEXT DEFAULT '',
        favorite_game TEXT DEFAULT 'valorant',
        role TEXT DEFAULT 'member',
        created_at TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        token TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        voter_key TEXT NOT NULL,
        target_type TEXT NOT NULL,
        target_id INTEGER NOT NULL,
        hardware_tag TEXT DEFAULT '',
        created_at TEXT NOT NULL,
        UNIQUE(voter_key, target_type, target_id)
    )
    """)

    try:
        cursor.execute("ALTER TABLE user_votes ADD COLUMN hardware_tag TEXT DEFAULT ''")
    except Exception:
        pass

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS legal_5651_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action_type TEXT NOT NULL,
        target_id INTEGER DEFAULT 0,
        user_id INTEGER DEFAULT 0,
        client_id TEXT DEFAULT '',
        ip_address TEXT NOT NULL,
        user_agent TEXT NOT NULL,
        content_summary TEXT DEFAULT '',
        utc_timestamp TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS content_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target_type TEXT NOT NULL,
        target_id INTEGER NOT NULL,
        reason TEXT NOT NULL,
        details TEXT DEFAULT '',
        reporter_key TEXT NOT NULL,
        ip_address TEXT NOT NULL,
        user_agent TEXT NOT NULL,
        status TEXT DEFAULT 'İnceleniyor',
        created_at TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS guest_ai_trials (
        trial_key TEXT PRIMARY KEY,
        ip_address TEXT NOT NULL,
        client_id TEXT NOT NULL,
        used_count INTEGER DEFAULT 1,
        utc_timestamp TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS site_settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS email_verifications (
        email TEXT PRIMARY KEY,
        username TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        system_specs TEXT DEFAULT '',
        favorite_game TEXT DEFAULT 'valorant',
        code TEXT NOT NULL,
        expires_at REAL NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_cache (
        cache_key TEXT PRIMARY KEY,
        game_slug TEXT NOT NULL,
        error_code TEXT DEFAULT '',
        query_summary TEXT NOT NULL,
        markdown TEXT NOT NULL,
        confidence INTEGER DEFAULT 97,
        hit_count INTEGER DEFAULT 1,
        created_at TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        short_name TEXT NOT NULL,
        category TEXT NOT NULL,
        developer TEXT NOT NULL,
        accent_color TEXT NOT NULL,
        secondary_color TEXT NOT NULL,
        banner_subtitle TEXT NOT NULL,
        engine TEXT NOT NULL,
        anticheat TEXT NOT NULL,
        common_tags TEXT NOT NULL,
        issue_count INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS issues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_slug TEXT NOT NULL,
        title TEXT NOT NULL,
        error_code TEXT NOT NULL,
        severity TEXT NOT NULL,
        category TEXT NOT NULL,
        symptom_summary TEXT NOT NULL,
        forum_sources TEXT NOT NULL,
        ai_root_cause TEXT NOT NULL,
        ai_solution_steps TEXT NOT NULL,
        verify_command TEXT,
        success_rate INTEGER DEFAULT 94,
        views INTEGER DEFAULT 1200,
        helpful_votes INTEGER DEFAULT 180,
        created_at TEXT NOT NULL,
        FOREIGN KEY (game_slug) REFERENCES games (slug)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS threads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_slug TEXT NOT NULL,
        author_name TEXT NOT NULL,
        author_avatar TEXT NOT NULL,
        title TEXT NOT NULL,
        error_code TEXT,
        system_specs TEXT,
        content TEXT NOT NULL,
        status TEXT DEFAULT 'AI Çözümledi',
        upvotes INTEGER DEFAULT 12,
        views INTEGER DEFAULT 145,
        created_at TEXT NOT NULL,
        FOREIGN KEY (game_slug) REFERENCES games (slug)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS replies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        thread_id INTEGER NOT NULL,
        author_name TEXT NOT NULL,
        is_ai INTEGER DEFAULT 0,
        ai_mode TEXT,
        content TEXT NOT NULL,
        helpful_count INTEGER DEFAULT 5,
        created_at TEXT NOT NULL,
        FOREIGN KEY (thread_id) REFERENCES threads (id) ON DELETE CASCADE
    )
    """)

    # Load Gemini API key from local .env if present
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as ef:
            for line in ef:
                if line.strip().startswith("GEMINI_API_KEY="):
                    val = line.strip().split("=", 1)[1].strip()
                    if val:
                        cursor.execute("INSERT OR IGNORE INTO site_settings (key, value) VALUES ('gemini_api_key', ?)", (val,))

    cursor.execute("SELECT COUNT(*) as cnt FROM games")
    if cursor.fetchone()["cnt"] == 0:
        seed_initial_data(cursor)

    conn.commit()
    conn.close()


def seed_initial_data(cursor):
    # Seed default demo admin & member user accounts
    cursor.execute("""
        INSERT OR IGNORE INTO users (username, email, password_hash, avatar_initials, system_specs, favorite_game, role, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "Admin",
        "admin@oyuncoz.com",
        hash_password("admin123"),
        "AD",
        "Windows 11 Pro | Ryzen 7 7800X3D | RTX 4070 Super | 32GB DDR5",
        "valorant",
        "admin",
        "2026-10-17"
    ))

    # Muted, desaturated, eye-friendly pastel slate accent colors
    games_data = [
        {
            "slug": "valorant",
            "name": "VALORANT",
            "short_name": "Valorant",
            "category": "Taktiksel FPS",
            "developer": "Riot Games",
            "accent_color": "#b85d66",
            "secondary_color": "#181e29",
            "banner_subtitle": "Riot Vanguard (VAN 9003 / 1067), TPM 2.0, Paket Kaybı ve FPS Düşüşü Çözüm Merkezi",
            "engine": "Unreal Engine 4",
            "anticheat": "Riot Vanguard (Kernel-Level)",
            "common_tags": json.dumps(["VAN 9003", "VAN 1067", "TPM 2.0", "Secure Boot", "Packet Loss", "VAL 62", "Micro-Stutter"]),
            "issue_count": 4
        },
        {
            "slug": "cs2",
            "name": "Counter-Strike 2",
            "short_name": "CS2",
            "category": "Rekabetçi FPS",
            "developer": "Valve",
            "accent_color": "#b88b52",
            "secondary_color": "#1c222e",
            "banner_subtitle": "Source 2 Frame Time Stutter, VAC Oturumu Doğrulayamadı, Sub-tick Paket Kaybı ve Ses Sorunları",
            "engine": "Source 2",
            "anticheat": "VAC (Valve Anti-Cheat)",
            "common_tags": json.dumps(["VAC Verify", "Shader Stutter", "1% Low FPS", "Mikrofon Algılamama", "Sub-tick Jitter", "pak01.vpk"]),
            "issue_count": 4
        },
        {
            "slug": "lol",
            "name": "League of Legends",
            "short_name": "LoL",
            "category": "MOBA",
            "developer": "Riot Games",
            "accent_color": "#5586ad",
            "secondary_color": "#16202e",
            "banner_subtitle": "Riot İstemcisi Siyah Ekran, Şampiyon Seçimi Sonrası Bağlantı Kopması, VAN 185 ve DirectX Çökmeleri",
            "engine": "Riot Proprietary Engine",
            "anticheat": "Riot Vanguard",
            "common_tags": json.dumps(["Client Siyah Ekran", "Reconnect Loop", "VAN 185", "DirectX 9/11", "FPS Sabitlenme", "Vanguard Hatası"]),
            "issue_count": 3
        },
        {
            "slug": "gtav-fivem",
            "name": "GTA V & FiveM",
            "short_name": "GTA V / FiveM",
            "category": "Açık Dünya / Roleplay",
            "developer": "Rockstar Games / Cfx.re",
            "accent_color": "#589471",
            "secondary_color": "#17241e",
            "banner_subtitle": "FiveM Early Exit Trap, Harita / Doku Yüklenmeme (Texture Loss), Social Club ve ERR_GFX_D3D_INIT Çözümleri",
            "engine": "RAGE Engine",
            "anticheat": "Cfx.re Adhesive / BattlEye",
            "common_tags": json.dumps(["ERR_GFX_D3D_INIT", "Texture Loss", "Early Exit Trap", "Social Club Code 134", "CitizenFX Crash"]),
            "issue_count": 3
        },
        {
            "slug": "fc25",
            "name": "EA Sports FC 25",
            "short_name": "EA FC 25",
            "category": "Spor / Futbol",
            "developer": "EA Sports",
            "accent_color": "#5e9c88",
            "secondary_color": "#172524",
            "banner_subtitle": "EA AntiCheat Başlatılamadı (Hata 115), Korner/Ara Sahne FPS Çöküşü ve Kolda Çift Tuş Basma Çözümleri",
            "engine": "Frostbite Engine",
            "anticheat": "EA AntiCheat (Kernel)",
            "common_tags": json.dumps(["EA AntiCheat Error", "Cutscene FPS Drop", "Double Controller Input", "DirectX Function Hung"]),
            "issue_count": 2
        },
        {
            "slug": "minecraft",
            "name": "Minecraft (Java & Bedrock)",
            "short_name": "Minecraft",
            "category": "Sandbox / Hayatta Kalma",
            "developer": "Mojang Studios",
            "accent_color": "#6c9a5c",
            "secondary_color": "#1a2419",
            "banner_subtitle": "Exit Code: 1, GLFW Error 65542 (WGL OpenGL), Chunk Yüklenirken Lag Spike ve Connection Timed Out Çözümleri",
            "engine": "LWJGL 3 / RenderDragon",
            "anticheat": "Server-Side / Vanilla",
            "common_tags": json.dumps(["Exit Code 1", "GLFW 65542", "Java 21/17", "Chunk Stutter", "getsockopt / Netty Error"]),
            "issue_count": 2
        },
        {
            "slug": "cod-warzone",
            "name": "Call of Duty: Warzone & BO6",
            "short_name": "CoD Warzone",
            "category": "Battle Royale / FPS",
            "developer": "Activision / Treyarch",
            "accent_color": "#a87954",
            "secondary_color": "#221c17",
            "banner_subtitle": "DirectX Unrecoverable Error (0x887A0005), Packet Burst (Paket Patlaması) ve Fetching Online Profile Döngüsü",
            "engine": "IW 9.0 Engine",
            "anticheat": "RICOCHET Anti-Cheat",
            "common_tags": json.dumps(["DirectX 0x887A0005", "Packet Burst", "RendererWorkerCount", "VRAM Scale Target", "Dev Error"]),
            "issue_count": 2
        },
        {
            "slug": "rust",
            "name": "Rust",
            "short_name": "Rust",
            "category": "Hayatta Kalma",
            "developer": "Facepunch Studios",
            "accent_color": "#b06655",
            "secondary_color": "#241917",
            "banner_subtitle": "EAC Authentication Timed Out (1/2), Asset Warmup Çökmesi (Sanal Bellek) ve GC Buffer Stutter Çözümü",
            "engine": "Unity Engine",
            "anticheat": "Easy Anti-Cheat (EAC)",
            "common_tags": json.dumps(["EAC Timed Out", "Asset Warmup Crash", "gc.buffer 2048", "Pagefile RAM Crash"]),
            "issue_count": 2
        },
        {
            "slug": "apex-legends",
            "name": "Apex Legends",
            "short_name": "Apex Legends",
            "category": "Battle Royale / Hero Shooter",
            "developer": "Respawn Entertainment",
            "accent_color": "#ab5c65",
            "secondary_color": "#23181b",
            "banner_subtitle": "0x887A0006 DXGI_ERROR_DEVICE_HUNG, %100 CPU Kullanımı ve code:net / code:leaf Bağlantı Kopması",
            "engine": "Source (Modified)",
            "anticheat": "Easy Anti-Cheat (EAC)",
            "common_tags": json.dumps(["DXGI_ERROR_DEVICE_HUNG", "code:net / code:leaf", "100% CPU Fix", "DirectX 12 Beta"]),
            "issue_count": 2
        },
        {
            "slug": "cyberpunk-2077",
            "name": "Cyberpunk 2077",
            "short_name": "Cyberpunk",
            "category": "Aksiyon RPG",
            "developer": "CD Projekt Red",
            "accent_color": "#afa055",
            "secondary_color": "#211f15",
            "banner_subtitle": "Whoa! Cyberpunk 2077 Has Flatlined, Path Tracing VRAM Taşması, Mod Çakışması ve Ses Cızırtısı",
            "engine": "REDengine 4",
            "anticheat": "Singleplayer (DRM-Free)",
            "common_tags": json.dumps(["Flatlined Crash", "REDmod / CET", "DLSS Frame Gen", "Audio Crackling", "GPU Driver Timeout"]),
            "issue_count": 2
        },
        {
            "slug": "elden-ring",
            "name": "Elden Ring",
            "short_name": "Elden Ring",
            "category": "Soulsborne RPG",
            "developer": "FromSoftware",
            "accent_color": "#a68253",
            "secondary_color": "#211d18",
            "banner_subtitle": "Inappropriate Activity Detected (EAC), Boss Savaşlarında Anlık Donma (Stutter) ve Beyaz Ekran Çökmesi",
            "engine": "FromSoftware Engine (DX12)",
            "anticheat": "Easy Anti-Cheat (EAC)",
            "common_tags": json.dumps(["EAC Inappropriate Activity", "DX12 Stutter", "USB Device Freeze", "White Screen Crash"]),
            "issue_count": 2
        },
        {
            "slug": "pubg",
            "name": "PUBG: Battlegrounds",
            "short_name": "PUBG",
            "category": "Battle Royale",
            "developer": "KRAFTON",
            "accent_color": "#b37a52",
            "secondary_color": "#241b15",
            "banner_subtitle": "BattlEye Corrupted Data, Maç Sonrası Lobi Yüklenmeme (Smoke Screen) ve %100 CPU Darboğazı",
            "engine": "Unreal Engine 4",
            "anticheat": "BattlEye / Zakynthos",
            "common_tags": json.dumps(["Corrupted Data", "Lobby Black Screen", "100% CPU Spike", "DX11 Enhanced"]),
            "issue_count": 2
        }
    ]

    for g in games_data:
        cursor.execute("""
            INSERT INTO games (slug, name, short_name, category, developer, accent_color, secondary_color, banner_subtitle, engine, anticheat, common_tags, issue_count)
            VALUES (:slug, :name, :short_name, :category, :developer, :accent_color, :secondary_color, :banner_subtitle, :engine, :anticheat, :common_tags, :issue_count)
        """, g)

    issues_data = [
        # VALORANT ISSUES
        {
            "game_slug": "valorant",
            "title": "VAN 9003 & VAN 1067: Windows 11 TPM 2.0 ve Secure Boot Uyumluluk Hatası",
            "error_code": "VAN 9003 / VAN 1067",
            "severity": "Kritik",
            "category": "Anti-Cheat & Güvenlik",
            "symptom_summary": "Oyun açıldıktan 1-2 dakika sonra 'This build of Vanguard is out of compliance with current system settings (VAN 9003)' veya 'VAN 1067' uyarısı vererek istemciyi kapatıyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "Reddit r/ValorantTechSupport",
                    "thread": "[SOLVED] VAN 9003 on Windows 11 even when Secure Boot says Enabled in BIOS",
                    "quote": "BIOS'ta Secure Boot 'Enabled' görünse bile 'Not Active' olabiliyor. CSM kapatıp Secure Boot Mode'u Custom -> Standard yapınca Factory Keys yüklendi ve sorun anında çözüldü.",
                    "upvotes": 1420
                },
                {
                    "forum": "Technopat Sosyal",
                    "thread": "Çözüldü: Valorant VAN 9003 ve VAN 1067 Hatası (ASUS / MSI / Gigabyte Anakartlar)",
                    "quote": "Gigabyte anakartlarda CSM Support kapattıktan sonra Secure Boot altından 'Restore Factory Keys' yapmadan Windows msinfo32 içinde Güvenli Önyükleme Açık olarak görünmüyor.",
                    "upvotes": 685
                }
            ]),
            "ai_root_cause": "Riot Vanguard çekirdek sürücüsü (vgk.sys), Windows 11'de önyükleme zincirinin bütünlüğünü doğrulamak için donanımsal TPM 2.0 ve aktif UEFI Secure Boot (Güvenli Önyükleme) şartı koşar. Forum verilerine göre kullanıcıların %78'inde BIOS'ta Secure Boot 'Enabled' görünmesine rağmen Platform Key (PK) yüklenmediği için durum 'Not Active' kalmaktadır veya `vgc` servisi Windows Hizmetleri'nde durmaktadır.",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "Sistem Durumunu msinfo32 ile Doğrulayın",
                    "detail": "Win + R tuşlarına basıp `msinfo32` yazın. 'BIOS Modu: UEFI' ve 'Güvenli Önyükleme Durumu: Açık' olmalıdır. Eğer 'Kapalı' veya 'Desteklenmiyor' yazıyorsa 2. adıma geçin.",
                    "difficulty": "Kolay"
                },
                {
                    "step": 2,
                    "title": "BIOS Üzerinden CSM Kapatma ve Secure Boot Key Yükleme",
                    "detail": "Bilgisayarı yeniden başlatıp BIOS'a (DEL/F2) girin. Boot sekmesinden CSM (Compatibility Support Module) ayarını 'Disabled' yapın. Ardından Secure Boot menüsüne girip 'Secure Boot Mode' ayarını 'Custom' yapıp 'Restore Factory Keys / Install Default Secure Boot Keys' seçeneğine tıklayın ve tekrar 'Standard' moduna alıp F10 ile kaydedin.",
                    "difficulty": "Orta"
                },
                {
                    "step": 3,
                    "title": "TPM 2.0 (fTPM / PTT) ve VGC Servisini Aktifleştirin",
                    "detail": "AMD işlemcilerde 'AMD CPU fTPM', Intel işlemcilerde 'Intel PTT' ayarını Enabled yapın. Windows açıldığında `services.msc` içerisinden 'vgc' servisinin Başlangıç Türünü 'Otomatik' olarak ayarlayın.",
                    "difficulty": "Kolay"
                }
            ]),
            "verify_command": "Confirm-SecureBootUEFI; Get-Tpm | Select-Object TpmPresent, TpmReady",
            "success_rate": 97,
            "views": 18450,
            "helpful_votes": 1620,
            "created_at": "2026-10-15"
        },
        {
            "game_slug": "valorant",
            "title": "Yüksek FPS'e Rağmen Anlık Takılma (Micro-Stutter) ve Fare Gecikmesi",
            "error_code": "PERF-STUTTER",
            "severity": "Yüksek",
            "category": "Performans & FPS",
            "symptom_summary": "FPS 300+ olmasına rağmen çatışma anında (yetenek kullanıldığında veya peek atarken) ekran 0.2 saniyeliğine donuyor ve fare takılıyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "Reddit r/ValorantCompetitive",
                    "thread": "PSA: 8000Hz / 4000Hz Mouse Polling Rate + HAGS + Discord Overlay causes massive micro-stutter",
                    "quote": "Mouse raporlama hızını (Polling Rate) 4000Hz'den 1000Hz'e çekip Valorant içinden 'Saf Girdi Süresi (Raw Input Buffer)' açtığımda tüm takılmalar bitti.",
                    "upvotes": 940
                },
                {
                    "forum": "DonanımHaber Forum",
                    "thread": "Valorant AMD/NVIDIA Shader Cache ve MPO Kaynaklı Drop Çözümü",
                    "quote": "Windows 11 24H2/25H2 güncellemesi sonrası Tam Ekran İyileştirmelerini devre dışı bırakmak ve GPU Shader Cache temizlemek %1 Low FPS'i ikiye katladı.",
                    "upvotes": 412
                }
            ]),
            "ai_root_cause": "Unreal Engine 4 tabanlı Valorant'ta anlık takılmaların 3 ana nedeni vardır: (1) 2000Hz+ yüksek polling rate'e sahip farelerde 'Saf Girdi Süresi (Raw Input Buffer)' kapalı olduğunda Windows mesaj kuyruğunun CPU'yu tıkaması, (2) Bozulmuş DirectX / GPU Gölgelendirici Önbelleği (Shader Cache), (3) Windows HAGS (Donanım Hızlandırmalı GPU Zamanlaması) ve Discord Donanım İvmesi çakışması.",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "Oyun İçi 'Saf Girdi Süresi (Raw Input Buffer)' Ayarını Açın",
                    "detail": "Valorant -> Ayarlar -> Genel -> Fare altındaki 'Saf Girdi Süresi' seçeneğini 'Açık' yapın. 4000Hz/8000Hz fare kullanıyorsanız bu ayar zorunludur; devam ederse fare yazılımından 1000Hz veya 2000Hz'e düşürün.",
                    "difficulty": "Kolay"
                },
                {
                    "step": 2,
                    "title": "DirectX ve GPU Gölgelendirici Önbelleğini (Shader Cache) Sıfırlayın",
                    "detail": "Windows Disk Temizleme (cleanmgr) aracını çalıştırıp 'DirectX Gölgelendirici Önbelleği'ni temizleyin. NVIDIA Denetim Masası -> 3D Ayarları -> 'Gölgelendirici Önbellek Boyutu'nu '10 GB' olarak sabitleyin.",
                    "difficulty": "Kolay"
                },
                {
                    "step": 3,
                    "title": "Tam Ekran İyileştirmeleri ve Core Isolation (Bellek Bütünlüğü) Ayarı",
                    "detail": "`VALORANT-Win64-Shipping.exe` dosyasına sağ tıklayıp Özellikler -> Uyumluluk -> 'Tam ekran iyileştirmelerini devre dışı bırak' kutucuğunu işaretleyin.",
                    "difficulty": "Orta"
                }
            ]),
            "verify_command": "Get-Process VALORANT-Win64-Shipping -ErrorAction SilentlyContinue | Select-Object Name, PriorityClass, WorkingSet64",
            "success_rate": 93,
            "views": 12900,
            "helpful_votes": 980,
            "created_at": "2026-10-14"
        },
        {
            "game_slug": "valorant",
            "title": "Ping Düşük Olmasına Rağmen %10-%30 Paket Kaybı (Packet Loss) ve Işınlanma",
            "error_code": "NET-PKTLOSS / VAL 62",
            "severity": "Yüksek",
            "category": "Ağ & Bağlantı",
            "symptom_summary": "İstanbul sunucusunda ping 12-18ms görünmesine rağmen sağ üstte 'Ağ Sorunu' ikonu çıkıyor, mermiler gitmiyor ve karakter geriye ışınlanıyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "Reddit r/ValorantTechSupport",
                    "thread": "Fixed 0 ping Packet Loss spikes by setting Valorant Network Buffering & disabling IPv6",
                    "quote": "Ağ bağdaştırıcısından IPv6'yı kapatıp DNS olarak Cloudflare (1.1.1.1) verdiğimde ve oyun içi Ağ Arabelleğini 'Orta' yaptığımda giden paket kaybı %0'a indi.",
                    "upvotes": 530
                }
            ]),
            "ai_root_cause": "Riot Direct yönlendirmelerinde UDP paketlerinin (özellikle Wi-Fi dolaşım agresifliği, modem QoS/Bufferbloat şişmesi veya hatalı MTU boyutu nedeniyle) parçalanması sonucu oluşur. Ayrıca Realtek/Intel Killer ağ kartlarındaki 'Önceliklendirme Motoru' UDP paketlerini yanlış kuyruğa sokabilmektedir.",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "Oyun İçi Ağ Arabelleğini (Network Buffering) Ayarlayın",
                    "detail": "Valorant Ayarlar -> Genel -> Ağ Arabelleği seçeneğini 'Asgari' yerine 'Orta' yapın. Bu ayar mikro paket gecikmelerini telafi eder.",
                    "difficulty": "Kolay"
                },
                {
                    "step": 2,
                    "title": "TCP/IP Yığınını Sıfırlayın ve IPv6'yı Devre Dışı Bırakın",
                    "detail": "Yönetici CMD/PowerShell açarak `netsh int ip reset` ve `netsh winsock reset` komutlarını çalıştırın. Ağ Bağdaştırıcısı Özellikleri'nden 'İnternet Protokolü Sürüm 6 (TCP/IPv6)' işaretini kaldırın.",
                    "difficulty": "Orta"
                }
            ]),
            "verify_command": "Test-NetConnection -ComputerName 162.249.79.1 -InformationLevel Detailed",
            "success_rate": 91,
            "views": 9400,
            "helpful_votes": 610,
            "created_at": "2026-10-12"
        },
        {
            "game_slug": "valorant",
            "title": "VAL 5 / VAL 43: İstemci Başlatılamadı veya Oturum Başka Yerde Açık Hatası",
            "error_code": "VAL 5 / VAL 43",
            "severity": "Orta",
            "category": "Çökme & Başlatma",
            "symptom_summary": "Oyuna girerken yükleme ekranında takılı kalıp VAL 43 veriyor ya da maç ortasında VAL 5 ile oyundan atıyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "Technopat Sosyal",
                    "thread": "Valorant VAL 43 ve VAL 5 Kesin Çözüm",
                    "quote": "RiotLocalMachine.ini ve %localappdata%\\VALORANT\\Saved\\Config klasörünü silip vgc servisini yeniden başlatınca hemen girdi.",
                    "upvotes": 320
                }
            ]),
            "ai_root_cause": "Riot İstemcisi kimlik doğrulama jetonunun (Auth Token) bozulması veya arka planda asılı kalan `RiotClientServices.exe` sürecinin yeni oturum el sıkışmasını engellemesinden kaynaklanır.",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "Asılı Kalan Riot Süreçlerini ve Önbelleği Temizleyin",
                    "detail": "Görev Yöneticisi'nden tüm Riot ve Valorant süreçlerini kapatın. `Win + R` tuşlarına basıp `%localappdata%\\Riot Games\\Riot Client\\Data` klasörünün içini temizleyin ve istemciyi Yönetici olarak başlatın.",
                    "difficulty": "Kolay"
                }
            ]),
            "verify_command": "Stop-Process -Name 'RiotClientServices','VALORANT-Win64-Shipping' -Force -ErrorAction SilentlyContinue",
            "success_rate": 95,
            "views": 7800,
            "helpful_votes": 490,
            "created_at": "2026-10-10"
        },

        # COUNTER-STRIKE 2 ISSUES
        {
            "game_slug": "cs2",
            "title": "VAC Oyun Oturumunuzu Doğrulayamadı (VAC Was Unable to Verify Your Game Session)",
            "error_code": "VAC-VERIFY-ERR",
            "severity": "Kritik",
            "category": "Anti-Cheat & Güvenlik",
            "symptom_summary": "Seçkin (Premier) veya Rekabetçi maça girerken 'VAC oyun oturumunuzu doğrulayamadı' hatası verip eşleştirmeyi iptal ediyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "Reddit r/GlobalOffensive",
                    "thread": "100% Working Fix for 'VAC was unable to verify your game session' in CS2",
                    "quote": "Dosya doğrulamak tek başına yetmiyor! Steam'i Yönetici olarak çalıştırıp Steam Service onarımı (`steamservice.exe /repair`) yapmak ve profil fotoğrafı/ismini bir kez değiştirmek anında çözüyor.",
                    "upvotes": 2150
                },
                {
                    "forum": "Steam Community Guides",
                    "thread": "CS2 VAC Verify Fix Without Reinstalling Windows",
                    "quote": "DEP (Veri Yürütme Engellemesi) kapalıysa veya üçüncü parti başlatıcılar (CCleaner, Razer Synapse makro servisi) USN Journal'ı kilitliyorsa VAC imza doğrulaması başarısız oluyor.",
                    "upvotes": 890
                }
            ]),
            "ai_root_cause": "CS2'de VAC modülü, `steamservice.exe` üzerinden oyun belleği imzasını ve NTFS USN Journal kayıtlarını denetler. Steam servisi yetki kaybederse, oyun kısayoldan (Steam dışı) başlatılırsa veya bozuk `.vpk` önbelleği oluşursa doğrulama reddedilir.",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "Steam Service Onarımı ve Yönetici Modu",
                    "detail": "Steam'i tamamen kapatın. Yönetici CMD açıp `\"C:\\Program Files (x86)\\Common Files\\Steam\\SteamService.exe\" /repair` komutunu çalıştırın.",
                    "difficulty": "Kolay"
                },
                {
                    "step": 2,
                    "title": "Oyun Dosyalarını Doğrulayın ve İndirme Önbelleğini Temizleyin",
                    "detail": "Steam -> Ayarlar -> İndirmeler -> 'İndirme Önbelleğini Temizle' butonuna tıklayın. Ardından CS2 Özellikler -> Yüklü Dosyalar -> 'Oyun dosyalarının bütünlüğünü doğrula' işlemini başlatın.",
                    "difficulty": "Kolay"
                },
                {
                    "step": 3,
                    "title": "BCDEDIT / DEP Kontrolü",
                    "detail": "Yönetici CMD'de `bcdedit /deletevalue nointegritychecks` ve `bcdedit /deletevalue loadoptions` komutlarını çalıştırıp bilgisayarı yeniden başlatın.",
                    "difficulty": "Orta"
                }
            ]),
            "verify_command": "Get-Service -Name 'Steam Client Service' | Select-Object Name, Status, StartType",
            "success_rate": 96,
            "views": 24100,
            "helpful_votes": 2100,
            "created_at": "2026-10-16"
        },
        {
            "game_slug": "cs2",
            "title": "Source 2 Frame-Time Spikes, Yüksek %1 Low FPS Düşüşü ve Su/Sis Takılması",
            "error_code": "CS2-FRAMETIME",
            "severity": "Yüksek",
            "category": "Performans & FPS",
            "symptom_summary": "Ortalama FPS 250 iken çatışmada veya el bombası patladığında ms (frame time) 4ms'den 35ms'ye fırlıyor ve oyun 60Hz gibi hissettiriyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "Reddit r/GlobalOffensive",
                    "thread": "CS2 Frame Pacing & 1% Low FPS Guide (Stop using outdated CS:GO launch options!)",
                    "quote": "Eski CS:GO başlatma seçeneklerini (`-high -threads`) silin! CS2'de `-high` veya yanlış thread komutu E-Core / P-Core zamanlamasını bozuyor. NVIDIA Reflex 'Etkin' (Takviye değil) olmalı.",
                    "upvotes": 1780
                }
            ]),
            "ai_root_cause": "Source 2 motoru çoklu iş parçacığı zamanlamasını kendi yönetir. Eski CS:GO başlatma kodları (`-threads`, `-high`, `-processheap`) Source 2'nin iş parçacığı havuzunu bozar. Ayrıca DirectX 11 gölgelendirici önbelleği (`directx_installer` / `shaders`) şiştiğinde her yeni efektte anlık derleme (shader compilation stutter) yaşanır.",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "Eski CS:GO Başlatma Seçeneklerini Temizleyin",
                    "detail": "Steam -> CS2 Başlatma Seçenekleri'ndeki `-threads`, `-high`, `-novid`, `-forcepreload` gibi tüm eski kodları silin. Sadece `-noreflex` (gerekirse) veya tamamen boş bırakın.",
                    "difficulty": "Kolay"
                },
                {
                    "step": 2,
                    "title": "CS2 DirectX Shader Cache Temizliği ve Optimum Görüntü Ayarları",
                    "detail": "Oyun içi Gelişmiş Görüntü ayarlarında: 'Düşük Gecikme Oranı (NVIDIA Reflex): Etkin', 'Parçacık Detayı: Düşük', 'Keskinliği Yumuşatma: 2x MSAA veya CMAA2' ve 'Dinamik Gölgeler: Tümü' olarak ayarlayın.",
                    "difficulty": "Kolay"
                },
                {
                    "step": 3,
                    "title": "Paket Kaybı / Jitter Kaynaklı Stutter İçin Ağ Arabelleği",
                    "detail": "Son güncellemelerle gelen 'Paket Kaybını / Jitter'ı Düzgünleştir (Buffering to smooth over packet loss)' ayarını '1 Paket' olarak seçin; bu ayar sub-tick takılmalarını %80 azaltır.",
                    "difficulty": "Kolay"
                }
            ]),
            "verify_command": "Get-ChildItem \"$env:LOCALAPPDATA\\NVIDIA\\DXCache\" -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum",
            "success_rate": 94,
            "views": 19300,
            "helpful_votes": 1540,
            "created_at": "2026-10-15"
        },
        {
            "game_slug": "cs2",
            "title": "CS2 Mikrofon Algılamama ve Sesin Karşı Tarafa Kesik/Hiç Gitmemesi",
            "error_code": "AUDIO-MIC-THRESHOLD",
            "severity": "Orta",
            "category": "Ses & Donanım",
            "symptom_summary": "Discord ve Windows'ta mikrofon sorunsuz çalışırken CS2 içinde bas-konuş tuşuna basıldığında ses simgesi çıkıyor ama takım arkadaşları hiçbir şey duymuyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "Reddit r/GlobalOffensive",
                    "thread": "Why your mic isn't working in CS2: voice_threshold and Windows Default Communications Device",
                    "quote": "CS2'de varsayılan mikrofon algılama eşiği çok yüksek çalışabiliyor. Konsola `voice_threshold 0` yazmak ve 'Kolaylaştırılmış Bas-Konuş (Streamlined Push to Talk)' açmak sorunu tamamen çözdü.",
                    "upvotes": 1120
                }
            ]),
            "ai_root_cause": "CS2 ses alt sistemi, mikrofon gürültü kapısı (noise gate) eşiğini (`voice_threshold`) bazı ses kartlarında çok yüksek algılar ve bas-konuş tuşuna basıldığında ses aygıtını o anda uyandırmaya çalışırken ilk 1-2 saniyeyi yutar.",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "Kolaylaştırılmış Bas-Konuş (Streamlined Push-to-Talk) Açın",
                    "detail": "CS2 Ayarlar -> Ses -> 'Kolaylaştırılmış Bas-Konuş' ayarını 'Evet' yapın. Bu ayar mikrofonu arka planda hazır tutarak bas-konuş gecikmesini ve ses kesilmesini önler.",
                    "difficulty": "Kolay"
                },
                {
                    "step": 2,
                    "title": "Steam Ses Ayarları ve Windows İletişim Aygıtı Eşitlemesi",
                    "detail": "Shift+Tab ile Steam Arayüzünü açıp Ayarlar -> Ses bölümünden Mikrofonunuzu 'Varsayılan' yerine doğrudan kendi adıyla seçin ve 'Ses Eşiği (Voice Transmission Threshold)' ayarını Kapalı yapın.",
                    "difficulty": "Kolay"
                }
            ]),
            "verify_command": "Get-CimInstance Win32_SoundDevice | Select-Object Name, Status",
            "success_rate": 98,
            "views": 11200,
            "helpful_votes": 870,
            "created_at": "2026-10-11"
        },
        {
            "game_slug": "cs2",
            "title": "pak01.vpk Bozuk Dosya Hatası ve Maç Ortasında Masaüstüne Atma",
            "error_code": "VPK-CORRUPT-01",
            "severity": "Yüksek",
            "category": "Çökme & Başlatma",
            "symptom_summary": "Harita yüklenirken 'Content file pak01.vpk doesn't match the server's file' hatası verip oyundan atıyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "Technopat Sosyal",
                    "thread": "Çözüldü: CS2 pak01.vpk Hatası Sürekli Tekrarlıyor (XMP / EXPO Bellek Kararsızlığı)",
                    "quote": "Sürekli pak01.vpk bozuluyorsa %90 RAM XMP/EXPO profilindeki anlık bit hatasından kaynaklanıyor. RAM frekansını bir kademe düşürünce bir daha hiç VPK hatası almadım.",
                    "upvotes": 460
                }
            ]),
            "ai_root_cause": "Source 2 motoru sıkıştırılmış `.vpk` arşivlerini RAM üzerinde anlık açar ve CRC kontrolü yapar. Hatalı `.vpk` bloğu veya agresif DDR4/DDR5 XMP/EXPO bellek zamanlaması CRC doğrulamasını bozar.",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "Hatalı VPK Dosyasını Silip Doğrulama Yapın",
                    "detail": "`steamapps\\common\\Counter-Strike Global Offensive\\game\\csgo` klasöründeki hata veren `pak01_xxx.vpk` dosyasını silin ve Steam üzerinden dosya bütünlüğünü doğrulayın.",
                    "difficulty": "Kolay"
                },
                {
                    "step": 2,
                    "title": "Tekrarlıyorsa RAM XMP/EXPO Kararlılığını Test Edin",
                    "detail": "Dosya doğrulamadan birkaç gün sonra tekrar aynı hatayı alıyorsanız Windows Bellek Tanılama (`mdsched.exe`) çalıştırın ve BIOS'tan RAM hızını 200MHz düşürerek test edin.",
                    "difficulty": "Orta"
                }
            ]),
            "verify_command": "Get-CimInstance Win32_PhysicalMemory | Select-Object Manufacturer, ConfiguredClockSpeed, Capacity",
            "success_rate": 92,
            "views": 6800,
            "helpful_votes": 410,
            "created_at": "2026-10-09"
        },

        # LEAGUE OF LEGENDS ISSUES
        {
            "game_slug": "lol",
            "title": "Şampiyon Seçimi Sonrası Oyun Ekranı Gelmiyor ve 'Yeniden Bağlan (Reconnect)' Döngüsü",
            "error_code": "LOL-RECONNECT-LOOP",
            "severity": "Kritik",
            "category": "Çökme & Başlatma",
            "symptom_summary": "Şampiyon seçimi bittikten sonra oyun penceresi (`League of Legends.exe`) açılmıyor, istemcide sürekli 'Yeniden Bağlan' butonu çıkıyor ve tıklayınca hiçbir şey olmuyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "Reddit r/leagueoflegends",
                    "thread": "Fix for 'Reconnect' loop after Champ Select (Overlays + Compatibility Mode + DNS)",
                    "quote": "League of Legends.exe üzerinde Windows Uyumluluk Modu (Windows 7/8) açıksa Vanguard güncellemesinden sonra oyun hiç başlamıyor. Uyumluluk tikini kaldırınca anında düzeldi!",
                    "upvotes": 1340
                },
                {
                    "forum": "Technopat Sosyal",
                    "thread": "LoL Şampiyon Seçiminden Sonra Oyuna Girmiyor (Yeniden Bağlan Hatası)",
                    "quote": "Discord Overlay, MSI Afterburner/RivaTuner ve Nvidia GeForce Experience oyun içi yer paylaşımlarını kapatıp Hextech Onarım mantığıyla Config klasörünü silmek kesin çözüm.",
                    "upvotes": 520
                }
            ]),
            "ai_root_cause": "Riot İstemcisi (`LeagueClientUx.exe`) ile oyun motoru (`League of Legends.exe`) arasındaki yerel el sıkışma; (1) `League of Legends.exe` dosyasında Uyumluluk Modu'nun açık kalması (Vanguard uyumluluk modunu engeller), (2) RivaTuner / Discord / Overwolf DLL enjeksiyonu veya (3) bozuk `game.cfg` dosyası nedeniyle kesilmektedir.",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "Uyumluluk Modu İşaretini Kaldırın (En Yaygın Sebep!)",
                    "detail": "`C:\\Riot Games\\League of Legends\\Game\\League of Legends.exe` dosyasına sağ tıklayın -> Özellikler -> Uyumluluk sekmesine gelin. 'Bu programı uyumluluk modunda çalıştır' işaretliyse KESİNLİKLE kaldırın.",
                    "difficulty": "Kolay"
                },
                {
                    "step": 2,
                    "title": "Config ve Logs Klasörünü Sıfırlayın",
                    "detail": "`C:\\Riot Games\\League of Legends` içindeki `Config` ve `Logs` klasörlerini silin. İstemci ayarlarından Oyun -> 'Eski DX9 Modunu Tercih Et' kapalı olduğundan ve 'Pencereli / Çerçevesiz' modda denediğinizden emin olun.",
                    "difficulty": "Kolay"
                },
                {
                    "step": 3,
                    "title": "Üçüncü Parti DLL Enjeksiyonlarını (RivaTuner / Discord Overlay) Kapatın",
                    "detail": "MSI Afterburner / RivaTuner Statistics Server çalışıyorsa `League of Legends.exe` için 'Application Detection Level: None' yapın.",
                    "difficulty": "Kolay"
                }
            ]),
            "verify_command": "Get-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Layers' -ErrorAction SilentlyContinue",
            "success_rate": 96,
            "views": 15600,
            "helpful_votes": 1290,
            "created_at": "2026-10-15"
        },
        {
            "game_slug": "lol",
            "title": "VAN 185 & VAN -81: Vanguard Bağlantı Koptu ve Oyun Ortasında İstemci Kapanması",
            "error_code": "VAN 185 / VAN -81",
            "severity": "Yüksek",
            "category": "Anti-Cheat & Güvenlik",
            "symptom_summary": "Oyun bittikten sonra veya maç esnasında 'Vanguard Hatası: VAN 185' vererek istemciyi kapatıyor ve tekrar girene kadar ceza yazıyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "Reddit r/LeagueOfLegends",
                    "thread": "How I permanently fixed VAN 185 and VAN -81 errors in League",
                    "quote": "vgc servisinin Hata Kurtarma (Recovery) sekmesinden 1., 2. ve sonraki hatalarda 'Hizmeti Yeniden Başlat' seçtiğimden beri VAN 185 tamamen bitti.",
                    "upvotes": 780
                }
            ]),
            "ai_root_cause": "Arka planda çalışan `vgc.exe` kullanıcı modu servisinin Riot kalp atışı (heartbeat) sunucusuyla olan oturumu zaman aşımına uğradığında veya servis anlık çöktüğünde Windows servisi otomatik yeniden başlatmazsa VAN 185 tetiklenir.",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "VGC Hizmeti İçin Otomatik Kurtarma Ayarlayın",
                    "detail": "`Win + R` -> `services.msc` açın -> `vgc` hizmetine çift tıklayın. 'Kurtarma (Recovery)' sekmesine geçip Birinci, İkinci ve Sonraki Hatalar kısmını 'Hizmeti Yeniden Başlat' ve süreyi '0 dakika' olarak kaydedin.",
                    "difficulty": "Kolay"
                },
                {
                    "step": 2,
                    "title": "Vanguard'ı Temiz Kaldırıp Yeniden Kurun",
                    "detail": "Sistem tepsisinden Vanguard'a sağ tıklayıp `More -> Uninstall Vanguard` seçin. Ardından Riot İstemcisini açarak temiz kurulum yapmasını sağlayın ve bilgisayarı yeniden başlatın.",
                    "difficulty": "Kolay"
                }
            ]),
            "verify_command": "Get-Service -Name 'vgc','vgk' -ErrorAction SilentlyContinue | Select-Object Name, Status, StartType",
            "success_rate": 93,
            "views": 10300,
            "helpful_votes": 815,
            "created_at": "2026-10-13"
        },
        {
            "game_slug": "lol",
            "title": "Alt+Tab Sonrası Ekranın Donması veya FPS'in 60'a Sabitlenmesi",
            "error_code": "DX11-ALTTAB-LOCK",
            "severity": "Orta",
            "category": "Performans & FPS",
            "symptom_summary": "Oyunda Alt+Tab yapıp geri dönünce ekran 3-5 saniye siyah kalıyor veya FPS 240'tan 60'a kilitleniyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "Technopat Sosyal",
                    "thread": "Windows 11 Alt+Tab Sonrası LoL FPS Düşüşü ve Donma Çözümü",
                    "quote": "Windows 11 Ayarlar -> Sistem -> Ekran -> Grafikler -> Pencereli oyunlar için iyileştirmeler ayarını açıp oyunu 'Çerçevesiz (Borderless)' moda almak Alt+Tab süresini 0 saniyeye indirdi.",
                    "upvotes": 395
                }
            ]),
            "ai_root_cause": "Windows Masaüstü Pencere Yöneticisi (DWM) ile Tam Ekran (Exclusive Fullscreen) DirectX 11 takas zinciri (SwapChain) arasında ekran yenileme hızı ve G-Sync/FreeSync durumu senkronize olamadığında oluşur.",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "Oyun İçi Görüntü Modunu 'Çerçevesiz (Borderless)' Yapın",
                    "detail": "LoL Görüntü Ayarları'ndan Tam Ekran yerine 'Çerçevesiz' seçin ve Dikey Senkronizasyon (V-Sync) tikini kaldırın.",
                    "difficulty": "Kolay"
                }
            ]),
            "verify_command": "Get-CimInstance -Namespace root\\wmi -ClassName WmiMonitorListedSupportedSourceModes -ErrorAction SilentlyContinue | Select-Object -First 1",
            "success_rate": 97,
            "views": 6900,
            "helpful_votes": 510,
            "created_at": "2026-10-08"
        },

        # GTA V / FIVEM ISSUES
        {
            "game_slug": "gtav-fivem",
            "title": "FiveM Harita / Doku Yüklenmeme (Texture Loss) ve Boşluğa Düşme Sorunu",
            "error_code": "FIVEM-TEXTURE-LOSS",
            "severity": "Kritik",
            "category": "Performans & FPS",
            "symptom_summary": "Roleplay sunucusunda hızlı araç sürerken yollar, binalar ve dokular kayboluyor, araç yerin altına düşüyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "Cfx.re / FiveM Community Forum",
                    "thread": "[GUIDE] Fixing Texture Loss / City Not Loading on High-Pop RP Servers",
                    "quote": "Extended Texture Budget (Genişletilmiş Doku Bütçesi) çubuğunu %0'da bırakmak FiveM'de özel araç/kıyafet paketleri yüzünden VRAM akışını kilitliyor. %50-%75 arasına çekince tüm harita anında yüklendi!",
                    "upvotes": 1650
                }
            ]),
            "ai_root_cause": "FiveM sunucularındaki yüksek boyutlu özel MLO binalar ve eklenti araçlar (add-on cars), GTA V'in varsayılan akış belleği (Streaming Memory) limitini aşar. 'Extended Texture Budget' ayarı düşük olduğunda RAGE motoru yeni yol dokularını VRAM'e yükleyemez.",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "Extended Texture Budget (Genişletilmiş Doku Bütçesi) Ayarını Artırın",
                    "detail": "Oyun içi Ayarlar -> Grafikler menüsünde 'Extended Texture Budget' çubuğunu ekran kartı VRAM'inize göre %50 ile %75 arasına getirin.",
                    "difficulty": "Kolay"
                },
                {
                    "step": 2,
                    "title": "FiveM Cache Klasörünü Güvenli Şekilde Temizleyin",
                    "detail": "FiveM dosya konumunu açın -> `FiveM Application Data\\data` klasörüne girin. `game-storage` HARİÇ `cache`, `server-cache` ve `server-cache-priv` klasörlerini silin.",
                    "difficulty": "Kolay"
                }
            ]),
            "verify_command": "Test-Path \"$env:LOCALAPPDATA\\FiveM\\FiveM.app\\data\\cache\"",
            "success_rate": 96,
            "views": 21400,
            "helpful_votes": 1890,
            "created_at": "2026-10-16"
        },
        {
            "game_slug": "gtav-fivem",
            "title": "ERR_GFX_D3D_INIT ve FiveM 'Early Exit Trap' Çökme Hatası",
            "error_code": "ERR_GFX_D3D_INIT",
            "severity": "Yüksek",
            "category": "Çökme & Başlatma",
            "symptom_summary": "Oyun yüklenirken veya 15-20 dakika oynadıktan sonra 'ERR_GFX_D3D_INIT' ya da 'FiveM has encountered an error (Early Exit Trap)' vererek kapanıyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "Reddit r/FiveM",
                    "thread": "Solved ERR_GFX_D3D_INIT and DirectX crashes once and for all",
                    "quote": "Belgelerim\\Rockstar Games\\GTA V\\settings.xml içindeki DX_Version değerini kontrol edin ve grafik modlarını (QuantV / NVE) eski sürümse güncelleyin.",
                    "upvotes": 740
                }
            ]),
            "ai_root_cause": "DirectX 11 cihazının ekran kartı sürücüsü zaman aşımı (TDR), bozuk `settings.xml` yapılandırması veya eski sürüm ENB/ReShade/NVE grafik eklentileri (`d3d11.dll`, `dxgi.dll`) yüzünden sıfırlanmasıdır.",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "settings.xml Sıfırlama ve Grafik Eklentisi Kontrolü",
                    "detail": "`Belgeler\\Rockstar Games\\GTA V\\settings.xml` dosyasını silin. GTA V ana dizininde `d3d11.dll` veya `dxgi.dll` varsa geçici olarak kaldırın.",
                    "difficulty": "Kolay"
                }
            ]),
            "verify_command": "Test-Path \"$env:USERPROFILE\\Documents\\Rockstar Games\\GTA V\\settings.xml\"",
            "success_rate": 91,
            "views": 13500,
            "helpful_votes": 940,
            "created_at": "2026-10-12"
        },
        {
            "game_slug": "gtav-fivem",
            "title": "Rockstar Games Launcher 'Code 134' / Social Club Çevrimdışı Mod Hatası",
            "error_code": "SOCIAL-CLUB-134",
            "severity": "Orta",
            "category": "Ağ & Bağlantı",
            "symptom_summary": "GTA V veya FiveM açılırken 'Unable to launch game, please verify your game data (Code 134)' veya Social Club bağlantı hatası veriyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "Rockstar Support / Reddit r/GrandTheftAutoV_PC",
                    "thread": "Code 134 / Offline Mode Fix (Guvenli Internet & Social Club Cache)",
                    "quote": "Belgelerim içindeki Rockstar Games\\Social Club ve Launcher klasörlerini silip modem veya DNS önbelleğini sıfırlayınca Code 134 anında düzeldi.",
                    "upvotes": 510
                }
            ]),
            "ai_root_cause": "Rockstar Games Servisleri'nin yerel kimlik önbelleğinin bozulması veya İSS (Güvenli İnternet / CGNAT IP bloğu) kaynaklı TLS el sıkışma reddi.",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "Social Club Yerel Profilini Yenileyin",
                    "detail": "Rockstar Games Launcher'ı kapatın. `Belgeler\\Rockstar Games\\Social Club` ve `Launcher` klasörlerinin adını `_old` olarak değiştirip Launcher'ı Yönetici olarak çalıştırın.",
                    "difficulty": "Kolay"
                }
            ]),
            "verify_command": "ipconfig /flushdns",
            "success_rate": 94,
            "views": 8200,
            "helpful_votes": 530,
            "created_at": "2026-10-07"
        },

        # EA SPORTS FC 25 ISSUES
        {
            "game_slug": "fc25",
            "title": "EA AntiCheat Başlatılamadı (Hata Kodu 115 / Secure Boot & Servis Hatası)",
            "error_code": "EAAC-ERR-115",
            "severity": "Kritik",
            "category": "Anti-Cheat & Güvenlik",
            "symptom_summary": "EA App veya Steam üzerinden FC 25 başlatılırken küçük EA AntiCheat penceresi doluyor ancak 'EA AntiCheat Service Encountered an Error' diyerek oyun kapanıyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "EA Answers HQ / Reddit r/EASportsFC",
                    "thread": "[PC] Fixed EA AntiCheat Launch Failure & Splash Screen Crash in FC 25",
                    "quote": "Oyun klasöründeki EAAntiCheat.Installer.exe dosyasını Yönetici olarak açıp önce 'Uninstall All', sonra 'Install' yapmak ve FC25.exe dijital imzasını yüklemek sorunu tamamen çözdü.",
                    "upvotes": 1190
                }
            ]),
            "ai_root_cause": "EA AntiCheat çekirdek sürücüsü (`EAAntiCheat.sys`), güncelleme sırasında eski sertifika önbelleğiyle çakıştığında veya `RivaTuner / Overwolf` gibi katman yazılımları `FC25.exe` belleğine erken kanca attığında başlatmayı iptal eder.",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "EAAntiCheat.Installer.exe ile Temiz Yeniden Kurulum Yapın",
                    "detail": "`EA SPORTS FC 25\\__Installer\\EAAntiCheat` klasöründeki `EAAntiCheat.Installer.exe` aracını Yönetici olarak çalıştırın. Açılan listeden FC 25'i seçip önce 'Kaldır (Uninstall)', ardından 'Yükle (Install)' butonuna basın.",
                    "difficulty": "Kolay"
                },
                {
                    "step": 2,
                    "title": "EA App Önbelleğini (App Recovery) Temizleyin",
                    "detail": "EA App sol üst menüden `Help -> App Recovery -> Clear Cache` seçeneğine tıklayarak bozuk oturum jetonlarını sıfırlayın.",
                    "difficulty": "Kolay"
                }
            ]),
            "verify_command": "Get-Service -Name 'EAAntiCheatService' -ErrorAction SilentlyContinue | Select-Object Name, Status, StartType",
            "success_rate": 95,
            "views": 16400,
            "helpful_votes": 1340,
            "created_at": "2026-10-16"
        },
        {
            "game_slug": "fc25",
            "title": "Korner, Duran Top ve Ara Sahnelerde Şiddetli FPS Düşüşü ve Takılma",
            "error_code": "FC25-CUTSCENE-FPS",
            "severity": "Yüksek",
            "category": "Performans & FPS",
            "symptom_summary": "Maç içi akıcıyken kornerlerde, gol sevinçlerinde ve devre arası geçişlerinde FPS bir anda 30'un altına düşüp oyun ağır çekime giriyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "Reddit r/EASportsFC",
                    "thread": "PC Stutter & Cutscene FPS Drop Fix: fcsetup.ini & Cloth/Hair Physics",
                    "quote": "Oyun içi Dinamik Çözünürlük (Dynamic Resolution) kapatıp Telli Saç (Strand Based Hair) ayarını Kapalı yapmak ve Ara Sahne Kalitesini 'Tam Kare Hızı (Full Frame Rate)' seçmek korner takılmalarını %100 bitirdi.",
                    "upvotes": 980
                }
            ]),
            "ai_root_cause": "Frostbite motorunda 'Telli Saç (Strand Based Hair)' ve 'Yarım Kare Hızı Ara Sahne' açık olduğunda korner/yakın çekim kameralarda GPU tessellation yükü aniden 4 katına çıkar ve V-Sync zamanlayıcısı kilitlenir.",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "Ara Sahne Performansı ve Telli Saç (Strand Hair) Ayarını Değiştirin",
                    "detail": "Oyun Ayarları -> Ekran Yapılandırması altında 'Ara Sahne Kalitesi: Tam Kare Hızı (Full Frame Rate)', 'Telli Saç: Kapalı' ve 'Dinamik Çözünürlük Ölçeği: Kapalı' olarak ayarlayın.",
                    "difficulty": "Kolay"
                }
            ]),
            "verify_command": "Test-Path \"$env:LOCALAPPDATA\\EA SPORTS FC 25\\fcsetup.ini\"",
            "success_rate": 96,
            "views": 11900,
            "helpful_votes": 920,
            "created_at": "2026-10-14"
        },

        # MINECRAFT ISSUES
        {
            "game_slug": "minecraft",
            "title": "Exit Code: 1 & GLFW Error 65542 (WGL: The Driver Does Not Appear to Support OpenGL)",
            "error_code": "MC-EXIT-CODE-1 / GLFW-65542",
            "severity": "Kritik",
            "category": "Çökme & Başlatma",
            "symptom_summary": "Minecraft Launcher'da 'Oyna' butonuna bastıktan hemen sonra oyun 'Oyun Beklenmedik Şekilde Çöktü (Çıkış Kodu: 1)' veya 'GLFW Error 65542' hatası veriyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "Reddit r/MinecraftHelp",
                    "thread": "[Java] Solved Exit Code 1 & GLFW Error 65542 on laptops and modded 1.20 / 1.21",
                    "quote": "Minecraft 1.20.5 ve 1.21 sürümleri Java 21 gerektiriyor! Eski Java 17 yolu seçiliyse veya mods klasöründe eski sürüm OptiFine/Fabric API kalmışsa anında Exit Code 1 veriyor.",
                    "upvotes": 1540
                }
            ]),
            "ai_root_cause": "Exit Code 1 hatasının iki temel nedeni vardır: (1) `.minecraft\\mods` klasöründe seçilen oyun sürümüyle uyumsuz bir mod/OptiFine `.jar` dosyası bulunması, (2) `javaw.exe` sürecinin harici ekran kartı (NVIDIA/AMD) yerine bozuk dahili GPU OpenGL sürücüsüyle (`opengl32.dll`) başlatılması.",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "Mods Klasörünü ve Java Sürümünü Kontrol Edin",
                    "detail": "`Win + R` -> `%appdata%\\.minecraft` klasörüne girin. `mods` klasöründeki uyumsuz modları yedekleyip boşaltın. Launcher -> Yüklemeler -> Düzenle -> Daha Fazla Seçenek altından 'Java Yürütülebilir Dosyası' kısmını varsayılana (Java 21) sıfırlayın.",
                    "difficulty": "Kolay"
                },
                {
                    "step": 2,
                    "title": "javaw.exe İçin Yüksek Performanslı GPU Seçin",
                    "detail": "Windows Ayarlar -> Sistem -> Ekran -> Grafikler menüsünden `javaw.exe` dosyasını ekleyip 'Yüksek Performans (Harici GPU)' olarak işaretleyin.",
                    "difficulty": "Kolay"
                }
            ]),
            "verify_command": "Test-Path \"$env:APPDATA\\.minecraft\\logs\\latest.log\"",
            "success_rate": 96,
            "views": 22500,
            "helpful_votes": 1910,
            "created_at": "2026-10-15"
        },
        {
            "game_slug": "minecraft",
            "title": "Yüksek FPS'e Rağmen Chunk Yüklenirken Anlık Donma (JVM Garbage Collection Lag Spike)",
            "error_code": "JVM-GC-SPIKE",
            "severity": "Yüksek",
            "category": "Performans & FPS",
            "symptom_summary": "FPS 400 görünmesine rağmen dünyada koşarken veya F3 ekranında bellek %85'e ulaştığında oyun her 3-4 saniyede bir anlık donuyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "Technopat Sosyal / Reddit r/feedthebeast",
                    "thread": "Minecraft RAM Verme Hatası: Çok Fazla RAM Vermek Neden Drop Yapar? (Aikar's Flags)",
                    "quote": "Minecraft'a 12GB-16GB RAM vermek Java Garbage Collector'un tek seferde devasa bellek temizliği yaparken oyunu dondurmasına yol açar. 4GB-6GB arası verip G1GC argümanları kullanmak tüm donmaları bitirdi.",
                    "upvotes": 870
                }
            ]),
            "ai_root_cause": "JVM (Java Sanal Makinesi) gereğinden fazla RAM (`-Xmx16G` gibi) ayrıldığında çöp toplama (Garbage Collection) döngüsünü geciktirir ve tek seferde büyük bellek bloğunu temizlerken 'Stop-the-World' duraksaması yaşatır.",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "Optimum JVM Başlatma Argümanlarını (4GB-6GB + G1GC) Girin",
                    "detail": "Minecraft Launcher -> Yüklemeler -> Düzenle -> JVM Değişkenleri satırını `-Xmx4G -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1NewSizePercent=20 -XX:G1ReservePercent=20 -XX:MaxGCPauseMillis=50` olarak güncelleyin.",
                    "difficulty": "Kolay"
                }
            ]),
            "verify_command": "Get-Process javaw -ErrorAction SilentlyContinue | Select-Object Name, WorkingSet64",
            "success_rate": 95,
            "views": 13400,
            "helpful_votes": 1080,
            "created_at": "2026-10-11"
        },

        # CALL OF DUTY: WARZONE & BO6 ISSUES
        {
            "game_slug": "cod-warzone",
            "title": "DirectX Encountered an Unrecoverable Error (0x887A0005 / Dev Error 0x00001338)",
            "error_code": "DX-0x887A0005 / 0x1338",
            "severity": "Kritik",
            "category": "Çökme & Başlatma",
            "symptom_summary": "Maçın ortasında veya uçaktan atlarken 'DirectX encountered an unrecoverable error' uyarısı verip masaüstüne atıyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "Reddit r/CODWarzone",
                    "thread": "How I stopped DirectX 0x887A0005 & 0x00001338 crashes in Warzone / BO6",
                    "quote": "VRAM Scale Target (VRAM Ölçek Hedefi) varsayılan olarak 90 geliyor ve CoD belleği taşırıp sürücüyü çökertiyor. Bu değeri 70'e çekip İsteğe Bağlı Doku Akışını (On-Demand Texture Streaming) Minimal yapınca çökmeler tamamen bitti.",
                    "upvotes": 1680
                }
            ]),
            "ai_root_cause": "IW 9.0 motoru, VRAM Scale Target %85-%90 olduğunda Windows DWM için ayrılan paylaşımlı GPU belleğine taşar ve DirectX 12 `DXGI_ERROR_DEVICE_REMOVED (0x887A0005)` hatasını tetikler.",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "VRAM Scale Target Değerini 70'e Düşürün ve Shader Yeniden Başlatın",
                    "detail": "Grafikler -> Kalite -> 'VRAM Scale Target' ayarını `70` olarak ayarlayın. Aynı menüden 'Restart Shaders Pre-Loading' (Gölgelendirici Ön Yüklemesini Yeniden Başlat) seçeneğine tıklayıp %100 olmasını bekleyin.",
                    "difficulty": "Kolay"
                }
            ]),
            "verify_command": "Get-ChildItem \"$env:USERPROFILE\\Documents\\Call of Duty\\players\" -ErrorAction SilentlyContinue",
            "success_rate": 94,
            "views": 17600,
            "helpful_votes": 1410,
            "created_at": "2026-10-15"
        },
        {
            "game_slug": "cod-warzone",
            "title": "Sürekli 'Packet Burst' (Turuncu 3 Kare İkonu) ve Çatışmada Takılma",
            "error_code": "COD-PACKET-BURST",
            "severity": "Yüksek",
            "category": "Performans & FPS",
            "symptom_summary": "Ping normal olmasına rağmen ekranın solunda sürekli turuncu 'Packet Burst' uyarısı çıkıyor ve oyun yarım saniye tekleme yapıyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "Reddit r/CODWarzone",
                    "thread": "PSA: 'Packet Burst' in Warzone is often CPU Thread Bottleneck + On-Demand Texture Streaming!",
                    "quote": "Belgelerim\\Call of Duty\\players klasöründeki ayar dosyasında RendererWorkerCount değerini işlemcinizin fiziksel çekirdek sayısına (veya 1 eksiğine) eşitlemek Packet Burst takılmalarını mucizevi şekilde çözüyor.",
                    "upvotes": 1290
                }
            ]),
            "ai_root_cause": "Warzone'daki 'Packet Burst' uyarısı yalnızca internetten değil, işlemcinin sunucudan gelen sıkıştırılmış dünya durum paketlerini ve anlık indirilen dokuları (`On-Demand Texture Streaming`) zamanında işleyememesinden kaynaklanır.",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "RendererWorkerCount Değerini Fiziksel Çekirdek Sayınıza Ayarlayın",
                    "detail": "`Belgeler\\Call of Duty\\players` içindeki `.cst` / `.ini` yapılandırma dosyasını Not Defteri ile açın. `RendererWorkerCount` satırını bulup işlemcinizin fiziksel çekirdek sayısına (Örn: 6 çekirdekli Ryzen 5 5600 için `6`, 8 çekirdekli işlemci için `7` veya `8`) ayarlayıp kaydedin.",
                    "difficulty": "Orta"
                }
            ]),
            "verify_command": "Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors",
            "success_rate": 93,
            "views": 14100,
            "helpful_votes": 1120,
            "created_at": "2026-10-12"
        },

        # RUST ISSUES
        {
            "game_slug": "rust",
            "title": "Sunucuya Girerken 'Asset Warmup' Sırasında Oyunun Kapanması ve EAC Timed Out",
            "error_code": "RUST-WARMUP-EAC",
            "severity": "Kritik",
            "category": "Çökme & Başlatma",
            "symptom_summary": "Sunucuya bağlanırken 'Asset Warmup (4500/9800)' aşamasında oyun hiçbir hata vermeden masaüstüne kapanıyor veya 'EAC Authentication Timed Out' veriyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "Reddit r/playrust",
                    "thread": "Crashing on Asset Warmup with 16GB RAM? Fix your Windows Pagefile (Virtual Memory)!",
                    "quote": "Rust sunucuya girerken anlık 22GB+ sanal bellek (commit charge) talep ediyor. 16GB RAM'iniz varsa ve Windows Sanal Belleği (Pagefile) kapalı veya küçükse Asset Warmup'ta %100 çöker.",
                    "upvotes": 1450
                }
            ]),
            "ai_root_cause": "Unity tabanlı Rust, büyük haritalı sunucularda tüm prefab varlıklarını yüklerken 16GB fiziksel RAM'i aşar. SSD üzerinde yeterli Sanal Bellek (`pagefile.sys`) yoksa Windows bellek tahsisini reddeder (`OutOfMemoryException`).",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "SSD Üzerinde Sanal Belleği (Pagefile) 16384 MB (16 GB) Yapın",
                    "detail": "`Win + R` -> `sysdm.cpl` -> Gelişmiş -> Performans Ayarları -> Gelişmiş -> Sanal Bellek 'Değiştir' menüsüne girin. SSD diskiniz için Özel Boyut seçip Başlangıç: `16384`, En Büyük: `24576` MB yazıp 'Ayarla' butonuna basın ve yeniden başlatın.",
                    "difficulty": "Kolay"
                }
            ]),
            "verify_command": "Get-CimInstance Win32_PageFileUsage | Select-Object Name, AllocatedBaseSize, CurrentUsage",
            "success_rate": 97,
            "views": 15200,
            "helpful_votes": 1280,
            "created_at": "2026-10-14"
        },
        {
            "game_slug": "rust",
            "title": "Büyük Klan Üslerinin Yanında 1 Saniyelik Donma (Garbage Collection Stutter)",
            "error_code": "RUST-GC-BUFFER",
            "severity": "Yüksek",
            "category": "Performans & FPS",
            "symptom_summary": "Haritada uçarken veya büyük yapıların yanından geçerken oyun aniden 1 saniyeliğine tamamen kilitleniyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "Reddit r/playrust",
                    "thread": "Reminder: Always set gc.buffer 2048 or 4096 in F1 console!",
                    "quote": "Rust varsayılan olarak `gc.buffer 256` ile açılıyor ve bellek tamponu her dakikada bir dolup oyunu donduruyor. `gc.buffer 2048` yapınca takılmalar bitti.",
                    "upvotes": 1120
                }
            ]),
            "ai_root_cause": "Unity motorunun varsayılan 256MB çöp toplama tamponu (`gc.buffer`) Rust'ın yoğun varlık akışında çok sık dolar.",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "F1 Konsolundan gc.buffer Değerini 2048 Yapın ve Kaydedin",
                    "detail": "Oyun içinde `F1` tuşuyla konsolu açıp sırasıyla `gc.buffer 2048` ve ardından ayarların kalıcı olması için `writecfg` komutunu yazıp Enter'a basın.",
                    "difficulty": "Kolay"
                }
            ]),
            "verify_command": "Get-Process RustClient -ErrorAction SilentlyContinue | Select-Object Name, WorkingSet64",
            "success_rate": 96,
            "views": 10800,
            "helpful_votes": 890,
            "created_at": "2026-10-10"
        },

        # APEX LEGENDS ISSUES
        {
            "game_slug": "apex-legends",
            "title": "0x887A0006 - DXGI_ERROR_DEVICE_HUNG Motor Çökme Hatası",
            "error_code": "DXGI-0x887A0006",
            "severity": "Kritik",
            "category": "Çökme & Başlatma",
            "symptom_summary": "Maç esnasında ekran donuyor ve 'Engine Error - 0x887A0006 - DXGI_ERROR_DEVICE_HUNG' uyarısıyla oyun kapanıyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "Reddit r/apexlegends",
                    "thread": "Solved 0x887A0006 DXGI_ERROR_DEVICE_HUNG on NVIDIA & AMD cards",
                    "quote": "Spot Shadow Detail (Spot Gölge Detayı) ayarını Kapalı yapmak ve DirectX 12 başlatma seçeneğiyle çalıştırmak DXGI çökmesini tamamen ortadan kaldırdı.",
                    "upvotes": 950
                }
            ]),
            "ai_root_cause": "Modifiye Source motorunda dinamik spot gölge hesaplamaları yüksek GPU Boost saat hızlarında TDR (Timeout Detection and Recovery) süresini aşarak sürücüyü askıda bırakır.",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "Spot Shadow Detail Kapatma ve Texture Streaming Budget Ayarı",
                    "detail": "Oyun içi Video Ayarları'ndan 'Spot Shadow Detail: Disabled' ve 'Dynamic Spot Shadows: Disabled' yapın. Steam başlatma seçeneklerinde bozuk `-high` komutu varsa kaldırın.",
                    "difficulty": "Kolay"
                }
            ]),
            "verify_command": "Test-Path \"$env:USERPROFILE\\Saved Games\\Respawn\\Apex\\local\\videoconfig.txt\"",
            "success_rate": 93,
            "views": 11500,
            "helpful_votes": 840,
            "created_at": "2026-10-13"
        },
        {
            "game_slug": "apex-legends",
            "title": "Maç Başında %100 CPU Kullanımı ve code:net / code:leaf Kopması",
            "error_code": "APEX-100CPU-CODENET",
            "severity": "Yüksek",
            "category": "Performans & FPS",
            "symptom_summary": "Haritaya ilk girildiğinde işlemci kullanımı %100'de kilitleniyor, fare takılıyor veya 'code:net' verip ana menüye atıyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "EA Forums / Reddit r/apexuniversity",
                    "thread": "Fix for 100% CPU usage spike at the start of every match in Apex",
                    "quote": "NVIDIA/AMD Shader Cache klasörünü temizledikten sonra lobide 2 dakika bekleyip tüm harita shaderlarının arka planda derlenmesini sağlamak %100 CPU sorununu çözüyor.",
                    "upvotes": 680
                }
            ]),
            "ai_root_cause": "Harita gölgelendiricileri (Vulkan/DX11 Shaders) maç başında tüm CPU çekirdeklerinde eşzamanlı derlendiğinde ağ iş parçacığı zaman aşımına uğrayarak `code:net` verir.",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "videoconfig.txt ve Shader Cache Yenileme",
                    "detail": "`%userprofile%\\Saved Games\\Respawn\\Apex\\local\\videoconfig.txt` içinde `setting.cl_ragdoll_self_collision` değerini `0` yapın ve oyunu açtıktan sonra maça girmeden पहले Poligon (Firing Range) haritasına bir kez girin.",
                    "difficulty": "Kolay"
                }
            ]),
            "verify_command": "Get-Process r5apex* -ErrorAction SilentlyContinue | Select-Object Name, CPU",
            "success_rate": 92,
            "views": 8400,
            "helpful_votes": 610,
            "created_at": "2026-10-09"
        },

        # CYBERPUNK 2077 ISSUES
        {
            "game_slug": "cyberpunk-2077",
            "title": "'Whoa! Cyberpunk 2077 Has Flatlined' Başlangıçta veya Kayıt Yüklerken Çökme",
            "error_code": "CP77-FLATLINED",
            "severity": "Kritik",
            "category": "Çökme & Başlatma",
            "symptom_summary": "CDPR Launcher'dan 'Oyna' dedikten hemen sonra ya da kayıtlı oyunu yüklerken 'Whoa! Cyberpunk 2077 has flatlined' hata raporu çıkıp oyun kapanıyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "Reddit r/cyberpunkgame",
                    "thread": "Ultimate Fix for 'Cyberpunk 2077 has flatlined' after patch / mod updates",
                    "quote": "Oyunu silip yükleseniz bile klasörde kalan eski `r6/cache/modded`, `red4ext` ve `bin/x64/version.dll` dosyaları silinmiyor! Bunları temizleyip UserSettings.json silince hemen açıldı.",
                    "upvotes": 1890
                }
            ]),
            "ai_root_cause": "REDengine 4 çökme günlüklerine (`stacktrace.txt`) göre 'Flatlined' hatalarının %85'i; oyun güncellendikten sonra kalan uyumsuz Cyber Engine Tweaks (`version.dll`), RED4ext/ArchiveXL kancaları veya bozuk `UserSettings.json` kaynaklıdır.",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "UserSettings.json ve Gölgelendirici Önbelleğini Sıfırlayın",
                    "detail": "`%localappdata%\\CD Projekt Red\\Cyberpunk 2077\\UserSettings.json` dosyasını silin. Bu işlem bozuk Ray Tracing / DLSS Frame Generation bayraklarını sıfırlar.",
                    "difficulty": "Kolay"
                },
                {
                    "step": 2,
                    "title": "Artık Mod DLL Kancalarını Temizleyin",
                    "detail": "Oyun klasöründeki `bin\\x64\\version.dll`, `winmm.dll` ve `r6\\cache\\modded` klasörlerini silin, ardından Steam/Epic üzerinden dosya doğrulaması yapın.",
                    "difficulty": "Kolay"
                }
            ]),
            "verify_command": "Test-Path \"$env:LOCALAPPDATA\\CD Projekt Red\\Cyberpunk 2077\\UserSettings.json\"",
            "success_rate": 95,
            "views": 14800,
            "helpful_votes": 1210,
            "created_at": "2026-10-14"
        },
        {
            "game_slug": "cyberpunk-2077",
            "title": "Ses Cızırtısı (Audio Crackling / Popping) ve Harita Açıp Kapatınca FPS Çöküşü",
            "error_code": "CP77-AUDIO-VRAM",
            "severity": "Orta",
            "category": "Ses & Donanım",
            "symptom_summary": "Yoğun çatışmalarda seste patlama/cızırtı oluyor ve haritayı veya envanteri birkaç kez açıp kapatınca FPS yarıya düşüyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "Steam Community / Reddit r/cyberpunkgame",
                    "thread": "Fix for Audio Crackling (Sample Rate 48000Hz) & Map Opening VRAM Leak",
                    "quote": "Windows Ses Ayarları'ndan örnekleme hızını 192000Hz/96000Hz yerine 24 bit 48000 Hz (DVD Kalitesi) yapınca ses cızırtısı tamamen kesildi.",
                    "upvotes": 670
                }
            ]),
            "ai_root_cause": "REDengine 4 ses mikseri 96kHz/192kHz örnekleme hızlarında tampon taşması yaşar. Harita açılışındaki FPS düşüşü ise 8GB/12GB VRAM'li kartlarda Işın İzleme doku havuzunun dolmasından kaynaklanır.",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "Windows Ses Formatını 24-bit, 48000 Hz Yapın",
                    "detail": "Denetim Masası -> Ses -> Kulaklık/Hoparlör Özellikleri -> Gelişmiş sekmesinden varsayılan biçimi '24 bit, 48000 Hz (Stüdyo Kalitesi)' olarak ayarlayın ve Uzamsal Sesi kapatın.",
                    "difficulty": "Kolay"
                }
            ]),
            "verify_command": "Get-CimInstance Win32_SoundDevice | Select-Object Name, Status",
            "success_rate": 96,
            "views": 7400,
            "helpful_votes": 520,
            "created_at": "2026-10-08"
        },

        # ELDEN RING ISSUES
        {
            "game_slug": "elden-ring",
            "title": "Inappropriate Activity Detected (Easy Anti-Cheat) ve Çevrimiçi Moda Girememe",
            "error_code": "EAC-INAPPROPRIATE",
            "severity": "Yüksek",
            "category": "Anti-Cheat & Güvenlik",
            "symptom_summary": "Herhangi bir hile kullanılmamasına rağmen ana menüde 'Inappropriate activity detected. Unable to start in online mode' hatası veriyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "Reddit r/Eldenring",
                    "thread": "Solved 'Inappropriate Activity Detected' after DLC / Patch update",
                    "quote": "Game\\EasyAntiCheat\\easyanticheat_eos_setup.exe dosyasını yönetici olarak çalıştırıp onarmak ve Steam DLC/oyun dosyalarını doğrulamak sorunu hemen çözdü.",
                    "upvotes": 1150
                }
            ]),
            "ai_root_cause": "Easy Anti-Cheat (EOS) servisinin güncelleme sonrası imza kataloglarının (`Certificates` klasörü) eşleşmemesi veya Windows Çekirdek Yalıtımı ile eski EAC sürücüsünün çakışmasıdır.",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "Easy Anti-Cheat EOS Servisini Yeniden Kaydedin",
                    "detail": "`ELDEN RING\\Game\\EasyAntiCheat` klasöründe CMD'yi Yönetici olarak açıp `easyanticheat_eos_setup.exe install 58fe7b6b942a4f9d9ef2ebde7b56a0e6` komutunu çalıştırın ve Steam dosya doğrulaması yapın.",
                    "difficulty": "Orta"
                }
            ]),
            "verify_command": "Get-Service -Name 'EasyAntiCheat*' -ErrorAction SilentlyContinue",
            "success_rate": 95,
            "views": 9800,
            "helpful_votes": 730,
            "created_at": "2026-10-11"
        },
        {
            "game_slug": "elden-ring",
            "title": "Boss Savaşlarında 1-2 Saniyelik Çift Donma (USB Device Enumerate Stutter)",
            "error_code": "ER-USB-STUTTER",
            "severity": "Yüksek",
            "category": "Performans & FPS",
            "symptom_summary": "Oyun akıcı giderken rastgele anlarda (özellikle boss savaşlarında) arka arkaya iki kez 1 saniye boyunca tamamen donuyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "Reddit r/Eldenring",
                    "thread": "The secret culprit behind Elden Ring's 1-second double freezes: Device Association Service & Xbox Game Pass virtual disks",
                    "quote": "Aygıt Yöneticisi'nde Xbox uygulaması tarafından oluşturulan 'Xvdd SCSI Miniport' sanal disk sürücüsü sürekli yenilendiği için Elden Ring her yenilemede 2 kez donuyor!",
                    "upvotes": 2400
                }
            ]),
            "ai_root_cause": "FromSoftware motoru DirectInput üzerinden bağlı donanım listesi (`WM_DEVICECHANGE`) her değiştiğinde tüm kontrolcüleri yeniden tarar. Windows'taki sanal diskler (`Xvdd`) veya temassızlık yapan USB aygıtları bu taramayı tetikleyerek çift donmaya yol açar.",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "Aygıt Yöneticisi'nde Sanal 'Xvdd' ve Kullanılmayan HID Aygıtlarını Kontrol Edin",
                    "detail": "Aygıt Yöneticisi -> Depolama Denetleyicileri altında 'Xvdd SCSI Miniport' varsa devre dışı bırakın. Ayrıca 'Microsoft Device Association Root Enumerator' öğesini devre dışı bırakarak USB tarama donmalarını engelleyin.",
                    "difficulty": "Orta"
                }
            ]),
            "verify_command": "Get-PnpDevice -FriendlyName '*Enumerator*' -ErrorAction SilentlyContinue | Select-Object Status, FriendlyName",
            "success_rate": 96,
            "views": 14200,
            "helpful_votes": 1310,
            "created_at": "2026-10-09"
        },

        # PUBG ISSUES
        {
            "game_slug": "pubg",
            "title": "Maç Bitiminde Lobi Yüklenmeme (Initializing / Siyah Duman Ekranı)",
            "error_code": "PUBG-LOBBY-HANG",
            "severity": "Yüksek",
            "category": "Ağ & Bağlantı",
            "symptom_summary": "Maçtan çıktıktan sonra lobiye dönerken ekran sadece dumanlı arka planda ('Initializing...') kalıyor, menü gelmiyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "Reddit r/PUBATTLEGROUNDS",
                    "thread": "Instant shortcut & permanent DNS/MTU fix for stuck on Lobby Screen after match",
                    "quote": "Lobi takıldığında Backspace -> Shift+Backspace yapmak lobiyi anında yeniliyor! Kalıcı çözüm için CoherentUI_Host.exe'ye güvenlik duvarı izni vermek ve Cloudflare DNS kullanmak gerekiyor.",
                    "upvotes": 920
                }
            ]),
            "ai_root_cause": "PUBG lobisi HTML5 tabanlı bir web arayüzüdür (`CoherentUI_Host.exe`). Maç sonunda lobi sunucusuna yapılan WebSocket bağlantısı MTU parçalanması veya DNS gecikmesi yüzünden zaman aşımına uğradığında arayüz yüklenemez.",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "Anlık Lobi Yenileme Kısayolu ve DNS Değişikliği",
                    "detail": "Takıldığında önce `Backspace`, ardından `Shift + Backspace` tuşlarına basın (arayüzü yeniden yükler). Kalıcı çözüm için ağ bağdaştırıcınızda DNS olarak `1.1.1.1` / `1.0.0.1` tanımlayın.",
                    "difficulty": "Kolay"
                }
            ]),
            "verify_command": "Resolve-DnsName prod-live-front.playbattlegrounds.com -ErrorAction SilentlyContinue",
            "success_rate": 95,
            "views": 8900,
            "helpful_votes": 640,
            "created_at": "2026-10-10"
        },
        {
            "game_slug": "pubg",
            "title": "DirectX 11 Enhanced vs DX11: Şehir İçi Çatışmalarda %100 CPU Kullanımı ve Stutter",
            "error_code": "PUBG-DX11E-CPU",
            "severity": "Orta",
            "category": "Performans & FPS",
            "symptom_summary": "Pochinki veya Bootcamp gibi kalabalık bölgelere paraşütle inerken CPU kullanımı %100'e vuruyor ve FPS yarıya düşüyor.",
            "forum_sources": json.dumps([
                {
                    "forum": "Reddit r/CompetitivePUBG",
                    "thread": "Why Pro Players use DirectX 11 Enhanced instead of DX12 or regular DX11",
                    "quote": "Normal DX11 tek çekirdeğe yükleniyor, DX12 ise stutter yapıyor. 'DirectX 11 Enhanced' seçmek render yükünü çoklu çekirdeklere dağıtarak %1 Low FPS'i ciddi oranda artırıyor.",
                    "upvotes": 810
                }
            ]),
            "ai_root_cause": "Standart DX11 modunda çizim çağrıları (Draw Calls) tek bir ana render iş parçacığında toplanır ve kalabalık şehirlerde CPU darboğazı yaratır.",
            "ai_solution_steps": json.dumps([
                {
                    "step": 1,
                    "title": "DirectX 11 Enhanced Moduna Geçin ve TslGame Önbelleğini Silin",
                    "detail": "PUBG Grafik Ayarları -> Gelişmiş -> DirectX Sürümü ayarını 'DirectX 11 Enhanced' yapın ve oyunu yeniden başlatın.",
                    "difficulty": "Kolay"
                }
            ]),
            "verify_command": "Get-Process TslGame -ErrorAction SilentlyContinue | Select-Object Name, CPU, WorkingSet64",
            "success_rate": 93,
            "views": 7100,
            "helpful_votes": 480,
            "created_at": "2026-10-06"
        }
    ]

    for issue in issues_data:
        cursor.execute("""
            INSERT INTO issues (
                game_slug, title, error_code, severity, category, symptom_summary,
                forum_sources, ai_root_cause, ai_solution_steps, verify_command,
                success_rate, views, helpful_votes, created_at
            ) VALUES (
                :game_slug, :title, :error_code, :severity, :category, :symptom_summary,
                :forum_sources, :ai_root_cause, :ai_solution_steps, :verify_command,
                :success_rate, :views, :helpful_votes, :created_at
            )
        """, issue)

    # Also seed all games and issues from WORLD_GAMES_CATALOG so the hub has 31+ games and 55+ issues out of the box
    try:
        from game_catalog import WORLD_GAMES_CATALOG
        existing_slugs = {g["slug"] for g in games_data}
        for idx, cg in enumerate(WORLD_GAMES_CATALOG):
            if cg["slug"] not in existing_slugs:
                cursor.execute("""
                    INSERT INTO games (slug, name, short_name, category, developer, accent_color, secondary_color, engine, anticheat, banner_subtitle, common_tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cg["slug"],
                    cg["name"],
                    cg["short_name"],
                    cg["category"],
                    cg["developer"],
                    cg["accent_color"],
                    cg["secondary_color"],
                    cg["engine"],
                    cg["anticheat"],
                    cg["banner_subtitle"],
                    json.dumps(cg.get("common_tags", []))
                ))
                existing_slugs.add(cg["slug"])

            for iss_idx, c_iss in enumerate(cg.get("default_issues", [])):
                cursor.execute("""
                    INSERT INTO issues (
                        game_slug, title, error_code, severity, category, symptom_summary,
                        forum_sources, ai_root_cause, ai_solution_steps, verify_command,
                        success_rate, views, helpful_votes, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cg["slug"],
                    c_iss["title"],
                    c_iss["error_code"],
                    c_iss["severity"],
                    c_iss["category"],
                    c_iss["symptom_summary"],
                    json.dumps(c_iss.get("forum_sources", [])),
                    c_iss["ai_root_cause"],
                    json.dumps(c_iss.get("ai_solution_steps", [])),
                    c_iss.get("verify_command", "sfc /verifyonly"),
                    c_iss.get("success_rate", 95),
                    6800 + (idx * 430) + (iss_idx * 250),
                    520 + (idx * 35) + (iss_idx * 18),
                    "2026-10-18"
                ))
    except Exception as e:
        print("Catalog seed warning:", e)

    threads_data = [
        {
            "game_slug": "valorant",
            "author_name": "EmreK_VLR",
            "author_avatar": "EK",
            "title": "ASUS B550 anakartta Secure Boot açık ama Valorant hala VAN 9003 hatası veriyor",
            "error_code": "VAN 9003",
            "system_specs": "Windows 11 Pro 24H2 | Ryzen 5 5600X | RTX 4060 | ASUS TUF B550-PLUS",
            "content": "Arkadaşlar BIOS'a girdim OS Type kısmını Windows UEFI Mode yaptım ama oyuna girince 2. rauntta VAN 9003 verip atıyor. msinfo32'ye baktığımda Güvenli Önyükleme Durumu hala Kapalı görünüyor. Nasıl aktif ederim?",
            "status": "OyunÇöz AI Çözümledi",
            "upvotes": 42,
            "views": 610,
            "created_at": "15 dakika önce",
            "replies": [
                {
                    "author_name": "OyunÇöz AI (Teknik Analiz Motoru)",
                    "is_ai": 1,
                    "ai_mode": "Forum + AI Sentezi",
                    "content": "Merhaba **EmreK_VLR**! ASUS B550 serisi anakartlarda sadece `OS Type: Windows UEFI Mode` seçmek, eğer daha önce Key Management anahtarları silindiyse Secure Boot'u `Active` durumuna geçirmez.\n\n### Adım Adım Kesin Çözüm (ASUS BIOS):\n1. Bilgisayarı yeniden başlatıp `DEL` veya `F2` ile BIOS'a girin ve `F7` tuşuyla **Advanced Mode**'a geçin.\n2. **Boot** -> **CSM (Compatibility Support Module)** menüsüne girip `Launch CSM` ayarının **Disabled** olduğundan emin olun.\n3. **Boot** -> **Secure Boot** menüsüne dönün. `OS Type` değerini **Windows UEFI Mode** yapın.\n4. Hemen altındaki **Key Management** sekmesine girin ve **Install Default Secure Boot Keys** (veya *Restore Factory Keys*) seçeneğine tıklayıp onaylayın.\n5. `Secure Boot State` satırının **User / Active** olarak değiştiğini göreceksiniz. `F10` ile kaydedip çıkın.",
                    "helpful_count": 38,
                    "created_at": "14 dakika önce"
                },
                {
                    "author_name": "BurakTech",
                    "is_ai": 0,
                    "ai_mode": None,
                    "content": "Aynısı dün başıma geldi, AI'ın dediği gibi Key Management içinden Install Default Keys yapınca msinfo32'de anında Açık oldu ve VAN 9003 bitti.",
                    "helpful_count": 14,
                    "created_at": "8 dakika önce"
                }
            ]
        },
        {
            "game_slug": "cs2",
            "author_name": "xSniperTR",
            "author_avatar": "XS",
            "title": "CS2 son güncellemeden sonra su ve molotof görünce FPS 280'den 90'a çakılıyor",
            "error_code": "CS2-STUTTER",
            "system_specs": "Windows 11 | i5-13400F | RX 6700 XT | 16GB DDR4 3200MHz",
            "content": "Özellikle Ancient ve Anubis haritalarında suya girince veya molotof/sis atıldığında oyun inanılmaz takılıyor. AMD Adrenalin sürücüm güncel, başlatma seçeneklerinde -high -threads 8 yazılı.",
            "status": "OyunÇöz AI Çözümledi",
            "upvotes": 29,
            "views": 420,
            "created_at": "1 saat önce",
            "replies": [
                {
                    "author_name": "OyunÇöz AI (Teknik Analiz Motoru)",
                    "is_ai": 1,
                    "ai_mode": "Forum + AI Sentezi",
                    "content": "Sistem özelliklerinize (**i5-13400F hibrit P/E çekirdek mimarisi + RX 6700 XT**) göre sorunun iki temel kaynağı tespit edildi:\n\n1. **`-high` ve `-threads 8` Başlatma Kodları:** i5-13400F işlemcinizde Performans (P) ve Verimlilik (E) çekirdekleri bulunur. `-threads 8` komutu Source 2 motorunun iş parçacıklarını yanlışlıkla E-Core çekirdeklerine sıkıştırarak su/parçacık fiziğinde ağır darboğaz yaratır. **Başlatma seçeneklerindeki tüm kodları silin.**\n2. **AMD DXNAVI Gölgelendirici Önbelleği:** AMD Software: Adrenalin Edition -> **Oyun** -> **Ekran Kartları** -> En alttaki **Gelişmiş** bölümünden **Gölgelendirici Önbelleğini Sıfırla (Reset Shader Cache)** işlemini uygulayın ve CS2 içinde **Parçacık Detayı: Düşük** yapın.",
                    "helpful_count": 24,
                    "created_at": "58 dakika önce"
                }
            ]
        },
        {
            "game_slug": "gtav-fivem",
            "author_name": "KaanRP",
            "author_avatar": "KR",
            "title": "FiveM kalabalık motel önünde yollar tamamen kayboluyor, araba boşluğa düşüyor",
            "error_code": "FIVEM-TEXTURE-LOSS",
            "system_specs": "Windows 10 | Ryzen 5 3600 | GTX 1660 Super 6GB | 16GB RAM",
            "content": "Sunucuda 150+ kişi varken şehir merkezine girdiğimde binalar kağıt gibi oluyor ve yollar yok oluyor. Tüm ayarlarım en düşükte olmasına rağmen düzelmedi.",
            "status": "OyunÇöz AI Çözümledi",
            "upvotes": 35,
            "views": 530,
            "created_at": "3 saat önce",
            "replies": [
                {
                    "author_name": "OyunÇöz AI (Teknik Analiz Motoru)",
                    "is_ai": 1,
                    "ai_mode": "Forum + AI Sentezi",
                    "content": "FiveM'de tüm ayarları en düşüğe çekmek paradoksal olarak **Extended Texture Budget** değerini sıfırladığı için doku kaybına (Texture Loss) neden olur!\n\n### GTX 1660 Super (6GB VRAM) İçin Optimum FiveM Ayarları:\n1. **Ayarlar -> Grafikler** sekmesinde en altta yer alan **Extended Texture Budget** çubuğunu **%55 - %65** seviyesine (VRAM barı ~4200 MB civarına gelene kadar) yükseltin.\n2. **Texture Quality (Doku Kalitesi):** `Normal` veya `High` yapın, diğer gölge ve yansıma ayarlarını `Normal` bırakın.\n3. Görev Yöneticisi -> Ayrıntılar sekmesinden `FiveM_bxxxx_GTAProcess.exe` işlemine sağ tıklayıp **Öncelik Ayarla -> Yüksek** seçin.",
                    "helpful_count": 31,
                    "created_at": "3 saat önce"
                }
            ]
        },
        {
            "game_slug": "mount-and-blade-2-bannerlord",
            "author_name": "Alparslan_MB",
            "author_avatar": "AM",
            "title": "Bannerlord 500v500 kuşatma savaşında d3d_device_context_map hatası verip kapanıyor",
            "error_code": "RGL-GPU-MAP-CRASH",
            "system_specs": "Windows 11 | Ryzen 7 5800X3D | RTX 3070 | 32GB RAM",
            "content": "Meydan savaşlarında hiçbir sorun yok ama büyük şehir kuşatmalarında merdivenler kurulurken d3d_device_context_map at rglGPU_device::lock_texture hatasıyla masaüstüne atıyor.",
            "status": "OyunÇöz AI Çözümledi",
            "upvotes": 51,
            "views": 740,
            "created_at": "4 saat önce",
            "replies": [
                {
                    "author_name": "OyunÇöz AI (Teknik Analiz Motoru)",
                    "is_ai": 1,
                    "ai_mode": "Forum + AI Sentezi",
                    "content": "Merhaba **Alparslan_MB**! Bu hata TaleWorlds motorunda kuşatma kuleleri/merdiven dokuları kilitlenirken bozuk gölgelendirici önbelleği (`C:\\ProgramData\\Mount and Blade II Bannerlord\\Shaders`) yüzünden tetiklenir.\n\n1. `Win + R` tuşlarına basıp `C:\\ProgramData\\Mount and Blade II Bannerlord` klasörünü açın ve içindeki **Shaders** klasörünü tamamen silin.\n2. Oyun içi Ses Ayarları'ndan **Ses Kanalları (Sound Channels)** değerini `Yüksek (512)` yerine `Orta (256)` yapın (kuşatma ses taşması da GPU senkronunu bozar).\n3. Grafik ayarlarından **Arazi Kalitesi (Terrain Quality)** ayarını Yüksek seviyesinde sabitleyin.",
                    "helpful_count": 46,
                    "created_at": "4 saat önce"
                }
            ]
        },
        {
            "game_slug": "red-dead-redemption-2",
            "author_name": "ArthurMorganTR",
            "author_avatar": "AM",
            "title": "RDR 2 Valentine kasabasına girerken ERR_GFX_STATE hatası alıyorum",
            "error_code": "ERR_GFX_STATE",
            "system_specs": "Windows 11 | Ryzen 5 7500F | RTX 4060 Ti | 32GB DDR5",
            "content": "Oyunu Vulkan'da oynuyorum, son NVIDIA sürücü güncellemesinden sonra kasabaya atla girerken ERR_GFX_STATE verip çöküyor.",
            "status": "OyunÇöz AI Çözümledi",
            "upvotes": 64,
            "views": 890,
            "created_at": "6 saat önce",
            "replies": [
                {
                    "author_name": "OyunÇöz AI (Teknik Analiz Motoru)",
                    "is_ai": 1,
                    "ai_mode": "Forum + AI Sentezi",
                    "content": "Ekran kartı sürücüsü güncellendiğinde RDR 2'nin eski Vulkan boru hattı (`sga_vulkan_final_init`) dosyaları geçersiz kalır ve `ERR_GFX_STATE` çökmesine yol açar.\n\n### 1 Dakikada Kesin Çözüm:\n1. `Belgeler\\Rockstar Games\\Red Dead Redemption 2\\Settings` klasörünü açın.\n2. **`sga_`** ile başlayan 3 önbellek dosyasını silin (`system.xml` dosyasını silmeyin).\n3. Steam başlatma seçeneklerine `-ignorepipelinecache` parametresini ekleyin.",
                    "helpful_count": 59,
                    "created_at": "6 saat önce"
                }
            ]
        },
        {
            "game_slug": "black-myth-wukong",
            "author_name": "DestinedOne",
            "author_avatar": "DO",
            "title": "Black Myth: Wukong açılırken Shader Compilation %42'de Out of Video Memory veriyor",
            "error_code": "UE5-SHADER-OOM",
            "system_specs": "Windows 11 | i7-14700K | RTX 4070 Super 12GB | 32GB DDR5",
            "content": "Ekran kartımda 12GB VRAM var ama daha oyunun menüsüne bile gelemeden gölgelendirici derlemesinde Out of Video Memory hatası alıyorum.",
            "status": "OyunÇöz AI Çözümledi",
            "upvotes": 48,
            "views": 690,
            "created_at": "8 saat önce",
            "replies": [
                {
                    "author_name": "OyunÇöz AI (Teknik Analiz Motoru)",
                    "is_ai": 1,
                    "ai_mode": "Forum + AI Sentezi",
                    "content": "**i7-14700K** işlemcinizde Unreal Engine 5 gölgelendirici derlemesi (Oodle decompression) sırasında oluşan yüksek AVX yükü, sahte `Out of Video Memory` hatası fırlatmaktadır (sorun RTX 4070 Super'de değildir!).\n\n### Çözüm:\n1. Denetim Masası -> **Güç Seçenekleri** menüsünden güç planını geçici olarak **Güç Tasarrufu (Power Saver)** moduna alın.\n2. Oyunu açıp %100 Shader Compilation işleminin tamamlanmasını bekleyin (yaklaşık 2 dakika sürer).\n3. Ana menü açıldıktan sonra güç planınızı tekrar **Dengeli / Yüksek Performans** moduna alabilirsiniz. Ayrıca anakartınızın en güncel `0x12B` mikro kodlu BIOS güncellemesini yapmanız kalıcı olarak bu hatayı önler.",
                    "helpful_count": 44,
                    "created_at": "8 saat önce"
                }
            ]
        }
    ]

    for t in threads_data:
        cursor.execute("""
            INSERT INTO threads (game_slug, author_name, author_avatar, title, error_code, system_specs, content, status, upvotes, views, created_at)
            VALUES (:game_slug, :author_name, :author_avatar, :title, :error_code, :system_specs, :content, :status, :upvotes, :views, :created_at)
        """, {k: v for k, v in t.items() if k != "replies"})
        thread_id = cursor.lastrowid
        for r in t["replies"]:
            cursor.execute("""
                INSERT INTO replies (thread_id, author_name, is_ai, ai_mode, content, helpful_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (thread_id, r["author_name"], r["is_ai"], r["ai_mode"], r["content"], r["helpful_count"], r["created_at"]))


if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()
    print("Database re-initialized with 12 games, users, and votes tables at:", DB_PATH)
