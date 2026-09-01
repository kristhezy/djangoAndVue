# 迁移「登录验证相关」页面 实现计划（第二阶段第 8 页）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把「登录验证相关」从 Django 模板 + jQuery（AT_aboutLogin.html）迁移为 Vue3 + Element Plus 组件，复用现有后端接口（零改动）。

**Architecture:** 沿用方案 B：`frontend/src/views/aboutLogin/index.vue` 新建组件，菜单 url 改写为 `/aboutLogin`（避开真实旧路由 `/sv/queryLoginCode`），POST 复用旧视图。

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
- **UI 组件库**：Element Plus 2.8.4（el-radio 用 `value`；el-form 用 `label-width="auto"`）。
- **后端接口**：复用现有视图，**零改动**。返回 `{code, msg, data}`。
- **不删**：`templates/AT_aboutLogin.html`、`saasview.py` 的 `queryLoginCode`/`splc` 视图。
- **分支**：直接在 `main` 上继续。每步提交。
- **Python**：`/Users/imc/vllm/yes/envs/py310/bin/python3`。
- **CSRF**：`frontend/src/api/http.js` 统一加 header。
- **e2e 只读验证**：查询验证码/设置验证码是真实写/查操作，e2e 只验证「渲染 + 校验 + 图片墙」，不真实提交。

---

## 后端契约（零改动，直接复用）

| 卡片 | 接口 | 请求体 | 返回 `data` |
|---|---|---|---|
| 1 查询验证码 | `/sv/queryLoginCode` | `{tel, env}` | 字符串 |
| 2 设置固定验证码 | `/sv/splc` | `{tel, code, role, env}`（role=partner）或 `{cid, tel, code, role, env}`（role=sale） | 字符串 |
| 3 小程序码 | 无接口，纯静态图片 | — | — |

**字段注意：**
- 卡片1 环境**只有 test**（默认 test，固定）。
- 卡片2 `role`：`sale`（销售，默认，需企业ID）/ `partner`（推荐官，隐藏企业ID）。
- 卡片2 校验：sale 时 cid 非空且 ≥18 位纯数字；tel 11 位纯数字；code 4 位纯数字。
- 卡片3 小程序码 9 张图，路径 `/static/img/{name}.png`，点击放大。

### 小程序码图片（9 张，复刻 AT_aboutLogin.html 第 161-169 行）

`jdkf` `jdcs` `mdcszy` `hxbd` `dzhx` `wfw666` `jtmp` `jtty` `cjzsbys`

---

## Task 1: 前端 aboutLogin/index.vue 组件（三卡片 + 图片墙 + 校验）

**Files:** Create `frontend/src/views/aboutLogin/index.vue`

- [ ] Step 1 写组件（卡片2 role 切换用 v-show 控制企业ID显隐；图片墙点击放大用 el-image 的 preview）
- [ ] Step 2 语法自检（Task 3 build 验证）
- [ ] Step 3 Commit

## Task 2: 菜单 url 改写 + 路由接入 + 后端测试

- [ ] Step 1 `MIGRATED` 增加 `'aboutLogin': '/aboutLogin'`
- [ ] Step 2 router `migrated` 增加 + 替换 `legacy('/sv/queryLoginCode')`
- [ ] Step 3 test_migration.py 新增断言（tools 分组）
- [ ] Step 4 跑测试
- [ ] Step 5 Commit

## Task 3: 端到端验证 + 生产构建 + 文档更新

- [x] Step 1 `npm run build`（通过）
- [x] Step 2 只读 e2e：0 iframe；三卡片标题齐全；note 在；小程序码 9 图；role 切换企业ID显隐正确（销售显示/推荐官隐藏）；sale cid 空校验正确；console 0 错误。
- [x] Step 3 更新 spec 验证清单
- [x] Step 4 更新进度并汇报

> 只读验证：未真实提交。临时 e2e 账号 e2e_aboutlogin 已删除。

---

## 进度记录

- [x] Task 1 前端组件
- [x] Task 2 菜单+路由+测试
- [x] Task 3 构建+e2e+文档
