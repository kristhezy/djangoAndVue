# 迁移「华为云SK配置」页面 实现计划（compconfig 组第 2 页）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把「华为云SK配置」从 Django 模板 + jQuery（OP_hwskset.html）迁移为 Vue3 + Element Plus 组件，复用现有后端接口（零改动）。

**Architecture:** 沿用方案 B：`frontend/src/views/hwskset/index.vue` 新建组件，菜单 url 改写为 `/hwskset`（避开真实旧路由 `/sv/hwskset`），POST 复用旧视图。

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
- **不删**：`templates/OP_hwskset.html`、`saasview.py` 的 `hwskset`/`queryCompanyId` 视图、`static/js/querymsgbyds.js`。
- **分支**：直接在 `main` 上继续。每步提交。
- **Python**：`/Users/imc/vllm/yes/envs/py310/bin/python3`。
- **CSRF**：`frontend/src/api/http.js` 统一加 header。
- **e2e 只读验证**：提交是真实写操作，e2e 只验证「渲染 + 校验 + 只读查询」，不真实提交。
- **结果展示**：文本插值 `{{ }}` + `white-space: pre-wrap`，用 `formatResult()` 把 `<br/>`→`\n` 并去掉 `<b>` 标签（防 XSS，不用 v-html）。

---

## 后端契约（零改动，直接复用）

| 接口 | 请求体 | 返回 `data` |
|---|---|---|
| POST `/sv/hwskset` | `{cid, cname, payment, tseat, ptseat:"", mk, env}` | `{hwskCompanyConfig: "..."}`（含 `<b>` 的 HTML 字符串） |
| POST `/sv/querycompid/saas` | `{ln, env}` | `code='0'` 时 `{cn, cid, phone}`；`code='10002'` 时错误字符串 |
| POST `/sv/qmbydsan` | `{dss:[15], num}` | `{qmbydsan: [{companyName, companyId, env, message, t}]}` |
| POST `/sv/aftergetqmbydsan` | `{dss:[15], num}` | `"更新数据成功！"` 或 `"无数据更新！"` |

**字段注意：**
- `payment`：下拉 3=预充值（默认）/ 1=线下。
- `mk`：勾选的模块 value 逗号拼接（M107/M138/M139/M142/M143）。
- `ptseat`：前端硬编码 `""`（旧版不提供推荐官席位输入）。
- 校验：`cid` 空 → `输入企业id！`；cname/payment/tseat/ptseat/mk 全空 → `修改类型不能全部为空！`。
- 手机号查询（`getCidByLname`）：loginName blur 或 Enter 触发 POST `/sv/querycompid/saas`；`code==='10002'` 时在 companyId 下方红字显示 `data`；成功则回填 companyId=cid、cname=cn，清空错误。
- 右侧「执行结果」：进入页面 `querymsgbyds([15],10)`；提交成功后 `querymsgbyds([15],7)`。`qmbydsan` 返回空数组/非数组 → 「暂无数据」。

---

## Task 1: 前端 hwskset/index.vue 组件（双栏 + 手机号查询 + 结果列表）

**Files:** Create `frontend/src/views/hwskset/index.vue`

- [ ] Step 1 写组件（左栏配置表单 + 右栏执行结果列表 + loginName blur/Enter 查询 + formatResult）
- [ ] Step 2 语法自检（Task 3 build 验证）
- [ ] Step 3 Commit

## Task 2: 菜单 url 改写 + 路由接入 + 后端测试

- [ ] Step 1 `MIGRATED` 增加 `'hwskset': '/hwskset'`
- [ ] Step 2 router `migrated` 增加 + 替换 `legacy('/sv/hwskset')`
- [ ] Step 3 test_migration.py 新增断言（compconfig 分组，`data['groups'][0]['items']`）
- [ ] Step 4 跑测试
- [ ] Step 5 Commit

## Task 3: 端到端验证 + 生产构建 + 文档更新

- [ ] Step 1 `npm run build`（通过）
- [ ] Step 2 只读 e2e：0 iframe；双栏标题齐全（华为云 SK 配置 / 执行结果）；5 模块勾选；付款方式下拉；空提交校验「输入企业id！」；console 0 错误。
- [ ] Step 3 更新 spec 验证清单
- [ ] Step 4 更新进度并汇报

> 只读验证：未真实提交。临时 e2e 账号删除。

---

## 进度记录

- [ ] Task 1 前端组件
- [ ] Task 2 菜单+路由+测试
- [ ] Task 3 构建+e2e+文档
