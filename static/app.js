// GameFix AI Hub (HemenÇöz) Frontend Controller (v4.0 - Security Hardened, KVKK/5651 Compliant, Guest Trial, Crash Log Analyzer & Troubleshooting Wizard)

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
  authToken: localStorage.getItem('gamefix_auth_token') || '',
  currentUser: null,
  pendingVerifyEmail: '',
  wizardByIssue: {},
  simulatedRamOverride: null
};

let resolveTimer = null;

function getAuthHeaders(extra = {}) {
  const headers = {
    'X-Client-Id': STATE.clientId,
    ...extra
  };
  if (STATE.authToken) {
    headers['Authorization'] = `Bearer ${STATE.authToken}`;
  }
  return headers;
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

function buildSafetyBannerHtml(combinedText) {
  const risks = analyzeTechnicalRisk(combinedText);
  if (risks.length === 0) return '';

  const restoreCmdRaw = 'Checkpoint-Computer -Description "HemenCoz_Yedek"';
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
        <code class="text-xs font-mono text-amber-200">Checkpoint-Computer -Description "HemenCoz_Yedek"</code>
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
  // 1. WebGL GPU Detection
  let gpuName = 'Tespit Edilemedi (WebGL)';
  try {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl2') || canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    if (gl) {
      const dbg = gl.getExtension('WEBGL_debug_renderer_info');
      const rawRenderer = dbg ? gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER);
      gpuName = cleanWebGLRendererName(rawRenderer);
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
    const raw = localStorage.getItem('hemencoz_cookie_consent');
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
      localStorage.setItem('hemencoz_detected_specs', finalSpecs);
    } catch (e) {}
  }

  if (STATE.currentUser && STATE.authToken) {
    try {
      await fetch('/api/auth/profile', {
        method: 'PUT',
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
      localStorage.setItem('hemencoz_detected_specs', hw.summary);
    } catch (e) {}
  }
  evaluateHardwareCompatibility();
  showToast(`🖥️ Algılanan donanım dolduruldu: ${hw.gpu}`);
}

function loadSavedHardwareSpecs() {
  if (!isFunctionalCookieAllowed()) return;
  try {
    const saved = localStorage.getItem('hemencoz_detected_specs');
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
    return localStorage.getItem('hemencoz_detected_specs') || '';
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

  // Parse RAM in GB
  let ramGb = null;
  const ramMatch = specs.match(/\b(\d{1,3})\s*\+?\s*GB\s*(?:RAM|Bellek)?/i);
  if (ramMatch) {
    ramGb = parseInt(ramMatch[1], 10);
  } else if (navigator.deviceMemory) {
    ramGb = navigator.deviceMemory;
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

function fallbackCover(slug, color) {
  if (window.makeGameCoverDataUri) {
    return window.makeGameCoverDataUri(slug, color);
  }
  return './static/logo.svg';
}

function renderSuggestionChips() {
  const aiContainer = document.getElementById('aiLabSuggestionsContainer');
  const modalContainer = document.getElementById('modalSuggestionsContainer');
  const addContainer = document.getElementById('addGameSuggestionsContainer');

  const buildChips = (inputId, hintId, errorInputId) => STATE.suggestions.map(s => `
    <button
      type="button"
      onclick="pickSuggestedGame('${s.name.replace(/'/g, "\\'")}', '${(s.hint || '').replace(/'/g, "\\'")}', '${inputId}', '${hintId}', '${errorInputId || ''}')"
      class="text-xs px-2.5 py-1.5 rounded-xl bg-[#212936] hover:bg-[#2a3446] text-gray-200 border border-white/10 transition flex items-center gap-2"
    >
      <img
        src="${s.image_url || fallbackCover(s.slug || 'game')}"
        onerror="this.onerror=null;this.src=fallbackCover('${s.slug || 'game'}')"
        alt="${s.name}"
        class="w-7 h-5 rounded object-cover border border-white/10 shrink-0"
      />
      <span class="font-bold text-white">${s.name}</span>
      <span class="text-[10px] text-gray-400">(${s.genre})</span>
    </button>
  `).join('');

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

// --- 2-STEP EMAIL VERIFICATION & AUTHENTICATION ---

async function checkCurrentSession() {
  if (!STATE.authToken) {
    updateAuthUI();
    return;
  }
  try {
    const res = await fetch('/api/auth/me', { headers: getAuthHeaders() });
    if (res.ok) {
      const data = await res.json();
      STATE.currentUser = data.user;
    } else {
      STATE.authToken = '';
      STATE.currentUser = null;
      localStorage.removeItem('gamefix_auth_token');
    }
  } catch (err) {
    console.error('Session check failed:', err);
  }
  updateAuthUI();
}

function hasGuestUsedFreeTrial() {
  try {
    return localStorage.getItem('hemencoz_guest_ai_trial_used') === '1';
  } catch (e) {
    return false;
  }
}

function markGuestFreeTrialUsed() {
  try {
    localStorage.setItem('hemencoz_guest_ai_trial_used', '1');
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

function fillPreviewVerificationCode() {
  const previewCode = document.getElementById('localInboxPreviewCode');
  const inp = document.getElementById('regVerificationCodeInput');
  if (previewCode && inp && previewCode.textContent) {
    inp.value = previewCode.textContent.trim();
    inp.focus();
  }
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
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) {
      showAuthAlert(`⚠️ ${data.detail || 'Kod gönderilemedi.'}`, 'error');
      showToast(data.detail || 'Kod gönderilemedi.');
      return;
    }

    if (data.already_registered && data.token && data.user) {
      STATE.authToken = data.token;
      STATE.currentUser = data.user;
      localStorage.setItem('gamefix_auth_token', data.token);
      updateAuthUI();
      closeAuthModal();
      await Promise.all([fetchIssues(), fetchThreads()]);
      showToast(`✓ Hoş geldin, ${data.user.username}!`);
      return;
    }

    STATE.pendingVerifyEmail = data.email;
    document.getElementById('registerFormStep1').classList.add('hidden');
    document.getElementById('registerFormStep2').classList.remove('hidden');
    document.getElementById('verifyEmailTargetText').textContent = `${data.email} adresine gönderilen 6 haneli onay kodunu girin:`;

    const previewBox = document.getElementById('localInboxPreviewBox');
    const previewCode = document.getElementById('localInboxPreviewCode');
    const codeInp = document.getElementById('regVerificationCodeInput');

    if (data.verification_code_preview) {
      previewBox.classList.remove('hidden');
      previewCode.textContent = data.verification_code_preview;
      codeInp.value = data.verification_code_preview;
    } else {
      previewBox.classList.add('hidden');
      codeInp.value = '';
    }

    setTimeout(() => codeInp.focus(), 80);
    showToast('6 haneli e-posta doğrulama kodu oluşturuldu!');
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
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: STATE.pendingVerifyEmail, code })
    });
    const data = await res.json();
    if (!res.ok) {
      showAuthAlert(`⚠️ ${data.detail || 'Doğrulama başarısız.'}`, 'error');
      showToast(data.detail || 'Doğrulama başarısız.');
      return;
    }

    STATE.authToken = data.token;
    STATE.currentUser = data.user;
    localStorage.setItem('gamefix_auth_token', data.token);
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
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ identifier, password })
    });
    const data = await res.json();
    if (!res.ok) {
      if (res.status === 404) {
        // User has not created an account yet -> switch to Register tab and pre-fill!
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
      showAuthAlert(`⚠️ ${data.detail || 'Giriş başarısız.'}`, 'error');
      showToast(data.detail || 'Giriş başarısız.');
      return;
    }

    STATE.authToken = data.token;
    STATE.currentUser = data.user;
    localStorage.setItem('gamefix_auth_token', data.token);
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
        localStorage.setItem('hemencoz_detected_specs', data.user.system_specs || '');
      } catch (e) {}
    }
    evaluateHardwareCompatibility();
    closeProfileModal();
    showToast('Profil ve sistem bilgileriniz güncellendi!');
  }
}

async function logoutUser() {
  await fetch('./api/auth/logout', { method: 'POST', headers: getAuthHeaders() });
  STATE.authToken = '';
  STATE.currentUser = null;
  localStorage.removeItem('gamefix_auth_token');
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
      headers: getAuthHeaders()
    });
    const data = await res.json();
    if (!res.ok) {
      showToast(data.detail || 'Hesap silinemedi.');
      return;
    }

    STATE.authToken = '';
    STATE.currentUser = null;
    try {
      localStorage.removeItem('gamefix_auth_token');
      localStorage.removeItem('hemencoz_detected_specs');
      localStorage.removeItem(`hemencoz_votes_${STATE.clientId}`);
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
    if (STATE.hasServerApiKey) {
      label.textContent = 'Canlı Gemini 3.8 Flash (API Key Aktif)';
    } else {
      label.textContent = 'Akıllı Forum + AI Motoru Aktif';
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

function renderSidebarGames() {
  const container = document.getElementById('gameNavList');
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
      <span class="text-xs px-2 py-0.5 rounded-full bg-white/10 text-gray-200 font-semibold">${totalIssues}</span>
    </button>
  `;

  for (const g of STATE.games) {
    const isActive = STATE.selectedGame === g.slug;
    const imgSrc = g.image_url || fallbackCover(g.slug, g.accent_color);
    html += `
      <button onclick="selectGame('${g.slug}')" class="game-nav-item ${isActive ? 'active' : ''}">
        <div class="flex items-center gap-3 min-w-0">
          <img
            src="${imgSrc}"
            onerror="this.onerror=null;this.src=fallbackCover('${g.slug}','${g.accent_color}')"
            alt="${g.short_name}"
            class="w-11 h-8 rounded-lg object-cover border border-white/15 shrink-0 shadow-sm"
          />
          <div class="truncate">
            <div class="text-sm font-bold truncate">${g.short_name}</div>
            <div class="text-[11px] text-gray-400 truncate">${g.category}</div>
          </div>
        </div>
        <span class="text-xs px-2 py-0.5 rounded-full bg-white/10 text-gray-200 font-semibold shrink-0">${g.issue_count}</span>
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
    applyGameTheme('#5e9c88');
    if (coverWrapper) coverWrapper.classList.add('hidden');
    catBadge.textContent = 'Tüm Oyunlar Portalı';
    engBadge.textContent = 'Motor: UE4/5 / Source 2 / Clausewitz / RAGE / LWJGL';
    acBadge.textContent = 'Koruma: Vanguard • VAC • EAC • RICOCHET';
    titleEl.textContent = 'Popüler Oyun Sorunları & Yapay Zeka Çözüm Merkezi';
    subEl.textContent = 'Sol menüden bir oyun seçebilir, "+ Yeni Oyun Ekle" ile istediğiniz oyunu (örn: Victoria 3, Bannerlord, RDR 2) ekleyebilir veya AI Çözümleyiciye yazarak otomatik sayfa oluşturabilirsiniz.';

    const globalTags = ['VAN 9003', 'VAC Verify', 'Exit Code 1', 'Packet Burst', 'EA AntiCheat', 'FIVEM Texture Loss', 'Asset Warmup', 'CP77 Flatlined'];
    tagsEl.innerHTML = globalTags
      .map(t => `<button onclick="filterByTag('${t}')" class="text-xs px-2.5 py-1 rounded-lg bg-white/5 hover:bg-white/10 text-gray-200 border border-white/10 transition font-mono">${t}</button>`)
      .join('');
  } else {
    const game = STATE.games.find(g => g.slug === STATE.selectedGame);
    if (!game) return;
    applyGameTheme(game.accent_color);
    if (coverWrapper && coverImg) {
      coverWrapper.classList.remove('hidden');
      coverImg.src = game.image_url || fallbackCover(game.slug, game.accent_color);
      coverImg.onerror = () => { coverImg.src = fallbackCover(game.slug, game.accent_color); };
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

function updateDynamicSEO() {
  try {
    const baseUrl = 'https://erenmtl.github.io/gamefix-hub/';
    const metaDesc = document.querySelector('meta[name="description"]');
    const canonicalEl = document.getElementById('canonicalLink');
    const schemaEl = document.getElementById('dynamicSeoSchema');

    if (STATE.selectedGame === 'all') {
      document.title = STATE.searchQuery
        ? `${STATE.searchQuery} Hatası Çözümü & Rehberi | HemenÇöz`
        : 'HemenÇöz | Oyun Hata Çözümleri, VAN 9003, CS2 VAC, FPS Artırma & Akıllı Arıza Çözüm Merkezi';
      if (metaDesc) {
        metaDesc.setAttribute(
          'content',
          'HemenÇöz ile Valorant VAN 9003 & VAN 1067, CS2 VAC oturum doğrulama ve Packet Burst, LoL Vanguard VAN 128, GTA V, Minecraft Exit Code 1, RDR 2, Bannerlord ve 30+ popüler oyunun hata çözümlerine saniyeler içinde ulaşın.'
        );
      }
      if (canonicalEl) canonicalEl.setAttribute('href', baseUrl);
      if (window.history && window.history.replaceState) {
        const nextUrl = STATE.searchQuery
          ? `${window.location.pathname}?q=${encodeURIComponent(STATE.searchQuery)}`
          : window.location.pathname;
        window.history.replaceState({}, '', nextUrl);
      }
    } else {
      const game = STATE.games.find(g => g.slug === STATE.selectedGame);
      if (game) {
        const tagSummary = (game.common_tags || []).slice(0, 4).join(', ');
        document.title = `${game.name} Hata Çözümleri (${tagSummary}) & Arıza Rehberi | HemenÇöz`;
        if (metaDesc) {
          metaDesc.setAttribute(
            'content',
            `${game.name} (${game.engine}) için en güncel forum sorunları, ${tagSummary} hata kodları, FPS düşmesi, çökme çözümleri ve HemenÇöz adım adım teknik rehberi.`
          );
        }
        const gameUrl = `${baseUrl}?game=${encodeURIComponent(game.slug)}`;
        if (canonicalEl) canonicalEl.setAttribute('href', gameUrl);
        if (window.history && window.history.replaceState) {
          window.history.replaceState({}, '', `${window.location.pathname}?game=${encodeURIComponent(game.slug)}`);
        }
      }
    }

    // Populate dynamic FAQPage Schema from current visible issues for Rich Search Snippets
    if (schemaEl && Array.isArray(STATE.issues) && STATE.issues.length > 0) {
      const faqEntities = STATE.issues.slice(0, 8).map(iss => ({
        '@type': 'Question',
        name: `${iss.game_name || ''} ${iss.title} (${iss.error_code || 'Çözüm'})`.trim(),
        acceptedAnswer: {
          '@type': 'Answer',
          text: (iss.ai_root_cause || iss.symptom_summary || '').replace(/[#*`>_~]/g, '').substring(0, 600)
        }
      }));
      schemaEl.textContent = JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        mainEntity: faqEntities
      });
    }
  } catch (e) {
    console.warn('Dynamic SEO update warning:', e);
  }
}

function renderHomeShowcase() {
  try {
    const totalGamesEl = document.getElementById('hudTotalGamesStat');
    const totalIssuesEl = document.getElementById('hudTotalIssuesStat');
    const gamesGrid = document.getElementById('homeGamesShowcaseGrid');
    const trendingGrid = document.getElementById('homeTrendingIssuesGrid');

    const totalIssuesCount = STATE.games.reduce((acc, g) => acc + (g.issue_count || 0), 0) || STATE.issues.length || 50;
    if (totalGamesEl) totalGamesEl.textContent = `${STATE.games.length || 30}+ Oyun`;
    if (totalIssuesEl) totalIssuesEl.textContent = `${totalIssuesCount}+ Rehber`;

    if (gamesGrid && STATE.games.length > 0) {
      const featuredGames = STATE.selectedGame === 'all'
        ? STATE.games.slice(0, 12)
        : [
            ...STATE.games.filter(g => g.slug === STATE.selectedGame),
            ...STATE.games.filter(g => g.slug !== STATE.selectedGame).slice(0, 11)
          ];

      gamesGrid.innerHTML = featuredGames.map(g => {
        const imgSrc = g.image_url || fallbackCover(g.slug, g.accent_color);
        return `
          <div
            onclick="selectGame('${g.slug}'); switchTab('issues');"
            class="showcase-card rounded-xl overflow-hidden cursor-pointer group flex flex-col justify-between"
          >
            <div class="relative h-20 w-full overflow-hidden bg-[#151b26]">
              <img
                src="${imgSrc}"
                onerror="this.onerror=null;this.src=fallbackCover('${g.slug}','${g.accent_color}')"
                alt="${g.name}"
                class="w-full h-full object-cover group-hover:scale-105 transition duration-300"
              />
              <div class="absolute inset-0 bg-gradient-to-t from-[#161c28] via-transparent to-transparent"></div>
              <span class="absolute top-1.5 right-1.5 text-[10px] font-bold px-1.5 py-0.5 rounded bg-black/75 text-[#a3d9c6] border border-white/10">
                ${g.issue_count || 2} Çözüm
              </span>
            </div>
            <div class="p-2.5">
              <div class="text-xs font-bold text-white truncate group-hover:text-[#88c0a8] transition">${g.short_name}</div>
              <div class="text-[10px] text-gray-400 truncate">${g.category}</div>
            </div>
          </div>
        `;
      }).join('');
    }

    if (trendingGrid && STATE.issues.length > 0) {
      const topIssues = STATE.issues.slice(0, 6);
      trendingGrid.innerHTML = topIssues.map(iss => {
        const imgSrc = iss.game_image_url || fallbackCover(iss.game_slug, iss.accent_color);
        return `
          <div
            onclick="quickSearchTag('${(iss.error_code || iss.title).replace(/'/g, '')}')"
            class="showcase-card rounded-xl p-3.5 cursor-pointer flex flex-col justify-between gap-2.5"
          >
            <div class="flex items-center justify-between gap-2">
              <div class="flex items-center gap-2 min-w-0">
                <img
                  src="${imgSrc}"
                  onerror="this.onerror=null;this.src=fallbackCover('${iss.game_slug}','${iss.accent_color}')"
                  alt="${iss.game_short_name}"
                  class="w-8 h-6 rounded object-cover border border-white/15 shrink-0"
                />
                <span class="text-xs font-bold text-gray-200 truncate">${iss.game_short_name}</span>
              </div>
              <span class="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-[#5e9c88]/20 text-[#a3d9c6] border border-[#5e9c88]/30 shrink-0">
                ${iss.error_code}
              </span>
            </div>
            <div class="text-xs font-bold text-white line-clamp-2 leading-snug">${iss.title}</div>
            <div class="flex items-center justify-between text-[11px] text-gray-400 pt-1 border-t border-white/5">
              <span class="text-[#88c0a8] font-semibold">✓ %${iss.success_rate} Başarı</span>
              <span>👍 ${iss.helpful_votes} Faydalı • Çözümü Gör →</span>
            </div>
          </div>
        `;
      }).join('');
    }
  } catch (e) {
    console.warn('Home showcase render warning:', e);
  }
}

function initCookieConsent() {
  try {
    const saved = localStorage.getItem('hemencoz_cookie_consent');
    const banner = document.getElementById('cookieConsentBanner');
    if (!saved && banner) {
      banner.classList.remove('hidden');
    } else if (saved) {
      const parsed = JSON.parse(saved);
      const funcEl = document.getElementById('cookiePrefFunctional');
      const anaEl = document.getElementById('cookiePrefAnalytics');
      if (funcEl) funcEl.checked = parsed.functional !== false;
      if (anaEl) anaEl.checked = parsed.analytics !== false;
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
    localStorage.setItem('hemencoz_cookie_consent', JSON.stringify(prefs));
  } catch (e) {}
  const banner = document.getElementById('cookieConsentBanner');
  if (banner) banner.classList.add('hidden');
  closeCookieSettingsModal();
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
    localStorage.setItem('hemencoz_cookie_consent', JSON.stringify(prefs));
  } catch (e) {}
  const banner = document.getElementById('cookieConsentBanner');
  if (banner) banner.classList.add('hidden');
  closeCookieSettingsModal();
  showToast('🍪 Özel çerez tercihleriniz kaydedildi.');
}

function openCookieSettingsModal() {
  const modal = document.getElementById('cookieSettingsModal');
  if (modal) modal.classList.remove('hidden');
}

function closeCookieSettingsModal() {
  const modal = document.getElementById('cookieSettingsModal');
  if (modal) modal.classList.add('hidden');
}

function openLegalModal(tab = 'kvkk') {
  switchLegalTab(tab);
  const modal = document.getElementById('legalModal');
  if (modal) modal.classList.remove('hidden');
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
            const imgSrc = g.image_url || fallbackCover(g.slug, g.accent_color);
            return `
              <button
                type="button"
                onclick="selectAutocompleteGame('${g.slug}')"
                class="w-full text-left p-2 rounded-xl hover:bg-white/10 transition flex items-center justify-between gap-3"
              >
                <div class="flex items-center gap-2.5 min-w-0">
                  <img src="${imgSrc}" onerror="this.onerror=null;this.src=fallbackCover('${g.slug}','${g.accent_color}')" alt="${g.short_name}" class="w-10 h-7 rounded object-cover border border-white/15 shrink-0" />
                  <div class="min-w-0">
                    <div class="text-xs font-bold text-white truncate">${g.name}</div>
                    <div class="text-[10px] text-gray-400 truncate">${g.category} • ${g.engine}</div>
                  </div>
                </div>
                <span class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-[#5e9c88]/20 text-[#a3d9c6] border border-[#5e9c88]/30 shrink-0">${g.issue_count || 2} Çözüm</span>
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
          ${matchedIssues.map(iss => `
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
                %${iss.success_rate} Başarı
              </span>
            </button>
          `).join('')}
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
    const raw = localStorage.getItem(`hemencoz_votes_${STATE.clientId}`);
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
    localStorage.setItem(`hemencoz_votes_${STATE.clientId}`, JSON.stringify(map));
  } catch (e) {}
}

async function fetchIssues() {
  const params = new URLSearchParams();
  if (STATE.selectedGame !== 'all') params.set('game_slug', STATE.selectedGame);
  if (STATE.selectedCategory !== 'all') params.set('category', STATE.selectedCategory);
  if (STATE.searchQuery) params.set('search', STATE.searchQuery);

  const res = await fetch(`/api/issues?${params.toString()}`, { headers: getAuthHeaders() });
  STATE.issues = await res.json();
  document.getElementById('issuesCountBadge').textContent = STATE.issues.length;
  renderIssues();
}

function renderIssues() {
  const container = document.getElementById('issuesListContainer');
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
      'Yüksek': 'bg-[#b38852]/20 text-[#e0c59e] border-[#b38852]/35',
      'Orta': 'bg-[#5586ad]/20 text-[#acc8e0] border-[#5586ad]/35'
    };
    const sevClass = severityColors[issue.severity] || severityColors['Yüksek'];

    const forumsHtml = (issue.forum_sources || []).map(f => `
      <div class="forum-quote-box p-3.5 space-y-1.5">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <span class="text-xs font-bold text-[#a3b8d4] flex items-center gap-1.5">
            <span>📌 ${escapeHTML(f.forum)}</span>
            <span class="text-gray-400 font-normal">• ${escapeHTML(f.thread)}</span>
          </span>
          <span class="text-[11px] px-2 py-0.5 rounded bg-white/5 text-gray-300 font-semibold">▲ ${Number(f.upvotes || 0)} Onay</span>
        </div>
        <p class="text-xs text-gray-300 italic">"${escapeHTML(f.quote)}"</p>
      </div>
    `).join('');

    const rawSteps = issue.ai_solution_steps || [];
    const wizState = STATE.wizardByIssue[issue.id] || { active: false, stepIndex: 0, solved: false };
    const totalSteps = Math.max(1, rawSteps.length);
    const curIdx = Math.min(Math.max(0, wizState.stepIndex || 0), totalSteps - 1);
    const curStepObj = rawSteps[curIdx] || { step: 1, title: 'Adım 1', difficulty: 'Kolay', detail: '' };
    const curStepRiskHtml = buildSafetyBannerHtml(`${curStepObj.title} ${curStepObj.detail}`);

    const stepsHtml = rawSteps.map(s => {
      const stepSafetyHtml = buildSafetyBannerHtml(`${s.title} ${s.detail}`);
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
            <p class="text-xs text-gray-200">Bu adımın işe yaradığı donanım etiketinizle (<strong>${escapeHTML(extractShortHardwareTag())}</strong>) doğrulandı.</p>
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
    const verifyCmdBlock = issue.verify_command ? `
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
    ` : '';

    // Check critical system safety warning (BIOS / TPM / Secure Boot / regedit / bcdedit / DDU)
    const combinedRiskText = `${issue.title} ${issue.error_code} ${issue.ai_root_cause} ${issue.verify_command || ''} ${(issue.ai_solution_steps || []).map(x => x.title + ' ' + x.detail).join(' ')}`;
    const safetyBannerHtml = buildSafetyBannerHtml(combinedRiskText);

    // Compute voting stats
    const upVotes = Number(issue.helpful_votes || 10);
    const baseSr = Number(issue.success_rate || 95);
    const downVotes = Number(issue.unhelpful_votes != null ? issue.unhelpful_votes : Math.max(2, Math.round(upVotes * (100 - baseSr) / Math.max(baseSr, 1))));
    const totalVotes = Number(issue.total_votes || (upVotes + downVotes));
    const currentSr = Math.round((upVotes / Math.max(1, totalVotes)) * 100);

    const activeVote = issue.user_vote || localVotes[`issue_${issue.id}`] || (issue.user_voted ? 'up' : null);
    const upBtnClass = activeVote === 'up'
      ? 'vote-btn-active font-bold'
      : 'bg-white/5 hover:bg-[#5e9c88]/20 text-gray-200 border-white/10';
    const downBtnClass = activeVote === 'down'
      ? 'bg-red-500/25 border-red-400/50 text-red-200 font-bold'
      : 'bg-white/5 hover:bg-red-500/15 text-gray-300 border-white/10';

    const userHwShort = extractShortHardwareTag();
    const hwTagsList = Array.isArray(issue.verified_hw_tags) && issue.verified_hw_tags.length > 0
      ? issue.verified_hw_tags
      : [userHwShort, 'Win 11 / RTX 3060', 'Win 10 / RX 6600'];
    const hwBadgesHtml = hwTagsList.slice(0, 3).map(tag => `
      <span class="text-[11px] font-semibold px-2.5 py-0.5 rounded-lg bg-[#5e9c88]/15 text-[#a3d9c6] border border-[#5e9c88]/30">
        👍 Bu çözüm işe yaradı (${escapeHTML(tag)})
      </span>
    `).join('');

    return `
      <article id="issueCard-${issue.id}" class="issue-card p-6 space-y-5 transition-all duration-300">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-xs font-bold px-2.5 py-1 rounded-lg text-white cursor-pointer flex items-center gap-2" style="background-color: ${escapeHTML(issue.accent_color)}" onclick="selectGame('${escapeHTML(issue.game_slug)}')">
              <img
                src="${issue.game_image_url || fallbackCover(issue.game_slug, issue.accent_color)}"
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
            <span class="text-xs px-2.5 py-1 rounded-lg bg-white/5 text-gray-300 border border-white/10">
              ${escapeHTML(issue.category)}
            </span>
          </div>
          <div class="flex items-center gap-2">
            <span id="issueSuccessBadge-${issue.id}" class="text-xs font-bold px-3 py-1 rounded-full bg-[#5e9c88]/15 text-[#a3d9c6] border border-[#5e9c88]/30">
              ✓ %${currentSr} Başarı (${totalVotes} Oy)
            </span>
          </div>
        </div>

        <div class="space-y-1.5">
          <h3 class="text-lg sm:text-xl font-extrabold text-white">${escapeHTML(issue.title)}</h3>
          <p class="text-sm text-gray-300">${escapeHTML(issue.symptom_summary)}</p>
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
        </div>

        <div class="space-y-3">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div class="text-xs font-bold uppercase tracking-wider text-gray-300">
              🛠️ Adım Adım Kesin Çözüm Rehberi
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

        <!-- Solution Verification & Hardware-Tagged Upvote/Downvote Component -->
        <div class="pt-4 border-t border-white/10 space-y-3">
          <div class="flex flex-wrap items-center gap-2" id="issueHwTags-${issue.id}">
            ${hwBadgesHtml}
          </div>
          <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
            <div class="flex flex-wrap items-center gap-2.5">
              <span class="text-xs font-bold text-gray-200">Bu çözüm çalıştı mı?</span>
              <button
                type="button"
                id="issueUpBtn-${issue.id}"
                onclick="voteIssue(${issue.id}, 'up')"
                class="px-3.5 py-1.5 rounded-xl border text-xs flex items-center gap-1.5 transition ${upBtnClass}"
              >
                <span>👍 Bu çözüm işe yaradı (${escapeHTML(userHwShort)})</span>
                <span id="issueUpCount-${issue.id}" class="font-bold">(${upVotes})</span>
              </button>
              <button
                type="button"
                id="issueDownBtn-${issue.id}"
                onclick="voteIssue(${issue.id}, 'down')"
                class="px-3.5 py-1.5 rounded-xl border text-xs flex items-center gap-1.5 transition ${downBtnClass}"
              >
                <span>👎 Hayır</span>
                <span id="issueDownCount-${issue.id}" class="font-bold">(${downVotes})</span>
              </button>
              <span id="issueRateInline-${issue.id}" class="text-xs font-semibold text-[#88c0a8]">
                • %${currentSr} Başarı (${totalVotes} Oy)
              </span>
              <span class="text-xs text-gray-400 hidden sm:inline">• 👁️ ${issue.views.toLocaleString('tr-TR')} görüntülenme</span>
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
    const hwTagsContainer = document.getElementById(`issueHwTags-${issueId}`);

    const totalVotes = data.total_votes || ((data.helpful_votes || 0) + (data.unhelpful_votes || 0));
    const sr = data.success_rate || 95;

    if (upCountEl) upCountEl.textContent = `(${data.helpful_votes})`;
    if (downCountEl) downCountEl.textContent = `(${data.unhelpful_votes || 0})`;
    if (badgeEl) badgeEl.textContent = `✓ %${sr} Başarı (${totalVotes} Oy)`;
    if (inlineEl) inlineEl.textContent = `• %${sr} Başarı (${totalVotes} Oy)`;

    if (Array.isArray(data.verified_hw_tags) && hwTagsContainer) {
      hwTagsContainer.innerHTML = data.verified_hw_tags.slice(0, 3).map(tag => `
        <span class="text-[11px] font-semibold px-2.5 py-0.5 rounded-lg bg-[#5e9c88]/15 text-[#a3d9c6] border border-[#5e9c88]/30">
          👍 Bu çözüm işe yaradı (${escapeHTML(tag)})
        </span>
      `).join('');
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
      found.helpful_votes = data.helpful_votes;
      found.unhelpful_votes = data.unhelpful_votes;
      found.total_votes = totalVotes;
      found.success_rate = sr;
      found.user_vote = data.user_vote;
      if (Array.isArray(data.verified_hw_tags)) {
        found.verified_hw_tags = data.verified_hw_tags;
      }
    }

    if (data.user_vote === 'up') {
      showToast(`👍 Bu çözüm işe yaradı (${userHwTag}) olarak doğrulandı!`);
    } else if (data.user_vote === 'down') {
      showToast('👎 Geri bildiriminiz kaydedildi. Alternatif çözüm için AI Çözümleyiciyi kullanabilirsiniz.');
    } else {
      showToast('Oyunuz geri alındı.');
    }
  }
}

function renderAiReportVoteBar(reportKey, initialConfidence = 96, isGuestTrial = false) {
  const bar = document.getElementById('aiResultVoteBar');
  if (!bar) return;
  const localVotes = getLocalVoteMap();
  const currentChoice = localVotes[`ai_${reportKey}`] || null;
  const baseUp = 48 + (currentChoice === 'up' ? 1 : 0);
  const baseDown = 2 + (currentChoice === 'down' ? 1 : 0);
  const total = baseUp + baseDown;
  const sr = Math.round((baseUp / total) * 100);
  const userHwTag = extractShortHardwareTag();

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
          <span class="text-xs font-bold text-white">Bu AI çözümü çalıştı mı?</span>
          <button
            type="button"
            onclick="voteAiReport('${escapeHTML(reportKey)}', 'up')"
            class="px-3.5 py-1.5 rounded-xl border text-xs flex items-center gap-1.5 transition ${upClass}"
          >
            <span>👍 Bu çözüm işe yaradı (${escapeHTML(userHwTag)}) (${baseUp})</span>
          </button>
          <button
            type="button"
            onclick="voteAiReport('${escapeHTML(reportKey)}', 'down')"
            class="px-3.5 py-1.5 rounded-xl border text-xs flex items-center gap-1.5 transition ${downClass}"
          >
            <span>👎 Hayır (${baseDown})</span>
          </button>
        </div>
        <span class="text-xs font-bold px-3 py-1 rounded-full bg-[#5e9c88]/15 text-[#a3d9c6] border border-[#5e9c88]/30">
          ✓ %${sr} Başarı (${total} Oy)
        </span>
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
    confEl.textContent = `✓ %${data.confidence || 96} Çözüm Başarısı`;

    const safetyHtml = buildSafetyBannerHtml(`${payload.error_code} ${payload.problem_description} ${data.markdown}`);
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
    renderAiReportVoteBar(reportKey, data.confidence || 96, Boolean(data.guest_trial_used || !STATE.currentUser));

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
  document.getElementById('threadsCountBadge').textContent = STATE.threads.length;
  renderThreads();
}

function renderThreads() {
  const container = document.getElementById('threadsListContainer');
  if (STATE.threads.length === 0) {
    container.innerHTML = `
      <div class="bg-[#1d2430] border border-white/10 rounded-2xl p-8 text-center space-y-3">
        <div class="text-base font-bold text-white">Bu oyun ekranında henüz soru sorulmamış</div>
        <p class="text-xs text-gray-400">İlk soruyu siz sorun, GameFix AI saniyeler içinde çözüm yanıtını oluştursun!</p>
        <button onclick="openAskModal()" class="accent-btn px-4 py-2 rounded-xl text-xs">+ İlk Soruyu Sor</button>
      </div>
    `;
    return;
  }

  container.innerHTML = STATE.threads.map(t => {
    const repliesHtml = (t.replies || []).map(rep => {
      if (rep.is_ai) {
        const repSafetyHtml = buildSafetyBannerHtml(`${t.error_code || ''} ${t.title || ''} ${rep.content || ''}`);
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
            <p class="text-xs sm:text-sm text-gray-200">${escapeHTML(rep.content)}</p>
          </div>
        `;
      }
    }).join('');

    const voteBtnClass = t.user_voted ? 'vote-btn-active' : 'bg-white/5 hover:bg-white/10 text-gray-200';
    const voteBtnLabel = t.user_voted ? '✓ Faydalı Konu (Oylandı)' : '▲ Faydalı Konu';
    const safeThreadTitlePreview = escapeHTML((t.title || '').slice(0, 50)).replace(/'/g, "\\'");

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
              <img
                src="${t.game_image_url || fallbackCover(t.game_slug, t.accent_color)}"
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
          <p class="text-xs sm:text-sm text-gray-300 leading-relaxed">${escapeHTML(t.content)}</p>
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
                <span id="threadVote-${t.id}">(${Number(t.upvotes || 0)})</span>
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

    if (countEl) countEl.textContent = `(${data.upvotes})`;
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
        showToast('Sorunuz yayınlandı ve GameFix AI tarafından yanıtlandı!');
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
