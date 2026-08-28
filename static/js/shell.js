// Shell mode — this page has header, sidebar, and iframe.
// Click interception in initSidebarMenu().
// Iframe load → pushState. Popstate → set iframe.src (no pushState on load).

var _initialLoad = true;
var _popstateNav = false;

document.addEventListener('DOMContentLoaded', function() {
    initGoto();
    initClock();
    initLogout();
    setcolor();
    initTabLabel();
    initIframeNav();
    initSidebarMenu();
    initPopup();
    initAgentCtx();
});

// ====== Handle ?goto= in URL（来自 base.html 的 redirect） ======
function initGoto() {
    var m = window.location.search.match(/[?&]goto=([^&]*)/);
    if (m) {
        history.replaceState({ url: decodeURIComponent(m[1]) }, '', decodeURIComponent(m[1]));
    }
}

// ====== Iframe Navigation ======
function initIframeNav() {
    var f = document.getElementById('mainFrame');
    if (!f) return;

    f.addEventListener('load', function() {
        var url;
        try { url = f.contentWindow.location.pathname + f.contentWindow.location.search; }
        catch(e) { return; }

        // 首次加载 + 侧边栏点击：push 新历史项
        var cleanUrl = url.replace(/[&?]_plain=1/g, '').replace('?&', '?').replace(/\?$/, '').replace(/&$/, '');
        if (!_popstateNav && !_initialLoad) { history.pushState({ url: cleanUrl }, '', cleanUrl); }

        // popstate 导航只回退历史，不 push，但需要同步 UI
        _popstateNav = false;
        _initialLoad = false;
        updateTabLabel(cleanUrl);
        updateActiveMenuItem(cleanUrl);
        updatePageCtx(cleanUrl);
    });

    window.addEventListener('popstate', function(e) {
        if (e.state && e.state.url) {
            _popstateNav = true;
            var url = e.state.url;
            f.src = url + (url.indexOf('?') >= 0 ? '&' : '?') + '_plain=1';
        }
    });
}

// ====== Tab Label ======
function initTabLabel() { updateTabLabel('/home'); }
function updateTabLabel(url) {
    var t = document.getElementById('tabBar'); if (!t) return;
    t.innerHTML = '<div class="tab-item active"><span class="tab-title">' + escapeHTML(getPageTitle(url)) + '</span></div>';
}

function getPageTitle(url) {
    var links = document.querySelectorAll('.menu-link');
    for (var i = 0; i < links.length; i++) {
        var h = links[i].getAttribute('href');
        if (!h || h === 'javascript:;' || h === '#') continue;
        if (url === h || url.indexOf(h + '?') === 0) return links[i].textContent.trim();
    }
    return url;
}

function updateActiveMenuItem(url) {
    document.querySelectorAll('.menu-item').forEach(function(i) { i.classList.remove('active'); });
    document.querySelectorAll('.menu-link').forEach(function(l) {
        var h = l.getAttribute('href');
        if (!h || h === 'javascript:;' || h === '#') return;
        if (url === h || url.indexOf(h + '?') === 0) {
            var item = l.closest('.menu-item');
            if (item) { item.classList.add('active'); var p = l.closest('.has-children'); if (p) p.classList.add('active', 'expanded'); }
        }
    });
}

function escapeHTML(s) { var d = document.createElement('div'); d.textContent = s; return d.innerHTML; }

// ====== 悬浮 Agent：页面上下文推送 ======
var _pageCtx = { path: '', title: '' };

function updatePageCtx(url) {
    _pageCtx = { path: url, title: getPageTitle(url) };
    postPageCtx();
}

function getAgentFrame() {
    return document.getElementById('agentFloatFrame');
}

function postPageCtx() {
    var f = getAgentFrame();
    if (!f || !f.contentWindow) return;
    try {
        f.contentWindow.postMessage({ type: 'page-ctx', path: _pageCtx.path, title: _pageCtx.title }, '*');
    } catch (e) { /* 面板未就绪时忽略 */ }
}

function initAgentCtx() {
    // 面板加载完成后会发 request-ctx 索取当前上下文，这里回发
    window.addEventListener('message', function (e) {
        if (!e.data || e.data.type !== 'request-ctx') return;
        var f = getAgentFrame();
        if (f && e.source === f.contentWindow) postPageCtx();
    });
}

// ====== Sidebar ======
function initSidebarMenu() {
    document.querySelectorAll('.has-children > .menu-link').forEach(function(l) {
        l.addEventListener('click', function(e) {
            if (this.getAttribute('href') === 'javascript:;') { e.preventDefault(); this.closest('.has-children').classList.toggle('expanded'); }
        });
    });

    document.querySelectorAll('.sidebar a[href]:not([href="javascript:;"])').forEach(function(a) {
        a.addEventListener('click', function(e) {
            e.preventDefault();
            var cleanUrl = this.getAttribute('href');
            document.getElementById('mainFrame').src = cleanUrl + (cleanUrl.indexOf('?') >= 0 ? '&' : '?') + '_plain=1';
        });
    });

    updateActiveMenuItem(window.location.search.indexOf('goto=') >= 0
        ? decodeURIComponent(window.location.search.match(/goto=([^&]*)/)[1])
        : '/home');
}

// ====== Clock ======
function initClock() {
    function u() {
        var n = new Date();
        var d = n.toLocaleDateString('zh-CN',{year:'numeric',month:'long',day:'numeric'});
        var w = n.toLocaleDateString('zh-CN',{weekday:'long'});
        var c = document.getElementById('clock'); if(c) c.innerText = d+' '+w;
    }
    u(); setInterval(u, 1000);
}

// ====== Theme ======
var color = "white";
function setcolor() {
    if (color == "white") {
        document.documentElement.style.setProperty('--header-bg-start', '#1a1a2e');document.documentElement.style.setProperty('--header-bg-end', '#16213e');document.documentElement.style.setProperty('--sidebar-bg', '#f8f9fb');document.documentElement.style.setProperty('--sidebar-border', '#e8e8e8');document.documentElement.style.setProperty('--content-bg', '#f5f7fa');document.documentElement.style.setProperty('--menu-text', '#4a4a4a');document.documentElement.style.setProperty('--menu-text-hover', '#6366f1');document.documentElement.style.setProperty('--menu-bg-hover', '#eef2ff');document.documentElement.style.setProperty('--menu-bg-active', '#eef2ff');document.documentElement.style.setProperty('--menu-active-border', '#6366f1');document.documentElement.style.setProperty('--submenu-bg', '#e0e7ff');document.documentElement.style.setProperty('--submenu-text', '#555');document.documentElement.style.setProperty('--toast-bg', '#1a1a2e');
    } else if (color == "black") {
        document.documentElement.style.setProperty('--header-bg-start', '#0d1117');document.documentElement.style.setProperty('--header-bg-end', '#161b22');document.documentElement.style.setProperty('--sidebar-bg', '#161b22');document.documentElement.style.setProperty('--sidebar-border', '#21262d');document.documentElement.style.setProperty('--content-bg', '#0d1117');document.documentElement.style.setProperty('--menu-text', '#c9d1d9');document.documentElement.style.setProperty('--menu-text-hover', '#818cf8');document.documentElement.style.setProperty('--menu-bg-hover', '#1c2333');document.documentElement.style.setProperty('--menu-bg-active', '#1c2333');document.documentElement.style.setProperty('--menu-active-border', '#818cf8');document.documentElement.style.setProperty('--submenu-bg', '#0d1117');document.documentElement.style.setProperty('--submenu-text', '#8b949e');document.documentElement.style.setProperty('--toast-bg', '#30363d');
        document.querySelector('.sidebar').style.background = 'linear-gradient(180deg, #161b22 0%, #0d1117 100%)';
    }
}

// ====== Logout ======
function initLogout() {
    document.querySelectorAll('[data-action="logout"]').forEach(function(e) { e.addEventListener('click', function(v) { v.preventDefault(); if(confirm('确定要退出登录吗？')) window.top.location.href = '/logout'; }); });
}

// ====== Toast ======
function showToast(m) { var t = document.getElementById('toast'); if(!t) return; t.style.display='block'; t.textContent=m; t.classList.add('show'); setTimeout(function(){t.classList.remove('show');t.style.display='none';},2000); }

// ====== Popup ======
function initPopup() {
    var b = document.getElementById('show-popup'); if(!b) return;
    var p = document.querySelector('.popup'); if(!p) return;
    var c = p.querySelector('a');
    b.addEventListener('click', function(){ p.style.display='block'; requestAnimationFrame(function(){p.classList.add('show');}); });
    function x(){ p.classList.remove('show'); setTimeout(function(){p.style.display='none';},200); }
    c.addEventListener('click', function(e){ e.preventDefault(); x(); });
    document.addEventListener('click', function(e){ if(p.style.display==='block' && !e.target.closest('.popup') && !e.target.closest('#show-popup')) x(); });
}
