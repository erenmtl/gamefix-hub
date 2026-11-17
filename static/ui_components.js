/**
 * OyunÇöz Merkezi UI Bileşen Kütüphanesi ve SVG İkon Sistemi (Aşama 1)
 * - İkon Seti: Lucide Icons (ISC Lisansı - Açık Kaynak)
 * - Oyun Rozetleri: Telifsiz Özgün Monogram / Harf Rozeti Sistemi
 * - Ortak Bileşenler: Button, Card, Badge, Alert, CodeBlock, Accordion, Tabs, Breadcrumb
 */
(function () {
  'use strict';

  const LUCIDE_PATHS = {
    search: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    check: '<path d="M20 6 9 17l-5-5"/>',
    'check-circle': '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/>',
    'alert-triangle': '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    'alert-circle': '<circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/>',
    info: '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
    copy: '<rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>',
    terminal: '<polyline points="4 17 10 11 4 5"/><line x1="12" x2="20" y1="19" y2="19"/>',
    shield: '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>',
    'chevron-down': '<path d="m6 9 6 6 6-6"/>',
    'chevron-right': '<path d="m9 18 6-6-6-6"/>',
    'external-link': '<path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
    'thumbs-up': '<path d="M7 10v12"/><path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2a3.13 3.13 0 0 1 3 3.88Z"/>',
    'thumbs-down': '<path d="M17 14V2"/><path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22a3.13 3.13 0 0 1-3-3.88Z"/>',
    cpu: '<rect width="16" height="16" x="4" y="4" rx="2"/><rect width="6" height="6" x="9" y="9" rx="1"/><path d="M15 2v2"/><path d="M15 20v2"/><path d="M2 15h2"/><path d="M2 9h2"/><path d="M20 15h2"/><path d="M20 9h2"/><path d="M9 2v2"/><path d="M9 20v2"/>',
    'file-text': '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/>',
    'message-square': '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    wrench: '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
    menu: '<line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/>',
    x: '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>'
  };

  function renderOcIcon(name, className) {
    const cls = className || 'w-4 h-4';
    const path = LUCIDE_PATHS[name] || LUCIDE_PATHS.info;
    return `<svg class="${cls} shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${path}</svg>`;
  }

  const GAME_MONOGRAM_MAP = {
    valorant: { code: 'VAL', color: '#b85d66' },
    cs2: { code: 'CS2', color: '#b88b52' },
    'counter-strike-2': { code: 'CS2', color: '#b88b52' },
    lol: { code: 'LoL', color: '#5586ad' },
    'league-of-legends': { code: 'LoL', color: '#5586ad' },
    'gtav-fivem': { code: 'GTA', color: '#589471' },
    'gta-v': { code: 'GTA', color: '#589471' },
    fivem: { code: 'FVM', color: '#589471' },
    fc25: { code: 'FC25', color: '#5e9c88' },
    'fc-25': { code: 'FC25', color: '#5e9c88' },
    minecraft: { code: 'MC', color: '#6c9a5c' },
    'cod-warzone': { code: 'WZ', color: '#a87954' },
    rust: { code: 'RST', color: '#b06655' },
    'apex-legends': { code: 'APX', color: '#ab5c65' },
    'cyberpunk-2077': { code: 'CP77', color: '#afa055' },
    'elden-ring': { code: 'ER', color: '#a68253' },
    pubg: { code: 'PUBG', color: '#b37a52' },
    'victoria-3': { code: 'VIC3', color: '#8c6d53' },
    'hearts-of-iron-4': { code: 'HOI4', color: '#6f7f65' },
    'mount-and-blade-2-bannerlord': { code: 'M&B2', color: '#a67b4b' },
    bannerlord: { code: 'M&B2', color: '#a67b4b' },
    'red-dead-redemption-2': { code: 'RDR2', color: '#a85751' },
    rdr2: { code: 'RDR2', color: '#a85751' },
    'baldurs-gate-3': { code: 'BG3', color: '#946b88' },
    'euro-truck-simulator-2': { code: 'ETS2', color: '#58829e' },
    'forza-horizon-5': { code: 'FH5', color: '#b36b82' },
    'helldivers-2': { code: 'HD2', color: '#a89552' },
    'rainbow-six-siege': { code: 'R6S', color: '#58789e' },
    'football-manager-2024': { code: 'FM24', color: '#7b659e' },
    'black-myth-wukong': { code: 'WKG', color: '#9e7c58' },
    wukong: { code: 'WKG', color: '#9e7c58' },
    palworld: { code: 'PAL', color: '#58949e' },
    'dota-2': { code: 'DOTA', color: '#a65852' },
    'escape-from-tarkov': { code: 'EFT', color: '#827c68' },
    'the-witcher-3': { code: 'TW3', color: '#b05c52' },
    'god-of-war-ragnarok': { code: 'GOW', color: '#4f84ad' },
    'overwatch-2': { code: 'OW2', color: '#bd7b48' },
    'diablo-iv': { code: 'DIV', color: '#9e4f4f' }
  };

  function getGameMonogramInfo(slugOrName, customColor) {
    const raw = String(slugOrName || 'OYUN').trim();
    const key = raw.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    if (GAME_MONOGRAM_MAP[key]) {
      return {
        code: GAME_MONOGRAM_MAP[key].code,
        color: customColor || GAME_MONOGRAM_MAP[key].color
      };
    }
    const words = raw.split(/[\s\-_:/]+/).filter(Boolean);
    let code = 'OYN';
    if (words.length >= 2) {
      code = words.slice(0, 3).map(w => w[0]).join('').toUpperCase();
    } else if (words.length === 1) {
      code = words[0].slice(0, 3).toUpperCase();
    }
    return { code, color: customColor || '#5e9c88' };
  }

  function makeGameMonogramSvgDataUri(slugOrName, accentColor) {
    const info = getGameMonogramInfo(slugOrName, accentColor);
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="160" height="96" viewBox="0 0 160 96">
      <rect width="160" height="96" rx="16" fill="#18202c"/>
      <rect x="2" y="2" width="156" height="92" rx="14" fill="none" stroke="${info.color}" stroke-opacity="0.45" stroke-width="2"/>
      <text x="80" y="57" text-anchor="middle" fill="#e6ecf5" font-family="Inter, Segoe UI, sans-serif" font-weight="800" font-size="28" letter-spacing="1">${info.code}</text>
    </svg>`;
    return 'data:image/svg+xml;utf8,' + encodeURIComponent(svg);
  }

  function renderGameMonogramBadge(slugOrName, sizeClass, accentColor) {
    const info = getGameMonogramInfo(slugOrName, accentColor);
    const sz = sizeClass || '';
    return `<span class="oc-monogram ${sz}" style="border-color:${info.color}66;background-color:${info.color}1f" aria-hidden="true">${info.code}</span>`;
  }

  // 8 Ortak Bileşen Yardımcıları
  const OC_UI = {
    Button: function ({ label, variant = 'primary', icon = '', onClick = '', href = '', type = 'button', extraClass = '' }) {
      const vClass = variant === 'secondary' ? 'oc-btn-secondary' : (variant === 'ghost' ? 'oc-btn-ghost' : 'oc-btn-primary');
      const iconHtml = icon ? renderOcIcon(icon, 'w-4 h-4') : '';
      if (href) {
        return `<a href="${href}" class="oc-btn ${vClass} ${extraClass}">${iconHtml}<span>${label}</span></a>`;
      }
      const clickAttr = onClick ? `onclick="${onClick}"` : '';
      return `<button type="${type}" ${clickAttr} class="oc-btn ${vClass} ${extraClass}">${iconHtml}<span>${label}</span></button>`;
    },
    Badge: function ({ text, variant = 'default', icon = '' }) {
      const vClass = variant === 'accent' ? 'oc-badge-accent' : (variant === 'success' ? 'oc-badge-success' : (variant === 'warning' ? 'oc-badge-warning' : ''));
      const iconHtml = icon ? renderOcIcon(icon, 'w-3.5 h-3.5') : '';
      return `<span class="oc-badge ${vClass}">${iconHtml}<span>${text}</span></span>`;
    },
    Alert: function ({ title = '', message = '', variant = 'info' }) {
      const iconMap = { info: 'info', warning: 'alert-triangle', danger: 'alert-circle', success: 'check-circle' };
      const iconHtml = renderOcIcon(iconMap[variant] || 'info', 'w-5 h-5 mt-0.5');
      return `<div class="oc-alert oc-alert-${variant}" role="status">${iconHtml}<div>${title ? `<strong class="block font-bold mb-0.5">${title}</strong>` : ''}<span>${message}</span></div></div>`;
    }
  };

  window.renderOcIcon = renderOcIcon;
  window.getGameMonogramInfo = getGameMonogramInfo;
  window.makeGameCoverDataUri = makeGameMonogramSvgDataUri;
  window.renderGameMonogramBadge = renderGameMonogramBadge;
  window.OC_UI = OC_UI;

  // --- AŞAMA 2: ÜST MENÜ, OYUNLAR AÇILIR PANELİ, ARAÇLAR MENÜSÜ VE MOBİL ÇEKMECE KONTROLLERİ ---
  window.toggleGamesNavPanel = function (forceState) {
    const panel = document.getElementById('gamesMegaPanel');
    const btn = document.getElementById('navGamesToggleBtn');
    if (!panel) return;
    const willOpen = typeof forceState === 'boolean' ? forceState : panel.classList.contains('hidden');
    panel.classList.toggle('hidden', !willOpen);
    if (btn) btn.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
    if (willOpen) {
      window.toggleToolsDropdown(false);
      const searchInp = document.getElementById('gamesDrawerSearchInput');
      if (searchInp) setTimeout(() => searchInp.focus(), 50);
    }
  };

  window.filterDrawerGames = function (query) {
    const q = String(query || '').trim().toLowerCase();
    const list = document.getElementById('gameNavList');
    if (!list) return;
    const items = list.querySelectorAll('button, a, .game-nav-item');
    items.forEach(el => {
      const txt = (el.textContent || '').toLowerCase();
      el.style.display = (!q || txt.includes(q)) ? '' : 'none';
    });
  };

  window.toggleToolsDropdown = function (forceState) {
    const menu = document.getElementById('navToolsDropdown');
    const btn = document.getElementById('navToolsToggleBtn');
    if (!menu) return;
    const willOpen = typeof forceState === 'boolean' ? forceState : menu.classList.contains('hidden');
    menu.classList.toggle('hidden', !willOpen);
    if (btn) btn.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
    if (willOpen) {
      const gPanel = document.getElementById('gamesMegaPanel');
      if (gPanel) gPanel.classList.add('hidden');
    }
  };

  window.toggleMobileNavDrawer = function (forceState) {
    const drawer = document.getElementById('mobileNavDrawer');
    const btn = document.getElementById('mobileDrawerToggleBtn');
    if (!drawer) return;
    const willOpen = typeof forceState === 'boolean' ? forceState : drawer.classList.contains('hidden');
    drawer.classList.toggle('hidden', !willOpen);
    if (btn) btn.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
  };

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      window.toggleGamesNavPanel(false);
      window.toggleToolsDropdown(false);
      window.toggleMobileNavDrawer(false);
    }
  });

  document.addEventListener('click', function (e) {
    const gPanel = document.getElementById('gamesMegaPanel');
    const gBtn = document.getElementById('navGamesToggleBtn');
    if (gPanel && !gPanel.classList.contains('hidden')) {
      if (!gPanel.contains(e.target) && (!gBtn || !gBtn.contains(e.target))) {
        window.toggleGamesNavPanel(false);
      }
    }
    const tMenu = document.getElementById('navToolsDropdown');
    const tBtn = document.getElementById('navToolsToggleBtn');
    if (tMenu && !tMenu.classList.contains('hidden')) {
      if (!tMenu.contains(e.target) && (!tBtn || !tBtn.contains(e.target))) {
        window.toggleToolsDropdown(false);
      }
    }
  });
})();
