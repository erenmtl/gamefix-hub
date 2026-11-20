// OyunÇöz Frontend Controller (v4.0 - Security Hardened, KVKK/5651 Compliant, Guest Trial, Crash Log Analyzer & Troubleshooting Wizard)

function getOrCreateClientId() {
  let cid = localStorage.getItem('gamefix_client_id');
  if (!cid) {
    cid = 'cid_' + Math.random().toString(36).substring(2) + '_' + Date.now().toString(36);
    localStorage.setItem('gamefix_client_id', cid);
  }
  return cid;
}

// Dynamic relative base path for GitHub Pages subdirectory (/gamefix-hub/) and local FastAPI compatibility
const BASE_URL = (() => {
  const path = window.location.pathname || '/';
  if (path.endsWith('/index.html')) {
    return path.slice(0, -'index.html'.length);
  }
  return path.endsWith('/') ? path : path + '/';
})();

function apiUrl(endpoint) {
  const clean = String(endpoint || '').replace(/^\/+/, '');
  return `./${clean}`;
}

// --- SECTION 1.1 & 1.5: STRICT XSS SANITIZATION (DOMPurify + escapeHTML) & COMMAND WHITELIST ---

function escapeHTML(raw) {
  if (raw == null) return '';
  return String(raw)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function renderSafeForumUserText(raw) {
  // Stage 1.4 & 1.5: Never render user forum text as raw HTML; escape first, then linkify safe http(s) URLs with rel="ugc nofollow noopener"
  const escaped = escapeHTML(raw);
  if (!escaped) return '';
  return escaped.replace(
    /\b(https?:\/\/[^\s<>"'`]+)/gi,
    (match) => `<a href="${match}" target="_blank" rel="ugc nofollow noopener" class="text-[#88c0a8] hover:underline break-all">${match}</a>`
  );
}

function sanitizeHTML(dirtyHtml) {
  if (!dirtyHtml) return '';
  if (window.DOMPurify && typeof window.DOMPurify.sanitize === 'function') {
    return window.DOMPurify.sanitize(dirtyHtml, {
      USE_PROFILES: { html: true },
      FORBID_TAGS: ['script', 'iframe', 'object', 'embed', 'form', 'input', 'style', 'link', 'meta', 'base'],
      FORBID_ATTR: ['onerror', 'onload', 'onmouseover', 'onfocus', 'onmouseenter', 'onmouseleave', 'onsubmit']
    });
  }
  // Fallback sanitizer if CDN is blocked
  return String(dirtyHtml)
    .replace(/<\s*(script|iframe|object|embed|style|link|meta)[^>]*>[\s\S]*?<\s*\/\s*\1\s*>/gi, '')
    .replace(/<\s*(script|iframe|object|embed|style|link|meta)[^>]*\/?>/gi, '')
    .replace(/\bon\w+\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+)/gi, '')
    .replace(/javascript\s*:/gi, '');
}

const DANGEROUS_COMMAND_PATTERNS_CLIENT = [
  /\bformat\s+[a-zA-Z]:/gi,
  /\bdel\s+\/[fFsSqQ][\s\/a-zA-Z0-9.*:\\"-]*/gi,
  /\brd\s+\/[sSqQ][\s\/a-zA-Z0-9.*:\\"-]*/gi,
  /\brmdir\s+\/[sSqQ][\s\/a-zA-Z0-9.*:\\"-]*/gi,
  /\brm\s+-[rRfF]{1,4}\b/gi,
  /\bRemove-Item\b[^\n]*-Recurse[^\n]*-Force/gi,
  /\bdiskpart\b/gi,
  /\bcipher\s+\/w:/gi,
  /\bbcdedit\s+\/delete\b(?!value)/gi,
  /\breg\s+delete\s+HKLM\\(SAM|SECURITY|SYSTEM|SOFTWARE\\Microsoft\\Windows\s*NT)\b/gi
];

function sanitizeAiCommandsClient(mdText) {
  if (!mdText) return '';
  let cleaned = String(mdText);
  for (const pat of DANGEROUS_COMMAND_PATTERNS_CLIENT) {
    cleaned = cleaned.replace(pat, '[GÜVENLİK FİLTRESİ: ZARARLI SİSTEM KOMUTU ENGELLENDİ]');
  }
  return cleaned;
}

// Purge any legacy localStorage auth token (Stage 1.2: Session moved to HttpOnly + Secure + SameSite=Lax cookie)
try {
  localStorage.removeItem('gamefix_auth_token');
} catch (e) {}

let STATE = {
  games: [],
  issues: [],
  threads: [],
  suggestions: [],
  selectedGame: 'all',
  selectedCategory: 'all',
  searchQuery: '',
  activeTab: 'ai-lab',
  hasServerApiKey: false,
  clientId: getOrCreateClientId(),
  currentUser: null,
  pendingVerifyEmail: '',
  wizardByIssue: {},
  simulatedRamOverride: null
};

let resolveTimer = null;

function getAuthHeaders(extra = {}) {
  return {
    'X-Client-Id': STATE.clientId,
    ...extra
  };
}

document.addEventListener('DOMContentLoaded', async () => {
  initCookieConsent();
  initLiveSearchListeners();
  loadSavedHardwareSpecs();
  await checkCurrentSession();
  await fetchStatus();
  await fetchGames();
  await refreshRandomSuggestions();
  await applyUrlSeoParams();
  await Promise.all([fetchIssues(), fetchThreads()]);
  renderHomeShowcase();
  updateDynamicSEO();
});

function showToast(msg) {
  const toast = document.getElementById('toastNotification');
  const text = document.getElementById('toastMessage');
  text.textContent = msg;
  toast.classList.remove('hidden');
  setTimeout(() => {
    toast.classList.add('hidden');
  }, 3800);
}

function hexToRgba(hex, alpha) {
  const clean = hex.replace('#', '');
  const r = parseInt(clean.substring(0, 2), 16) || 94;
  const g = parseInt(clean.substring(2, 4), 16) || 156;
  const b = parseInt(clean.substring(4, 6), 16) || 136;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function applyGameTheme(accentHex) {
  document.documentElement.style.setProperty('--accent', accentHex);
  document.documentElement.style.setProperty('--accent-glow', hexToRgba(accentHex, 0.13));
}

function encodeBase64Utf8(str) {
  try {
    return btoa(unescape(encodeURIComponent(str)));
  } catch (e) {
    return '';
  }
}

function decodeBase64Utf8(b64) {
  try {
    return decodeURIComponent(escape(atob(b64)));
  } catch (e) {
    return '';
  }
}

function copyCodeFromBtn(btnEl, b64Code) {
  const raw = decodeBase64Utf8(b64Code);
  if (!raw) return;
  navigator.clipboard.writeText(raw);
  const origText = btnEl.innerHTML;
  btnEl.innerHTML = '✓ Kopyalandı!';
  btnEl.classList.add('text-[#a3d9c6]', 'border-[#5e9c88]');
  showToast('📋 Komut panoya kopyalandı!');
  setTimeout(() => {
    btnEl.innerHTML = origText;
    btnEl.classList.remove('text-[#a3d9c6]', 'border-[#5e9c88]');
  }, 2000);
}

function formatSimpleMarkdown(md) {
  if (!md) return '';
  const safeMd = sanitizeAiCommandsClient(md);
  let html = safeMd
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  const copyPlaceholders = [];
  const registerCopyBtn = (rawCode, labelText, isBlock, cleanDisplayCode, langLabel) => {
    const idx = copyPlaceholders.length;
    const b64 = encodeBase64Utf8(rawCode);
    if (isBlock) {
      copyPlaceholders.push(
        `<div class="my-3 rounded-xl overflow-hidden border border-white/15 bg-[#121721]"><div class="flex items-center justify-between px-3.5 py-1.5 bg-[#1a2230] border-b border-white/10"><span class="text-[10px] font-mono font-bold text-[#88c0a8] tracking-wider">${escapeHTML(langLabel)}</span><button type="button" onclick="copyCodeFromBtn(this, '${b64}')" class="text-[11px] font-semibold px-2.5 py-0.5 rounded bg-white/10 hover:bg-white/20 text-white border border-white/10 transition">📋 Komutu Kopyala</button></div><pre class="!my-0 !border-0 !rounded-none"><code>${cleanDisplayCode}</code></pre></div>`
      );
    } else {
      copyPlaceholders.push(
        `<span class="inline-flex items-center gap-1.5 bg-white/10 hover:bg-white/15 px-2 py-0.5 rounded-md border border-white/15 cursor-pointer group" onclick="copyCodeFromBtn(this, '${b64}')" title="📋 Komutu Kopyala"><code>${cleanDisplayCode}</code><span class="text-[10px] font-semibold text-[#a3d9c6] opacity-90 group-hover:opacity-100">📋 Komutu Kopyala</span></span>`
      );
    }
    return `%%COPY_PLACEHOLDER_${idx}%%`;
  };

  html = html.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, (_, lang, code) => {
    const cleanCode = code.trim();
    const unescapedCode = cleanCode
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&amp;/g, '&');
    const langLabel = (lang || 'Komut / Kod').toUpperCase();
    return registerCopyBtn(unescapedCode, '📋 Komutu Kopyala', true, cleanCode, langLabel);
  });

  html = html.replace(/`([^`]+)`/g, (_, inlineCode) => {
    const unescaped = inlineCode.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');
    const isCommandLike = /(\b(bcdedit|sfc|dism|sc\s+delete|netsh|regedit|msinfo32|services\.msc|sysdm\.cpl|rstrui\.exe|dxdiag|writecfg|gc\.buffer|Checkpoint-Computer|ipconfig|taskkill|winget|chkdsk)\b|[%\\\/]|--[a-z0-9-]+|-[a-z0-9]{2,})/i.test(unescaped);
    if (isCommandLike && unescaped.length >= 4) {
      return registerCopyBtn(unescaped, '📋 Komutu Kopyala', false, inlineCode, '');
    }
    return `<code>${inlineCode}</code>`;
  });

  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
  html = html.replace(/^## (.*$)/gim, '<h3>$1</h3>');
  html = html.replace(/^---$/gim, '<hr/>');
  html = html.replace(/^&gt; (.*$)/gim, '<blockquote>$1</blockquote>');
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');

  const lines = html.split('\n');
  let out = [];
  let inList = false;

  for (let line of lines) {
    const trimmed = line.trim();
    if (/^\d+\.\s+/.test(trimmed)) {
      if (!inList) {
        out.push('<ol>');
        inList = 'ol';
      }
      out.push(`<li>${trimmed.replace(/^\d+\.\s+/, '')}</li>`);
    } else if (/^[-*]\s+/.test(trimmed)) {
      if (!inList) {
        out.push('<ul>');
        inList = 'ul';
      }
      out.push(`<li>${trimmed.replace(/^[-*]\s+/, '')}</li>`);
    } else {
      if (inList) {
        out.push(`</${inList}>`);
        inList = false;
      }
      if (trimmed.startsWith('<h3') || trimmed.startsWith('%%COPY_PLACEHOLDER_') || trimmed.startsWith('<pre') || trimmed.startsWith('<hr') || trimmed.startsWith('<blockquote')) {
        out.push(trimmed);
      } else if (trimmed.length > 0) {
        out.push(`<p>${trimmed}</p>`);
      }
    }
  }
  if (inList) out.push(`</${inList}>`);

  let sanitizedOut = sanitizeHTML(out.join('\n'));
  sanitizedOut = sanitizedOut.replace(/%%COPY_PLACEHOLDER_(\d+)%%/g, (_, idxStr) => {
    return copyPlaceholders[Number(idxStr)] || '';
  });
  return sanitizedOut;
}

// --- FEATURE 3: SAFETY BANNER COMPONENT FOR CRITICAL SYSTEM OPERATIONS ---

function analyzeTechnicalRisk(combinedText) {
  const txt = String(combinedText || '');
  const risks = [];

  if (/\b(bios|uefi|secure\s*boot|tpm\s*2\.0|ftpm|ptt|csm|key\s*management)\b/i.test(txt)) {
    risks.push({
      badge: '⚠️ BIOS / UEFI & Secure Boot İşlemi',
      hint: 'Anakart BIOS/UEFI ayarlarında (Secure Boot, TPM 2.0, CSM) değişiklik yapılırken yanlış önyükleme modu seçilmesi sistem açılışını etkileyebilir.'
    });
  }
  if (/\b(regedit|kayıt\s*defteri|hkey_|dword)\b/i.test(txt)) {
    risks.push({
      badge: '⚠️ Windows Kayıt Defteri (Regedit)',
      hint: 'Kayıt Defteri anahtarlarında yapılacak değişiklikler sistem davranışını doğrudan etkiler.'
    });
  }
  if (/\b(bcdedit|sc\s+delete|nointegritychecks|sysdm\.cpl|pagefile|sanal\s*bellek)\b/i.test(txt)) {
    risks.push({
      badge: '⚠️ Çekirdek / Komut Satırı (CMD & bcdedit)',
      hint: 'Yönetici Komut İstemi (bcdedit, servis silme veya sanal bellek) işlemleri çekirdek yapılandırmasını değiştirir.'
    });
  }
  if (/\b(ddu|display\s*driver\s*uninstaller|güvenli\s*mod|safe\s*mode|sürücü\s*sil)\b/i.test(txt)) {
    risks.push({
      badge: '⚠️ Temiz Sürücü Kaldırma (DDU / Güvenli Mod)',
      hint: 'Ekran kartı veya sistem sürücüsünü tamamen kaldırmadan önce güncel kurulum paketini indirdiğinizden emin olun.'
    });
  }
  return risks;
}

function buildRiskyCommandNotesHtml(rawText) {
  const txt = String(rawText || '');
  const notes = [];

  if (/\bbcdedit\b/i.test(txt)) {
    notes.push({
      cmd: 'bcdedit',
      what: 'Windows Önyükleme Yapılandırma Verilerini (BCD) değiştirerek çekirdek doğrulama veya önyükleme parametrelerini günceller.',
      risk: 'Yanlış parametre kullanımı Windows açılış davranışını veya sürücü imza doğrulamasını etkileyebilir.',
      undo: 'Yönetici CMD ekranında varsayılan önyükleme bütünlüğüne dönmek için: bcdedit /deletevalue nointegritychecks ve bcdedit /set testsigning off komutlarını çalıştırıp sistemi yeniden başlatın.'
    });
  }
  if (/\bsc\s+delete\b/i.test(txt)) {
    notes.push({
      cmd: 'sc delete (vgc / vgk)',
      what: 'Belirtilen Windows arka plan hizmetini (örn. Riot Vanguard vgc/vgk) kayıt defterinden ve hizmet listesinden kaldırır.',
      risk: 'Hizmet silindikten sonra ilgili oyun veya anti-cheat istemcisi onarım yapılana kadar başlatılamaz.',
      undo: 'Riot İstemcisi (veya ilgili oyun başlatıcısı) üzerinden "Onar / Güncelle" seçeneğini çalıştırarak hizmeti temiz şekilde yeniden kurun ve bilgisayarı yeniden başlatın.'
    });
  }
  if (/\b(regedit|kayıt\s*defteri|hkey_|dword|tdrdelay)\b/i.test(txt)) {
    notes.push({
      cmd: 'regedit (Kayıt Defteri)',
      what: 'Windows Kayıt Defteri (Registry) altındaki sistem veya ekran kartı zaman aşımı (TdrDelay vb.) anahtarlarını düzenler.',
      risk: 'Hatalı anahtar silinmesi veya yanlış DWORD değeri girilmesi sistem kararlılığını bozabilir.',
      undo: 'Değişiklik öncesi Regedit üzerinden "Dosya > Ver (.reg)" ile aldığınız yedeğe çift tıklayarak veya oluşturduğunuz DWORD değerini silip bilgisayarı yeniden başlatarak geri alabilirsiniz.'
    });
  }
  if (/\bnetsh\s+int\s+ip\s+reset\b/i.test(txt)) {
    notes.push({
      cmd: 'netsh int ip reset',
      what: 'Windows TCP/IP ağ yığınını (IPv4/IPv6 soket ve yönlendirme tablolarını) fabrika varsayılanlarına sıfırlar.',
      risk: 'Ağ bağdaştırıcınızda elle (statik) girilmiş IP veya özel DNS adresleri varsa otomatik (DHCP) moda döner.',
      undo: 'Denetim Masası > Ağ ve Paylaşım Merkezi > Bağdaştırıcı Ayarları üzerinden özel DNS/statik IP ayarlarınızı yeniden girebilir veya Sistem Geri Yükleme Noktasına dönebilirsiniz.'
    });
  }

  if (notes.length === 0) return '';

  return notes.map(n => `
    <div class="rounded-xl p-3.5 bg-[#1b1922] border border-amber-400/40 text-xs space-y-1.5 shadow-sm">
      <div class="font-extrabold text-amber-200 flex items-center gap-1.5">
        <span>⚠️ Kritik Komut Bilgilendirmesi:</span>
        <code class="px-1.5 py-0.5 rounded bg-black/40 text-amber-100 font-mono">${escapeHTML(n.cmd)}</code>
      </div>
      <div class="grid grid-cols-1 gap-1 text-gray-200 leading-relaxed">
        <div><strong class="text-[#a3d9c6]">Ne yapar?:</strong> ${escapeHTML(n.what)}</div>
        <div><strong class="text-amber-300">Risk:</strong> ${escapeHTML(n.risk)}</div>
        <div><strong class="text-sky-300">Geri alma:</strong> ${escapeHTML(n.undo)}</div>
      </div>
    </div>
  `).join('');
}

function buildSafetyBannerHtml(combinedText) {
  const risks = analyzeTechnicalRisk(combinedText);
  if (risks.length === 0) return '';

  const restoreCmdRaw = 'Checkpoint-Computer -Description "OyunCoz_Yedek"';
  const restoreCmdB64 = encodeBase64Utf8(restoreCmdRaw);
  const rstruiB64 = encodeBase64Utf8('rstrui.exe');

  const badgesHtml = risks.map(r => `
    <span class="text-[11px] font-bold px-2.5 py-0.5 rounded-md bg-amber-500/20 text-amber-200 border border-amber-400/35">
      ${r.badge}
    </span>
  `).join('');

  return `
    <div class="rounded-xl p-4 bg-gradient-to-r from-amber-500/15 via-[#261f16] to-[#1d2430] border border-amber-400/45 space-y-2.5 shadow-md">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <div class="flex items-center gap-2">
          <span class="text-base">🛡️</span>
          <span class="text-xs sm:text-sm font-extrabold text-amber-200">
            Teknik Risk &amp; Sistem Geri Yükleme Noktası Uyarısı
          </span>
        </div>
        <div class="flex flex-wrap gap-1.5">
          ${badgesHtml}
        </div>
      </div>
      <p class="text-xs text-gray-200 leading-relaxed">
        Bu çözüm rehberi <strong>${risks[0].hint}</strong> İşlemlere başlamadan önce tek tıkla <strong>Sistem Geri Yükleme Noktası</strong> oluşturmanız önerilir:
      </p>
      <div class="bg-[#141923]/90 border border-amber-400/30 rounded-lg px-3 py-2 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <code class="text-xs font-mono text-amber-200">Checkpoint-Computer -Description "OyunCoz_Yedek"</code>
        <div class="flex flex-wrap items-center gap-2 shrink-0">
          <button
            type="button"
            onclick="copyCodeFromBtn(this, '${restoreCmdB64}')"
            class="text-[11px] font-bold px-3 py-1 rounded-lg bg-amber-500/25 hover:bg-amber-500/40 text-amber-100 border border-amber-400/40 transition flex items-center gap-1"
          >
            <span>📋 Komutu Kopyala</span>
          </button>
          <button
            type="button"
            onclick="copyCodeFromBtn(this, '${rstruiB64}')"
            class="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-white/5 hover:bg-white/10 text-gray-200 border border-white/10 transition flex items-center gap-1"
          >
            <span>📋 rstrui.exe</span>
          </button>
        </div>
      </div>
    </div>
  `;
}

// --- FEATURE 2: AUTOMATIC HARDWARE DETECTION & FORM AUTO-FILLER (WebGL + Navigator API) ---

let DETECTED_HARDWARE_CACHE = null;

function cleanWebGLRendererName(rawRenderer) {
  if (!rawRenderer) return 'Standart DirectX/Vulkan GPU';
  let s = String(rawRenderer).trim();
  // Extract inside ANGLE (Vendor, Renderer, Version)
  const angleMatch = s.match(/ANGLE\s*\([^,]+,\s*([^,]+),/i);
  if (angleMatch && angleMatch[1]) {
    s = angleMatch[1].trim();
  }
  s = s
    .replace(/Direct3D11.*$/i, '')
    .replace(/vs_\d+_\d+.*$/i, '')
    .replace(/\(0x[0-9A-Fa-f]+\)/g, '')
    .replace(/\s+/g, ' ')
    .trim();
  return s || 'Masaüstü/Mobil GPU';
}

async function detectClientHardware() {
  // Stage 3.11: Runs ONLY when user explicitly clicks "Donanımımı Algıla" button
  let gpuName = 'Tespit Edilemedi (WebGL)';
  try {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl2') || canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    if (gl) {
      const dbg = gl.getExtension('WEBGL_debug_renderer_info');
      const rawRenderer = dbg ? gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER);
      gpuName = cleanWebGLRendererName(rawRenderer);
      const loseCtx = gl.getExtension('WEBGL_lose_context');
      if (loseCtx) loseCtx.loseContext();
    }
  } catch (e) {}

  // 2. OS & Architecture Detection via UserAgentData / UserAgent
  let osName = 'Windows 10/11 64-bit';
  try {
    const ua = navigator.userAgent || '';
    if (navigator.userAgentData && navigator.userAgentData.getHighEntropyValues) {
      const hev = await navigator.userAgentData.getHighEntropyValues(['platform', 'platformVersion', 'architecture']);
      if (hev.platform === 'Windows') {
        const majorVer = parseInt((hev.platformVersion || '0').split('.')[0], 10);
        osName = majorVer >= 13 ? 'Windows 11 (64-bit)' : 'Windows 10 (64-bit)';
      } else if (hev.platform) {
        osName = `${hev.platform} ${hev.architecture || ''}`.trim();
      }
    } else if (/Windows NT 10\.0/i.test(ua)) {
      osName = 'Windows 11 / 10 (64-bit)';
    } else if (/Mac OS X/i.test(ua)) {
      osName = 'macOS';
    } else if (/Linux/i.test(ua)) {
      osName = 'Linux (Proton/SteamOS)';
    } else if (/Android/i.test(ua)) {
      osName = 'Android';
    } else if (/iPhone|iPad/i.test(ua)) {
      osName = 'iOS';
    }
  } catch (e) {}

  // 3. CPU Logical Cores (Threads)
  const cores = navigator.hardwareConcurrency ? `${navigator.hardwareConcurrency} Çekirdek/Thread CPU` : 'Çok Çekirdekli CPU';

  // 4. RAM Estimate
  let ram = '16GB RAM';
  if (navigator.deviceMemory) {
    ram = navigator.deviceMemory >= 8 ? '16GB+ RAM' : `${navigator.deviceMemory}GB RAM`;
  }

  const summary = `${osName} | ${gpuName} | ${cores} | ${ram}`;
  DETECTED_HARDWARE_CACHE = { gpu: gpuName, cpu: cores, os: osName, ram, summary };
  return DETECTED_HARDWARE_CACHE;
}

async function triggerHardwareAutoDetect() {
  const hw = await detectClientHardware();
  const box = document.getElementById('hardwareConfirmBox');
  if (box) {
    document.getElementById('hwDetectGpuText').textContent = hw.gpu;
    document.getElementById('hwDetectCpuText').textContent = hw.cpu;
    document.getElementById('hwDetectOsText').textContent = hw.os;
    document.getElementById('hwDetectRamText').textContent = hw.ram;
    document.getElementById('hwDetectEditableSummary').value = hw.summary;
    switchTab('ai-lab');
    box.classList.remove('hidden');
    box.scrollIntoView({ behavior: 'smooth', block: 'center' });
    showToast('🖥️ Donanımınız WebGL & Sistem API ile tespit edildi. Onaylayarak formlara doldurabilirsiniz.');
  }
}

function dismissHardwareConfirmBox() {
  const box = document.getElementById('hardwareConfirmBox');
  if (box) box.classList.add('hidden');
}

function isFunctionalCookieAllowed() {
  try {
    const raw = localStorage.getItem('oyuncoz_cookie_consent');
    if (!raw) return true;
    const parsed = JSON.parse(raw);
    return parsed.functional !== false;
  } catch (e) {
    return true;
  }
}

async function confirmAndApplyDetectedHardware() {
  const summaryInp = document.getElementById('hwDetectEditableSummary');
  const finalSpecs = (summaryInp && summaryInp.value.trim()) || (DETECTED_HARDWARE_CACHE && DETECTED_HARDWARE_CACHE.summary) || '';
  if (!finalSpecs) return;

  ['aiLabSpecs', 'modalThreadSpecs', 'regSpecs', 'profileSpecsInput'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = finalSpecs;
  });

  if (isFunctionalCookieAllowed()) {
    try {
      localStorage.setItem('oyuncoz_detected_specs', finalSpecs);
    } catch (e) {}
  }

  if (STATE.currentUser) {
    try {
      await fetch('/api/auth/profile', {
        method: 'PUT',
        credentials: 'same-origin',
        headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({
          system_specs: finalSpecs,
          favorite_game: STATE.currentUser.favorite_game || 'valorant'
        })
      });
      STATE.currentUser.system_specs = finalSpecs;
    } catch (e) {}
  }

  dismissHardwareConfirmBox();
  evaluateHardwareCompatibility();
  showToast('✓ Donanım bilgileriniz tüm arıza formlarına ve profilinize otomatik dolduruldu!');
}

async function autoFillSingleSpecsInput(inputId) {
  const hw = await detectClientHardware();
  const target = document.getElementById(inputId);
  if (target) {
    target.value = hw.summary;
  }
  ['aiLabSpecs', 'modalThreadSpecs', 'regSpecs', 'profileSpecsInput'].forEach(id => {
    const el = document.getElementById(id);
    if (el && !el.value) el.value = hw.summary;
  });
  if (isFunctionalCookieAllowed()) {
    try {
      localStorage.setItem('oyuncoz_detected_specs', hw.summary);
    } catch (e) {}
  }
  evaluateHardwareCompatibility();
  showToast(`🖥️ Algılanan donanım dolduruldu: ${hw.gpu}`);
}

function loadSavedHardwareSpecs() {
  if (!isFunctionalCookieAllowed()) return;
  try {
    const saved = localStorage.getItem('oyuncoz_detected_specs');
    if (saved) {
      ['aiLabSpecs', 'modalThreadSpecs', 'regSpecs', 'profileSpecsInput'].forEach(id => {
        const el = document.getElementById(id);
        if (el && !el.value) el.value = saved;
      });
    }
  } catch (e) {}
  evaluateHardwareCompatibility();
}

// --- KILLER FEATURE 4: HARDWARE COMPATIBILITY & BOTTLENECK WARNING BADGE + SHORT TAG EXTRACTOR ---

function getCurrentUserSpecsString() {
  if (STATE.simulatedRamOverride) return STATE.simulatedRamOverride;
  if (STATE.currentUser && STATE.currentUser.system_specs) return STATE.currentUser.system_specs;
  const aiInp = document.getElementById('aiLabSpecs');
  if (aiInp && aiInp.value.trim()) return aiInp.value.trim();
  try {
    return localStorage.getItem('oyuncoz_detected_specs') || '';
  } catch (e) {
    return '';
  }
}

function extractShortHardwareTag(rawSpecs) {
  const specs = String(rawSpecs || getCurrentUserSpecsString() || '').trim();
  if (!specs) return 'Win 11 / RTX 3060';
  let osLabel = 'Win 11';
  if (/win(?:dows)?\s*10/i.test(specs)) osLabel = 'Win 10';
  else if (/win(?:dows)?\s*11/i.test(specs)) osLabel = 'Win 11';
  else if (/mac/i.test(specs)) osLabel = 'macOS';
  else if (/linux|steamos/i.test(specs)) osLabel = 'Linux';

  let gpuLabel = 'DirectX GPU';
  const gpuMatch = specs.match(/\b(RTX\s*\d{3,4}(?:\s*Ti|\s*SUPER)?|GTX\s*\d{3,4}(?:\s*Ti|\s*SUPER)?|RX\s*\d{3,4}(?:\s*XT|\s*XTX)?|Arc\s*A\d{3}|Intel\s*(?:Iris|UHD)|Radeon\s*\w+|Apple\s*M\d)/i);
  if (gpuMatch && gpuMatch[1]) {
    gpuLabel = gpuMatch[1].replace(/\s+/g, ' ').trim();
  }
  return `${osLabel} / ${gpuLabel}`;
}

function simulateEightGbRamWarning() {
  const current = getCurrentUserSpecsString() || 'Windows 11, Ryzen 5 5600, RTX 3060';
  const simulated = current.replace(/\b\d+\s*\+?\s*GB\s*RAM\b/i, '').trim() + ' | 8 GB RAM';
  STATE.simulatedRamOverride = simulated;
  const aiInp = document.getElementById('aiLabSpecs');
  if (aiInp) aiInp.value = simulated;
  evaluateHardwareCompatibility();
  showToast('⚠️ 8 GB RAM darboğaz testi aktif edildi!');
}

function clearSimulatedHardwareOverride() {
  STATE.simulatedRamOverride = null;
  loadSavedHardwareSpecs();
  evaluateHardwareCompatibility();
  showToast('✓ Orijinal donanım profilinize dönüldü.');
}

function evaluateHardwareCompatibility() {
  const banner = document.getElementById('hardwareBottleneckBanner');
  if (!banner) return;

  const specs = getCurrentUserSpecsString();
  const slug = STATE.selectedGame || 'all';
  const gameObj = STATE.games.find(g => g.slug === slug);
  const gameTitle = gameObj ? gameObj.name : 'Seçili Oyun';

  // Parse RAM in GB solely from user-saved/confirmed specs (never probe device hardware automatically on load)
  let ramGb = null;
  const ramMatch = specs.match(/\b(\d{1,3})\s*\+?\s*GB\s*(?:RAM|Bellek)?/i);
  if (ramMatch) {
    ramGb = parseInt(ramMatch[1], 10);
  }

  const heavyRamGames = [
    'gtav-fivem', 'mount-and-blade-2-bannerlord', 'rust', 'escape-from-tarkov',
    'hogwarts-legacy', 'starfield', 'ark-survival-ascended', 'cities-skylines-2',
    'victoria-3', 'beamng-drive', 'black-myth-wukong', 'cyberpunk-2077', 'red-dead-redemption-2', 'cod-warzone'
  ];
  const isHeavyRamGame = slug === 'all' || heavyRamGames.includes(slug);
  const isLowRam = ramGb !== null && ramGb <= 8;
  const isIntegratedGpu = /\b(intel\s*(uhd|hd|iris)|vega\s*\d|integrated|dahili)\b/i.test(specs);
  const isWin11VanguardGame = ['valorant', 'lol'].includes(slug) && /win(?:dows)?\s*11/i.test(specs);

  const warnings = [];
  if (isLowRam && isHeavyRamGame) {
    const targetLabel = slug === 'all' ? 'FiveM, Bannerlord, Rust ve UE5 oyunlarında' : `<strong>${escapeHTML(gameTitle)}</strong> oyununda`;
    warnings.push({
      type: 'critical',
      title: `⚠️ Donanım Uyarısı: ${ramGb} GB RAM bu oyunda ani takılmalara (stutter) yol açabilir, sanal bellek adımını uygulayın`,
      detail: `Kayıtlı sisteminizde <strong>${ramGb} GB RAM</strong> tespit edildi. ${targetLabel} yüksek doku/varlık akışı nedeniyle 8 GB RAM sınırında anlık FPS düşmesi (drop) ve bellek çökmesi yaşanabilir. Windows Sanal Bellek (Pagefile / <code>sysdm.cpl</code>) boyutunu <strong>16384 MB - 24576 MB</strong> olarak sabitlemeniz önerilir.`,
      cmd: 'sysdm.cpl'
    });
  }

  if (isIntegratedGpu && slug !== 'all') {
    warnings.push({
      type: 'warning',
      title: `⚠️ GPU Darboğaz Uyarısı: Paylaşımlı / Dahili GPU Tespit Edildi`,
      detail: `<strong>${escapeHTML(gameTitle)}</strong> için Windows Grafik Ayarları üzerinden yüksek performanslı harici GPU'yu seçtiğinizden ve doku kalitesini Düşük/Orta seviyede tuttuğunuzdan emin olun.`,
      cmd: 'ms-settings:display-advancedgraphics'
    });
  }

  if (isWin11VanguardGame && warnings.length === 0) {
    warnings.push({
      type: 'info',
      title: `🖥️ Donanım Uyumluluk Kontrolü (${escapeHTML(extractShortHardwareTag(specs))}): Windows 11 + Riot Vanguard Aktif`,
      detail: `Windows 11 profilinizde <strong>${escapeHTML(gameTitle)}</strong> için UEFI Secure Boot ve TPM 2.0 zorunludur. VAN 9003 / VAN 1067 hatası alırsanız aşağıdaki <code>msinfo32</code> komutuyla Güvenli Önyükleme durumunu kontrol edin.`,
      cmd: 'msinfo32'
    });
  }

  if (warnings.length === 0) {
    // Show a compact hardware compatibility status bar with a 1-click "8 GB RAM Stutter Uyarısını Test Et" button on FiveM/Bannerlord/heavy games
    if (heavyRamGames.includes(slug)) {
      const shortHw = extractShortHardwareTag(specs);
      banner.className = 'rounded-2xl p-3.5 bg-[#192230] border border-[#5e9c88]/35 flex flex-col sm:flex-row sm:items-center justify-between gap-3';
      banner.innerHTML = `
        <div class="flex items-center gap-2.5 text-xs text-gray-200">
          <span class="px-2 py-0.5 rounded-md bg-[#5e9c88]/20 text-[#a3d9c6] border border-[#5e9c88]/30 font-bold">✓ Donanım Uyumlu (${escapeHTML(shortHw)})</span>
          <span><strong>${escapeHTML(gameTitle)}</strong> için bellek ve GPU profiliniz yeterli görünüyor.</span>
        </div>
        <button
          type="button"
          onclick="simulateEightGbRamWarning()"
          class="text-[11px] font-semibold px-3 py-1 rounded-lg bg-amber-500/15 hover:bg-amber-500/25 text-amber-200 border border-amber-400/30 transition shrink-0"
        >
          🧪 8 GB RAM Darboğaz Rozetini Test Et
        </button>
      `;
      banner.classList.remove('hidden');
      return;
    }
    banner.classList.add('hidden');
    banner.innerHTML = '';
    return;
  }

  const w = warnings[0];
  const cmdB64 = encodeBase64Utf8(w.cmd || 'sysdm.cpl');
  const isCrit = w.type === 'critical' || w.type === 'warning';
  banner.className = isCrit
    ? 'rounded-2xl p-4 bg-gradient-to-r from-amber-500/18 via-[#261f16] to-[#1b2230] border border-amber-400/50 space-y-2 shadow-lg'
    : 'rounded-2xl p-4 bg-[#192230] border border-[#5e9c88]/40 space-y-2 shadow-md';

  banner.innerHTML = `
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
      <div class="text-xs sm:text-sm font-extrabold ${isCrit ? 'text-amber-200' : 'text-[#a3d9c6]'}">
        ${w.title}
      </div>
      <div class="flex flex-wrap items-center gap-2 shrink-0">
        <button
          type="button"
          onclick="copyCodeFromBtn(this, '${cmdB64}')"
          class="text-[11px] font-bold px-3 py-1 rounded-lg bg-amber-500/25 hover:bg-amber-500/40 text-amber-100 border border-amber-400/40 transition"
        >
          📋 Komutu Kopyala (${escapeHTML(w.cmd)})
        </button>
        ${STATE.simulatedRamOverride ? `
          <button type="button" onclick="clearSimulatedHardwareOverride()" class="text-[11px] px-2.5 py-1 rounded-lg bg-white/10 hover:bg-white/15 text-gray-200">
            Sıfırla
          </button>
        ` : ''}
      </div>
    </div>
    <p class="text-xs text-gray-200 leading-relaxed">${w.detail}</p>
  `;
  banner.classList.remove('hidden');
}

// --- SMART GAME RECOGNITION & RANDOM WORLD SUGGESTIONS ---

async function refreshRandomSuggestions() {
  try {
    const res = await fetch('./api/games/suggestions?count=6');
    const data = await res.json();
    STATE.suggestions = data.suggestions || [];
    renderSuggestionChips();
  } catch (err) {
    console.error('Suggestions error:', err);
  }
}

function fallbackCover(slug, color, subtitle) {
  if (window.makeGameCoverDataUri) {
    return window.makeGameCoverDataUri(slug, color, subtitle);
  }
  return './static/logo.svg';
}

function resolveSafeCoverUrl(rawUrl, slugOrName, accentColor, subtitle) {
  return fallbackCover(slugOrName, accentColor, subtitle);
}

function renderSuggestionChips() {
  const aiContainer = document.getElementById('aiLabSuggestionsContainer');
  const modalContainer = document.getElementById('modalSuggestionsContainer');
  const addContainer = document.getElementById('addGameSuggestionsContainer');

  const buildChips = (inputId, hintId, errorInputId) => STATE.suggestions.map(s => {
    const safeSrc = resolveSafeCoverUrl(s.image_url, s.name || s.slug, '#5e9c88', s.genre);
    const safeNameAttr = (s.name || s.slug || 'game').replace(/'/g, "\\'");
    return `
      <button
        type="button"
        onclick="pickSuggestedGame('${safeNameAttr}', '${(s.hint || '').replace(/'/g, "\\'")}', '${inputId}', '${hintId}', '${errorInputId || ''}')"
        class="text-xs px-2.5 py-1.5 rounded-xl bg-[#212936] hover:bg-[#2a3446] text-gray-200 border border-white/10 transition flex items-center gap-2"
      >
        <img loading="lazy" decoding="async"
          src="${safeSrc}"
          onerror="this.onerror=null;this.src=fallbackCover('${safeNameAttr}','#5e9c88')"
          alt="${escapeHTML(s.name)}"
          class="w-7 h-5 rounded object-cover border border-white/10 shrink-0"
        />
        <span class="font-bold text-white">${escapeHTML(s.name)}</span>
        <span class="text-[10px] text-gray-400">(${escapeHTML(s.genre)})</span>
      </button>
    `;
  }).join('');

  if (aiContainer) aiContainer.innerHTML = buildChips('aiLabGameInput', 'aiLabSmartHint', 'aiLabErrorCode');
  if (modalContainer) modalContainer.innerHTML = buildChips('modalThreadGameInput', 'modalGameSmartHint', 'modalThreadErrorCode');
  if (addContainer) addContainer.innerHTML = buildChips('newGameQueryInput', 'addGameSmartHint', '');
}

function pickSuggestedGame(gameName, sampleError, inputId, hintId, errorInputId) {
  const inp = document.getElementById(inputId);
  if (inp) {
    inp.value = gameName;
    previewSmartGameRecognition(gameName, hintId);
  }
  if (errorInputId && sampleError) {
    const errInp = document.getElementById(errorInputId);
    if (errInp && !errInp.value) {
      errInp.value = sampleError.split(',')[0].trim();
    }
  }
}

function previewSmartGameRecognition(rawValue, hintElementId) {
  const hintEl = document.getElementById(hintElementId);
  if (!hintEl) return;

  const trimmed = (rawValue || '').trim();
  if (!trimmed) {
    hintEl.textContent = '';
    return;
  }

  clearTimeout(resolveTimer);
  resolveTimer = setTimeout(async () => {
    try {
      const res = await fetch(`/api/games/resolve?q=${encodeURIComponent(trimmed)}`);
      const info = await res.json();
      if (!info || info.status === 'empty') {
        hintEl.textContent = '';
        return;
      }

      if (info.status === 'existing') {
        if (info.corrected_from) {
          hintEl.innerHTML = `✨ <strong>"${info.corrected_from}"</strong> → <strong>${info.canonical_name}</strong> olarak algılandı (Mevcut Ekran)`;
        } else {
          hintEl.innerHTML = `✓ <strong>${info.canonical_name}</strong> (${info.category} • ${info.developer})`;
        }
      } else {
        if (info.corrected_from) {
          hintEl.innerHTML = `✨ <strong>"${info.corrected_from}"</strong> → <strong>${info.canonical_name}</strong> (${info.developer}) olarak anlaşıldı! Yeni ekran oluşturulacak.`;
        } else {
          hintEl.innerHTML = `✨ <strong>${info.canonical_name}</strong> (${info.category}) — Özel oyun ekranı otomatik oluşturulacak!`;
        }
      }
    } catch (err) {
      console.error(err);
    }
  }, 180);
}

function requireMemberAuth(actionDesc = 'Bu özelliği kullanmak') {
  if (!STATE.currentUser) {
    showToast(`🔒 ${actionDesc} için lütfen oturum açın veya ücretsiz kayıt olun.`);
    openAuthModal('login');
    return false;
  }
  return true;
}

function openAddGameModal() {
  if (!requireMemberAuth('Yeni oyun sayfası eklemek')) return;
  ensureLazyModalMounted('addGameModal');
  document.getElementById('newGameQueryInput').value = '';
  document.getElementById('addGameSmartHint').textContent = '';
  refreshRandomSuggestions();
  document.getElementById('addGameModal').classList.remove('hidden');
  setTimeout(() => document.getElementById('newGameQueryInput').focus(), 80);
}

function closeAddGameModal() {
  document.getElementById('addGameModal').classList.add('hidden');
}

async function submitAddNewGame(e) {
  e.preventDefault();
  if (!requireMemberAuth('Yeni oyun eklemek')) return;
  const q = document.getElementById('newGameQueryInput').value.trim();
  if (!q) return;

  const btn = document.getElementById('addGameSubmitBtn');
  const origText = btn.textContent;
  btn.disabled = true;
  btn.textContent = '⏳ Oyun Tanınıyor ve Sayfa Oluşturuluyor...';

  try {
    const res = await fetch('/api/games/create', {
      method: 'POST',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ game_query: q })
    });
    const data = await res.json();
    if (!res.ok) {
      showToast(data.detail || 'Oyun oluşturulamadı.');
      return;
    }

    const game = data.game;
    closeAddGameModal();
    await fetchGames();
    await selectGame(game.slug);
    switchTab('issues');

    if (game.corrected_from) {
      showToast(`"${game.corrected_from}" → ${game.name} olarak algılandı ve özel ekranı açıldı!`);
    } else if (game.was_created) {
      showToast(`${game.name} için yeni oyun ekranı ve forum çözümleri oluşturuldu!`);
    } else {
      showToast(`${game.name} ekranına geçildi.`);
    }
  } catch (err) {
    showToast('Oyun eklenirken bir hata oluştu.');
  } finally {
    btn.disabled = false;
    btn.textContent = origText;
  }
}

// --- 2-STEP EMAIL VERIFICATION & AUTHENTICATION (HttpOnly Cookie Session) ---

async function checkCurrentSession() {
  try {
    const res = await fetch('/api/auth/me', {
      credentials: 'same-origin',
      headers: getAuthHeaders()
    });
    if (res.ok) {
      const data = await res.json();
      STATE.currentUser = data.user;
    } else {
      STATE.currentUser = null;
    }
  } catch (err) {
    STATE.currentUser = null;
  }
  updateAuthUI();
}

function hasGuestUsedFreeTrial() {
  try {
    return localStorage.getItem('oyuncoz_guest_ai_trial_used') === '1';
  } catch (e) {
    return false;
  }
}

function markGuestFreeTrialUsed() {
  try {
    localStorage.setItem('oyuncoz_guest_ai_trial_used', '1');
  } catch (e) {}
}

function updateAuthUI() {
  const guestArea = document.getElementById('guestAuthArea');
  const userArea = document.getElementById('userProfileArea');
  const aiGuestLock = document.getElementById('aiLabGuestLock');
  const aiGuestTrialText = document.getElementById('aiLabGuestTrialText');
  const aiMemberArea = document.getElementById('aiLabMemberArea');

  if (aiMemberArea) aiMemberArea.classList.remove('hidden');

  if (STATE.currentUser) {
    guestArea.classList.add('hidden');
    userArea.classList.remove('hidden');
    document.getElementById('navUserAvatar').textContent = STATE.currentUser.avatar_initials || 'OY';
    document.getElementById('navUsername').textContent = STATE.currentUser.username;

    if (aiGuestLock) aiGuestLock.classList.add('hidden');

    const aiSpecs = document.getElementById('aiLabSpecs');
    if (aiSpecs && !aiSpecs.value && STATE.currentUser.system_specs) {
      aiSpecs.value = STATE.currentUser.system_specs;
    }
  } else {
    guestArea.classList.remove('hidden');
    userArea.classList.add('hidden');

    if (aiGuestLock) {
      aiGuestLock.classList.remove('hidden');
      if (aiGuestTrialText) {
        if (hasGuestUsedFreeTrial()) {
          aiGuestTrialText.textContent = '🔒 Ücretsiz Misafir Hakkınız Kullanıldı (2. Sorgu İçin Üye Olun)';
        } else {
          aiGuestTrialText.textContent = '🎁 Misafir Hakkı: 1 Ücretsiz AI Analizi';
        }
      }
    }
  }
  evaluateHardwareCompatibility();
}

function showAuthAlert(msg, type = 'error') {
  const el = document.getElementById('authModalAlert');
  if (!el) return;
  el.classList.remove('hidden');
  if (type === 'success') {
    el.className = 'rounded-xl p-3 text-xs leading-relaxed border bg-[#5e9c88]/20 border-[#5e9c88]/40 text-[#a3d9c6]';
  } else if (type === 'info') {
    el.className = 'rounded-xl p-3 text-xs leading-relaxed border bg-[#5586ad]/20 border-[#5586ad]/40 text-[#acc8e0]';
  } else {
    el.className = 'rounded-xl p-3 text-xs leading-relaxed border bg-[#a8555d]/20 border-[#a8555d]/40 text-[#f2c6cb]';
  }
  el.innerHTML = msg;
}

function clearAuthAlert() {
  const el = document.getElementById('authModalAlert');
  if (el) {
    el.classList.add('hidden');
    el.innerHTML = '';
  }
}

function openAuthModal(tab = 'login') {
  ensureLazyModalMounted('authModal');
  clearAuthAlert();
  switchAuthTab(tab);
  document.getElementById('authModal').classList.remove('hidden');
}

function closeAuthModal() {
  clearAuthAlert();
  document.getElementById('authModal').classList.add('hidden');
}

function switchAuthTab(tab) {
  clearAuthAlert();
  const loginBtn = document.getElementById('authTabLogin');
  const regBtn = document.getElementById('authTabRegister');
  const loginForm = document.getElementById('loginForm');
  const regStep1 = document.getElementById('registerFormStep1');
  const regStep2 = document.getElementById('registerFormStep2');

  if (tab === 'login') {
    loginBtn.className = 'text-sm font-bold text-white border-b-2 border-[#5e9c88] pb-1';
    regBtn.className = 'text-sm font-bold text-gray-400 border-b-2 border-transparent pb-1';
    loginForm.classList.remove('hidden');
    regStep1.classList.add('hidden');
    regStep2.classList.add('hidden');
  } else {
    regBtn.className = 'text-sm font-bold text-white border-b-2 border-[#5e9c88] pb-1';
    loginBtn.className = 'text-sm font-bold text-gray-400 border-b-2 border-transparent pb-1';
    loginForm.classList.add('hidden');
    regStep1.classList.remove('hidden');
    regStep2.classList.add('hidden');
  }
}

function backToRegisterStep1() {
  clearAuthAlert();
  document.getElementById('registerFormStep2').classList.add('hidden');
  document.getElementById('registerFormStep1').classList.remove('hidden');
}

async function requestEmailVerificationCode(e) {
  e.preventDefault();
  clearAuthAlert();

  const kvkkCheckbox = document.getElementById('regKvkkConsent');
  if (!kvkkCheckbox || !kvkkCheckbox.checked) {
    showAuthAlert('⚠️ Kayıt olabilmek için KVKK Aydınlatma Metni ve Kullanım Koşulları açık rıza kutucuğunu onaylamanız zorunludur.', 'error');
    showToast('Lütfen KVKK ve Kullanım Koşulları kutucuğunu onaylayın.');
    return;
  }

  const btn = document.getElementById('sendCodeBtn');
  const origText = btn.textContent;
  btn.disabled = true;
  btn.textContent = '⏳ Kod Gönderiliyor...';

  const payload = {
    username: document.getElementById('regUsername').value.trim(),
    email: document.getElementById('regEmail').value.trim(),
    password: document.getElementById('regPassword').value,
    system_specs: document.getElementById('regSpecs').value.trim(),
    favorite_game: STATE.selectedGame !== 'all' ? STATE.selectedGame : 'valorant',
    kvkk_consent: true,
    website_url: document.getElementById('regHoneypot')?.value || ''
  };

  try {
    const res = await fetch('./api/auth/send-code', {
      method: 'POST',
      credentials: 'same-origin',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) {
      showAuthAlert(`⚠️ ${escapeHTML(data.detail || 'Kod gönderilemedi.')}`, 'error');
      showToast(data.detail || 'Kod gönderilemedi.');
      return;
    }

    if (data.already_registered && data.user) {
      STATE.currentUser = data.user;
      updateAuthUI();
      closeAuthModal();
      await Promise.all([fetchIssues(), fetchThreads()]);
      showToast(`✓ Hoş geldin, ${data.user.username}!`);
      return;
    }

    STATE.pendingVerifyEmail = data.email;
    document.getElementById('registerFormStep1').classList.add('hidden');
    document.getElementById('registerFormStep2').classList.remove('hidden');
    document.getElementById('verifyEmailTargetText').textContent = `${data.email} adresine gönderilen 6 haneli tek kullanımlık onay kodunu girin:`;

    const codeInp = document.getElementById('regVerificationCodeInput');
    if (codeInp) {
      codeInp.value = '';
      setTimeout(() => codeInp.focus(), 80);
    }
    showToast('6 haneli doğrulama kodu e-posta adresinize gönderildi!');
  } catch (err) {
    showAuthAlert('⚠️ Sunucuya bağlanılamadı. Lütfen tekrar deneyin.', 'error');
    showToast('İstek sırasında hata oluştu.');
  } finally {
    btn.disabled = false;
    btn.textContent = origText;
  }
}

async function verifyCodeAndCompleteRegister(e) {
  e.preventDefault();
  clearAuthAlert();
  const code = document.getElementById('regVerificationCodeInput').value.trim();
  const btn = document.getElementById('verifyCodeSubmitBtn');
  const origText = btn.textContent;
  btn.disabled = true;
  btn.textContent = '⏳ Doğrulanıyor...';

  try {
    const res = await fetch('/api/auth/verify-register', {
      method: 'POST',
      credentials: 'same-origin',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ email: STATE.pendingVerifyEmail, code })
    });
    const data = await res.json();
    if (!res.ok) {
      showAuthAlert(`⚠️ ${escapeHTML(data.detail || 'Doğrulama başarısız.')}`, 'error');
      showToast(data.detail || 'Doğrulama başarısız.');
      return;
    }

    STATE.currentUser = data.user;
    updateAuthUI();
    closeAuthModal();
    await Promise.all([fetchIssues(), fetchThreads()]);
    showToast(`✓ E-postanız doğrulandı! Hoş geldin, ${data.user.username}!`);
  } catch (err) {
    showAuthAlert('⚠️ Doğrulama sırasında bağlantı hatası oluştu.', 'error');
    showToast('Doğrulama sırasında hata oluştu.');
  } finally {
    btn.disabled = false;
    btn.textContent = origText;
  }
}

async function submitLogin(e) {
  e.preventDefault();
  clearAuthAlert();
  const identifier = document.getElementById('loginIdentifier').value.trim();
  const password = document.getElementById('loginPassword').value;
  const btn = document.getElementById('loginSubmitBtn');
  const origText = btn ? btn.textContent : 'Giriş Yap';
  if (btn) {
    btn.disabled = true;
    btn.textContent = '⏳ Giriş Yapılıyor...';
  }

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      credentials: 'same-origin',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ identifier, password })
    });
    const data = await res.json();
    if (!res.ok) {
      if (res.status === 404) {
        switchAuthTab('register');
        if (identifier.includes('@')) {
          document.getElementById('regEmail').value = identifier;
          document.getElementById('regUsername').value = identifier.split('@')[0];
        } else {
          document.getElementById('regUsername').value = identifier;
        }
        document.getElementById('regPassword').value = password;
        showAuthAlert(
          'ℹ️ <strong>Bu hesap henüz kayıtlı değil.</strong> Bilgileriniz dolduruldu; aşağıdan e-posta adresinizi kontrol edip <strong>"📩 E-Postaya Onay Kodu Gönder"</strong> butonuna basarak hemen hesabınızı açabilirsiniz!',
          'info'
        );
        return;
      }
      showAuthAlert(`⚠️ ${escapeHTML(data.detail || 'Giriş başarısız.')}`, 'error');
      showToast(data.detail || 'Giriş başarısız.');
      return;
    }

    STATE.currentUser = data.user;
    updateAuthUI();
    closeAuthModal();
    await Promise.all([fetchIssues(), fetchThreads()]);
    showToast(`✓ Hoş geldin, ${data.user.username}!`);
  } catch (err) {
    showAuthAlert('⚠️ Sunucuya ulaşılamadı. Lütfen sayfayı yenileyip tekrar deneyin.', 'error');
    showToast('Sunucu bağlantı hatası.');
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = origText;
    }
  }
}

function openProfileModal() {
  if (!STATE.currentUser) return;
  ensureLazyModalMounted('profileModal');
  document.getElementById('profileModalAvatar').textContent = STATE.currentUser.avatar_initials;
  document.getElementById('profileModalUsername').textContent = STATE.currentUser.username;
  document.getElementById('profileModalEmail').textContent = STATE.currentUser.email;
  document.getElementById('profileSpecsInput').value = STATE.currentUser.system_specs || '';
  document.getElementById('profileFavGameSelect').value = STATE.currentUser.favorite_game || 'valorant';
  document.getElementById('profileModal').classList.remove('hidden');
}

function closeProfileModal() {
  document.getElementById('profileModal').classList.add('hidden');
}

async function saveUserProfile(e) {
  e.preventDefault();
  const system_specs = document.getElementById('profileSpecsInput').value;
  const favorite_game = document.getElementById('profileFavGameSelect').value;

  const res = await fetch('./api/auth/profile', {
    method: 'PUT',
    headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ system_specs, favorite_game })
  });
  if (res.ok) {
    const data = await res.json();
    STATE.currentUser = data.user;
    document.getElementById('aiLabSpecs').value = data.user.system_specs || '';
    if (isFunctionalCookieAllowed()) {
      try {
        localStorage.setItem('oyuncoz_detected_specs', data.user.system_specs || '');
      } catch (e) {}
    }
    evaluateHardwareCompatibility();
    closeProfileModal();
    showToast('Profil ve sistem bilgileriniz güncellendi!');
  }
}

async function logoutUser() {
  await fetch('./api/auth/logout', { method: 'POST', credentials: 'same-origin', headers: getAuthHeaders() });
  STATE.currentUser = null;
  updateAuthUI();
  closeProfileModal();
  await Promise.all([fetchIssues(), fetchThreads()]);
  showToast('Oturum kapatıldı.');
}

async function deleteMyAccountPermanently() {
  if (!STATE.currentUser) return;
  const confirmed = window.confirm(
    '6698 Sayılı KVKK Madde 11 kapsamında hesabınızı, oturumlarınızı, oylarınızı ve açtığınız tüm forum verilerini KALICI OLARAK silmek istediğinize emin misiniz? Bu işlem geri alınamaz.'
  );
  if (!confirmed) return;

  try {
    const res = await fetch('./api/auth/account', {
      method: 'DELETE',
      credentials: 'same-origin',
      headers: getAuthHeaders()
    });
    const data = await res.json();
    if (!res.ok) {
      showToast(data.detail || 'Hesap silinemedi.');
      return;
    }

    STATE.currentUser = null;
    try {
      localStorage.removeItem('oyuncoz_detected_specs');
      localStorage.removeItem(`oyuncoz_votes_${STATE.clientId}`);
    } catch (e) {}

    updateAuthUI();
    closeProfileModal();
    await Promise.all([fetchIssues(), fetchThreads()]);
    showToast(data.message || '🗑️ Hesabınız ve tüm kişisel verileriniz KVKK Madde 11 kapsamında kalıcı olarak silindi.');
  } catch (err) {
    showToast('Hesap silme işlemi sırasında hata oluştu.');
  }
}

// --- STATUS & GAMES ---

async function fetchStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    STATE.hasServerApiKey = data.has_server_api_key;
    const label = document.getElementById('aiStatusLabel');
    if (label) {
      label.textContent = 'OyunÇöz Teknik Analiz Motoru Aktif';
    }
  } catch (err) {
    console.error('Status error:', err);
  }
}

async function fetchGames() {
  const res = await fetch('/api/games');
  STATE.games = await res.json();
  document.getElementById('sidebarTotalGamesBadge').textContent = `${STATE.games.length} Oyun Aktif`;
  const navPill = document.getElementById('navTotalGamesPill');
  if (navPill) navPill.textContent = `${STATE.games.length} Oyun`;

  renderSidebarGames();
  populateGameSelects();
  updateHeroBanner();
}

window.renderSidebarGames = renderSidebarGames;
function renderSidebarGames(forceRender = false) {
  const container = document.getElementById('gameNavList');
  if (!container) return;
  const megaPanel = document.getElementById('gamesMegaPanel');
  if (!forceRender && megaPanel && megaPanel.classList.contains('hidden')) {
    container._needsRender = true;
    return;
  }
  container._needsRender = false;
  const totalIssues = STATE.games.reduce((acc, g) => acc + (g.issue_count || 0), 0);

  let html = `
    <button onclick="selectGame('all')" class="game-nav-item ${STATE.selectedGame === 'all' ? 'active' : ''}">
      <div class="flex items-center gap-3">
        <div class="w-11 h-8 rounded-lg bg-[#5e9c88]/20 border border-[#5e9c88]/40 flex items-center justify-center text-xs font-extrabold text-[#a3d9c6] shrink-0">
          TÜMÜ
        </div>
        <div>
          <div class="text-sm font-bold">Tüm Oyunlar</div>
          <div class="text-[11px] text-gray-400">Genel Forum & AI Akışı</div>
        </div>
      </div>
      ${totalIssues > 0 ? `<span class="text-xs px-2 py-0.5 rounded-full bg-white/10 text-gray-200 font-semibold">${totalIssues}</span>` : ''}
    </button>
  `;

  for (const g of STATE.games) {
    const isActive = STATE.selectedGame === g.slug;
    const imgSrc = resolveSafeCoverUrl(g.image_url, g.short_name || g.name || g.slug, g.accent_color, g.category);
    const safeTitle = (g.short_name || g.slug || '').replace(/'/g, "\\'");
    const countBadge = g.issue_count > 0
      ? `<span class="text-xs px-2 py-0.5 rounded-full bg-white/10 text-gray-200 font-semibold shrink-0">${g.issue_count}</span>`
      : '';
    html += `
      <button onclick="selectGame('${g.slug}')" class="game-nav-item ${isActive ? 'active' : ''}">
        <div class="flex items-center gap-3 min-w-0">
          <img loading="lazy" decoding="async"
            src="${imgSrc}"
            onerror="this.onerror=null;this.src=fallbackCover('${safeTitle}','${g.accent_color}')"
            alt="${escapeHTML(g.short_name)}"
            class="w-11 h-8 rounded-lg object-cover border border-white/15 shrink-0 shadow-sm"
          />
          <div class="truncate">
            <div class="text-sm font-bold truncate">${escapeHTML(g.short_name)}</div>
            <div class="text-[11px] text-gray-400 truncate">${escapeHTML(g.category)}</div>
          </div>
        </div>
        ${countBadge}
      </button>
    `;
  }

  container.innerHTML = html;
}

function populateGameSelects() {
  const datalist = document.getElementById('allGamesDatalist');
  const favSelect = document.getElementById('profileFavGameSelect');

  if (datalist) {
    datalist.innerHTML = STATE.games
      .map(g => `<option value="${g.name}">${g.developer} • ${g.category}</option>`)
      .join('');
  }

  if (favSelect) {
    favSelect.innerHTML = STATE.games
      .map(g => `<option value="${g.slug}">${g.name} (${g.developer})</option>`)
      .join('');
  }

  if (STATE.selectedGame !== 'all') {
    const currentObj = STATE.games.find(g => g.slug === STATE.selectedGame);
    if (currentObj) {
      const aiInp = document.getElementById('aiLabGameInput');
      const modalInp = document.getElementById('modalThreadGameInput');
      if (aiInp) aiInp.value = currentObj.name;
      if (modalInp) modalInp.value = currentObj.name;
    }
  }
}

function updateHeroBanner() {
  const catBadge = document.getElementById('heroCategoryBadge');
  const engBadge = document.getElementById('heroEngineBadge');
  const acBadge = document.getElementById('heroAnticheatBadge');
  const titleEl = document.getElementById('heroGameTitle');
  const subEl = document.getElementById('heroGameSubtitle');
  const tagsEl = document.getElementById('heroCommonTags');
  const coverWrapper = document.getElementById('heroGameCoverWrapper');
  const coverImg = document.getElementById('heroGameCoverImg');

  if (STATE.selectedGame === 'all') {
    applyGameTheme('#10b981');
    if (coverWrapper) {
      coverWrapper.classList.add('hidden');
    }
    if (engBadge) engBadge.classList.add('hidden');
    if (acBadge) acBadge.classList.add('hidden');
    if (catBadge) {
      catBadge.innerHTML = '<span class="w-2 h-2 rounded-full bg-[#34d399]"></span><span>CANLI OYUN ARIZA &amp; FPS ÇÖZÜM MERKEZİ</span>';
    }
    if (titleEl) {
      titleEl.textContent = 'Hangi hatayı alıyorsun?';
    }
    if (subEl) {
      subEl.innerHTML = 'Aldığın hata kodunu (<code class="text-[#34d399] font-mono font-bold">VAN 185</code>, <code class="text-[#38bdf8] font-mono font-bold">ERR_GFX_STATE</code>, <code class="text-[#f43f5e] font-mono font-bold">VAN 9003</code>) veya oyun adını yaz; doğrudan test edilmiş adım adım çözüm sayfasına git.';
    }
  } else {
    const game = STATE.games.find(g => g.slug === STATE.selectedGame);
    if (!game) return;
    applyGameTheme(game.accent_color);
    if (coverWrapper && coverImg) {
      coverWrapper.classList.remove('hidden');
      const subLabel = `${game.category} • ${game.engine}`;
      const dynamicFallback = fallbackCover(game.short_name || game.name || game.slug, game.accent_color, subLabel);
      coverImg.className = 'w-32 h-20 sm:w-40 sm:h-24 rounded-2xl object-cover border border-white/20 shadow-xl transition-all duration-300';
      coverImg.alt = game.name;
      coverImg.onerror = () => {
        coverImg.onerror = null;
        coverImg.src = dynamicFallback;
      };
      coverImg.src = resolveSafeCoverUrl(game.image_url, game.short_name || game.name || game.slug, game.accent_color, subLabel);
    }
    catBadge.textContent = `${game.category} • ${game.developer}`;
    engBadge.textContent = `Motor: ${game.engine}`;
    acBadge.textContent = `Koruma: ${game.anticheat}`;
    titleEl.textContent = `${game.name} — Forum Sorunları & AI Çözüm Ekranı`;
    subEl.textContent = game.banner_subtitle;

    tagsEl.innerHTML = (game.common_tags || [])
      .map(t => `<button onclick="filterByTag('${t}')" class="text-xs px-2.5 py-1 rounded-lg bg-white/5 hover:bg-white/10 text-gray-200 border border-white/10 transition font-mono">${t}</button>`)
      .join('');

    const aiInp = document.getElementById('aiLabGameInput');
    const modalInp = document.getElementById('modalThreadGameInput');
    if (aiInp) aiInp.value = game.name;
    if (modalInp) modalInp.value = game.name;
  }
  evaluateHardwareCompatibility();
}

async function applyUrlSeoParams() {
  try {
    const params = new URLSearchParams(window.location.search);
    const gameParam = params.get('game');
    const queryParam = params.get('q') || params.get('search');

    if (gameParam) {
      const exists = STATE.games.find(g => g.slug === gameParam);
      if (exists) {
        STATE.selectedGame = gameParam;
        renderSidebarGames();
        updateHeroBanner();
        switchTab('issues');
      }
    }

    if (queryParam) {
      STATE.searchQuery = queryParam.trim();
      const input = document.getElementById('globalSearchInput');
      const clearBtn = document.getElementById('clearSearchBtn');
      if (input) input.value = STATE.searchQuery;
      if (clearBtn && STATE.searchQuery) clearBtn.classList.remove('hidden');
      switchTab('issues');
    }
  } catch (e) {
    console.warn('SEO URL param parse error:', e);
  }
}

function buildStrictSeoMetaDescription(rawSentence) {
  let s = String(rawSentence || '').replace(/\s+/g, ' ').trim();
  if (!s.endsWith('.')) s += '.';
  if (s.length > 160) {
    s = s.slice(0, 159).replace(/\s+\S*$/, '').replace(/[,;:\-]+$/, '') + '.';
  }
  while (s.length < 150) {
    const pad = ' Adım adım güncel çözüm adımlarını inceleyin.';
    if (s.length + pad.length <= 160) {
      s = s.slice(0, -1) + ' için adım adım teknik çözüm rehberi.';
    } else {
      break;
    }
  }
  return s;
}

function updateDynamicSEO() {
  try {
    const baseUrl = 'https://oyuncoz.com/';
    const metaDesc = document.querySelector('meta[name="description"]');
    const canonicalEl = document.getElementById('canonicalLink');

    // Stage 3.6: Parameterized URLs (?game=, ?q=) always keep canonical pointing to the main homepage
    if (canonicalEl) canonicalEl.setAttribute('href', baseUrl);

    if (STATE.selectedGame === 'all') {
      if (STATE.searchQuery) {
        const cleanQ = STATE.searchQuery.slice(0, 28).trim();
        let t = `${cleanQ} Çözüm Rehberi | OyunÇöz`;
        if (t.length > 60) t = `${cleanQ.slice(0, 20)} Çözümü | OyunÇöz`;
        document.title = t;
      } else {
        document.title = 'OyunÇöz | Oyun Hata Kodları ve FPS Çözümleri';
      }
      if (metaDesc) {
        metaDesc.setAttribute(
          'content',
          'OyunÇöz, Windows 10 ve 11 bilgisayarlarda karşılaşılan oyun hata kodları, çökme sorunları ve FPS düşüşleri için adım adım teknik çözüm rehberleri sunar.'
        );
      }
      if (window.history && window.history.replaceState) {
        const nextUrl = STATE.searchQuery
          ? `${window.location.pathname}?q=${encodeURIComponent(STATE.searchQuery)}`
          : window.location.pathname;
        window.history.replaceState({}, '', nextUrl);
      }
    } else {
      const game = STATE.games.find(g => g.slug === STATE.selectedGame);
      if (game) {
        const shortName = (game.short_name || game.name || 'Oyun').trim();
        let t = `${shortName} Hata Kodları ve FPS Çözümleri | OyunÇöz`;
        if (t.length > 60) {
          t = `${shortName} Hata Çözüm Rehberi | OyunÇöz`;
        }
        if (t.length > 60) {
          t = `${shortName.slice(0, 28)} Çözümleri | OyunÇöz`;
        }
        document.title = t;
        if (metaDesc) {
          const tagSummary = (game.common_tags || []).slice(0, 2).join(' ve ') || 'çökme';
          const descCandidate = `Windows 10 ve 11 sistemlerde ${game.name} oynarken oluşan ${tagSummary} hata kodları, çökme sorunları ve FPS düşüşleri için adım adım teknik çözüm rehberi sunar.`;
          metaDesc.setAttribute('content', buildStrictSeoMetaDescription(descCandidate));
        }
        if (window.history && window.history.replaceState) {
          window.history.replaceState({}, '', `${window.location.pathname}?game=${encodeURIComponent(game.slug)}`);
        }
      }
    }
  } catch (e) {
    console.warn('Dynamic SEO update warning:', e);
  }
}

function renderHomeShowcase() {
  try {
    const totalGamesEl = document.getElementById('hudTotalGamesStat');
    const totalIssuesEl = document.getElementById('hudTotalIssuesStat');
    const allIssuesBtnEl = document.getElementById('allIssuesLinkBtn');
    const gamesGrid = document.getElementById('homeGamesShowcaseGrid');
    const trendingGrid = document.getElementById('homeTrendingIssuesGrid');

    const totalIssuesCount = STATE.games.reduce((acc, g) => acc + (g.issue_count || 0), 0) || STATE.issues.length;
    if (totalGamesEl && STATE.games.length > 0) totalGamesEl.textContent = `${STATE.games.length} Oyun`;
    if (totalIssuesEl && totalIssuesCount > 0) totalIssuesEl.textContent = `${totalIssuesCount} Rehber`;
    if (allIssuesBtnEl && totalIssuesCount > 0) allIssuesBtnEl.textContent = `Tüm ${totalIssuesCount} Çözüm Rehberini Listele →`;

    if (gamesGrid && STATE.games.length > 0) {
      const featuredGames = STATE.selectedGame === 'all'
        ? STATE.games.slice(0, 12)
        : [
            ...STATE.games.filter(g => g.slug === STATE.selectedGame),
            ...STATE.games.filter(g => g.slug !== STATE.selectedGame).slice(0, 11)
          ];

      gamesGrid.innerHTML = featuredGames.map(g => {
        const imgSrc = resolveSafeCoverUrl(g.image_url, g.short_name || g.name || g.slug, g.accent_color, g.category);
        const safeTitle = (g.short_name || g.slug || '').replace(/'/g, "\\'");
        const solBadge = g.issue_count > 0
          ? `<span class="absolute top-1.5 right-1.5 text-[10px] font-bold px-1.5 py-0.5 rounded bg-black/75 text-[#a3d9c6] border border-white/10">${g.issue_count} Rehber</span>`
          : '';
        return `
          <div
            onclick="selectGame('${g.slug}'); switchTab('issues');"
            class="showcase-card rounded-xl overflow-hidden cursor-pointer group flex flex-col justify-between"
          >
            <div class="relative h-20 w-full overflow-hidden bg-[#151b26]">
              <img loading="lazy" decoding="async"
                src="${imgSrc}"
                onerror="this.onerror=null;this.src=fallbackCover('${safeTitle}','${g.accent_color}')"
                alt="${escapeHTML(g.name)}"
                class="w-full h-full object-cover group-hover:scale-105 transition duration-300"
              />
              <div class="absolute inset-0 bg-gradient-to-t from-[#161c28] via-transparent to-transparent"></div>
              ${solBadge}
            </div>
            <div class="p-2.5">
              <div class="text-xs font-bold text-white truncate group-hover:text-[#88c0a8] transition">${escapeHTML(g.short_name)}</div>
              <div class="text-[10px] text-gray-400 truncate">${escapeHTML(g.category)}</div>
            </div>
          </div>
        `;
      }).join('');
    }

    if (trendingGrid && STATE.issues.length > 0) {
      const topIssues = STATE.issues.slice(0, 6);
      trendingGrid.innerHTML = topIssues.map(iss => {
        const imgSrc = resolveSafeCoverUrl(iss.game_image_url, iss.game_short_name || iss.game_slug, iss.accent_color, iss.category);
        const safeTitle = (iss.game_short_name || iss.game_slug || '').replace(/'/g, "\\'");
        const rateStatus = (iss.show_success_rate && iss.total_votes >= 20 && iss.success_rate != null)
          ? `<span class="text-[#88c0a8] font-semibold">✓ İşe yarama oranı: %${iss.success_rate} (${iss.total_votes} Oy)</span>`
          : `<span class="text-gray-400">📅 Güncelleme: ${escapeHTML(iss.updated_at_display || '15.03.2026')}</span>`;
        const voteLabel = iss.helpful_votes > 0
          ? `👍 ${iss.helpful_votes} Evet • Rehberi Gör →`
          : `Adım Adım Rehberi Gör →`;
        return `
          <div
            onclick="quickSearchTag('${(iss.error_code || iss.title).replace(/'/g, '')}')"
            class="showcase-card rounded-xl p-3.5 cursor-pointer flex flex-col justify-between gap-2.5"
          >
            <div class="flex items-center justify-between gap-2">
              <div class="flex items-center gap-2 min-w-0">
                <img loading="lazy" decoding="async"
                  src="${imgSrc}"
                  onerror="this.onerror=null;this.src=fallbackCover('${safeTitle}','${iss.accent_color}')"
                  alt="${escapeHTML(iss.game_short_name)}"
                  class="w-8 h-6 rounded object-cover border border-white/15 shrink-0"
                />
                <span class="text-xs font-bold text-gray-200 truncate">${escapeHTML(iss.game_short_name)}</span>
              </div>
              <span class="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-[#5e9c88]/20 text-[#a3d9c6] border border-[#5e9c88]/30 shrink-0">
                ${escapeHTML(iss.error_code)}
              </span>
            </div>
            <div class="text-xs font-bold text-white line-clamp-2 leading-snug">${escapeHTML(iss.title)}</div>
            <div class="flex items-center justify-between text-[11px] text-gray-400 pt-1 border-t border-white/5">
              ${rateStatus}
              <span>${voteLabel}</span>
            </div>
          </div>
        `;
      }).join('');
    }
  } catch (e) {
    console.warn('Home showcase render warning:', e);
  }
}

// --- STAGE 7.2: COOKIE-CONSENT-AWARE ANALYTICS INTEGRATION (Plausible / Umami / GA4) ---
window.__OYUNCOZ_ANALYTICS_ACTIVE = false;

function hasAnalyticsCookieConsent() {
  try {
    const raw = localStorage.getItem('oyuncoz_cookie_consent');
    if (!raw) return false;
    const parsed = JSON.parse(raw);
    return Boolean(parsed && parsed.analytics === true);
  } catch (e) {
    return false;
  }
}

function disableAnalyticsTracking() {
  window.__OYUNCOZ_ANALYTICS_ACTIVE = false;
  const existing = document.getElementById('oyuncozAnalyticsScript');
  if (existing) existing.remove();
}

async function initConsentAwareAnalytics() {
  // Stage 7.2: Strictly never start tracking unless analytics cookie consent is explicitly granted
  if (!hasAnalyticsCookieConsent()) {
    disableAnalyticsTracking();
    return false;
  }
  if (window.__OYUNCOZ_ANALYTICS_ACTIVE || document.getElementById('oyuncozAnalyticsScript')) {
    return true;
  }
  try {
    const res = await fetch('/api/public-config');
    if (!res.ok) return false;
    const cfg = await res.json();
    const ana = (cfg && cfg.analytics) || {};
    const provider = String(ana.provider || 'none').toLowerCase();
    const analyticsId = String(ana.id || '').trim();
    const domain = String(ana.domain || 'oyuncoz.com').trim();
    const customSrc = String(ana.script_url || '').trim();

    if (provider === 'none' || (!analyticsId && provider !== 'plausible')) {
      return false;
    }

    const script = document.createElement('script');
    script.id = 'oyuncozAnalyticsScript';
    script.defer = true;

    if (provider === 'plausible') {
      script.src = customSrc || 'https://plausible.io/js/script.js';
      script.setAttribute('data-domain', domain);
      document.head.appendChild(script);
    } else if (provider === 'umami') {
      script.src = customSrc || 'https://cloud.umami.is/script.js';
      script.setAttribute('data-website-id', analyticsId);
      document.head.appendChild(script);
    } else if (provider === 'ga4') {
      window[`ga-disable-${analyticsId}`] = false;
      script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(analyticsId)}`;
      document.head.appendChild(script);
      window.dataLayer = window.dataLayer || [];
      window.gtag = function(){ window.dataLayer.push(arguments); };
      window.gtag('js', new Date());
      window.gtag('config', analyticsId, { anonymize_ip: true });
    }
    window.__OYUNCOZ_ANALYTICS_ACTIVE = true;
    return true;
  } catch (e) {
    return false;
  }
}

function initCookieConsent() {
  try {
    const saved = localStorage.getItem('oyuncoz_cookie_consent');
    if (saved) initConsentAwareAnalytics();
    if (!saved) {
      const mountBannerOnce = () => {
        window.removeEventListener('pointerdown', mountBannerOnce);
        window.removeEventListener('keydown', mountBannerOnce);
        if (localStorage.getItem('oyuncoz_cookie_consent')) return;
        const b = ensureLazyModalMounted('cookieConsentBanner');
        if (b) b.classList.remove('hidden');
      };
      window.addEventListener('pointerdown', mountBannerOnce, { once: true, passive: true });
      window.addEventListener('keydown', mountBannerOnce, { once: true, passive: true });
    }
  } catch (e) {}
}

function acceptCookies(mode = 'all') {
  const prefs = {
    essential: true,
    functional: mode === 'all',
    analytics: mode === 'all',
    updated_at: new Date().toISOString()
  };
  try {
    localStorage.setItem('oyuncoz_cookie_consent', JSON.stringify(prefs));
  } catch (e) {}
  const banner = document.getElementById('cookieConsentBanner');
  if (banner) banner.classList.add('hidden');
  closeCookieSettingsModal();
  initConsentAwareAnalytics();
  showToast(mode === 'all' ? '🍪 Tüm çerez tercihleri kaydedildi.' : '🍪 Yalnızca zorunlu çerezler aktif edildi.');
}

function saveCustomCookiePrefs() {
  const funcEl = document.getElementById('cookiePrefFunctional');
  const anaEl = document.getElementById('cookiePrefAnalytics');
  const prefs = {
    essential: true,
    functional: funcEl ? funcEl.checked : true,
    analytics: anaEl ? anaEl.checked : true,
    updated_at: new Date().toISOString()
  };
  try {
    localStorage.setItem('oyuncoz_cookie_consent', JSON.stringify(prefs));
  } catch (e) {}
  const banner = document.getElementById('cookieConsentBanner');
  if (banner) banner.classList.add('hidden');
  closeCookieSettingsModal();
  initConsentAwareAnalytics();
  showToast('🍪 Özel çerez tercihleriniz kaydedildi.');
}

function openCookieSettingsModal() {
  ensureLazyModalMounted('cookieSettingsModal');
  const modal = document.getElementById('cookieSettingsModal');
  if (modal) modal.classList.remove('hidden');
}

function closeCookieSettingsModal() {
  const modal = document.getElementById('cookieSettingsModal');
  if (modal) modal.classList.add('hidden');
}

function openLegalModal(tab = 'kvkk') {
  const map = {
    kvkk: './kvkk-aydinlatma-metni.html',
    privacy: './gizlilik-ve-cerez-politikasi.html',
    terms: './kullanim-kosullari.html',
    disclaimer: './telif-ve-sorumluluk-reddi.html',
    about: './hakkimizda.html',
    contact: './iletisim.html'
  };
  window.location.href = map[tab] || './hakkimizda.html';
}

function closeLegalModal() {
  const modal = document.getElementById('legalModal');
  if (modal) modal.classList.add('hidden');
}

function switchLegalTab(tab) {
  ['kvkk', 'privacy', 'terms', 'disclaimer'].forEach(t => {
    const btn = document.getElementById(`legalTabBtn-${t}`);
    const content = document.getElementById(`legalContent-${t}`);
    if (!btn || !content) return;
    if (t === tab) {
      btn.className = 'px-3 py-1.5 rounded-xl text-xs font-bold bg-[#5e9c88]/25 text-[#a3d9c6] border border-[#5e9c88]/40';
      content.classList.remove('hidden');
    } else {
      btn.className = 'px-3 py-1.5 rounded-xl text-xs font-bold bg-white/5 text-gray-300 border border-white/10 hover:text-white';
      content.classList.add('hidden');
    }
  });
}

async function selectGame(slug) {
  STATE.selectedGame = slug;
  if (window.toggleGamesNavPanel) window.toggleGamesNavPanel(false);
  if (window.toggleMobileNavDrawer) window.toggleMobileNavDrawer(false);
  renderSidebarGames();
  updateHeroBanner();
  await Promise.all([fetchIssues(), fetchThreads()]);
  renderHomeShowcase();
  updateDynamicSEO();
}

function switchTab(tabName) {
  const normalized = tabName === 'ai' ? 'ai-lab' : tabName;
  STATE.activeTab = normalized;
  ['issues', 'ai-lab', 'forum'].forEach(t => {
    const btn = document.getElementById(`tabBtn-${t}`);
    const section = document.getElementById(`tabContent-${t}`);
    if (!btn || !section) return;
    if (t === normalized) {
      btn.classList.add('active');
      section.classList.remove('hidden');
    } else {
      btn.classList.remove('active');
      section.classList.add('hidden');
    }
  });

  if (normalized === 'issues') {
    const ic = document.getElementById('issuesListContainer') || document.getElementById('issuesContainer');
    if (ic && (ic._needsRender || ic.children.length === 0)) {
      renderIssues(true);
    }
  }
  const catWrapper = document.getElementById('categoryFilterWrapper');
  if (catWrapper) {
    if (normalized === 'issues') {
      catWrapper.classList.remove('hidden');
    } else {
      catWrapper.classList.add('hidden');
    }
  }
}

function switchMainTab(tabName) {
  switchTab(tabName);
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// --- FEATURE 4: LIVE AUTOCOMPLETE SEARCH ENGINE (GAMES, ERROR CODES & FPS GUIDES) ---

let ALL_ISSUES_INDEX = [];

async function ensureAllIssuesIndex() {
  if (ALL_ISSUES_INDEX.length > 0) return ALL_ISSUES_INDEX;
  try {
    const res = await fetch('/api/issues', { headers: getAuthHeaders() });
    if (res.ok) {
      ALL_ISSUES_INDEX = await res.json();
    }
  } catch (e) {}
  return ALL_ISSUES_INDEX.length > 0 ? ALL_ISSUES_INDEX : STATE.issues;
}

function initLiveSearchListeners() {
  document.addEventListener('click', (e) => {
    const deskWrap = document.getElementById('desktopSearchWrapper');
    const mobWrap = document.getElementById('mobileSearchWrapper');
    if (deskWrap && !deskWrap.contains(e.target)) {
      const dd = document.getElementById('liveSearchDropdown');
      if (dd) dd.classList.add('hidden');
    }
    if (mobWrap && !mobWrap.contains(e.target)) {
      const mdd = document.getElementById('mobileLiveSearchDropdown');
      if (mdd) mdd.classList.add('hidden');
    }
  });
}

function closeLiveAutocomplete() {
  const dd = document.getElementById('liveSearchDropdown');
  const mdd = document.getElementById('mobileLiveSearchDropdown');
  if (dd) dd.classList.add('hidden');
  if (mdd) mdd.classList.add('hidden');
}

function handleSearchKeydown(e) {
  if (e.key === 'Escape') {
    closeLiveAutocomplete();
  } else if (e.key === 'Enter') {
    e.preventDefault();
    const val = e.target.value.trim();
    closeLiveAutocomplete();
    if (val) {
      filterByTag(val);
    }
  }
}

async function openLiveAutocomplete(val, isMobile = false) {
  await renderLiveAutocomplete(val, isMobile);
}

async function handleLiveSearchInput(val, isMobile = false) {
  const deskInput = document.getElementById('globalSearchInput');
  const mobInput = document.getElementById('mobileSearchInput');
  if (isMobile && deskInput) deskInput.value = val;
  if (!isMobile && mobInput) mobInput.value = val;

  const hintEl = document.getElementById('searchShortcutHint');
  const clearBtn = document.getElementById('clearSearchBtn');
  if (val && val.trim()) {
    if (hintEl) hintEl.classList.add('hidden');
    if (clearBtn) clearBtn.classList.remove('hidden');
  } else {
    if (hintEl) hintEl.classList.remove('hidden');
    if (clearBtn) clearBtn.classList.add('hidden');
  }

  await renderLiveAutocomplete(val, isMobile);
  handleGlobalSearch(val);
}

async function renderLiveAutocomplete(rawVal, isMobile = false) {
  const dropdown = document.getElementById(isMobile ? 'mobileLiveSearchDropdown' : 'liveSearchDropdown');
  if (!dropdown) return;

  const q = String(rawVal || '').trim().toLowerCase();
  const poolIssues = await ensureAllIssuesIndex();

  if (!q) {
    // Show Quick Trending Searches & Top Games when focused with empty query
    const popularQueries = [
      { label: 'VAN 9003 & VAN 1067', desc: 'Valorant Secure Boot & TPM 2.0', tag: 'VAN 9003' },
      { label: 'CS2 VAC Doğrulama', desc: 'VAC oturumunuzu doğrulayamadı', tag: 'VAC' },
      { label: 'D3D / ERR_GFX_STATE', desc: 'GTA V, RDR2 & Bannerlord GPU Çökmesi', tag: 'ERR_GFX' },
      { label: 'FPS Artırma & Stutter', desc: 'Anlık takılma, %1 Low FPS ve Shader', tag: 'Performans' },
      { label: 'Exit Code 1 / GLFW', desc: 'Minecraft Java & OpenGL Hatası', tag: 'Exit Code 1' },
      { label: 'Out of Video Memory', desc: 'UE5 Shader Compilation Çökmesi', tag: 'Out of Video Memory' }
    ];

    dropdown.innerHTML = `
      <div class="p-3 space-y-2">
        <div class="text-[11px] font-bold uppercase tracking-wider text-[#88c0a8] px-1">🔥 Popüler Hızlı Aramalar (Tıkla & Filtrele)</div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
          ${popularQueries.map(p => `
            <button
              type="button"
              onclick="selectAutocompleteTag('${p.tag}')"
              class="text-left p-2 rounded-xl bg-white/5 hover:bg-[#5e9c88]/20 border border-white/5 hover:border-[#88c0a8]/40 transition flex items-center justify-between gap-2"
            >
              <div class="min-w-0">
                <div class="text-xs font-bold text-white truncate">${p.label}</div>
                <div class="text-[10px] text-gray-400 truncate">${p.desc}</div>
              </div>
              <span class="text-xs text-[#88c0a8] shrink-0">→</span>
            </button>
          `).join('')}
        </div>
      </div>
    `;
    dropdown.classList.remove('hidden');
    return;
  }

  // Filter matching games
  const matchedGames = STATE.games.filter(g =>
    (g.name || '').toLowerCase().includes(q) ||
    (g.short_name || '').toLowerCase().includes(q) ||
    (g.category || '').toLowerCase().includes(q) ||
    (g.common_tags || []).some(t => t.toLowerCase().includes(q))
  ).slice(0, 4);

  // Filter matching issues (including special alias matching for "d3d", "fps", "vac", "van")
  const isFpsQuery = q.includes('fps') || q.includes('kasma') || q.includes('takılma') || q.includes('stutter');
  const isD3dQuery = q.includes('d3d') || q.includes('dx12') || q.includes('dx11') || q.includes('gfx') || q.includes('directx');

  const matchedIssues = poolIssues.filter(iss => {
    const hay = `${iss.title || ''} ${iss.error_code || ''} ${iss.game_name || ''} ${iss.category || ''} ${iss.symptom_summary || ''} ${iss.ai_root_cause || ''}`.toLowerCase();
    if (hay.includes(q)) return true;
    if (isFpsQuery && (iss.category || '').toLowerCase().includes('performans')) return true;
    if (isD3dQuery && /(d3d|dx11|dx12|dxgi|err_gfx|directx|shader)/i.test(hay)) return true;
    return false;
  }).slice(0, 6);

  let sectionsHtml = '';

  if (matchedGames.length > 0) {
    sectionsHtml += `
      <div class="p-3 space-y-1.5">
        <div class="text-[10px] font-bold uppercase tracking-wider text-gray-400 px-1">🎮 Eşleşen Oyun Ekranları (${matchedGames.length})</div>
        <div class="space-y-1">
          ${matchedGames.map(g => {
            const imgSrc = fallbackCover(g.short_name || g.name || g.slug, g.accent_color);
            const gCount = Number(g.issue_count || 0);
            const gBadge = gCount > 0
              ? `<span class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-[#5e9c88]/20 text-[#a3d9c6] border border-[#5e9c88]/30 shrink-0">${gCount} Çözüm</span>`
              : '';
            return `
              <button
                type="button"
                onclick="selectAutocompleteGame('${g.slug}')"
                class="w-full text-left p-2 rounded-xl hover:bg-white/10 transition flex items-center justify-between gap-3"
              >
                <div class="flex items-center gap-2.5 min-w-0">
                  <img loading="lazy" decoding="async" src="${imgSrc}" onerror="this.onerror=null;this.src=fallbackCover('${g.slug}','${g.accent_color}')" alt="${g.short_name}" class="w-10 h-7 rounded object-cover border border-white/15 shrink-0" />
                  <div class="min-w-0">
                    <div class="text-xs font-bold text-white truncate">${g.name}</div>
                    <div class="text-[10px] text-gray-400 truncate">${g.category} • ${g.engine}</div>
                  </div>
                </div>
                ${gBadge}
              </button>
            `;
          }).join('')}
        </div>
      </div>
    `;
  }

  if (matchedIssues.length > 0) {
    sectionsHtml += `
      <div class="p-3 space-y-1.5">
        <div class="text-[10px] font-bold uppercase tracking-wider text-gray-400 px-1">🛠️ Eşleşen Hata Kodları &amp; Çözüm Rehberleri (${matchedIssues.length})</div>
        <div class="space-y-1">
          ${matchedIssues.map(iss => {
            const pillText = (iss.show_success_rate && Number(iss.total_votes || 0) >= 20 && iss.success_rate != null)
              ? `%${iss.success_rate} İşe Yarama`
              : 'Adım Adım Rehber';
            return `
            <button
              type="button"
              onclick="selectAutocompleteIssue(${iss.id}, '${iss.game_slug}')"
              class="w-full text-left p-2.5 rounded-xl hover:bg-white/10 transition flex items-start justify-between gap-3"
            >
              <div class="min-w-0 space-y-0.5">
                <div class="flex items-center gap-1.5">
                  <span class="text-[10px] font-bold px-1.5 py-0.5 rounded text-white" style="background-color: ${iss.accent_color}">${iss.game_short_name}</span>
                  <span class="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-white/10 text-[#d9c382]">${iss.error_code}</span>
                </div>
                <div class="text-xs font-bold text-white truncate">${iss.title}</div>
                <div class="text-[11px] text-gray-400 truncate">${iss.symptom_summary}</div>
              </div>
              <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#5e9c88]/20 text-[#a3d9c6] shrink-0 mt-1">
                ${pillText}
              </span>
            </button>
          `;
          }).join('')}
        </div>
      </div>
    `;
  }

  const safeQ = q.replace(/'/g, "\\'");
  sectionsHtml += `
    <div class="p-3 bg-[#131924] flex items-center justify-between gap-2">
      <span class="text-xs text-gray-300 truncate">Aradığınız <strong>"${rawVal}"</strong> sorunu listede yok mu?</span>
      <button
        type="button"
        onclick="selectAutocompleteAiQuery('${safeQ}')"
        class="accent-btn px-3 py-1.5 rounded-xl text-xs font-bold shrink-0"
      >
        🤖 AI İle Şimdi Çözümle
      </button>
    </div>
  `;

  dropdown.innerHTML = sectionsHtml;
  dropdown.classList.remove('hidden');
}

function selectAutocompleteTag(tag) {
  closeLiveAutocomplete();
  quickSearchTag(tag);
}

async function selectAutocompleteGame(slug) {
  closeLiveAutocomplete();
  await selectGame(slug);
  switchTab('issues');
  window.scrollTo({ top: 180, behavior: 'smooth' });
}

async function selectAutocompleteIssue(issueId, gameSlug) {
  closeLiveAutocomplete();
  STATE.selectedGame = gameSlug || 'all';
  STATE.searchQuery = '';
  const deskInput = document.getElementById('globalSearchInput');
  const mobInput = document.getElementById('mobileSearchInput');
  if (deskInput) deskInput.value = '';
  if (mobInput) mobInput.value = '';
  document.getElementById('clearSearchBtn')?.classList.add('hidden');
  document.getElementById('searchShortcutHint')?.classList.remove('hidden');

  renderSidebarGames();
  updateHeroBanner();
  switchTab('issues');
  await fetchIssues();
  updateDynamicSEO();

  setTimeout(() => {
    const cardEl = document.getElementById(`issueCard-${issueId}`);
    if (cardEl) {
      cardEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
      cardEl.classList.add('ring-2', 'ring-[#88c0a8]');
      setTimeout(() => cardEl.classList.remove('ring-2', 'ring-[#88c0a8]'), 2600);
    }
  }, 120);
}

function selectAutocompleteAiQuery(queryText) {
  closeLiveAutocomplete();
  switchTab('ai-lab');
  const errInp = document.getElementById('aiLabErrorCode');
  const descInp = document.getElementById('aiLabDescription');
  if (errInp) errInp.value = queryText.toUpperCase();
  if (descInp && !descInp.value) {
    descInp.value = `"${queryText}" hatası / sorunu yaşıyorum. Donanımıma uygun adım adım çözüm rehberi oluşturur musunuz?`;
  }
  window.scrollTo({ top: 200, behavior: 'smooth' });
}

function quickSearchTag(tagText) {
  STATE.selectedGame = 'all';
  renderSidebarGames();
  updateHeroBanner();
  filterByTag(tagText);
  window.scrollTo({ top: 180, behavior: 'smooth' });
}

function filterByTag(tagText) {
  const input = document.getElementById('globalSearchInput');
  const mobInput = document.getElementById('mobileSearchInput');
  if (input) input.value = tagText;
  if (mobInput) mobInput.value = tagText;
  STATE.searchQuery = tagText;
  document.getElementById('clearSearchBtn')?.classList.remove('hidden');
  document.getElementById('searchShortcutHint')?.classList.add('hidden');
  switchTab('issues');
  fetchIssues();
  updateDynamicSEO();
}

function handleGlobalSearch(val) {
  STATE.searchQuery = val.trim();
  const clearBtn = document.getElementById('clearSearchBtn');
  const hintEl = document.getElementById('searchShortcutHint');
  if (STATE.searchQuery) {
    if (clearBtn) clearBtn.classList.remove('hidden');
    if (hintEl) hintEl.classList.add('hidden');
  } else {
    if (clearBtn) clearBtn.classList.add('hidden');
    if (hintEl) hintEl.classList.remove('hidden');
  }
  fetchIssues();
  fetchThreads();
}

function clearGlobalSearch() {
  const deskInput = document.getElementById('globalSearchInput');
  const mobInput = document.getElementById('mobileSearchInput');
  if (deskInput) deskInput.value = '';
  if (mobInput) mobInput.value = '';
  STATE.searchQuery = '';
  document.getElementById('clearSearchBtn')?.classList.add('hidden');
  document.getElementById('searchShortcutHint')?.classList.remove('hidden');
  closeLiveAutocomplete();
  fetchIssues();
  fetchThreads();
}

function handleCategoryChange(cat) {
  STATE.selectedCategory = cat;
  fetchIssues();
}

// --- FEATURE 1: SOLUTION VERIFICATION & VOTING (UPVOTE / DOWNVOTE + CLIENT_ID DEDUPLICATION) ---

function getLocalVoteMap() {
  try {
    const raw = localStorage.getItem(`oyuncoz_votes_${STATE.clientId}`);
    return raw ? JSON.parse(raw) : {};
  } catch (e) {
    return {};
  }
}

function setLocalVoteChoice(targetKey, choice) {
  try {
    const map = getLocalVoteMap();
    if (!choice) {
      delete map[targetKey];
    } else {
      map[targetKey] = choice;
    }
    localStorage.setItem(`oyuncoz_votes_${STATE.clientId}`, JSON.stringify(map));
  } catch (e) {}
}

async function fetchIssues() {
  const params = new URLSearchParams();
  if (STATE.selectedGame !== 'all') params.set('game_slug', STATE.selectedGame);
  if (STATE.selectedCategory !== 'all') params.set('category', STATE.selectedCategory);
  if (STATE.searchQuery) params.set('search', STATE.searchQuery);

  const res = await fetch(`/api/issues?${params.toString()}`, { headers: getAuthHeaders() });
  STATE.issues = await res.json();
  const badgeEl = document.getElementById('issuesCountBadge') || document.getElementById('tabCountIssues');
  if (badgeEl) {
    badgeEl.textContent = String(STATE.issues.length);
  }
  renderIssues();
}

function renderIssues(forceRender = false) {
  const container = document.getElementById('issuesListContainer') || document.getElementById('issuesContainer');
  if (!container) return;
  const tabSec = document.getElementById('tabContent-issues');
  if (!forceRender && tabSec && tabSec.classList.contains('hidden')) {
    container._needsRender = true;
    return;
  }
  container._needsRender = false;
  if (STATE.issues.length === 0) {
    container.innerHTML = `
      <div class="bg-[#1d2430] border border-white/10 rounded-2xl p-8 text-center space-y-3">
        <div class="text-base font-bold text-white">Aramanızla eşleşen hazır forum kaydı bulunamadı</div>
        <p class="text-xs text-gray-400 max-w-md mx-auto">
          Aradığınız oyunu veya hata kodunu doğrudan <strong>Yapay Zeka Arıza Çözümleyici</strong> sekmesinde analiz edebilir ya da yeni oyun sayfası oluşturabilirsiniz.
        </p>
        <div class="pt-2 flex justify-center gap-3">
          <button onclick="clearGlobalSearch()" class="px-4 py-2 rounded-xl text-xs bg-white/10 text-white">Filtreyi Temizle</button>
          <button onclick="switchTab('ai-lab')" class="accent-btn px-4 py-2 rounded-xl text-xs">AI İle Şimdi Çözümle</button>
        </div>
      </div>
    `;
    return;
  }

  const localVotes = getLocalVoteMap();

  container.innerHTML = STATE.issues.map(issue => {
    const severityColors = {
      'Kritik': 'bg-[#a8555d]/20 text-[#deb0b5] border-[#a8555d]/35',
      'Yüksek': 'bg-[#b38852]/20 text-[#e0c59e] border-[#b3885d]/35',
      'Orta': 'bg-[#5586ad]/20 text-[#acc8e0] border-[#5586ad]/35'
    };
    const sevClass = severityColors[issue.severity] || severityColors['Yüksek'];

    const forumsHtml = (issue.forum_sources || []).map(f => {
      const fUpvotes = Number(f.upvotes || 0);
      const upvoteBadge = fUpvotes > 0
        ? `<span class="text-[11px] px-2 py-0.5 rounded bg-white/5 text-gray-300 font-semibold">▲ ${fUpvotes} Onay</span>`
        : '';
      return `
      <div class="forum-quote-box p-3.5 space-y-1.5">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <span class="text-xs font-bold text-[#a3b8d4] flex items-center gap-1.5">
            <span>📌 ${escapeHTML(f.forum)}</span>
            <span class="text-gray-400 font-normal">• ${escapeHTML(f.thread)}</span>
          </span>
          ${upvoteBadge}
        </div>
        <p class="text-xs text-gray-300 italic">"${escapeHTML(f.quote)}"</p>
      </div>
    `;
    }).join('');

    const rawSteps = issue.ai_solution_steps || [];
    const wizState = STATE.wizardByIssue[issue.id] || { active: false, stepIndex: 0, solved: false };
    const totalSteps = Math.max(1, rawSteps.length);
    const curIdx = Math.min(Math.max(0, wizState.stepIndex || 0), totalSteps - 1);
    const curStepObj = rawSteps[curIdx] || { step: 1, title: 'Adım 1', difficulty: 'Kolay', detail: '' };
    const curStepRiskHtml = buildSafetyBannerHtml(`${curStepObj.title} ${curStepObj.detail}`) + buildRiskyCommandNotesHtml(`${curStepObj.title} ${curStepObj.detail}`);

    const stepsHtml = rawSteps.map(s => {
      const stepSafetyHtml = buildSafetyBannerHtml(`${s.title} ${s.detail}`) + buildRiskyCommandNotesHtml(`${s.title} ${s.detail}`);
      return `
        <div class="flex items-start gap-3.5 bg-[#181e29] p-3.5 rounded-xl border border-white/5">
          <div class="w-7 h-7 rounded-lg accent-btn flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">
            ${escapeHTML(s.step)}
          </div>
          <div class="flex-1 space-y-2">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <h4 class="text-sm font-bold text-white">${escapeHTML(s.title)}</h4>
              <span class="text-[11px] px-2 py-0.5 rounded bg-white/5 text-gray-300 border border-white/10">Zorluk: ${escapeHTML(s.difficulty)}</span>
            </div>
            ${stepSafetyHtml}
            <div class="text-xs text-gray-300 leading-relaxed ai-markdown">${formatSimpleMarkdown(s.detail)}</div>
          </div>
        </div>
      `;
    }).join('');

    const wizardHtml = wizState.active ? `
      <div class="rounded-2xl bg-[#161e2b] border border-[#88c0a8]/45 p-5 space-y-4 shadow-xl">
        <div class="flex flex-wrap items-center justify-between gap-2 border-b border-white/10 pb-3">
          <div class="flex items-center gap-2">
            <span class="px-2.5 py-0.5 rounded-full bg-[#5e9c88]/25 text-[#a3d9c6] border border-[#88c0a8]/40 text-xs font-extrabold">
              🧭 Adım ${curIdx + 1} / ${totalSteps}
            </span>
            <span class="text-xs font-bold text-white">İnteraktif Adım Adım Çözüm Sihirbazı</span>
          </div>
          <div class="flex items-center gap-1.5">
            ${rawSteps.map((_, idx) => `
              <span class="w-6 h-1.5 rounded-full ${idx <= curIdx ? 'bg-[#88c0a8]' : 'bg-white/10'}"></span>
            `).join('')}
          </div>
        </div>

        ${wizState.solved ? `
          <div class="p-4 rounded-xl bg-emerald-500/15 border border-emerald-400/40 text-center space-y-2">
            <div class="text-base font-extrabold text-emerald-200">🎉 Harika! Sorununuzun Çözüldüğüne Sevindik!</div>
            <p class="text-xs text-gray-200">Bu adımın işe yaradığı geri bildiriminizle kaydedildi.</p>
            <button type="button" onclick="toggleIssueWizard(${issue.id})" class="px-4 py-1.5 rounded-lg bg-white/10 hover:bg-white/15 text-xs text-white font-semibold">
              Tüm Adımları Görünümüne Dön
            </button>
          </div>
        ` : `
          <div class="space-y-3">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <h4 class="text-base font-extrabold text-white">${escapeHTML(curStepObj.step)}. ${escapeHTML(curStepObj.title)}</h4>
              <span class="text-[11px] px-2.5 py-0.5 rounded bg-white/5 text-[#a3d9c6] border border-white/10">Zorluk: ${escapeHTML(curStepObj.difficulty)}</span>
            </div>
            ${curStepRiskHtml}
            <div class="text-xs sm:text-sm text-gray-200 leading-relaxed ai-markdown bg-[#121822] p-4 rounded-xl border border-white/10">
              ${formatSimpleMarkdown(curStepObj.detail)}
            </div>
          </div>

          <div class="pt-2 flex flex-wrap items-center justify-between gap-2 border-t border-white/10">
            <button
              type="button"
              onclick="wizardPrevStep(${issue.id})"
              ${curIdx === 0 ? 'disabled' : ''}
              class="px-3 py-1.5 rounded-xl text-xs font-semibold bg-white/5 hover:bg-white/10 text-gray-300 disabled:opacity-40"
            >
              ← Önceki Adım
            </button>
            <div class="flex flex-wrap items-center gap-2">
              <button
                type="button"
                onclick="wizardMarkSolved(${issue.id})"
                class="px-4 py-2 rounded-xl text-xs font-extrabold bg-emerald-500/25 hover:bg-emerald-500/35 text-emerald-100 border border-emerald-400/40 transition shadow"
              >
                ✅ İşe Yaradı, Çözüldü
              </button>
              <button
                type="button"
                onclick="wizardNextStep(${issue.id}, ${totalSteps})"
                class="px-4 py-2 rounded-xl text-xs font-bold bg-amber-500/20 hover:bg-amber-500/30 text-amber-100 border border-amber-400/35 transition"
              >
                ❌ İşe Yaramadı, Sonraki Adıma Geç →
              </button>
            </div>
          </div>
        `}
      </div>
    ` : '';

    const verifyCmdB64 = issue.verify_command ? encodeBase64Utf8(issue.verify_command) : '';
    const verifyCmdNotesHtml = issue.verify_command ? buildRiskyCommandNotesHtml(issue.verify_command) : '';
    const verifyCmdBlock = issue.verify_command ? `
      <div class="space-y-2">
        <div class="bg-[#151a23] border border-white/10 rounded-xl p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div class="space-y-0.5 overflow-x-auto">
            <div class="text-[11px] text-gray-400 font-semibold uppercase tracking-wider">PowerShell / CMD Hızlı Kontrol Komutu:</div>
            <code class="text-xs text-[#8fbcbb] font-mono">${escapeHTML(issue.verify_command)}</code>
          </div>
          <button
            type="button"
            onclick="copyCodeFromBtn(this, '${verifyCmdB64}')"
            class="px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/15 text-xs text-white font-medium shrink-0 transition"
          >
            📋 Komutu Kopyala
          </button>
        </div>
        ${verifyCmdNotesHtml}
      </div>
    ` : '';

    // Check critical system safety warning (BIOS / TPM / Secure Boot / regedit / bcdedit / DDU)
    const combinedRiskText = `${issue.title} ${issue.error_code} ${issue.ai_root_cause} ${issue.verify_command || ''} ${(issue.ai_solution_steps || []).map(x => x.title + ' ' + x.detail).join(' ')}`;
    const safetyBannerHtml = buildSafetyBannerHtml(combinedRiskText);

    // Stage 2: Honest voting stats from database (0 by default; rate shown only when total_votes >= 20)
    const upVotes = Number(issue.helpful_votes || 0);
    const downVotes = Number(issue.unhelpful_votes || 0);
    const totalVotes = Number(issue.total_votes || (upVotes + downVotes));
    const showRate = Boolean(issue.show_success_rate && totalVotes >= 20 && issue.success_rate != null);
    const currentSr = showRate ? Number(issue.success_rate) : null;

    const activeVote = issue.user_vote || localVotes[`issue_${issue.id}`] || (issue.user_voted ? 'up' : null);
    const upBtnClass = activeVote === 'up'
      ? 'vote-btn-active font-bold'
      : 'bg-white/5 hover:bg-[#5e9c88]/20 text-gray-200 border-white/10';
    const downBtnClass = activeVote === 'down'
      ? 'bg-red-500/25 border-red-400/50 text-red-200 font-bold'
      : 'bg-white/5 hover:bg-red-500/15 text-gray-300 border-white/10';

    const authorName = issue.author_name || 'OyunÇöz Teknik Ekibi';
    const authorRole = issue.author_role || 'Sistem & Oyun Arıza Editörleri';
    const updatedDisplay = issue.updated_at_display || '15.03.2026';
    const dateModifiedIso = issue.date_modified || issue.updated_at || '2026-03-15';
    const testedVer = issue.tested_version || 'Windows 10 / 11 (23H2 & 24H2) • Güncel İstemci Sürümü';

    return `
      <article id="issueCard-${issue.id}" class="issue-card p-6 space-y-5 transition-all duration-300">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-xs font-bold px-2.5 py-1 rounded-lg text-white cursor-pointer flex items-center gap-2" style="background-color: ${escapeHTML(issue.accent_color)}" onclick="selectGame('${escapeHTML(issue.game_slug)}')">
              <img loading="lazy" decoding="async"
                src="${fallbackCover(issue.game_short_name || issue.game_slug, issue.accent_color)}"
                onerror="this.onerror=null;this.src=fallbackCover('${escapeHTML(issue.game_slug)}','${escapeHTML(issue.accent_color)}')"
                alt="${escapeHTML(issue.game_short_name)}"
                class="w-6 h-4 rounded object-cover border border-white/20"
              />
              <span>${escapeHTML(issue.game_short_name)}</span>
            </span>
            <span class="text-xs font-mono font-bold px-2.5 py-1 rounded-lg bg-white/5 text-[#d9c382] border border-white/10">
              ${escapeHTML(issue.error_code)}
            </span>
            <span class="text-xs font-semibold px-2.5 py-1 rounded-lg border ${sevClass}">
              Önem: ${escapeHTML(issue.severity)}
            </span>
            ${issue.editor_verified !== false ? '<span class="editor-verified-badge text-xs font-bold px-2.5 py-1 rounded-lg bg-emerald-500/15 text-emerald-200 border border-emerald-400/30">✓ Editör kontrolünden geçti</span>' : '<span class="ai-draft-badge text-xs font-bold px-2.5 py-1 rounded-lg bg-amber-500/15 text-amber-200 border border-amber-400/30">🤖 Yapay Zeka Taslağı</span>'}
            <span class="text-xs px-2.5 py-1 rounded-lg bg-white/5 text-gray-300 border border-white/10">
              ${escapeHTML(issue.category)}
            </span>
          </div>
          <div class="flex items-center gap-2">
            <span id="issueSuccessBadge-${issue.id}" class="${showRate ? '' : 'hidden '}text-xs font-bold px-3 py-1 rounded-full bg-[#5e9c88]/15 text-[#a3d9c6] border border-[#5e9c88]/30">
              ${showRate ? `✓ İşe yarama oranı: %${currentSr} (${totalVotes} Oy)` : ''}
            </span>
          </div>
        </div>

        <div class="space-y-1.5">
          <h3 class="text-lg sm:text-xl font-extrabold text-white">${escapeHTML(issue.title)}</h3>
          <p class="text-sm text-gray-300">${escapeHTML(issue.symptom_summary)}</p>
        </div>

        <!-- Stage 2.3: Yazar Kutusu, Son Güncelleme (dateModified) ve Test Edilen Sürüm -->
        <div class="p-3.5 rounded-xl bg-[#161c27] border border-white/10 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
          <div class="flex items-center gap-2.5">
            <span class="oc-brand-icon !w-9 !h-9" aria-hidden="true"><svg class="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg></span>
            <div>
              <div class="text-white font-bold">
                Yazar: <a href="./hakkimizda.html" class="text-[#88c0a8] hover:underline">${escapeHTML(authorName)}</a>
              </div>
              <div class="text-[11px] text-gray-400">${escapeHTML(authorRole)}</div>
            </div>
          </div>
          <div class="flex flex-wrap items-center gap-2 text-[11px] text-gray-300">
            <span class="px-2.5 py-1 rounded-lg bg-white/5 border border-white/10">
              📅 Son güncelleme: <time datetime="${escapeHTML(dateModifiedIso)}" class="font-semibold text-white">${escapeHTML(updatedDisplay)}</time>
            </span>
            <span class="px-2.5 py-1 rounded-lg bg-white/5 border border-white/10">
              🧪 Test edilen sürüm: <strong class="text-[#a3d9c6]">${escapeHTML(testedVer)}</strong>
            </span>
          </div>
        </div>

        ${safetyBannerHtml}

        <div class="space-y-2">
          <div class="text-xs font-bold uppercase tracking-wider text-[#90a8c8]">
            🌐 Forumlardan Derlenen Kullanıcı Raporları &amp; Çözüm Kaynakları
          </div>
          <div class="grid grid-cols-1 gap-2.5">
            ${forumsHtml}
          </div>
        </div>

        <div class="ai-root-box p-4 space-y-1.5">
          <div class="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#a3d9c6]">
            <span>🤖 Yapay Zeka Kök Neden Analizi (Root Cause)</span>
          </div>
          <p class="text-xs sm:text-sm text-gray-200 leading-relaxed">${escapeHTML(issue.ai_root_cause)}</p>
          <div class="pt-1.5 text-[11px] font-semibold text-amber-200 flex items-center gap-1.5"><span>⚠️</span><span>Bu çözüm yapay zeka tarafından üretildi, uygulamadan önce geri yükleme noktası oluşturun.</span></div>
        </div>

        <div class="space-y-3">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div class="text-xs font-bold uppercase tracking-wider text-gray-300">
              🛠️ Adım Adım Çözüm Rehberi
            </div>
            <button
              type="button"
              onclick="toggleIssueWizard(${issue.id})"
              class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 ${wizState.active ? 'accent-btn shadow' : 'bg-[#5e9c88]/20 hover:bg-[#5e9c88]/35 text-[#a3d9c6] border border-[#88c0a8]/40'}"
            >
              <span>🧭 ${wizState.active ? 'Tüm Adımları Alt Alta Göster' : 'Sihirbaz Modunda Çöz (Adım Adım)'}</span>
            </button>
          </div>
          ${wizState.active ? wizardHtml : `<div class="space-y-2.5">${stepsHtml}</div>`}
        </div>

        ${verifyCmdBlock}

        <!-- Stage 2.3: Bu çözüm işe yaradı mı? Evet / Hayır (Tek Oy, 20+ Oyda Gerçek Oran) -->
        <div class="pt-4 border-t border-white/10 space-y-3">
          <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
            <div class="flex flex-wrap items-center gap-2.5">
              <span class="text-xs font-bold text-gray-200">Bu çözüm işe yaradı mı?</span>
              <button
                type="button"
                id="issueUpBtn-${issue.id}"
                onclick="voteIssue(${issue.id}, 'up')"
                class="px-3.5 py-1.5 rounded-xl border text-xs flex items-center gap-1.5 transition ${upBtnClass}"
              >
                <span>👍 Evet</span>
                <span id="issueUpCount-${issue.id}" class="font-bold ${upVotes > 0 ? '' : 'hidden'}">${upVotes > 0 ? `(${upVotes})` : ''}</span>
              </button>
              <button
                type="button"
                id="issueDownBtn-${issue.id}"
                onclick="voteIssue(${issue.id}, 'down')"
                class="px-3.5 py-1.5 rounded-xl border text-xs flex items-center gap-1.5 transition ${downBtnClass}"
              >
                <span>👎 Hayır</span>
                <span id="issueDownCount-${issue.id}" class="font-bold ${downVotes > 0 ? '' : 'hidden'}">${downVotes > 0 ? `(${downVotes})` : ''}</span>
              </button>
              <span id="issueRateInline-${issue.id}" class="${showRate ? '' : 'hidden '}text-xs font-semibold text-[#88c0a8]">
                ${showRate ? `• İşe yarama oranı: %${currentSr} (${totalVotes} Oy)` : ''}
              </span>
            </div>

            <button
              type="button"
              onclick="customizeIssueInAiLab('${issue.game_name.replace(/'/g, "\\'")}', '${issue.error_code.replace(/'/g, "\\'")}', '${issue.title.replace(/'/g, "\\'")}')"
              class="px-3.5 py-1.5 rounded-xl bg-white/10 hover:bg-white/15 text-xs font-semibold text-white flex items-center gap-1.5 transition self-start lg:self-auto"
            >
              <span>⚡ Bu Sorunu Kendi Sistemime Göre AI İle Özelleştir</span>
            </button>
          </div>
        </div>
      </article>
    `;
  }).join('');
}

// --- KILLER FEATURE 2: INTERACTIVE STEP-BY-STEP TROUBLESHOOTING WIZARD ---

function toggleIssueWizard(issueId) {
  const cur = STATE.wizardByIssue[issueId] || { active: false, stepIndex: 0, solved: false };
  STATE.wizardByIssue[issueId] = {
    active: !cur.active,
    stepIndex: 0,
    solved: false
  };
  renderIssues();
}

function wizardPrevStep(issueId) {
  const cur = STATE.wizardByIssue[issueId] || { active: true, stepIndex: 0, solved: false };
  STATE.wizardByIssue[issueId] = {
    ...cur,
    active: true,
    stepIndex: Math.max(0, (cur.stepIndex || 0) - 1),
    solved: false
  };
  renderIssues();
}

function wizardNextStep(issueId, totalSteps) {
  const cur = STATE.wizardByIssue[issueId] || { active: true, stepIndex: 0, solved: false };
  const nextIdx = (cur.stepIndex || 0) + 1;
  if (nextIdx >= totalSteps) {
    showToast('ℹ️ Tüm standart adımları tamamladınız. Sorununuz devam ediyorsa kendi donanımınıza göre AI ile özelleştirin!');
    const iss = STATE.issues.find(i => i.id === issueId);
    if (iss) {
      customizeIssueInAiLab(iss.game_name, iss.error_code, iss.title);
    }
    return;
  }
  STATE.wizardByIssue[issueId] = {
    ...cur,
    active: true,
    stepIndex: nextIdx,
    solved: false
  };
  renderIssues();
}

function wizardMarkSolved(issueId) {
  const cur = STATE.wizardByIssue[issueId] || { active: true, stepIndex: 0, solved: false };
  STATE.wizardByIssue[issueId] = {
    ...cur,
    active: true,
    solved: true
  };
  voteIssue(issueId, 'up');
  renderIssues();
}

function copyCommand(cmd) {
  navigator.clipboard.writeText(cmd);
  showToast('📋 Komut panoya kopyalandı!');
}

async function voteIssue(issueId, voteType = 'up') {
  const userHwTag = extractShortHardwareTag();
  const res = await fetch(`./api/issues/${issueId}/vote`, {
    method: 'POST',
    headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ vote_type: voteType, hardware_tag: userHwTag })
  });
  if (res.ok) {
    const data = await res.json();
    setLocalVoteChoice(`issue_${issueId}`, data.user_vote);

    const upCountEl = document.getElementById(`issueUpCount-${issueId}`);
    const downCountEl = document.getElementById(`issueDownCount-${issueId}`);
    const upBtnEl = document.getElementById(`issueUpBtn-${issueId}`);
    const downBtnEl = document.getElementById(`issueDownBtn-${issueId}`);
    const badgeEl = document.getElementById(`issueSuccessBadge-${issueId}`);
    const inlineEl = document.getElementById(`issueRateInline-${issueId}`);

    const upCnt = Number(data.helpful_votes || 0);
    const downCnt = Number(data.unhelpful_votes || 0);
    const totalVotes = Number(data.total_votes || (upCnt + downCnt));
    const showRate = Boolean(data.show_success_rate && totalVotes >= 20 && data.success_rate != null);
    const sr = showRate ? Number(data.success_rate) : null;

    if (upCountEl) {
      upCountEl.textContent = upCnt > 0 ? `(${upCnt})` : '';
      upCountEl.classList.toggle('hidden', upCnt === 0);
    }
    if (downCountEl) {
      downCountEl.textContent = downCnt > 0 ? `(${downCnt})` : '';
      downCountEl.classList.toggle('hidden', downCnt === 0);
    }
    if (badgeEl) {
      badgeEl.textContent = showRate ? `✓ İşe yarama oranı: %${sr} (${totalVotes} Oy)` : '';
      badgeEl.classList.toggle('hidden', !showRate);
    }
    if (inlineEl) {
      inlineEl.textContent = showRate ? `• İşe yarama oranı: %${sr} (${totalVotes} Oy)` : '';
      inlineEl.classList.toggle('hidden', !showRate);
    }

    if (upBtnEl) {
      upBtnEl.className = data.user_vote === 'up'
        ? 'px-3.5 py-1.5 rounded-xl border text-xs flex items-center gap-1.5 transition vote-btn-active font-bold'
        : 'px-3.5 py-1.5 rounded-xl border text-xs flex items-center gap-1.5 transition bg-white/5 hover:bg-[#5e9c88]/20 text-gray-200 border-white/10';
    }
    if (downBtnEl) {
      downBtnEl.className = data.user_vote === 'down'
        ? 'px-3.5 py-1.5 rounded-xl border text-xs flex items-center gap-1.5 transition bg-red-500/25 border-red-400/50 text-red-200 font-bold'
        : 'px-3.5 py-1.5 rounded-xl border text-xs flex items-center gap-1.5 transition bg-white/5 hover:bg-red-500/15 text-gray-300 border-white/10';
    }

    // Update issue in STATE.issues too
    const found = STATE.issues.find(i => i.id === issueId);
    if (found) {
      found.helpful_votes = upCnt;
      found.unhelpful_votes = downCnt;
      found.total_votes = totalVotes;
      found.show_success_rate = showRate;
      found.success_rate = sr;
      found.user_vote = data.user_vote;
    }

    if (data.user_vote === 'up') {
      showToast('👍 Geri bildiriminiz (Evet) kaydedildi!');
    } else if (data.user_vote === 'down') {
      showToast('👎 Geri bildiriminiz (Hayır) kaydedildi. Alternatif çözüm için AI Çözümleyiciyi kullanabilirsiniz.');
    } else {
      showToast('Oyunuz geri alındı.');
    }
  }
}

function renderAiReportVoteBar(reportKey, initialConfidence = null, isGuestTrial = false) {
  const bar = document.getElementById('aiResultVoteBar');
  if (!bar) return;
  const localVotes = getLocalVoteMap();
  const currentChoice = localVotes[`ai_${reportKey}`] || null;
  const upCnt = currentChoice === 'up' ? 1 : 0;
  const downCnt = currentChoice === 'down' ? 1 : 0;

  const upClass = currentChoice === 'up'
    ? 'vote-btn-active font-bold'
    : 'bg-white/5 hover:bg-[#5e9c88]/20 text-gray-200 border-white/10';
  const downClass = currentChoice === 'down'
    ? 'bg-red-500/25 border-red-400/50 text-red-200 font-bold'
    : 'bg-white/5 hover:bg-red-500/15 text-gray-300 border-white/10';

  const guestSavePromptHtml = (!STATE.currentUser || isGuestTrial) ? `
    <div class="mt-3 p-3.5 rounded-xl bg-[#161e2b] border border-[#88c0a8]/40 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div class="text-xs text-gray-200">
        🎁 <strong>Ücretsiz Misafir Analiziniz Tamamlandı!</strong> Bu çözümü profilinize kaydetmek veya 2. AI sorgusunu yapmak için ücretsiz hesap açın.
      </div>
      <button
        type="button"
        onclick="promptRegisterToSaveAiSolution()"
        class="accent-btn px-4 py-2 rounded-xl text-xs font-bold shrink-0 shadow"
      >
        💾 Çözümü Kaydet &amp; Ücretsiz Üye Ol
      </button>
    </div>
  ` : '';

  bar.innerHTML = `
    <div class="space-y-2">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div class="flex flex-wrap items-center gap-2.5">
          <span class="text-xs font-bold text-white">Bu çözüm işe yaradı mı?</span>
          <button
            type="button"
            onclick="voteAiReport('${escapeHTML(reportKey)}', 'up')"
            class="px-3.5 py-1.5 rounded-xl border text-xs flex items-center gap-1.5 transition ${upClass}"
          >
            <span>👍 Evet${upCnt > 0 ? ` (${upCnt})` : ''}</span>
          </button>
          <button
            type="button"
            onclick="voteAiReport('${escapeHTML(reportKey)}', 'down')"
            class="px-3.5 py-1.5 rounded-xl border text-xs flex items-center gap-1.5 transition ${downClass}"
          >
            <span>👎 Hayır${downCnt > 0 ? ` (${downCnt})` : ''}</span>
          </button>
        </div>
      </div>
      ${guestSavePromptHtml}
    </div>
  `;
}

function promptRegisterToSaveAiSolution() {
  openAuthModal('register');
  showAuthAlert(
    '💾 <strong>Çözümü kaydetmek ve sınırsız AI arıza analizi yapmak için</strong> ücretsiz hesabınızı oluşturun.',
    'info'
  );
}

function voteAiReport(reportKey, choice) {
  const localVotes = getLocalVoteMap();
  const prev = localVotes[`ai_${reportKey}`] || null;
  const next = prev === choice ? null : choice;
  setLocalVoteChoice(`ai_${reportKey}`, next);
  renderAiReportVoteBar(reportKey);
  if (next === 'up') {
    showToast(`👍 AI çözümünü (${extractShortHardwareTag()}) ile doğruladığınız için teşekkürler!`);
  } else if (next === 'down') {
    showToast('👎 Geri bildiriminiz kaydedildi.');
  } else {
    showToast('Oyunuz geri alındı.');
  }
}

// --- KILLER FEATURE 1: DRAG & DROP CRASH LOG / DUMP ANALYZER (Client-Side FileReader + Privacy Masking) ---

function handleCrashLogDragOver(e) {
  e.preventDefault();
  e.stopPropagation();
  const dz = document.getElementById('crashLogDropZone');
  if (dz) dz.classList.add('border-[#88c0a8]', 'bg-[#1d283a]');
}

function handleCrashLogDragLeave(e) {
  e.preventDefault();
  e.stopPropagation();
  const dz = document.getElementById('crashLogDropZone');
  if (dz) dz.classList.remove('border-[#88c0a8]', 'bg-[#1d283a]');
}

function handleCrashLogDrop(e) {
  e.preventDefault();
  e.stopPropagation();
  const dz = document.getElementById('crashLogDropZone');
  if (dz) dz.classList.remove('border-[#88c0a8]', 'bg-[#1d283a]');
  const files = e.dataTransfer && e.dataTransfer.files;
  if (files && files.length > 0) {
    readAndAnalyzeCrashLogFile(files[0]);
  }
}

function handleCrashLogFileSelect(e) {
  const files = e.target && e.target.files;
  if (files && files.length > 0) {
    readAndAnalyzeCrashLogFile(files[0]);
  }
}

function anonymizePersonalPathsInLog(rawText) {
  if (!rawText) return { maskedText: '', maskedCount: 0 };
  let count = 0;
  let masked = String(rawText);

  // Mask Windows paths: C:\Users\ActualUsername\... -> C:\Users\[USER]\...
  masked = masked.replace(/([A-Za-z]:\\Users\\)([^\\\/\r\n"'\s]+)(\\?)/gi, (_, prefix, uname, suffix) => {
    if (uname.toUpperCase() === '[USER]' || uname.toLowerCase() === 'public' || uname.toLowerCase() === 'default') {
      return `${prefix}${uname}${suffix}`;
    }
    count++;
    return `${prefix}[USER]${suffix}`;
  });

  // Mask forward-slash Windows/macOS/Linux user paths: C:/Users/Name/ or /Users/Name/ or /home/Name/
  masked = masked.replace(/((?:[A-Za-z]:)?\/(?:Users|home)\/)([^\\\/\r\n"'\s]+)(\/?)/gi, (_, prefix, uname, suffix) => {
    if (uname.toUpperCase() === '[USER]' || uname.toLowerCase() === 'shared') {
      return `${prefix}${uname}${suffix}`;
    }
    count++;
    return `${prefix}[USER]${suffix}`;
  });

  return { maskedText: masked, maskedCount: count };
}

function parseAndApplyCrashLog(fileName, rawContent) {
  const { maskedText, maskedCount } = anonymizePersonalPathsInLog(rawContent);
  const lines = maskedText.split(/\r?\n/);

  const criticalRegex = /(\b(Exception|Error|Fatal|Crash|Access\s*Violation|OutOfMemory|Out\s*of\s*Video\s*Memory|Exit\s*Code|Stacktrace|Unhandled|DXGI_ERROR_[A-Z0-9_]+|ERR_GFX_[A-Z0-9_]+|VAN\s*\d+|nvlddmkm|amdkmdag)\b|0x[0-9A-Fa-f]{6,16}|[a-zA-Z0-9_-]+\.dll)/i;

  const matchedLines = [];
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    if (criticalRegex.test(trimmed)) {
      matchedLines.push(trimmed.slice(0, 220));
      if (matchedLines.length >= 12) break;
    }
  }

  if (matchedLines.length === 0) {
    // Fallback: take last non-empty lines of log
    const nonEmpty = lines.map(l => l.trim()).filter(Boolean);
    matchedLines.push(...nonEmpty.slice(-6).map(l => l.slice(0, 220)));
  }

  // Extract a primary error token for #aiLabErrorCode
  const joinedMatches = matchedLines.join(' ');
  const tokenMatch = joinedMatches.match(/(DXGI_ERROR_[A-Z0-9_]+|ERR_GFX_[A-Z0-9_]+|0x[0-9A-Fa-f]{6,10}|Exit\s*Code\s*-?\d+|VAN\s*\d+|[a-zA-Z0-9_-]+\.dll|OutOfMemory\w*|Access\s*Violation)/i);

  const errInp = document.getElementById('aiLabErrorCode');
  if (errInp && tokenMatch && tokenMatch[1]) {
    errInp.value = tokenMatch[1];
  }

  const gameInp = document.getElementById('aiLabGameInput');
  if (gameInp && !gameInp.value.trim()) {
    if (/valorant|vgc|vgk|van\s*9003/i.test(joinedMatches)) gameInp.value = 'Valorant';
    else if (/fivem|citizenfx|rage|err_gfx_d3d_init/i.test(joinedMatches)) gameInp.value = 'GTA V / FiveM';
    else if (/bannerlord|taleworlds|d3d_device_context/i.test(joinedMatches)) gameInp.value = 'Mount & Blade II: Bannerlord';
    else if (/cs2|engine2\.dll|vac/i.test(joinedMatches)) gameInp.value = 'Counter-Strike 2';
    else if (/minecraft|lwjgl|glfw|exit\s*code\s*1/i.test(joinedMatches)) gameInp.value = 'Minecraft';
  }

  const descInp = document.getElementById('aiLabDescription');
  const summaryBlock = `[CRASH LOG ANALİZİ - Dosya: ${fileName} | Kişisel Yollar C:\\Users\\[USER] Olarak Maskelendi]\n` +
    matchedLines.slice(0, 8).map(l => `• ${l}`).join('\n');

  if (descInp) {
    descInp.value = summaryBlock;
    descInp.classList.add('ring-2', 'ring-[#88c0a8]');
    setTimeout(() => descInp.classList.remove('ring-2', 'ring-[#88c0a8]'), 2400);
  }

  // Show preview box
  const box = document.getElementById('crashLogResultBox');
  const fileBadge = document.getElementById('crashLogFileNameBadge');
  const matchBadge = document.getElementById('crashLogMatchCountBadge');
  const maskBadge = document.getElementById('crashLogMaskedCountBadge');
  const preEl = document.getElementById('crashLogExtractedPreview');

  if (box && preEl) {
    if (fileBadge) fileBadge.textContent = `📄 ${fileName}`;
    if (matchBadge) matchBadge.textContent = `${matchedLines.length} Kritik Hata Satırı Ayıklandı`;
    if (maskBadge) maskBadge.textContent = `🛡️ ${maskedCount} Kişisel Dosya Yolu C:\\Users\\[USER] Maskelendi`;
    preEl.textContent = matchedLines.join('\n');
    box.classList.remove('hidden');
  }

  showToast(`📄 "${fileName}" tarayıcıda analiz edildi ve kişisel dosya yolları maskelendi!`);
}

function readAndAnalyzeCrashLogFile(file) {
  if (!file) return;
  const maxBytes = 4 * 1024 * 1024; // Read up to 4MB in browser
  const blob = file.size > maxBytes ? file.slice(file.size - maxBytes) : file;
  const reader = new FileReader();
  reader.onload = (ev) => {
    const text = String(ev.target?.result || '');
    parseAndApplyCrashLog(file.name, text);
  };
  reader.onerror = () => {
    showToast('⚠️ Dosya tarayıcıda okunamadı.');
  };
  reader.readAsText(blob, 'utf-8');
}

function loadSampleCrashLog() {
  const sampleLog = [
    '2026-10-28 00:42:11.104 [INFO] Initializing RenderDevice DirectX 11...',
    '2026-10-28 00:42:12.519 [WARN] Loading user shader cache from C:\\Users\\EmreOyuncu\\AppData\\Local\\Temp\\RAGE_ShaderCache\\pipeline.bin',
    '2026-10-28 00:42:14.882 [ERROR] Fatal Exception 0xC0000005 (Access Violation) in module d3d11.dll at 0033:00007FF8A12C4810',
    '2026-10-28 00:42:14.883 [FATAL] ERR_GFX_D3D_INIT: DXGI_ERROR_DEVICE_REMOVED (0x887A0005) - GPU driver nvlddmkm.sys stopped responding.',
    '2026-10-28 00:42:14.885 [ERROR] OutOfMemoryException: Failed to allocate 2048 MB VRAM buffer (Exit Code -1073741819)',
    '2026-10-28 00:42:14.890 [INFO] Crash dump written to C:\\Users\\EmreOyuncu\\Documents\\Rockstar Games\\GTA V\\Launcher.log'
  ].join('\n');
  parseAndApplyCrashLog('sample_gta5_crash.log', sampleLog);
}

function clearCrashLogAnalysis() {
  const box = document.getElementById('crashLogResultBox');
  const preEl = document.getElementById('crashLogExtractedPreview');
  const fileInp = document.getElementById('crashLogFileInput');
  if (box) box.classList.add('hidden');
  if (preEl) preEl.textContent = '';
  if (fileInp) fileInp.value = '';
}

function customizeIssueInAiLab(gameName, errorCode, title) {
  if (!STATE.currentUser && hasGuestUsedFreeTrial()) {
    showToast('🔒 Ücretsiz misafir AI analiz hakkınızı kullandınız. 2. sorgu için lütfen ücretsiz üye olun.');
    openAuthModal('register');
    return;
  }
  switchTab('ai-lab');
  document.getElementById('aiLabGameInput').value = gameName;
  previewSmartGameRecognition(gameName, 'aiLabSmartHint');
  document.getElementById('aiLabErrorCode').value = errorCode;
  if (STATE.currentUser && STATE.currentUser.system_specs) {
    document.getElementById('aiLabSpecs').value = STATE.currentUser.system_specs;
  } else {
    loadSavedHardwareSpecs();
  }
  document.getElementById('aiLabDescription').value = `${title} sorununu yaşıyorum. Standart adımları denedim, kendi donanımıma özel detaylı analiz ve çözüm adımlarını istiyorum.`;
  document.getElementById('aiLabSpecs').focus();
  window.scrollTo({ top: 220, behavior: 'smooth' });
}

async function submitAiDiagnostic(e) {
  e.preventDefault();

  // Section 2.3: Guest Trial Flow (1 free AI analysis for guests; 2nd query triggers registration modal)
  if (!STATE.currentUser && hasGuestUsedFreeTrial()) {
    showToast('🔒 İlk ücretsiz misafir AI analiz hakkınızı kullandınız! 2. sorgu ve çözümleri kaydetmek için ücretsiz üye olun.');
    openAuthModal('register');
    showAuthAlert(
      '🎁 <strong>İlk ücretsiz misafir AI analiz hakkınızı kullandınız.</strong> Sınırsız AI arıza çözümleme yapmak ve çözümleri kaydetmek için hemen ücretsiz hesap açın!',
      'info'
    );
    return;
  }

  const btn = document.getElementById('aiAnalyzeSubmitBtn');
  const origHtml = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '<span>⏳ Oyun Tanınıyor ve Yapay Zeka Çözüm Üretiyor...</span>';

  const payload = {
    game_slug: document.getElementById('aiLabGameInput').value.trim(),
    error_code: document.getElementById('aiLabErrorCode').value,
    system_specs: document.getElementById('aiLabSpecs').value,
    problem_description: document.getElementById('aiLabDescription').value,
    website_url: document.getElementById('aiLabHoneypot')?.value || ''
  };

  try {
    const res = await fetch('./api/ai/analyze', {
      method: 'POST',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) {
      showToast(data.detail || 'Lütfen giriş yapın.');
      if (res.status === 401) {
        markGuestFreeTrialUsed();
        updateAuthUI();
        openAuthModal('register');
        showAuthAlert(`🔒 ${escapeHTML(data.detail || '2. AI sorgusu için ücretsiz üye olun.')}`, 'info');
      }
      return;
    }

    if (!STATE.currentUser || data.guest_trial_used) {
      markGuestFreeTrialUsed();
      updateAuthUI();
    }

    if (data.resolved_game) {
      await fetchGames();
      STATE.selectedGame = data.resolved_game.slug;
      renderSidebarGames();
      updateHeroBanner();
      await Promise.all([fetchIssues(), fetchThreads()]);

      if (data.resolved_game.was_created) {
        showToast(`✨ "${data.resolved_game.name}" için özel oyun ekranı otomatik oluşturuldu!`);
      } else if (data.resolved_game.corrected_from) {
        showToast(`✨ "${data.resolved_game.corrected_from}" → "${data.resolved_game.name}" olarak tanındı!`);
      }
    }

    const card = document.getElementById('aiLabResultCard');
    const modeBadge = document.getElementById('aiResultModeBadge');
    const confEl = document.getElementById('aiResultConfidence');
    const safetyEl = document.getElementById('aiResultSafetyBanner');
    const contentEl = document.getElementById('aiLabResultContent');

    modeBadge.textContent = data.mode;
    if (confEl) {
      confEl.textContent = 'Adım Adım Teknik Çözüm Rehberi';
    }

    const safetyHtml = buildSafetyBannerHtml(`${payload.error_code} ${payload.problem_description} ${data.markdown}`) + buildRiskyCommandNotesHtml(`${payload.error_code} ${payload.problem_description} ${data.markdown}`);
    if (safetyEl) {
      if (safetyHtml) {
        safetyEl.innerHTML = safetyHtml;
        safetyEl.classList.remove('hidden');
      } else {
        safetyEl.innerHTML = '';
        safetyEl.classList.add('hidden');
      }
    }

    contentEl.innerHTML = formatSimpleMarkdown(data.markdown);
    const reportKey = encodeBase64Utf8(`${payload.game_slug}:${payload.error_code}`).slice(0, 16) || 'default';
    renderAiReportVoteBar(reportKey, null, Boolean(data.guest_trial_used || !STATE.currentUser));

    card.classList.remove('hidden');
    card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  } catch (err) {
    showToast('Analiz sırasında bir hata oluştu.');
  } finally {
    btn.disabled = false;
    btn.innerHTML = origHtml;
  }
}

async function fetchThreads() {
  const params = new URLSearchParams();
  if (STATE.selectedGame !== 'all') params.set('game_slug', STATE.selectedGame);
  if (STATE.searchQuery) params.set('search', STATE.searchQuery);

  const res = await fetch(`./api/threads?${params.toString()}`, { headers: getAuthHeaders() });
  STATE.threads = await res.json();
  const badgeEl = document.getElementById('threadsCountBadge');
  if (badgeEl) {
    badgeEl.textContent = STATE.threads.length > 0 ? String(STATE.threads.length) : '';
    badgeEl.classList.toggle('hidden', STATE.threads.length === 0);
  }
  renderThreads();
}

function renderThreads() {
  const container = document.getElementById('threadsListContainer') || document.getElementById('forumThreadsContainer');
  if (!container) return;
  if (STATE.threads.length === 0) {
    container.innerHTML = `
      <div class="oc-card p-8 text-center space-y-3">
        <div class="text-base font-bold text-white">Henüz bu konuda soru açılmamış</div>
        <p class="text-xs sm:text-sm text-gray-400 mx-auto">Yaşadığın hatayla ilgili ilk soruyu sen sor; hem topluluk hem de teknik analiz motorumuz yanıtlasın.</p>
        <button type="button" onclick="openAskModal()" class="oc-btn oc-btn-primary text-xs sm:text-sm">İlk soruyu sen sor</button>
      </div>
    `;
    return;
  }

  container.innerHTML = STATE.threads.map(t => {
    const repliesHtml = (t.replies || []).map(rep => {
      if (rep.is_ai) {
        const repSafetyHtml = buildSafetyBannerHtml(`${t.error_code || ''} ${t.title || ''} ${rep.content || ''}`) + buildRiskyCommandNotesHtml(`${t.error_code || ''} ${t.title || ''} ${rep.content || ''}`);
        return `
          <div class="ai-root-box p-4 space-y-2.5">
            <div class="flex flex-wrap items-center justify-between gap-2 border-b border-[#5e9c88]/20 pb-2">
              <div class="flex items-center gap-2">
                <span class="px-2 py-0.5 rounded bg-[#5e9c88] text-white font-extrabold text-[11px]">AI ÇÖZÜM</span>
                <span class="text-xs font-bold text-[#a3d9c6]">${escapeHTML(rep.author_name)}</span>
                <span class="text-[11px] text-gray-400">• ${escapeHTML(rep.ai_mode || 'Otomatik Teşhis')}</span>
              </div>
              <span class="text-[11px] text-gray-400">${escapeHTML(rep.created_at)}</span>
            </div>
            ${repSafetyHtml}
            <div class="ai-markdown text-xs sm:text-sm leading-relaxed">
              ${formatSimpleMarkdown(rep.content)}
              <div class="mt-2 p-2.5 rounded-lg bg-amber-500/15 border border-amber-400/35 text-[11px] font-semibold text-amber-100 flex items-center gap-1.5"><span>⚠️</span><span>Bu çözüm yapay zeka tarafından üretildi, uygulamadan önce geri yükleme noktası oluşturun.</span></div>
            </div>
          </div>
        `;
      } else {
        const safeRepPreview = escapeHTML((rep.content || '').slice(0, 45)).replace(/'/g, "\\'");
        return `
          <div class="bg-[#181e29] border border-white/10 rounded-xl p-3.5 space-y-1.5">
            <div class="flex items-center justify-between gap-2">
              <span class="text-xs font-bold text-[#a3b8d4]">👤 ${escapeHTML(rep.author_name)}</span>
              <div class="flex items-center gap-2.5">
                <span class="text-[11px] text-gray-400">${escapeHTML(rep.created_at)}</span>
                <button
                  type="button"
                  onclick="openReportModal('reply', ${Number(rep.id || 0)}, '${safeRepPreview}')"
                  class="text-[11px] text-gray-400 hover:text-red-300 transition flex items-center gap-1"
                  title="5651 Sayılı Kanun Kapsamında İçeriği Bildir"
                >
                  <span>🚨 İçeriği Bildir</span>
                </button>
              </div>
            </div>
            <p class="text-xs sm:text-sm text-gray-200">${renderSafeForumUserText(rep.content)}</p>
          </div>
        `;
      }
    }).join('');

    const voteBtnClass = t.user_voted ? 'vote-btn-active' : 'bg-white/5 hover:bg-white/10 text-gray-200';
    const voteBtnLabel = t.user_voted ? '✓ Faydalı Konu (Oylandı)' : '▲ Faydalı Konu';
    const safeThreadTitlePreview = escapeHTML((t.title || '').slice(0, 50)).replace(/'/g, "\\'");
    const tUpvotes = Number(t.upvotes || 0);

    return `
      <article class="issue-card p-6 space-y-4">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <div class="flex flex-wrap items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-white/10 text-white font-bold text-xs flex items-center justify-center">
              ${escapeHTML(t.author_avatar)}
            </div>
            <div>
              <div class="flex items-center gap-2">
                <span class="text-xs font-bold text-white">${escapeHTML(t.author_name)}</span>
                <span class="text-[11px] text-gray-400">• ${escapeHTML(t.created_at)}</span>
              </div>
              <div class="text-[11px] text-gray-400">${escapeHTML(t.system_specs || 'Sistem belirtilmedi')}</div>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <span class="text-xs font-bold px-2.5 py-1 rounded-lg text-white cursor-pointer flex items-center gap-2" style="background-color: ${escapeHTML(t.accent_color)}" onclick="selectGame('${escapeHTML(t.game_slug)}')">
              <img loading="lazy" decoding="async"
                src="${fallbackCover(t.game_short_name || t.game_slug, t.accent_color)}"
                onerror="this.onerror=null;this.src=fallbackCover('${escapeHTML(t.game_slug)}','${escapeHTML(t.accent_color)}')"
                alt="${escapeHTML(t.game_short_name)}"
                class="w-6 h-4 rounded object-cover border border-white/20"
              />
              <span>${escapeHTML(t.game_short_name)}</span>
            </span>
            ${t.error_code ? `<span class="text-xs font-mono px-2.5 py-1 rounded-lg bg-white/5 text-[#d9c382] border border-white/10">${escapeHTML(t.error_code)}</span>` : ''}
            <span class="text-xs font-semibold px-2.5 py-1 rounded-lg bg-[#5e9c88]/20 text-[#a3d9c6] border border-[#5e9c88]/30">
              ✓ ${escapeHTML(t.status)}
            </span>
          </div>
        </div>

        <div class="space-y-1.5">
          <h3 class="text-base sm:text-lg font-bold text-white">${escapeHTML(t.title)}</h3>
          <p class="text-xs sm:text-sm text-gray-300 leading-relaxed">${renderSafeForumUserText(t.content)}</p>
        </div>

        <div class="space-y-3 pt-2">
          ${repliesHtml}
        </div>

        <div class="pt-3 border-t border-white/10 space-y-3">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div class="flex items-center gap-2">
              <button
                id="threadVoteBtn-${t.id}"
                onclick="upvoteThread(${t.id})"
                class="px-3.5 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 border border-white/10 transition ${voteBtnClass}"
              >
                <span id="threadVoteText-${t.id}">${voteBtnLabel}</span>
                <span id="threadVote-${t.id}" class="${tUpvotes > 0 ? '' : 'hidden'}">${tUpvotes > 0 ? `(${tUpvotes})` : ''}</span>
              </button>
              <button
                type="button"
                onclick="openReportModal('thread', ${Number(t.id)}, '${safeThreadTitlePreview}')"
                class="px-3 py-1.5 rounded-xl text-xs font-semibold bg-red-500/10 hover:bg-red-500/20 text-red-300 border border-red-500/25 transition flex items-center gap-1"
              >
                <span>🚨 İçeriği Bildir</span>
              </button>
            </div>
            <button
              onclick="toggleReplyForm(${t.id})"
              class="text-xs font-semibold text-[#88c0a8] hover:underline"
            >
              💬 Topluluk Yanıtı Ekle
            </button>
          </div>

          <form id="replyForm-${t.id}" onsubmit="submitThreadReply(event, ${t.id})" class="hidden flex flex-col sm:flex-row gap-2 pt-1">
            <input
              id="replyContent-${t.id}"
              type="text"
              required
              placeholder="Bu sorunla ilgili çözüm veya deneyiminizi yazın..."
              class="flex-1 bg-[#161b24] text-xs text-white rounded-xl px-3 py-2 border border-white/10"
            />
            <button type="submit" class="accent-btn px-4 py-2 rounded-xl text-xs shrink-0">
              Gönder
            </button>
          </form>
        </div>
      </article>
    `;
  }).join('');
}

function toggleReplyForm(threadId) {
  if (!requireMemberAuth('Konuya yanıt yazmak')) return;
  const form = document.getElementById(`replyForm-${threadId}`);
  form.classList.toggle('hidden');
}

async function submitThreadReply(e, threadId) {
  e.preventDefault();
  if (!requireMemberAuth('Konuya yanıt yazmak')) return;
  const content = document.getElementById(`replyContent-${threadId}`).value;

  const res = await fetch(`./api/threads/${threadId}/replies`, {
    method: 'POST',
    headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ content, website_url: '' })
  });
  const data = await res.json();
  if (res.ok) {
    showToast('Yanıtınız foruma eklendi!');
    await fetchThreads();
  } else {
    showToast(data.detail || 'Yanıt gönderilemedi.');
  }
}

async function upvoteThread(threadId) {
  const res = await fetch(`./api/threads/${threadId}/upvote`, {
    method: 'POST',
    headers: getAuthHeaders()
  });
  if (res.ok) {
    const data = await res.json();
    const countEl = document.getElementById(`threadVote-${threadId}`);
    const textEl = document.getElementById(`threadVoteText-${threadId}`);
    const btnEl = document.getElementById(`threadVoteBtn-${threadId}`);
    const upCnt = Number(data.upvotes || 0);

    if (countEl) {
      countEl.textContent = upCnt > 0 ? `(${upCnt})` : '';
      countEl.classList.toggle('hidden', upCnt === 0);
    }
    if (data.user_voted) {
      if (textEl) textEl.textContent = '✓ Faydalı Konu (Oylandı)';
      if (btnEl) btnEl.classList.add('vote-btn-active');
      showToast('Konuyu faydalı olarak işaretlediniz!');
    } else {
      if (textEl) textEl.textContent = '▲ Faydalı Konu';
      if (btnEl) btnEl.classList.remove('vote-btn-active');
      showToast('Oyunuz geri alındı.');
    }
  }
}

// --- SECTION 1.3: 5651 CONTENT REPORTING (🚨 İçeriği Bildir) ---

function openReportModal(targetType, targetId, previewTitle = '') {
  ensureLazyModalMounted('reportContentModal');
  document.getElementById('reportTargetType').value = targetType || 'thread';
  document.getElementById('reportTargetId').value = String(targetId || 0);
  document.getElementById('reportDetailsInput').value = '';
  const prevEl = document.getElementById('reportModalTargetPreview');
  if (prevEl) {
    prevEl.textContent = previewTitle
      ? `Bildirilen İçerik: "${previewTitle}" (#${targetId})`
      : `İçerik #${targetId} (${targetType})`;
  }
  document.getElementById('reportContentModal').classList.remove('hidden');
}

function closeReportModal() {
  document.getElementById('reportContentModal').classList.add('hidden');
}

async function submitContentReport(e) {
  e.preventDefault();
  const target_type = document.getElementById('reportTargetType').value;
  const target_id = Number(document.getElementById('reportTargetId').value || 0);
  const reason = document.getElementById('reportReasonSelect').value;
  const details = document.getElementById('reportDetailsInput').value.trim();

  const btn = document.getElementById('reportSubmitBtn');
  const origText = btn.textContent;
  btn.disabled = true;
  btn.textContent = '⏳ Gönderiliyor...';

  try {
    const res = await fetch('./api/reports', {
      method: 'POST',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ target_type, target_id, reason, details })
    });
    const data = await res.json();
    closeReportModal();
    showToast(data.message || '🚨 Bildiriminiz 5651 sayılı kanun kapsamında kaydedildi.');
  } catch (err) {
    showToast('Bildirim gönderilirken hata oluştu.');
  } finally {
    btn.disabled = false;
    btn.textContent = origText;
  }
}

function openAskModal() {
  if (!requireMemberAuth('Foruma yeni soru sormak ve AI çözümü almak')) return;
  ensureLazyModalMounted('askQuestionModal');
  refreshRandomSuggestions();
  if (STATE.selectedGame !== 'all') {
    const g = STATE.games.find(x => x.slug === STATE.selectedGame);
    if (g) {
      document.getElementById('modalThreadGameInput').value = g.name;
      previewSmartGameRecognition(g.name, 'modalGameSmartHint');
    }
  } else {
    document.getElementById('modalThreadGameInput').value = '';
    document.getElementById('modalGameSmartHint').textContent = '';
  }

  if (STATE.currentUser && STATE.currentUser.system_specs) {
    document.getElementById('modalThreadSpecs').value = STATE.currentUser.system_specs;
  } else {
    loadSavedHardwareSpecs();
  }
  document.getElementById('askQuestionModal').classList.remove('hidden');
}

function closeAskModal() {
  document.getElementById('askQuestionModal').classList.add('hidden');
}

async function submitNewThread(e) {
  e.preventDefault();
  if (!requireMemberAuth('Foruma soru sormak')) return;

  const btn = document.getElementById('modalThreadSubmitBtn');
  const origText = btn.textContent;
  btn.disabled = true;
  btn.textContent = '⏳ Oyun Tanınıyor ve AI Yanıtlıyor...';

  const payload = {
    game_slug: document.getElementById('modalThreadGameInput').value.trim(),
    error_code: document.getElementById('modalThreadErrorCode').value,
    system_specs: document.getElementById('modalThreadSpecs').value,
    title: document.getElementById('modalThreadTitle').value,
    content: document.getElementById('modalThreadContent').value,
    website_url: document.getElementById('modalThreadHoneypot')?.value || ''
  };

  try {
    const res = await fetch('./api/threads', {
      method: 'POST',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      const data = await res.json();
      closeAskModal();
      document.getElementById('modalThreadTitle').value = '';
      document.getElementById('modalThreadContent').value = '';

      await fetchGames();
      if (data.resolved_game) {
        STATE.selectedGame = data.resolved_game.slug;
        renderSidebarGames();
        updateHeroBanner();
      }
      switchTab('forum');
      await Promise.all([fetchIssues(), fetchThreads()]);

      if (data.resolved_game && data.resolved_game.was_created) {
        showToast(`✨ "${data.resolved_game.name}" sayfası otomatik oluşturuldu ve sorunuz AI tarafından yanıtlandı!`);
      } else {
        showToast('Sorunuz yayınlandı ve OyunÇöz AI tarafından yanıtlandı!');
      }
    } else {
      const errData = await res.json();
      showToast(errData.detail || 'Soru gönderilemedi.');
    }
  } catch (err) {
    showToast('Soru gönderilirken hata oluştu.');
  } finally {
    btn.disabled = false;
    btn.textContent = origText;
  }
}


// --- STAGE 4.1: LAZY MODAL RENDERING (Modals are NOT in initial DOM until user opens them) ---
const LAZY_MODAL_TEMPLATES = {"askQuestionModal": "<div id=\"askQuestionModal\" class=\"hidden fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4\">\n    <div class=\"bg-[#1d2430] border border-white/15 rounded-2xl max-w-2xl w-full p-6 space-y-4 shadow-2xl max-h-[92vh] overflow-y-auto\">\n      <div class=\"flex items-center justify-between border-b border-white/10 pb-3\">\n        <div>\n          <h3 class=\"text-lg font-bold text-white\">Foruma Yeni Soru Sor (Otomatik AI Çözümlü)</h3>\n          <p class=\"text-xs text-gray-400\">Listede olmayan bir oyun yazarsanız (örn: <code>victorie 3</code>) oyunu otomatik tanır ve sayfasını oluşturur.</p>\n        </div>\n        <button onclick=\"closeAskModal()\" class=\"text-gray-400 hover:text-white p-1\">✕</button>\n      </div>\n\n      <!-- Random Suggestions inside Modal -->\n      <div class=\"bg-[#181e29] border border-white/10 rounded-xl p-3 space-y-2\">\n        <div class=\"flex items-center justify-between\">\n          <span class=\"text-[11px] font-semibold text-[#a3d9c6]\">🎲 Oyun Dünyasından Rastgele Öneriler (İsterseniz tıklayın veya kendi oyununuzu yazın):</span>\n          <button type=\"button\" onclick=\"refreshRandomSuggestions()\" class=\"text-[11px] px-2 py-0.5 rounded bg-white/5 hover:bg-white/10 text-gray-300\">🔄 Yenile</button>\n        </div>\n        <div id=\"modalSuggestionsContainer\" class=\"flex flex-wrap gap-1.5\"></div>\n      </div>\n\n      <form onsubmit=\"submitNewThread(event)\" class=\"space-y-4\">\n        <!-- Honeypot Bot Trap -->\n        <div class=\"hidden\" aria-hidden=\"true\" style=\"position:absolute;left:-9999px;opacity:0;pointer-events:none;\">\n          <input id=\"modalThreadHoneypot\" name=\"website_url\" type=\"text\" tabindex=\"-1\" autocomplete=\"off\" />\n        </div>\n        <div class=\"grid grid-cols-1 sm:grid-cols-2 gap-4\">\n          <div>\n            <label class=\"block text-xs font-semibold text-gray-300 mb-1\">Oyun Adı (Yazın veya Seçin)</label>\n            <input\n              id=\"modalThreadGameInput\"\n              list=\"allGamesDatalist\"\n              type=\"text\"\n              required\n              placeholder=\"Örn: victorie 3, Valorant, RDR 2...\"\n              oninput=\"previewSmartGameRecognition(this.value, 'modalGameSmartHint')\"\n              class=\"w-full bg-[#212936] text-sm text-white rounded-xl px-3 py-2.5 border border-white/10\"\n            />\n            <div id=\"modalGameSmartHint\" class=\"text-[11px] text-[#88c0a8] mt-1 min-h-[16px]\"></div>\n          </div>\n          <div>\n            <label class=\"block text-xs font-semibold text-gray-300 mb-1\">Hata Kodu (Varsa)</label>\n            <input id=\"modalThreadErrorCode\" type=\"text\" placeholder=\"Örn: Late-Game Lag, VAN 9003, VAC\" class=\"w-full bg-[#212936] text-sm text-white rounded-xl px-3 py-2.5 border border-white/10\" />\n          </div>\n        </div>\n\n        <div>\n          <div class=\"flex items-center justify-between mb-1\">\n            <label class=\"block text-xs font-semibold text-gray-300\">Sistem Özellikleriniz</label>\n            <button type=\"button\" onclick=\"autoFillSingleSpecsInput('modalThreadSpecs')\" class=\"text-[11px] font-bold text-[#a3d9c6] hover:text-white px-2 py-0.5 rounded bg-[#5e9c88]/20 border border-[#88c0a8]/35 transition\">\n              🖥️ Otomatik Algıla ve Doldur\n            </button>\n          </div>\n          <input id=\"modalThreadSpecs\" type=\"text\" placeholder=\"Örn: Win 11, RTX 4060, i5-13400F\" class=\"w-full bg-[#212936] text-sm text-white rounded-xl px-3 py-2.5 border border-white/10\" />\n        </div>\n\n        <div>\n          <label class=\"block text-xs font-semibold text-gray-300 mb-1\">Konu Başlığı</label>\n          <input id=\"modalThreadTitle\" type=\"text\" required placeholder=\"Sorununuzu özetleyen net bir başlık yazın...\" class=\"w-full bg-[#212936] text-sm text-white rounded-xl px-3 py-2.5 border border-white/10\" />\n        </div>\n\n        <div>\n          <label class=\"block text-xs font-semibold text-gray-300 mb-1\">Sorun Açıklaması</label>\n          <textarea id=\"modalThreadContent\" rows=\"4\" required placeholder=\"Hatanın nasıl oluştuğunu ve denediğiniz yöntemleri detaylıca paylaşın...\" class=\"w-full bg-[#212936] text-sm text-white rounded-xl p-3 border border-white/10\"></textarea>\n        </div>\n\n        <div class=\"flex items-center justify-end gap-3 pt-2\">\n          <button type=\"button\" onclick=\"closeAskModal()\" class=\"px-4 py-2 rounded-xl text-xs font-semibold bg-white/5 text-gray-300 hover:bg-white/10\">\n            İptal\n          </button>\n          <button type=\"submit\" id=\"modalThreadSubmitBtn\" class=\"accent-btn px-5 py-2.5 rounded-xl text-xs sm:text-sm\">\n            🚀 Soruyu Yayınla ve AI İle Çözümle\n          </button>\n        </div>\n      </form>\n    </div>\n  </div>", "addGameModal": "<div id=\"addGameModal\" class=\"hidden fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4\">\n    <div class=\"bg-[#1d2430] border border-white/15 rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl\">\n      <div class=\"flex items-center justify-between border-b border-white/10 pb-3\">\n        <div>\n          <h3 class=\"text-lg font-bold text-white\">✨ Yeni Oyun Ekle & Özel Sayfa Oluştur</h3>\n          <p class=\"text-xs text-gray-400\">Oyun adını yazın (örn: <code>victorie 3</code>) veya önerilerden seçin; AI doğru oyunu bulup forum sorunlarıyla birlikte sayfasını hazırlasın.</p>\n        </div>\n        <button onclick=\"closeAddGameModal()\" class=\"text-gray-400 hover:text-white p-1\">✕</button>\n      </div>\n\n      <!-- Random World Game Suggestions inside Add Game Modal -->\n      <div class=\"bg-[#181e29] border border-white/10 rounded-xl p-3.5 space-y-2\">\n        <div class=\"flex items-center justify-between\">\n          <span class=\"text-xs font-semibold text-[#a3d9c6]\">🎲 Oyun Dünyasından Öneriler:</span>\n          <button type=\"button\" onclick=\"refreshRandomSuggestions()\" class=\"text-xs px-2 py-0.5 rounded bg-white/5 hover:bg-white/10 text-gray-300\">🔄 Rastgele Getir</button>\n        </div>\n        <div id=\"addGameSuggestionsContainer\" class=\"flex flex-wrap gap-1.5\"></div>\n      </div>\n\n      <form onsubmit=\"submitAddNewGame(event)\" class=\"space-y-4\">\n        <div>\n          <label class=\"block text-xs font-semibold text-gray-300 mb-1.5\">Eklemek İstediğiniz Oyun Adı</label>\n          <input\n            id=\"newGameQueryInput\"\n            type=\"text\"\n            required\n            placeholder=\"Örn: victorie 3, Bannerlord, RDR 2, HOI4...\"\n            oninput=\"previewSmartGameRecognition(this.value, 'addGameSmartHint')\"\n            class=\"w-full bg-[#212936] text-sm text-white rounded-xl px-3.5 py-2.5 border border-white/10 focus:outline-none focus:border-white/25\"\n          />\n          <div id=\"addGameSmartHint\" class=\"text-xs text-[#88c0a8] mt-1.5 min-h-[20px]\"></div>\n        </div>\n\n        <div class=\"flex justify-end gap-2 pt-2\">\n          <button type=\"button\" onclick=\"closeAddGameModal()\" class=\"px-4 py-2 rounded-xl text-xs bg-white/5 text-gray-300\">İptal</button>\n          <button type=\"submit\" id=\"addGameSubmitBtn\" class=\"accent-btn px-5 py-2.5 rounded-xl text-xs sm:text-sm\">\n            🚀 Oyun Sayfasını Oluştur ve Aç\n          </button>\n        </div>\n      </form>\n    </div>\n  </div>", "authModal": "<div id=\"authModal\" class=\"hidden fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4\">\n    <div class=\"bg-[#1d2430] border border-white/15 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl\">\n      <div class=\"flex items-center justify-between border-b border-white/10 pb-3\">\n        <div class=\"flex gap-4\">\n          <button type=\"button\" id=\"authTabLogin\" onclick=\"switchAuthTab('login')\" class=\"text-sm font-bold text-white border-b-2 border-[#5e9c88] pb-1\">\n            Giriş Yap\n          </button>\n          <button type=\"button\" id=\"authTabRegister\" onclick=\"switchAuthTab('register')\" class=\"text-sm font-bold text-gray-400 border-b-2 border-transparent pb-1\">\n            Yeni Hesap Aç\n          </button>\n        </div>\n        <button type=\"button\" onclick=\"closeAuthModal()\" class=\"text-gray-400 hover:text-white p-1\">✕</button>\n      </div>\n\n      <!-- Inline Feedback / Error Box inside Modal -->\n      <div id=\"authModalAlert\" class=\"hidden rounded-xl p-3 text-xs leading-relaxed border\"></div>\n\n      <!-- Login Form -->\n      <form id=\"loginForm\" onsubmit=\"submitLogin(event)\" class=\"space-y-3.5\">\n        <div>\n          <label class=\"block text-xs font-semibold text-gray-300 mb-1\">Kullanıcı Adı veya E-Posta</label>\n          <input id=\"loginIdentifier\" type=\"text\" required placeholder=\"Kullanıcı adınız veya e-posta adresiniz\" class=\"w-full bg-[#212936] text-sm text-white rounded-xl px-3.5 py-2.5 border border-white/10 focus:outline-none focus:border-[#5e9c88]\" />\n        </div>\n        <div>\n          <label class=\"block text-xs font-semibold text-gray-300 mb-1\">Şifre</label>\n          <input id=\"loginPassword\" type=\"password\" required placeholder=\"••••••••\" class=\"w-full bg-[#212936] text-sm text-white rounded-xl px-3.5 py-2.5 border border-white/10 focus:outline-none focus:border-[#5e9c88]\" />\n        </div>\n        <div class=\"flex items-center justify-between pt-2\">\n          <button type=\"button\" onclick=\"switchAuthTab('register')\" class=\"text-xs text-[#88c0a8] hover:underline font-medium\">\n            Hesabınız yok mu? Yeni Hesap Açın →\n          </button>\n          <div class=\"flex gap-2\">\n            <button type=\"button\" onclick=\"closeAuthModal()\" class=\"px-3.5 py-2 rounded-xl text-xs bg-white/5 text-gray-300\">İptal</button>\n            <button type=\"submit\" id=\"loginSubmitBtn\" class=\"accent-btn px-5 py-2 rounded-xl text-xs\">Giriş Yap</button>\n          </div>\n        </div>\n      </form>\n\n      <!-- Register Step 1: Enter Details & Request Verification Code -->\n      <form id=\"registerFormStep1\" onsubmit=\"requestEmailVerificationCode(event)\" class=\"hidden space-y-3.5\">\n        <!-- Honeypot Bot Trap -->\n        <div class=\"hidden\" aria-hidden=\"true\" style=\"position:absolute;left:-9999px;opacity:0;pointer-events:none;\">\n          <input id=\"regHoneypot\" name=\"website_url\" type=\"text\" tabindex=\"-1\" autocomplete=\"off\" />\n        </div>\n        <div>\n          <label class=\"block text-xs font-semibold text-gray-300 mb-1\">Kullanıcı Adı</label>\n          <input id=\"regUsername\" type=\"text\" required placeholder=\"Örn: MertFPS\" class=\"w-full bg-[#212936] text-sm text-white rounded-xl px-3.5 py-2.5 border border-white/10 focus:outline-none focus:border-[#5e9c88]\" />\n        </div>\n        <div>\n          <label class=\"block text-xs font-semibold text-gray-300 mb-1\">E-Posta Adresi (Onay kodu gönderilecek)</label>\n          <input id=\"regEmail\" type=\"email\" required placeholder=\"ornek@mail.com\" class=\"w-full bg-[#212936] text-sm text-white rounded-xl px-3.5 py-2.5 border border-white/10 focus:outline-none focus:border-[#5e9c88]\" />\n        </div>\n        <div>\n          <label class=\"block text-xs font-semibold text-gray-300 mb-1\">Şifre</label>\n          <input id=\"regPassword\" type=\"password\" required placeholder=\"En az 4 karakter\" class=\"w-full bg-[#212936] text-sm text-white rounded-xl px-3.5 py-2.5 border border-white/10 focus:outline-none focus:border-[#5e9c88]\" />\n        </div>\n        <div>\n          <div class=\"flex items-center justify-between mb-1\">\n            <label class=\"block text-xs font-semibold text-gray-300\">Sistem Özellikleriniz (Opsiyonel)</label>\n            <button type=\"button\" onclick=\"autoFillSingleSpecsInput('regSpecs')\" class=\"text-[11px] font-bold text-[#a3d9c6] hover:text-white px-2 py-0.5 rounded bg-[#5e9c88]/20 border border-[#88c0a8]/35 transition\">\n              🖥️ Otomatik Algıla\n            </button>\n          </div>\n          <input id=\"regSpecs\" type=\"text\" placeholder=\"Örn: Win 11, Ryzen 5 5600, RTX 4060, 16GB RAM\" class=\"w-full bg-[#212936] text-sm text-white rounded-xl px-3.5 py-2.5 border border-white/10 focus:outline-none focus:border-[#5e9c88]\" />\n        </div>\n        <div class=\"pt-1\">\n          <label class=\"flex items-start gap-2.5 cursor-pointer text-xs text-gray-300 leading-relaxed\">\n            <input id=\"regKvkkConsent\" type=\"checkbox\" required class=\"mt-0.5 rounded border-white/20 bg-[#212936] text-[#5e9c88] focus:ring-0\" />\n            <span>\n              <button type=\"button\" onclick=\"window.open('./kvkk-aydinlatma-metni.html', '_blank')\" class=\"text-[#88c0a8] hover:underline font-semibold\">KVKK Aydınlatma Metni</button> ve\n              <button type=\"button\" onclick=\"window.open('./kullanim-kosullari.html', '_blank')\" class=\"text-[#88c0a8] hover:underline font-semibold\">Kullanım Koşullarını</button> okudum, onaylıyorum. <span class=\"text-amber-300 font-bold\">(Zorunlu Açık Rıza)</span>\n            </span>\n          </label>\n        </div>\n        <div class=\"flex justify-end gap-2 pt-2\">\n          <button type=\"button\" onclick=\"closeAuthModal()\" class=\"px-4 py-2 rounded-xl text-xs bg-white/5 text-gray-300\">İptal</button>\n          <button type=\"submit\" id=\"sendCodeBtn\" class=\"accent-btn px-5 py-2 rounded-xl text-xs\">\n            📩 E-Postaya Onay Kodu Gönder\n          </button>\n        </div>\n      </form>\n\n      <!-- Register Step 2: Enter 6-Digit Email Verification Code -->\n      <form id=\"registerFormStep2\" onsubmit=\"verifyCodeAndCompleteRegister(event)\" class=\"hidden space-y-4\">\n        <div class=\"bg-[#181e29] border border-[#5e9c88]/40 rounded-xl p-3.5 space-y-1.5\">\n          <div class=\"text-xs font-bold text-[#a3d9c6]\">📩 E-Posta Doğrulama Kodu Gönderildi</div>\n          <p id=\"verifyEmailTargetText\" class=\"text-xs text-gray-300\"></p>\n          <p class=\"text-[11px] text-gray-400\">Kod 10 dakika geçerlidir, tek kullanımlıktır ve 5 hatalı denemede kilitlenir.</p>\n        </div>\n\n        <div>\n          <label class=\"block text-xs font-semibold text-gray-300 mb-1.5\">6 Haneli Onay Kodu</label>\n          <input\n            id=\"regVerificationCodeInput\"\n            type=\"text\"\n            maxlength=\"6\"\n            required\n            placeholder=\"Örn: 482915\"\n            class=\"w-full bg-[#212936] text-center font-mono text-lg tracking-widest text-white rounded-xl px-3.5 py-2.5 border border-white/15 focus:outline-none focus:border-[#5e9c88]\"\n          />\n        </div>\n\n        <div class=\"flex items-center justify-between pt-2\">\n          <button type=\"button\" onclick=\"backToRegisterStep1()\" class=\"text-xs text-gray-400 hover:text-white\">\n            ← Bilgileri Düzenle\n          </button>\n          <button type=\"submit\" id=\"verifyCodeSubmitBtn\" class=\"accent-btn px-5 py-2.5 rounded-xl text-xs\">\n            ✓ Kodu Doğrula ve Hesabı Aç\n          </button>\n        </div>\n      </form>\n    </div>\n  </div>", "profileModal": "<div id=\"profileModal\" class=\"hidden fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4\">\n    <div class=\"bg-[#1d2430] border border-white/15 rounded-2xl max-w-lg w-full p-6 space-y-5 shadow-2xl\">\n      <div class=\"flex items-center justify-between border-b border-white/10 pb-3\">\n        <div class=\"flex items-center gap-3\">\n          <div id=\"profileModalAvatar\" class=\"w-10 h-10 rounded-xl accent-btn flex items-center justify-center font-bold text-sm\">OY</div>\n          <div>\n            <h3 id=\"profileModalUsername\" class=\"text-base font-bold text-white\">Oyuncu</h3>\n            <p id=\"profileModalEmail\" class=\"text-xs text-gray-400\">oyuncu@mail.com</p>\n          </div>\n        </div>\n        <button onclick=\"closeProfileModal()\" class=\"text-gray-400 hover:text-white p-1\">✕</button>\n      </div>\n\n      <form onsubmit=\"saveUserProfile(event)\" class=\"space-y-3.5\">\n        <div>\n          <div class=\"flex items-center justify-between mb-1\">\n            <label class=\"block text-xs font-semibold text-gray-300\">Kayıtlı Bilgisayar / Sistem Özelliklerim</label>\n            <button type=\"button\" onclick=\"autoFillSingleSpecsInput('profileSpecsInput')\" class=\"text-[11px] font-bold text-[#a3d9c6] hover:text-white px-2 py-0.5 rounded bg-[#5e9c88]/20 border border-[#88c0a8]/35 transition\">\n              🖥️ Otomatik Algıla\n            </button>\n          </div>\n          <input id=\"profileSpecsInput\" type=\"text\" placeholder=\"Örn: Windows 11, Ryzen 5 5600, RTX 4060, 16GB RAM\" class=\"w-full bg-[#212936] text-sm text-white rounded-xl px-3.5 py-2.5 border border-white/10\" />\n          <p class=\"text-[11px] text-gray-400 mt-1\">AI Çözümleyici ve Forum sorularında donanımınız otomatik olarak doldurulur.</p>\n        </div>\n        <div>\n          <label class=\"block text-xs font-semibold text-gray-300 mb-1\">Favori Oyunum</label>\n          <select id=\"profileFavGameSelect\" class=\"w-full bg-[#212936] text-sm text-white rounded-xl px-3.5 py-2.5 border border-white/10\"></select>\n        </div>\n        <div class=\"flex justify-between items-center pt-1\">\n          <button type=\"button\" onclick=\"logoutUser()\" class=\"px-3.5 py-2 rounded-xl text-xs font-semibold bg-white/10 text-gray-200 hover:bg-white/15 border border-white/15\">\n            Çıkış Yap\n          </button>\n          <button type=\"submit\" class=\"accent-btn px-4 py-2 rounded-xl text-xs\">\n            Profili Güncelle\n          </button>\n        </div>\n        <!-- KVKK Article 11 Right to Erasure (Permanent Account & Data Deletion) -->\n        <div class=\"pt-3 mt-2 border-t border-white/10 flex flex-col sm:flex-row sm:items-center justify-between gap-2\">\n          <span class=\"text-[11px] text-gray-400\">6698 Sayılı KVKK Madde 11 kapsamında veri silme hakkı:</span>\n          <button\n            type=\"button\"\n            onclick=\"deleteMyAccountPermanently()\"\n            class=\"px-3.5 py-2 rounded-xl text-xs font-bold bg-red-500/15 text-red-300 hover:bg-red-500/30 border border-red-500/35 transition\"\n          >\n            🗑️ Hesabımı ve Tüm Verilerimi Kalıcı Olarak Sil\n          </button>\n        </div>\n      </form>\n    </div>\n  </div>", "reportContentModal": "<div id=\"reportContentModal\" class=\"hidden fixed inset-0 z-[66] bg-black/75 backdrop-blur-sm flex items-center justify-center p-4\">\n    <div class=\"bg-[#1d2430] border border-red-500/35 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl\">\n      <div class=\"flex items-center justify-between border-b border-white/10 pb-3\">\n        <div>\n          <h3 class=\"text-base font-bold text-white flex items-center gap-2\">\n            <span>🚨 İçeriği Bildir (5651 Uyarı & Kaldır)</span>\n          </h3>\n          <p id=\"reportModalTargetPreview\" class=\"text-[11px] text-gray-400 mt-0.5 truncate\">İçerik İnceleme Bildirimi</p>\n        </div>\n        <button type=\"button\" onclick=\"closeReportModal()\" class=\"text-gray-400 hover:text-white p-1\">✕</button>\n      </div>\n      <form onsubmit=\"submitContentReport(event)\" class=\"space-y-3.5\">\n        <input id=\"reportTargetType\" type=\"hidden\" value=\"thread\" />\n        <input id=\"reportTargetId\" type=\"hidden\" value=\"0\" />\n        <div>\n          <label class=\"block text-xs font-semibold text-gray-300 mb-1\">Bildirim Nedeni</label>\n          <select id=\"reportReasonSelect\" required class=\"w-full bg-[#212936] text-xs text-white rounded-xl px-3 py-2.5 border border-white/10\">\n            <option value=\"Küfür / Hakaret / Nefret Söylemi\">Küfür / Hakaret / Nefret Söylemi</option>\n            <option value=\"Crack / Warez / Korsan Paylaşım\">Crack / Warez / Korsan Paylaşım</option>\n            <option value=\"Hile / Zararlı Link / Kısaltılmış Link\">Hile / Zararlı Link / Kısaltılmış Link</option>\n            <option value=\"Kişisel Veri İfşası (KVKK İhlali)\">Kişisel Veri İfşası (KVKK İhlali)</option>\n            <option value=\"Spam veya Yanıltıcı Teknik Komut\">Spam veya Yanıltıcı Teknik Komut</option>\n          </select>\n        </div>\n        <div>\n          <label class=\"block text-xs font-semibold text-gray-300 mb-1\">Ek Açıklama (Opsiyonel)</label>\n          <textarea id=\"reportDetailsInput\" rows=\"2\" placeholder=\"İnceleme ekibimiz için ek bilgi...\" class=\"w-full bg-[#212936] text-xs text-white rounded-xl p-3 border border-white/10\"></textarea>\n        </div>\n        <div class=\"flex justify-end gap-2 pt-1\">\n          <button type=\"button\" onclick=\"closeReportModal()\" class=\"px-3.5 py-2 rounded-xl text-xs bg-white/5 text-gray-300\">İptal</button>\n          <button type=\"submit\" id=\"reportSubmitBtn\" class=\"px-4 py-2 rounded-xl text-xs font-bold bg-red-500/25 hover:bg-red-500/40 text-red-200 border border-red-400/40 transition\">\n            🚨 Bildirimi Gönder\n          </button>\n        </div>\n      </form>\n    </div>\n  </div>", "cookieSettingsModal": "<div id=\"cookieSettingsModal\" class=\"hidden fixed inset-0 z-[68] bg-black/75 backdrop-blur-sm flex items-center justify-center p-4\">\n    <div class=\"bg-[#1b2230] border border-white/15 rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl\">\n      <div class=\"flex items-center justify-between border-b border-white/10 pb-3\">\n        <div class=\"flex items-center gap-2.5\">\n          <span class=\"text-xl\">🍪</span>\n          <div>\n            <h3 class=\"text-base font-bold text-white\">Çerez ve Gizlilik Tercihleri</h3>\n            <p class=\"text-xs text-gray-400\">KVKK ve GDPR uyumlu çerez yönetim paneli</p>\n          </div>\n        </div>\n        <button type=\"button\" onclick=\"closeCookieSettingsModal()\" class=\"text-gray-400 hover:text-white p-1\">✕</button>\n      </div>\n\n      <div class=\"space-y-3 text-xs\">\n        <div class=\"p-3.5 rounded-xl bg-[#151b26] border border-white/10 flex items-start justify-between gap-3\">\n          <div>\n            <div class=\"font-bold text-white\">1. Zorunlu Güvenlik & Oturum Çerezleri</div>\n            <p class=\"text-gray-400 mt-0.5\">Üye girişi, e-posta doğrulama ve oylama güvenliği için gereklidir. Devre dışı bırakılamaz.</p>\n          </div>\n          <span class=\"px-2 py-0.5 rounded bg-[#5e9c88]/20 text-[#a3d9c6] font-bold shrink-0\">Her Zaman Aktif</span>\n        </div>\n\n        <label class=\"p-3.5 rounded-xl bg-[#151b26] border border-white/10 flex items-start justify-between gap-3 cursor-pointer\">\n          <div>\n            <div class=\"font-bold text-white\">2. İşlevsel & Donanım Hatırlama Çerezleri</div>\n            <p class=\"text-gray-400 mt-0.5\">Sistem özelliklerinizi (GPU/CPU) ve son seçtiğiniz oyun ekranını hatırlar.</p>\n          </div>\n          <input id=\"cookiePrefFunctional\" type=\"checkbox\" checked class=\"mt-1 w-4 h-4 rounded accent-[#5e9c88]\" />\n        </label>\n\n        <label class=\"p-3.5 rounded-xl bg-[#151b26] border border-white/10 flex items-start justify-between gap-3 cursor-pointer\">\n          <div>\n            <div class=\"font-bold text-white\">3. Performans & Akıllı Önbellek Çerezleri</div>\n            <p class=\"text-gray-400 mt-0.5\">En çok aranan hata kodlarını önbelleğe alarak çözümlerin 0 gecikmeyle açılmasını sağlar.</p>\n          </div>\n          <input id=\"cookiePrefAnalytics\" type=\"checkbox\" checked class=\"mt-1 w-4 h-4 rounded accent-[#5e9c88]\" />\n        </label>\n      </div>\n\n      <div class=\"flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-white/10\">\n        <button type=\"button\" onclick=\"acceptCookies('essential')\" class=\"px-3.5 py-2 rounded-xl text-xs bg-white/5 hover:bg-white/10 text-gray-300\">\n          Sadece Zorunlular\n        </button>\n        <div class=\"flex gap-2\">\n          <button type=\"button\" onclick=\"saveCustomCookiePrefs()\" class=\"px-4 py-2 rounded-xl text-xs bg-white/10 hover:bg-white/15 text-white font-semibold\">\n            Seçimi Kaydet\n          </button>\n          <button type=\"button\" onclick=\"acceptCookies('all')\" class=\"accent-btn px-4 py-2 rounded-xl text-xs\">\n            Tümünü Kabul Et\n          </button>\n        </div>\n      </div>\n    </div>\n  </div>", "cookieConsentBanner": "<div id=\"cookieConsentBanner\" class=\"hidden fixed bottom-0 inset-x-0 z-[60] p-3 sm:p-4 pointer-events-none\">\n    <div class=\"max-w-5xl mx-auto max-h-[22vh] overflow-y-auto bg-[#18202d]/95 backdrop-blur-md border border-[#88c0a8]/35 rounded-2xl p-3 sm:p-4 shadow-2xl pointer-events-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-4\">\n      <div class=\"flex items-start gap-3.5\">\n        <div class=\"w-10 h-10 rounded-xl bg-[#5e9c88]/20 border border-[#88c0a8]/30 flex items-center justify-center text-lg shrink-0\">🍪</div>\n        <div class=\"space-y-1 text-xs text-gray-300 leading-relaxed\">\n          <div class=\"font-bold text-white text-sm\">Çerez (Cookie) ve KVKK Gizlilik Bildirimi</div>\n          <p>\n            <strong>OyunÇöz</strong> üzerinde oturum güvenliğinizi sağlamak, donanım tercihlerinizi hatırlamak ve oyun hata çözümlerini hızlandırmak için 6698 sayılı KVKK ile uyumlu çerezler kullanıyoruz. Detaylar için\n            <button type=\"button\" onclick=\"window.open('./gizlilik-ve-cerez-politikasi.html', '_blank')\" class=\"text-[#88c0a8] underline font-semibold hover:text-white\">Çerez Politikası</button> ve\n            <button type=\"button\" onclick=\"window.open('./kvkk-aydinlatma-metni.html', '_blank')\" class=\"text-[#88c0a8] underline font-semibold hover:text-white\">KVKK Aydınlatma Metni</button>'ni inceleyebilirsiniz.\n          </p>\n        </div>\n      </div>\n      <div class=\"flex flex-wrap items-center gap-2 shrink-0 w-full md:w-auto justify-end\">\n        <button type=\"button\" onclick=\"openCookieSettingsModal()\" class=\"px-3 py-2 rounded-xl text-xs font-semibold bg-white/5 hover:bg-white/10 text-gray-300 border border-white/10 transition\">\n          ⚙️ Ayarlar\n        </button>\n        <button type=\"button\" onclick=\"acceptCookies('essential')\" class=\"px-3.5 py-2 rounded-xl text-xs font-semibold bg-white/10 hover:bg-white/15 text-gray-200 border border-white/10 transition\">\n          Sadece Zorunlu\n        </button>\n        <button type=\"button\" onclick=\"acceptCookies('all')\" class=\"accent-btn px-4 py-2 rounded-xl text-xs font-bold shadow\">\n          ✓ Tümünü Kabul Et\n        </button>\n      </div>\n    </div>\n  </div>"};

function ensureLazyModalMounted(modalId) {
  if (document.getElementById(modalId)) return document.getElementById(modalId);
  const tpl = LAZY_MODAL_TEMPLATES[modalId];
  if (!tpl) return null;
  let root = document.getElementById('lazyModalsRoot');
  if (!root) {
    root = document.createElement('div');
    root.id = 'lazyModalsRoot';
    document.body.appendChild(root);
  }
  const wrapper = document.createElement('div');
  wrapper.innerHTML = tpl;
  const el = wrapper.firstElementChild;
  if (el) {
    root.appendChild(el);
  }
  if (modalId === 'profileModal' || modalId === 'askQuestionModal') {
    populateGameSelects();
  }
  if (modalId === 'authModal' || modalId === 'profileModal' || modalId === 'askQuestionModal') {
    loadSavedHardwareSpecs();
  }
  return document.getElementById(modalId);
}


// --- AŞAMA 3: HATA KODU SAYFALARI DOĞRUDAN YÖNLENDİRME, ENTER ARAMA SONUÇLARI VE GERÇEK OYUN SAYILARI ---
const DEDICATED_ERROR_PAGES = [{"slug": "gta-6/err-gfx-state-cokme-hatasi", "oyun": "GTA 6", "oyun_hub_url": "/gta-6-hata-cozumleri.html", "hata_kodu": "ERR_GFX_STATE / DX12 Crash", "issue_id": 12, "oncelik": 1, "tek_cumle_ozet": "GTA 6'da RAGE 9 motoru DirectX 12 gölgelendirici önbelleği, VRAM taşması ve Rockstar Launcher kaynaklı açılmama/çökme çözümü.", "varyant_yazimlari": ["gta 6 açılmıyor", "gta 6 err_gfx_state", "gta 6 çökme hatası", "gta 6 kasma ve fps düşmesi", "gta 6 dx12 hatası", "gta 6 sistem gereksinimleri vram hatası"], "title": "GTA 6 Açılmıyor ve ERR_GFX_STATE Çökme Hatası Çözümü", "meta_description": "GTA 6 açılmıyor, ERR_GFX_STATE DirectX 12 çökmesi, Rockstar Launcher SDK hatası ve Vice City FPS düşmesi sorunları için adım adım teknik çözüm rehberi.", "h1": "GTA 6 Açılmıyor, ERR_GFX_STATE ve FPS Düşmesi Nasıl Çözülür?", "kisa_aciklama": "Grand Theft Auto VI (GTA 6) oynarken karşılaşılan ERR_GFX_STATE, açılış ekranında kapanma (gta 6 açılmıyor) ve ani FPS düşmesi sorunları; RAGE 9 oyun motorunun DirectX 12 Ultimate gölgelendirici önbelleği (Shader Cache) bozulmasından, 8 GB / 12 GB VRAM sınırının aşılmasından veya Rockstar Games Launcher SDK servisinin yanıt vermemesinden kaynaklanır.", "hizli_cozum": {"baslik": "En Olası İlk Adım: RAGE Gölgelendirici Önbelleğini Sıfırlayıp VRAM Hedefini Dengeleyin", "aciklama": "Belgeler\Rockstar Games\GTA VI\Settings klasöründeki geçici pipeline önbellek dosyalarını temizleyin, Windows Grafik Ayarlarında Donanım Hızlandırmalı GPU Zamanlamasını (HAGS) kontrol edin ve Rockstar Games Launcher'ı Yönetici olarak başlatın.", "komut": "cleanmgr /d C"}, "senaryolar": [{"id": "vram-8-12gb", "etiket": "8 GB / 12 GB Ekran Kartı (VRAM Hatası)", "baslik": "8 GB ve 12 GB VRAM Ekran Kartlarında Çökme ve Doku Kaybı Önleme", "aciklama": "RAGE 9 motorunda Işın İzleme (Ray Traced Global Illumination) ve Yüksek Çözünürlüklü Dokular aynı anda açıldığında 8-10 GB VRAM sınırını aşar. Doku Kalitesini 'Yüksek', Ray Tracing Yansımaları 'Kapalı/Orta' seviyesine alıp DLSS / FSR Kalite modunu etkinleştirin ve Windows Sanal Belleğini 16384 MB yapın."}, {"id": "rockstar-launcher", "etiket": "Oyun Hiç Açılmıyor (Rockstar Launcher)", "baslik": "Rockstar Games Launcher 'Quitting Unexpectedly' ve SDK Döngüsü", "aciklama": "Oyun 'Başlatılıyor' yazıp kapanıyorsa Belgeler\Rockstar Games\Launcher klasöründeki geçici oturum önbelleğini temizleyin, OneDrive'ın Belgeler klasörünü kilitlemesini durdurun ve hem Steam/Epic hem de Rockstar Launcher'ı Yönetici olarak çalıştırın."}, {"id": "dx12-stutter", "etiket": "Anlık Takılma & FPS Düşmesi (Stutter)", "baslik": "Vice City Şehir İçi Gezinme Takılması (Traversal & Shader Stutter)", "aciklama": "Sürücü güncellemesi sonrası ilk girişte gölgelendirici derlemesinin (%100) ana menüde tamamlanmasını bekleyin, NVIDIA Denetim Masası'ndan Gölgelendirici Önbellek Boyutunu 10 GB yapın ve DirectStorage için oyunun NVMe SSD üzerinde kurulu olduğundan emin olun."}], "nedenler": ["Belgeler\Rockstar Games\GTA VI\Settings klasöründeki derlenmiş DirectX 12 / Vulkan boru hattı (pipeline) önbellek dosyalarının ekran kartı sürücü güncellemesi sonrası bozulması.", "8 GB veya 12 GB VRAM'e sahip ekran kartlarında Işın İzleme (Ray Tracing) ve kalabalık yoğunluğu ayarlarının video belleğini taşırması.", "Rockstar Games Launcher Service veya Social Club SDK bileşeninin arka planda yetki kaybetmesi ya da Windows Defender Kontrollü Klasör Erişimi tarafından Belgeler klasörünün engellenmesi.", "Oyunun NVMe SSD yerine SATA disk üzerinde çalıştırılması nedeniyle DirectStorage doku akışının zaman aşımına uğraması."], "cozum_adimlari": [{"baslik": "Settings Klasöründeki Bozuk RAGE Grafik Önbelleğini ve DirectX Shader Cache'i Temizleyin", "aciklama": "ERR_GFX_STATE veya yükleme ekranında çökme yaşıyorsanız Belgeler\Rockstar Games\GTA VI\Settings klasöründeki geçici sga_ / pipeline önbellek dosyalarını silin (hikaye kayıtlarınıza dokunmayın) ve Windows Disk Temizleme aracıyla DirectX Gölgelendirici Önbelleğini sıfırlayın.", "komut": "cleanmgr /d C", "komut_notu": {"ne_yapar": "Windows Disk Temizleme aracını açarak bozulmuş DirectX 12 gölgelendirici önbellek dosyalarını güvenli şekilde temizlemenizi sağlar.", "risk": "Yalnızca geçici grafik önbelleğini siler; oyun kayıt (save) dosyalarınıza zarar vermez.", "geri_alma": "Oyun yeniden başlatıldığında güncel ekran kartı sürücünüze uygun temiz gölgelendirici önbelleğini otomatik oluşturur."}, "gorsel_yolu": "", "alt_metin": "Windows Disk Temizleme aracında DirectX Gölgelendirici Önbelleği ve RAGE Settings temizliği"}, {"baslik": "VRAM Taşmasını Önlemek İçin Sanal Belleği (Pagefile) 16384 MB - 24576 MB Yapın", "aciklama": "GTA 6 açık dünya akışında hem VRAM hem sistem RAM'ini yoğun kullanır. Win + R > SystemPropertiesPerformance.exe > Gelişmiş > Sanal Bellek (Değiştir) penceresinden hızlı NVMe SSD diskinizde Başlangıç: 16384 MB, En Büyük: 24576 MB sanal bellek tanımlayın.", "komut": "SystemPropertiesPerformance.exe", "komut_notu": {"ne_yapar": "Windows Performans Seçenekleri ve Sanal Bellek yapılandırma penceresini doğrudan açar.", "risk": "Salt ayar penceresi açma komutudur; sistem dosyalarını değiştirmez.", "geri_alma": "Sanal Bellek penceresinden istediğiniz zaman tekrar 'Tüm sürücülerde disk belleği dosyası boyutunu otomatik yönet' seçeneğini işaretleyebilirsiniz."}, "gorsel_yolu": "", "alt_metin": "Windows Performans Seçenekleri Sanal Bellek ekranında 16384 MB - 24576 MB yapılandırması"}, {"baslik": "Rockstar Games Launcher Servisini ve Sistem Dosya Bütünlüğünü Onarın", "aciklama": "Oyun hiç tepki vermiyor veya Rockstar Games Launcher hata kodu veriyorsa arka planda kilitli kalan Launcher süreçlerini kapatın, sistem kütüphanelerini doğrulayın ve başlatıcıyı Yönetici olarak çalıştırın.", "komut": "sfc /scannow", "komut_notu": {"ne_yapar": "Windows Sistem Dosyası Denetleyicisi ile bozuk DirectX 12, Visual C++ ve sistem DLL dosyalarını tarar ve onarır.", "risk": "Resmi Microsoft bakım komutudur; kişisel dosyaları veya oyun verilerini silmez.", "geri_alma": "Orijinal Windows sistem bileşenlerini onardığı için geri alma işlemi gerektirmez."}, "gorsel_yolu": "", "alt_metin": "Yönetici Komut İstemi üzerinde sfc scannow sistem doğrulaması ve Rockstar Launcher onarımı"}, {"baslik": "Oyun İçi Grafik, Işın İzleme (Ray Tracing) ve Kalabalık Yoğunluğu Ayarlarını Dengeleyin", "aciklama": "Şehir merkezinde ani FPS düşmesi yaşıyorsanız Grafik ayarlarından Nüfus/Trafik Yoğunluğu (Population Density) çubuğunu %70 seviyesine çekin, Gölgelendirici Kalitesini Yüksek yapın ve DLSS / FSR / XeSS Ölçekleme modunu 'Kalite (Quality)' konumuna getirin.", "komut": "", "gorsel_yolu": "", "alt_metin": "GTA 6 Grafik ayarlarında VRAM kullanımı, Kalabalık Yoğunluğu ve DLSS/FSR Kalite modu seçimi"}], "isle_yaramazsa": "Ekran kartınızda MSI Afterburner hız aşırtma (Overclock) profili açıksa varsayılan değerlere döndürün, Discord ve GeForce Experience oyun içi ekran katmanlarını (Overlay) kapatın ve DDU ile en güncel WHQL Game Ready / Adrenalin sürücüsünü temiz kurulumla yükleyin.", "resmi_kaynak_url": "", "resmi_kaynak_baslik": "Rockstar Games Resmi Destek Merkezi", "sss": [{"soru": "GTA 6 ERR_GFX_STATE hatası neden olur?", "cevap": "RAGE oyun motorunun DirectX 12 gölgelendirici boru hattı (pipeline) önbelleğinin bozulması, ekran kartı VRAM sınırının aşılması veya kararsız GPU hız aşırtma (overclock) ayarları nedeniyle grafik sürücüsünün yanıt vermeyi kesmesinden kaynaklanır."}, {"soru": "GTA 6 açılmıyor, Rockstar Games Launcher 'Çıkılıyor' deyip kapanıyor; nasıl düzelir?", "cevap": "Windows Güvenliği > Virüs ve tehdit koruması > Fidye yazılımına karşı koruma altındaki 'Denetimli klasör erişimi' özelliğinin Belgeler\Rockstar Games klasörünü engellemediğinden emin olun ve Rockstar Games Launcher'ı Yönetici olarak başlatıp oyun dosyalarını doğrulayın."}, {"soru": "8 GB VRAM ekran kartında GTA 6 kasma ve doku yüklenmeme sorunu nasıl önlenir?", "cevap": "8 GB VRAM'li kartlarda Işın İzleme (Ray Tracing) kapatılmalı, Doku Kalitesi Orta/Yüksek seviyesinde tutulmalı, DLSS/FSR Kalite modu açılmalı ve SSD üzerinde en az 16 GB Windows Sanal Belleği (Pagefile) tanımlanmalıdır."}], "ilgili_hatalar": [{"url": "/gta-6-hata-cozumleri.html", "oyun": "GTA 6", "hata_kodu": "TÜM HATALAR", "baslik": "GTA 6 Hata Kodları, Açılmama ve FPS Çözüm Merkezi"}, {"url": "/gta-v/err-gfx-d3d-init", "oyun": "GTA V", "hata_kodu": "ERR_GFX_D3D_INIT", "baslik": "GTA 5 ERR_GFX_D3D_INIT Hatası Çözümü (DirectX 11)"}, {"url": "/fivem/harita-yuklenmiyor-texture-loss", "oyun": "FiveM", "hata_kodu": "TEXTURE LOSS", "baslik": "FiveM Harita Yüklenmiyor (Texture Loss) Çözüm Rehberi"}, {"url": "/rdr2/err-gfx-state", "oyun": "Red Dead Redemption 2", "hata_kodu": "ERR_GFX_STATE", "baslik": "RDR2 ERR_GFX_STATE Hatası Çözümü (sga_ Vulkan Temizliği)"}], "video_embed_url": "", "yazar": "OyunÇöz Teknik Ekibi", "tarih_yayin": "2026-11-18", "tarih_guncelleme": "2026-11-18", "test_edilen_surum": "Windows 11 (23H2 & 24H2) • DirectX 12 Ultimate", "editor_verified": true}, {"slug": "lol/van-185", "oyun": "League of Legends", "oyun_hub_url": "/lol-hata-cozumleri.html", "hata_kodu": "VAN 185", "issue_id": 10, "varyant_yazimlari": ["VAN 185", "Vanguard 185", "van 185 lol", "LoL Vanguard hatası 185", "League of Legends VAN 185"], "title": "LoL Vanguard VAN 185 Hatası Çözümü (Adım Adım)", "meta_description": "League of Legends oynarken karşılaşılan LoL Vanguard VAN 185 bağlantı hatası için oturum yenileme, vgc servisi ve ağ sıfırlama adımlarını içeren çözüm rehberi.", "h1": "League of Legends VAN 185 Hatası Nasıl Çözülür?", "kisa_aciklama": "League of Legends VAN 185 hatası, oyun açıkken Riot İstemcisi ile Vanguard arka plan doğrulama servisi arasındaki kalp atışı (heartbeat) sinyalinin kesildiğini ve oturumun güvenlik nedeniyle sonlandırıldığını gösterir. Oyuncuların van 185 lol aramalarında sıkça karşılaştığı bu durum, genellikle açık kalan istemci oturumlarından veya yerel ağ kesintilerinden kaynaklanan bir LoL Vanguard hatası 185 uyarısıdır.", "nedenler": ["Arka planda asılı kalan çoklu RiotClientServices.exe süreçlerinin Vanguard 185 oturum jetonunu (token) kilitlemesi.", "Windows Güç Seçenekleri veya ağ bağdaştırıcısı güç tasarrufu modunun kısa süreli paket ve DNS/IPv6 oturum kopmasına yol açması.", "Riot Client yerel önbellek (Data/Logs) dosyalarının veya vgc/vgk servis durumunun bozulması."], "cozum_adimlari": [{"baslik": "Asılı Kalan Tüm Riot ve Vanguard Süreçlerini Sonlandırın", "aciklama": "Riot İstemcisi'nin arka planda açık kalmasından kaynaklanan VAN 185 oturum çakışmasını gidermek için Oturumu Kapat seçeneğiyle çıkış yapın ve Görev Yöneticisi'nden LeagueClient.exe, RiotClientServices.exe ile vgtray.exe süreçlerini tamamen kapatın.", "komut": "taskkill /F /IM RiotClientServices.exe /IM LeagueClient.exe", "komut_notu": {"ne_yapar": "Arka planda asılı kalan Riot İstemcisi ve League of Legends süreçlerini zorla sonlandırır.", "risk": "Açık olan oyun lobisi veya istemci penceresi kapanır; sistem dosyalarına zarar vermez.", "geri_alma": "Riot İstemcisi'ni masaüstü kısayolundan Yönetici olarak yeniden başlatmanız yeterlidir."}, "gorsel_yolu": "", "alt_metin": "Görev Yöneticisi üzerinden RiotClientServices.exe ve LeagueClient.exe süreçlerinin sonlandırılması"}, {"baslik": "Riot Client Yerel Oturum Önbelleğini Temizleyin", "aciklama": "Win + R tuşlarına basıp %localappdata%\Riot Games\Riot Client\Data klasörünü açın. İçindeki geçici oturum dosyalarını temizledikten sonra Riot İstemcisi'ni Yönetici olarak başlatıp hesabınıza yeniden giriş yapın.", "komut": "", "gorsel_yolu": "", "alt_metin": "Riot Client Data klasöründeki geçici oturum önbellek dosyalarının temizlenmesi"}, {"baslik": "VAN 185 Oturum Kopması İçin Winsock ve DNS Sıfırlama Uygulayın", "aciklama": "Yerel ağ soketlerindeki tıkanıklığı ve DNS önbelleğindeki kopmaları gidermek için Komut İstemi'ni (CMD) Yönetici olarak açıp aşağıdaki ağ sıfırlama komutlarını çalıştırın ve bilgisayarı yeniden başlatın.", "komut": "netsh winsock reset && netsh int ip reset && ipconfig /flushdns", "komut_notu": {"ne_yapar": "Windows TCP/IP ağ yığınını, Winsock soket katalog ayarlarını fabrika varsayılanlarına sıfırlar ve DNS önbelleğini temizler.", "risk": "Ağ bağdaştırıcınızda elle (statik) girilmiş IP veya DNS yapılandırması varsa otomatik (DHCP) moda dönebilir.", "geri_alma": "Yeniden başlatma sonrasında özel DNS veya statik IP kullanıyorsanız Ağ Bağdaştırıcısı Özellikleri (IPv4) üzerinden tekrar tanımlayın."}, "gorsel_yolu": "", "alt_metin": "Yönetici Komut İstemi üzerinde netsh winsock reset ve ipconfig flushdns komutlarının çalıştırılması"}, {"baslik": "Riot Vanguard Servislerini (vgc ve vgk) Komut Satırından Temiz Kurun", "aciklama": "Oturum yenileme ve ağ sıfırlamasına rağmen Vanguard 185 hatası devam ediyorsa, Komut İstemi'ni Yönetici olarak açıp vgc ve vgk servislerini kaldırın. Ardından bilgisayarı yeniden başlatarak Riot İstemcisi üzerinden Vanguard'ı temiz kurun.", "komut": "sc delete vgc && sc delete vgk", "komut_notu": {"ne_yapar": "Belirtilen Windows arka plan hizmet kaydını (bozuk vgc ve vgk anti-cheat servisini) hizmet tablosundan kaldırır.", "risk": "Yanlış hizmet adı yazılması sistem veya oyun istemcisi servislerinin yeniden kurulana kadar çalışmamasına yol açabilir.", "geri_alma": "Riot İstemcisi'ni Yönetici olarak çalıştırıp Güncelle / Onar seçeneğine tıklayarak Vanguard hizmetini temiz şekilde yeniden kurun."}, "gorsel_yolu": "", "alt_metin": "Yönetici Komut İstemi ile sc delete vgc ve sc delete vgk komutlarının uygulanması"}], "isle_yaramazsa": "Şampiyon seçimi sonrasında oyun ekranı gelmiyor ve 'Yeniden Bağlan (Reconnect)' döngüsüne giriyorsa C:\Riot Games\League of Legends\Config klasöründeki game.cfg ve PersistedSettings.json dosyalarını silip League of Legends.exe > Özellikler > Uyumluluk sekmesinden 'Tam ekran iyileştirmelerini devre dışı bırak' seçeneğini işaretleyin.", "resmi_kaynak_url": "", "resmi_kaynak_baslik": "Riot Games League of Legends Vanguard Resmi Destek Sayfası", "sss": [{"soru": "VAN 185 hatası neden olur?", "cevap": "VAN 185 hatası, League of Legends açıkken Riot İstemcisi ile Vanguard arka plan doğrulama servisi arasındaki kalp atışı (heartbeat) oturum sinyalinin zaman aşımına uğraması, arka planda asılı kalan RiotClientServices.exe süreçlerinin oturum jetonunu kilitlemesi veya kısa süreli DNS/ağ kopmaları nedeniyle oluşur."}, {"soru": "LoL'de Vanguard 185 hatası nasıl düzelir?", "cevap": "Riot İstemcisi'nden tamamen çıkış yapıp (Oturumu Kapat), Görev Yöneticisi'nden açık Riot süreçlerini sonlandırmak, %localappdata%\Riot Games\Riot Client\Data önbelleğini temizlemek ve Yönetici CMD üzerinden Winsock/DNS sıfırlaması yaparak bilgisayarı yeniden başlatmak sorunu giderir."}, {"soru": "VAN 185 hatası hesabımın banlandığı anlamına mı gelir?", "cevap": "Mevcut teknik kayıtlara göre VAN 185 bir hesap yasaklaması (ban) değil, Riot İstemcisi ile Vanguard servisi arasındaki yerel oturum ve bağlantı doğrulama kopmasıdır; oturumu kapatıp servisleri yenileyerek tekrar giriş yapılabilir."}], "ilgili_hatalar": [{"url": "/lol/van-128", "oyun": "League of Legends", "hata_kodu": "VAN 128", "baslik": "LoL Vanguard VAN 128 Hatası Çözüm Rehberi"}, {"url": "/lol-hata-cozumleri.html", "oyun": "League of Legends", "hata_kodu": "TÜM HATALAR", "baslik": "League of Legends Hata Kodları ve Çözüm Merkezi"}, {"url": "/valorant/van-9003", "oyun": "Valorant", "hata_kodu": "VAN 9003", "baslik": "Valorant VAN 9003 Secure Boot Çözüm Rehberi"}, {"url": "/valorant/van-1067", "oyun": "Valorant", "hata_kodu": "VAN 1067", "baslik": "Valorant VAN 1067 Bağlantı Hatası Çözüm Rehberi"}], "video_embed_url": "", "yazar": "OyunÇöz Teknik Ekibi", "tarih_yayin": "2026-03-01", "tarih_guncelleme": "2026-11-17", "test_edilen_surum": "Windows 10 / 11 (23H2 & 24H2) • Güncel LoL İstemcisi", "oncelik": 2, "tek_cumle_ozet": "LoL'de Riot İstemcisi ile Vanguard arasındaki oturum bağlantısı koptuğunda oluşan hata kodu.", "hizli_cozum": {"baslik": "En Olası İlk Adım: Açık Riot Süreçlerini Kapatıp Oturumu Yenileyin", "aciklama": "Riot İstemcisi'nden 'Oturumu Kapat' diyerek çıkın, Görev Yöneticisi'nden RiotClientServices.exe ile vgtray.exe süreçlerini sonlandırıp istemciyi Yönetici olarak yeniden başlatın.", "komut": "taskkill /F /IM RiotClientServices.exe /IM LeagueClient.exe"}}, {"slug": "valorant/van-9003", "oyun": "Valorant", "oyun_hub_url": "/valorant-hata-cozumleri.html", "hata_kodu": "VAN 9003", "issue_id": 1, "varyant_yazimlari": ["VAN 9003", "van9003", "valorant van 9003", "van 9003 valorant", "secure boot van 9003"], "title": "Valorant VAN 9003 Hatası Çözümü (Secure Boot & BIOS)", "meta_description": "Windows 11'de karşılaşılan Valorant VAN 9003 (van9003) Secure Boot ve UEFI BIOS hatası için ASUS, MSI, Gigabyte ve ASRock adım adım çözüm rehberi.", "h1": "Valorant VAN 9003 Hatası Nasıl Çözülür? (UEFI Secure Boot)", "kisa_aciklama": "Valorant VAN 9003 ('This build of Vanguard requires secure boot to be enabled in order to play'), Riot Vanguard çekirdek sürücüsünün (vgk.sys) Windows 11 önyükleme zincirinde UEFI Güvenli Önyükleme (Secure Boot) doğrulamasını aktif olarak bulamadığını gösteren hata kodudur. Oyuncuların valorant van 9003 veya bitişik yazımla van9003 olarak arattığı bu uyarı, anakart BIOS ayarlarında CSM kapatılıp Secure Boot anahtarları etkinleştirilerek çözülür.", "nedenler": ["Anakart BIOS ayarlarında CSM (Compatibility Support Module) özelliğinin açık (Enabled) bırakılması.", "BIOS içinde Secure Boot seçeneği 'Enabled' görünmesine rağmen Platform Key (PK) fabrika anahtarlarının yüklenmemiş olması nedeniyle durumun 'Not Active' kalması.", "Disk bölümleme tablosunun UEFI için gereken GPT yerine eski MBR (Legacy) formatında olması."], "cozum_adimlari": [{"baslik": "Mevcut Güvenli Önyükleme (Secure Boot) ve BIOS Modunu Doğrulayın", "aciklama": "Klavyeden Win + R tuşlarına basıp msinfo32 yazarak Sistem Bilgisi penceresini açın. 'BIOS Modu' satırının UEFI olduğundan ve 'Güvenli Önyükleme Durumu (Secure Boot State)' satırının Açık/Kapalı durumunu kontrol edin. Ayrıca tpm.msc komutuyla TPM 2.0 hazırlık durumunu doğrulayın.", "komut": "powershell -Command \"Confirm-SecureBootUEFI\"", "komut_notu": {"ne_yapar": "Windows PowerShell üzerinden anakartta UEFI Secure Boot özelliğinin aktif (True) olup olmadığını salt-okunur olarak sorgular.", "risk": "Salt-okunur bir doğrulama komutudur; sistem veya BIOS ayarlarında değişiklik yapmaz.", "geri_alma": "Herhangi bir sistem değişikliği yapmadığı için geri alma işlemi gerektirmez."}, "gorsel_yolu": "", "alt_metin": "Windows msinfo32 Sistem Bilgisi ekranında BIOS Modu UEFI ve Güvenli Önyükleme Durumu kontrolü"}, {"baslik": "Anakart BIOS Menüsünden CSM Kapatma ve Secure Boot Aktifleştirme", "aciklama": "Bilgisayarı yeniden başlatırken DEL veya F2 tuşuna basarak BIOS'a girin. Boot menüsünden CSM (Compatibility Support Module) ayarını Disabled yapın, OS Type / Secure Boot Mode ayarını Windows UEFI Mode veya Standard konumuna getirin ve Key Management altından varsayılan fabrika anahtarlarını (Install Default Secure Boot Keys / Restore Factory Keys) yükleyin.", "komut": "", "anakart_bolumleri": [{"marka": "ASUS", "adimlar": "BIOS > Boot > CSM (Compatibility Support Module) > Launch CSM: Disabled yapın. Ardından Boot > Secure Boot > OS Type: Windows UEFI Mode seçin ve Key Management > Install Default Secure Boot Keys seçeneğini onaylayıp F10 ile kaydedin.", "alt_metin": "ASUS UEFI BIOS Boot sekmesinde CSM kapatma ve Windows UEFI Mode seçimi"}, {"marka": "MSI", "adimlar": "BIOS > Settings > Advanced > Windows OS Configuration > BIOS UEFI/CSM Mode: UEFI seçin. Secure Boot menüsüne girip Secure BootMode: Custom > Enroll all Factory Default keys onaylayın ve tekrar Standard moda alıp F10 ile kaydedin.", "alt_metin": "MSI Click BIOS 5 ekranında UEFI modu ve Enroll all Factory Default keys adımı"}, {"marka": "Gigabyte", "adimlar": "BIOS > Boot > CSM Support: Disabled yapın. Açılan Secure Boot menüsünde Secure Boot: Enabled seçin. Durum 'Not Active' görünüyorsa Secure Boot Mode'u Custom yapıp 'Restore Factory Keys' seçin ve F10 ile kaydedin.", "alt_metin": "Gigabyte UEFI BIOS ekranında CSM Support Disabled ve Restore Factory Keys adımı"}, {"marka": "ASRock", "adimlar": "BIOS > Boot > CSM (Compatibility Support Module): Disabled yapın. Security > Secure Boot menüsüne geçip 'Install default Secure Boot keys' seçeneğine tıklayın ve Secure Boot: Enabled yaparak F10 ile kaydedin.", "alt_metin": "ASRock UEFI Setup Utility ekranında Secure Boot ve varsayılan anahtar yükleme adımı"}], "gorsel_yolu": "", "alt_metin": "BIOS Boot menüsünde CSM Disabled ve Secure Boot Key Management fabrika anahtarlarının yüklenmesi"}, {"baslik": "AMD fTPM ve Intel PTT (TPM 2.0) Modülünü Etkinleştirin", "aciklama": "AMD Ryzen işlemcili anakartlarda Advanced > AMD fTPM Configuration > AMD fTPM Switch ayarını Enabled yapın. Intel işlemcili anakartlarda Settings > Security > Trusted Computing > Intel Platform Trust Technology (PTT) ayarını Enabled konumuna getirin ve F10 ile kaydedip çıkın.", "komut": "", "gorsel_yolu": "", "alt_metin": "BIOS güvenlik ayarlarında AMD fTPM ve Intel PTT (TPM 2.0) özelliğinin etkinleştirilmesi"}, {"baslik": "Riot Vanguard (vgc) Hizmetini Otomatik Başlatın", "aciklama": "Windows açıldığında Hizmetler (services.msc) penceresinden 'vgc' hizmetini bulun, Başlangıç Türünü 'Otomatik' yapıp hizmeti başlatın. Komut İstemi'ni (CMD) Yönetici olarak açıp aşağıdaki komutu çalıştırarak servisin çalıştığını doğrulayın.", "komut": "sc config vgc start= auto && net start vgc", "komut_notu": {"ne_yapar": "Riot Vanguard kullanıcı modu hizmetini (vgc) Otomatik başlangıç türüne alır ve servisi başlatır.", "risk": "Standart Windows hizmet yapılandırma komutudur; sistem dosyalarını silmez.", "geri_alma": "Hizmetler (services.msc) penceresinden vgc hizmetini tekrar Elle (Manual) durumuna getirebilirsiniz."}, "gorsel_yolu": "", "alt_metin": "Windows Hizmetler (services.msc) ekranında vgc servisinin Otomatik başlatılması"}], "isle_yaramazsa": "msinfo32 ekranında BIOS Modu 'Eski (Legacy)' görünüyorsa diskiniz MBR formatındadır; CSM kapatmadan önce diskin GPT formatında olması gerekir. Ayrıca Windows Güvenliği > Cihaz Güvenliği > Çekirdek Yalıtımı altındaki Bellek Bütünlüğü ayarını kontrol edin.", "resmi_kaynak_url": "", "resmi_kaynak_baslik": "Riot Games Valorant VAN 9003 ve Secure Boot Resmi Destek Sayfası", "sss": [{"soru": "BIOS'ta Secure Boot Enabled görünmesine rağmen Valorant neden hala VAN 9003 (van9003) veriyor?", "cevap": "ASUS, MSI, Gigabyte ve ASRock anakartlarda Secure Boot seçeneği Enabled olsa bile Platform Key (PK) anahtarları yüklenmemişse Secure Boot durumu 'Not Active' kalır. BIOS > Secure Boot > Key Management menüsünden 'Install Default Secure Boot Keys' (veya Restore Factory Keys) işlemini uyguladığınızda Secure Boot aktif hale gelir."}, {"soru": "valorant van 9003 hatası Windows 11'de neden ortaya çıkar?", "cevap": "Windows 11 23H2 ve 24H2 sürümlerinde Riot Vanguard çekirdek sürücüsü (vgk.sys), önyükleme zincirinin güvenliğini doğrulamak için UEFI Secure Boot ve TPM 2.0 modüllerinin donanımsal olarak 'Aktif (Active)' durumda çalışmasını zorunlu tutar."}, {"soru": "BIOS ayarlarını değiştirmeden önce hangi önlemi almalıyım?", "cevap": "İşlemlere başlamadan önce msinfo32 üzerinden BIOS Modunun UEFI olduğundan emin olun ve PowerShell'de Checkpoint-Computer -Description \"OyunCoz_Yedek\" komutuyla bir Sistem Geri Yükleme Noktası oluşturun."}], "ilgili_hatalar": [{"url": "/valorant/van-1067", "oyun": "Valorant", "hata_kodu": "VAN 1067", "baslik": "Valorant VAN 1067 Bağlantı ve TPM 2.0 Hatası Çözümü"}, {"url": "/valorant/val-62", "oyun": "Valorant", "hata_kodu": "VAL 62", "baslik": "Valorant VAL 62 ve Paket Kaybı Çözüm Rehberi"}, {"url": "/valorant-hata-cozumleri.html", "oyun": "Valorant", "hata_kodu": "TÜM HATALAR", "baslik": "Valorant Hata Kodları ve Çözüm Merkezi"}, {"url": "/lol/van-185", "oyun": "League of Legends", "hata_kodu": "VAN 185", "baslik": "LoL Vanguard VAN 185 Hatası Çözümü (Adım Adım)"}], "video_embed_url": "", "yazar": "OyunÇöz Teknik Ekibi", "tarih_yayin": "2026-03-01", "tarih_guncelleme": "2026-11-17", "test_edilen_surum": "Windows 10 / 11 (23H2 & 24H2) • Güncel Valorant İstemcisi", "oncelik": 3, "tek_cumle_ozet": "Windows 11'de BIOS UEFI Secure Boot özelliği aktif olmadığında çıkan Vanguard uyumluluk hatası.", "hizli_cozum": {"baslik": "En Olası İlk Adım: BIOS'ta CSM Kapatıp Secure Boot Anahtarlarını Yükleyin", "aciklama": "BIOS > Boot menüsünden CSM (Compatibility Support Module) ayarını Disabled yapın ve Secure Boot > Key Management altından 'Install Default Secure Boot Keys / Restore Factory Keys' seçeneğini onaylayın.", "komut": "powershell -Command \"Confirm-SecureBootUEFI\""}, "senaryolar": [{"id": "asus-msi", "etiket": "ASUS / MSI Anakart", "baslik": "ASUS ve MSI BIOS Üzerinden Secure Boot Aktifleştirme", "aciklama": "ASUS anakartlarda BIOS > Boot > CSM > Launch CSM: Disabled yapın; ardından Secure Boot > OS Type: Windows UEFI Mode seçip Key Management > Install Default Secure Boot Keys onaylayın. MSI anakartlarda Settings > Advanced > Windows OS Configuration > BIOS UEFI/CSM Mode: UEFI seçip Secure Boot > Enroll all Factory Default keys adımını uygulayın."}, {"id": "gigabyte-asrock", "etiket": "Gigabyte / ASRock Anakart", "baslik": "Gigabyte ve ASRock BIOS Üzerinden Secure Boot Aktifleştirme", "aciklama": "Gigabyte anakartlarda BIOS > Boot > CSM Support: Disabled yapın; Secure Boot menüsünde durum 'Not Active' ise Secure Boot Mode'u Custom yapıp 'Restore Factory Keys' seçin. ASRock anakartlarda Boot > CSM: Disabled yapıp Security > Secure Boot > Install default Secure Boot keys seçeneğine tıklayın."}]}, {"slug": "lol/van-128", "oyun": "League of Legends", "oyun_hub_url": "/lol-hata-cozumleri.html", "hata_kodu": "VAN 128", "issue_id": 9, "varyant_yazimlari": ["VAN 128", "Vanguard 128", "van 128 lol", "van128", "LoL Vanguard VAN 128"], "title": "LoL Vanguard VAN 128 Hatası Çözümü (Adım Adım)", "meta_description": "League of Legends VAN 128 Vanguard başlatılamadı hatası için test imzalama modunu kapatma, vgc/vgk temiz kurulumu ve antivirüs istisnası çözüm rehberi.", "h1": "League of Legends VAN 128 Hatası Nasıl Çözülür?", "kisa_aciklama": "League of Legends VAN 128 hatası, Riot Vanguard çekirdek sürücüsünün (vgk.sys) işletim sistemi açılışında güvenli modda başlatılamadığını veya üçüncü parti bir sürücüyle çakıştığını belirten hata kodudur. Oyuncuların van 128 lol ve van128 aramalarında karşılaştığı bu sorun, Windows sınama modu ayarları ve Vanguard servis onarımı ile adım adım giderilebilir.", "nedenler": ["Windows önyükleme ayarlarında test imzalama modu (testsigning) veya bütünlük kontrolü devre dışı (nointegritychecks) bayrağının açık olması.", "Üçüncü parti antivirüs yazılımlarının (Kaspersky, Avast, AVG, Malwarebytes) çekirdek kancalarının vgk.sys sürücüsüyle çakışması.", "Vanguard vgc ve vgk servis kayıtlarının güncelleme sırasında bozulması."], "cozum_adimlari": [{"baslik": "Windows Test İmzalama Modunu ve Bütünlük Bayraklarını Kapatın", "aciklama": "Vanguard 128 hatasını gidermek için Komut İstemi'ni (CMD) Yönetici olarak açın. Windows sınama modunu kapatan ve çekirdek bütünlük doğrulamasını varsayılan haline getiren aşağıdaki komutları çalıştırın.", "komut": "bcdedit /set testsigning off && bcdedit /deletevalue nointegritychecks", "komut_notu": {"ne_yapar": "Windows Önyükleme Yapılandırma Verilerini (BCD) güncelleyerek çekirdek bütünlük doğrulamasını ve sınama modunu varsayılan standart haline getirir.", "risk": "Yanlış parametre kullanımı Windows açılış davranışını veya imzasız sürücü kontrolünü etkileyebilir.", "geri_alma": "İşlem öncesi oluşturduğunuz Sistem Geri Yükleme Noktasına (rstrui.exe) dönebilir veya standart Windows önyükleme ayarlarını koruyabilirsiniz."}, "gorsel_yolu": "", "alt_metin": "Yönetici Komut İstemi üzerinde bcdedit testsigning off komutunun çalıştırılması"}, {"baslik": "Riot Vanguard Servislerini (vgc ve vgk) Komut Satırından Temizleyin", "aciklama": "Komut İstemi'ni (CMD) Yönetici olarak açın ve sırasıyla sc delete vgc ile sc delete vgk komutlarını çalıştırın. Ardından C:\Program Files\Riot Vanguard klasörünü silip bilgisayarınızı yeniden başlatın ve Riot İstemcisi üzerinden Vanguard'ı temiz kurun.", "komut": "sc delete vgc && sc delete vgk", "komut_notu": {"ne_yapar": "Bozulmuş veya kilitlenmiş Riot Vanguard (vgc ve vgk) çekirdek hizmet kaydını Windows Hizmet Yöneticisi'nden kaldırır.", "risk": "Hizmet silindikten sonra Riot İstemcisi üzerinden onarım yapılana kadar oyun açılmaz.", "geri_alma": "Riot İstemcisi'ni Yönetici olarak açıp Onar / Güncelle seçeneğini çalıştırarak Vanguard hizmetini temiz şekilde yeniden kurun."}, "gorsel_yolu": "", "alt_metin": "Yönetici Komut İstemi ekranında sc delete vgc ve sc delete vgk servis temizleme adımı"}, {"baslik": "Bellek Bütünlüğü ve 3. Parti Antivirüs Çakışmasını Giderin", "aciklama": "Kaspersky, Avast, AVG veya Malwarebytes kullanıyorsanız C:\Program Files\Riot Vanguard ve C:\Riot Games klasörlerini istisnalara (dışlamalara) ekleyin. Windows Güvenliği > Cihaz Güvenliği > Çekirdek Yalıtımı menüsünden Bellek Bütünlüğü durumunu kontrol edin.", "komut": "", "gorsel_yolu": "", "alt_metin": "Windows Güvenliği Çekirdek Yalıtımı ve antivirüs dışlama klasörlerinin kontrol edilmesi"}, {"baslik": "vgc Hizmetinin Otomatik Başladığını Doğrulayın", "aciklama": "Win + R tuşlarına basıp services.msc yazarak Hizmetler ekranını açın. Listeden vgc hizmetini bulun, Başlangıç Türünü Otomatik yapın ve hizmeti başlatın.", "komut": "sc config vgc start= auto && net start vgc", "komut_notu": {"ne_yapar": "Riot Vanguard kullanıcı modu servisinin (vgc) başlangıç türünü Otomatik olarak ayarlar ve servisi başlatır.", "risk": "Standart servis başlatma komutu sistem ayarlarına zarar vermez.", "geri_alma": "services.msc üzerinden vgc hizmetinin başlangıç türünü tekrar Elle (Manual) konumuna alabilirsiniz."}, "gorsel_yolu": "", "alt_metin": "Windows Hizmetler (services.msc) penceresinde vgc servisinin Otomatik olarak ayarlanması"}], "isle_yaramazsa": "Şampiyon seçimi sonrasında siyah ekran veya 'Yeniden Bağlan (Reconnect)' döngüsü devam ediyorsa C:\Riot Games\League of Legends\Config klasöründeki game.cfg ve PersistedSettings.json dosyalarını silin; League of Legends.exe > Özellikler > Uyumluluk sekmesinden 'Tam ekran iyileştirmelerini devre dışı bırak' kutusunu işaretleyin ve uyumluluk modu seçiliyse kaldırın.", "resmi_kaynak_url": "", "resmi_kaynak_baslik": "Riot Games League of Legends Vanguard Resmi Destek Sayfası", "sss": [{"soru": "LoL VAN 128 hatası neden olur?", "cevap": "VAN 128, Vanguard'ın çekirdek sürücüsünün (vgk.sys) Windows başlangıcında güvenilir modda yüklenemediğini gösterir. Genellikle Windows test imzalama modunun açık olması, üçüncü parti antivirüslerin çekirdek kancaları veya bozuk Vanguard servis kayıtları nedeniyle oluşur."}, {"soru": "League of Legends VAN 128 hatası donanımsal bir arızadan mı kaynaklanır?", "cevap": "Çoğu durumda donanımsal arıza değildir; işletim sistemi önyükleme bayrakları (testsigning), antivirüs çakışmaları veya vgc/vgk servis izinlerinden kaynaklanır ve yazılımsal adımlarla giderilebilir."}, {"soru": "Çözüm adımlarını uygulamadan önce hangi yedeği almalıyım?", "cevap": "PowerShell'i Yönetici olarak açıp Checkpoint-Computer -Description \"OyunCoz_Yedek\" komutuyla veya rstrui.exe arayüzüyle bir Sistem Geri Yükleme Noktası oluşturmanız önerilir."}], "ilgili_hatalar": [{"url": "/lol/van-185", "oyun": "League of Legends", "hata_kodu": "VAN 185", "baslik": "LoL Vanguard VAN 185 Hatası Çözümü (Adım Adım)"}, {"url": "/lol-hata-cozumleri.html", "oyun": "League of Legends", "hata_kodu": "TÜM HATALAR", "baslik": "League of Legends Hata Kodları ve Çözüm Merkezi"}, {"url": "/valorant/van-9003", "oyun": "Valorant", "hata_kodu": "VAN 9003", "baslik": "Valorant VAN 9003 Secure Boot Çözüm Rehberi"}, {"url": "/valorant/van-1067", "oyun": "Valorant", "hata_kodu": "VAN 1067", "baslik": "Valorant VAN 1067 Bağlantı Hatası Çözüm Rehberi"}], "video_embed_url": "", "yazar": "OyunÇöz Teknik Ekibi", "tarih_yayin": "2026-03-01", "tarih_guncelleme": "2026-11-17", "test_edilen_surum": "Windows 10 / 11 (23H2 & 24H2) • Güncel LoL İstemcisi", "oncelik": 4, "tek_cumle_ozet": "Windows sınama modu veya antivirüs çakışması nedeniyle Vanguard çekirdek sürücüsünün başlamama hatası.", "hizli_cozum": {"baslik": "En Olası İlk Adım: Windows Sınama Modunu Kapatıp Bilgisayarı Yeniden Başlatın", "aciklama": "Yönetici Komut İstemi'nde (CMD) sınama modunu ve bütünlük kontrolü devre dışı bayrağını kapatıp sistemi yeniden başlatın.", "komut": "bcdedit /set testsigning off && bcdedit /deletevalue nointegritychecks"}}, {"slug": "gta-v/err-gfx-d3d-init", "oyun": "GTA V", "oyun_hub_url": "/gtav-fivem-hata-cozumleri.html", "hata_kodu": "ERR_GFX_D3D_INIT", "issue_id": 12, "varyant_yazimlari": ["err_gfx_d3d_init gta 5", "ERR_GFX_D3D_INIT", "gta 5 err_gfx_d3d_init hatası", "gta v err gfx d3d init"], "title": "GTA 5 ERR_GFX_D3D_INIT Hatası Çözümü (DirectX 11)", "meta_description": "GTA 5 oynarken karşılaşılan err_gfx_d3d_init gta 5 DirectX 11 çökme hatası için settings.xml DX_Version ayarı, DLL temizliği ve sürücü çözüm rehberi.", "h1": "GTA 5 ERR_GFX_D3D_INIT Hatası Nasıl Çözülür?", "kisa_aciklama": "GTA V'te karşılaşılan ERR_GFX_D3D_INIT hatası, RAGE oyun motorunun DirectX görüntü bağdaştırıcısını başlatamadığını veya oyun sırasında ekran kartı sürücüsünün yanıt vermeyi kestiğini gösterir. Oyuncuların err_gfx_d3d_init gta 5 aramalarında en sık karşılaştığı bu durum, settings.xml yapılandırması ve bozuk grafik kütüphanelerinin temizlenmesiyle adım adım giderilir.", "nedenler": ["Belgeler\Rockstar Games\GTA V\settings.xml içindeki DX_Version değerinin uyumsuz kalması.", "Oyun klasöründe kalan d3d11.dll veya dxgi.dll gibi bozuk ReShade / ENB grafik modu kalıntıları.", "Arka planda çalışan ekran kaydı katmanları veya agresif ekran kartı hız aşırtma (Overclock) profilleri."], "cozum_adimlari": [{"baslik": "settings.xml Dosyasında DX_Version Değerini 2 (DirectX 11) Yapın", "aciklama": "Belgeler > Rockstar Games > GTA V klasöründeki settings.xml dosyasını Not Defteri ile açın. <DX_Version value=\"2\" /> satırının 2 olduğundan emin olup dosyayı kaydedin.", "komut": "powershell -Command \"Test-Path $env:USERPROFILE\Documents\Rockstar*\GTA*\settings.xml\"", "komut_notu": {"ne_yapar": "Belgeler klasöründeki GTA V settings.xml yapılandırma dosyasının mevcut olup olmadığını salt-okunur kontrol eder.", "risk": "Salt-okunur doğrulama komutudur; oyun kayıtlarına veya ayarlarına dokunmaz.", "geri_alma": "Herhangi bir değişiklik yapmadığı için geri alma gerektirmez."}, "gorsel_yolu": "", "alt_metin": "Belgeler Rockstar Games GTA V klasöründeki settings.xml dosyasında DX_Version value 2 ayarı"}, {"baslik": "Oyun Dizinindeki Bozuk d3d11.dll ve dxgi.dll Kalıntılarını Temizleyin", "aciklama": "GTA V kurulum klasöründe veya Belgeler\Rockstar Games\GTA V dizininde daha önce kurulmuş ReShade/ENB modlarından kalan d3d11.dll ya da dxgi.dll dosyaları varsa bunları silin.", "komut": "", "gorsel_yolu": "", "alt_metin": "GTA V ana dizinindeki uyumsuz d3d11.dll ve dxgi.dll grafik modu dosyalarının kontrolü"}, {"baslik": "Ekran Kartı Sürücüsünü ve Hız Aşırtma (Overclock) Profilini Kontrol Edin", "aciklama": "Ekran kartı sürücünüzü güncel WHQL sürüme yükseltin, MSI Afterburner üzerinde hız aşırtma (Overclock) profili açıksa varsayılan saat hızlarına çekin ve Windows sistem dosyalarını doğrulayın.", "komut": "sfc /scannow", "komut_notu": {"ne_yapar": "Windows Sistem Dosyası Denetleyicisi'ni çalıştırarak bozuk DirectX ve sistem DLL kütüphanelerini onarır.", "risk": "Standart Microsoft sistem bakım komutudur; kişisel verileri silmez.", "geri_alma": "Orijinal Windows sistem dosyalarını doğruladığı için geri alma gerektirmez."}, "gorsel_yolu": "", "alt_metin": "Ekran kartı hız aşırtma profilinin sıfırlanması ve sfc scannow sistem doğrulaması"}], "isle_yaramazsa": "Sorun devam ederse GTA V oyun dosyalarının bütünlüğünü Steam, Epic Games veya Rockstar Games Launcher üzerinden doğrulayın ve oyun içi grafik ayarlarından MSAA / Post FX değerlerini düşürerek test edin.", "resmi_kaynak_url": "", "resmi_kaynak_baslik": "Rockstar Games GTA V ERR_GFX_D3D_INIT Resmi Destek Sayfası", "sss": [{"soru": "GTA V ERR_GFX_D3D_INIT hatası neden olur?", "cevap": "Ekran kartı hız aşırtması (overclock), bozuk gölgelendirici önbelleği veya uyumsuz grafik modları (d3d11.dll / dxgi.dll) DirectX 11 cihazının sıfırlanmasına yol açar. GPU hız aşırtmasını varsayılana çekmek ve settings.xml'de DX_Version değerini 2 yapmak sorunu giderir."}, {"soru": "settings.xml dosyasını değiştirmek GTA 5 hikaye kaydımı (save) siler mi?", "cevap": "Hayır, settings.xml yalnızca ekran çözünürlüğü ve DirectX sürümü gibi grafik ayarlarını tutar; hikaye kayıt dosyalarınız Profiles klasöründe yer alır."}], "ilgili_hatalar": [{"url": "/fivem/harita-yuklenmiyor-texture-loss", "oyun": "FiveM", "hata_kodu": "TEXTURE LOSS", "baslik": "FiveM Harita Yüklenmiyor (Texture Loss) Çözüm Rehberi"}, {"url": "/gtav-fivem-hata-cozumleri.html", "oyun": "GTA V & FiveM", "hata_kodu": "TÜM HATALAR", "baslik": "GTA V ve FiveM Hata Kodları Çözüm Merkezi"}, {"url": "/rdr2/err-gfx-state", "oyun": "Red Dead Redemption 2", "hata_kodu": "ERR_GFX_STATE", "baslik": "RDR2 ERR_GFX_STATE Hatası Çözüm Rehberi"}], "video_embed_url": "", "yazar": "OyunÇöz Teknik Ekibi", "tarih_yayin": "2026-03-01", "tarih_guncelleme": "2026-11-17", "test_edilen_surum": "Windows 10 / 11 (23H2 & 24H2) • GTA V Güncel Sürüm", "oncelik": 5, "tek_cumle_ozet": "GTA 5'te DirectX 11 görüntü bağdaştırıcısının sıfırlanması veya settings.xml uyumsuzluğu hatası.", "hizli_cozum": {"baslik": "En Olası İlk Adım: settings.xml İçinde DirectX 11 (DX_Version = 2) Ayarlayın", "aciklama": "Belgeler\Rockstar Games\GTA V\settings.xml dosyasını Not Defteri ile açıp <DX_Version value=\"2\" /> satırını 2 olarak kaydedin ve oyun klasöründeki eski d3d11.dll / dxgi.dll mod kalıntılarını silin.", "komut": ""}}, {"slug": "valorant/van-1067", "oyun": "Valorant", "oyun_hub_url": "/valorant-hata-cozumleri.html", "hata_kodu": "VAN 1067", "issue_id": 1, "varyant_yazimlari": ["VAN 1067", "van1067", "valorant van 1067", "van 1067 hatası"], "title": "Valorant VAN 1067 Hatası Çözümü (TPM 2.0 ve vgc Servisi)", "meta_description": "Valorant VAN 1067 bağlantı hatası için TPM 2.0 (fTPM/PTT) kontrolü, vgc servisini otomatik başlatma ve ekran katmanı çakışmalarını giderme çözüm rehberi.", "h1": "Valorant VAN 1067 Bağlantı Hatası Nasıl Çözülür?", "kisa_aciklama": "Valorant VAN 1067 hatası, Riot İstemcisi'nin arka planda çalışan Riot Vanguard kullanıcı modu hizmeti (vgc.exe) veya donanımsal TPM 2.0 güvenlik çipiyle olan şifreli oturum bağlantısının koptuğunu belirten hata kodudur. Genellikle BIOS güncellemesi sonrası fTPM/PTT modülünün kapanması veya vgc servisinin durması nedeniyle ortaya çıkar.", "nedenler": ["BIOS güncellemesi sonrasında AMD fTPM veya Intel PTT (TPM 2.0) modülünün devre dışı kalması.", "Windows Hizmetleri'nde (services.msc) 'vgc' servisinin durması veya başlangıç türünün 'Elle' kalması.", "Discord Donanım İvmesi, RivaTuner (RTSS) veya 3. parti antivirüs sürücülerinin vgc.exe iletişimini engellemesi."], "cozum_adimlari": [{"baslik": "tpm.msc ile TPM 2.0 Hazırlık Durumunu Doğrulayın", "aciklama": "Win + R tuşlarına basıp tpm.msc komutunu çalıştırın. Açılan pencerede 'Durum: TPM kullanılmaya hazır' ve 'Belirtim Sürümü: 2.0' yazdığını kontrol edin.", "komut": "powershell -Command \"Get-Tpm | Select-Object TpmPresent, TpmReady\"", "komut_notu": {"ne_yapar": "Sistemde TPM 2.0 güvenlik yongasının mevcut (TpmPresent) ve kullanıma hazır (TpmReady) olup olmadığını sorgular.", "risk": "Salt-okunur sorgulama komutudur; hiçbir sistem ayarını değiştirmez.", "geri_alma": "Geri alma işlemi gerektirmez."}, "gorsel_yolu": "", "alt_metin": "Windows tpm.msc ekranında TPM kullanılmaya hazır ve Belirtim Sürümü 2.0 doğrulaması"}, {"baslik": "BIOS Üzerinden AMD fTPM veya Intel PTT Özelliğini Açın", "aciklama": "tpm.msc ekranında TPM görünmüyorsa BIOS'a girin; AMD işlemcilerde Advanced > AMD fTPM Configuration > AMD fTPM Switch ayarını, Intel işlemcilerde Settings > Security > Trusted Computing > Intel Platform Trust Technology (PTT) ayarını Enabled yapın ve F10 ile kaydedin.", "komut": "", "gorsel_yolu": "", "alt_metin": "BIOS ayarlarında AMD fTPM Switch ve Intel PTT seçeneklerinin Enabled yapılması"}, {"baslik": "vgc Hizmetini Otomatik Yapın ve Hata Kurtarma Seçeneğini Ayarlayın", "aciklama": "Win + R > services.msc ekranında 'vgc' hizmetine çift tıklayın. Başlangıç Türünü 'Otomatik' yapın, Kurtarma sekmesinden 'İlk Hata: Hizmeti Yeniden Başlat' seçeneğini işaretleyip kaydedin ve Yönetici CMD üzerinden servisi başlatın.", "komut": "sc config vgc start= auto && net start vgc", "komut_notu": {"ne_yapar": "Riot Vanguard (vgc) hizmetini Otomatik başlangıç moduna geçirir ve servisi başlatır.", "risk": "Standart Windows servis başlatma işlemidir; sistem kararlılığını bozmaz.", "geri_alma": "services.msc üzerinden vgc hizmetinin başlangıç türünü tekrar Elle konumuna getirebilirsiniz."}, "gorsel_yolu": "", "alt_metin": "services.msc penceresinde vgc hizmeti Başlangıç Türü Otomatik ve Kurtarma ayarları"}, {"baslik": "Çakışan Ekran Katmanlarını (Overlay) Kapatıp Yeniden Başlatın", "aciklama": "Discord Ayarlar > Oyun Arayüzü (Overlay) ve RivaTuner Statistics Server (RTSS) gibi üçüncü parti ekran katmanı uygulamalarını kapatıp bilgisayarınızı yeniden başlatın.", "komut": "", "gorsel_yolu": "", "alt_metin": "Discord Oyun Arayüzü (Overlay) ve arka plan katman yazılımlarının kapatılması"}], "isle_yaramazsa": "Sorun devam ediyorsa Windows Güvenliği > Cihaz Güvenliği > Çekirdek Yalıtım (Core Isolation) altındaki 'Bellek Bütünlüğü' ayarını kontrol edin ve anakart üreticinizin web sitesinden güncel BIOS sürümünü kontrol edin.", "resmi_kaynak_url": "", "resmi_kaynak_baslik": "Riot Games Valorant VAN 1067 Resmi Destek Sayfası", "sss": [{"soru": "Valorant VAN 1067 hatası neden kaynaklanır?", "cevap": "VAN 1067 hatası TPM 2.0 servisinin yanıt vermemesi, vgc hizmetinin durması veya Discord/RivaTuner gibi 3. parti ekran katmanı (overlay) yazılımlarının Vanguard ile çakışmasından kaynaklanır."}, {"soru": "VAN 1067 ile VAN 9003 arasındaki fark nedir?", "cevap": "VAN 9003 doğrudan BIOS üzerindeki UEFI Secure Boot (Güvenli Önyükleme) özelliğinin kapalı veya 'Not Active' olmasından kaynaklanırken, VAN 1067 daha çok TPM 2.0 iletişim kopması ve vgc arka plan servisinin durmasıyla ilişkilidir."}], "ilgili_hatalar": [{"url": "/valorant/van-9003", "oyun": "Valorant", "hata_kodu": "VAN 9003", "baslik": "Valorant VAN 9003 Hatası Çözümü (Secure Boot & BIOS)"}, {"url": "/valorant/val-62", "oyun": "Valorant", "hata_kodu": "VAL 62", "baslik": "Valorant VAL 62 ve Paket Kaybı Çözüm Rehberi"}, {"url": "/valorant-hata-cozumleri.html", "oyun": "Valorant", "hata_kodu": "TÜM HATALAR", "baslik": "Valorant Hata Kodları ve Çözüm Merkezi"}, {"url": "/lol/van-128", "oyun": "League of Legends", "hata_kodu": "VAN 128", "baslik": "LoL Vanguard VAN 128 Hatası Çözümü (Adım Adım)"}], "video_embed_url": "", "yazar": "OyunÇöz Teknik Ekibi", "tarih_yayin": "2026-03-01", "tarih_guncelleme": "2026-11-17", "test_edilen_surum": "Windows 10 / 11 (23H2 & 24H2) • Güncel Valorant İstemcisi", "oncelik": 6, "tek_cumle_ozet": "TPM 2.0 güvenlik yongası veya vgc arka plan servisi yanıt vermediğinde oluşan bağlantı hatası.", "hizli_cozum": {"baslik": "En Olası İlk Adım: BIOS'tan TPM 2.0 (fTPM / PTT) Açıp vgc Servisini Başlatın", "aciklama": "tpm.msc ekranında TPM 2.0 hazır görünmüyorsa BIOS'tan AMD fTPM veya Intel PTT ayarını Enabled yapın; ardından Windows Hizmetleri'nde vgc servisini Otomatik moda alıp başlatın.", "komut": "sc config vgc start= auto && net start vgc"}, "senaryolar": [{"id": "amd-ftpm", "etiket": "AMD Ryzen İşlemci (fTPM)", "baslik": "AMD Ryzen Sistemlerde BIOS fTPM 2.0 Açma", "aciklama": "BIOS'a girip Advanced > AMD fTPM Configuration menüsüne geçin ve 'AMD CPU fTPM' (veya Security Device Support) ayarını Enabled yaparak F10 ile kaydedin."}, {"id": "intel-ptt", "etiket": "Intel Core İşlemci (PTT)", "baslik": "Intel Sistemlerde BIOS PTT (Platform Trust Technology) Açma", "aciklama": "BIOS'a girip Settings > Security > Trusted Computing (veya Peripherals) menüsüne geçin ve 'Intel Platform Trust Technology (PTT)' ayarını Enabled yaparak F10 ile kaydedin."}]}, {"slug": "cs2/vac-oturum-dogrulanamadi", "oyun": "Counter-Strike 2", "oyun_hub_url": "/cs2-hata-cozumleri.html", "hata_kodu": "VAC Oturum Doğrulanamadı", "issue_id": 5, "varyant_yazimlari": ["cs2 vac oyun oturumunuzu doğrulayamadı", "vac oturum doğrulanamadı", "vac was unable to verify your game session cs2", "cs2 vac hatası"], "title": "CS2 VAC Oyun Oturumunuzu Doğrulayamadı Hatası Çözümü", "meta_description": "Counter-Strike 2 (CS2) 'VAC oyun oturumunuzu doğrulayamadı' hatası için dosya bütünlüğü doğrulama, SteamService.exe onarımı ve bcdedit çözüm rehberi.", "h1": "CS2 VAC Oyun Oturumunuzu Doğrulayamadı Hatası Nasıl Çözülür?", "kisa_aciklama": "Counter-Strike 2 'VAC oyun oturumunuzu doğrulayamadı (VAC Was Unable to Verify Your Game Session)' uyarısı, Valve Anti-Cheat servisinin (SteamService.exe) oyun belleğindeki imzaları doğrulayamadığını ve resmi eşleştirme sunucularına girişi engellediğini belirtir. Bu uyarı bir VAC yasaklaması (ban) değildir; servis ve dosya doğrulamasıyla adım adım giderilir.", "nedenler": ["Steam istemcisinin yetersiz yetkiyle çalışması veya arka planda SteamService.exe bileşeninin kilitlenmesi.", "Güncelleme sonrasında pak01.vpk veya bin/win64 klasöründeki imza dosyalarının bozulması.", "Windows önyükleme yapılandırmasında nointegritychecks değerinin açık kalması."], "cozum_adimlari": [{"baslik": "CS2 Oyun Dosyalarının Bütünlüğünü Doğrulayın", "aciklama": "Steam Kütüphanesi > Counter-Strike 2 > Sağ Tık Özellikler > Yüklü Dosyalar menüsünden 'Oyun dosyalarının bütünlüğünü doğrula' işlemini tamamlayın.", "komut": "", "gorsel_yolu": "", "alt_metin": "Steam Kütüphanesi Counter-Strike 2 Yüklü Dosyalar sekmesinde dosya bütünlüğü doğrulama adımı"}, {"baslik": "Steam Client Service Bileşenini Onarın ve Yönetici Başlatın", "aciklama": "Steam'i tamamen kapatın. Komut İstemi'ni Yönetici olarak açıp SteamService.exe /repair komutunu çalıştırın ve ardından Steam'i Yönetici Olarak başlatın.", "komut": "\"C:\Program Files (x86)\Common Files\Steam\SteamService.exe\" /repair", "komut_notu": {"ne_yapar": "VAC imza doğrulamasından sorumlu olan resmi Steam Client Service bileşenini onarır ve yeniden kaydeder.", "risk": "Yalnızca Steam servis kayıtlarını onarır; oyun veya sistem dosyalarını silmez.", "geri_alma": "Steam istemcisini normal şekilde yeniden başlatmanız yeterlidir."}, "gorsel_yolu": "", "alt_metin": "Yönetici Komut İstemi üzerinde SteamService.exe repair komutunun çalıştırılması"}, {"baslik": "Windows Çekirdek Bütünlük Kontrolünü Varsayılana Döndürün", "aciklama": "Yönetici CMD penceresinde bcdedit /deletevalue nointegritychecks ve bcdedit /deletevalue loadoptions komutlarını uygulayın ve bilgisayarınızı yeniden başlatın.", "komut": "bcdedit /deletevalue nointegritychecks && bcdedit /deletevalue loadoptions", "komut_notu": {"ne_yapar": "Windows Önyükleme Yapılandırma Verilerinde (BCD) devre dışı bırakılmış bütünlük kontrollerini varsayılan standart duruma döndürür.", "risk": "Standart Windows güvenlik doğrulamasını etkinleştirir; imzasız test sürücüleri varsa yüklenmeyebilir.", "geri_alma": "İşlem öncesi oluşturduğunuz Sistem Geri Yükleme Noktasına (rstrui.exe) dönebilirsiniz."}, "gorsel_yolu": "", "alt_metin": "Yönetici CMD penceresinde bcdedit deletevalue nointegritychecks komutunun uygulanması"}], "isle_yaramazsa": "Steam > Ayarlar > İndirmeler menüsünden 'İndirme Önbelleğini Temizle' seçeneğini uygulayın ve oyunu masaüstü kısayolu yerine doğrudan Steam Kütüphanesi içerisinden başlatın.", "resmi_kaynak_url": "", "resmi_kaynak_baslik": "Steam Destek — VAC Oyun Oturumunuzu Doğrulayamadı Resmi Makalesi", "sss": [{"soru": "CS2 VAC oyun oturumunuzu doğrulayamadı hatası VAC ban mıdır?", "cevap": "Hayır, bu uyarı kesinlikle bir VAC yasaklaması (ban) değildir. Yerel Steam Client Service bileşeninin veya oyun dosyası imzalarının o oturumda doğrulanamadığını belirtir."}, {"soru": "Dosya doğrulama yaptığım halde hata neden tekrar ediyor?", "cevap": "Steam yönetici yetkisi olmadan açıldığında veya SteamService.exe arka planda durduğunda tek başına dosya doğrulama yetmez; SteamService.exe /repair işlemi uygulanıp bilgisayar yeniden başlatılmalıdır."}], "ilgili_hatalar": [{"url": "/cs2/packet-burst-fps-dusmesi", "oyun": "Counter-Strike 2", "hata_kodu": "PACKET BURST & FPS", "baslik": "CS2 Packet Burst ve FPS Düşmesi Çözüm Rehberi"}, {"url": "/cs2-hata-cozumleri.html", "oyun": "Counter-Strike 2", "hata_kodu": "TÜM HATALAR", "baslik": "Counter-Strike 2 (CS2) Hata Kodları ve Çözüm Merkezi"}, {"url": "/valorant/van-9003", "oyun": "Valorant", "hata_kodu": "VAN 9003", "baslik": "Valorant VAN 9003 Hatası Çözümü (Secure Boot & BIOS)"}], "video_embed_url": "", "yazar": "OyunÇöz Teknik Ekibi", "tarih_yayin": "2026-03-01", "tarih_guncelleme": "2026-11-17", "test_edilen_surum": "Windows 10 / 11 (23H2 & 24H2) • Counter-Strike 2 Source 2", "oncelik": 7, "tek_cumle_ozet": "Steam Client Service veya oyun dosyası imzaları doğrulanamadığında eşleştirmeyi engelleyen uyarı.", "hizli_cozum": {"baslik": "En Olası İlk Adım: SteamService.exe /repair Çalıştırıp Dosyaları Doğrulayın", "aciklama": "Steam'i kapatıp Yönetici CMD üzerinde SteamService.exe /repair komutunu çalıştırın, ardından Steam'i Yönetici olarak açıp CS2 dosya bütünlüğünü doğrulayın.", "komut": "\"C:\Program Files (x86)\Common Files\Steam\SteamService.exe\" /repair"}}, {"slug": "minecraft/exit-code-1", "oyun": "Minecraft", "oyun_hub_url": "/minecraft-hata-cozumleri.html", "hata_kodu": "Exit Code 1 (Çıkış Kodu: 1)", "issue_id": 15, "varyant_yazimlari": ["minecraft exit code 1", "çıkış kodu 1 minecraft", "exit code: 1", "oyun beklenmedik şekilde çöktü çıkış kodu 1"], "title": "Minecraft Exit Code 1 (Çıkış Kodu: 1) Hatası Çözüm Rehberi", "meta_description": "Minecraft Launcher 'Oyun beklenmedik şekilde çöktü: Çıkış Kodu 1 (Exit Code 1)' hatası için Java 21 uyumu, mods klasörü ve JVM RAM argümanı çözüm rehberi.", "h1": "Minecraft Exit Code 1 (Çıkış Kodu: 1) Hatası Nasıl Çözülür?", "kisa_aciklama": "Minecraft Launcher'da 'Oyun beklenmedik şekilde çöktü — Çıkış Kodu: 1 (Exit Code: 1)' hatası, Java Sanal Makinesi'nin (JVM) başlatma sırasında uyumsuz bir Forge/Fabric modu, bozuk yapılandırma dosyası veya yanlış Java sürümü nedeniyle sonlandığını gösterir.", "nedenler": ["Minecraft 1.20.5 ve 1.21+ sürümleri Java 21 gerektirirken sistemde eski Java 8 veya Java 17 yolunun seçili olması.", "%appdata%\.minecraft\mods klasöründe oyun sürümüyle uyumsuz bir .jar mod dosyasının bulunması.", "JVM Başlatma Argümanlarında (-Xmx) sistemde bulunandan fazla RAM ayrılması."], "cozum_adimlari": [{"baslik": "mods Klasöründeki Uyumsuz Modları ve latest.log Kaydını Kontrol Edin", "aciklama": "Win + R tuşlarına basıp %appdata%\.minecraft\logs\latest.log dosyasını açarak çökme satırını kontrol edin; uyumsuz modları mods klasöründen geçici olarak çıkarın.", "komut": "java -version", "komut_notu": {"ne_yapar": "Sistemde kurulu olan varsayılan Java sürümünü ve 64-bit mimarisini salt-okunur olarak gösterir.", "risk": "Salt-okunur sorgulama komutudur; hiçbir sistem ayarını değiştirmez.", "geri_alma": "Geri alma işlemi gerektirmez."}, "gorsel_yolu": "", "alt_metin": "appdata .minecraft logs klasöründeki latest.log dosyası ve mods klasörü kontrolü"}, {"baslik": "Minecraft Yüklemeler Ayarından Java Yürütülebilir Dosya Yolunu Sıfırlayın", "aciklama": "Minecraft Launcher > Yüklemeler (Installations) > Profilin yanındaki 3 nokta > Düzenle > Daha Fazla Seçenek altındaki 'Java Yürütülebilir Dosyası' kutusunu sıfırlayarak yerleşik Java 21'i kullanmasını sağlayın.", "komut": "", "gorsel_yolu": "", "alt_metin": "Minecraft Launcher Yüklemeler Düzenle ekranında Java Yürütülebilir Dosyası yolunun sıfırlanması"}, {"baslik": "JVM RAM Argümanını (-Xmx) Dengeli Seviyeye Ayarlayın", "aciklama": "16 GB RAM'li bir bilgisayarda JVM Argümanları satırındaki -Xmx değerini -Xmx4G veya modlu paketlerde -Xmx6G olarak ayarlayıp kaydedin.", "komut": "", "gorsel_yolu": "", "alt_metin": "Minecraft Launcher JVM Bağımsız Değişkenleri satırında -Xmx4G RAM ayarı"}], "isle_yaramazsa": "Windows Grafik Ayarları üzerinden javaw.exe dosyasını Yüksek Performanslı harici ekran kartınıza (NVIDIA / AMD) atayın ve ekran kartı OpenGL sürücünüzü güncelleyin.", "resmi_kaynak_url": "", "resmi_kaynak_baslik": "Minecraft Help Center — Resmi Çökme ve Exit Code Destek Sayfası", "sss": [{"soru": "Minecraft Exit Code 1 hatası neden olur?", "cevap": "En yaygın sebebi Forge/Fabric mods klasöründeki uyumsuz bir .jar mod dosyası veya Minecraft 1.20.5+ sürümünde Java 21 yerine eski Java sürümünün seçili olmasıdır."}, {"soru": "mods klasöründeki modları taşımak dünyalarımı (saves) siler mi?", "cevap": "Dünyalarınız saves klasöründe yer alır; ancak modlu bloklar içeren bir dünyayı modları çıkardıktan sonra açmadan önce saves klasörünüzün yedeğini almanız önerilir."}], "ilgili_hatalar": [{"url": "/minecraft/glfw-error-65542", "oyun": "Minecraft", "hata_kodu": "GLFW 65542", "baslik": "Minecraft GLFW Error 65542 (WGL OpenGL) Çözüm Rehberi"}, {"url": "/minecraft-hata-cozumleri.html", "oyun": "Minecraft", "hata_kodu": "TÜM HATALAR", "baslik": "Minecraft Hata Kodları ve Çözüm Merkezi"}, {"url": "/black-myth-wukong/out-of-video-memory", "oyun": "Black Myth: Wukong", "hata_kodu": "Out of Video Memory", "baslik": "Black Myth: Wukong Out of Video Memory Hatası Çözümü"}], "video_embed_url": "", "yazar": "OyunÇöz Teknik Ekibi", "tarih_yayin": "2026-03-01", "tarih_guncelleme": "2026-11-17", "test_edilen_surum": "Windows 10 / 11 (23H2 & 24H2) • Minecraft 1.20.4 / 1.21 (Java 21)", "oncelik": 8, "tek_cumle_ozet": "Uyumsuz Forge/Fabric modları veya yanlış Java 21 yürütülebilir yolu nedeniyle oluşan çökme kodu.", "hizli_cozum": {"baslik": "En Olası İlk Adım: Uyumsuz Modları Çıkarın ve Yerleşik Java 21 Yolunu Sıfırlayın", "aciklama": "%appdata%\.minecraft\mods klasöründeki uyumsuz .jar modlarını kontrol edin ve Minecraft Launcher > Yüklemeler > Düzenle altından Java Yürütülebilir Dosyası yolunu varsayılana sıfırlayın.", "komut": "java -version"}}, {"slug": "rdr2/err-gfx-state", "oyun": "Red Dead Redemption 2", "oyun_hub_url": "/red-dead-redemption-2-hata-cozumleri.html", "hata_kodu": "ERR_GFX_STATE", "issue_id": 19, "varyant_yazimlari": ["ERR_GFX_STATE", "rdr2 err_gfx_state", "err gfx state rdr2", "sga_vulkan_final_init"], "title": "RDR2 ERR_GFX_STATE Hatası Çözümü (sga_ Vulkan Temizliği)", "meta_description": "Red Dead Redemption 2 (RDR2) ERR_GFX_STATE çökme hatası için Settings klasöründeki sga_ Vulkan önbellek dosyalarını silme ve -ignorepipelinecache rehberi.", "h1": "Red Dead Redemption 2 ERR_GFX_STATE Hatası Nasıl Çözülür?", "kisa_aciklama": "Red Dead Redemption 2 'ERR_GFX_STATE' hatası, RAGE oyun motorunun Vulkan veya DirectX 12 grafik boru hattı (pipeline) önbelleğini yüklerken bozuk bir sga_ gölgelendirici dosyasıyla karşılaştığını ve GPU sürücüsünün çöktüğünü belirtir. Belgeler klasöründeki sga_ önbellek dosyalarının temizlenmesi ve başlatma parametresiyle bu sorun adım adım giderilir.", "nedenler": ["Belgeler\Rockstar Games\Red Dead Redemption 2\Settings klasöründeki sga_vulkan_final_init dosyalarının bozulması.", "Ekran kartı sürücü güncellemesi sonrasında eski pipeline önbelleğinin sıfırlanmaması.", "Aşırı GPU hız aşırtma (Overclock) veya RivaTuner / MSI Afterburner OSD katmanı çakışması."], "cozum_adimlari": [{"baslik": "Settings Klasöründeki Bozuk sga_ Önbellek Dosyalarını Silin", "aciklama": "Belgeler\Rockstar Games\Red Dead Redemption 2\Settings klasörünü açın ve sga_vulkan_final_init ile başlayan 3 önbellek dosyasını silin (system.xml dosyasını silmeyin).", "komut": "powershell -Command \"Get-ChildItem $env:USERPROFILE\Documents\Rockstar*\Red*\Settings\sga_* -ErrorAction SilentlyContinue\"", "komut_notu": {"ne_yapar": "Belgeler klasöründeki RDR2 Settings dizininde bulunan sga_ önbellek dosyalarını listeler.", "risk": "Salt-okunur listeleme komutudur; hikaye kayıt (save) dosyalarınıza dokunmaz.", "geri_alma": "Oyun yeniden başlatıldığında temiz sga_ önbellek dosyalarını otomatik olarak oluşturur."}, "gorsel_yolu": "", "alt_metin": "Belgeler Rockstar Games Red Dead Redemption 2 Settings klasöründeki sga_ dosyalarının silinmesi"}, {"baslik": "Başlatma Seçeneklerine -ignorepipelinecache Parametresini Ekleyin", "aciklama": "Steam, Epic Games veya Rockstar Games Launcher üzerinde RDR2 Başlatma Seçenekleri (Launch Arguments) kutusuna -ignorepipelinecache komutunu ekleyin.", "komut": "-ignorepipelinecache", "komut_notu": {"ne_yapar": "Oyun açılışında bozuk Vulkan/DX12 grafik boru hattı önbelleğinin yoksayılmasını sağlar.", "risk": "Oyun başlatıcısı (Launcher) parametresidir; sistem ayarlarını değiştirmez.", "geri_alma": "Başlatma seçeneklerinden parametreyi silerek varsayılan duruma dönebilirsiniz."}, "gorsel_yolu": "", "alt_metin": "Steam ve Rockstar Games Launcher başlatma seçeneklerine -ignorepipelinecache parametresinin eklenmesi"}, {"baslik": "Grafik API Ayarını system.xml Üzerinden Sabitleyin", "aciklama": "Sorun devam ederse Settings\system.xml dosyasını Not Defteri ile açıp <API>kSettingAPI_Vulkan</API> satırını kontrol edin veya kSettingAPI_DX12 ile değiştirip kaydedin.", "komut": "", "gorsel_yolu": "", "alt_metin": "RDR2 system.xml dosyasında kSettingAPI_Vulkan ve kSettingAPI_DX12 satırının düzenlenmesi"}], "isle_yaramazsa": "Ekran kartınızda hız aşırtma (Overclock) varsa varsayılan değerlere çekin, RivaTuner OSD katmanını kapatın ve ekran kartı sürücünüzün güncel WHQL sürümünü kullanın.", "resmi_kaynak_url": "", "resmi_kaynak_baslik": "Rockstar Games RDR2 ERR_GFX_STATE Resmi Destek Sayfası", "sss": [{"soru": "RDR2 ERR_GFX_STATE hatası neden olur?", "cevap": "Belgeler\Rockstar Games\Red Dead Redemption 2\Settings klasöründeki sga_vulkan_final_init gölgelendirici önbellek dosyalarının ekran kartı sürücü güncellemesi veya ani kapanma sonrasında bozulmasından kaynaklanır."}, {"soru": "sga_ dosyalarını silmek RDR2 kayıt (save) dosyalarımı siler mi?", "cevap": "Hayır, hikaye kayıtlarınız Profiles klasöründe saklanır; sga_ ile başlayan dosyalar yalnızca geçici grafik önbelleğidir ve oyun açılışta yeniden oluşturulur."}], "ilgili_hatalar": [{"url": "/red-dead-redemption-2-hata-cozumleri.html", "oyun": "Red Dead Redemption 2", "hata_kodu": "TÜM HATALAR", "baslik": "Red Dead Redemption 2 Hata Kodları ve Çözüm Merkezi"}, {"url": "/bannerlord/d3d-device-context-map", "oyun": "Mount & Blade II: Bannerlord", "hata_kodu": "d3d_device_context", "baslik": "Bannerlord d3d_device_context_map GPU Çökmesi Çözümü"}, {"url": "/fc-25/anticheat-hatasi", "oyun": "EA Sports FC 25", "hata_kodu": "EA AntiCheat", "baslik": "EA Sports FC 25 AntiCheat Hatası Çözüm Rehberi"}, {"url": "/black-myth-wukong/out-of-video-memory", "oyun": "Black Myth: Wukong", "hata_kodu": "Out of Video Memory", "baslik": "Black Myth: Wukong Out of Video Memory Hatası Çözümü"}], "video_embed_url": "", "yazar": "OyunÇöz Teknik Ekibi", "tarih_yayin": "2026-03-01", "tarih_guncelleme": "2026-11-17", "test_edilen_surum": "Windows 10 / 11 (23H2 & 24H2) • RDR2 Güncel Sürüm", "oncelik": 9, "tek_cumle_ozet": "Belgeler klasöründeki sga_ Vulkan gölgelendirici önbelleği bozulduğunda oluşan RAGE motoru hatası.", "hizli_cozum": {"baslik": "En Olası İlk Adım: Belgeler Klasöründeki Bozuk sga_ Dosyalarını Silin", "aciklama": "Belgeler\Rockstar Games\Red Dead Redemption 2\Settings klasöründeki sga_vulkan_final_init ile başlayan 3 önbellek dosyasını silip oyunu yeniden başlatın.", "komut": ""}}, {"slug": "fivem/harita-yuklenmiyor-texture-loss", "oyun": "FiveM", "oyun_hub_url": "/gtav-fivem-hata-cozumleri.html", "hata_kodu": "Texture Loss (Harita Yüklenmeme)", "issue_id": 12, "varyant_yazimlari": ["fivem harita yüklenmiyor", "fivem texture loss", "fivem yollar kayboluyor", "extended texture budget fivem"], "title": "FiveM Harita Yüklenmiyor (Texture Loss) Çözüm Rehberi", "meta_description": "FiveM sunucularında yolların ve binaların kaybolması (harita yüklenmiyor / texture loss) sorunu için Extended Texture Budget ve cache temizleme rehberi.", "h1": "FiveM Harita Yüklenmiyor (Texture Loss) Sorunu Nasıl Çözülür?", "kisa_aciklama": "FiveM roleplay sunucularında şehir içinde hızla ilerlerken yolların, binaların ve zemin dokularının kaybolması (Texture Loss), özel sunucu varlıklarının (modlu araçlar, kıyafetler ve MLO haritalar) ekran kartı VRAM doku bütçesini aşmasından kaynaklanır. Extended Texture Budget ayarı ve CitizenFX önbellek temizliği ile bu sorun adım adım giderilebilir.", "nedenler": ["Oyun içi Grafik ayarlarındaki 'Extended Texture Budget' çubuğunun en solda (sıfırda) bırakılması nedeniyle özel sunucu dokularının VRAM'e yüklenememesi.", "%localappdata%\FiveM\FiveM.app\data altındaki cache ve server-cache klasörlerinde biriken bozuk sunucu varlıkları.", "8 GB ve 16 GB RAM bulunan sistemlerde Windows Sanal Bellek (Pagefile) alanının kalabalık sunucular için yetersiz kalması."], "cozum_adimlari": [{"baslik": "Extended Texture Budget Ayarını Ekran Kartı Belleğinize Göre Yükseltin", "aciklama": "FiveM'de tüm grafik ayarlarını en düşüğe çekmek VRAM doku bütçesini sıfırlar ve yolları yok eder. Ayarlar > Grafikler (Graphics) sekmesinde en altta yer alan 'Extended Texture Budget' çubuğunu ekran kartı belleğinize göre %50 ile %65 arasına yükseltin.", "komut": "", "gorsel_yolu": "", "alt_metin": "FiveM Grafik ayarlarında Extended Texture Budget çubuğunun yüzde 50-65 seviyesine getirilmesi"}, {"baslik": "FiveM CitizenFX Önbellek (Cache) Klasörlerini Temizleyin", "aciklama": "Win + R tuşlarına basıp %localappdata%\FiveM\FiveM.app\data klasörünü açın. 'game-storage' klasörü HARİÇ içerideki 'cache', 'server-cache' ve 'server-cache-priv' klasörlerini silin. Bu işlem bozuk sunucu scriptlerini ve dokularını temizler.", "komut": "powershell -Command \"Remove-Item -Path '$env:LOCALAPPDATA\FiveM\FiveM.app\data\cache\*' -Recurse -Force -ErrorAction SilentlyContinue\"", "komut_notu": {"ne_yapar": "FiveM'in geçici cache klasörü içindeki bozulmuş sunucu önbellek dosyalarını temizler; game-storage klasörüne dokunmaz.", "risk": "Sunucuya ilk girişte güncel sunucu önbelleği yeniden indirilir; ana oyun dosyaları silinmez.", "geri_alma": "FiveM istemcisini yeniden başlattığınızda temiz önbellek klasörü otomatik olarak oluşturulur."}, "gorsel_yolu": "", "alt_metin": "FiveM.app data klasöründe game-storage hariç cache ve server-cache klasörlerinin temizlenmesi"}, {"baslik": "8 GB ve 16 GB RAM Sistemler İçin Sanal Bellek (Pagefile) Yapılandırması", "aciklama": "Kalabalık FiveM sunucuları 14 GB'ın üzerinde bellek tüketir. Gelişmiş Sistem Ayarları > Performans > Gelişmiş > Sanal Bellek bölümünden SSD diskinizde Başlangıç: 16384 MB, En Yüksek: 24576 MB sanal bellek tanımlayın.", "komut": "", "gorsel_yolu": "", "alt_metin": "Windows Gelişmiş Sistem Ayarları Sanal Bellek penceresinde 16384 MB - 24576 MB yapılandırması"}], "isle_yaramazsa": "Harita kaybolmasıyla birlikte DirectX çökmesi de yaşıyorsanız GTA V ERR_GFX_D3D_INIT çözüm rehberimizdeki settings.xml DX_Version ayarını kontrol edin ve oyun içi Doku Kalitesi (Texture Quality) ayarını Normal/Yüksek seviyesinde sabitleyin.", "resmi_kaynak_url": "", "resmi_kaynak_baslik": "Cfx.re / FiveM Resmi İstemci Destek Dokümantasyonu", "sss": [{"soru": "FiveM'de ayarları düşürdüğüm halde neden yollar ve binalar kayboluyor?", "cevap": "Extended Texture Budget çubuğu en solda (sıfırda) kaldığında FiveM özel sunucu varlıklarını (modlu araçlar ve MLO binalar) VRAM'e yükleyemez. Bu çubuğu yarıya (%50-%65) getirmek doku kaybını çözer."}, {"soru": "FiveM cache temizlerken hangi klasörü silmemeliyim?", "cevap": "%localappdata%\FiveM\FiveM.app\data içindeki 'game-storage' klasörünü silmemelisiniz; yalnızca cache, server-cache ve server-cache-priv klasörlerini temizlemeniz yeterlidir."}], "ilgili_hatalar": [{"url": "/gta-v/err-gfx-d3d-init", "oyun": "GTA V", "hata_kodu": "ERR_GFX_D3D_INIT", "baslik": "GTA 5 ERR_GFX_D3D_INIT Hatası Çözümü (DirectX 11)"}, {"url": "/gtav-fivem-hata-cozumleri.html", "oyun": "GTA V & FiveM", "hata_kodu": "TÜM HATALAR", "baslik": "GTA V ve FiveM Hata Kodları Çözüm Merkezi"}, {"url": "/rdr2/err-gfx-state", "oyun": "Red Dead Redemption 2", "hata_kodu": "ERR_GFX_STATE", "baslik": "RDR2 ERR_GFX_STATE Hatası Çözüm Rehberi"}], "video_embed_url": "", "yazar": "OyunÇöz Teknik Ekibi", "tarih_yayin": "2026-03-01", "tarih_guncelleme": "2026-11-17", "test_edilen_surum": "Windows 10 / 11 (23H2 & 24H2) • FiveM Cfx.re Güncel İstemci", "oncelik": 10, "tek_cumle_ozet": "FiveM sunucularında Extended Texture Budget düşük kaldığında yolların ve binaların kaybolması sorunu.", "hizli_cozum": {"baslik": "En Olası İlk Adım: Extended Texture Budget Çubuğunu %50-%65 Seviyesine Çekin", "aciklama": "FiveM Grafik ayarlarının en altındaki 'Extended Texture Budget' çubuğunu sıfırda bırakmayın; ekran kartı belleğinize göre orta seviyeye (%50-%65) yükseltin.", "komut": ""}}, {"slug": "cs2/packet-burst-fps-dusmesi", "oyun": "Counter-Strike 2", "oyun_hub_url": "/cs2-hata-cozumleri.html", "hata_kodu": "Packet Burst ve FPS Düşmesi", "issue_id": 6, "varyant_yazimlari": ["cs2 packet burst", "cs2 fps düşmesi", "cs2 takılma sorunu", "cs2 jitter çözümü"], "title": "CS2 Packet Burst ve FPS Düşmesi Çözümü (Source 2 Rehberi)", "meta_description": "Counter-Strike 2 (CS2) Packet Burst, Jitter ve çatışma anında ani FPS düşmesi sorunu için 1 Paket ağ arabelleği, Shader Cache ve başlatma kodu çözüm rehberi.", "h1": "CS2 Packet Burst ve FPS Düşmesi Sorunu Nasıl Çözülür?", "kisa_aciklama": "CS2'de sağ üst köşede beliren 'Packet Burst / Jitter' uyarısı ve çatışma anındaki ani kare süresi (frame-time) sıçramaları, Source 2 motorunun büyük sub-tick ağ paketlerini veya derlenmemiş DirectX gölgelendiricilerini zamanında işleyemediğini gösterir.", "nedenler": ["Oyun içi 'Paket Kaybını / Gecikmeyi Dengelemek İçin Arabelleğe Alma' ayarının kapalı (Yok) olması.", "Ekran kartı güncellemesi sonrasında eski DirectX Shader Cache dosyalarının çakışması.", "Eski CS:GO başlatma seçeneklerinin (-high, -threads, +mat_queue_mode) Source 2 işlemci zamanlamasını bozması."], "cozum_adimlari": [{"baslik": "Oyun İçi Ağ Arabelleğe Alma Ayarını 1 Paket Yapın", "aciklama": "CS2 Ayarlar > Oyun > 'Paket kaybını / gecikmeyi dengelemek için arabelleğe alma' seçeneğini 'Yok' yerine '1 Paket' olarak ayarlayın. Bu ayar sub-tick paket dalgalanmalarını dengeler.", "komut": "", "gorsel_yolu": "", "alt_metin": "CS2 Oyun ayarlarında Paket kaybını dengelemek için arabelleğe alma seçeneğinin 1 Paket yapılması"}, {"baslik": "Bozuk DirectX Gölgelendirici Önbelleğini (Shader Cache) Temizleyin", "aciklama": "Windows Disk Temizleme (cleanmgr) aracını açıp 'DirectX Gölgelendirici Önbelleği' kutucuğunu işaretleyerek temizleyin; NVIDIA Denetim Masası > 3D Ayarları altından Gölgelendirici Önbellek Boyutu ayarını 10 GB yapın.", "komut": "cleanmgr /d C", "komut_notu": {"ne_yapar": "Windows Disk Temizleme aracını C: sürücüsü için başlatır; DirectX Gölgelendirici Önbelleği seçilerek bozuk derlenmiş shader dosyaları temizlenir.", "risk": "Yalnızca geçici önbellek dosyalarını temizler; kişisel dosyalarınıza dokunmaz.", "geri_alma": "Oyun açıldığında temiz gölgelendirici önbelleğini otomatik olarak yeniden derler."}, "gorsel_yolu": "", "alt_metin": "Windows Disk Temizleme aracında DirectX Gölgelendirici Önbelleği temizliği"}, {"baslik": "Eski CS:GO Başlatma Seçeneklerini Kaldırın", "aciklama": "Steam > CS2 > Özellikler > Başlatma Seçenekleri kutusundaki -high, -threads veya +mat_queue_mode gibi eski CS:GO parametrelerini tamamen silin.", "komut": "", "gorsel_yolu": "", "alt_metin": "Steam CS2 Özellikler Başlatma Seçenekleri kutusundaki eski -high ve -threads kodlarının silinmesi"}], "isle_yaramazsa": "Oyun içi Gelişmiş Görüntü ayarlarında NVIDIA Reflex Düşük Gecikme Oranı ayarını 'Etkin' (Etkin + Takviye değil), Parçacık Detayı ayarını 'Düşük' olarak seçip test edin.", "resmi_kaynak_url": "", "resmi_kaynak_baslik": "Steam / Valve Counter-Strike 2 Resmi Performans ve Ağ Rehberi", "sss": [{"soru": "Eski CS:GO başlatma kodları (-threads, -high) CS2'de neden FPS düşürüyor?", "cevap": "Source 2 motoru çoklu iş parçacığı zamanlamasını kendisi yönetir; -high ve -threads gibi eski kodlar işlemcinin P-Core / E-Core dağılımını bozarak %1 Low FPS düşüşüne yol açar."}, {"soru": "Pingim düşük olduğu halde neden Packet Burst uyarısı çıkıyor?", "cevap": "Sub-tick mimarisinde anlık büyük paket grupları geldiğinde arabellek 'Yok' seçiliyse paket sıralaması bozulur; '1 Paket' arabelleğe alma ayarı bu dalgalanmayı sönümler."}], "ilgili_hatalar": [{"url": "/cs2/vac-oturum-dogrulanamadi", "oyun": "Counter-Strike 2", "hata_kodu": "VAC DOĞRULAMA", "baslik": "CS2 VAC Oyun Oturumunuzu Doğrulayamadı Hatası Çözümü"}, {"url": "/cs2-hata-cozumleri.html", "oyun": "Counter-Strike 2", "hata_kodu": "TÜM HATALAR", "baslik": "Counter-Strike 2 (CS2) Hata Kodları ve Çözüm Merkezi"}, {"url": "/valorant/val-62", "oyun": "Valorant", "hata_kodu": "VAL 62", "baslik": "Valorant VAL 62 ve Paket Kaybı Çözüm Rehberi"}], "video_embed_url": "", "yazar": "OyunÇöz Teknik Ekibi", "tarih_yayin": "2026-03-01", "tarih_guncelleme": "2026-11-17", "test_edilen_surum": "Windows 10 / 11 (23H2 & 24H2) • Counter-Strike 2 Source 2", "oncelik": 11, "tek_cumle_ozet": "Source 2 motorunda sub-tick paket dalgalanması ve bozuk DirectX gölgelendirici önbelleği kaynaklı takılma.", "hizli_cozum": {"baslik": "En Olası İlk Adım: Oyun İçi Ağ Arabelleğini '1 Paket' Yapın ve Eski Kodları Silin", "aciklama": "CS2 Ayarlar > Oyun altından 'Paket kaybını / gecikmeyi dengelemek için arabelleğe alma' seçeneğini '1 Paket' yapın ve Steam başlatma seçeneklerindeki eski -threads / -high kodlarını silin.", "komut": ""}}, {"slug": "bannerlord/d3d-device-context-map", "oyun": "Mount & Blade II: Bannerlord", "oyun_hub_url": "/mount-and-blade-2-bannerlord-hata-cozumleri.html", "hata_kodu": "d3d_device_context_->Map", "issue_id": 18, "varyant_yazimlari": ["d3d_device_context", "d3d_device_context_map", "rglGPU_device::lock_texture", "bannerlord d3d_device_context"], "title": "Bannerlord d3d_device_context_map Hatası Çözüm Rehberi", "meta_description": "Mount & Blade II: Bannerlord d3d_device_context_map (lock_texture) çökmesi için ProgramData Shaders temizliği ve ses kanalı optimizasyonu çözüm rehberi.", "h1": "Bannerlord d3d_device_context_map Hatası Nasıl Çözülür?", "kisa_aciklama": "Mount & Blade II: Bannerlord 'd3d_device_context_->Map at rglGPU_device::lock_texture' hatası, büyük meydan ve kuşatma savaşlarında RGL motorunun ekran kartı belleğindeki (VRAM) bir dokuyu kilitlerken bozuk gölgelendirici önbelleği nedeniyle DirectX 11 cihazının yanıt vermeyi kestiğini gösterir.", "nedenler": ["C:\ProgramData\Mount and Blade II Bannerlord\Shaders klasöründeki derlenmiş gölgelendirici dosyalarının bozulması.", "Kuşatma savaşlarında 512 (Çok Yüksek) ses kanalı ve arazi gölgelendiricilerinin aynı anda bellek taşmasına yol açması.", "Güncel olmayan Harmony / ButterLib modlarının yeni oyun yamasıyla çakışması."], "cozum_adimlari": [{"baslik": "ProgramData Altındaki Bozuk Shaders Klasörünü Silin", "aciklama": "Win + R tuşlarına basıp C:\ProgramData\Mount and Blade II Bannerlord yolunu açın, Shaders klasörünü tamamen silin ve Steam üzerinden oyun dosyalarının bütünlüğünü doğrulayın.", "komut": "powershell -Command \"Test-Path 'C:\ProgramData\Mount and Blade II Bannerlord\Shaders'\"", "komut_notu": {"ne_yapar": "ProgramData altındaki Bannerlord Shaders önbellek klasörünün varlığını salt-okunur olarak kontrol eder.", "risk": "Salt-okunur kontrol komutudur; kayıt (save) dosyalarınıza zarar vermez.", "geri_alma": "Steam dosya doğrulaması çalıştırıldığında temiz Shaders dosyaları yeniden indirilir."}, "gorsel_yolu": "", "alt_metin": "C ProgramData Mount and Blade II Bannerlord dizinindeki Shaders klasörünün temizlenmesi"}, {"baslik": "Arazi Kalitesi ve Ses Kanalları Ayarını Optimize Edin", "aciklama": "Oyun içi Performans ayarlarından Arazi Kalitesi (Terrain Quality) seçeneğini 'Yüksek' yapın ve Ses ayarlarından Ses Kanalları (Sound Channels) değerini 'Orta (256)' seviyesine çekin.", "komut": "", "gorsel_yolu": "", "alt_metin": "Bannerlord Performans ve Ses ayarlarında Arazi Kalitesi ve Ses Kanalları (256) optimizasyonu"}, {"baslik": "Ekran Kartı Gölgelendirici Önbelleğini ve Sürücüyü Güncelleyin", "aciklama": "Windows Disk Temizleme (cleanmgr) aracıyla DirectX Gölgelendirici Önbelleği'ni temizleyin ve GPU sürücünüzün güncel WHQL sürümde olduğundan emin olun.", "komut": "", "gorsel_yolu": "", "alt_metin": "Windows Disk Temizleme aracında DirectX Gölgelendirici Önbelleği temizleme adımı"}], "isle_yaramazsa": "Topluluk modları (Harmony, ButterLib, UIExtenderEx) kullanıyorsanız mod sürümlerinin aktif Bannerlord yamasıyla uyumlu olduğundan ve Modules klasöründeki .dll dosyalarında Windows güvenlik engeli bulunmadığından emin olun.", "resmi_kaynak_url": "", "resmi_kaynak_baslik": "TaleWorlds Mount & Blade II: Bannerlord Resmi Teknik Destek Forumu", "sss": [{"soru": "Bannerlord d3d_device_context hatası neden özellikle kuşatma savaşlarında çıkar?", "cevap": "Kuşatma savaşlarında yüzlerce birimin zırh/arazi gölgelendiricileri ve 512 ses kanalı aynı anda işlendiğinde C:\ProgramData\Mount and Blade II Bannerlord\Shaders içindeki bozuk önbellek GPU kilitlenmesine yol açar."}, {"soru": "ProgramData Shaders klasörünü silmek kayıtlı oyunumu (Save) etkiler mi?", "cevap": "Hayır, Bannerlord kayıt dosyalarınız Belgeler\Mount and Blade II Bannerlord\Game Saves klasöründe tutulur."}], "ilgili_hatalar": [{"url": "/mount-and-blade-2-bannerlord-hata-cozumleri.html", "oyun": "Mount & Blade II: Bannerlord", "hata_kodu": "TÜM HATALAR", "baslik": "Mount & Blade II: Bannerlord Hata Çözüm Merkezi"}, {"url": "/rdr2/err-gfx-state", "oyun": "Red Dead Redemption 2", "hata_kodu": "ERR_GFX_STATE", "baslik": "RDR2 ERR_GFX_STATE Hatası Çözüm Rehberi"}, {"url": "/fc-25/anticheat-hatasi", "oyun": "EA Sports FC 25", "hata_kodu": "EA AntiCheat", "baslik": "EA Sports FC 25 AntiCheat Hatası Çözüm Rehberi"}, {"url": "/black-myth-wukong/out-of-video-memory", "oyun": "Black Myth: Wukong", "hata_kodu": "Out of Video Memory", "baslik": "Black Myth: Wukong Out of Video Memory Hatası Çözümü"}], "video_embed_url": "", "yazar": "OyunÇöz Teknik Ekibi", "tarih_yayin": "2026-03-01", "tarih_guncelleme": "2026-11-17", "test_edilen_surum": "Windows 10 / 11 (23H2 & 24H2) • Bannerlord Güncel Sürüm", "oncelik": 12, "tek_cumle_ozet": "Kuşatma savaşlarında bozuk ProgramData Shaders önbelleği nedeniyle oluşan DirectX 11 GPU çökmesi.", "hizli_cozum": {"baslik": "En Olası İlk Adım: ProgramData Altındaki Bozuk Shaders Klasörünü Silin", "aciklama": "C:\ProgramData\Mount and Blade II Bannerlord\Shaders klasörünü tamamen silip Steam üzerinden oyun dosyalarının bütünlüğünü doğrulayın.", "komut": ""}}, {"slug": "fc-25/anticheat-hatasi", "oyun": "EA Sports FC 25", "oyun_hub_url": "/fc25-hata-cozumleri.html", "hata_kodu": "EA AntiCheat Hatası (115 / 7)", "issue_id": 14, "varyant_yazimlari": ["fc 25 anticheat hatası", "ea anticheat service encountered an error", "fc 25 açılmıyor anticheat", "ea anticheat hata 115"], "title": "EA Sports FC 25 AntiCheat Hatası Çözümü (Adım Adım)", "meta_description": "EA Sports FC 25 açılış ekranında kapanma ve EA AntiCheat Service Encountered an Error (115 / 7) hatası için App Recovery ve onarım çözüm rehberi.", "h1": "EA Sports FC 25 AntiCheat Hatası Nasıl Çözülür?", "kisa_aciklama": "EA Sports FC 25 açılış ekranında (Splash Screen) kapanma veya 'EA AntiCheat Service Encountered an Error (115 / 7)' uyarısı, çekirdek düzeyindeki EAAntiCheat.GameService.exe hizmetinin dijital sertifikaları doğrulayamadığını veya önbelleğin bozulduğunu gösterir.", "nedenler": ["Oyun klasöründeki EAAntiCheat.GameServiceLauncher.exe veya .dll dosyalarının dijital imzasının bozulması.", "EA App önbelleğinin veya EA AntiCheat yükleyicisinin güncelleme sırasında yarım kalması.", "Faceit Anti-Cheat, Riot Vanguard veya DS4Windows sanal kontrolcü sürücülerinin çakışması."], "cozum_adimlari": [{"baslik": "EA App Recovery ile İstemci Önbelleğini Temizleyin", "aciklama": "Windows Başlat menüsünden EA > App Recovery aracını çalıştırıp 'Clear Cache' butonuna tıklayın ve EA App istemcisini Yönetici olarak yeniden başlatın.", "komut": "", "gorsel_yolu": "", "alt_metin": "EA App Recovery penceresinde Clear Cache önbellek temizleme adımı"}, {"baslik": "EA AntiCheat Installer Aracıyla Kaldır (Uninstall All) ve Yeniden Yükle Yapın", "aciklama": "FC 25 kurulum klasöründeki __Installer\EAAntiCheat dizinine girin, EAAntiCheat.Installer.exe aracını Yönetici olarak çalıştırıp 'Uninstall All' ve ardından FC 25'i seçerek 'Install' yapın.", "komut": "powershell -Command \"Get-Service EAAntiCheatService -ErrorAction SilentlyContinue\"", "komut_notu": {"ne_yapar": "EAAntiCheatService arka plan hizmetinin sistemde kurulu ve hazır olup olmadığını salt-okunur olarak kontrol eder.", "risk": "Salt-okunur sorgulama komutudur; sistem ayarlarını değiştirmez.", "geri_alma": "Herhangi bir değişiklik yapmadığı için geri alma gerektirmez."}, "gorsel_yolu": "", "alt_metin": "EAAntiCheat.Installer.exe aracında FC 25 için Uninstall All ve Install işlemi"}, {"baslik": "Alternatif (Eski Sürümler İçin): EXE ve DLL Dijital İmzalarını Doğrulayın", "aciklama": "Yukarıdaki iki adım sorunu çözmezse FC25.exe ve EAAntiCheat.GameServiceLauncher.exe dosyalarına sağ tıklayıp Özellikler > Dijital İmzalar > Ayrıntılar > Sertifikayı Göster > Sertifika Yükle adımını uygulayın.", "komut": "", "gorsel_yolu": "", "alt_metin": "FC25.exe Özellikler Dijital İmzalar sekmesinden sertifika doğrulama adımı"}], "isle_yaramazsa": "Arka planda çalışan DS4Windows, reWASD veya Faceit Anti-Cheat varsa kapatıp test edin; hem Steam'i hem de EA App istemcisini Yönetici olarak çalıştırarak oyunu başlatın.", "resmi_kaynak_url": "", "resmi_kaynak_baslik": "EA Help — EA AntiCheat Resmi Sorun Giderme Sayfası", "sss": [{"soru": "FC 25 AntiCheat ekranı dolduktan sonra oyun neden hiç hata vermeden kapanıyor?", "cevap": "EA App önbelleğindeki bozuk lisans oturumu veya EAAntiCheat.GameService.exe servisinin yetki eksikliği oyunun Splash Screen sonrasında kapanmasına yol açar; App Recovery (Clear Cache) ve EA AntiCheat yeniden kurulumu sorunu giderir."}, {"soru": "EA AntiCheat onarımı yapmak Ultimate Team veya Kariyer kaydımı siler mi?", "cevap": "Hayır, yalnızca anti-cheat servis dosyalarını yeniler; oyun içi ilerlemeniz ve kayıtlarınız korunur."}], "ilgili_hatalar": [{"url": "/fc25-hata-cozumleri.html", "oyun": "EA Sports FC 25", "hata_kodu": "TÜM HATALAR", "baslik": "EA Sports FC 25 Hata Kodları ve Çözüm Merkezi"}, {"url": "/rdr2/err-gfx-state", "oyun": "Red Dead Redemption 2", "hata_kodu": "ERR_GFX_STATE", "baslik": "RDR2 ERR_GFX_STATE Hatası Çözüm Rehberi"}, {"url": "/bannerlord/d3d-device-context-map", "oyun": "Mount & Blade II: Bannerlord", "hata_kodu": "d3d_device_context", "baslik": "Bannerlord d3d_device_context_map Hatası Çözüm Rehberi"}, {"url": "/black-myth-wukong/out-of-video-memory", "oyun": "Black Myth: Wukong", "hata_kodu": "Out of Video Memory", "baslik": "Black Myth: Wukong Out of Video Memory Hatası Çözümü"}], "video_embed_url": "", "yazar": "OyunÇöz Teknik Ekibi", "tarih_yayin": "2026-03-01", "tarih_guncelleme": "2026-11-17", "test_edilen_surum": "Windows 10 / 11 (23H2 & 24H2) • EA Sports FC 25 Güncel Sürüm", "oncelik": 13, "tek_cumle_ozet": "EA App önbelleği veya EAAntiCheat servisi bozulduğunda oyunun açılış ekranında kapanması sorunu.", "hizli_cozum": {"baslik": "En Olası İlk Adım: EA App Recovery ile Önbelleği Temizleyip AntiCheat'i Onarın", "aciklama": "EA App > App Recovery > Clear Cache işlemini uygulayın ve FC 25 kurulum dizinindeki EAAntiCheat.Installer.exe aracıyla Uninstall All / Install yapın.", "komut": ""}}, {"slug": "black-myth-wukong/out-of-video-memory", "oyun": "Black Myth: Wukong", "oyun_hub_url": "/black-myth-wukong-hata-cozumleri.html", "hata_kodu": "Out of Video Memory", "issue_id": 25, "varyant_yazimlari": ["out of video memory wukong", "black myth wukong out of video memory", "out of video memory trying to allocate a rendering resource", "wukong shader compilation crash"], "title": "Black Myth: Wukong Out of Video Memory Hatası Çözümü", "meta_description": "Black Myth: Wukong 'Out of video memory trying to allocate a rendering resource' gölgelendirici derleme çökmesi için sanal bellek, -dx11 ve BIOS çözüm rehberi.", "h1": "Black Myth: Wukong Out of Video Memory Hatası Nasıl Çözülür?", "kisa_aciklama": "Black Myth: Wukong ve diğer Unreal Engine 5 oyunlarında açılışta çıkan 'Out of video memory trying to allocate a rendering resource' hatası, ekran kartı VRAM belleğinizin bitmesinden değil; yoğun gölgelendirici derlemesi (Shader Compilation) sırasında işlemci veya sanal bellek (Pagefile) taşmasından kaynaklanır.", "nedenler": ["13. ve 14. Nesil Intel Core (i7/i9 K serisi) işlemcilerde yüksek voltaj/frekans nedeniyle Oodle veri açma işleminin çökmesi.", "Windows Sanal Bellek (Pagefile) boyutunun 16 GB altında veya kapalı olması.", "DirectX 12 gölgelendirici önbelleğinin ilk derleme sırasında kilitlenmesi."], "cozum_adimlari": [{"baslik": "Sanal Bellek (Pagefile) Boyutunu 16384 MB Yapın ve -dx11 Ekleyin", "aciklama": "Win + R > sysdm.cpl > Gelişmiş > Performans Ayarları > Gelişmiş > Sanal Bellek menüsünden Özel Boyut seçip Başlangıç ve En Büyük boyutu 16384 MB olarak kaydedin; Steam Başlatma Seçenekleri'ne -dx11 parametresini ekleyin.", "komut": "-dx11", "komut_notu": {"ne_yapar": "Black Myth: Wukong'u DirectX 12 yerine DirectX 11 uyumluluk modunda başlatarak gölgelendirici derleme yükünü azaltır.", "risk": "Steam başlatma seçeneğidir; sistem dosyalarını değiştirmez.", "geri_alma": "Steam Başlatma Seçenekleri kutusundan -dx11 ifadesini silerek DirectX 12 moduna geri dönebilirsiniz."}, "gorsel_yolu": "", "alt_metin": "Windows Sanal Bellek 16384 MB ayarı ve Steam -dx11 başlatma seçeneği"}, {"baslik": "Intel 13. ve 14. Nesil (i7/i9 K Serisi) İşlemciler İçin: 0x12B Mikro Kodlu BIOS Güncellemesi", "aciklama": "Yalnızca 13. veya 14. nesil Intel Core işlemci kullanıyorsanız Oodle veri açma çökmesini önlemek için anakart üreticinizin yayınladığı Intel Default Settings (0x12B microcode) BIOS sürümünü kurun.", "komut": "", "gorsel_yolu": "", "alt_metin": "Anakart BIOS ekranında Intel Default Settings ve 0x12B mikro kod güncellemesi"}, {"baslik": "Intel 13./14. Nesil İçin Geçici Çözüm: Gölgelendirici Derlemesi Sırasında Güç Tasarrufu Modu", "aciklama": "BIOS güncellemesi yapana kadar Denetim Masası > Güç Seçenekleri (powercfg.cpl) ekranından güç planını geçici olarak 'Güç Tasarrufu' moduna alın, Shader Compilation (%100) tamamlandıktan sonra tekrar Dengeli moda dönün.", "komut": "powercfg.cpl", "komut_notu": {"ne_yapar": "Windows Denetim Masası Güç Seçenekleri penceresini açar.", "risk": "Salt arayüz açma komutudur; herhangi bir risk taşımaz.", "geri_alma": "Gölgelendirici derlemesi bittikten sonra Güç Seçenekleri'nden tekrar Dengeli planı seçebilirsiniz."}, "gorsel_yolu": "", "alt_metin": "Windows Güç Seçenekleri penceresinde gölgelendirici derlemesi için Güç Tasarrufu planı seçimi"}], "isle_yaramazsa": "Windows Disk Temizleme aracıyla DirectX Gölgelendirici Önbelleği'ni temizleyin ve ekran kartı sürücünüzü güncel WHQL sürümüne yükseltin.", "resmi_kaynak_url": "", "resmi_kaynak_baslik": "Game Science — Black Myth: Wukong Resmi Destek Duyuruları", "sss": [{"soru": "12 GB veya 16 GB ekran kartım olmasına rağmen neden Out of Video Memory hatası alıyorum?", "cevap": "Unreal Engine 5 gölgelendirici derlemesi (Oodle decompression) sırasında oluşan işlemci veya sanal bellek (Pagefile) hatasını da 'Out of video memory' başlığıyla raporlar; sanal belleği 16384 MB yapmak ve Intel 13./14. nesilde BIOS güncellemek sorunu çözer."}, {"soru": "-dx11 başlatma kodu grafik kalitesini etkiler mi?", "cevap": "-dx11 uyumluluk modu Işın İzleme (Ray Tracing) özelliğini devre dışı bırakır ancak gölgelendirici çökmesini aşarak oyuna sorunsuz girmenizi sağlar."}], "ilgili_hatalar": [{"url": "/black-myth-wukong-hata-cozumleri.html", "oyun": "Black Myth: Wukong", "hata_kodu": "TÜM HATALAR", "baslik": "Black Myth: Wukong Hata Kodları ve Çözüm Merkezi"}, {"url": "/rdr2/err-gfx-state", "oyun": "Red Dead Redemption 2", "hata_kodu": "ERR_GFX_STATE", "baslik": "RDR2 ERR_GFX_STATE Hatası Çözüm Rehberi"}, {"url": "/bannerlord/d3d-device-context-map", "oyun": "Mount & Blade II: Bannerlord", "hata_kodu": "d3d_device_context", "baslik": "Bannerlord d3d_device_context_map Hatası Çözüm Rehberi"}, {"url": "/fc-25/anticheat-hatasi", "oyun": "EA Sports FC 25", "hata_kodu": "EA AntiCheat", "baslik": "EA Sports FC 25 AntiCheat Hatası Çözüm Rehberi"}], "video_embed_url": "", "yazar": "OyunÇöz Teknik Ekibi", "tarih_yayin": "2026-03-01", "tarih_guncelleme": "2026-11-17", "test_edilen_surum": "Windows 10 / 11 (23H2 & 24H2) • Black Myth: Wukong Güncel Sürüm", "oncelik": 14, "tek_cumle_ozet": "Unreal Engine 5 gölgelendirici derlemesi sırasında sanal bellek veya işlemci kaynaklı bellek hatası.", "hizli_cozum": {"baslik": "En Olası İlk Adım: Sanal Belleği 16384 MB Yapın ve -dx11 Parametresiyle Başlatın", "aciklama": "Windows Sanal Bellek (Pagefile) boyutunu 16384 MB olarak ayarlayın ve Steam Başlatma Seçenekleri kutusuna -dx11 parametresini ekleyin.", "komut": "-dx11"}, "senaryolar": [{"id": "amd-veya-genel", "etiket": "AMD Ryzen / Genel Sistemler", "baslik": "Sanal Bellek (16384 MB) ve -dx11 Başlatma Modu", "aciklama": "sysdm.cpl > Gelişmiş > Performans > Sanal Bellek altından Başlangıç ve En Büyük boyutu 16384 MB yapın ve Steam Başlatma Seçenekleri'ne -dx11 parametresini ekleyin."}, {"id": "intel-13-14-nesil", "etiket": "Intel 13. / 14. Nesil (i7 / i9 K)", "baslik": "0x12B Mikro Kodlu BIOS Güncellemesi ve Geçici Güç Tasarrufu Modu", "aciklama": "13. veya 14. nesil Intel işlemcilerde Oodle gölgelendirici açma çökmesini önlemek için anakartınızın 0x12B microcode (Intel Default Settings) BIOS güncellemesini kurun veya ilk derleme sırasında Windows Güç Seçenekleri'nden geçici olarak 'Güç Tasarrufu' modunu seçin."}]}];

window.renderHomeShowcase = function() {
  try {
    const gamesGrid = document.getElementById('homeGamesShowcaseGrid');
    if (gamesGrid && STATE.games.length > 0) {
      const featuredGames = STATE.games.slice(0, 16);
      gamesGrid.innerHTML = featuredGames.map(g => {
        const mono = window.getGameMonogramInfo ? window.getGameMonogramInfo(g.slug, g.accent_color) : { code: (g.short_name || 'OYN').slice(0,3).toUpperCase(), color: '#10b981' };
        const realCount = Math.max(Number(g.issue_count || 0), 1);
        const engineInfo = escapeHTML((g.engine || 'PC').split('(')[0].trim());
        return `
          <a
            href="/${g.slug}-hata-cozumleri.html"
            onclick="event.preventDefault(); selectGame('${g.slug}'); switchTab('issues'); document.getElementById('tabContent-issues')?.scrollIntoView({behavior:'smooth'});"
            class="oc-card oc-card-interactive p-4 flex items-center justify-between gap-3 group"
            style="border-left: 3px solid ${mono.color} !important;"
          >
            <div class="flex items-center gap-3 min-w-0">
              <span class="oc-monogram" style="background: linear-gradient(135deg, ${mono.color}, ${mono.color}bb); border-color: rgba(255,255,255,0.28);" aria-hidden="true">${mono.code}</span>
              <div class="min-w-0">
                <div class="text-xs sm:text-sm font-extrabold text-white group-hover:text-[#34d399] transition truncate">${escapeHTML(g.short_name || g.name)}</div>
                <div class="text-[11px] text-gray-400 truncate">${engineInfo}</div>
              </div>
            </div>
            <span class="px-2.5 py-1 rounded-lg bg-white/5 border border-white/10 text-[11px] font-bold text-gray-200 shrink-0">${realCount} Hata Kodu</span>
          </a>
        `;
      }).join('');
    }
  } catch (e) {
    console.warn('renderHomeShowcase error:', e);
  }
};

window.renderLiveAutocomplete = async function(rawVal, isMobile = false) {
  const dropdown = document.getElementById(isMobile ? 'mobileLiveSearchDropdown' : 'liveSearchDropdown');
  if (!dropdown) return;
  const q = String(rawVal || '').trim().toLowerCase();

  if (!q) {
    const topPages = DEDICATED_ERROR_PAGES.slice(0, 6);
    dropdown.innerHTML = `
      <div class="p-3 space-y-2">
        <div class="text-[11px] font-bold uppercase tracking-wider text-[#88c0a8] px-1">En Çok Bakılan Hata Kodları</div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
          ${topPages.map(p => `
            <a
              href="/${p.slug}"
              class="p-2.5 rounded-xl bg-white/5 hover:bg-[#5e9c88]/20 border border-white/5 hover:border-[#88c0a8]/40 transition flex items-center justify-between gap-2"
            >
              <div class="min-w-0">
                <div class="text-xs font-bold text-white truncate">${escapeHTML(p.oyun)} • ${escapeHTML(p.hata_kodu)}</div>
                <div class="text-[11px] text-gray-400 truncate">${escapeHTML(p.tek_cumle_ozet || p.title)}</div>
              </div>
              <span class="text-xs text-[#88c0a8] shrink-0">→</span>
            </a>
          `).join('')}
        </div>
      </div>
    `;
    dropdown.classList.remove('hidden');
    return;
  }

  const matchedPages = DEDICATED_ERROR_PAGES.filter(p => {
    const hay = `${p.oyun} ${p.hata_kodu} ${p.title} ${(p.varyant_yazimlari || []).join(' ')} ${p.kisa_aciklama}`.toLowerCase();
    return hay.includes(q);
  }).slice(0, 6);

  const matchedGames = STATE.games.filter(g =>
    (g.name || '').toLowerCase().includes(q) ||
    (g.short_name || '').toLowerCase().includes(q) ||
    (g.common_tags || []).some(t => t.toLowerCase().includes(q))
  ).slice(0, 4);

  let htmlParts = '';
  if (matchedPages.length > 0) {
    htmlParts += `
      <div class="p-3 space-y-1.5">
        <div class="text-[11px] font-bold uppercase tracking-wider text-gray-400 px-1">Hata Kodu Çözüm Sayfaları (${matchedPages.length})</div>
        <div class="space-y-1">
          ${matchedPages.map(p => `
            <a
              href="/${p.slug}"
              class="block p-2.5 rounded-xl hover:bg-white/10 transition flex items-center justify-between gap-3"
            >
              <div class="min-w-0">
                <div class="flex items-center gap-2">
                  <span class="oc-badge oc-badge-accent font-mono">${escapeHTML(p.hata_kodu)}</span>
                  <span class="text-xs font-bold text-white truncate">${escapeHTML(p.title)}</span>
                </div>
                <div class="text-[11px] text-gray-400 truncate mt-0.5">${escapeHTML(p.tek_cumle_ozet || p.meta_description)}</div>
              </div>
              <span class="text-xs font-bold text-[#88c0a8] shrink-0">Çözümü gör →</span>
            </a>
          `).join('')}
        </div>
      </div>
    `;
  }

  if (matchedGames.length > 0) {
    htmlParts += `
      <div class="p-3 space-y-1.5">
        <div class="text-[11px] font-bold uppercase tracking-wider text-gray-400 px-1">Oyunlar (${matchedGames.length})</div>
        <div class="space-y-1">
          ${matchedGames.map(g => `
            <a
              href="/${g.slug}-hata-cozumleri.html"
              class="block p-2 rounded-xl hover:bg-white/10 transition flex items-center justify-between gap-3"
            >
              <span class="text-xs font-bold text-white">${escapeHTML(g.name)}</span>
              <span class="text-[11px] text-[#88c0a8]">${Number(g.issue_count || 1)} Hata Kodu →</span>
            </a>
          `).join('')}
        </div>
      </div>
    `;
  }

  const safeQ = q.replace(/'/g, "\\'");
  htmlParts += `
    <div class="p-3 bg-[#131924] flex items-center justify-between gap-2">
      <span class="text-xs text-gray-300 truncate">Aradığın <strong>"${escapeHTML(rawVal)}"</strong> hatası listede yok mu?</span>
      <button
        type="button"
        onclick="selectAutocompleteAiQuery('${safeQ}')"
        class="oc-btn oc-btn-primary !min-h-[36px] !py-1.5 !px-3 text-xs shrink-0"
      >
        AI çözümleyiciyle analiz et
      </button>
    </div>
  `;

  dropdown.innerHTML = htmlParts;
  dropdown.classList.remove('hidden');
};

window.handleHeroSearchSubmit = async function(e) {
  if (e) e.preventDefault();
  closeLiveAutocomplete();
  const inp = document.getElementById('globalSearchInput');
  const q = String(inp ? inp.value : '').trim();
  const resBox = document.getElementById('heroSearchResultsSection');
  if (!resBox) return;
  if (!q) {
    resBox.classList.add('hidden');
    return;
  }

  const ql = q.toLowerCase();
  const matchedPages = DEDICATED_ERROR_PAGES.filter(p => {
    const hay = `${p.oyun} ${p.hata_kodu} ${p.title} ${(p.varyant_yazimlari || []).join(' ')} ${p.kisa_aciklama}`.toLowerCase();
    return hay.includes(ql);
  });

  resBox.classList.remove('hidden');
  if (matchedPages.length > 0) {
    resBox.innerHTML = `
      <div class="flex items-center justify-between">
        <h2 class="text-sm font-bold text-white">"${escapeHTML(q)}" İçin Arama Sonuçları (${matchedPages.length})</h2>
        <button type="button" onclick="document.getElementById('heroSearchResultsSection').classList.add('hidden')" class="text-xs text-gray-400 hover:text-white">Kapat ✕</button>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        ${matchedPages.map(p => `
          <a href="/${p.slug}" class="oc-card oc-card-interactive p-4 flex items-center justify-between gap-3">
            <div>
              <div class="flex items-center gap-2">
                <span class="oc-badge oc-badge-accent font-mono">${escapeHTML(p.hata_kodu)}</span>
                <span class="text-xs font-bold text-white">${escapeHTML(p.title)}</span>
              </div>
              <p class="text-xs text-gray-400 mt-1">${escapeHTML(p.tek_cumle_ozet || p.meta_description)}</p>
            </div>
            <span class="text-xs font-bold text-[#88c0a8] shrink-0">Çözümü gör →</span>
          </a>
        `).join('')}
      </div>
    `;
  } else {
    const safeQ = q.replace(/'/g, "\\'");
    resBox.innerHTML = `
      <div class="oc-card p-5 text-center space-y-3">
        <div class="text-sm font-bold text-white">"${escapeHTML(q)}" için hazır hata kodu sayfası bulunamadı</div>
        <p class="text-xs text-gray-400 mx-auto">Bu hatayı yapay zeka arıza çözümleyici ile hemen analiz edip sistemine özel çözüm adımlarını oluşturabilirsin.</p>
        <button type="button" onclick="selectAutocompleteAiQuery('${safeQ}')" class="oc-btn oc-btn-primary text-xs sm:text-sm">
          AI çözümleyiciyle analiz et
        </button>
      </div>
    `;
  }
};

window.handleSearchKeydown = function(e) {
  if (e.key === 'Enter') {
    window.handleHeroSearchSubmit(e);
  } else if (e.key === 'Escape') {
    closeLiveAutocomplete();
  }
};


window.filterHomeTopErrors = function(catKey, btnEl) {
  const cards = document.querySelectorAll('#homeTopErrorsGrid > article[data-error-cat]');
  cards.forEach(card => {
    const c = card.getAttribute('data-error-cat');
    if (!catKey || catKey === 'all' || c === catKey) {
      card.classList.remove('hidden');
    } else {
      card.classList.add('hidden');
    }
  });
  const btns = document.querySelectorAll('.home-err-filter-btn');
  btns.forEach(b => {
    b.className = 'home-err-filter-btn px-3 py-1.5 rounded-xl text-xs font-bold bg-white/5 text-gray-300 hover:text-white border border-white/10 transition';
  });
  if (btnEl) {
    btnEl.className = 'home-err-filter-btn px-3 py-1.5 rounded-xl text-xs font-extrabold bg-[#10b981] text-white border border-[#34d399]/50 transition';
  }
};
