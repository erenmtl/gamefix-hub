// GameFix AI Hub Frontend Controller (v3.0 - AI Smart Cache, Email OTP Verification & Member-Only AI Lock)

function getOrCreateClientId() {
  let cid = localStorage.getItem('gamefix_client_id');
  if (!cid) {
    cid = 'cid_' + Math.random().toString(36).substring(2) + '_' + Date.now().toString(36);
    localStorage.setItem('gamefix_client_id', cid);
  }
  return cid;
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
  pendingVerifyEmail: ''
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
  await checkCurrentSession();
  await fetchStatus();
  await fetchGames();
  await refreshRandomSuggestions();
  await applyUrlSeoParams();
  await Promise.all([fetchIssues(), fetchThreads()]);
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

function formatSimpleMarkdown(md) {
  if (!md) return '';
  let html = md
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  html = html.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, (_, lang, code) => {
    return `<pre><code>${code.trim()}</code></pre>`;
  });

  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
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
      if (trimmed.startsWith('<h3') || trimmed.startsWith('<pre') || trimmed.startsWith('<hr') || trimmed.startsWith('<blockquote')) {
        out.push(trimmed);
      } else if (trimmed.length > 0) {
        out.push(`<p>${trimmed}</p>`);
      }
    }
  }
  if (inList) out.push(`</${inList}>`);

  return out.join('\n');
}

// --- SMART GAME RECOGNITION & RANDOM WORLD SUGGESTIONS ---

async function refreshRandomSuggestions() {
  try {
    const res = await fetch('/api/games/suggestions?count=6');
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
  return `/api/games/cover/${slug}`;
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

function updateAuthUI() {
  const guestArea = document.getElementById('guestAuthArea');
  const userArea = document.getElementById('userProfileArea');
  const aiGuestLock = document.getElementById('aiLabGuestLock');
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

    if (aiGuestLock) aiGuestLock.classList.remove('hidden');
  }
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
  const btn = document.getElementById('sendCodeBtn');
  const origText = btn.textContent;
  btn.disabled = true;
  btn.textContent = '⏳ Kod Gönderiliyor...';

  const payload = {
    username: document.getElementById('regUsername').value.trim(),
    email: document.getElementById('regEmail').value.trim(),
    password: document.getElementById('regPassword').value,
    system_specs: document.getElementById('regSpecs').value.trim(),
    favorite_game: STATE.selectedGame !== 'all' ? STATE.selectedGame : 'valorant'
  };

  try {
    const res = await fetch('/api/auth/send-code', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
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

  const res = await fetch('/api/auth/profile', {
    method: 'PUT',
    headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ system_specs, favorite_game })
  });
  if (res.ok) {
    const data = await res.json();
    STATE.currentUser = data.user;
    document.getElementById('aiLabSpecs').value = data.user.system_specs || '';
    closeProfileModal();
    showToast('Profil ve sistem bilgileriniz güncellendi!');
  }
}

async function logoutUser() {
  await fetch('/api/auth/logout', { method: 'POST', headers: getAuthHeaders() });
  STATE.authToken = '';
  STATE.currentUser = null;
  localStorage.removeItem('gamefix_auth_token');
  updateAuthUI();
  closeProfileModal();
  await Promise.all([fetchIssues(), fetchThreads()]);
  showToast('Oturum kapatıldı.');
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
        ? `${STATE.searchQuery} Hatası Çözümü & Rehberi | GameFix AI Hub`
        : 'GameFix AI Hub | Oyun Hata Çözümleri, VAN 9003, CS2 VAC, FPS Artırma & Yapay Zeka Arıza Çözümleyici';
      if (metaDesc) {
        metaDesc.setAttribute(
          'content',
          'Valorant VAN 9003 & VAN 1067, CS2 VAC oturum doğrulama ve Packet Burst, LoL Vanguard VAN 128, GTA V, Minecraft Exit Code 1, Elden Ring ve 45+ popüler oyunun hata çözümleri ve Yapay Zeka arıza çözümleyici.'
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
        document.title = `${game.name} Hata Çözümleri (${tagSummary}) & AI Arıza Rehberi | GameFix AI Hub`;
        if (metaDesc) {
          metaDesc.setAttribute(
            'content',
            `${game.name} (${game.engine}) için en güncel forum sorunları, ${tagSummary} hata kodları, FPS düşmesi, çökme çözümleri ve Yapay Zeka destekli teknik rehber.`
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
          text: (iss.ai_solution || iss.forum_summary || '').replace(/[#*`>_~]/g, '').substring(0, 600)
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

async function selectGame(slug) {
  STATE.selectedGame = slug;
  renderSidebarGames();
  updateHeroBanner();
  await Promise.all([fetchIssues(), fetchThreads()]);
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

function quickSearchTag(tagText) {
  STATE.selectedGame = 'all';
  renderSidebarGames();
  updateHeroBanner();
  filterByTag(tagText);
  window.scrollTo({ top: 180, behavior: 'smooth' });
}

function filterByTag(tagText) {
  const input = document.getElementById('globalSearchInput');
  input.value = tagText;
  STATE.searchQuery = tagText;
  document.getElementById('clearSearchBtn').classList.remove('hidden');
  switchTab('issues');
  fetchIssues();
  updateDynamicSEO();
}

function handleGlobalSearch(val) {
  STATE.searchQuery = val.trim();
  const clearBtn = document.getElementById('clearSearchBtn');
  if (STATE.searchQuery) {
    clearBtn.classList.remove('hidden');
  } else {
    clearBtn.classList.add('hidden');
  }
  fetchIssues();
  fetchThreads();
}

function clearGlobalSearch() {
  document.getElementById('globalSearchInput').value = '';
  STATE.searchQuery = '';
  document.getElementById('clearSearchBtn').classList.add('hidden');
  fetchIssues();
  fetchThreads();
}

function handleCategoryChange(cat) {
  STATE.selectedCategory = cat;
  fetchIssues();
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
            <span>📌 ${f.forum}</span>
            <span class="text-gray-400 font-normal">• ${f.thread}</span>
          </span>
          <span class="text-[11px] px-2 py-0.5 rounded bg-white/5 text-gray-300 font-semibold">▲ ${f.upvotes} Onay</span>
        </div>
        <p class="text-xs text-gray-300 italic">"${f.quote}"</p>
      </div>
    `).join('');

    const stepsHtml = (issue.ai_solution_steps || []).map(s => `
      <div class="flex items-start gap-3.5 bg-[#181e29] p-3.5 rounded-xl border border-white/5">
        <div class="w-7 h-7 rounded-lg accent-btn flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">
          ${s.step}
        </div>
        <div class="flex-1 space-y-1">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <h4 class="text-sm font-bold text-white">${s.title}</h4>
            <span class="text-[11px] px-2 py-0.5 rounded bg-white/5 text-gray-300 border border-white/10">Zorluk: ${s.difficulty}</span>
          </div>
          <p class="text-xs text-gray-300 leading-relaxed">${s.detail}</p>
        </div>
      </div>
    `).join('');

    const verifyCmdBlock = issue.verify_command ? `
      <div class="bg-[#151a23] border border-white/10 rounded-xl p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div class="space-y-0.5 overflow-x-auto">
          <div class="text-[11px] text-gray-400 font-semibold uppercase tracking-wider">PowerShell / CMD Hızlı Kontrol Komutu:</div>
          <code class="text-xs text-[#8fbcbb] font-mono">${issue.verify_command}</code>
        </div>
        <button
          onclick="copyCommand('${issue.verify_command.replace(/'/g, "\\'").replace(/\\/g, "\\\\")}')"
          class="px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/15 text-xs text-white font-medium shrink-0 transition"
        >
          📋 Komutu Kopyala
        </button>
      </div>
    ` : '';

    const voteBtnClass = issue.user_voted ? 'vote-btn-active' : 'bg-white/5 hover:bg-white/10 text-gray-200';
    const voteBtnLabel = issue.user_voted ? '✓ İşime Yaradı (Oylandı)' : '👍 İşime Yaradı';

    return `
      <article class="issue-card p-6 space-y-5">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-xs font-bold px-2.5 py-1 rounded-lg text-white cursor-pointer flex items-center gap-2" style="background-color: ${issue.accent_color}" onclick="selectGame('${issue.game_slug}')">
              <img
                src="${issue.game_image_url || fallbackCover(issue.game_slug, issue.accent_color)}"
                onerror="this.onerror=null;this.src=fallbackCover('${issue.game_slug}','${issue.accent_color}')"
                alt="${issue.game_short_name}"
                class="w-6 h-4 rounded object-cover border border-white/20"
              />
              <span>${issue.game_short_name}</span>
            </span>
            <span class="text-xs font-mono font-bold px-2.5 py-1 rounded-lg bg-white/5 text-[#d9c382] border border-white/10">
              ${issue.error_code}
            </span>
            <span class="text-xs font-semibold px-2.5 py-1 rounded-lg border ${sevClass}">
              Önem: ${issue.severity}
            </span>
            <span class="text-xs px-2.5 py-1 rounded-lg bg-white/5 text-gray-300 border border-white/10">
              ${issue.category}
            </span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs font-bold px-3 py-1 rounded-full bg-[#5e9c88]/15 text-[#a3d9c6] border border-[#5e9c88]/30">
              ✓ %${issue.success_rate} Çözüm Başarısı
            </span>
          </div>
        </div>

        <div class="space-y-1.5">
          <h3 class="text-lg sm:text-xl font-extrabold text-white">${issue.title}</h3>
          <p class="text-sm text-gray-300">${issue.symptom_summary}</p>
        </div>

        <div class="space-y-2">
          <div class="text-xs font-bold uppercase tracking-wider text-[#90a8c8]">
            🌐 Forumlardan Derlenen Kullanıcı Raporları & Çözüm Kaynakları
          </div>
          <div class="grid grid-cols-1 gap-2.5">
            ${forumsHtml}
          </div>
        </div>

        <div class="ai-root-box p-4 space-y-1.5">
          <div class="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#a3d9c6]">
            <span>🤖 Yapay Zeka Kök Neden Analizi (Root Cause)</span>
          </div>
          <p class="text-xs sm:text-sm text-gray-200 leading-relaxed">${issue.ai_root_cause}</p>
        </div>

        <div class="space-y-2.5">
          <div class="text-xs font-bold uppercase tracking-wider text-gray-300">
            🛠️ Adım Adım Kesin Çözüm Rehberi
          </div>
          <div class="space-y-2.5">
            ${stepsHtml}
          </div>
        </div>

        ${verifyCmdBlock}

        <div class="pt-3 border-t border-white/10 flex flex-wrap items-center justify-between gap-3">
          <div class="flex items-center gap-3">
            <button
              id="issueVoteBtn-${issue.id}"
              onclick="voteIssue(${issue.id})"
              class="px-3.5 py-1.5 rounded-xl border border-white/10 text-xs font-semibold flex items-center gap-1.5 transition ${voteBtnClass}"
            >
              <span id="issueVoteText-${issue.id}">${voteBtnLabel}</span>
              <span id="issueVote-${issue.id}" class="font-bold">(${issue.helpful_votes})</span>
            </button>
            <span class="text-xs text-gray-400">👁️ ${issue.views.toLocaleString('tr-TR')} görüntülenme</span>
          </div>

          <button
            onclick="customizeIssueInAiLab('${issue.game_name.replace(/'/g, "\\'")}', '${issue.error_code.replace(/'/g, "\\'")}', '${issue.title.replace(/'/g, "\\'")}')"
            class="px-3.5 py-1.5 rounded-xl bg-white/10 hover:bg-white/15 text-xs font-semibold text-white flex items-center gap-1.5 transition"
          >
            <span>⚡ Bu Sorunu Kendi Sistemime Göre AI İle Özelleştir</span>
          </button>
        </div>
      </article>
    `;
  }).join('');
}

function copyCommand(cmd) {
  navigator.clipboard.writeText(cmd);
  showToast('Komut panoya kopyalandı!');
}

async function voteIssue(issueId) {
  const res = await fetch(`/api/issues/${issueId}/vote`, {
    method: 'POST',
    headers: getAuthHeaders()
  });
  if (res.ok) {
    const data = await res.json();
    const countEl = document.getElementById(`issueVote-${issueId}`);
    const textEl = document.getElementById(`issueVoteText-${issueId}`);
    const btnEl = document.getElementById(`issueVoteBtn-${issueId}`);

    if (countEl) countEl.textContent = `(${data.helpful_votes})`;
    if (data.user_voted) {
      if (textEl) textEl.textContent = '✓ İşime Yaradı (Oylandı)';
      if (btnEl) btnEl.classList.add('vote-btn-active');
      showToast('Oyunuz kaydedildi!');
    } else {
      if (textEl) textEl.textContent = '👍 İşime Yaradı';
      if (btnEl) btnEl.classList.remove('vote-btn-active');
      showToast('Oyunuz geri alındı.');
    }
  }
}

function customizeIssueInAiLab(gameName, errorCode, title) {
  if (!requireMemberAuth('Yapay zeka ile özel çözüm üretmek')) return;
  switchTab('ai-lab');
  document.getElementById('aiLabGameInput').value = gameName;
  previewSmartGameRecognition(gameName, 'aiLabSmartHint');
  document.getElementById('aiLabErrorCode').value = errorCode;
  if (STATE.currentUser && STATE.currentUser.system_specs) {
    document.getElementById('aiLabSpecs').value = STATE.currentUser.system_specs;
  }
  document.getElementById('aiLabDescription').value = `${title} sorununu yaşıyorum. Standart adımları denedim, kendi donanımıma özel detaylı analiz ve çözüm adımlarını istiyorum.`;
  document.getElementById('aiLabSpecs').focus();
  window.scrollTo({ top: 220, behavior: 'smooth' });
}

async function submitAiDiagnostic(e) {
  e.preventDefault();
  if (!requireMemberAuth('Yapay zeka ile çözümleme yapmak')) return;

  const btn = document.getElementById('aiAnalyzeSubmitBtn');
  const origHtml = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '<span>⏳ Oyun Tanınıyor ve Yapay Zeka Çözüm Üretiyor...</span>';

  const payload = {
    game_slug: document.getElementById('aiLabGameInput').value.trim(),
    error_code: document.getElementById('aiLabErrorCode').value,
    system_specs: document.getElementById('aiLabSpecs').value,
    problem_description: document.getElementById('aiLabDescription').value
  };

  try {
    const res = await fetch('/api/ai/analyze', {
      method: 'POST',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) {
      showToast(data.detail || 'Lütfen giriş yapın.');
      if (res.status === 401) openAuthModal('login');
      return;
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
    const contentEl = document.getElementById('aiLabResultContent');

    modeBadge.textContent = data.mode;
    confEl.textContent = `Çözüm Güven Oranı: %${data.confidence || 95}`;
    contentEl.innerHTML = formatSimpleMarkdown(data.markdown);
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

  const res = await fetch(`/api/threads?${params.toString()}`, { headers: getAuthHeaders() });
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
        return `
          <div class="ai-root-box p-4 space-y-2">
            <div class="flex flex-wrap items-center justify-between gap-2 border-b border-[#5e9c88]/20 pb-2">
              <div class="flex items-center gap-2">
                <span class="px-2 py-0.5 rounded bg-[#5e9c88] text-white font-extrabold text-[11px]">AI ÇÖZÜM</span>
                <span class="text-xs font-bold text-[#a3d9c6]">${rep.author_name}</span>
                <span class="text-[11px] text-gray-400">• ${rep.ai_mode || 'Otomatik Teşhis'}</span>
              </div>
              <span class="text-[11px] text-gray-400">${rep.created_at}</span>
            </div>
            <div class="ai-markdown text-xs sm:text-sm leading-relaxed">
              ${formatSimpleMarkdown(rep.content)}
            </div>
          </div>
        `;
      } else {
        return `
          <div class="bg-[#181e29] border border-white/10 rounded-xl p-3.5 space-y-1.5">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-[#a3b8d4]">👤 ${rep.author_name}</span>
              <span class="text-[11px] text-gray-400">${rep.created_at}</span>
            </div>
            <p class="text-xs sm:text-sm text-gray-200">${rep.content}</p>
          </div>
        `;
      }
    }).join('');

    const voteBtnClass = t.user_voted ? 'vote-btn-active' : 'bg-white/5 hover:bg-white/10 text-gray-200';
    const voteBtnLabel = t.user_voted ? '✓ Faydalı Konu (Oylandı)' : '▲ Faydalı Konu';

    return `
      <article class="issue-card p-6 space-y-4">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <div class="flex flex-wrap items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-white/10 text-white font-bold text-xs flex items-center justify-center">
              ${t.author_avatar}
            </div>
            <div>
              <div class="flex items-center gap-2">
                <span class="text-xs font-bold text-white">${t.author_name}</span>
                <span class="text-[11px] text-gray-400">• ${t.created_at}</span>
              </div>
              <div class="text-[11px] text-gray-400">${t.system_specs || 'Sistem belirtilmedi'}</div>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <span class="text-xs font-bold px-2.5 py-1 rounded-lg text-white cursor-pointer flex items-center gap-2" style="background-color: ${t.accent_color}" onclick="selectGame('${t.game_slug}')">
              <img
                src="${t.game_image_url || fallbackCover(t.game_slug, t.accent_color)}"
                onerror="this.onerror=null;this.src=fallbackCover('${t.game_slug}','${t.accent_color}')"
                alt="${t.game_short_name}"
                class="w-6 h-4 rounded object-cover border border-white/20"
              />
              <span>${t.game_short_name}</span>
            </span>
            ${t.error_code ? `<span class="text-xs font-mono px-2.5 py-1 rounded-lg bg-white/5 text-[#d9c382] border border-white/10">${t.error_code}</span>` : ''}
            <span class="text-xs font-semibold px-2.5 py-1 rounded-lg bg-[#5e9c88]/20 text-[#a3d9c6] border border-[#5e9c88]/30">
              ✓ ${t.status}
            </span>
          </div>
        </div>

        <div class="space-y-1.5">
          <h3 class="text-base sm:text-lg font-bold text-white">${t.title}</h3>
          <p class="text-xs sm:text-sm text-gray-300 leading-relaxed">${t.content}</p>
        </div>

        <div class="space-y-3 pt-2">
          ${repliesHtml}
        </div>

        <div class="pt-3 border-t border-white/10 space-y-3">
          <div class="flex items-center justify-between">
            <button
              id="threadVoteBtn-${t.id}"
              onclick="upvoteThread(${t.id})"
              class="px-3.5 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 border border-white/10 transition ${voteBtnClass}"
            >
              <span id="threadVoteText-${t.id}">${voteBtnLabel}</span>
              <span id="threadVote-${t.id}">(${t.upvotes})</span>
            </button>
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

  const res = await fetch(`/api/threads/${threadId}/replies`, {
    method: 'POST',
    headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ content })
  });
  if (res.ok) {
    showToast('Yanıtınız foruma eklendi!');
    await fetchThreads();
  }
}

async function upvoteThread(threadId) {
  const res = await fetch(`/api/threads/${threadId}/upvote`, {
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
    content: document.getElementById('modalThreadContent').value
  };

  try {
    const res = await fetch('/api/threads', {
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
