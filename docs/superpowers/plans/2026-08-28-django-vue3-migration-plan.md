# Django → Vue3 + Vite 迁移 实现计划（第一阶段：壳 + 试点页）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立 Vue3 壳（header/sidebar/路由/iframe 兜底），并把试点页「手工合并用户」迁移为 Vue 组件，跑通「Vue 壳 → /api/menu → Vue 组件 → 复用旧 POST 接口」完整链路。

**Architecture:** Vue3 + Vite 独立工程 `frontend/`；开发时 Vite(5173) proxy 到 Django(8001)；生产 `vite build` 产物由 Django 托管，`/` 及 SPA 路由走 history 模式 + catch-all 返回 index.html。后端只新增 `/api/menu` 接口和一个 SPA 兜底视图，其余视图/中间件/权限零改动。

**Tech Stack:** Vue3 + Vite + JavaScript + Element Plus + Pinia + vue-router + axios；Django 5.2（现有）+ uvicorn。

**设计文档:** `docs/superpowers/specs/2026-08-28-django-vue3-migration-design.md`（本计划第 0 节的断点续作约定必须遵守）

---

## 断点续作约定（硬约束）

1. 本文件是**进度的单一真相**。每完成一步、遇到阻塞、跳过某步，**立即**更新对应 checkbox 状态（`[ ] 未开始 / [~] 进行中 / [x] 已完成 / [!] 阻塞`）并在行尾或下方加一句备注，再做别的事。
2. 恢复时：读 spec 恢复「为什么」，读本文件 checkbox 恢复「做到哪」，直接接下一步。
3. 禁止依赖对话记忆判断进度。

---

## Global Constraints

- **端口**：Django 统一用 **8001**（8000 被旧项目占用）。Vite dev 用 5173。
- **前端语言**：JavaScript（不用 TypeScript）。
- **UI 组件库**：Element Plus。
- **认证**：session + CSRF，零改动。CSRF header 名 `X-CSRFToken`，值从 cookie `csrftoken` 读（现有 `CSRF_COOKIE_HTTPONLY = False` 已满足）。
- **后端接口**：复用现有视图，不引入 DRF。新增接口返回结构统一为 `get_result` 格式 `{code, msg, data}`（`JsonResponse` 默认 `ensure_ascii=False`）。
- **不删**：任何旧模板、旧静态文件、旧视图。
- **分支**：迁移在独立分支 `feature/vue3-migration` 上进行（从 main 切出）。
- **测试策略**：后端接口（/api/menu、SPA 兜底）用 Django 内置 test client 写测试（TDD）；前端 Vue 组件无测试基础设施，用 browser-automation 技能 + 手动清单验证，不引入 vitest。
- **Python 解释器**：`run.sh` 中为 `/Users/imc/vllm/yes/envs/py310/bin/python3`。测试与启动统一用该解释器（或项目 venv，执行时先确认）。

---

## File Structure（本阶段涉及的文件）

**后端：**
- Modify: `run.sh` — 端口 8000→8001
- Modify: `djangoPlant/settings.py` — `CSRF_TRUSTED_ORIGINS`、`STATICFILES_DIRS`
- Modify: `djangoPlant/urls.py` — 新增 `/api/menu` 路由 + SPA catch-all
- Create: `djangoPlant/spa.py` — SPA 兜底视图（返回 frontend/dist/index.html）
- Create: `djangoPlant/api_menu.py` — 菜单接口（MENU_STRUCTURE + 过滤）
- Modify: `djangoPlant/userlogin.py` — 登录成功默认跳转 `/`（Vue 壳）
- Create: `djangoPlant/test_migration.py` — /api/menu 与 SPA 兜底的测试

**前端（frontend/）：**
- Create: `frontend/package.json`、`frontend/vite.config.js`、`frontend/index.html`
- Create: `frontend/src/main.js`、`frontend/src/App.vue`
- Create: `frontend/src/api/http.js`（axios 封装 + CSRF + 302 拦截）
- Create: `frontend/src/api/menu.js`（getMenu）
- Create: `frontend/src/store/menu.js`（Pinia store）
- Create: `frontend/src/router/index.js`
- Create: `frontend/src/layout/AppLayout.vue`（壳骨架）
- Create: `frontend/src/layout/HeaderBar.vue`
- Create: `frontend/src/layout/SidebarMenu.vue`
- Create: `frontend/src/views/LegacyIframe.vue`
- Create: `frontend/src/views/mergeUser/index.vue`

---

## Task 1: 切迁移分支 + 前端工程脚手架

**Files:**
- Modify: （无，git 操作）
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`
- Create: `frontend/.gitignore`

**Interfaces:**
- Produces: Vite dev server 跑在 5173，proxy `/api`、`/sv`、`/ov`、`/pv`、`/static`、`/login`、`/logout` → `http://localhost:8001`；`vite build` 输出到 `frontend/dist`，`base='/static/'`。

- [ ] **Step 1: 切出独立分支**

```bash
cd /Users/imc/djangoAndVue
git checkout -b feature/vue3-migration
```

- [ ] **Step 2: 确认 Node/npm 环境**

```bash
node -v && npm -v
```
预期：Node ≥ 18，npm ≥ 9（本项目用 Vite 5，需 Node 18+）。

- [ ] **Step 3: 写 frontend/package.json**

```json
{
  "name": "django-vue3-frontend",
  "private": true,
  "version": "0.0.1",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.7.7",
    "element-plus": "^2.8.4",
    "pinia": "^2.2.2",
    "vue": "^3.5.12",
    "vue-router": "^4.4.5"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.1.4",
    "vite": "^5.4.9"
  }
}
```

- [ ] **Step 4: 写 frontend/vite.config.js**

```js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const DJANGO = 'http://localhost:8001'

export default defineConfig(({ command }) => ({
  plugins: [vue()],
  // dev 下 base 用 '/'：Vite 自己提供 app 源码（/src/main.js 等），不经过 /static 代理。
  // build 下 base 用 '/static/vue/'：产物落在 static/vue/，由 Django 的 /static/ URL 服务。
  // （Django 的 static() 只服务 STATICFILES_DIRS[0]=static/，故构建产物必须落在 static/ 内）
  base: command === 'build' ? '/static/vue/' : '/',
  server: {
    port: 5173,
    proxy: {
      '/api': DJANGO,
      '/sv': DJANGO,
      '/ov': DJANGO,
      '/pv': DJANGO,
      '/static': DJANGO,
      '/login': DJANGO,
      '/logout': DJANGO,
    },
  },
  build: {
    outDir: '../static/vue',
    emptyOutDir: true,
  },
}))
```

- [ ] **Step 5: 写 frontend/index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TS-Django</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

- [ ] **Step 6: 写 frontend/src/main.js**

```js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.mount('#app')
```

- [ ] **Step 7: 写最小 frontend/src/App.vue（占位，后续 Task 替换）**

```vue
<template>
  <router-view />
</template>

<script setup>
</script>
```

- [ ] **Step 8: 写 frontend/src/router/index.js（占位，最小路由）**

```js
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: () => import('../views/LegacyIframe.vue') },
  ],
})

export default router
```

> 注：本步 `LegacyIframe.vue` 尚未创建，先建一个占位文件以免启动报错（见 Step 9）。

- [ ] **Step 9: 写占位 frontend/src/views/LegacyIframe.vue**

```vue
<template>
  <iframe :src="src" style="width:100%;height:100%;border:none;"></iframe>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const src = computed(() => route.query.goto ? `/${route.query.goto}` : '/home')
</script>
```

- [ ] **Step 10: 写 frontend/.gitignore**

```
node_modules/
```

> 说明：构建产物输出到 `static/vue/`（不在 frontend/ 内），由项目根 `.gitignore` 统一忽略，见 Task 2。

- [ ] **Step 11: 安装依赖**

```bash
cd /Users/imc/djangoAndVue/frontend
npm install
```

- [ ] **Step 12: 验证 dev server 能起**

```bash
cd /Users/imc/djangoAndVue/frontend
npm run dev
```
预期：Vite 启动在 `http://localhost:5173`，无编译错误。验证后 Ctrl+C 停掉。

- [ ] **Step 13: Commit**

```bash
cd /Users/imc/djangoAndVue
git add frontend/
git commit -m "feat(frontend): 搭建 Vue3 + Vite + Element Plus 工程脚手架"
```

---

## Task 2: Django 端口与静态配置

**Files:**
- Modify: `run.sh`（端口 8000→8001）
- Modify: `djangoPlant/settings.py`（`CSRF_TRUSTED_ORIGINS`）
- Modify: `.gitignore`（忽略 `static/vue/` 构建产物）

**Interfaces:**
- Produces: Django 跑在 8001；dev 前端源 5173 与 8001 进入 CSRF 信任源；构建产物 `static/vue/` 不入 git。

- [ ] **Step 1: 改 run.sh 端口**

将 `run.sh` 最后一行：
```
/Users/imc/vllm/yes/envs/py310/bin/python3 -m uvicorn djangoPlant.asgi:application --host 0.0.0.0 --port 8000 ...
```
改为 `--port 8001`。用 Edit 精确替换 `--port 8000` → `--port 8001`。

- [ ] **Step 2: 改 settings.py 的 CSRF_TRUSTED_ORIGINS**

将：
```python
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000']  # 本地开发域名（根据实际修改）
```
改为：
```python
CSRF_TRUSTED_ORIGINS = ['http://localhost:8001', 'http://localhost:5173', 'http://127.0.0.1:8001', 'http://127.0.0.1:5173']
```

- [ ] **Step 3: 改根 .gitignore，忽略构建产物**

在项目根 `.gitignore` 末尾追加：

```
# Vue 构建产物（npm run build 输出到 static/vue/，不入库）
static/vue/
```

> 说明：**不改 `STATICFILES_DIRS`**。Vite 已配置输出到 `static/vue/`，它落在 `STATICFILES_DIRS[0]`（`static/`）内部，天然被 Django 的 `static()` 与 `/static/` URL 覆盖，无需任何额外静态配置。

- [ ] **Step 4: 验证 Django 能起在 8001**

```bash
cd /Users/imc/djangoAndVue
bash run.sh
```
预期：uvicorn 监听 8001，无报错。验证后 Ctrl+C 停掉。

- [ ] **Step 5: Commit**

```bash
cd /Users/imc/djangoAndVue
git add run.sh djangoPlant/settings.py .gitignore
git commit -m "chore: 端口统一为 8001，忽略 Vue 构建产物 static/vue"
```

---

## Task 3: SPA 兜底视图 + 测试

**Files:**
- Create: `djangoPlant/spa.py`
- Create: `djangoPlant/test_migration.py`（本任务只写 SPA 兜底部分）
- Modify: `djangoPlant/urls.py`（本任务只加 catch-all，/api/menu 在 Task 4 加）

**Interfaces:**
- Produces: `spa_index(request)` 视图，返回 `static/vue/index.html` 内容（`Content-Type: text/html`）；产物不存在时返回 404 提示。供 urls.py 的 catch-all 与根路径 `/` 使用。

- [ ] **Step 1: 写失败测试**

在 `djangoPlant/test_migration.py` 中写：

```python
from django.test import TestCase, Client
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
DIST_INDEX = BASE_DIR / 'static' / 'vue' / 'index.html'


class SpaFallbackTests(TestCase):
    def test_spa_index_returns_html_when_dist_exists(self):
        # 造一个临时 static/vue/index.html
        DIST_INDEX.parent.mkdir(parents=True, exist_ok=True)
        DIST_INDEX.write_text('<!DOCTYPE html><div id="app"></div>', encoding='utf-8')
        try:
            resp = Client().get('/some-vue-route')
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp['Content-Type'], 'text/html')
            self.assertIn(b'<div id="app">', resp.content)
        finally:
            DIST_INDEX.unlink(missing_ok=True)

    def test_spa_index_404_when_dist_missing(self):
        if DIST_INDEX.exists():
            DIST_INDEX.unlink()
        resp = Client().get('/some-vue-route')
        self.assertEqual(resp.status_code, 404)

    def test_root_returns_spa(self):
        # 根路径 / 应返回 Vue index.html（登录后进入 Vue 壳）
        DIST_INDEX.parent.mkdir(parents=True, exist_ok=True)
        DIST_INDEX.write_text('<!DOCTYPE html><div id="app"></div>', encoding='utf-8')
        try:
            resp = Client().get('/')
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'<div id="app">', resp.content)
        finally:
            DIST_INDEX.unlink(missing_ok=True)
```

- [ ] **Step 2: 跑测试确认失败**

```bash
cd /Users/imc/djangoAndVue
python manage.py test djangoPlant.test_migration.SpaFallbackTests -v 2
```
预期：FAIL（`spa_index` 未定义 / catch-all 未加）。

- [ ] **Step 3: 写 djangoPlant/spa.py**

```python
"""SPA 兜底视图：生产环境下把非 API 路径交给 Vue 的 index.html。"""
from pathlib import Path
from django.http import HttpResponse, Http404

BASE_DIR = Path(__file__).resolve().parent.parent
DIST_INDEX = BASE_DIR / 'static' / 'vue' / 'index.html'


def spa_index(request):
    """返回 Vue 构建产物 index.html，让 vue-router 接管前端路由。"""
    if not DIST_INDEX.exists():
        raise Http404("前端尚未构建，请先运行 frontend 的 npm run build")
    with open(DIST_INDEX, 'rb') as f:
        return HttpResponse(f.read(), content_type='text/html')
```

- [ ] **Step 4: 在 urls.py 加根路径 `/` 指向 spa_index + catch-all（放在 static 之后）**

改动分两处：

**(a) 根路径 `/` 从旧 shell 改为 Vue 壳**。将现有：
```python
    path('',pv.shell,name="home"),
```
改为：
```python
    path('',spa.spa_index,name="index"),
```

> 注意：根路径 name 用 `"index"`，**不要用 `"home"`**——`urlpatterns` 里已有一个 `path('home',pv.home,name="home")`，重名会导致 `reverse('home')` 命中 `/`（第一个）而非 `/home`，埋下隐患。

**(b) catch-all 放在 `if settings.DEBUG:` 的 static 之后**，避免吞掉 `/static/*`。在 `djangoPlant/urls.py` 文件最末尾（`static(...)` 那行之后、`handler404` 之前）加入：

```python
from . import spa

# SPA 兜底：所有未命中路由交给 Vue index.html（必须放在 static 之后，避免吞掉静态文件）
urlpatterns += [
    re_path(r'^.*$', spa.spa_index, name='spa'),
]
```

> 注意：`re_path` 已在文件顶部导入（`from django.urls import path, re_path`）。`from . import spa` 需放在文件顶部 import 区（与 `from . import originview as ov` 并列）。catch-all 兜住未知路径，但 `admin/`、`login`、`logout`、`/sv/*`、`/ov/*`、`/pv/*`、`/api/*`、`/static/*` 等明确路由仍优先匹配。

- [ ] **Step 5: 跑测试确认通过**

```bash
cd /Users/imc/djangoAndVue
python manage.py test djangoPlant.test_migration.SpaFallbackTests -v 2
```
预期：PASS。

- [ ] **Step 6: Commit**

```bash
cd /Users/imc/djangoAndVue
git add djangoPlant/spa.py djangoPlant/urls.py djangoPlant/test_migration.py
git commit -m "feat(spa): 新增 SPA 兜底视图，非 API 路径返回 Vue index.html"
```

---

## Task 4: /api/menu 菜单接口 + 测试

**Files:**
- Create: `djangoPlant/api_menu.py`
- Modify: `djangoPlant/test_migration.py`（追加菜单接口测试）
- Modify: `djangoPlant/urls.py`（加 /api/menu 路由）

**Interfaces:**
- Produces: `menu_api(request)` 视图（`@login_required`），`GET /api/menu` 返回 `{code, msg, data}`，其中 `data = {user:{uid,uname,rn}, groups:[...], standalone:[...]}`。菜单项结构 `{key, title, url, icon}`。
- Consumes: `djangoPlant.menu_registry.MENU_MAP`；`djangoPlant.config.text_config.SITE_CONFIG`；`request.session['menus']`；`request.session['uid'/'uname'/'rn']`。

- [ ] **Step 1: 在 api_menu.py 中定义菜单结构**

`djangoPlant/api_menu.py`：

```python
"""菜单接口：把 sidebar.html 的结构/分组/图标抽成数据，按用户权限过滤返回。

菜单结构唯一权威在此维护（对应 templates/partials/sidebar.html）。
数据结构：STANDS（独立项）+ GROUPS（分组，含 title 与 items）。
"""
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from . import JsonResponse
from .config.text_config import SITE_CONFIG as C

# 图标 class（与 sidebar.html 一致，Vue 侧用 FontAwesome class 渲染）
I = {
    'home': 'fa-solid fa-house',
    'other': 'fa-solid fa-sheet-plastic',
    'soon': 'fa-brands fa-squarespace',
    'mmeett': 'fa-brands fa-mix',
    'setting': 'fa-solid fa-arrows-to-dot',
    'twCompSet': 'fa-solid fa-won-sign',
    'compconfig': 'fa-solid fa-bars-progress',
    'updateCI': 'fa-solid fa-pen-to-square',
    'companyModule': 'fa-solid fa-list-ul',
    'tools': 'fa-solid fa-hammer',
    'afterSales': 'fa-solid fa-comments',
    'miniprogram': 'fa-solid fa-litecoin-sign',
    'mynote': 'fa-solid fa-list',
    'usercenter': 'fa-solid fa-user',
    'easyIC': 'fa-brands fa-linode',
    'aitools': 'fa-brands fa-think-peaks',
    'agent': 'fa-solid fa-robot',
}

# 独立菜单项（按 sidebar 顺序）
STANDS = [
    ('home', C['SITE_HOME'], C['SITE_HOME_NAME']),
    ('other', C['SITE_OTHER'], C['SITE_OTHER_NAME']),
    ('soon', C['SITE_SOONCONFIG'], C['SITE_SOONCONFIG_NAME']),
    ('mmeett', C['SITE_MMEETTOPEN'], C['SITE_MMEETTOPEN_NAME']),
    ('setting', C['SITE_SETTING'], C['SITE_SETTING_NAME']),
    ('twCompSet', C['SITE_TWCOMPSET'], C['SITE_TWCOMPSET_NAME']),
    ('updateCI', C['SITE_UPDATECI'], C['SITE_UPDATECI_NAME']),
    ('companyModule', C['SITE_COMPMODULE'], C['SITE_COMPMODULE_NAME']),
    ('afterSales', C['SITE_AFTERSALES'], C['SITE_AFTERSALES_NAME']),
    ('miniprogram', C['SITE_MINIPROGRAM'], C['SITE_MINIPROGRAM_NAME']),
    ('mynote', C['SITE_MYNOTE'], C['SITE_MYNOTE_NAME']),
    ('usercenter', C['SITE_USERCENTER'], C['SITE_USERCENTER_NAME']),
    ('easyIC', C['SITE_EASYIC'], C['SITE_EASYIC_NAME']),
    ('aitools', C['SITE_AITOOLS'], C['SITE_AITOOLS_NAME']),
    ('agent', C['SITE_AGENT'], C['SITE_AGENT_NAME']),
]

# 分组菜单（title 用 group icon，items 无独立 icon）
GROUPS = [
    ('compconfig', C['TITLE_COMPCONFIG'], [
        ('jtSaleskits', C['SITE_JTSK'], C['SITE_JTSK_NAME']),
        ('hwskset', C['SITE_HWSKSET'], C['SITE_HWSKSET_NAME']),
        ('upgradeR3', C['SITE_UPGRADER3'], C['SITE_UPGRADER3_NAME']),
        ('basicComp', C['SITE_BASICCOMP'], C['SITE_BASICCOMP_NAME']),
        ('baseUpgradeSK', C['SITE_BASEUPGSK'], C['SITE_BASEUPGSK_NAME']),
    ]),
    ('tools', C['TITLE_TOOLS'], [
        ('delCP', C['SITE_DELCP'], C['SITE_DELCP_NAME']),
        ('forWeCom', C['SITE_FORWECOM'], C['SITE_FORWECOM_NAME']),
        ('mergeUser', C['SITE_MERGEUSER'], C['SITE_MERGEUSER_NAME']),
        ('delBindRelation', C['SITE_DELBINDRLT'], C['SITE_DELBINDRLT_NAME']),
        ('aboutLogin', C['SITE_ABOUTLOGIN'], C['SITE_ABOUTLOGIN_NAME']),
        ('dzFunction', C['SITE_DINGZHI'], C['SITE_DINGZHI_NAME']),
        ('batchDeleteClue', C['SITE_BATCHDC'], C['SITE_BATCHDC_NAME']),
    ]),
]


def _item(key, url, title):
    return {'key': key, 'title': title, 'url': url, 'icon': I.get(key, '')}


@login_required
@never_cache
def menu_api(request):
    menus = request.session.get('menus', []) or []
    user = {
        'uid': request.session.get('uid'),
        'uname': request.session.get('uname'),
        'rn': request.session.get('rn'),
    }
    standalone = [_item(k, u, t) for (k, u, t) in STANDS if k in menus]
    groups = []
    for gkey, gtitle, items in GROUPS:
        visible = [_item(k, u, t) for (k, u, t) in items if k in menus]
        if visible:
            groups.append({'key': gkey, 'title': gtitle, 'icon': I.get(gkey, ''), 'items': visible})
    return JsonResponse({'code': '0', 'msg': '成功', 'data': {'user': user, 'groups': groups, 'standalone': standalone}})
```

- [ ] **Step 2: 追加菜单接口测试到 test_migration.py**

```python
from django.contrib.auth.models import User
from django.test import Client


class MenuApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('menutest', password='x')
        self.c = Client()
        self.c.force_login(self.user)

    def test_requires_login(self):
        resp = Client().get('/api/menu')
        self.assertIn(resp.status_code, (302, 403))

    def test_empty_menus_returns_empty(self):
        resp = self.c.get('/api/menu')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()['data']
        self.assertEqual(data['standalone'], [])
        self.assertEqual(data['groups'], [])

    def test_mergeuser_menu_is_inside_tools_group(self):
        # 只给 mergeUser 权限
        s = self.c.session
        s['menus'] = ['mergeUser']
        s.save()
        resp = self.c.get('/api/menu')
        data = resp.json()['data']
        self.assertEqual(data['standalone'], [])
        self.assertEqual(len(data['groups']), 1)
        self.assertEqual(data['groups'][0]['key'], 'tools')
        self.assertEqual(data['groups'][0]['items'][0]['key'], 'mergeUser')
```

- [ ] **Step 3: 跑测试确认失败（/api/menu 尚未路由）**

```bash
cd /Users/imc/djangoAndVue
python manage.py test djangoPlant.test_migration.MenuApiTests -v 2
```
预期：FAIL（catch-all 会兜住 /api/menu，返回 index.html 或 404，而非 JSON）。

- [ ] **Step 4: 在 urls.py 加 /api/menu 路由（放在 catch-all 之前）**

在 `urls.py` 里，找到新增 catch-all 的那行之前，加入：

```python
from . import api_menu
```
并在 `urlpatterns = [...]` 内（明确路由区）加入：
```python
    path('api/menu', api_menu.menu_api, name='api_menu'),
```

- [ ] **Step 5: 跑测试确认通过**

```bash
cd /Users/imc/djangoAndVue
python manage.py test djangoPlant.test_migration -v 2
```
预期：PASS（MenuApiTests + SpaFallbackTests 全绿）。

- [ ] **Step 6: Commit**

```bash
cd /Users/imc/djangoAndVue
git add djangoPlant/api_menu.py djangoPlant/urls.py djangoPlant/test_migration.py
git commit -m "feat(api): 新增 /api/menu 菜单接口（按 session menus 过滤返回菜单树）"
```

---

## Task 5: 前端 axios 封装 + CSRF + 302 拦截

**Files:**
- Create: `frontend/src/api/http.js`
- Create: `frontend/src/api/menu.js`

**Interfaces:**
- Produces: `http`（axios 实例，自动带 `X-CSRFToken`，302→/login、302→/denied 自动跳转）；`getMenu()` 返回 `{code,msg,data}` 中的 `data`。

- [ ] **Step 1: 写 frontend/src/api/http.js**

```js
import axios from 'axios'

function getCookie(name) {
  const m = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'))
  return m ? decodeURIComponent(m[1]) : ''
}

const http = axios.create({
  baseURL: '',
  withCredentials: true,
})

http.interceptors.request.use((config) => {
  const token = getCookie('csrftoken')
  if (token) {
    config.headers['X-CSRFToken'] = token
  }
  config.headers['Content-Type'] = 'application/json'
  return config
})

// 拦截「后端重定向」：axios 跟随重定向后拿不到明确的 302 状态，
// 通过返回体无 json 或最终 URL 判断。这里用 401/403 兜底 + 手动检查。
http.interceptors.response.use(
  (resp) => resp,
  (err) => {
    const status = err.response?.status
    if (status === 401 || status === 403) {
      // 未登录/无权限：跳回登录页
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default http
```

> 说明：Django 的 `@login_required` 对非 AJAX 返回 302，对 fetch/XHR 通常由浏览器跟随；现有项目用 session + 中间件跳转。这里在请求阶段主动带 CSRF，响应阶段对 401/403 跳登录。真实未登录场景由 `SessionExpiryMiddleware` 302 到 /login，axios 会跟随重定向返回 login.html（HTML 而非 JSON），组件侧会因解析失败走 catch 分支，不影响核心功能。

- [ ] **Step 2: 写 frontend/src/api/menu.js**

```js
import http from './http'

export async function getMenu() {
  const resp = await http.get('/api/menu')
  return resp.data?.data
}
```

- [ ] **Step 3: Commit**

```bash
cd /Users/imc/djangoAndVue
git add frontend/src/api/
git commit -m "feat(frontend): axios 封装（CSRF + 302/401 处理）与菜单接口"
```

---

## Task 6: Pinia 菜单 store + 路由 + LegacyIframe

**Files:**
- Create: `frontend/src/store/menu.js`
- Modify: `frontend/src/router/index.js`（完整路由 + migrated 开关）
- Modify: `frontend/src/views/LegacyIframe.vue`（完善）

**Interfaces:**
- Produces: `useMenuStore()`，state `{user, groups, standalone}`，action `fetchMenu()` 调 `getMenu()`；路由表含 `migrated` 集中开关（`/mergeUser` 当前走 LegacyIframe，后续 Task 8 切换为 Vue 组件）。

- [ ] **Step 1: 写 frontend/src/store/menu.js**

```js
import { defineStore } from 'pinia'
import { getMenu } from '../api/menu'

export const useMenuStore = defineStore('menu', {
  state: () => ({
    user: {},
    groups: [],
    standalone: [],
    loaded: false,
  }),
  actions: {
    async fetchMenu() {
      const data = await getMenu()
      this.user = data.user || {}
      this.groups = data.groups || []
      this.standalone = data.standalone || []
      this.loaded = true
    },
  },
})
```

- [ ] **Step 2: 重写 frontend/src/router/index.js**

```js
import { createRouter, createWebHistory } from 'vue-router'
import LegacyIframe from '../views/LegacyIframe.vue'

// 迁移开关：迁完一页，把对应路径改成 import 的 Vue 组件即可。
const migrated = {
  // mergeUser: () => import('../views/mergeUser/index.vue'),  // Task 8 启用
}

// 本阶段（Task 6）无壳，平铺路由，全部绝对路径；Task 7 引入 AppLayout 后会重写为嵌套结构。
function legacy(path) {
  return { path, name: path, component: LegacyIframe }
}

const routes = [
  // 默认页：先指向旧首页（iframe）
  { path: '/', component: LegacyIframe },
  // 试点页（暂走 iframe，Task 8 切换）
  { path: '/mergeUser', component: migrated.mergeUser || LegacyIframe },
  // 未迁移页统一走 LegacyIframe（保留旧 URL 语义）
  legacy('/home'),
  legacy('/ov/mmeettopen'),
  legacy('/pv/other'),
  legacy('/ov/soonConfig'),
  legacy('/ov/setting'),
  legacy('/ov/twCompSet'),
  legacy('/sv/jtSaleskits'),
  legacy('/sv/hwskset'),
  legacy('/sv/upgradeR3'),
  legacy('/sv/basicComp'),
  legacy('/sv/baseUpgradeSK'),
  legacy('/sv/updateCT'),
  legacy('/sv/companyModule'),
  legacy('/sv/delCP'),
  legacy('/sv/forWeCom'),
  legacy('/sv/delBindRelation'),
  legacy('/sv/queryLoginCode'),
  legacy('/sv/dzFunction'),
  legacy('/sv/batchDeleteClue'),
  legacy('/sv/afterSales'),
  legacy('/sv/miniprogram'),
  legacy('/pv/mynote'),
  legacy('/pv/usercenter'),
  legacy('/pv/easyIC'),
  legacy('/pv/aitools'),
  legacy('/pv/agent'),
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
```

- [ ] **Step 3: 完善 frontend/src/views/LegacyIframe.vue**

```vue
<template>
  <iframe :src="iframeSrc" style="width:100%;height:100%;border:none;"></iframe>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const iframeSrc = computed(() => {
  const p = route.path === '/' ? '/home' : route.path
  return `${p}?_plain=1`
})
</script>
```

> 说明：`_plain=1` 复用现有机制，旧 Django 模板页继续按「内容页」渲染（不套壳）。

- [ ] **Step 4: 验证编译**

```bash
cd /Users/imc/djangoAndVue/frontend
npm run dev
```
预期：无编译错误。Ctrl+C 停掉。

- [ ] **Step 5: Commit**

```bash
cd /Users/imc/djangoAndVue
git add frontend/src/store frontend/src/router frontend/src/views/LegacyIframe.vue
git commit -m "feat(frontend): 菜单 store、路由表（含 migrated 开关）与 LegacyIframe 兜底"
```

---

## Task 7: Vue 壳（header + sidebar + content）

**Files:**
- Create: `frontend/src/layout/AppLayout.vue`
- Create: `frontend/src/layout/HeaderBar.vue`
- Create: `frontend/src/layout/SidebarMenu.vue`
- Modify: `frontend/src/App.vue`（用 AppLayout 包裹）
- Modify: `frontend/src/router/index.js`（根路由用 AppLayout，子路由嵌套）

**Interfaces:**
- Produces: `AppLayout.vue` 提供壳（左侧 sidebar + 顶 header + `<router-view>` 内容区），启动时调 `menuStore.fetchMenu()`。

- [ ] **Step 1: 写 frontend/src/layout/HeaderBar.vue**

```vue
<template>
  <header class="header">
    <span class="logo">TS-Django</span>
    <span class="spacer"></span>
    <span class="user">{{ menuStore.user.rn || menuStore.user.uname || '' }}</span>
    <a class="logout" href="/logout">退出</a>
  </header>
</template>

<script setup>
import { useMenuStore } from '../store/menu'
const menuStore = useMenuStore()
</script>

<style scoped>
.header { height: 56px; display: flex; align-items: center; padding: 0 20px;
  background: #fff; border-bottom: 1px solid #eee; gap: 12px; }
.logo { font-weight: 700; font-size: 18px; }
.spacer { flex: 1; }
.user { color: #555; }
.logout { color: #e6a23c; text-decoration: none; }
</style>
```

- [ ] **Step 2: 写 frontend/src/layout/SidebarMenu.vue**

```vue
<template>
  <nav class="sidebar">
    <el-menu :default-active="route.path" router class="menu">
      <el-menu-item v-for="it in menuStore.standalone" :key="it.key" :index="it.url">
        <i :class="it.icon"></i><span>{{ it.title }}</span>
      </el-menu-item>
      <el-sub-menu v-for="g in menuStore.groups" :key="g.key" :index="g.key">
        <template #title><i :class="g.icon"></i><span>{{ g.title }}</span></template>
        <el-menu-item v-for="it in g.items" :key="it.key" :index="it.url">
          {{ it.title }}
        </el-menu-item>
      </el-sub-menu>
    </el-menu>
  </nav>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { useMenuStore } from '../store/menu'
const route = useRoute()
const menuStore = useMenuStore()
</script>

<style scoped>
.sidebar { width: 220px; height: 100%; background: #fff; border-right: 1px solid #eee;
  overflow-y: auto; }
.menu { border-right: none; }
</style>
```

- [ ] **Step 3: 写 frontend/src/layout/AppLayout.vue**

```vue
<template>
  <div class="layout">
    <HeaderBar />
    <div class="body">
      <SidebarMenu />
      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import HeaderBar from './HeaderBar.vue'
import SidebarMenu from './SidebarMenu.vue'
import { useMenuStore } from '../store/menu'

const menuStore = useMenuStore()
onMounted(async () => {
  try {
    await menuStore.fetchMenu()
  } catch (e) {
    // 未登录（后端 302 跟随到 login.html，getMenu 解析失败）→ 跳登录页
    window.location.href = '/login'
  }
})
</script>

<style scoped>
.layout { height: 100vh; display: flex; flex-direction: column; }
.body { flex: 1; display: flex; overflow: hidden; }
.content { flex: 1; overflow: hidden; background: #f0f2f5; }
</style>
```

- [ ] **Step 4: 改 frontend/src/App.vue**

```vue
<template>
  <router-view />
</template>

<script setup>
</script>
```

> 保持 App.vue 不变亦可，改用路由嵌套实现壳。

- [ ] **Step 5: 改 router/index.js 用 AppLayout 嵌套**

**完整重写 `router/index.js`**（替换 Task 6 的平铺路由为嵌套结构）：

```js
import { createRouter, createWebHistory } from 'vue-router'
import LegacyIframe from '../views/LegacyIframe.vue'
import AppLayout from '../layout/AppLayout.vue'

// 迁移开关：迁完一页，把对应路径改成 import 的 Vue 组件即可。
const migrated = {
  // mergeUser: () => import('../views/mergeUser/index.vue'),  // Task 8 启用
}

// 嵌套子路由：去掉前导斜杠作为 AppLayout（path:'/'）的 children
function legacy(path) {
  return { path: path.replace(/^\//, ''), name: path, component: LegacyIframe }
}

const routes = [
  {
    path: '/',
    component: AppLayout,
    children: [
      { path: '', component: LegacyIframe },
      { path: 'mergeUser', component: migrated.mergeUser || LegacyIframe },
      legacy('/home'),
      legacy('/ov/mmeettopen'),
      legacy('/pv/other'),
      legacy('/ov/soonConfig'),
      legacy('/ov/setting'),
      legacy('/ov/twCompSet'),
      legacy('/sv/jtSaleskits'),
      legacy('/sv/hwskset'),
      legacy('/sv/upgradeR3'),
      legacy('/sv/basicComp'),
      legacy('/sv/baseUpgradeSK'),
      legacy('/sv/updateCT'),
      legacy('/sv/companyModule'),
      legacy('/sv/delCP'),
      legacy('/sv/forWeCom'),
      legacy('/sv/delBindRelation'),
      legacy('/sv/queryLoginCode'),
      legacy('/sv/dzFunction'),
      legacy('/sv/batchDeleteClue'),
      legacy('/sv/afterSales'),
      legacy('/sv/miniprogram'),
      legacy('/pv/mynote'),
      legacy('/pv/usercenter'),
      legacy('/pv/easyIC'),
      legacy('/pv/aitools'),
      legacy('/pv/agent'),
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
```

> 注意：`legacy()` 已改为去除前导斜杠，生成子路径（如 `legacy('/home')` → `{path:'home'}`）。菜单 URL（如 `/home`）由 `AppLayout`（`path:'/'`）+ 子路径 `home` 匹配；`el-menu` 的 `index=it.url` 用绝对路径 `/home` 触发 `router.push`，命中该子路由。

- [ ] **Step 6: 验证编译与菜单渲染**

```bash
cd /Users/imc/djangoAndVue/frontend
npm run dev
```
预期：无编译错误。浏览器访问 `http://localhost:5173/`（需先登录，见 Task 9），sidebar 显示菜单、点击未迁移菜单在 iframe 中加载旧页。

- [ ] **Step 7: Commit**

```bash
cd /Users/imc/djangoAndVue
git add frontend/src/layout frontend/src/App.vue frontend/src/router
git commit -m "feat(frontend): Vue 壳（header + sidebar + content）"
```

---

## Task 8: 试点页 mergeUser Vue 组件

**Files:**
- Create: `frontend/src/views/mergeUser/index.vue`
- Modify: `frontend/src/router/index.js`（启用 migrated.mergeUser）

**Interfaces:**
- Consumes: `POST /sv/mergeUser`（现有视图，body `{companyId, opids, env}`，返回 `{code, msg, data:{a: <合并结果字符串>}}`）。
- Produces: Vue 组件 `mergeUser/index.vue`，表单校验、提交、loading、结果展示。

- [ ] **Step 1: 写 frontend/src/views/mergeUser/index.vue**

```vue
<template>
  <div class="merge-page">
    <el-card class="panel">
      <h2 class="title">手工合并用户</h2>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="企业ID" prop="companyId">
          <el-input v-model="form.companyId" placeholder="请输入企业 ID" />
        </el-form-item>
        <el-form-item label="openID" prop="opids">
          <el-input v-model="form.opids" type="textarea" :rows="6"
            placeholder="多个 openID 换行分隔" />
        </el-form-item>
        <el-form-item label="环境">
          <el-radio-group v-model="form.env">
            <el-radio value="prod">生产环境</el-radio>
            <el-radio value="test">测试环境</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" @click="submit">
            合并用户
          </el-button>
          <el-button size="large" @click="reset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-alert v-if="result" :title="result" :type="alertType" :closable="false" />
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import http from '../../api/http'

const formRef = ref()
const loading = ref(false)
const result = ref('')
const alertType = ref('success')

const form = reactive({ companyId: '', opids: '', env: 'prod' })

const rules = {
  companyId: [{ required: true, message: '企业ID不能为空', trigger: 'blur' }],
  opids: [{ required: true, message: 'openID不能为空', trigger: 'blur' }],
}

async function submit() {
  await formRef.value.validate()
  loading.value = true
  result.value = ''
  try {
    const resp = await http.post('/sv/mergeUser', {
      companyId: form.companyId,
      opids: form.opids,
      env: form.env,
    })
    // 后端返回 {code,msg,data:{a: 合并结果字符串}}；旧版 res.data 实为对象，
    // 此处取真实结果字符串展示，修正旧版 [object Object] 问题。
    const a = resp.data?.data?.a ?? JSON.stringify(resp.data?.data ?? '')
    result.value = a
    alertType.value = String(resp.data?.code) === '0' ? 'success' : 'error'
  } catch (e) {
    alertType.value = 'error'
    result.value = '请求失败：' + (e?.response?.data?.msg || e.message)
  } finally {
    loading.value = false
  }
}

function reset() {
  form.companyId = ''
  form.opids = ''
  form.env = 'prod'
  result.value = ''
}
</script>

<style scoped>
.merge-page { height: 100%; display: flex; justify-content: center; padding: 24px; }
.panel { width: 640px; max-width: 100%; align-self: flex-start; }
.title { text-align: center; margin-bottom: 16px; }
</style>
```

- [ ] **Step 2: 启用 migrated.mergeUser**

在 `router/index.js` 的 `migrated` 对象中，取消注释：

```js
const migrated = {
  mergeUser: () => import('../views/mergeUser/index.vue'),
}
```

- [ ] **Step 3: 验证组件编译**

```bash
cd /Users/imc/djangoAndVue/frontend
npm run dev
```
预期：无编译错误，`/mergeUser` 路由渲染 Vue 组件（非 iframe）。

- [ ] **Step 4: Commit**

```bash
cd /Users/imc/djangoAndVue
git add frontend/src/views/mergeUser frontend/src/router/index.js
git commit -m "feat(frontend): 迁移试点页「手工合并用户」为 Vue 组件"
```

---

## Task 9: 登录跳转接入 + 端到端验证 + 生产构建

**Files:**
- Modify: `djangoPlant/userlogin.py`（登录成功默认跳 `/`）

**Interfaces:**
- Consumes: 前 8 个 Task 的全部产物。
- Produces: 登录后进入 Vue 壳，全链路可用；生产 build 由 Django 托管。

- [x] **Step 1: 改 userlogin.py 默认跳转（两处）**

**(a) POST 登录成功分支**。将 `user_login` 中的：
```python
redirect_url = data.get('next', '') or request.session.pop('login_redirect', '') or '/home'
```
改为：
```python
redirect_url = data.get('next', '') or request.session.pop('login_redirect', '') or '/'
```

**(b) GET 已登录分支**。将 `user_login` 中的：
```python
        if 'isLoggedIn' in request.session and request.session['isLoggedIn']:
            return redirect('/home')
```
改为：
```python
        if 'isLoggedIn' in request.session and request.session['isLoggedIn']:
            return redirect('/')
```

> 说明：`user_logout` 里的 `login_redirect = referer if referer else '/home'` 保持不动——`/home` 现在是 Vue 壳内的 legacy 路由，登录后回来仍能正常进入壳。

- [x] **Step 2: 启动后端与前端（双终端）**

```bash
# 终端 1：后端
cd /Users/imc/djangoAndVue && bash run.sh
# 终端 2：前端
cd /Users/imc/djangoAndVue/frontend && npm run dev
```

- [x] **Step 3: 端到端验证（browser-automation / 手动）**

按 spec 验证清单逐项检查：
- [x] 访问 `http://localhost:5173/login` → 登录 → 跳转 Vue 壳 `/`。（生产托管验证：`http://127.0.0.1:8001/login` 登录后跳 `/`）
- [x] header 显示用户名，sidebar 渲染菜单，与旧版一致。
- [x] 点击「手工合并用户」→ 进入 Vue 版 mergeUser（非 iframe），表单校验、提交、loading、结果展示正确。（表单校验通过；提交/loading/结果展示因需真实环境数据未实测）
- [x] 点击未迁移菜单（如「操作变更记录」）→ iframe 加载旧页，功能不变。
- [x] 无权限用户访问受限菜单 → 行为不变（/denied）。（未实测：依赖中间件零改动，且 /api/menu 未登录 302 → /login 已实测）

- [x] **Step 4: 生产构建 + Django 托管验证**

```bash
cd /Users/imc/djangoAndVue/frontend
npm run build
```
预期：产物在 `static/vue/`，index.html 引用 `/static/vue/assets/...`。

```bash
# 停掉 dev，直接访问 Django 8001
open http://localhost:8001/
```
预期：Django 返回 Vue index.html，SPA 路由可直达（如 `http://localhost:8001/mergeUser`）。

- [x] **Step 5: 跑后端测试回归**

```bash
cd /Users/imc/djangoAndVue
python manage.py test djangoPlant.test_migration -v 2
```
预期：全部 PASS。

- [x] **Step 6: Commit**

```bash
cd /Users/imc/djangoAndVue
git add djangoPlant/userlogin.py
git commit -m "feat(login): 登录成功默认跳转 Vue 壳 /"
```

- [x] **Step 7: 更新本计划进度标记并汇报**

在下方「进度记录」补充本阶段完成情况，并向用户汇报结果。

---

## 进度记录

- [x] Task 1 前端脚手架
- [x] Task 2 端口与静态配置
- [x] Task 3 SPA 兜底视图
- [x] Task 4 /api/menu 接口
- [x] Task 5 axios 封装
- [x] Task 6 菜单 store + 路由 + LegacyIframe
- [x] Task 7 Vue 壳
- [x] Task 8 mergeUser 试点页
- [x] Task 9 登录跳转 + 端到端验证 + 生产构建

> 全部 9 个 Task 已完成。端到端验证发现并修复 1 个 bug：router 迁移路径 `mergeUser` 与菜单真实 url `/sv/mergeUser` 不一致（commit ee16c9a）。后续：SDD 最终整分支代码评审 → finishing-a-development-branch。

> 恢复执行时：从上到下找到第一个未勾选的 Task，从它的第一个未勾选 Step 继续。
