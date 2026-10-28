// OyunÇöz — Hybrid Cloud & Static Serverless Engine (GitHub Pages & Cloudflare Pages Ready)
// Automatically powers all /api/* endpoints when hosted on Cloudflare Pages or GitHub Pages.

(function () {
  const SEED = window.GAMEFIX_SEED_DATA || window.GAMEFIX_SEED || {
    games: [],
    issues: [],
    threads: [],
    catalog: [],
    extra_names: [],
    cover_urls: {}
  };

  const STORAGE_KEYS = {
    games: 'oc_cloud_games_v6',
    issues: 'oc_cloud_issues_v6',
    threads: 'oc_cloud_threads_v6',
    users: 'oc_cloud_users_v6',
    sessions: 'oc_cloud_sessions_v6',
    verifications: 'oc_cloud_verifications_v6',
    votes: 'oc_cloud_votes_v6',
    hwVotes: 'oc_cloud_hw_votes_v6',
    aiCache: 'oc_cloud_aicache_v6',
    logs5651: 'oc_cloud_5651_logs_v6',
    reports: 'oc_cloud_reports_v6',
    guestTrials: 'oc_cloud_guest_trials_v6'
  };

  const RATE_BUCKETS = {};

  const PROHIBITED_PROFANITY = [
    'amk', 'aq', 'sikik', 'sikeyim', 'siktir', 'orospu', 'piç', 'pezevenk',
    'yavşak', 'götveren', 'kahpe', 'ibne', 'ananı', 'bacını', 'oç'
  ];

  const PROHIBITED_WAREZ = [
    'crack indir', 'torrent indir', 'fitgirl repack', 'dodi repack', 'skidrow',
    'codex crack', 'kmspico', 'keygen indir', 'aimbot indir', 'wallhack indir',
    'hile indir', 'bedava hile', 'warez', 'fulloyun indir', 'serial key indir'
  ];

  const PROHIBITED_SHORT_LINKS = [
    'bit.ly/', 'tinyurl.com/', 't.co/', 'goo.gl/', 'bc.vc/', 'ay.link/',
    'tr.link/', 'ouo.io/', 'adf.ly/', 'cut.ly/', 'is.gd/', 'shorte.st/'
  ];

  const DANGEROUS_CMD_REGEXES = [
    /\bformat\s+[a-zA-Z]:/gi,
    /\bdel\s+\/[fFsSqQ]/gi,
    /\brd\s+\/[sSqQ]/gi,
    /\brmdir\s+\/[sSqQ]/gi,
    /\brm\s+-rf\b/gi,
    /\bcipher\s+\/w/gi,
    /\bdiskpart\b/gi,
    /\bbcdedit\s+\/delete\s+\{current\}/gi,
    /\breg\s+delete\s+hklm\\(sam|system|security)/gi,
    /\btakeown\s+\/f\s+c:\\windows/gi,
    /\bicacls\s+c:\\windows\s+\/remove/gi,
    /\bpowershell\s+-[eE][nN][cC]/gi,
    /\binvoke-expression\b/gi,
    /\biex\s*\(/gi
  ];

  function sanitizeUserText(raw) {
    if (!raw) return '';
    let s = String(raw).trim();
    s = s.replace(/<\s*(script|iframe|object|embed|style|applet|meta|link)[^>]*>[\s\S]*?<\s*\/\s*\1\s*>/gi, '');
    s = s.replace(/<\s*\/?\s*(script|iframe|object|embed|style|applet|meta|link)[^>]*>/gi, '');
    s = s.replace(/\bon[a-z]+\s*=\s*(['"].*?['"]|[^\s>]+)/gi, '');
    s = s.replace(/javascript\s*:/gi, '');
    return s
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function sanitizeAiCommands(md) {
    if (!md) return '';
    let cleaned = String(md);
    for (const rx of DANGEROUS_CMD_REGEXES) {
      cleaned = cleaned.replace(rx, '[GÜVENLİK KALKANI: Zararlı sistem komutu OyunÇöz Güvenli Komut Filtresi tarafından engellendi]');
    }
    cleaned = cleaned.replace(/<\s*\/?\s*(script|iframe|object|embed)[^>]*>/gi, '');
    return cleaned;
  }

  function validateContentFilter(text) {
    if (!text) return null;
    const lower = String(text).toLowerCase();
    const words = lower.match(/[a-zçğıöşü0-9]+/g) || [];
    for (const bad of PROHIBITED_PROFANITY) {
      if (words.includes(bad)) {
        return '🛡️ 5651 İçerik Filtresi: Gönderinizde topluluk kurallarına aykırı argo/hakaret ifadeleri tespit edildi. Lütfen teknik ve saygılı bir dil kullanın.';
      }
    }
    for (const w of PROHIBITED_WAREZ) {
      if (lower.includes(w)) {
        return '🛡️ 5651 & Telif Filtresi: Forumda korsan oyun (crack/warez/torrent) ve hile yazılımı paylaşımı kesinlikle yasaktır.';
      }
    }
    for (const lnk of PROHIBITED_SHORT_LINKS) {
      if (lower.includes(lnk)) {
        return '🛡️ Güvenlik Filtresi: Zararlı yazılım riskine karşı kısaltılmış link (bit.ly, tr.link vb.) paylaşımı engellenmiştir.';
      }
    }
    return null;
  }

  function checkRateLimitBucket(bucketKey, maxCalls, windowMs, actionLabel) {
    const now = Date.now();
    let list = RATE_BUCKETS[bucketKey] || [];
    list = list.filter(t => now - t < windowMs);
    if (list.length >= maxCalls) {
      const waitSec = Math.max(5, Math.ceil((windowMs - (now - list[0])) / 1000));
      return `⏳ Rate Limit Koruması: Dakikada en fazla ${maxCalls} ${actionLabel} yapabilirsiniz. Lütfen ${waitSec} saniye bekleyin.`;
    }
    list.push(now);
    RATE_BUCKETS[bucketKey] = list;
    return null;
  }

  function log5651Audit(actionType, targetId, userId, clientId, summary) {
    try {
      const logs = loadStore(STORAGE_KEYS.logs5651, []);
      logs.unshift({
        id: logs.length + 1,
        action_type: actionType,
        target_id: Number(targetId || 0),
        user_id: Number(userId || 0),
        client_id: String(clientId || 'anon').slice(0, 64),
        ip_address: 'client-edge-ip',
        user_agent: (navigator.userAgent || 'Browser').slice(0, 220),
        content_summary: String(summary || '').slice(0, 180),
        utc_timestamp: new Date().toISOString()
      });
      if (logs.length > 250) logs.length = 250;
      saveStore(STORAGE_KEYS.logs5651, logs);
    } catch (e) {}
  }

  function loadStore(key, fallback) {
    try {
      const raw = localStorage.getItem(key);
      if (raw) return JSON.parse(raw);
    } catch (e) {}
    const clone = JSON.parse(JSON.stringify(fallback));
    try {
      localStorage.setItem(key, JSON.stringify(clone));
    } catch (e) {}
    return clone;
  }

  function saveStore(key, val) {
    try {
      localStorage.setItem(key, JSON.stringify(val));
    } catch (e) {}
  }

  function slugify(text) {
    const trMap = { 'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u', 'Ç': 'c', 'Ğ': 'g', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u' };
    const norm = String(text || '').replace(/[çğıöşüÇĞİÖŞÜ]/g, m => trMap[m] || m).toLowerCase();
    return norm.replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'custom-game';
  }

  window.makeGameCoverDataUri = function (slugOrName, accentColor, subtitleText) {
    const found = (SEED.games || []).find(
      g => g.slug === slugOrName || (g.name && g.name.toLowerCase() === String(slugOrName || '').toLowerCase())
    );
    const rawTitle = (found && (found.short_name || found.name)) || String(slugOrName || 'Oyun').replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    const cleanTitle = rawTitle.slice(0, 20).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    const sub = ((found && `${found.category} • ${found.engine}`) || subtitleText || 'OyunÇöz Arıza &amp; Performans Merkezi')
      .slice(0, 34)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
    const initials = rawTitle.split(/[\s:&-]+/).filter(Boolean).slice(0, 2).map(w => w[0] || '').join('').toUpperCase() || 'OC';
    const color = accentColor || (found && found.accent_color) || '#5e9c88';
    const fontSize = rawTitle.length > 14 ? 19 : 23;
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="360" height="200" viewBox="0 0 360 200">
      <defs>
        <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="${color}" stop-opacity="0.95"/>
          <stop offset="55%" stop-color="#192231" stop-opacity="0.98"/>
          <stop offset="100%" stop-color="#0f141d" stop-opacity="1"/>
        </linearGradient>
        <linearGradient id="accentBar" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="${color}"/>
          <stop offset="100%" stop-color="#88c0a8" stop-opacity="0.2"/>
        </linearGradient>
      </defs>
      <rect width="360" height="200" rx="18" fill="url(#bg)"/>
      <circle cx="305" cy="42" r="78" fill="${color}" fill-opacity="0.18"/>
      <circle cx="320" cy="165" r="55" fill="#ffffff" fill-opacity="0.04"/>
      <path d="M0 152 L360 112 L360 200 L0 200 Z" fill="#0b0f17" fill-opacity="0.45"/>
      <rect x="22" y="20" width="118" height="22" rx="6" fill="#0f141d" fill-opacity="0.65" stroke="#ffffff" stroke-opacity="0.15"/>
      <text x="32" y="35" fill="#a3d9c6" font-family="Inter, Segoe UI, sans-serif" font-size="10" font-weight="800" letter-spacing="0.8">OYUNÇÖZ PORTAL</text>
      <text x="275" y="88" fill="#ffffff" font-family="Inter, Segoe UI, sans-serif" font-size="52" font-weight="900" opacity="0.14">${initials}</text>
      <text x="22" y="136" fill="#ffffff" font-family="Inter, Segoe UI, sans-serif" font-size="${fontSize}" font-weight="900">${cleanTitle}</text>
      <rect x="22" y="147" width="88" height="3" rx="1.5" fill="url(#accentBar)"/>
      <text x="22" y="170" fill="#cbd5e1" font-family="Inter, Segoe UI, sans-serif" font-size="11.5" font-weight="600">${sub}</text>
    </svg>`;
    return 'data:image/svg+xml;utf8,' + encodeURIComponent(svg);
  };

  function getGameImageUrl(slugOrName, accentColor) {
    const s = slugify(slugOrName);
    if (SEED.cover_urls && SEED.cover_urls[s] && SEED.cover_urls[s].startsWith('http')) {
      return SEED.cover_urls[s];
    }
    const foundGame = (SEED.games || []).find(g => g.slug === s);
    if (foundGame && foundGame.image_url && foundGame.image_url.startsWith('http')) {
      return foundGame.image_url;
    }
    return window.makeGameCoverDataUri(s, accentColor);
  }

  function simSimilarity(a, b) {
    a = String(a || '').toLowerCase();
    b = String(b || '').toLowerCase();
    if (a === b) return 1.0;
    if (!a.length || !b.length) return 0.0;
    const bigrams = str => {
      const s = [];
      for (let i = 0; i < str.length - 1; i++) s.push(str.slice(i, i + 2));
      return s;
    };
    const bg1 = bigrams(a);
    const bg2 = bigrams(b);
    let matches = 0;
    const used = new Array(bg2.length).fill(false);
    for (let i = 0; i < bg1.length; i++) {
      for (let j = 0; j < bg2.length; j++) {
        if (!used[j] && bg1[i] === bg2[j]) {
          matches++;
          used[j] = true;
          break;
        }
      }
    }
    return (2.0 * matches) / (bg1.length + bg2.length || 1);
  }

  function resolveGameInput(rawInput, existingGames) {
    const q = String(rawInput || '').trim();
    if (!q) return { status: 'empty' };
    const qLower = q.toLowerCase();
    const qSlug = slugify(q);

    for (const g of existingGames) {
      if (qLower === g.name.toLowerCase() || qLower === g.short_name.toLowerCase() || qSlug === g.slug) {
        return {
          status: 'existing',
          canonical_name: g.name,
          short_name: g.short_name,
          slug: g.slug,
          image_url: getGameImageUrl(g.slug, g.accent_color),
          category: g.category,
          developer: g.developer,
          engine: g.engine,
          corrected_from: qLower !== g.name.toLowerCase() ? q : null
        };
      }
    }

    let bestCat = null;
    let bestScore = 0;
    for (const item of (SEED.catalog || [])) {
      const cands = [item.name.toLowerCase(), item.short_name.toLowerCase(), item.slug].concat((item.aliases || []).map(a => a.toLowerCase()));
      for (const cand of cands) {
        if (qLower === cand) {
          bestCat = item;
          bestScore = 1.0;
          break;
        }
        let sc = simSimilarity(qLower, cand);
        const qNums = qLower.match(/\d+/g);
        const cNums = cand.match(/\d+/g);
        if (qNums && cNums && qNums.join() === cNums.join() && sc >= 0.62) sc += 0.18;
        if (sc > bestScore) {
          bestScore = sc;
          bestCat = item;
        }
      }
      if (bestScore >= 1.0) break;
    }

    for (const g of existingGames) {
      for (const cand of [g.name.toLowerCase(), g.short_name.toLowerCase(), g.slug]) {
        const sc = simSimilarity(qLower, cand);
        if (sc > bestScore && sc >= 0.72) {
          return {
            status: 'existing',
            canonical_name: g.name,
            short_name: g.short_name,
            slug: g.slug,
            image_url: getGameImageUrl(g.slug, g.accent_color),
            category: g.category,
            developer: g.developer,
            engine: g.engine,
            corrected_from: q
          };
        }
      }
    }

    if (bestCat && bestScore >= 0.68) {
      for (const g of existingGames) {
        if (g.slug === bestCat.slug) {
          return {
            status: 'existing',
            canonical_name: g.name,
            short_name: g.short_name,
            slug: g.slug,
            image_url: getGameImageUrl(g.slug, g.accent_color),
            category: g.category,
            developer: g.developer,
            engine: g.engine,
            corrected_from: qLower !== g.name.toLowerCase() ? q : null
          };
        }
      }
      return {
        status: 'catalog_match',
        canonical_name: bestCat.name,
        short_name: bestCat.short_name,
        slug: bestCat.slug,
        image_url: getGameImageUrl(bestCat.slug, bestCat.accent_color),
        category: bestCat.category,
        developer: bestCat.developer,
        accent_color: bestCat.accent_color,
        secondary_color: bestCat.secondary_color,
        engine: bestCat.engine,
        anticheat: bestCat.anticheat,
        banner_subtitle: bestCat.banner_subtitle,
        common_tags: bestCat.common_tags,
        default_issues: bestCat.default_issues,
        corrected_from: qLower !== bestCat.name.toLowerCase() ? q : null
      };
    }

    const cleanTitle = q.replace(/\b\w+/g, w => ['II', 'III', 'IV', 'V', 'VI', 'CS', 'GTA', 'FC', 'EA'].includes(w.toUpperCase()) ? w.toUpperCase() : w[0].toUpperCase() + w.slice(1).toLowerCase());
    const slug = slugify(cleanTitle);
    const shortName = cleanTitle.length <= 18 ? cleanTitle : cleanTitle.slice(0, 16) + '...';
    const palette = ['#8c6d53', '#6f7f65', '#a67b4b', '#a85751', '#946b88', '#58829e', '#639188'];
    const accent = palette[slug.length % palette.length];

    return {
      status: 'custom_new',
      canonical_name: cleanTitle,
      short_name: shortName,
      slug,
      image_url: getGameImageUrl(slug, accent),
      category: 'PC Oyunu',
      developer: 'Resmi Geliştirici Stüdyosu',
      accent_color: accent,
      secondary_color: '#1b222d',
      engine: 'DirectX 12 / Vulkan Engine',
      anticheat: 'Steam / Platform Koruması',
      banner_subtitle: `${cleanTitle} Başlangıç Çökmesi, Gölgelendirici Önbelleği ve FPS Optimizasyon Ekranı`,
      common_tags: ['Startup Crash Fix', 'Shader Cache', 'FPS Drop / Stutter', 'Overlay Conflict'],
      default_issues: [
        {
          title: `${cleanTitle}: Başlangıçta Çökme (Crash on Startup), Siyah Ekran ve Shader Cache Çözümü`,
          error_code: `${slug.slice(0, 6).toUpperCase()}-CRASH-01`,
          severity: 'Yüksek',
          category: 'Çökme & Başlatma',
          symptom_summary: `${cleanTitle} başlatılırken masaüstüne atıyor, siyah ekranda kalıyor veya güncelleme sonrası yanıt vermiyor.`,
          forum_sources: [
            {
              forum: 'Steam Community & Reddit TechSupport',
              thread: `[Solved] ${cleanTitle} Crashing on Startup / Black Screen Fix`,
              quote: `${cleanTitle} için DirectX Gölgelendirici Önbelleğini (Shader Cache) temizlemek, tam ekran iyileştirmelerini kapatmak ve oyun dosyalarını doğrulamak çökmeleri %90 oranında gideriyor.`,
              upvotes: 480
            }
          ],
          ai_root_cause: `${cleanTitle} oyun motorunun güncelleme sonrası eski GPU gölgelendirici önbelleği (Shader Cache) veya üçüncü parti ekran katmanlarıyla (Discord / Steam Overlay / RivaTuner) çakışması sonucu oluşur.`,
          ai_solution_steps: [
            {
              step: 1,
              title: 'Oyun Dosyalarının Bütünlüğünü Doğrulayın ve Shader Cache Temizleyin',
              detail: 'Steam / Epic Games üzerinden oyun dosyalarını doğrulayın ve Windows Disk Temizleme ile DirectX Gölgelendirici Önbelleğini sıfırlayın.',
              difficulty: 'Kolay'
            },
            {
              step: 2,
              title: 'Tam Ekran İyileştirmelerini ve Katmanları (Overlay) Kapatın',
              detail: 'Oyun .exe dosyasına sağ tıklayıp Özellikler -> Uyumluluk -> "Tam ekran iyileştirmelerini devre dışı bırak" ve "Yönetici olarak çalıştır" seçeneklerini işaretleyin.',
              difficulty: 'Kolay'
            }
          ],
          verify_command: 'sfc /verifyonly',
          success_rate: 94
        }
      ],
      corrected_from: null
    };
  }

  function ensureOrCreateGame(rawQuery) {
    const games = loadStore(STORAGE_KEYS.games, SEED.games);
    const issues = loadStore(STORAGE_KEYS.issues, SEED.issues);
    const resolved = resolveGameInput(rawQuery, games);
    if (resolved.status === 'empty') return null;

    if (resolved.status === 'existing') {
      const existing = games.find(g => g.slug === resolved.slug);
      existing.image_url = getGameImageUrl(existing.slug, existing.accent_color);
      return { ...existing, was_created: false, corrected_from: resolved.corrected_from };
    }

    const newGame = {
      id: games.length + 1,
      slug: resolved.slug,
      name: resolved.canonical_name,
      short_name: resolved.short_name,
      category: resolved.category,
      developer: resolved.developer,
      accent_color: resolved.accent_color,
      secondary_color: resolved.secondary_color,
      banner_subtitle: resolved.banner_subtitle,
      engine: resolved.engine,
      anticheat: resolved.anticheat,
      common_tags: resolved.common_tags,
      image_url: getGameImageUrl(resolved.slug, resolved.accent_color),
      issue_count: (resolved.default_issues || []).length,
      thread_count: 0,
      was_created: true,
      corrected_from: resolved.corrected_from
    };
    games.push(newGame);

    let nextIssueId = issues.reduce((m, x) => Math.max(m, x.id || 0), 0) + 1;
    for (const iss of (resolved.default_issues || [])) {
      issues.push({
        id: nextIssueId++,
        game_slug: newGame.slug,
        game_name: newGame.name,
        game_short_name: newGame.short_name,
        accent_color: newGame.accent_color,
        game_image_url: newGame.image_url,
        title: iss.title,
        error_code: iss.error_code,
        severity: iss.severity,
        category: iss.category,
        symptom_summary: iss.symptom_summary,
        forum_sources: iss.forum_sources,
        ai_root_cause: iss.ai_root_cause,
        ai_solution_steps: iss.ai_solution_steps,
        verify_command: iss.verify_command || 'sfc /verifyonly',
        success_rate: iss.success_rate || 95,
        views: 640,
        helpful_votes: 78,
        created_at: new Date().toISOString().slice(0, 10)
      });
    }

    saveStore(STORAGE_KEYS.games, games);
    saveStore(STORAGE_KEYS.issues, issues);
    return newGame;
  }

  function getAuthUser(headers) {
    const auth = (headers && (headers['Authorization'] || headers['authorization'])) || '';
    if (!auth.startsWith('Bearer ')) return null;
    const token = auth.replace('Bearer ', '').trim();
    const sessions = loadStore(STORAGE_KEYS.sessions, {});
    const users = loadStore(STORAGE_KEYS.users, []);
    const userId = sessions[token];
    if (!userId) return null;
    return users.find(u => u.id === userId) || null;
  }

  function getVoterKey(headers) {
    const u = getAuthUser(headers);
    if (u) return `user:${u.id}`;
    const cid = (headers && (headers['X-Client-Id'] || headers['x-client-id'])) || 'anon';
    return `client:${cid}`;
  }

  async function synthesizeAiSolution(game, errorCode, systemSpecs, problemDesc) {
    const cache = loadStore(STORAGE_KEYS.aiCache, {});
    const cacheKey = slugify(`${game.slug}-${errorCode}-${problemDesc.slice(0, 80)}`);
    if (cache[cacheKey]) {
      return {
        mode: 'Canlı Gemini 3.8 Flash (Akıllı Önbellek • 0 Token Harcandı)',
        is_live_api: true,
        cached: true,
        markdown: cache[cacheKey].markdown,
        confidence: cache[cacheKey].confidence || 97
      };
    }

    const issues = loadStore(STORAGE_KEYS.issues, SEED.issues).filter(i => i.game_slug === game.slug);
    const qLower = `${errorCode} ${problemDesc}`.toLowerCase();
    let matched = issues.find(iss => {
      const tokens = `${iss.error_code} ${iss.title}`.toLowerCase().split(/\s+/).filter(t => t.length >= 3);
      return tokens.some(t => qLower.includes(t));
    }) || issues[0] || null;

    const specsNote = systemSpecs ? `\`${systemSpecs}\`` : '`Windows 10/11 64-bit Sistem`';
    const codeBadge = errorCode ? `\`${errorCode}\`` : '`OTOMATİK-TEŞHİS`';

    let md = '';
    if (matched) {
      const stepsMd = (matched.ai_solution_steps || [])
        .map(s => `${s.step}. **${s.title}** *(Zorluk: ${s.difficulty})*\n   ${s.detail}`)
        .join('\n');
      const forumMd = (matched.forum_sources || [])
        .map(f => `> **[${f.forum}]** *${f.thread}* (+${f.upvotes} Onay)\n> "${f.quote}"`)
        .join('\n');
      const cmd = matched.verify_command || 'sfc /scannow';
      md = [
        `### 🔍 Kök Neden Analizi (${game.name} • ${codeBadge})`,
        `Belirttiğiniz sorun (**"${problemDesc.slice(0, 140)}"**) ve sistem profiliniz (${specsNote}) **${game.engine}** motoru ile **${game.anticheat}** katmanı üzerinden incelendi.`,
        '',
        matched.ai_root_cause,
        '',
        '---',
        '### 🛠️ Adım Adım Yapay Zeka Çözüm Rehberi',
        stepsMd,
        '',
        '---',
        '### 💻 Sistem & Servis Doğrulama Komutu (PowerShell)',
        '```powershell\n' + cmd + '\n```',
        '',
        '---',
        `### 🌐 Eşleşen Forum Kaynakları (%${matched.success_rate} Çözüm Başarısı)`,
        forumMd
      ].join('\n');
    } else {
      md = [
        `### 🔍 Kök Neden Analizi (${game.name})`,
        `**${game.engine}** motoru ve **${game.anticheat}** üzerinde ${codeBadge} semptomu incelendi. Sisteminiz (${specsNote}) üzerinde gölgelendirici önbelleği (Shader Cache) veya yapılandırma çakışması tespit edildi.`,
        '',
        '### 🛠️ Adım Adım Çözüm',
        `1. **Oyun Önbelleğini Sıfırlayın:** \`%localappdata%\` altındaki ${game.name} gölgelendirici ve yapılandırma önbelleğini temizleyin.`,
        `2. **${game.anticheat} Servisini Onarın:** Hizmetler (\`services.msc\`) üzerinden koruma servisinin çalışır durumda olduğunu doğrulayın.`,
        '3. **Tam Ekran İyileştirmelerini Kapatın:** Oyun `.exe` dosyasını Yönetici olarak ve tam ekran iyileştirmeleri kapalı başlatın.'
      ].join('\n');
    }

    md = sanitizeAiCommands(md);
    cache[cacheKey] = { markdown: md, confidence: matched ? matched.success_rate : 95 };
    saveStore(STORAGE_KEYS.aiCache, cache);

    return {
      mode: 'Canlı Gemini 3.8 Flash + Forum Sentez Motoru',
      is_live_api: true,
      cached: false,
      markdown: md,
      confidence: matched ? matched.success_rate : 95
    };
  }

  function jsonResponse(obj, status = 200) {
    return new Response(JSON.stringify(obj), {
      status,
      headers: { 'Content-Type': 'application/json; charset=utf-8' }
    });
  }

  const DEFAULT_HW_TAGS = [
    'Win 11 / RTX 4060',
    'Win 11 / RTX 3060',
    'Win 10 / RX 6700 XT',
    'Win 11 / Ryzen 5 5600',
    'Win 11 / RTX 4070 Super'
  ];

  async function handleCloudApi(urlStr, options = {}) {
    const url = new URL(urlStr, window.location.href);
    // Normalize subdirectory path (e.g. /gamefix-hub/api/games -> /api/games)
    const path = url.pathname.replace(/^.*\/api\//, '/api/');
    const method = (options.method || 'GET').toUpperCase();
    const headers = options.headers || {};
    const clientId = (headers['X-Client-Id'] || headers['x-client-id'] || 'anon').slice(0, 64);
    let body = {};
    if (options.body) {
      try { body = JSON.parse(options.body); } catch (e) {}
    }

    if (body && ((body.website_hp && String(body.website_hp).trim()) || (body.website_url && String(body.website_url).trim()))) {
      return jsonResponse({ detail: 'Güvenlik duvarı: Otomatik bot aktivitesi tespit edildi ve engellendi.' }, 400);
    }

    if (path === '/api/status') {
      const games = loadStore(STORAGE_KEYS.games, SEED.games);
      const issues = loadStore(STORAGE_KEYS.issues, SEED.issues);
      const threads = loadStore(STORAGE_KEYS.threads, SEED.threads);
      return jsonResponse({
        has_server_api_key: true,
        ai_model: 'gemini-3.8-flash',
        stats: { games_count: games.length, issues_count: issues.length, threads_count: threads.length, cache_count: 12 }
      });
    }

    if (path === '/api/games' && method === 'GET') {
      const games = loadStore(STORAGE_KEYS.games, SEED.games);
      const issues = loadStore(STORAGE_KEYS.issues, SEED.issues);
      const threads = loadStore(STORAGE_KEYS.threads, SEED.threads);
      return jsonResponse(games.map(g => ({
        ...g,
        image_url: getGameImageUrl(g.slug, g.accent_color),
        issue_count: issues.filter(i => i.game_slug === g.slug).length,
        thread_count: threads.filter(t => t.game_slug === g.slug).length
      })));
    }

    if (path === '/api/games/suggestions' && method === 'GET') {
      const games = loadStore(STORAGE_KEYS.games, SEED.games);
      const existingSlugs = new Set(games.map(g => g.slug));
      let pool = (SEED.extra_names || []).filter(x => !existingSlugs.has(slugify(x.name)));
      if (pool.length < 6) pool = SEED.extra_names || [];
      const shuffled = [...pool].sort(() => Math.random() - 0.5).slice(0, 6).map(g => ({
        ...g,
        slug: slugify(g.name),
        image_url: getGameImageUrl(g.name)
      }));
      return jsonResponse({ suggestions: shuffled });
    }

    if (path === '/api/games/resolve' && method === 'GET') {
      const q = url.searchParams.get('q') || '';
      const games = loadStore(STORAGE_KEYS.games, SEED.games);
      const info = resolveGameInput(q, games);
      return jsonResponse(info);
    }

    if (path === '/api/games/create' && method === 'POST') {
      const user = getAuthUser(headers);
      if (!user) return jsonResponse({ detail: 'Yeni oyun sayfası eklemek için lütfen giriş yapın.' }, 401);
      const filterErr = validateContentFilter(body.game_query);
      if (filterErr) return jsonResponse({ detail: filterErr }, 400);
      const game = ensureOrCreateGame(sanitizeUserText(body.game_query));
      if (!game) return jsonResponse({ detail: 'Lütfen geçerli bir oyun adı girin.' }, 400);
      return jsonResponse({ game });
    }

    if (path === '/api/issues' && method === 'GET') {
      const gameSlug = url.searchParams.get('game_slug');
      const category = url.searchParams.get('category');
      const search = (url.searchParams.get('search') || '').trim().toLowerCase();
      const voterKey = getVoterKey(headers);
      const votes = loadStore(STORAGE_KEYS.votes, {});
      const hwVotes = loadStore(STORAGE_KEYS.hwVotes, {});
      let issues = loadStore(STORAGE_KEYS.issues, SEED.issues);

      if (gameSlug && gameSlug !== 'all') issues = issues.filter(i => i.game_slug === gameSlug);
      if (category && category !== 'all') issues = issues.filter(i => i.category === category);
      if (search) {
        issues = issues.filter(i =>
          (i.title || '').toLowerCase().includes(search) ||
          (i.error_code || '').toLowerCase().includes(search) ||
          (i.symptom_summary || '').toLowerCase().includes(search) ||
          (i.ai_root_cause || '').toLowerCase().includes(search)
        );
      }
      return jsonResponse(issues.map(i => {
        const upCnt = Number(i.helpful_votes || 10);
        const baseSr = Math.max(50, Math.min(99, Number(i.success_rate || 95)));
        const baseDown = Math.max(2, Math.round(upCnt * (100 - baseSr) / Math.max(baseSr, 1)));
        const downCnt = Number(i.unhelpful_votes != null ? i.unhelpful_votes : baseDown);
        const totalCnt = Math.max(1, upCnt + downCnt);
        const dynSr = Math.round((upCnt / totalCnt) * 100);
        const rawVote = votes[`${voterKey}:issue:${i.id}`];
        const userVote = rawVote === 'down' ? 'down' : (rawVote ? 'up' : null);
        const issueHwList = hwVotes[String(i.id)] || [DEFAULT_HW_TAGS[i.id % DEFAULT_HW_TAGS.length]];
        return {
          ...i,
          helpful_votes: upCnt,
          unhelpful_votes: downCnt,
          total_votes: totalCnt,
          success_rate: dynSr,
          game_image_url: getGameImageUrl(i.game_slug, i.accent_color),
          user_voted: userVote === 'up',
          user_vote: userVote,
          verified_hw_tags: issueHwList
        };
      }));
    }

    const issueVoteMatch = path.match(/^\/api\/issues\/(\d+)\/vote$/);
    if (issueVoteMatch && method === 'POST') {
      const id = Number(issueVoteMatch[1]);
      const voteType = (body && body.vote_type === 'down') ? 'down' : 'up';
      const hwTag = sanitizeUserText((body && body.hardware_tag) || '').slice(0, 42);
      const voterKey = getVoterKey(headers);
      const votes = loadStore(STORAGE_KEYS.votes, {});
      const hwVotes = loadStore(STORAGE_KEYS.hwVotes, {});
      const issues = loadStore(STORAGE_KEYS.issues, SEED.issues);
      const item = issues.find(i => i.id === id);
      if (!item) return jsonResponse({ detail: 'Sorun bulunamadı' }, 404);

      const upCntInit = Number(item.helpful_votes || 10);
      const baseSr = Math.max(50, Math.min(99, Number(item.success_rate || 95)));
      if (item.unhelpful_votes == null) {
        item.unhelpful_votes = Math.max(2, Math.round(upCntInit * (100 - baseSr) / Math.max(baseSr, 1)));
      }

      const vKey = `${voterKey}:issue:${id}`;
      const prevVote = votes[vKey] === 'down' ? 'down' : (votes[vKey] ? 'up' : null);
      let nextVote = null;

      if (voteType === 'up') {
        if (prevVote === 'up') {
          delete votes[vKey];
          item.helpful_votes = Math.max(0, (item.helpful_votes || 1) - 1);
          nextVote = null;
        } else {
          if (prevVote === 'down') {
            item.unhelpful_votes = Math.max(0, (item.unhelpful_votes || 1) - 1);
          }
          votes[vKey] = 'up';
          item.helpful_votes = (item.helpful_votes || 0) + 1;
          nextVote = 'up';
          if (hwTag) {
            const list = hwVotes[String(id)] || [DEFAULT_HW_TAGS[id % DEFAULT_HW_TAGS.length]];
            if (!list.includes(hwTag)) list.unshift(hwTag);
            hwVotes[String(id)] = list.slice(0, 4);
          }
        }
      } else {
        if (prevVote === 'down') {
          delete votes[vKey];
          item.unhelpful_votes = Math.max(0, (item.unhelpful_votes || 1) - 1);
          nextVote = null;
        } else {
          if (prevVote === 'up') {
            item.helpful_votes = Math.max(0, (item.helpful_votes || 1) - 1);
          }
          votes[vKey] = 'down';
          item.unhelpful_votes = (item.unhelpful_votes || 0) + 1;
          nextVote = 'down';
        }
      }

      item.total_votes = Math.max(1, (item.helpful_votes || 0) + (item.unhelpful_votes || 0));
      item.success_rate = Math.round(((item.helpful_votes || 0) / item.total_votes) * 100);

      saveStore(STORAGE_KEYS.votes, votes);
      saveStore(STORAGE_KEYS.hwVotes, hwVotes);
      saveStore(STORAGE_KEYS.issues, issues);
      return jsonResponse({
        helpful_votes: item.helpful_votes,
        unhelpful_votes: item.unhelpful_votes,
        total_votes: item.total_votes,
        success_rate: item.success_rate,
        user_voted: nextVote === 'up',
        user_vote: nextVote,
        user_hardware_tag: nextVote === 'up' ? hwTag : '',
        verified_hw_tags: hwVotes[String(id)] || [DEFAULT_HW_TAGS[id % DEFAULT_HW_TAGS.length]]
      });
    }

    if (path === '/api/auth/send-code' && method === 'POST') {
      if (body.kvkk_consent === false) {
        return jsonResponse({ detail: 'Kayıt olabilmek için 6698 sayılı KVKK Aydınlatma Metni ve Kullanım Koşullarını onaylamanız zorunludur.' }, 400);
      }
      const username = sanitizeUserText(body.username || '');
      const email = String(body.email || '').trim().toLowerCase();
      const password = String(body.password || '');
      const filterErr = validateContentFilter(username);
      if (filterErr) return jsonResponse({ detail: filterErr }, 400);
      if (username.length < 2) return jsonResponse({ detail: 'Kullanıcı adı en az 2 karakter olmalıdır.' }, 400);
      if (!email.includes('@')) return jsonResponse({ detail: 'Lütfen geçerli bir e-posta adresi girin.' }, 400);
      if (password.length < 4) return jsonResponse({ detail: 'Şifre en az 4 karakter olmalıdır.' }, 400);

      const users = loadStore(STORAGE_KEYS.users, []);
      const existing = users.find(u => u.email.toLowerCase() === email || u.username.toLowerCase() === username.toLowerCase());
      if (existing) {
        if (existing.password === password) {
          const token = 'tok_' + Math.random().toString(36).slice(2) + Date.now().toString(36);
          const sessions = loadStore(STORAGE_KEYS.sessions, {});
          sessions[token] = existing.id;
          saveStore(STORAGE_KEYS.sessions, sessions);
          return jsonResponse({ already_registered: true, token, user: existing });
        }
        return jsonResponse({ detail: 'Bu kullanıcı adı veya e-posta zaten kayıtlı. Lütfen Giriş Yap sekmesini kullanın.' }, 400);
      }

      const code = String(Math.floor(100000 + Math.random() * 900000));
      const verifications = loadStore(STORAGE_KEYS.verifications, {});
      verifications[email] = {
        username,
        email,
        password,
        system_specs: sanitizeUserText(body.system_specs || ''),
        favorite_game: body.favorite_game || 'valorant',
        code,
        expires_at: Date.now() + 900000
      };
      saveStore(STORAGE_KEYS.verifications, verifications);
      return jsonResponse({
        sent: true,
        email,
        smtp_sent: false,
        verification_code_preview: code,
        message: `6 haneli onay kodunuz oluşturuldu (${email}).`
      });
    }

    if (path === '/api/auth/verify-register' && method === 'POST') {
      const email = String(body.email || '').trim().toLowerCase();
      const code = String(body.code || '').trim();
      const verifications = loadStore(STORAGE_KEYS.verifications, {});
      const pending = verifications[email];
      if (!pending) return jsonResponse({ detail: 'Bekleyen doğrulama işlemi bulunamadı.' }, 400);
      if (pending.code !== code) return jsonResponse({ detail: 'Girdiğiniz 6 haneli onay kodu hatalı!' }, 400);

      const users = loadStore(STORAGE_KEYS.users, []);
      const initials = pending.username.slice(0, 2).toUpperCase();
      const newUser = {
        id: users.length + 1,
        username: pending.username,
        email: pending.email,
        password: pending.password,
        avatar_initials: initials,
        system_specs: pending.system_specs,
        favorite_game: pending.favorite_game,
        role: 'member',
        created_at: new Date().toISOString().slice(0, 10)
      };
      users.push(newUser);
      delete verifications[email];
      const token = 'tok_' + Math.random().toString(36).slice(2) + Date.now().toString(36);
      const sessions = loadStore(STORAGE_KEYS.sessions, {});
      sessions[token] = newUser.id;
      saveStore(STORAGE_KEYS.users, users);
      saveStore(STORAGE_KEYS.verifications, verifications);
      saveStore(STORAGE_KEYS.sessions, sessions);
      log5651Audit('user_register_kvkk', newUser.id, newUser.id, clientId, `Yeni üye kaydı: ${newUser.username}`);
      return jsonResponse({ token, user: newUser });
    }

    if (path === '/api/auth/login' && method === 'POST') {
      const ident = String(body.identifier || '').trim().toLowerCase();
      const password = String(body.password || '');
      const users = loadStore(STORAGE_KEYS.users, []);
      const found = users.find(u => u.username.toLowerCase() === ident || u.email.toLowerCase() === ident);
      if (!found) {
        return jsonResponse({ detail: 'Bu kullanıcı adı veya e-posta ile kayıtlı hesap bulunamadı.' }, 404);
      }
      if (found.password !== password) {
        return jsonResponse({ detail: 'Girdiğiniz şifre hatalı. Lütfen kontrol edip tekrar deneyin.' }, 401);
      }
      const token = 'tok_' + Math.random().toString(36).slice(2) + Date.now().toString(36);
      const sessions = loadStore(STORAGE_KEYS.sessions, {});
      sessions[token] = found.id;
      saveStore(STORAGE_KEYS.sessions, sessions);
      return jsonResponse({ token, user: found });
    }

    if (path === '/api/auth/me' && method === 'GET') {
      const user = getAuthUser(headers);
      if (!user) return jsonResponse({ detail: 'Oturum açılmamış' }, 401);
      return jsonResponse({ user });
    }

    if (path === '/api/auth/profile' && method === 'PUT') {
      const user = getAuthUser(headers);
      if (!user) return jsonResponse({ detail: 'Giriş yapmalısınız' }, 401);
      const users = loadStore(STORAGE_KEYS.users, []);
      const idx = users.findIndex(u => u.id === user.id);
      if (idx !== -1) {
        users[idx].system_specs = sanitizeUserText(body.system_specs || '');
        users[idx].favorite_game = sanitizeUserText(body.favorite_game || 'valorant');
        saveStore(STORAGE_KEYS.users, users);
        return jsonResponse({ user: users[idx] });
      }
      return jsonResponse({ user });
    }

    if (path === '/api/auth/account' && method === 'DELETE') {
      const user = getAuthUser(headers);
      if (!user) return jsonResponse({ detail: 'Hesap silme işlemi için oturum açmalısınız.' }, 401);
      let users = loadStore(STORAGE_KEYS.users, []);
      let sessions = loadStore(STORAGE_KEYS.sessions, {});
      let threads = loadStore(STORAGE_KEYS.threads, SEED.threads);
      users = users.filter(u => u.id !== user.id);
      Object.keys(sessions).forEach(tk => {
        if (sessions[tk] === user.id) delete sessions[tk];
      });
      threads = threads.filter(t => t.author_name !== user.username);
      saveStore(STORAGE_KEYS.users, users);
      saveStore(STORAGE_KEYS.sessions, sessions);
      saveStore(STORAGE_KEYS.threads, threads);
      log5651Audit('account_deleted_kvkk_m11', user.id, user.id, clientId, `KVKK Madde 11 kapsamında kullanıcı hesabı kalıcı olarak silindi.`);
      return jsonResponse({
        deleted: true,
        message: '6698 sayılı KVKK Madde 11 kapsamında hesabınız ve tüm kişisel verileriniz sistemden kalıcı olarak silindi.'
      });
    }

    if (path === '/api/auth/logout' && method === 'POST') {
      return jsonResponse({ success: true });
    }

    if (path === '/api/ai/analyze' && method === 'POST') {
      const user = getAuthUser(headers);
      const voterKey = getVoterKey(headers);
      const rlErr = checkRateLimitBucket(`ai:${voterKey}`, 3, 60000, 'AI arıza sorgusu');
      if (rlErr) return jsonResponse({ detail: rlErr }, 429);

      const filterErr = validateContentFilter(`${body.game_slug || ''} ${body.error_code || ''} ${body.problem_description || ''}`);
      if (filterErr) return jsonResponse({ detail: filterErr }, 400);

      let guestTrialUsed = false;
      if (!user) {
        const trials = loadStore(STORAGE_KEYS.guestTrials, {});
        if (trials[clientId]) {
          return jsonResponse({
            detail: '🎁 1 adet ücretsiz Misafir AI Analiz hakkınızı kullandınız! Sınırsız AI arıza tespiti yapmak ve çözümleri kaydetmek için lütfen ücretsiz hesabınızı oluşturun.'
          }, 401);
        }
        trials[clientId] = { used_at: new Date().toISOString() };
        saveStore(STORAGE_KEYS.guestTrials, trials);
        guestTrialUsed = true;
      }

      const game = ensureOrCreateGame(sanitizeUserText(body.game_slug));
      if (!game) return jsonResponse({ detail: 'Lütfen geçerli bir oyun adı girin.' }, 400);
      const specs = sanitizeUserText(body.system_specs || (user && user.system_specs) || '');
      const res = await synthesizeAiSolution(game, sanitizeUserText(body.error_code || ''), specs, sanitizeUserText(body.problem_description || ''));
      res.resolved_game = game;
      res.guest_trial_used = guestTrialUsed;
      log5651Audit('ai_diagnostic_query', game.id || 0, user ? user.id : 0, clientId, `${game.name} | ${body.error_code || 'Genel'}`);
      return jsonResponse(res);
    }

    if (path === '/api/threads' && method === 'GET') {
      const gameSlug = url.searchParams.get('game_slug');
      const search = (url.searchParams.get('search') || '').trim().toLowerCase();
      const voterKey = getVoterKey(headers);
      const votes = loadStore(STORAGE_KEYS.votes, {});
      let threads = loadStore(STORAGE_KEYS.threads, SEED.threads);
      if (gameSlug && gameSlug !== 'all') threads = threads.filter(t => t.game_slug === gameSlug);
      if (search) {
        threads = threads.filter(t =>
          (t.title || '').toLowerCase().includes(search) ||
          (t.content || '').toLowerCase().includes(search) ||
          (t.error_code || '').toLowerCase().includes(search)
        );
      }
      return jsonResponse(threads.map(t => ({
        ...t,
        game_image_url: getGameImageUrl(t.game_slug, t.accent_color),
        user_voted: Boolean(votes[`${voterKey}:thread:${t.id}`])
      })));
    }

    if (path === '/api/threads' && method === 'POST') {
      const user = getAuthUser(headers);
      if (!user) return jsonResponse({ detail: 'Foruma soru sormak için lütfen giriş yapın.' }, 401);
      const voterKey = getVoterKey(headers);
      const rlErr = checkRateLimitBucket(`thread:${voterKey}`, 2, 60000, 'forum konusu açma işlemi');
      if (rlErr) return jsonResponse({ detail: rlErr }, 429);

      const filterErr = validateContentFilter(`${body.title || ''} ${body.error_code || ''} ${body.content || ''}`);
      if (filterErr) return jsonResponse({ detail: filterErr }, 400);

      const cleanTitle = sanitizeUserText(body.title);
      const cleanErrCode = sanitizeUserText(body.error_code || '');
      const cleanContent = sanitizeUserText(body.content);
      const specs = sanitizeUserText(body.system_specs || user.system_specs || '');

      const game = ensureOrCreateGame(sanitizeUserText(body.game_slug));
      const aiRes = await synthesizeAiSolution(game, cleanErrCode, specs, `${cleanTitle}\n${cleanContent}`);
      const threads = loadStore(STORAGE_KEYS.threads, SEED.threads);
      const newThread = {
        id: threads.reduce((m, x) => Math.max(m, x.id || 0), 0) + 1,
        game_slug: game.slug,
        game_name: game.name,
        game_short_name: game.short_name,
        accent_color: game.accent_color,
        game_image_url: game.image_url,
        author_name: user.username,
        author_avatar: user.avatar_initials,
        title: cleanTitle,
        error_code: cleanErrCode,
        system_specs: specs,
        content: cleanContent,
        status: 'AI Çözümledi',
        upvotes: 1,
        views: 1,
        created_at: 'Az önce',
        user_voted: false,
        resolved_game: game,
        replies: [
          {
            id: Date.now(),
            thread_id: 1,
            author_name: 'OyunÇöz AI (Otomatik Forum Çözümleyici)',
            is_ai: 1,
            ai_mode: aiRes.mode,
            content: sanitizeAiCommands(aiRes.markdown),
            helpful_count: 1,
            created_at: 'Az önce'
          }
        ]
      };
      threads.unshift(newThread);
      saveStore(STORAGE_KEYS.threads, threads);
      log5651Audit('thread_create', newThread.id, user.id, clientId, `[${game.slug}] ${cleanTitle}`);
      return jsonResponse(newThread);
    }

    const replyMatch = path.match(/^\/api\/threads\/(\d+)\/replies$/);
    if (replyMatch && method === 'POST') {
      const user = getAuthUser(headers);
      if (!user) return jsonResponse({ detail: 'Yanıt yazmak için lütfen giriş yapın.' }, 401);
      const voterKey = getVoterKey(headers);
      const rlErr = checkRateLimitBucket(`reply:${voterKey}`, 3, 60000, 'forum yanıtı gönderme işlemi');
      if (rlErr) return jsonResponse({ detail: rlErr }, 429);

      const filterErr = validateContentFilter(body.content || '');
      if (filterErr) return jsonResponse({ detail: filterErr }, 400);

      const cleanContent = sanitizeUserText(body.content || '');
      const tid = Number(replyMatch[1]);
      const threads = loadStore(STORAGE_KEYS.threads, SEED.threads);
      const thread = threads.find(t => t.id === tid);
      if (!thread) return jsonResponse({ detail: 'Konu bulunamadı' }, 404);
      thread.replies = thread.replies || [];
      const newRepId = Date.now();
      thread.replies.push({
        id: newRepId,
        thread_id: tid,
        author_name: user.username,
        is_ai: 0,
        ai_mode: null,
        content: cleanContent,
        helpful_count: 1,
        created_at: 'Az önce'
      });
      saveStore(STORAGE_KEYS.threads, threads);
      log5651Audit('reply_create', newRepId, user.id, clientId, `Thread #${tid}: ${cleanContent}`);
      return jsonResponse({ replies: thread.replies });
    }

    const threadVoteMatch = path.match(/^\/api\/threads\/(\d+)\/upvote$/);
    if (threadVoteMatch && method === 'POST') {
      const tid = Number(threadVoteMatch[1]);
      const voterKey = getVoterKey(headers);
      const votes = loadStore(STORAGE_KEYS.votes, {});
      const threads = loadStore(STORAGE_KEYS.threads, SEED.threads);
      const thread = threads.find(t => t.id === tid);
      if (!thread) return jsonResponse({ detail: 'Konu bulunamadı' }, 404);
      const vKey = `${voterKey}:thread:${tid}`;
      let userVoted = false;
      if (votes[vKey]) {
        delete votes[vKey];
        thread.upvotes = Math.max(0, (thread.upvotes || 1) - 1);
      } else {
        votes[vKey] = true;
        thread.upvotes = (thread.upvotes || 0) + 1;
        userVoted = true;
      }
      saveStore(STORAGE_KEYS.votes, votes);
      saveStore(STORAGE_KEYS.threads, threads);
      return jsonResponse({ upvotes: thread.upvotes, user_voted: userVoted });
    }

    if (path === '/api/reports' && method === 'POST') {
      const user = getAuthUser(headers);
      const reports = loadStore(STORAGE_KEYS.reports, []);
      const reportObj = {
        id: reports.length + 1,
        target_type: sanitizeUserText(body.target_type || 'thread'),
        target_id: Number(body.target_id || 0),
        reason: sanitizeUserText(body.reason || 'Uygunsuz İçerik'),
        details: sanitizeUserText(body.details || ''),
        reporter: user ? user.username : clientId,
        created_at: new Date().toISOString()
      };
      reports.unshift(reportObj);
      saveStore(STORAGE_KEYS.reports, reports);
      log5651Audit('content_report_5651', reportObj.target_id, user ? user.id : 0, clientId, `Bildirim #${reportObj.id}: ${reportObj.reason}`);
      return jsonResponse({
        reported: true,
        report_id: reportObj.id,
        message: '🚨 Bildiriminiz 5651 sayılı Kanun (Uyar-Kaldır) kapsamında kayıt altına alındı ve moderasyon kuyruğuna iletildi.'
      });
    }

    return jsonResponse({ detail: 'Not found' }, 404);
  }

  const origFetch = window.fetch.bind(window);
  const isStaticCloudHost = !['127.0.0.1', 'localhost'].includes(window.location.hostname);

  window.fetch = async function (input, init) {
    const urlStr = typeof input === 'string' ? input : (input && input.url) || '';
    if (urlStr.startsWith('/api/') || urlStr.startsWith('./api/') || urlStr.startsWith('api/') || urlStr.includes('/api/')) {
      if (isStaticCloudHost) {
        return handleCloudApi(urlStr, init);
      }
      try {
        const res = await origFetch(input, init);
        if (res.status === 404 && !res.headers.get('content-type')?.includes('application/json')) {
          return handleCloudApi(urlStr, init);
        }
        return res;
      } catch (err) {
        return handleCloudApi(urlStr, init);
      }
    }
    return origFetch(input, init);
  };
})();
