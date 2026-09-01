# 迁移「解除绑定关系」页面 实现计划（第二阶段第 7 页）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把「解除绑定关系」从 Django 模板 + jQuery（AT_delBindRelation.html）迁移为 Vue3 + Element Plus 组件，复用现有后端接口（零改动）。

**Architecture:** 沿用方案 B：`frontend/src/views/delBindRelation/index.vue` 新建组件，菜单 url 改写为 `/delBindRelation`（避开真实旧路由 `/sv/delBindRelation`），POST 复用旧视图。

**Tech Stack:** Vue3 + Element Plus 2.8.4 + axios；Django 5.2（零改动）。

**设计文档:** `docs/superpowers/specs/2026-08-28-django-vue3-migration-design.md`（第 10 节）

---

## 断点续作约定（硬约束）

1. 本文件是**进度的单一真相**。每完成一步立即更新 checkbox。
2. 恢复时读本文件 checkbox 恢复「做到哪」。
3. 禁止依赖对话记忆判断进度。

---

## Global Constraints

- **端口**：Django 统一 **8001**。
- **前端语言**：JavaScript。
- **UI 组件库**：Element Plus 2.8.4（el-radio 用 `value`；el-form 用 `label-width="auto"` 避免 label 换行）。
- **后端接口**：复用现有视图，**零改动**。返回 `{code, msg, data}`。
- **不删**：`templates/AT_delBindRelation.html`、`saasview.py` 的 `delBindRelation`/`cleanAppToken`、`forWechatCom` 视图。
- **分支**：直接在 `main` 上继续。每步提交。
- **Python**：`/Users/imc/vllm/yes/envs/py310/bin/python3`。
- **CSRF**：`frontend/src/api/http.js` 统一加 header。
- **e2e 只读验证**：三卡片都是真实写/清操作，e2e 只验证「渲染 + 校验」，不真实提交。

---

## 后端契约（零改动，直接复用）

| 卡片 | 接口 | 请求体 | 返回 `data` |
|---|---|---|---|
| 1 清除公众号/小程序绑定 | `/sv/forWeCom` | `{companyId, appId, status, env, type:3}` | 字符串 |
| 2 清除过期企业信息 | `/sv/delBindRelation` | `{companyIds, env}` | 字符串，多条用 `<br/>` 拼接 |
| 3 清除app登录token | `/sv/cleanAppToken` | `{companyId, env}` | 字符串 |

**字段注意：**
- 卡片1 `status` 是字符串 `"0"/"1"/"2"`（默认 "0"）。
- 卡片2 `companyIds` 后端用 `shd`（逗号/换行/空格）分隔，可多企业。
- 卡片2 返回含 `<br/>`，前端需转为换行展示（文本插值 + pre-wrap，替换 `<br>` → `\n`）。

### 卡片1 应用ID下拉硬编码（5 项）

| value | label |
|---|---|
| wx_oa | 公众号 |
| card | 小程序 |
| cpe_backlog | 自建应用 |
| cpe_investment_applet | 招商/推广版小程序 |
| cpe_partner_applet | 合伙人小程序 |

### 卡片1 Status 下拉：`0` / `1` / `2`（默认 `0`）

---

## Task 1: 前端 delBindRelation/index.vue 组件（三卡片 + 校验）

**Files:** Create `frontend/src/views/delBindRelation/index.vue`

- [ ] Step 1 写组件（三卡片，label-width="auto"，result 文本插值 + pre-wrap + `<br>`→`\n`）
- [ ] Step 2 语法自检（Task 3 build 验证）
- [ ] Step 3 Commit

## Task 2: 菜单 url 改写 + 路由接入 + 后端测试

- [ ] Step 1 `MIGRATED` 增加 `'delBindRelation': '/delBindRelation'`
- [ ] Step 2 router `migrated` 增加 + 替换 `legacy('/sv/delBindRelation')`
- [ ] Step 3 test_migration.py 新增断言（tools 分组）
- [ ] Step 4 跑测试
- [ ] Step 5 Commit

## Task 3: 端到端验证 + 生产构建 + 文档更新

- [x] Step 1 `npm run build`（通过）
- [x] Step 2 只读 e2e：0 iframe；三卡片标题齐全；notice 提示区在；应用ID下拉 5 项；校验「"企业ID"不能为空！」正确；console 0 错误。
- [x] Step 3 更新 spec 验证清单
- [x] Step 4 更新进度并汇报

> 只读验证：未真实提交。临时 e2e 账号 e2e_delbind 已删除。

---

## 进度记录

- [x] Task 1 前端组件
- [x] Task 2 菜单+路由+测试
- [x] Task 3 构建+e2e+文档
