# 迁移「定制企业功能」页面 实现计划（第二阶段第 9 页）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把「定制企业功能」从 Django 模板 + jQuery（AT_dzFunction.html）迁移为 Vue3 + Element Plus 组件，复用现有后端接口（零改动）。

**Architecture:** 沿用方案 B：`frontend/src/views/dzFunction/index.vue` 新建组件，菜单 url 改写为 `/dzFunction`（避开真实旧路由 `/sv/dzFunction`），POST 复用旧视图。

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
- **不删**：`templates/AT_dzFunction.html`、`saasview.py` 的 `dzFunction` 视图。
- **分支**：直接在 `main` 上继续。每步提交。
- **Python**：`/Users/imc/vllm/yes/envs/py310/bin/python3`。
- **CSRF**：`frontend/src/api/http.js` 统一加 header。
- **e2e 只读验证**：两卡片都是真实写操作，e2e 只验证「渲染 + 校验」，不真实提交。

---

## 后端契约（零改动，直接复用）

| 卡片 | 接口 | 请求体 | 返回 `data` |
|---|---|---|---|
| 1 红蚂蚁修改客户阶段 | `/sv/dzFunction` | `{cfid, fs, env, type:"hmyupdcs"}` | 字符串 |
| 2 华为云license激活 | `/sv/dzFunction` | `{compid, lisence, remark, env, type:"hwylicensejh"}` | 字符串 |
| 3 预留 | 无接口，纯静态 | — | — |

**字段注意：**
- 卡片1 校验：cfid、fs 非空。
- 卡片2 校验：lisence 非空（旧版只校验 lisence，compid/remark 虽标 required 但未在前端校验）。
- 卡片3 是「预留功能区域」纯占位文案。

---

## Task 1: 前端 dzFunction/index.vue 组件（三卡片 + 校验）

**Files:** Create `frontend/src/views/dzFunction/index.vue`

- [ ] Step 1 写组件（卡片1/2 表单 + 卡片3 占位）
- [ ] Step 2 语法自检（Task 3 build 验证）
- [ ] Step 3 Commit

## Task 2: 菜单 url 改写 + 路由接入 + 后端测试

- [ ] Step 1 `MIGRATED` 增加 `'dzFunction': '/dzFunction'`
- [ ] Step 2 router `migrated` 增加 + 替换 `legacy('/sv/dzFunction')`
- [ ] Step 3 test_migration.py 新增断言（tools 分组）
- [ ] Step 4 跑测试
- [ ] Step 5 Commit

## Task 3: 端到端验证 + 生产构建 + 文档更新

- [x] Step 1 `npm run build`（通过）
- [x] Step 2 只读 e2e：0 iframe；三卡片标题齐全；预留区文案在；卡片1「必填项不能为空！」、卡片2「"lisence"不能为空！」校验正确；console 0 错误。
- [x] Step 3 更新 spec 验证清单
- [x] Step 4 更新进度并汇报

> 只读验证：未真实提交。临时 e2e 账号 e2e_dzfn 已删除。

---

## 进度记录

- [x] Task 1 前端组件
- [x] Task 2 菜单+路由+测试
- [x] Task 3 构建+e2e+文档
