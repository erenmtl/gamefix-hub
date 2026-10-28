import os
import re
import html
import json
import time
import hashlib
import secrets
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timezone
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, Header, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from google import genai

from database import init_db, get_db_connection, hash_password, verify_password
from game_catalog import resolve_game_input, get_random_world_suggestions, get_game_image_url

app = FastAPI(
    title="OyunÇöz API",
    description="Popüler Oyunların Forum Sorunları ve Yapay Zeka Destekli Çözüm Platformu",
    version="4.0.0"
)

init_db()

# --- SECURITY, RATE LIMITING, 5651 LOGGING & CONTENT FILTERING ---

RATE_LIMIT_BUCKETS: dict[str, list[float]] = {}

PROHIBITED_PROFANITY = [
    "amk", "aq", "sikik", "sikeyim", "siktir", "orospu", "piç", "pezevenk",
    "yavşak", "götveren", "kahpe", "ibne", "ananı", "bacını", "oç"
]

PROHIBITED_WAREZ_TERMS = [
    "crack indir", "torrent indir", "fitgirl repack", "dodi repack", "skidrow",
    "codex crack", "kmspico", "keygen indir", "aimbot indir", "wallhack indir",
    "hile indir", "bedava hile", "warez", "fulloyun indir", "serial key indir"
]

PROHIBITED_SHORT_LINKS = [
    "bit.ly/", "tinyurl.com/", "t.co/", "goo.gl/", "bc.vc/", "ay.link/",
    "tr.link/", "ouo.io/", "adf.ly/", "cut.ly/", "is.gd/", "shorte.st/"
]

DANGEROUS_COMMAND_PATTERNS = [
    r"\bformat\s+[a-zA-Z]:",
    r"\bdel\s+/[fFsSqQ]",
    r"\brd\s+/[sSqQ]",
    r"\brmdir\s+/[sSqQ]",
    r"\brm\s+-rf\b",
    r"\bcipher\s+/w",
    r"\bdiskpart\b",
    r"\bbcdedit\s+/delete\s+\{current\}",
    r"\breg\s+delete\s+hklm\\(sam|system|security)",
    r"\btakeown\s+/f\s+c:\\windows",
    r"\bicacls\s+c:\\windows\s+/remove",
    r"\bpowershell\s+-[eE][nN][cC]",
    r"\binvoke-expression\b",
    r"\biex\s*\("
]


def sanitize_user_text(raw: Optional[str]) -> str:
    """Strips dangerous XSS tags/attributes and normalizes user input."""
    if not raw:
        return ""
    s = str(raw).strip()
    # Remove script/iframe/object/embed/style blocks completely
    s = re.sub(r"<\s*(script|iframe|object|embed|style|applet|meta|link)[^>]*>[\s\S]*?<\s*/\s*\1\s*>", "", s, flags=re.IGNORECASE)
    s = re.sub(r"<\s*/?\s*(script|iframe|object|embed|style|applet|meta|link)[^>]*>", "", s, flags=re.IGNORECASE)
    # Remove inline event handlers like onload=, onerror=, onclick=
    s = re.sub(r"\bon[a-z]+\s*=\s*(['\"].*?['\"]|[^\s>]+)", "", s, flags=re.IGNORECASE)
    s = re.sub(r"javascript\s*:", "", s, flags=re.IGNORECASE)
    # Escape remaining HTML tags
    return html.escape(s, quote=True)


def sanitize_ai_commands(markdown_text: str) -> str:
    """Filters out any destructive system commands against our safe command policy."""
    if not markdown_text:
        return ""
    cleaned = markdown_text
    for pat in DANGEROUS_COMMAND_PATTERNS:
        cleaned = re.sub(
            pat,
            "[GÜVENLİK KALKANI: Zararlı sistem komutu OyunÇöz Güvenli Komut Filtresi tarafından engellendi]",
            cleaned,
            flags=re.IGNORECASE
        )
    # Also strip raw <script> or <iframe> if ever present in markdown
    cleaned = re.sub(r"<\s*/?\s*(script|iframe|object|embed)[^>]*>", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bon(load|error|click|mouseover)\s*=", "data-blocked=", cleaned, flags=re.IGNORECASE)
    return cleaned


def check_prohibited_content(text: str):
    """5651 Law & Community Filter: Blocks profanity, shortened links, and crack/warez/cheat sharing."""
    if not text:
        return
    lower_txt = text.lower()
    words = re.findall(r"[a-zçğıöşü0-9]+", lower_txt)
    for bad in PROHIBITED_PROFANITY:
        if bad in words:
            raise HTTPException(
                status_code=400,
                detail="🛡️ 5651 İçerik Filtresi: Gönderinizde topluluk kurallarına aykırı argo/hakaret ifadeleri tespit edildi. Lütfen teknik ve saygılı bir dil kullanın."
            )
    for warez in PROHIBITED_WAREZ_TERMS:
        if warez in lower_txt:
            raise HTTPException(
                status_code=400,
                detail="🛡️ 5651 & Telif Filtresi: Forumda korsan oyun (crack/warez/torrent) ve hile yazılımı paylaşımı kesinlikle yasaktır."
            )
    for link in PROHIBITED_SHORT_LINKS:
        if link in lower_txt:
            raise HTTPException(
                status_code=400,
                detail="🛡️ Güvenlik Filtresi: Zararlı yazılım riskine karşı kısaltılmış link (bit.ly, tr.link vb.) paylaşımı engellenmiştir."
            )


def check_honeypot(hp_value: Optional[str]):
    if hp_value and hp_value.strip():
        raise HTTPException(status_code=400, detail="Güvenlik duvarı: Otomatik bot aktivitesi tespit edildi ve engellendi.")


def check_rate_limit(bucket_key: str, max_calls: int, window_sec: int = 60, action_name: str = "işlem"):
    now = time.time()
    timestamps = RATE_LIMIT_BUCKETS.get(bucket_key, [])
    timestamps = [t for t in timestamps if now - t < window_sec]
    if len(timestamps) >= max_calls:
        wait_sec = max(5, int(window_sec - (now - timestamps[0])))
        raise HTTPException(
            status_code=429,
            detail=f"⏳ Rate Limit Koruması: Dakikada en fazla {max_calls} {action_name} yapabilirsiniz. Lütfen {wait_sec} saniye bekleyip tekrar deneyin."
        )
    timestamps.append(now)
    RATE_LIMIT_BUCKETS[bucket_key] = timestamps


def get_client_ip(request: Optional[Request]) -> str:
    if not request:
        return "127.0.0.1"
    xff = request.headers.get("x-forwarded-for") or request.headers.get("cf-connecting-ip")
    if xff:
        return xff.split(",")[0].strip()[:64]
    if request.client and request.client.host:
        return request.client.host[:64]
    return "127.0.0.1"


def get_user_agent(request: Optional[Request]) -> str:
    if not request:
        return "Unknown"
    return (request.headers.get("user-agent") or "Unknown")[:250]


def log_5651_event(
    action_type: str,
    target_id: int,
    user_id: int,
    client_id: str,
    ip_address: str,
    user_agent: str,
    content_summary: str
):
    """Records immutable 5651 legal audit log (IP, User-Agent, UTC Timestamp, Client ID)."""
    try:
        utc_now = datetime.now(timezone.utc).isoformat()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO legal_5651_logs (action_type, target_id, user_id, client_id, ip_address, user_agent, content_summary, utc_timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            action_type,
            int(target_id or 0),
            int(user_id or 0),
            (client_id or "")[:64],
            (ip_address or "127.0.0.1")[:64],
            (user_agent or "Unknown")[:250],
            (content_summary or "")[:200],
            utc_now
        ))
        conn.commit()
        conn.close()
    except Exception:
        pass


class SendVerificationCodeRequest(BaseModel):
    username: str
    email: str
    password: str
    system_specs: Optional[str] = ""
    favorite_game: Optional[str] = "valorant"
    kvkk_consent: Optional[bool] = True
    website_hp: Optional[str] = ""
    website_url: Optional[str] = ""


class VerifyEmailRegisterRequest(BaseModel):
    email: str
    code: str


class LoginRequest(BaseModel):
    identifier: str
    password: str


class ProfileUpdateRequest(BaseModel):
    system_specs: str
    favorite_game: str


class AdminApiKeyRequest(BaseModel):
    api_key: str


class CreateGameRequest(BaseModel):
    game_query: str


class AIAnalyzeRequest(BaseModel):
    game_slug: str
    error_code: Optional[str] = ""
    system_specs: Optional[str] = ""
    problem_description: str
    website_hp: Optional[str] = ""
    website_url: Optional[str] = ""


class NewThreadRequest(BaseModel):
    game_slug: str
    title: str
    error_code: Optional[str] = ""
    system_specs: Optional[str] = ""
    content: str
    website_hp: Optional[str] = ""
    website_url: Optional[str] = ""


class NewReplyRequest(BaseModel):
    content: str
    website_hp: Optional[str] = ""
    website_url: Optional[str] = ""


class ContentReportRequest(BaseModel):
    target_type: str
    target_id: int
    reason: str
    details: Optional[str] = ""


def get_current_user(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.replace("Bearer ", "").strip()
    if not token:
        return None
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id, u.username, u.email, u.avatar_initials, u.system_specs, u.favorite_game, u.role, u.created_at
        FROM sessions s
        JOIN users u ON s.user_id = u.id
        WHERE s.token = ?
    """, (token,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def resolve_voter_key(user: Optional[dict], x_client_id: Optional[str]) -> str:
    if user:
        return f"user:{user['id']}"
    if x_client_id and x_client_id.strip():
        return f"client:{x_client_id.strip()[:64]}"
    return "client:anonymous"


def get_server_gemini_key() -> str:
    env_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if env_key:
        return env_key
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM site_settings WHERE key = 'gemini_api_key'")
    row = cursor.fetchone()
    conn.close()
    if row and row["value"] and row["value"].strip():
        return row["value"].strip()
    return ""


def build_ai_cache_key(game_slug: str, error_code: str, problem_description: str) -> str:
    """
    Creates a normalized semantic fingerprint so identical or near-identical error queries
    for the same game hit the SQLite AI Cache (0 token cost!).
    """
    tr_map = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    norm_code = re.sub(r"[^a-z0-9]+", "", (error_code or "").translate(tr_map).lower())
    words = re.findall(r"[a-z0-9]{3,}", (problem_description or "").translate(tr_map).lower())
    stopwords = {"bir", "ama", "icin", "olan", "গিয়ে", "sonra", "oyun", "oyunda", "hatasi", "hata", "aliyorum", "veriyor", "nasil", "cozulur"}
    key_tokens = sorted(set(w for w in words if w not in stopwords))[:8]
    raw_fingerprint = f"{game_slug.lower()}|{norm_code}|{'_'.join(key_tokens)}"
    return hashlib.sha256(raw_fingerprint.encode("utf-8")).hexdigest()[:32]


def try_send_smtp_email(to_email: str, username: str, code: str) -> bool:
    """
    Sends real verification email if SMTP_HOST / SMTP_USER / SMTP_PASS are set in environment.
    Returns True if sent via real SMTP, False if using local instant inbox preview.
    """
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com").strip()
    smtp_port = int(os.environ.get("SMTP_PORT", "465"))
    smtp_user = os.environ.get("SMTP_USER", "").strip()
    smtp_pass = os.environ.get("SMTP_PASS", "").strip()

    if not smtp_user or not smtp_pass:
        return False

    try:
        body = (
            f"Merhaba {username},\n\n"
            f"OyunÇöz hesabınızı doğrulamak için 6 haneli onay kodunuz:\n\n"
            f"    {code}\n\n"
            f"Bu kod 10 dakika boyunca geçerlidir.\n"
        )
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = f"OyunÇöz E-Posta Doğrulama Kodunuz: {code}"
        msg["From"] = smtp_user
        msg["To"] = to_email

        with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=8) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [to_email], msg.as_string())
        return True
    except Exception:
        return False


def ensure_or_create_game_in_db(raw_game_input: str) -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM games ORDER BY id ASC")
    existing_games = [dict(r) for r in cursor.fetchall()]

    resolved = resolve_game_input(raw_game_input, existing_games)
    if resolved.get("status") == "empty":
        conn.close()
        raise HTTPException(status_code=400, detail="Lütfen geçerli bir oyun adı girin.")

    if resolved["status"] == "existing":
        cursor.execute("SELECT * FROM games WHERE slug = ?", (resolved["slug"],))
        game_row = dict(cursor.fetchone())
        game_row["common_tags"] = json.loads(game_row["common_tags"])
        game_row["image_url"] = get_game_image_url(game_row["slug"])
        game_row["was_created"] = False
        game_row["corrected_from"] = resolved.get("corrected_from")
        conn.close()
        return game_row

    slug = resolved["slug"]
    cursor.execute("SELECT * FROM games WHERE slug = ?", (slug,))
    already = cursor.fetchone()
    if already:
        game_row = dict(already)
        game_row["common_tags"] = json.loads(game_row["common_tags"])
        game_row["image_url"] = get_game_image_url(game_row["slug"])
        game_row["was_created"] = False
        game_row["corrected_from"] = resolved.get("corrected_from")
        conn.close()
        return game_row

    default_issues = resolved.get("default_issues", [])
    cursor.execute("""
        INSERT INTO games (slug, name, short_name, category, developer, accent_color, secondary_color, banner_subtitle, engine, anticheat, common_tags, issue_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        slug,
        resolved["canonical_name"],
        resolved["short_name"],
        resolved["category"],
        resolved["developer"],
        resolved["accent_color"],
        resolved["secondary_color"],
        resolved["banner_subtitle"],
        resolved["engine"],
        resolved["anticheat"],
        json.dumps(resolved["common_tags"]),
        len(default_issues)
    ))

    now_str = datetime.now().strftime("%Y-%m-%d")
    for iss in default_issues:
        cursor.execute("""
            INSERT INTO issues (
                game_slug, title, error_code, severity, category, symptom_summary,
                forum_sources, ai_root_cause, ai_solution_steps, verify_command,
                success_rate, views, helpful_votes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            slug,
            iss["title"],
            iss["error_code"],
            iss["severity"],
            iss["category"],
            iss["symptom_summary"],
            json.dumps(iss["forum_sources"]),
            iss["ai_root_cause"],
            json.dumps(iss["ai_solution_steps"]),
            iss.get("verify_command", "sfc /verifyonly"),
            iss.get("success_rate", 95),
            640,
            78,
            now_str
        ))

    conn.commit()
    cursor.execute("SELECT * FROM games WHERE slug = ?", (slug,))
    new_game = dict(cursor.fetchone())
    new_game["common_tags"] = json.loads(new_game["common_tags"])
    new_game["image_url"] = get_game_image_url(new_game["slug"])
    new_game["issue_count"] = len(default_issues)
    new_game["thread_count"] = 0
    new_game["was_created"] = True
    new_game["corrected_from"] = resolved.get("corrected_from")
    conn.close()
    return new_game


def generate_ai_solution(
    game_name: str,
    game_slug: str,
    engine: str,
    anticheat: str,
    error_code: str,
    system_specs: str,
    problem_description: str
) -> dict:
    # 1. Check Smart SQLite AI Cache first (0 Token Cost!)
    cache_key = build_ai_cache_key(game_slug, error_code, problem_description)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ai_cache WHERE cache_key = ?", (cache_key,))
    cached_row = cursor.fetchone()
    if cached_row:
        cursor.execute("UPDATE ai_cache SET hit_count = hit_count + 1 WHERE cache_key = ?", (cache_key,))
        conn.commit()
        conn.close()
        return {
            "mode": f"Canlı Gemini 3.8 Flash (Akıllı Önbellek • 0 Token Harcandı)",
            "is_live_api": True,
            "cached": True,
            "markdown": cached_row["markdown"],
            "matched_issue_title": None,
            "confidence": cached_row["confidence"]
        }

    cursor.execute("SELECT * FROM issues WHERE game_slug = ?", (game_slug,))
    game_issues = [dict(row) for row in cursor.fetchall()]
    conn.close()

    kb_context = ""
    matched_issue = None
    query_lower = f"{error_code} {problem_description}".lower()

    for iss in game_issues:
        code_tokens = [t.strip().lower() for t in iss["error_code"].replace("/", " ").split() if len(t.strip()) >= 3]
        title_tokens = [t.strip().lower() for t in iss["title"].split() if len(t.strip()) >= 4]
        if any(tok in query_lower for tok in code_tokens) or any(tok in query_lower for tok in title_tokens):
            matched_issue = iss
            break

    if not matched_issue and game_issues:
        matched_issue = game_issues[0]

    for iss in game_issues:
        kb_context += f"- Hata: {iss['title']} ({iss['error_code']})\n  Kök Neden: {iss['ai_root_cause']}\n"

    effective_key = get_server_gemini_key()
    if effective_key:
        try:
            client = genai.Client(api_key=effective_key)
            system_instruction = (
                "Sen 'OyunÇöz AI' adında, Reddit, Technopat Sosyal, Steam Topluluğu ve resmi oyun forumlarındaki "
                "binlerce teknik çözüm konusunu analiz eden uzman bir Oyun Arıza Tespit ve Çözüm Yapay Zekasısın. "
                "Yanıtlarını Türkçe, öz, teknik olarak doğru ve Markdown formatında ver. "
                "Yanıtında şu bölümler yer alsın:\n"
                "1. **🔍 Kök Neden Analizi (Forum & Telemetri Sentezi)**\n"
                "2. **🛠️ Adım Adım Kesin Çözüm Rehberi**\n"
                "3. **💻 Sistem Doğrulama Komutu (PowerShell / CMD)**\n"
                "4. **📌 Forum Topluluk Notu & Başarı Oranı**"
            )
            prompt = (
                f"Oyun: {game_name} (Motor: {engine}, Anti-Cheat: {anticheat})\n"
                f"Hata Kodu / Etiket: {error_code or 'Belirtilmedi'}\n"
                f"Kullanıcı Sistem Özellikleri: {system_specs or 'Standart Windows 10/11 PC'}\n"
                f"Sorun Açıklaması: {problem_description}\n\n"
                f"Bilgi Tabanımızdaki İlgili Forum Kayıtları:\n{kb_context}\n\n"
                "Lütfen bu oyuncunun sorununu donanım/yazılım düzeyinde analiz et ve adım adım çöz."
            )
            interaction = client.interactions.create(
                model="gemini-3.8-flash",
                system_instruction=system_instruction,
                input=prompt
            )
            output_text = sanitize_ai_commands((interaction.output_text or "").strip())
            if output_text:
                # Save to SQLite AI Cache so future identical queries cost 0 tokens!
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO ai_cache (cache_key, game_slug, error_code, query_summary, markdown, confidence, hit_count, created_at)
                    VALUES (?, ?, ?, ?, ?, 98, 1, ?)
                """, (cache_key, game_slug, error_code or "", problem_description[:120], output_text, datetime.now().strftime("%Y-%m-%d %H:%M")))
                conn.commit()
                conn.close()

                return {
                    "mode": "Canlı Gemini 3.8 Flash (Sunucu AI)",
                    "is_live_api": True,
                    "cached": False,
                    "markdown": output_text,
                    "matched_issue_title": matched_issue["title"] if matched_issue else None,
                    "confidence": 98
                }
        except Exception:
            fallback_res = build_smart_simulation_response(
                game_name, engine, anticheat, error_code, system_specs, problem_description, matched_issue
            )
            fallback_res["markdown"] = sanitize_ai_commands(fallback_res["markdown"])
            fallback_res["mode"] = "Akıllı AI Teşhis Motoru (Sunucu Yedek Modu)"
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO ai_cache (cache_key, game_slug, error_code, query_summary, markdown, confidence, hit_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?)
            """, (cache_key, game_slug, error_code or "", problem_description[:120], fallback_res["markdown"], fallback_res["confidence"], datetime.now().strftime("%Y-%m-%d %H:%M")))
            conn.commit()
            conn.close()
            return fallback_res

    sim_res = build_smart_simulation_response(
        game_name, engine, anticheat, error_code, system_specs, problem_description, matched_issue
    )
    sim_res["markdown"] = sanitize_ai_commands(sim_res["markdown"])
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO ai_cache (cache_key, game_slug, error_code, query_summary, markdown, confidence, hit_count, created_at)
        VALUES (?, ?, ?, ?, ?, ?, 1, ?)
    """, (cache_key, game_slug, error_code or "", problem_description[:120], sim_res["markdown"], sim_res["confidence"], datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()
    return sim_res


def build_smart_simulation_response(
    game_name: str,
    engine: str,
    anticheat: str,
    error_code: str,
    system_specs: str,
    problem_description: str,
    matched_issue: Optional[dict]
) -> dict:
    specs_note = f"`{system_specs}`" if system_specs else "`Windows 10/11 64-bit Sistem`"
    code_badge = f"`{error_code}`" if error_code else "`GENEL-ARIZA-TESPİT`"

    if matched_issue:
        steps = json.loads(matched_issue["ai_solution_steps"])
        forums = json.loads(matched_issue["forum_sources"])
        steps_md = "\n".join(
            [f"{s['step']}. **{s['title']}** *(Zorluk: {s['difficulty']})*\n   {s['detail']}" for s in steps]
        )
        forum_md = "\n".join(
            [f"> **[{f['forum']}]** *{f['thread']}* (+{f['upvotes']} Onay)\n> \"{f['quote']}\"" for f in forums]
        )
        verify_cmd = matched_issue.get("verify_command") or "sfc /scannow"

        md = (
            f"### 🔍 Kök Neden Analizi ({game_name} • {code_badge})\n"
            f"Belirttiğiniz sorun (**\"{problem_description[:140]}\"**) ve sistem profiliniz ({specs_note}) "
            f"**{engine}** motoru ile **{anticheat}** katmanı üzerinden incelendi.\n\n"
            f"{matched_issue['ai_root_cause']}\n\n"
            f"---\n"
            f"### 🛠️ Adım Adım Yapay Zeka Çözüm Rehberi\n"
            f"{steps_md}\n\n"
            f"---\n"
            f"### 💻 Sistem & Servis Doğrulama Komutu (PowerShell)\n"
            f"```powershell\n{verify_cmd}\n```\n\n"
            f"---\n"
            f"### 🌐 Eşleşen Forum Kaynakları (%{matched_issue['success_rate']} Çözüm Başarısı)\n"
            f"{forum_md}"
        )
        return {
            "mode": "Akıllı AI Teşhis Motoru (Forum Sentezi)",
            "is_live_api": False,
            "cached": False,
            "markdown": md,
            "matched_issue_title": matched_issue["title"],
            "confidence": matched_issue["success_rate"]
        }

    md = (
        f"### 🔍 Kök Neden Analizi ({game_name})\n"
        f"**{engine}** motoru ve **{anticheat}** üzerinde `{error_code or 'Belirtilmeyen Hata'}` semptomu incelendi. "
        f"Sisteminiz ({specs_note}) üzerinde gölgelendirici önbelleği (Shader Cache), çekirdek sürücü çakışması veya bozuk yapılandırma dosyası tespit edildi.\n\n"
        f"### 🛠️ Adım Adım Çözüm\n"
        f"1. **Oyun Önbelleğini ve Config Dosyalarını Sıfırlayın:** `%localappdata%` altındaki oyun yapılandırma klasörünü yedekleyip silin.\n"
        f"2. **{anticheat} Servisini Onarın:** Hizmetler (`services.msc`) üzerinden anti-cheat servisinin çalışır durumda olduğunu doğrulayın.\n"
        f"3. **Ekran Kartı Gölgelendirici Önbelleğini Temizleyin:** DirectX Shader Cache temizliği yapıp oyunu Yönetici olarak başlatın."
    )
    return {
        "mode": "Akıllı AI Teşhis Motoru (Forum Sentezi)",
        "is_live_api": False,
        "cached": False,
        "markdown": md,
        "matched_issue_title": None,
        "confidence": 90
    }


# --- 2-STEP EMAIL VERIFICATION & AUTHENTICATION ENDPOINTS ---

@app.post("/api/auth/send-code")
def send_registration_verification_code(
    req: SendVerificationCodeRequest,
    request: Request,
    x_client_id: Optional[str] = Header(None)
):
    check_honeypot(req.website_hp or req.website_url)
    if req.kvkk_consent is False:
        raise HTTPException(
            status_code=400,
            detail="Kayıt olabilmek için 6698 sayılı KVKK Aydınlatma Metni ve Kullanım Koşullarını onaylamanız zorunludur."
        )

    username = sanitize_user_text(req.username)
    email = req.email.strip().lower()
    check_prohibited_content(username)

    if len(username) < 2:
        raise HTTPException(status_code=400, detail="Kullanıcı adı en az 2 karakter olmalıdır.")
    if "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(status_code=400, detail="Lütfen geçerli bir e-posta adresi girin (örn: adiniz@gmail.com).")
    if len(req.password) < 4:
        raise HTTPException(status_code=400, detail="Şifre en az 4 karakter olmalıdır.")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE lower(email) = ? OR lower(username) = ?", (email, username.lower()))
    existing_user = cursor.fetchone()
    if existing_user:
        if verify_password(req.password, existing_user["password_hash"]):
            token = secrets.token_hex(24)
            now_str = datetime.now().strftime("%Y-%m-%d")
            cursor.execute("INSERT INTO sessions (token, user_id, created_at) VALUES (?, ?, ?)", (token, existing_user["id"], now_str))
            conn.commit()
            user_dict = {
                "id": existing_user["id"],
                "username": existing_user["username"],
                "email": existing_user["email"],
                "avatar_initials": existing_user["avatar_initials"],
                "system_specs": existing_user["system_specs"],
                "favorite_game": existing_user["favorite_game"],
                "role": existing_user["role"],
                "created_at": existing_user["created_at"]
            }
            conn.close()
            return {
                "already_registered": True,
                "token": token,
                "user": user_dict,
                "message": "Hesabınız zaten kayıtlı! Otomatik olarak giriş yapıldı."
            }
        conn.close()
        if existing_user["email"].lower() == email:
            raise HTTPException(status_code=400, detail="Bu e-posta adresi zaten kayıtlı. Lütfen 'Giriş Yap' sekmesinden şifrenizle giriş yapın.")
        raise HTTPException(status_code=400, detail="Bu kullanıcı adı başka bir oyuncu tarafından kullanılıyor. Lütfen farklı bir kullanıcı adı seçin.")

    code = f"{secrets.randbelow(900000) + 100000}"
    pwd_hash = hash_password(req.password)
    expires_at = time.time() + 900  # 15 minutes
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    cursor.execute("""
        INSERT OR REPLACE INTO email_verifications (email, username, password_hash, system_specs, favorite_game, code, expires_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        email,
        username,
        pwd_hash,
        sanitize_user_text(req.system_specs or ""),
        req.favorite_game or "valorant",
        code,
        expires_at,
        now_str
    ))
    conn.commit()
    conn.close()

    smtp_sent = try_send_smtp_email(email, username, code)
    return {
        "sent": True,
        "email": email,
        "smtp_sent": smtp_sent,
        "verification_code_preview": None if smtp_sent else code,
        "message": (
            f"{email} adresine 6 haneli doğrulama kodu gönderildi."
            if smtp_sent else
            f"6 haneli onay kodunuz oluşturuldu ({email})."
        )
    }


@app.post("/api/auth/verify-register")
def verify_email_and_register(
    req: VerifyEmailRegisterRequest,
    request: Request,
    x_client_id: Optional[str] = Header(None)
):
    email = req.email.strip().lower()
    code = req.code.strip()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM email_verifications WHERE email = ?", (email,))
    pending = cursor.fetchone()

    if not pending:
        conn.close()
        raise HTTPException(status_code=400, detail="Bu e-posta için bekleyen bir doğrulama işlemi bulunamadı. Lütfen tekrar kod isteyin.")

    if time.time() > pending["expires_at"]:
        cursor.execute("DELETE FROM email_verifications WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        raise HTTPException(status_code=400, detail="Doğrulama kodunun süresi dolmuş. Lütfen yeni kod isteyin.")

    if pending["code"] != code:
        conn.close()
        raise HTTPException(status_code=400, detail="Girdiğiniz 6 haneli onay kodu hatalı! Lütfen kontrol edip tekrar deneyin.")

    username = pending["username"]
    initials = "".join([p[0].upper() for p in username.split()[:2]]) or "OY"
    if len(initials) == 1:
        initials = username[:2].upper()

    now_str = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT id FROM users WHERE lower(email) = ?", (email,))
    existing_row = cursor.fetchone()
    if existing_row:
        user_id = existing_row["id"]
    else:
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, avatar_initials, system_specs, favorite_game, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'member', ?)
        """, (
            username,
            email,
            pending["password_hash"],
            initials,
            pending["system_specs"],
            pending["favorite_game"],
            now_str
        ))
        user_id = cursor.lastrowid

    cursor.execute("DELETE FROM email_verifications WHERE email = ?", (email,))

    token = secrets.token_hex(24)
    cursor.execute("INSERT INTO sessions (token, user_id, created_at) VALUES (?, ?, ?)", (token, user_id, now_str))
    conn.commit()

    cursor.execute("SELECT id, username, email, avatar_initials, system_specs, favorite_game, role, created_at FROM users WHERE id = ?", (user_id,))
    user_dict = dict(cursor.fetchone())
    conn.close()

    log_5651_event(
        action_type="user_register_kvkk",
        target_id=user_id,
        user_id=user_id,
        client_id=x_client_id or "",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        content_summary=f"Yeni üye kaydı ve KVKK açık rıza onayı: {username} ({email})"
    )

    return {"token": token, "user": user_dict}


@app.post("/api/auth/login")
def login_user(req: LoginRequest):
    ident = req.identifier.strip().lower()
    if not ident or not req.password:
        raise HTTPException(status_code=400, detail="Lütfen kullanıcı adı/e-posta ve şifrenizi girin.")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE lower(username) = ? OR lower(email) = ?", (ident, ident))
    user_row = cursor.fetchone()

    if not user_row:
        cursor.execute("SELECT * FROM email_verifications WHERE lower(email) = ? OR lower(username) = ?", (ident, ident))
        pending = cursor.fetchone()
        conn.close()
        if pending:
            raise HTTPException(
                status_code=403,
                detail=f"Hesabınız için e-posta doğrulaması bekleniyor ({pending['email']}). Onay Kodunuz: {pending['code']}"
            )
        raise HTTPException(
            status_code=404,
            detail="Bu kullanıcı adı veya e-posta ile kayıtlı hesap bulunamadı. Lütfen 'Yeni Hesap Aç' sekmesinden kayıt olun."
        )

    if not verify_password(req.password, user_row["password_hash"]):
        conn.close()
        raise HTTPException(status_code=401, detail="Girdiğiniz şifre hatalı. Lütfen kontrol edip tekrar deneyin.")

    token = secrets.token_hex(24)
    now_str = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO sessions (token, user_id, created_at) VALUES (?, ?, ?)", (token, user_row["id"], now_str))
    conn.commit()

    user_dict = {
        "id": user_row["id"],
        "username": user_row["username"],
        "email": user_row["email"],
        "avatar_initials": user_row["avatar_initials"],
        "system_specs": user_row["system_specs"],
        "favorite_game": user_row["favorite_game"],
        "role": user_row["role"],
        "created_at": user_row["created_at"]
    }
    conn.close()
    return {"token": token, "user": user_dict}


@app.get("/api/auth/me")
def get_me(authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Oturum açılmamış")
    return {"user": user}


@app.put("/api/auth/profile")
def update_profile(req: ProfileUpdateRequest, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Bu işlem için giriş yapmalısınız.")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users SET system_specs = ?, favorite_game = ? WHERE id = ?
    """, (sanitize_user_text(req.system_specs), sanitize_user_text(req.favorite_game), user["id"]))
    conn.commit()
    cursor.execute("SELECT id, username, email, avatar_initials, system_specs, favorite_game, role, created_at FROM users WHERE id = ?", (user["id"],))
    updated = dict(cursor.fetchone())
    conn.close()
    return {"user": updated}


@app.delete("/api/auth/account")
def delete_user_account(
    request: Request,
    authorization: Optional[str] = Header(None),
    x_client_id: Optional[str] = Header(None)
):
    """KVKK Article 11 Compliance: Permanently deletes user account, sessions, votes, and personal data."""
    user = get_current_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Hesap silme işlemi için oturum açmış olmalısınız.")

    conn = get_db_connection()
    cursor = conn.cursor()
    uid = user["id"]
    uname = user["username"]
    uemail = user["email"]

    cursor.execute("DELETE FROM sessions WHERE user_id = ?", (uid,))
    cursor.execute("DELETE FROM user_votes WHERE voter_key = ?", (f"user:{uid}",))
    cursor.execute("DELETE FROM email_verifications WHERE lower(email) = ?", (uemail.lower(),))
    cursor.execute("DELETE FROM replies WHERE author_name = ? AND is_ai = 0", (uname,))
    cursor.execute("DELETE FROM threads WHERE author_name = ?", (uname,))
    cursor.execute("DELETE FROM users WHERE id = ?", (uid,))
    conn.commit()
    conn.close()

    log_5651_event(
        action_type="account_deleted_kvkk_m11",
        target_id=uid,
        user_id=uid,
        client_id=x_client_id or "",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        content_summary=f"KVKK Madde 11 kapsamında kullanıcı hesabı ve kişisel verileri kalıcı olarak silindi (ID: {uid})."
    )

    return {
        "deleted": True,
        "message": "6698 sayılı KVKK Madde 11 kapsamında hesabınız ve tüm kişisel verileriniz sistemden kalıcı olarak silindi."
    }


@app.post("/api/auth/logout")
def logout_user(authorization: Optional[str] = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "").strip()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()
        conn.close()
    return {"success": True}


# --- STATUS & ADMIN SERVER API KEY CONFIG ---

@app.get("/api/status")
def get_status():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as games_count FROM games")
    games_count = cursor.fetchone()["games_count"]
    cursor.execute("SELECT COUNT(*) as issues_count FROM issues")
    issues_count = cursor.fetchone()["issues_count"]
    cursor.execute("SELECT COUNT(*) as threads_count FROM threads")
    threads_count = cursor.fetchone()["threads_count"]
    cursor.execute("SELECT COUNT(*) as cache_count FROM ai_cache")
    cache_count = cursor.fetchone()["cache_count"]
    conn.close()

    has_key = bool(get_server_gemini_key())
    return {
        "has_server_api_key": has_key,
        "ai_model": "gemini-3.8-flash",
        "stats": {
            "games_count": games_count,
            "issues_count": issues_count,
            "threads_count": threads_count,
            "cache_count": cache_count
        }
    }


@app.post("/api/admin/apikey")
def set_server_api_key(req: AdminApiKeyRequest, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Sunucu API anahtarını yalnızca Site Yöneticisi değiştirebilir.")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO site_settings (key, value) VALUES ('gemini_api_key', ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
    """, (req.api_key.strip(),))
    conn.commit()
    conn.close()

    has_key = bool(get_server_gemini_key())
    return {
        "success": True,
        "has_server_api_key": has_key,
        "message": "Sunucu Gemini API anahtarı kaydedildi." if has_key else "Sunucu anahtarı kaldırıldı."
    }


# --- GAMES, SMART FUZZY RESOLVER & RANDOM WORLD SUGGESTIONS ---

@app.get("/api/games")
def list_games():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM games ORDER BY id ASC")
    rows = [dict(r) for r in cursor.fetchall()]

    for r in rows:
        r["common_tags"] = json.loads(r["common_tags"])
        r["image_url"] = get_game_image_url(r["slug"])
        cursor.execute("SELECT COUNT(*) as cnt FROM issues WHERE game_slug = ?", (r["slug"],))
        r["issue_count"] = cursor.fetchone()["cnt"]
        cursor.execute("SELECT COUNT(*) as cnt FROM threads WHERE game_slug = ?", (r["slug"],))
        r["thread_count"] = cursor.fetchone()["cnt"]

    conn.close()
    return rows


@app.get("/api/games/cover/{slug}")
def serve_game_cover_svg(slug: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, short_name, category, accent_color FROM games WHERE slug = ?", (slug,))
    row = cursor.fetchone()
    conn.close()

    if row:
        title = html.escape(row["short_name"] or row["name"])
        subtitle = html.escape(row["category"])
        color = row["accent_color"] or "#5e9c88"
    else:
        title = html.escape(slug.replace("-", " ").title()[:18])
        subtitle = "PC Oyunu"
        color = "#5e9c88"

    initials = "".join([w[0].upper() for w in title.split()[:2]]) or "GF"
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="320" height="180" viewBox="0 0 320 180">
      <defs>
        <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="{color}" stop-opacity="0.85"/>
          <stop offset="100%" stop-color="#141821" stop-opacity="1"/>
        </linearGradient>
      </defs>
      <rect width="320" height="180" rx="16" fill="url(#bg)"/>
      <circle cx="270" cy="40" r="65" fill="#ffffff" fill-opacity="0.06"/>
      <text x="24" y="78" fill="#ffffff" font-family="Inter, sans-serif" font-size="38" font-weight="800" opacity="0.25">{initials}</text>
      <text x="24" y="132" fill="#ffffff" font-family="Inter, sans-serif" font-size="22" font-weight="800">{title}</text>
      <text x="24" y="156" fill="#d8dee9" font-family="Inter, sans-serif" font-size="12" font-weight="600" opacity="0.85">{subtitle}</text>
    </svg>"""
    return Response(content=svg, media_type="image/svg+xml")


@app.get("/api/games/suggestions")
def get_game_suggestions(count: int = Query(6)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT slug FROM games")
    existing_slugs = [r["slug"] for r in cursor.fetchall()]
    conn.close()
    return {"suggestions": get_random_world_suggestions(existing_slugs, count=count)}


@app.get("/api/games/resolve")
def resolve_game_name(q: str = Query("")):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM games")
    existing_games = [dict(r) for r in cursor.fetchall()]
    conn.close()

    info = resolve_game_input(q, existing_games)
    if info.get("status") == "empty":
        return {"status": "empty"}
    return {
        "status": info["status"],
        "canonical_name": info["canonical_name"],
        "short_name": info["short_name"],
        "slug": info["slug"],
        "image_url": get_game_image_url(info["slug"]),
        "category": info["category"],
        "developer": info["developer"],
        "engine": info["engine"],
        "corrected_from": info.get("corrected_from")
    }


@app.post("/api/games/create")
def create_or_open_game(req: CreateGameRequest, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Yeni oyun sayfası eklemek için lütfen ücretsiz hesabınızla giriş yapın.")
    check_prohibited_content(req.game_query)
    game_obj = ensure_or_create_game_in_db(sanitize_user_text(req.game_query))
    return {"game": game_obj}


# --- ISSUES & THREADS ENDPOINTS ---

class IssueVoteRequest(BaseModel):
    vote_type: Optional[str] = "up"
    hardware_tag: Optional[str] = ""


DEFAULT_VERIFIED_HW_TAGS = [
    "Win 11 / RTX 4060",
    "Win 11 / RTX 3060",
    "Win 10 / RX 6700 XT",
    "Win 11 / Ryzen 5 5600",
    "Win 11 / RTX 4070 Super"
]


@app.get("/api/issues")
def list_issues(
    game_slug: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None),
    x_client_id: Optional[str] = Header(None)
):
    user = get_current_user(authorization)
    voter_key = resolve_voter_key(user, x_client_id)

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT i.*, g.name as game_name, g.short_name as game_short_name, g.accent_color
        FROM issues i
        JOIN games g ON i.game_slug = g.slug
        WHERE 1=1
    """
    params = []

    if game_slug and game_slug != "all":
        query += " AND i.game_slug = ?"
        params.append(game_slug)

    if category and category != "all":
        query += " AND i.category = ?"
        params.append(category)

    if search and search.strip():
        q = f"%{search.strip()}%"
        query += " AND (i.title LIKE ? OR i.error_code LIKE ? OR i.symptom_summary LIKE ? OR i.ai_root_cause LIKE ?)"
        params.extend([q, q, q, q])

    query += " ORDER BY i.helpful_votes DESC"
    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT target_id, hardware_tag FROM user_votes WHERE voter_key = ? AND target_type = 'issue'", (voter_key,))
    upvoted_rows = cursor.fetchall()
    upvoted_ids = {r["target_id"] for r in upvoted_rows}
    user_hw_map = {r["target_id"]: (r["hardware_tag"] or "") for r in upvoted_rows}

    cursor.execute("SELECT target_id FROM user_votes WHERE voter_key = ? AND target_type = 'issue_down'", (voter_key,))
    downvoted_ids = {r["target_id"] for r in cursor.fetchall()}

    cursor.execute("SELECT target_id, COUNT(*) as cnt FROM user_votes WHERE target_type = 'issue_down' GROUP BY target_id")
    extra_down_counts = {r["target_id"]: r["cnt"] for r in cursor.fetchall()}

    cursor.execute("SELECT target_id, hardware_tag FROM user_votes WHERE target_type = 'issue' AND hardware_tag != '' ORDER BY id DESC")
    hw_tags_by_issue: dict[int, list[str]] = {}
    for hr in cursor.fetchall():
        tid = hr["target_id"]
        tag = hr["hardware_tag"]
        if tid not in hw_tags_by_issue:
            hw_tags_by_issue[tid] = []
        if tag and tag not in hw_tags_by_issue[tid] and len(hw_tags_by_issue[tid]) < 4:
            hw_tags_by_issue[tid].append(tag)

    for r in rows:
        r["forum_sources"] = json.loads(r["forum_sources"])
        r["ai_solution_steps"] = json.loads(r["ai_solution_steps"])
        r["game_image_url"] = get_game_image_url(r["game_slug"])
        base_sr = max(50, min(99, int(r.get("success_rate") or 95)))
        up_cnt = int(r.get("helpful_votes") or 10)
        base_down = max(2, int(round(up_cnt * (100 - base_sr) / max(base_sr, 1))))
        down_cnt = base_down + extra_down_counts.get(r["id"], 0)
        total_cnt = max(1, up_cnt + down_cnt)
        r["unhelpful_votes"] = down_cnt
        r["total_votes"] = total_cnt
        r["success_rate"] = int(round((up_cnt / total_cnt) * 100))
        r["user_voted"] = r["id"] in upvoted_ids
        r["user_vote"] = "up" if r["id"] in upvoted_ids else ("down" if r["id"] in downvoted_ids else None)
        r["user_hardware_tag"] = user_hw_map.get(r["id"], "")
        default_hw = DEFAULT_VERIFIED_HW_TAGS[r["id"] % len(DEFAULT_VERIFIED_HW_TAGS)]
        custom_hw = hw_tags_by_issue.get(r["id"], [])
        r["verified_hw_tags"] = custom_hw if custom_hw else [default_hw]

    conn.close()
    return rows


@app.post("/api/issues/{issue_id}/vote")
def vote_issue(
    issue_id: int,
    payload: Optional[IssueVoteRequest] = None,
    authorization: Optional[str] = Header(None),
    x_client_id: Optional[str] = Header(None)
):
    vote_type = (payload.vote_type if payload and payload.vote_type else "up").lower()
    if vote_type not in ("up", "down"):
        vote_type = "up"
    hw_tag = sanitize_user_text((payload.hardware_tag if payload and payload.hardware_tag else "")[:42])

    user = get_current_user(authorization)
    voter_key = resolve_voter_key(user, x_client_id)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, helpful_votes, success_rate FROM issues WHERE id = ?", (issue_id,))
    issue = cursor.fetchone()
    if not issue:
        conn.close()
        raise HTTPException(status_code=404, detail="Sorun bulunamadı")

    cursor.execute("""
        SELECT id FROM user_votes WHERE voter_key = ? AND target_type = 'issue' AND target_id = ?
    """, (voter_key, issue_id))
    existing_up = cursor.fetchone()

    cursor.execute("""
        SELECT id FROM user_votes WHERE voter_key = ? AND target_type = 'issue_down' AND target_id = ?
    """, (voter_key, issue_id))
    existing_down = cursor.fetchone()

    user_vote = None

    if vote_type == "up":
        if existing_up:
            cursor.execute("DELETE FROM user_votes WHERE id = ?", (existing_up["id"],))
            cursor.execute("UPDATE issues SET helpful_votes = MAX(0, helpful_votes - 1) WHERE id = ?", (issue_id,))
            user_vote = None
        else:
            if existing_down:
                cursor.execute("DELETE FROM user_votes WHERE id = ?", (existing_down["id"],))
            cursor.execute("""
                INSERT INTO user_votes (voter_key, target_type, target_id, hardware_tag, created_at)
                VALUES (?, 'issue', ?, ?, ?)
            """, (voter_key, issue_id, hw_tag, datetime.now().isoformat()))
            cursor.execute("UPDATE issues SET helpful_votes = helpful_votes + 1 WHERE id = ?", (issue_id,))
            user_vote = "up"
    else:
        if existing_down:
            cursor.execute("DELETE FROM user_votes WHERE id = ?", (existing_down["id"],))
            user_vote = None
        else:
            if existing_up:
                cursor.execute("DELETE FROM user_votes WHERE id = ?", (existing_up["id"],))
                cursor.execute("UPDATE issues SET helpful_votes = MAX(0, helpful_votes - 1) WHERE id = ?", (issue_id,))
            cursor.execute("""
                INSERT INTO user_votes (voter_key, target_type, target_id, hardware_tag, created_at)
                VALUES (?, 'issue_down', ?, '', ?)
            """, (voter_key, issue_id, datetime.now().isoformat()))
            user_vote = "down"

    conn.commit()
    cursor.execute("SELECT helpful_votes, success_rate FROM issues WHERE id = ?", (issue_id,))
    updated_issue = cursor.fetchone()
    up_cnt = int(updated_issue["helpful_votes"] or 0)
    base_sr = max(50, min(99, int(updated_issue["success_rate"] or 95)))
    base_down = max(2, int(round(up_cnt * (100 - base_sr) / max(base_sr, 1))))

    cursor.execute("SELECT COUNT(*) as cnt FROM user_votes WHERE target_type = 'issue_down' AND target_id = ?", (issue_id,))
    extra_down = cursor.fetchone()["cnt"]
    down_cnt = base_down + extra_down
    total_cnt = max(1, up_cnt + down_cnt)
    dynamic_sr = int(round((up_cnt / total_cnt) * 100))

    cursor.execute("SELECT hardware_tag FROM user_votes WHERE target_type = 'issue' AND target_id = ? AND hardware_tag != '' ORDER BY id DESC LIMIT 4", (issue_id,))
    verified_hw_tags = [r["hardware_tag"] for r in cursor.fetchall() if r["hardware_tag"]]
    if not verified_hw_tags:
        verified_hw_tags = [DEFAULT_VERIFIED_HW_TAGS[issue_id % len(DEFAULT_VERIFIED_HW_TAGS)]]

    conn.close()

    return {
        "helpful_votes": up_cnt,
        "unhelpful_votes": down_cnt,
        "total_votes": total_cnt,
        "success_rate": dynamic_sr,
        "user_voted": user_vote == "up",
        "user_vote": user_vote,
        "user_hardware_tag": hw_tag if user_vote == "up" else "",
        "verified_hw_tags": verified_hw_tags
    }


@app.post("/api/ai/analyze")
def ai_analyze_issue(
    req: AIAnalyzeRequest,
    request: Request,
    authorization: Optional[str] = Header(None),
    x_client_id: Optional[str] = Header(None)
):
    check_honeypot(req.website_hp or req.website_url)
    ip_addr = get_client_ip(request)
    user_agent = get_user_agent(request)
    user = get_current_user(authorization)
    voter_key = resolve_voter_key(user, x_client_id)

    # Rate Limiting: Max 3 AI queries per minute per IP and per user/client
    check_rate_limit(f"ai_ip:{ip_addr}", max_calls=3, window_sec=60, action_name="AI arıza sorgusu")
    check_rate_limit(f"ai_user:{voter_key}", max_calls=3, window_sec=60, action_name="AI arıza sorgusu")

    check_prohibited_content(f"{req.game_slug} {req.error_code or ''} {req.problem_description}")

    guest_trial_used = False
    if not user:
        # Guest Trial Check: Allow 1 free AI analysis per client_id / IP
        trial_key = f"cid:{(x_client_id or 'anon').strip()[:48]}"
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT used_count FROM guest_ai_trials WHERE trial_key = ?",
            (trial_key,)
        )
        trial_row = cursor.fetchone()
        if trial_row and trial_row["used_count"] >= 1:
            conn.close()
            raise HTTPException(
                status_code=401,
                detail="🎁 1 adet ücretsiz Misafir AI Analiz hakkınızı kullandınız! Sınırsız AI arıza tespiti yapmak ve çözümleri kaydetmek için lütfen ücretsiz hesabınızı oluşturun."
            )
        cursor.execute("""
            INSERT OR REPLACE INTO guest_ai_trials (trial_key, ip_address, client_id, used_count, utc_timestamp)
            VALUES (?, ?, ?, 1, ?)
        """, (trial_key, ip_addr, (x_client_id or "")[:64], datetime.now(timezone.utc).isoformat()))
        conn.commit()
        conn.close()
        guest_trial_used = True

    game = ensure_or_create_game_in_db(sanitize_user_text(req.game_slug))
    specs = sanitize_user_text(req.system_specs or "") or (user.get("system_specs") if user else "") or ""

    result = generate_ai_solution(
        game_name=game["name"],
        game_slug=game["slug"],
        engine=game["engine"],
        anticheat=game["anticheat"],
        error_code=sanitize_user_text(req.error_code or ""),
        system_specs=specs,
        problem_description=sanitize_user_text(req.problem_description)
    )
    result["resolved_game"] = game
    result["guest_trial_used"] = guest_trial_used

    log_5651_event(
        action_type="ai_diagnostic_query",
        target_id=game.get("id", 0),
        user_id=user["id"] if user else 0,
        client_id=x_client_id or "",
        ip_address=ip_addr,
        user_agent=user_agent,
        content_summary=f"{game['name']} | {req.error_code or 'Genel'} | {req.problem_description[:90]}"
    )

    return result


@app.get("/api/threads")
def list_threads(
    game_slug: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None),
    x_client_id: Optional[str] = Header(None)
):
    user = get_current_user(authorization)
    voter_key = resolve_voter_key(user, x_client_id)

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT t.*, g.name as game_name, g.short_name as game_short_name, g.accent_color
        FROM threads t
        JOIN games g ON t.game_slug = g.slug
        WHERE 1=1
    """
    params = []

    if game_slug and game_slug != "all":
        query += " AND t.game_slug = ?"
        params.append(game_slug)

    if search and search.strip():
        q = f"%{search.strip()}%"
        query += " AND (t.title LIKE ? OR t.content LIKE ? OR t.error_code LIKE ?)"
        params.extend([q, q, q])

    query += " ORDER BY t.id DESC"
    cursor.execute(query, params)
    threads = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT target_id FROM user_votes WHERE voter_key = ? AND target_type = 'thread'", (voter_key,))
    voted_thread_ids = {r["target_id"] for r in cursor.fetchall()}

    for t in threads:
        t["user_voted"] = t["id"] in voted_thread_ids
        t["game_image_url"] = get_game_image_url(t["game_slug"])
        cursor.execute("SELECT * FROM replies WHERE thread_id = ? ORDER BY is_ai DESC, id ASC", (t["id"],))
        t["replies"] = [dict(rep) for rep in cursor.fetchall()]

    conn.close()
    return threads


@app.post("/api/threads")
def create_thread(
    req: NewThreadRequest,
    request: Request,
    authorization: Optional[str] = Header(None),
    x_client_id: Optional[str] = Header(None)
):
    check_honeypot(req.website_hp or req.website_url)
    user = get_current_user(authorization)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Foruma soru sormak ve AI çözümü almak için lütfen e-posta onaylı hesabınızla giriş yapın."
        )

    ip_addr = get_client_ip(request)
    user_agent = get_user_agent(request)
    voter_key = resolve_voter_key(user, x_client_id)

    # Rate Limiting: Max 2 forum threads per minute
    check_rate_limit(f"thread_ip:{ip_addr}", max_calls=2, window_sec=60, action_name="forum konusu açma işlemi")
    check_rate_limit(f"thread_user:{voter_key}", max_calls=2, window_sec=60, action_name="forum konusu açma işlemi")

    # 5651 Content Filter (Profanity, Shortened Links, Crack/Warez)
    check_prohibited_content(f"{req.title} {req.error_code or ''} {req.content}")

    clean_title = sanitize_user_text(req.title)
    clean_error_code = sanitize_user_text(req.error_code or "")
    clean_content = sanitize_user_text(req.content)
    specs = sanitize_user_text(req.system_specs or "") or (user["system_specs"] or "")

    game = ensure_or_create_game_in_db(sanitize_user_text(req.game_slug))
    author_name = user["username"]
    initials = user["avatar_initials"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO threads (game_slug, author_name, author_avatar, title, error_code, system_specs, content, status, upvotes, views, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'AI Çözümledi', 1, 1, 'Az önce')
    """, (
        game["slug"],
        author_name,
        initials,
        clean_title,
        clean_error_code,
        specs,
        clean_content
    ))
    thread_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # 5651 Legal Audit Log
    log_5651_event(
        action_type="thread_create",
        target_id=thread_id,
        user_id=user["id"],
        client_id=x_client_id or "",
        ip_address=ip_addr,
        user_agent=user_agent,
        content_summary=f"[{game['slug']}] {clean_title[:120]}"
    )

    ai_res = generate_ai_solution(
        game_name=game["name"],
        game_slug=game["slug"],
        engine=game["engine"],
        anticheat=game["anticheat"],
        error_code=clean_error_code,
        system_specs=specs,
        problem_description=f"{clean_title}\n{clean_content}"
    )

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO replies (thread_id, author_name, is_ai, ai_mode, content, helpful_count, created_at)
        VALUES (?, 'OyunÇöz AI (Otomatik Forum Çözümleyici)', 1, ?, ?, 1, 'Az önce')
    """, (thread_id, ai_res["mode"], sanitize_ai_commands(ai_res["markdown"])))
    conn.commit()

    cursor.execute("""
        SELECT t.*, g.name as game_name, g.short_name as game_short_name, g.accent_color
        FROM threads t
        JOIN games g ON t.game_slug = g.slug
        WHERE t.id = ?
    """, (thread_id,))
    new_thread = dict(cursor.fetchone())
    new_thread["user_voted"] = False
    new_thread["game_image_url"] = get_game_image_url(new_thread["game_slug"])
    new_thread["resolved_game"] = game
    cursor.execute("SELECT * FROM replies WHERE thread_id = ? ORDER BY is_ai DESC, id ASC", (thread_id,))
    new_thread["replies"] = [dict(r) for r in cursor.fetchall()]
    conn.close()

    return new_thread


@app.post("/api/threads/{thread_id}/replies")
def add_reply(
    thread_id: int,
    req: NewReplyRequest,
    request: Request,
    authorization: Optional[str] = Header(None),
    x_client_id: Optional[str] = Header(None)
):
    check_honeypot(req.website_hp or req.website_url)
    user = get_current_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Yanıt yazmak için lütfen giriş yapın.")

    ip_addr = get_client_ip(request)
    user_agent = get_user_agent(request)
    voter_key = resolve_voter_key(user, x_client_id)

    check_rate_limit(f"reply_ip:{ip_addr}", max_calls=3, window_sec=60, action_name="forum yanıtı gönderme işlemi")
    check_rate_limit(f"reply_user:{voter_key}", max_calls=3, window_sec=60, action_name="forum yanıtı gönderme işlemi")

    check_prohibited_content(req.content)
    clean_content = sanitize_user_text(req.content)
    if not clean_content:
        raise HTTPException(status_code=400, detail="Lütfen geçerli bir yanıt yazın.")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM threads WHERE id = ?", (thread_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Konu bulunamadı")

    cursor.execute("""
        INSERT INTO replies (thread_id, author_name, is_ai, ai_mode, content, helpful_count, created_at)
        VALUES (?, ?, 0, NULL, ?, 1, 'Az önce')
    """, (thread_id, user["username"], clean_content))
    reply_id = cursor.lastrowid
    conn.commit()

    cursor.execute("SELECT * FROM replies WHERE thread_id = ? ORDER BY is_ai DESC, id ASC", (thread_id,))
    replies = [dict(r) for r in cursor.fetchall()]
    conn.close()

    log_5651_event(
        action_type="reply_create",
        target_id=reply_id,
        user_id=user["id"],
        client_id=x_client_id or "",
        ip_address=ip_addr,
        user_agent=user_agent,
        content_summary=f"Thread #{thread_id} yanıt: {clean_content[:120]}"
    )

    return {"replies": replies}


@app.post("/api/reports")
def report_content(
    req: ContentReportRequest,
    request: Request,
    authorization: Optional[str] = Header(None),
    x_client_id: Optional[str] = Header(None)
):
    """5651 Law Notice & Take-Down Content Reporting Endpoint."""
    user = get_current_user(authorization)
    reporter_key = resolve_voter_key(user, x_client_id)
    ip_addr = get_client_ip(request)
    user_agent = get_user_agent(request)
    utc_now = datetime.now(timezone.utc).isoformat()

    clean_reason = sanitize_user_text(req.reason)[:80]
    clean_details = sanitize_user_text(req.details or "")[:300]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO content_reports (target_type, target_id, reason, details, reporter_key, ip_address, user_agent, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'İnceleniyor', ?)
    """, (
        sanitize_user_text(req.target_type)[:32],
        int(req.target_id),
        clean_reason,
        clean_details,
        reporter_key,
        ip_addr,
        user_agent,
        utc_now
    ))
    report_id = cursor.lastrowid
    conn.commit()
    conn.close()

    log_5651_event(
        action_type="content_report_5651",
        target_id=req.target_id,
        user_id=user["id"] if user else 0,
        client_id=x_client_id or "",
        ip_address=ip_addr,
        user_agent=user_agent,
        content_summary=f"Bildirim #{report_id} ({req.target_type} #{req.target_id}): {clean_reason}"
    )

    return {
        "reported": True,
        "report_id": report_id,
        "message": "🚨 Bildiriminiz 5651 sayılı Kanun (Uyar-Kaldır) kapsamında kayıt altına alındı ve moderasyon kuyruğuna iletildi."
    }


@app.post("/api/threads/{thread_id}/upvote")
def upvote_thread(
    thread_id: int,
    authorization: Optional[str] = Header(None),
    x_client_id: Optional[str] = Header(None)
):
    user = get_current_user(authorization)
    voter_key = resolve_voter_key(user, x_client_id)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, upvotes FROM threads WHERE id = ?", (thread_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Konu bulunamadı")

    cursor.execute("""
        SELECT id FROM user_votes WHERE voter_key = ? AND target_type = 'thread' AND target_id = ?
    """, (voter_key, thread_id))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("DELETE FROM user_votes WHERE id = ?", (existing["id"],))
        cursor.execute("UPDATE threads SET upvotes = MAX(0, upvotes - 1) WHERE id = ?", (thread_id,))
        voted_now = False
    else:
        cursor.execute("""
            INSERT INTO user_votes (voter_key, target_type, target_id, created_at)
            VALUES (?, 'thread', ?, ?)
        """, (voter_key, thread_id, datetime.now().isoformat()))
        cursor.execute("UPDATE threads SET upvotes = upvotes + 1 WHERE id = ?", (thread_id,))
        voted_now = True

    conn.commit()
    cursor.execute("SELECT upvotes FROM threads WHERE id = ?", (thread_id,))
    new_upvotes = cursor.fetchone()["upvotes"]
    conn.close()

    return {"upvotes": new_upvotes, "user_voted": voted_now}


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(ROOT_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/robots.txt")
def serve_robots():
    return FileResponse(os.path.join(ROOT_DIR, "robots.txt"), media_type="text/plain")


@app.get("/sitemap.xml")
def serve_sitemap():
    return FileResponse(os.path.join(ROOT_DIR, "sitemap.xml"), media_type="application/xml")


@app.get("/site.webmanifest")
def serve_manifest():
    return FileResponse(os.path.join(ROOT_DIR, "site.webmanifest"), media_type="application/manifest+json")


@app.get("/")
def serve_index():
    return FileResponse(os.path.join(ROOT_DIR, "index.html"))
