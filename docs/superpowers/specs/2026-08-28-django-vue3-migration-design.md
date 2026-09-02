# Django 模板 → Django + Vue3 + Vite 迁移设计文档

- **日期**: 2026-08-28
- **状态**: 已评审，待实现
- **关联文档**: 实现计划见 `docs/superpowers/plans/2026-08-28-django-vue3-migration-plan.md`（writing-plans 阶段产出）

---

## 0. 断点续作要求（本项目的硬约束）

本迁移周期长、步骤多，**必须在任意一次对话中断后仍能无缝继续**。为此确立以下约定，实现计划（plan）文件严格遵循：

1. **两份文档各司其职**：
   - 本设计文档 = 「目标态」：回答「改什么、为什么这么改、怎么定」。内容稳定，不随进度变化。
   - 实现计划（plan）= 「当前进度」：把迁移拆成一系列**可勾选的小步骤**，每步带状态 `[ ] 未开始 / [~] 进行中 / [x] 已完成 / [!] 阻塞`。
2. **plan 是进度的单一真相**：每完成一步、遇到阻塞、或决定跳过某步，**立即**更新 plan 的对应勾选状态与备注，再做别的事。
3. **断连恢复流程**：用户把这两个文件丢给新会话 → 从 spec 恢复「为什么/怎么做」，从 plan 的勾选恢复「做到哪」，直接接下一步。
4. **禁止**：依赖对话记忆判断进度；禁止在 plan 滞后时靠重新扫描代码库「猜」进度。

---

## 1. 背景与现状

现有系统 `hzy_django` 是一个基于 **Django 5.2 + Django 模板（服务端渲染）+ jQuery/axios** 的本地内部管理后台，用于支持接口调用的日常工作。

### 1.1 现状关键特征

- **「壳 + iframe」结构**：`shell.html` 渲染 header + sidebar，内容页通过 `<iframe>` 以 `?_plain=1` 加载（`base.html` 内判断）。已是「半 SPA」的壳。
- **后端已半 API 化**：视图函数 `GET` 返回 `render()` 的 HTML 页面，`POST` 返回 `JsonResponse` JSON。数据接口大多已存在，只是与页面渲染耦合在同一视图函数内。
- **认证与权限**：Django session（cookie）+ CSRF；`menu_registry.py` 是菜单 key→URL 唯一写死点；`MenuPermissionMiddleware` 按 `request.path` 反查菜单 key 做权限拦截。
- **菜单数据三处来源**（迁移 `/api/menu` 时需合并）：
  1. `djangoPlant/config/text_config.py` 的 `SITE_CONFIG`：菜单 URL + 显示名 + 图标引用。
  2. `templates/partials/sidebar.html`：菜单结构、分组（`has_any_menu` 分组）、顺序。
  3. `djangoPlant/menu_registry.py`：`MENU_MAP`（key→url）、`PUBLIC_MENUS`/`ADMIN_MENUS`、`match_menu_key()`。

### 1.2 规模

- 约 **35 个模板**，其中多个超大（`soonConfig.html` 48KB、`MmeettOpen.html` 44KB、`mmeettTreeView.html` 42KB 等）。
- 视图文件巨大（`saasview.py` 79KB / 1801 行、`originview.py` 59KB / 1232 行、`publicview.py` 32KB / 813 行）。
- 前端 JS 重（`mmeettOpen.js` 67KB、`other.js` 22KB 等）。
- 涉及 AI Agent 流式输出（SSE）、微信小程序、SaaS 配置等复杂功能。

> 结论：体量大的内部工具，**必须渐进式迁移，不能一次性全切**。

---

## 2. 目标与决策记录

### 2.1 目标（四个，均需满足）

1. **技术栈现代化**：摆脱 jQuery/模板，组件化 Vue3 提升可维护性。
2. **前后端彻底分离**：Django 只做 JSON API，前端独立 Vite 工程。
3. **改善用户体验**：去掉 iframe 割裂感，收敛为真 SPA。
4. **渐进式、低风险**：新旧共存、可随时回退、优先不破坏现有功能。

### 2.2 决策记录（已与用户确认，不可随意更改）

| 决策项 | 结论 | 理由 |
|---|---|---|
| 迁移方案 | **方案 B：Vue 新壳 + iframe 兜底旧页** | 同时满足「彻底分离（最终态）」与「渐进低风险（过程）」 |
| UI 组件库 | **Element Plus** | 国内流行、中文文档好、适合后台管理 |
| 前端语言 | **JavaScript**（不用 TS） | 单人本地工具，后端 JSON 弱类型，TS 收益低、成本高、可逆（后续可逐步加） |
| 后端接口层 | **复用现有视图** | 现有视图已是 GET 页面 + POST JSON 模式，接口大多已存在 |
| 认证方式 | **保持 session + CSRF** | 零改动，中间件/权限原样复用 |
| 菜单数据 | **新增 `/api/menu`** | 权限单一数据源不变，Vue 壳用接口渲染 |
| 迁移节奏 | **先壳后页，试点跑通** | 渐进低风险 |
| 试点页面 | **AT_mergeUser（合并用户）** | 依赖最轻，覆盖「表单→接口→展示」最常见模式 |
| 部署方式 | **Django 托管构建产物** | 一套代码本地/局域网都能用 |
| **端口** | **8001**（8000 被旧项目占用） | 用户指定，全局统一 |

---

## 3. 总体架构

```
浏览器
  │
  ├─ 开发: Vite dev (5173) ──proxy──▶ Django (8001)
  │         └─ /api, /sv, /ov, /pv, /static, /login, /logout
  │
  └─ 生产: Django 托管 (8001)
            ├─ /api/* , /sv/* , /ov/* , /pv/*   → 现有 JSON 视图
            ├─ /static/*                          → 现有静态 + vite build 产物
            └─ / (其他非 API 路径)                 → 返回 Vue 的 index.html（SPA 兜底）
```

- **Django 保持现状**：现有 30+ 视图、中间件、session、权限、数据库全部不动。
- **新增 `frontend/` Vue 工程**，独立目录、独立依赖。
- **后端只新增**：① `/api/menu` 接口；② 一个 SPA 兜底视图（`/` 指向 Vue index.html）。

---

## 4. 目录结构

```
djangoAndVue/
├── djangoPlant/              # 现有后端（尽量不动）
│   ├── urls.py               # + 新增 /api/menu、SPA 兜底路由
│   ├── api_menu.py           # + 新增菜单接口
├── templates/                # 旧模板（保留，作 iframe 兜底 & 回退）
├── static/                   # 旧静态（保留）
└── frontend/                 # 新建 Vue3 + Vite + JS + Element Plus
    ├── src/
    │   ├── main.js
    │   ├── App.vue
    │   ├── router/index.js
    │   ├── api/              # axios 封装 + CSRF + 302 处理
    │   ├── layout/           # 壳：header + sidebar + content
    │   ├── views/
    │   │   ├── LegacyIframe.vue        # 兜底旧页（iframe 内嵌）
    │   │   └── mergeUser/index.vue     # 试点页
    │   └── store/menu.js     # Pinia：菜单状态
    ├── vite.config.js        # dev proxy → 8001
    └── package.json
```

---

## 5. 端口与运行时配置（统一 8001）

| 位置 | 改动 |
|---|---|
| Django 开发服务器 | `run.sh` / 启动命令端口改为 **8001** |
| Vite dev proxy | 目标 `http://localhost:8001` |
| `ALLOWED_HOSTS` | 增加 `localhost:8001` / `127.0.0.1:8001`（或保持 host 名配置） |
| `CSRF_TRUSTED_ORIGINS` | 增加 `http://localhost:8001`、`http://localhost:5173`（dev 时前端源） |

---

## 6. 认证与 CSRF（零改动）

- 登录仍走 Django `/login`（渲染 `login.html`），登录后 redirect 到 Vue 壳 `/`。
- session cookie 全局有效；`CSRF_COOKIE_HTTPONLY = False` 已满足前端读 token 要求。
- 前端 axios 封装：每次请求自动从 cookie 读 `csrftoken` 放入 `X-CSRFToken` header（与现有 `base.html` 中 `header` 对象一致）。
- 响应拦截器：
  - 302 → `/login`（未登录）：前端跳转登录页。
  - 302 → `/denied`（无权限）：前端提示无权限。
- **`MenuPermissionMiddleware` 零改动**：它只拦截 `MENU_MAP` 命中的路径，`/api/*` 不在其中会自动放行。

---

## 7. `/api/menu` 接口设计

- 新增 `@login_required` 的 `GET /api/menu`，返回当前用户可见菜单树。
- **数据来源合并三处**（见 1.1）：
  - 权限：`request.session['menus']`（用户可见的菜单 key 列表）。
  - 结构/分组/顺序/图标/显示名/key→url：统一从 `SITE_CONFIG`（`text_config.py`）抽成结构化数据（与旧 `sidebar.html` 渲染用同一来源，保证 Vue 侧边栏与旧版 url 一致）。**迁移中少数需动旧文件的地方，但只是「读出来」，不改变旧渲染逻辑**。
  - `menu_registry.MENU_MAP` 保持不动——它仍是 `MenuPermissionMiddleware` 做 path→key 反查的权限映射，与菜单渲染 url 是两回事。
- 返回结构（示意）：

```json
{
  "code": "0",
  "data": {
    "user": { "uname": "...", "rn": "..." },
    "groups": [
      { "title": "SAAS企业开户配置", "items": [
          { "key": "jtSaleskits", "title": "加推Saleskits", "url": "/sv/jtSaleskits", "icon": "fa-solid fa-bars-progress" }
      ]},
      { "title": "SAAS辅助工具", "items": [ ... ] }
    ],
    "standalone": [
      { "key": "home", "title": "AT-首页", "url": "/home", "icon": "fa-solid fa-house" }
    ]
  }
}
```

> 注：图标当前在 `text_config.py` 的 `ICONS` 中以完整 `<i>` 标签存储。Vue 侧统一用 FontAwesome class 渲染，`/api/menu` 返回 class 字符串（如 `fa-solid fa-house`）而非 HTML 标签。

---

## 8. Vue 壳设计

- **header**：用户信息（来自 `/api/menu` 返回的 `user` 字段）+ 退出登录。
- **sidebar**：渲染 `/api/menu` 菜单树，高亮当前路由，分组折叠。
- **content**：`<router-view>`。
- **路由策略**（渐进开关）：
  - 已迁移页 → Vue 组件（如 `/mergeUser` → `mergeUser/index.vue`）。
  - 未迁移页 → `LegacyIframe.vue`，`<iframe src="/旧URL?_plain=1">`，复用现有 `_plain` 机制，旧页继续用 Django 模板 + jQuery 跑，完全不受影响。
  - 用集中配置（如 `migrated: true/false`）控制某页走 Vue 还是 iframe，单行开关即可回退单页。
- **效果**：从「全 iframe」收敛到「Vue + 旧页 iframe 共存」，每迁一页少一个 iframe。

---

## 9. 试点页 `mergeUser` 迁移

### 9.1 后端

- `saasview.py` 的 `mergeUser` 视图 POST 接口**完全复用，零改动**。
- 已接收 `{companyId, opids, env}`，返回 `get_result(code, msg, result)` 的 JSON。
- `result.a` 是字符串（`str(allrlt)` 转成），形如 `"{'openid1': '用户合并成功!', ...}"`。

### 9.2 前端

新建 `frontend/src/views/mergeUser/index.vue`，Element Plus 重写：

| 旧实现（jQuery） | 新实现（Vue3 + Element Plus） |
|---|---|
| `<input id='companyId'>` | `el-input`，绑定 `form.companyId` |
| `<textarea id='openId'>` | `el-input type="textarea"`，绑定 `form.opids` |
| 两个 radio（prod/test） | `el-radio-group`，默认 `prod` |
| `alert()` 非空校验 | `el-form` 校验规则 + `ElMessage` |
| `result.innerHTML = loading.gif` | `v-loading` 指令 |
| `result.innerHTML = res.data` | `el-alert` / `el-card` 展示结果 |

### 9.3 待确认项（实现阶段核实）

- [ ] 后端返回的 `result.a` 是 Python dict 的字符串表示，前端需决定：直接字符串展示，还是做友好解析（如按 openId 逐行展示成功/失败）。**倾向友好解析**，但需先看真实返回样例确认字段格式。

---

## 10. 迁移与回退流程

### 10.1 单页迁移流程（每个页面重复）

1. 后端：确认/新增干净 JSON 接口（大多已存在）。
2. 前端：新建 `views/<name>/index.vue`，Element Plus 重写，调用同一接口。
3. 路由：把 `LegacyIframe` 的该条目换成 Vue 组件路由（改 `migrated` 开关）。
4. 验证：dev 跑通 → 生产构建验证。
5. 回退：改回 `migrated: false`，该页自动回 iframe 旧版。

### 10.2 回退与安全网

- **旧模板/静态完全不删**：迁移是「新增 Vue 组件 + 改路由指向」，旧 `AT_mergeUser.html` 和 `mergeUser` 视图原样保留。
- **渐进开关**：`migrated: true/false` 单行回退单页。
- **git 独立分支**：迁移在独立分支进行，可整体回退到迁移前。

---

## 11. 验证清单

- [x] 登录 → 跳转 Vue 壳，header/sidebar 正常渲染，菜单与旧版一致。
- [x] 点击「手工合并用户」→ Vue 版 mergeUser，表单校验、提交、loading、结果展示正确。
- [x] 点击「操作变更记录」→ Vue 版 other 列表，筛选/查询/分页/删除正确，刷新 `/other` 仍是 Vue 版（非 iframe）。
- [x] 点击「我的记录」→ Vue 版 mynote 卡片列表，查询/新增/编辑/删除正确，正文 URL 识别为链接，刷新 `/mynote` 仍是 Vue 版（非 iframe）。
- [x] 点击「删除线索[合]」→ Vue 版 delCP 三卡片，企业下拉（prod/test 两组）、选企业联动（回填企业ID + 锁环境）、删除类型切换（合伙人ID禁用/启用）、卡片2校验 + 只读查询回填均正确，刷新 `/delCP` 仍是 Vue 版（非 iframe，0 iframe）。
- [x] 点击「批量删除线索」→ Vue 版 batchDeleteClue 单卡片，企业下拉（2 家）、手机号 textarea、环境 radio、校验正确，刷新 `/batchDeleteClue` 仍是 Vue 版（非 iframe，0 iframe）。
- [x] 点击「企业微信相关」→ Vue 版 forWeCom 双卡片（生成企微应用链接 / 获取密文企微ID），应用ID下拉 8 项、校验正确，刷新 `/forWeCom` 仍是 Vue 版（非 iframe，0 iframe）。
- [x] 点击「解除绑定关系」→ Vue 版 delBindRelation 三卡片（清绑定 / 清过期企业 / 清token），应用ID下拉 5 项、校验正确，刷新 `/delBindRelation` 仍是 Vue 版（非 iframe，0 iframe）。
- [x] 点击「登录验证相关」→ Vue 版 aboutLogin 三卡片（查验证码 / 设固定验证码 / 小程序码9图），role 切换企业ID显隐、校验正确，刷新 `/aboutLogin` 仍是 Vue 版（非 iframe，0 iframe）。
- [x] 点击「定制企业功能」→ Vue 版 dzFunction 三卡片（红蚂蚁改阶段 / 华为license / 预留区），校验正确，刷新 `/dzFunction` 仍是 Vue 版（非 iframe，0 iframe）。
- [x] 点击「加推Saleskits」→ Vue 版 jtSaleskits 双栏（配置 / 执行结果），5 个企业模块勾选、版本切换（招商版显示模块 / 家装版隐藏模块+显示家装类型+禁用测试环境）、空提交校验、右侧只读操作记录列表，刷新 `/jtSaleskits` 仍是 Vue 版（非 iframe，0 iframe）。
- [x] 点击「华为云SK配置」→ Vue 版 hwskset 双栏（配置 / 执行结果），手机号查询企业ID回填、付款方式下拉、5 个企业模块勾选、空提交校验，刷新 `/hwskset` 仍是 Vue 版（非 iframe，0 iframe）。
- [x] 点击「转介绍3.0配置」→ Vue 版 upgradeR3 双栏（配置 / 执行结果），企业ID+席位 textarea、空提交校验、提交后显示结果+菜单SQL+复制跳转按钮，刷新 `/upgradeR3` 仍是 Vue 版（非 iframe，0 iframe）。
- [x] 点击「销售工具版配置」→ Vue 版 basicComp 双栏（配置 / 执行结果），企业IDs textarea、8 模块勾选（M115 禁用、6 默认勾选）、空提交校验，刷新 `/basicComp` 仍是 Vue 版（非 iframe，0 iframe）。
- [x] 执行结果 message 的 HTML 加粗/换行标签已通过公共 `OperationLog` 组件安全净化渲染（先转义再还原 `<b>`/`<br/>`，防 XSS）。
- [x] 点击「工具版升级SK」→ Vue 版 baseUpgradeSK 单卡片（企业数据 3 textarea + 6 模块勾选 + 环境 + 结果），空提交校验，刷新 `/baseUpgradeSK` 仍是 Vue 版（非 iframe，0 iframe）。
- [x] 点击「企业模块配置」→ Vue 版 companyModule（企业IDs + 6 组 40 模块勾选，M107 互斥、增加/删除模块切换），空提交校验，刷新 `/companyModule` 仍是 Vue 版（非 iframe，0 iframe）。
- [ ] 点击其他未迁移菜单（如「设置」）→ LegacyIframe，旧页功能与迁移前一致。
- [ ] 无权限用户访问 → 被中间件拦到 `/denied`，行为不变。
- [ ] 生产构建：`npm run build` → Django 托管，局域网 `192.168.10.7:8001` 可访问。

---

## 12. 明确不做（YAGNI）

- **不引入 DRF**：复用现有视图，避免 serializer 重写成本。
- **不改认证为 JWT**：保持 session + CSRF。
- **不一次性迁移所有页面**：先壳后页，试点跑通再批量。
- **不删旧模板/静态**：保留作 iframe 兜底与回退。
- **不上 TypeScript**（本次）：单人本地工具，收益不足以覆盖成本。
