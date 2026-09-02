# 迁移「工具版升级SK」页面 实现计划（compconfig 组第 5 页 / 组内最后 1 页）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把「工具版升级SK」从 Django 模板 + jQuery（OP_baseUpgradeSK.html）迁移为 Vue3 + Element Plus 组件，复用现有后端接口（零改动）。

**Architecture:** 沿用方案 B：`frontend/src/views/baseUpgradeSK/index.vue` 新建组件，菜单 url 改写为 `/baseUpgradeSK`（避开真实旧路由 `/sv/baseUpgradeSK`），POST 复用旧视图。

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
- **不删**：`templates/OP_baseUpgradeSK.html`、`saasview.py` 的 `baseUpgradeSK` 视图、`static/js/baseUpgradeSK.js`。
- **分支**：直接在 `main` 上继续。每步提交。
- **Python**：`/Users/imc/vllm/yes/envs/py310/bin/python3`。
- **CSRF**：`frontend/src/api/http.js` 统一加 header。
- **e2e 只读验证**：提交是真实写操作，e2e 只验证「渲染 + 校验 + 只读查询」，不真实提交。

---

## 后端契约（零改动，直接复用）

| 接口 | 请求体 | 返回 `data` |
|---|---|---|
| POST `/sv/baseUpgradeSK` | `{companyIds, sseats, pseats, mk, env}` | 字符串（含 `<br/>`） |

**字段注意：**
- `companyIds`/`sseats`/`pseats` 用 `shd`（逗号/换行/空格分隔）拆分，zip 对齐。
- `mk`：勾选模块 value 逗号拼接。6 个可选模块：M107/M138/M139/M141/M142/M143（注意 M142 是「小程序装修」，非 toB版）。
- 校验：companyIds/sseats/pseats 任一为空 → `必填项不能为空！`。
- 返回 `data` 直接是字符串（含 `<br/>`），`formatResult()` 转 `<br/>`→`\n`。
- **无右栏执行结果**：本页是单卡片居中布局，无 `/sv/qmbydsan` 调用。

---

## Task 1: 前端 baseUpgradeSK/index.vue 组件（单卡片）

**Files:** Create `frontend/src/views/baseUpgradeSK/index.vue`

- [x] Step 1 写组件（企业数据 3 textarea + 6 模块勾选 + 环境 + 结果展示）
- [x] Step 2 语法自检（Task 3 build 验证）
- [x] Step 3 Commit

## Task 2: 菜单 url 改写 + 路由接入 + 后端测试

- [x] Step 1 `MIGRATED` 增加 `'baseUpgradeSK': '/baseUpgradeSK'`
- [x] Step 2 router `migrated` 增加 + 替换 `legacy('/sv/baseUpgradeSK')`
- [x] Step 3 test_migration.py 新增断言（compconfig 分组）
- [x] Step 4 跑测试（20 通过）
- [x] Step 5 Commit

## Task 3: 端到端验证 + 生产构建 + 文档更新

- [x] Step 1 `npm run build`（通过）
- [x] Step 2 只读 e2e：0 iframe；标题「工具版升级 SK」；6 模块勾选；空提交校验「必填项不能为空！」；console 0 错误。
- [x] Step 3 更新 spec 验证清单
- [x] Step 4 更新进度并汇报

> 只读验证：未真实提交。临时 e2e 账号 e2e_busk 已删除。

---

## 进度记录

- [x] Task 1 前端组件
- [x] Task 2 菜单+路由+测试
- [x] Task 3 构建+e2e+文档
