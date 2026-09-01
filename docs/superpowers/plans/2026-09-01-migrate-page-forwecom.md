# 迁移「企业微信相关」页面 实现计划（第二阶段第 6 页）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把「企业微信相关」从 Django 模板 + jQuery（AT_wecom.html + 内联 JS）迁移为 Vue3 + Element Plus 组件，复用现有后端接口（零改动）。

**Architecture:** 沿用方案 B：`frontend/src/views/forWeCom/index.vue` 新建组件，菜单 url 由 `/api/menu` 改写为独立前端路径 `/forWeCom`（避开真实旧路由 `/sv/forWeCom`），POST 复用旧视图 `/sv/forWeCom` 的 POST 分支。

**Tech Stack:** Vue3 + Element Plus 2.8.4 + axios（已有）；Django 5.2（零改动）。

**设计文档:** `docs/superpowers/specs/2026-08-28-django-vue3-migration-design.md`（第 10 节「单页迁移流程」）

---

## 断点续作约定（硬约束）

1. 本文件是**进度的单一真相**。每完成一步、遇到阻塞、跳过某步，**立即**更新对应 checkbox 状态。
2. 恢复时：读 spec 恢复「为什么」，读本文件 checkbox 恢复「做到哪」，直接接下一步。
3. 禁止依赖对话记忆判断进度。

---

## Global Constraints

- **端口**：Django 统一用 **8001**。
- **前端语言**：JavaScript（不用 TypeScript）。
- **UI 组件库**：Element Plus 2.8.4（el-radio 用 `value` 属性）。
- **后端接口**：复用现有视图，**零改动**。返回 `{code, msg, data}`。
- **不删**：`templates/AT_wecom.html`、`saasview.py` 的 `forWechatCom` 视图。
- **分支**：直接在 `main` 上继续。每步提交。
- **Python 解释器**：`/Users/imc/vllm/yes/envs/py310/bin/python3`。
- **CSRF**：POST 由 `frontend/src/api/http.js` 统一加 `X-CSRFToken`。
- **e2e 只读验证**：生成链接会 `window.open` 外链、获取密文是真实接口，e2e 只验证「页面渲染 + 表单校验」，不真实提交。

---

## 后端契约（零改动，直接复用）

| 接口 | method | 请求体 | 返回 `data` |
|---|---|---|---|
| `/sv/forWeCom` | POST | `{companyId, appId, env, type:1}` | 字符串（企微授权链接，含 `http`） |
| `/sv/forWeCom` | POST | `{corpId, env, type:2}` | 字符串（密文 corpId） |

**字段注意：**
- 视图还支持 `type:3`（清除公众号/小程序绑定），但旧模板无对应 UI，迁移不新增，保持与旧版一致。
- 卡片1 返回含 `http` 时旧版会 `window.open(res.data)` 打开授权链接；迁移后保留此行为。

### 卡片1 应用ID下拉硬编码（复刻 AT_wecom.html 第 82-90 行）

| value | label |
|---|---|
| cpe_tong | 通讯录 |
| cpe_radar | 雷达 |
| cpe_file | 文件 |
| cpe_article | 文章 |
| cpe_video | 视频 |
| cpe_poster | 海报 |
| cpe_manual | 宣传册 |
| cpe_case | 案例 |

---

## Task 1: 前端 forWeCom/index.vue 组件（双卡片 + 校验）

**Files:**
- Create: `frontend/src/views/forWeCom/index.vue`

- [ ] **Step 1: 写组件**（见组件代码，下同结构：卡片1 生成链接 / 卡片2 获取密文）

- [ ] **Step 2: 语法自检**：由 Task 3 `npm run build` 验证。

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/forWeCom/index.vue
git commit -m "feat(frontend): 迁移「企业微信相关」为 Vue 双卡片组件"
```

---

## Task 2: 菜单 url 改写 + 路由接入 + 后端测试

- [ ] **Step 1: api_menu.py 的 MIGRATED 增加 forWeCom** → `'forWeCom': '/forWeCom',`

- [ ] **Step 2: router 接入**：`migrated` 增加 `forWeCom`；`legacy('/sv/forWeCom')` 改为 `{ path: 'forWeCom', component: migrated.forWeCom || LegacyIframe }`。

- [ ] **Step 3: 后端测试新增断言**（forWeCom 在 tools 分组）：

```python
    def test_forwecom_menu_url_rewritten_to_frontend_path(self):
        s = self.c.session
        s['menus'] = ['forWeCom']
        s.save()
        resp = self.c.get('/api/menu')
        data = resp.json()['data']
        item = next(x for x in data['groups'][0]['items'] if x['key'] == 'forWeCom')
        self.assertEqual(item['url'], '/forWeCom')
```

- [ ] **Step 4: 跑后端测试** → 预期全 PASS。

- [ ] **Step 5: Commit**

---

## Task 3: 端到端验证 + 生产构建 + 文档更新

- [x] **Step 1: 生产构建** `npm run build`（通过）
- [x] **Step 2: 只读 e2e**：直达 `/forWeCom` → 0 iframe；两卡片标题齐全；应用ID下拉 8 项；校验（cid 非 18/19 位 → 提示「企业ID只能是18或19位的纯数字！」；corpId 空 → 提示「"企微ID(明文)"不能为空！」）；刷新仍 Vue 版（console 0 错误）。
- [x] **Step 3: 更新 spec 验证清单**
- [x] **Step 4: 更新本计划进度标记并汇报**

> 只读验证：未真实触发生成链接/获取密文。临时 e2e 账号 e2e_forwecom 已删除。

---

## 进度记录

- [x] Task 1 前端 forWeCom/index.vue 组件
- [x] Task 2 菜单 url 改写 + 路由接入 + 后端测试
- [x] Task 3 端到端验证 + 生产构建 + 文档更新
