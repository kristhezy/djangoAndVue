# 迁移「加推Saleskits」页面 实现计划（compconfig 组第 1 页）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把「加推Saleskits」从 Django 模板 + jQuery（OP_jtSaleskits.html）迁移为 Vue3 + Element Plus 组件，复用现有后端接口（零改动）。

**Architecture:** 沿用方案 B：`frontend/src/views/jtSaleskits/index.vue` 新建组件，菜单 url 改写为 `/jtSaleskits`（避开真实旧路由 `/sv/jtSaleskits`），POST 复用旧视图。

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
- **不删**：`templates/OP_jtSaleskits.html`、`saasview.py` 的 `jtSaleskits` 视图、`static/js/jtsaleskits.js`、`static/js/querymsgbyds.js`。
- **分支**：直接在 `main` 上继续。每步提交。
- **Python**：`/Users/imc/vllm/yes/envs/py310/bin/python3`。
- **CSRF**：`frontend/src/api/http.js` 统一加 header。
- **e2e 只读验证**：提交是真实写操作，e2e 只验证「渲染 + 校验 + 只读查询」，不真实提交。
- **结果展示**：文本插值 `{{ }}` + `white-space: pre-wrap`，用 `formatResult()` 把 `<br/>`→`\n` 并去掉 `<b>` 标签（防 XSS，不用 v-html）。

---

## 后端契约（零改动，直接复用）

| 接口 | 请求体 | 返回 `data` |
|---|---|---|
| POST `/sv/jtSaleskits` | `{companyIds, sseats, pseats, mk, env, type(0/1), jzc}` | `{skCompanyConfig: "..."}`（含 `<b>`/`<br/>` 的 HTML 字符串） |
| POST `/sv/qmbydsan` | `{dss:[3], num}` | `{qmbydsan: [{companyName, companyId, env, message, t}]}` |
| POST `/sv/aftergetqmbydsan` | `{dss:[3], num}` | `"更新数据成功！"` 或 `"无数据更新！"` |

**字段注意：**
- `type`：`zs`→0（招商版 Saleskits）、`jz`→1（家装版）。
- `mk`：勾选的模块 value 用逗号拼接（M107/M138/M139/M142/M143）。
- `jzc`：仅家装版需要（`hmy_company`红蚂蚁 / `ds_company`点石）；招商版后端不读。
- 校验：companyIds/sseats/pseats 非空 → `必填项不能为空！`；家装版未选 jzc → `家装类型不能为空! `。
- 版本联动（handleRadioChange）：zs→显示模块、隐藏家装类型、启用测试环境；jz→隐藏模块、显示家装类型、禁用测试环境、清空模块勾选。
- 右侧「执行结果」：进入页面 `querymsgbyds([3],10)`；提交成功后 `querymsgbyds([3],6)`。`qmbydsan` 返回空数组/非数组 → 显示「暂无数据」。

---

## Task 1: 前端 jtSaleskits/index.vue 组件（双栏 + 版本联动 + 结果列表）

**Files:** Create `frontend/src/views/jtSaleskits/index.vue`

- [ ] Step 1 写组件（左栏配置表单 + 右栏执行结果列表 + 版本/environment 联动 + formatResult）
- [ ] Step 2 语法自检（Task 3 build 验证）
- [ ] Step 3 Commit

## Task 2: 菜单 url 改写 + 路由接入 + 后端测试

- [ ] Step 1 `MIGRATED` 增加 `'jtSaleskits': '/jtSaleskits'`
- [ ] Step 2 router `migrated` 增加 + 替换 `legacy('/sv/jtSaleskits')`
- [ ] Step 3 test_migration.py 新增断言（compconfig 分组，`data['groups'][0]['items']`）
- [ ] Step 4 跑测试
- [ ] Step 5 Commit

## Task 3: 端到端验证 + 生产构建 + 文档更新

- [ ] Step 1 `npm run build`（通过）
- [ ] Step 2 只读 e2e：0 iframe；双栏标题齐全（加推 Saleskits 配置 / 执行结果）；5 个模块勾选；版本切换 jz 时模块隐藏 + 家装类型出现 + 测试环境禁用；空提交校验「必填项不能为空！」；console 0 错误。
- [ ] Step 3 更新 spec 验证清单
- [ ] Step 4 更新进度并汇报

> 只读验证：未真实提交。临时 e2e 账号删除。

---

## 进度记录

- [ ] Task 1 前端组件
- [ ] Task 2 菜单+路由+测试
- [ ] Task 3 构建+e2e+文档
