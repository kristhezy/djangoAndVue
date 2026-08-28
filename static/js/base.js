var IS_PLAIN = (window.location.search.indexOf('_plain=1') !== -1);

// 在 iframe 中 session 过期时强制整页跳转登录
if (IS_PLAIN && window.self !== window.top && window.location.pathname === '/login') {
    window.top.location.href = '/login';
}

document.addEventListener('DOMContentLoaded', function() {
    if (IS_PLAIN) {
        initEventDelegation();
        return;
    }
    initClock();
    initLogout();
    setcolor();
    initTabs();
    initEventDelegation();
});

// ====== Event Delegation ======
function initEventDelegation() {
    document.addEventListener('change', function(e) {
        if (e.target.matches('input[type="radio"]') && typeof handleRadioChange === 'function') {
            handleRadioChange();
        }
    });
}

// ====== Tab Bar (navigation only, no Ajax) ======
function initTabs() {
    var url = window.location.pathname + window.location.search;
    var title = getPageTitle(url);

    var saved = getSavedTabs();
    var exists = saved.some(function(t) { return t.url === url; });
    if (!exists) {
        saved.push({ title: title, url: url });
        if (saved.length > 15) saved = saved.slice(saved.length - 15);
        saveTabs(saved);
    }

    var tabBar = document.getElementById('tabBar');
    if (!tabBar) return;
    tabBar.innerHTML = '';
    saved.forEach(function(t) {
        var isActive = (t.url === url);
        var tab = document.createElement('div');
        tab.className = 'tab-item' + (isActive ? ' active' : '');
        tab.title = t.title;
        tab.innerHTML = '<span class="tab-title">' + escapeHTML(t.title) + '</span>' +
            '<span class="tab-close" data-url="' + escapeHTML(t.url) + '">&times;</span>';
        tab.addEventListener('click', function(e) {
            if (e.target.closest('.tab-close')) return;
            if (t.url !== url) window.location.href = t.url;
        });
        tabBar.appendChild(tab);
    });
    updateActiveMenuItem(url);
}

document.addEventListener('click', function(e) {
    var closeBtn = e.target.closest('.tab-close');
    if (!closeBtn) return;
    e.stopPropagation(); e.preventDefault();
    var closeUrl = closeBtn.getAttribute('data-url');
    var saved = getSavedTabs();
    saved = saved.filter(function(t) { return t.url !== closeUrl; });
    saveTabs(saved);
    var currentUrl = window.location.pathname + window.location.search;
    if (closeUrl === currentUrl && saved.length > 0) {
        window.location.href = saved[saved.length - 1].url;
    } else { initTabs(); }
});

function getSavedTabs() {
    try { return JSON.parse(sessionStorage.getItem('_tabs') || '[]'); } catch(e) { return []; }
}
function saveTabs(tabs) {
    try { sessionStorage.setItem('_tabs', JSON.stringify(tabs)); } catch(e) {}
}

function getPageTitle(url) {
    var links = document.querySelectorAll('.menu-link');
    for (var i = 0; i < links.length; i++) {
        var href = links[i].getAttribute('href');
        if (!href || href === 'javascript:;' || href === '#') continue;
        if (url === href || url.indexOf(href + '?') === 0 || url.endsWith(href)) {
            return links[i].textContent.trim();
        }
    }
    var h1 = document.querySelector('.card-header h1') || document.querySelector('h1');
    if (h1) return h1.textContent.trim();
    return url;
}

function updateActiveMenuItem(url) {
    document.querySelectorAll('.menu-item').forEach(function(item) { item.classList.remove('active'); });
    document.querySelectorAll('.menu-link').forEach(function(link) {
        var href = link.getAttribute('href');
        if (href && href !== 'javascript:;' && url.indexOf(href) !== -1) {
            var item = link.closest('.menu-item');
            if (item) {
                item.classList.add('active');
                var parent = link.closest('.has-children');
                if (parent) parent.classList.add('active', 'expanded');
            }
        }
    });
}

function escapeHTML(str) { var div = document.createElement('div'); div.textContent = str; return div.innerHTML; }

// ====== Theme ======
let color = "white";
function setcolor(){
    if (color == "white"){
        document.documentElement.style.setProperty('--header-bg-start', '#1a1a2e');
        document.documentElement.style.setProperty('--header-bg-end', '#16213e');
        document.documentElement.style.setProperty('--sidebar-bg', '#f8f9fb');
        document.documentElement.style.setProperty('--sidebar-border', '#e8e8e8');
        document.documentElement.style.setProperty('--content-bg', '#f5f7fa');
        document.documentElement.style.setProperty('--menu-text', '#4a4a4a');
        document.documentElement.style.setProperty('--menu-text-hover', '#6366f1');
        document.documentElement.style.setProperty('--menu-bg-hover', '#eef2ff');
        document.documentElement.style.setProperty('--menu-bg-active', '#eef2ff');
        document.documentElement.style.setProperty('--menu-active-border', '#6366f1');
        document.documentElement.style.setProperty('--submenu-bg', '#e0e7ff');
        document.documentElement.style.setProperty('--submenu-text', '#555');
        document.documentElement.style.setProperty('--toast-bg', '#1a1a2e');
    } else if(color == "black"){
        document.documentElement.style.setProperty('--header-bg-start', '#0d1117');
        document.documentElement.style.setProperty('--header-bg-end', '#161b22');
        document.documentElement.style.setProperty('--sidebar-bg', '#161b22');
        document.documentElement.style.setProperty('--sidebar-border', '#21262d');
        document.documentElement.style.setProperty('--content-bg', '#0d1117');
        document.documentElement.style.setProperty('--menu-text', '#c9d1d9');
        document.documentElement.style.setProperty('--menu-text-hover', '#818cf8');
        document.documentElement.style.setProperty('--menu-bg-hover', '#1c2333');
        document.documentElement.style.setProperty('--menu-bg-active', '#1c2333');
        document.documentElement.style.setProperty('--menu-active-border', '#818cf8');
        document.documentElement.style.setProperty('--submenu-bg', '#0d1117');
        document.documentElement.style.setProperty('--submenu-text', '#8b949e');
        document.documentElement.style.setProperty('--toast-bg', '#30363d');
        document.querySelector('.sidebar').style.background = 'linear-gradient(180deg, #161b22 0%, #0d1117 100%)';
    }
}

/* Sidebar expand/collapse + active state */
document.addEventListener('DOMContentLoaded', function() {
    var allMenuItems = document.querySelectorAll('.menu-item');
    var hasChildrenItems = document.querySelectorAll('.menu-item.has-children');
    var pureItems = document.querySelectorAll('.menu-item:not(.has-children)');
    var submenuLinks = document.querySelectorAll('.submenu .menu-link');
    var currentUrl = window.location.href;

    hasChildrenItems.forEach(function(item) {
        var menuLink = item.querySelector('.menu-link');
        if (!menuLink) return;
        menuLink.addEventListener('click', function(e) {
            var href = this.getAttribute('href');
            if (href === 'javascript:;' || href === '#') {
                e.preventDefault();
                item.classList.toggle('expanded');
            }
        });
    });

    document.addEventListener('click', function(e) {
        var targetLink = e.target.closest('.menu-link');
        if (!targetLink) return;
        var pureItem = targetLink.closest('.menu-item:not(.has-children)');
        if (pureItem) {
            allMenuItems.forEach(function(item) { if (!item.closest('.submenu')) item.classList.remove('active'); });
            pureItem.classList.add('active');
            return;
        }
        var isSubmenuLink = targetLink.closest('.submenu');
        if (isSubmenuLink) {
            var parentMenuItem = targetLink.closest('.menu-item.has-children');
            if (parentMenuItem) {
                parentMenuItem.classList.add('active', 'expanded');
                hasChildrenItems.forEach(function(item) { if (item !== parentMenuItem) item.classList.remove('active'); });
                submenuLinks.forEach(function(link) { link.parentElement.classList.remove('active'); });
                targetLink.parentElement.classList.add('active');
            }
        }
    });

    var initMenuActiveState = function() {
        pureItems.forEach(function(item) {
            var link = item.querySelector('.menu-link');
            if (!link) return;
            var linkHref = link.getAttribute('href');
            if (linkHref && linkHref !== 'javascript:;' && currentUrl.includes(linkHref)) {
                allMenuItems.forEach(function(i) { if (!i.closest('.submenu')) i.classList.remove('active'); });
                item.classList.add('active');
            }
        });
        submenuLinks.forEach(function(link) {
            var linkHref = link.getAttribute('href');
            if (linkHref && linkHref !== 'javascript:;' && currentUrl.includes(linkHref)) {
                var parentMenuItem = link.closest('.menu-item.has-children');
                if (parentMenuItem) {
                    parentMenuItem.classList.add('active', 'expanded');
                    hasChildrenItems.forEach(function(item) { if (item !== parentMenuItem) item.classList.remove('active'); });
                    submenuLinks.forEach(function(l) { l.parentElement.classList.remove('active'); });
                    link.parentElement.classList.add('active');
                }
            }
        });
    };
    initMenuActiveState();
});

function initLogout() {
    document.querySelectorAll('[data-action="logout"]').forEach(function(element) {
        element.addEventListener('click', function(e) {
            e.preventDefault();
            if (confirm('确定要退出登录吗？')) window.location.href = '/logout';
        });
    });
}

function initClock() {
    function updateTime() {
        var now = new Date();
        var dateStr = now.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric'});
        var weekStr = now.toLocaleDateString('zh-CN', {weekday: 'long'});
        var clock = document.getElementById('clock');
        if (clock) clock.innerText = dateStr + ' ' + weekStr;
    }
    updateTime(); setInterval(updateTime, 1000);
}

function showToast(message) {
    var toast = document.getElementById('toast');
    if (!toast) return;
    toast.style.display = "block"; toast.textContent = message; toast.classList.add('show');
    setTimeout(function() { toast.classList.remove('show'); toast.style.display = "none"; }, 2000);
}

/* Popup */
var showPopupBtn = document.getElementById('show-popup');
if (showPopupBtn) {
    var popup = document.querySelector('.popup');
    var closeBtn = popup.querySelector('a');
    var rpart = document.querySelector('main');

    showPopupBtn.addEventListener('click', function() {
        popup.style.display = 'block';
        requestAnimationFrame(function() { popup.classList.add('show'); });
    });

    function closePopup() {
        popup.classList.remove('show');
        setTimeout(function() { popup.style.display = 'none'; }, 200);
    }

    closeBtn.addEventListener('click', function(e) { e.preventDefault(); closePopup(); });
    rpart.addEventListener('click', function() { if (popup.style.display === 'block') closePopup(); });
}
