// draft.js — 全站通用表单草稿（sessionStorage），解决「切页丢已填数据」。
// 保存：document 事件委托（捕获阶段）监听 input/change，存字段值（跳过 password/hidden/file/button 等
//       与 data-no-draft 标记的字段）。
// 回填：defer 加载 → DOMContentLoaded 后执行（晚于页面自身初始化，不会被默认值覆盖）。
// 重置：点击「重置」按钮（.btn-reset / [data-draft-reset] / 文字含 重置|清空|reset|clear），
//       按按钮所在模块（.card/.panel/.box/.section/.module，无则整页）——
//       1) 清空该模块草稿；2) 把字段还原为页面默认值（defaultValue/defaultChecked/defaultSelected）。
//       页面上原有的重置按钮（若有自己的清空 JS）仍照常运行，本脚本只额外负责清草稿 + 兜底还原。
// 存储：sessionStorage key = 'draft:' + pathname，值 = JSON {fieldKey: {v, t}}
(function () {
    'use strict';
    var store = window.sessionStorage;
    if (!store) return;

    var KEY = 'draft:' + location.pathname;
    var state = {};
    var timer = null;
    var SKIP_TYPE = { password: 1, hidden: 1, file: 1, submit: 1, button: 1, reset: 1, image: 1 };
    var SCOPE_SELECTOR = '.card, .panel, .box, .section, .module, [class*="-card"], [class*="-panel"]';

    function load() { try { state = JSON.parse(store.getItem(KEY)) || {}; } catch (e) { state = {}; } }
    function flush() { try { store.setItem(KEY, JSON.stringify(state)); } catch (e) {} }

    function isField(el) {
        var t = (el.tagName || '').toLowerCase();
        return t === 'input' || t === 'select' || t === 'textarea';
    }
    function isSkip(el) {
        if (el.disabled) return true;
        if (el.hasAttribute('data-no-draft')) return true;
        return !!SKIP_TYPE[(el.type || '').toLowerCase()];
    }
    function fieldKey(el) {
        var t = (el.type || '').toLowerCase();
        if (t === 'radio') return el.name || null;
        return el.id || el.name || null;
    }
    function readVal(el) {
        var t = (el.type || '').toLowerCase();
        if (t === 'checkbox') return { v: !!el.checked, t: 'checkbox' };
        if (t === 'radio') return { v: el.value, t: 'radio' };
        return { v: el.value, t: t };
    }
    function writeVal(el, rec) {
        var t = (el.type || '').toLowerCase();
        if (t === 'checkbox') { el.checked = !!rec.v; return; }
        if (t === 'radio') { el.checked = (el.value === rec.v); return; }
        el.value = (rec.v == null ? '' : rec.v);
    }
    // 还原字段为页面默认值（等价于原生 <input type=reset>）
    function resetField(el) {
        var tag = el.tagName.toLowerCase();
        var t = (el.type || '').toLowerCase();
        if (tag === 'select') {
            var sel = -1;
            for (var i = 0; i < el.options.length; i++) { if (el.options[i].defaultSelected) { sel = i; break; } }
            el.selectedIndex = sel >= 0 ? sel : 0;
        } else if (t === 'checkbox' || t === 'radio') {
            el.checked = el.defaultChecked;
        } else {
            el.value = el.defaultValue;
        }
    }
    function scopeOf(el) {
        return (el && el.closest) ? el.closest(SCOPE_SELECTOR) : null;
    }

    function capture(el) {
        var k = fieldKey(el);
        if (!k) return;
        state[k] = readVal(el);
        if (timer) clearTimeout(timer);
        timer = setTimeout(flush, 300);
    }

    function restore() {
        Object.keys(state).forEach(function (k) {
            var rec = state[k];
            if (!rec) return;
            if (rec.t === 'radio') {
                var els = document.getElementsByName(k);
                for (var i = 0; i < els.length; i++) if (els[i].value === rec.v) els[i].checked = true;
            } else {
                var el = document.getElementById(k) || document.getElementsByName(k)[0];
                if (el && isField(el) && !isSkip(el)) writeVal(el, rec);
            }
        });
    }

    // 重置某模块：清草稿 + 字段还原默认值
    function doReset(scope) {
        var target = scope || document.body;
        var fields = target.querySelectorAll('input, select, textarea');
        for (var i = 0; i < fields.length; i++) {
            var f = fields[i];
            if (!isSkip(f)) resetField(f);
            var k = fieldKey(f);
            if (k) delete state[k];
        }
        flush();
    }

    // 保存
    document.addEventListener('input', function (e) {
        var el = e.target;
        if (el && isField(el) && !isSkip(el)) capture(el);
    }, true);
    document.addEventListener('change', function (e) {
        var el = e.target;
        if (el && isField(el) && !isSkip(el)) capture(el);
    }, true);

    // 重置
    document.addEventListener('click', function (e) {
        var btn = e.target && e.target.closest ? e.target.closest('button, [role="button"]') : null;
        if (!btn) return;
        var isReset = btn.hasAttribute('data-draft-reset') ||
            /reset|clear|重置|清空/i.test((btn.className || '').toString()) ||
            /重置|清空|reset|clear/i.test((btn.textContent || '').trim());
        if (!isReset) return;
        var scope = scopeOf(btn) || (btn.closest ? btn.closest('.card') : null);
        doReset(scope);
    }, true);

    // 回填（defer 脚本执行时 readyState 已是 'interactive'，监听 DOMContentLoaded 保证晚于页面初始化）
    if (document.readyState === 'complete') {
        load(); restore();
    } else {
        document.addEventListener('DOMContentLoaded', function () {
            load(); restore();
        });
    }
})();
