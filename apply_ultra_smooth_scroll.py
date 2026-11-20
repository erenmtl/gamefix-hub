# -*- coding: utf-8 -*-
"""
OyunÇöz Ultra Akıcı Kaydırma (Scroll Jank / Lag Eliminator) & Cache-Buster Betiği:
1. static/styles.css:
   - Mid-scroll layout sıçraması yaratan content-visibility: auto kuralını kaldırır.
   - body ve .oc-hero-glow üzerindeki büyük radial-gradient boyamalarını kaldırıp saf GPU-dostu solid yüzey (#0b101b / #141f35) kullanır.
   - Tüm sayfada backdrop-filter / blur efektlerini tamamen devre dışı bırakır.
   - Kartların üzerinde fare dururken kaydırma yapıldığında GPU katmanı oluşturup yıkan hover transform: translateY() ve box-shadow efektlerini kaldırır; yalnızca hafif border-color değişimi bırakır.
2. index.html:
   - <main> dışındaki 380 satırlık mükerrer #populerCozumRehberleri bloğunu kaldırarak ~350 gereksiz DOM düğümünü temizler.
   - Sürekli 60fps repaint tetikleyen animate-pulse sınıfını kaldırır.
3. static/app.js ve static/ui_components.js:
   - İlk sayfa açılışında gizli olan #tabContent-issues içerisine 51 hata rehberinin (~1.800 DOM düğümü) ve gizli olan #gamesMegaPanel içerisine 31 oyun kartının peşinen basılmasını engeller; yalnızca kullanıcı ilgili sekmeyi/paneli açtığında (on-demand) render eder.
4. Tüm HTML dosyalarında styles.css, ui_components.js, seed_data.js ve app.js bağlantılarına ?v=20261120v4 önbellek kırıcı (cache-buster) ekler.
"""
import os
import re

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_VER = "20261120v4"


def optimize_styles_css():
    css_path = os.path.join(ROOT_DIR, "static", "styles.css")
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    marker = "/* ─── GÖRSEL ZENGİNLEŞTİRME"
    if marker in css:
        css = css[:css.index(marker)]

    ultra_fast_css = """/* ─── GÖRSEL ZENGİNLEŞTİRME & SIFIR GECİKMELİ (ZERO-JANK) KAYDIRMA OPTİMİZASYONU ───
   - Büyük radial-gradient arka planlar, backdrop-filter blur ve kart gölge/transform
     animasyonları kaldırılarak kaydırma sırasında CPU/GPU boyama maliyeti sıfırlandı.
   ──────────────────────────────────────────────────────────────────────────────── */
body {
  background-color: #0b101b !important;
  background-image: none !important;
}

*,
*::before,
*::after {
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

header.sticky,
#mobileStickyActionBar {
  background-color: #0e1524 !important;
}

.oc-brand-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.85rem;
  background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%);
  border: 1px solid rgba(255, 255, 255, 0.22);
  flex-shrink: 0;
}

.oc-card,
.issue-card,
.gamer-hud-card,
.showcase-card,
.hero-banner {
  background-color: #131c2e !important;
  background-image: none !important;
  border: 1px solid rgba(148, 163, 184, 0.18) !important;
  box-shadow: none !important;
  transition: border-color 0.12s linear !important;
}

.oc-card-interactive {
  position: relative;
  overflow: hidden;
  transition: border-color 0.12s linear !important;
}

.oc-card-interactive:hover {
  transform: none !important;
  border-color: rgba(52, 211, 153, 0.65) !important;
  box-shadow: none !important;
}

.oc-hero-glow {
  position: relative;
  overflow: hidden;
  background-color: #152036 !important;
  background-image: none !important;
  border: 1px solid rgba(52, 211, 153, 0.35) !important;
}

.oc-gradient-text {
  color: #34d399;
}

.oc-btn-primary {
  background-color: #10b981 !important;
  background-image: none !important;
  color: #ffffff !important;
  border: 1px solid rgba(52, 211, 153, 0.45) !important;
  box-shadow: none !important;
}

.oc-btn-primary:hover {
  background-color: #059669 !important;
}

.oc-monogram {
  color: #ffffff !important;
  font-weight: 800 !important;
  letter-spacing: -0.03em;
  box-shadow: none !important;
}

.oc-cat-bento {
  position: relative;
  overflow: hidden;
  border-radius: 1rem;
  padding: 1rem;
  background-color: #101828;
  border: 1px solid rgba(148, 163, 184, 0.18);
  transition: border-color 0.12s linear;
}

.oc-cat-bento:hover {
  transform: none;
  background-color: #162238;
  border-color: rgba(52, 211, 153, 0.5);
}
"""
    css = css.rstrip() + "\n\n" + ultra_fast_css
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(css)
    print("[OK] Optimized static/styles.css for zero-repaint scrolling")


def optimize_index_html():
    idx_path = os.path.join(ROOT_DIR, "index.html")
    with open(idx_path, "r", encoding="utf-8") as f:
        txt = f.read()

    # 1. Remove animate-pulse
    txt = txt.replace(" animate-pulse", "")

    # 2. Remove the duplicate 380-line #populerCozumRehberleri block outside <main>
    dup_marker = "  <!-- PROGRAMATİK STATİK SEO REHBERLERİ DİZİNİ (/cozum/ 30 POPÜLER OYUN HATASI) -->"
    footer_marker = "  <!-- SEO-OPTIMIZED & LEGALLY COMPLIANT SEMANTIC FOOTER -->"
    if dup_marker in txt and footer_marker in txt:
        s_idx = txt.index(dup_marker)
        e_idx = txt.index(footer_marker)
        txt = txt[:s_idx] + txt[e_idx:]
        print("[OK] Removed duplicate 380-line #populerCozumRehberleri block outside <main> in index.html")

    with open(idx_path, "w", encoding="utf-8") as f:
        f.write(txt)


def optimize_js_lazy_dom():
    app_path = os.path.join(ROOT_DIR, "static", "app.js")
    with open(app_path, "r", encoding="utf-8") as f:
        app_txt = f.read()

    # 1. Remove animate-pulse from updateHeroBanner
    app_txt = app_txt.replace(" animate-pulse", "")

    # 2. Defer renderIssues() when #tabContent-issues is hidden so 1,800 hidden DOM nodes aren't created on homepage boot
    old_render_issues_start = """function renderIssues() {
  const container = document.getElementById('issuesListContainer') || document.getElementById('issuesContainer');
  if (!container) return;"""

    new_render_issues_start = """function renderIssues(forceRender = false) {
  const container = document.getElementById('issuesListContainer') || document.getElementById('issuesContainer');
  if (!container) return;
  const tabSec = document.getElementById('tabContent-issues');
  if (!forceRender && tabSec && tabSec.classList.contains('hidden')) {
    container._needsRender = true;
    return;
  }
  container._needsRender = false;"""

    if old_render_issues_start in app_txt:
        app_txt = app_txt.replace(old_render_issues_start, new_render_issues_start, 1)

    # 3. Also in switchTab, when switching to 'issues', trigger renderIssues(true) if needed
    old_switch_tab = """  const catWrapper = document.getElementById('categoryFilterWrapper');"""
    new_switch_tab = """  if (normalized === 'issues') {
    const ic = document.getElementById('issuesListContainer') || document.getElementById('issuesContainer');
    if (ic && (ic._needsRender || ic.children.length === 0)) {
      renderIssues(true);
    }
  }
  const catWrapper = document.getElementById('categoryFilterWrapper');"""

    if old_switch_tab in app_txt and "ic._needsRender" not in app_txt:
        app_txt = app_txt.replace(old_switch_tab, new_switch_tab, 1)

    # 4. Also update tabCountIssues badge when issues are fetched
    old_badge_update = """  const badgeEl = document.getElementById('issuesCountBadge');
  if (badgeEl) {
    badgeEl.textContent = STATE.issues.length > 0 ? String(STATE.issues.length) : '';
    badgeEl.classList.toggle('hidden', STATE.issues.length === 0);
  }"""
    new_badge_update = """  const badgeEl = document.getElementById('issuesCountBadge') || document.getElementById('tabCountIssues');
  if (badgeEl) {
    badgeEl.textContent = String(STATE.issues.length);
  }"""
    if old_badge_update in app_txt:
        app_txt = app_txt.replace(old_badge_update, new_badge_update, 1)

    # 5. Defer renderSidebarGames() while #gamesMegaPanel is hidden, and render on toggleGamesNavPanel(true)
    old_render_sidebar = """function renderSidebarGames() {
  const container = document.getElementById('gameNavList');"""
    new_render_sidebar = """window.renderSidebarGames = renderSidebarGames;
function renderSidebarGames(forceRender = false) {
  const container = document.getElementById('gameNavList');
  if (!container) return;
  const megaPanel = document.getElementById('gamesMegaPanel');
  if (!forceRender && megaPanel && megaPanel.classList.contains('hidden')) {
    container._needsRender = true;
    return;
  }
  container._needsRender = false;"""
    if old_render_sidebar in app_txt:
        app_txt = app_txt.replace(old_render_sidebar, new_render_sidebar, 1)

    with open(app_path, "w", encoding="utf-8") as f:
        f.write(app_txt)

    # In static/ui_components.js, when toggleGamesNavPanel opens the panel, call window.renderSidebarGames(true) if needed
    ui_path = os.path.join(ROOT_DIR, "static", "ui_components.js")
    with open(ui_path, "r", encoding="utf-8") as f:
        ui_txt = f.read()

    old_toggle_games = """    if (willOpen) {
      panel.classList.remove('hidden');"""
    new_toggle_games = """    if (willOpen) {
      panel.classList.remove('hidden');
      const gList = document.getElementById('gameNavList');
      if (gList && (gList._needsRender || gList.children.length === 0) && typeof window.renderSidebarGames === 'function') {
        window.renderSidebarGames(true);
      }"""
    if old_toggle_games in ui_txt and "window.renderSidebarGames(true)" not in ui_txt:
        ui_txt = ui_txt.replace(old_toggle_games, new_toggle_games, 1)
        with open(ui_path, "w", encoding="utf-8") as f:
            f.write(ui_txt)

    print("[OK] Enabled lazy on-demand DOM rendering for hidden #issuesListContainer and #gameNavList")


def add_cache_busters_everywhere():
    updated_files = 0
    for root, dirs, files in os.walk(ROOT_DIR):
        if ".git" in dirs:
            dirs.remove(".git")
        for fname in files:
            if not fname.endswith((".html", ".py")):
                continue
            if fname == "apply_ultra_smooth_scroll.py":
                continue
            fpath = os.path.join(root, fname)
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                txt = f.read()
            orig = txt
            for asset in ("styles.css", "ui_components.js", "seed_data.js", "app.js"):
                txt = re.sub(
                    rf"(static/{re.escape(asset)})(?:\?v=[a-zA-Z0-9_.-]+)?",
                    rf"\1?v={CACHE_VER}",
                    txt,
                )
            if txt != orig:
                with open(fpath, "w", encoding="utf-8") as wf:
                    wf.write(txt)
                updated_files += 1
    print(f"[OK] Added ?v={CACHE_VER} cache-buster to static assets in {updated_files} files")


if __name__ == "__main__":
    optimize_styles_css()
    optimize_index_html()
    optimize_js_lazy_dom()
    add_cache_busters_everywhere()
