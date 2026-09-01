# 迁移「转介绍3.0配置」页面 实现计划（compconfig 组第 3 页）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把「转介绍3.0配置」从 Django 模板 + jQuery（OP_upgradeR3.html）迁移为 Vue3 + Element Plus 组件，复用现有后端接口（零改动）。

**Architecture:** 沿用方案 B：`frontend/src/views/upgradeR3/index.vue` 新建组件，菜单 url 改写为 `/upgradeR3`（避开真实旧路由 `/sv/upgradeR3`），POST 复用旧视图。

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
- **不删**：`templates/OP_upgradeR3.html`、`saasview.py` 的 `upgradeR3` 视图、`static/js/upgradeR3.js`、`static/js/querymsgbyds.js`。
- **分支**：直接在 `main` 上继续。每步提交。
- **Python**：`/Users/imc/vllm/yes/envs/py310/bin/python3`。
- **CSRF**：`frontend/src/api/http.js` 统一加 header。
- **e2e 只读验证**：提交是真实写操作，e2e 只验证「渲染 + 校验 + 只读查询」，不真实提交。
- **结果展示**：文本插值 `{{ }}` + `white-space: pre-wrap`，用 `formatResult()` 把 `<br/>`→`\n`（防 XSS，不用 v-html）。

---

## 后端契约（零改动，直接复用）

| 接口 | 请求体 | 返回 `data` |
|---|---|---|
| POST `/sv/upgradeR3` | `{companyIds, seats, env}` | `{upgradeR3: "字符串(含\\n)", ur3sql: "SQL字符串(含<br/>与\\n)"}` |
| POST `/sv/qmbydsan` | `{dss:[1], num}` | `{qmbydsan: [{companyName, companyId, env, message, t}]}` |
| POST `/sv/aftergetqmbydsan` | `{dss:[1], num}` | `"更新数据成功！"` 或 `"无数据更新！"` |

**字段注意：**
- 校验：companyIds 空 → `企业id不能为空！`；seats 空 → `席位数不能为空！`。
- `upgradeR3` 是 `str(dict)` 结果（`\n` 分隔多条），直接 pre-wrap 文本展示。
- `ur3sql` 含 `<br/>` 与 `\n`，展示时 `formatResult()` 转 `<br/>`→`\n`；复制时复制清理后的 SQL。
- 提交成功后：显示 result1(upgradeR3)、提示「菜单sql,若企业菜单异常,需执行此处sql」、显示 rsql SQL、显示「复制并跳转提交sql」按钮（点击复制 SQL 到剪贴板并 `window.open('https://sqlprod.jiatuiyun.net/submitsql/')`）。
- 右侧「执行结果」：进入页面 `querymsgbyds([1],10)`；提交成功后 `querymsgbyds([1],4)`。`qmbydsan` 返回空数组/非数组 → 「暂无数据」。

---

## Task 1: 前端 upgradeR3/index.vue 组件（双栏 + SQL 复制 + 结果列表）

**Files:** Create `frontend/src/views/upgradeR3/index.vue`

- [ ] Step 1 写组件（左栏配置表单 + SQL 展示/复制 + 右栏执行结果列表 + formatResult）
- [ ] Step 2 语法自检（Task 3 build 验证）
- [ ] Step 3 Commit

## Task 2: 菜单 url 改写 + 路由接入 + 后端测试

- [ ] Step 1 `MIGRATED` 增加 `'upgradeR3': '/upgradeR3'`
- [ ] Step 2 router `migrated` 增加 + 替换 `legacy('/sv/upgradeR3')`
- [ ] Step 3 test_migration.py 新增断言（compconfig 分组，`data['groups'][0]['items']`）
- [ ] Step 4 跑测试
- [ ] Step 5 Commit

## Task 3: 端到端验证 + 生产构建 + 文档更新

- [ ] Step 1 `npm run build`（通过）
- [ ] Step 2 只读 e2e：0 iframe；双栏标题齐全（转介绍 3.0 配置 / 执行结果）；空提交校验「企业id不能为空！」；console 0 错误。
- [ ] Step 3 更新 spec 验证清单
- [ ] Step 4 更新进度并汇报

> 只读验证：未真实提交。临时 e2e 账号删除。

---

## 进度记录

- [ ] Task 1 前端组件
- [ ] Task 2 菜单+路由+测试
- [ ] Task 3 构建+e2e+文档
