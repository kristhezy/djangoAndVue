# 迁移「销售工具版配置」页面 实现计划（compconfig 组第 4 页）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把「销售工具版配置」从 Django 模板 + jQuery（OP_basicCompCfg.html）迁移为 Vue3 + Element Plus 组件，复用现有后端接口（零改动）；同时抽取公共 `OperationLog` 组件修复「执行结果」message 中 HTML 加粗标签渲染。

**Architecture:** 沿用方案 B：`frontend/src/views/basicComp/index.vue` 新建组件，菜单 url 改写为 `/basicComp`（避开真实旧路由 `/sv/basicComp`），POST 复用旧视图。抽取 `frontend/src/components/OperationLog.vue`，统一处理 `/sv/qmbydsan` + `/sv/aftergetqmbydsan`，用「先转义再还原 `<b>`/`<br/>`」的安全净化渲染加粗。

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
- **不删**：`templates/OP_basicCompCfg.html`、`saasview.py` 的 `basicCompCfg` 视图、`static/js/querymsgbyds.js`。
- **分支**：直接在 `main` 上继续。每步提交。
- **Python**：`/Users/imc/vllm/yes/envs/py310/bin/python3`。
- **CSRF**：`frontend/src/api/http.js` 统一加 header。
- **e2e 只读验证**：提交是真实写操作，e2e 只验证「渲染 + 校验 + 只读查询」，不真实提交。

---

## 后端契约（零改动，直接复用）

| 接口 | 请求体 | 返回 `data` |
|---|---|---|
| POST `/sv/basicComp` | `{companyId, mk, env}` | `{basicCompanyConfig: "字符串(含\\n)"}` |
| POST `/sv/qmbydsan` | `{dss:[2], num}` | `{qmbydsan: [{companyName, companyId, env, message, t}]}` |
| POST `/sv/aftergetqmbydsan` | `{dss:[2], num}` | `"更新数据成功！"` 或 `"无数据更新！"` |

**字段注意：**
- `companyId` 用 `shd`（逗号/换行/空格分隔）拆分多企业。
- `mk`：勾选模块 value 逗号拼接。8 个可选模块：M100/M103/M104/M114/M115(禁用)/M119/M120/M124；其中 M100/M103/M104/M114/M119/M120 默认勾选，M115 禁用。
- 校验：companyId 空 → `企业id不能为空！`；mk 空 → `模块最少选择一个！`。
- 提交成功后 `querymsgbyds([2],6)`；进入页面 `querymsgbyds([2],10)`。
- **HTML 标签问题**：`qmbydsan` 的 `message` 含 `<b>xxx</b>` 加粗与 `<br/>` 换行。旧版直接 innerHTML 渲染，迁移版需安全净化（先全转义，再仅还原 `<b>`/`</b>`/`<br/>`）。

---

## Task 1: 抽取公共 OperationLog 组件 + 重构已有三页

**Files:**
- Create `frontend/src/components/OperationLog.vue`
- Modify `frontend/src/views/jtSaleskits/index.vue`（用 OperationLog 替换右栏，ds=[3]）
- Modify `frontend/src/views/hwskset/index.vue`（ds=[15]）
- Modify `frontend/src/views/upgradeR3/index.vue`（ds=[1]）

- [x] Step 1 OperationLog.vue（`sanitize()` 先转义再还原 `<b>`/`<br/>`；`defineExpose({refresh})`）
- [x] Step 2 三页替换右栏为 `<OperationLog ref="log" :ds="[N]" :init-num="10"/>`，提交后 `log.value?.refresh(M)`
- [x] Step 3 构建自检
- [x] Step 4 Commit

## Task 2: 前端 basicComp/index.vue 组件

**Files:** Create `frontend/src/views/basicComp/index.vue`

- [x] Step 1 写组件（企业IDs textarea + 8 模块勾选(含禁用 M115) + 环境 + OperationLog ds=[2]）
- [x] Step 2 语法自检
- [x] Step 3 Commit

## Task 3: 菜单 url 改写 + 路由接入 + 后端测试

- [x] Step 1 `MIGRATED` 增加 `'basicComp': '/basicComp'`
- [x] Step 2 router `migrated` 增加 + 替换 `legacy('/sv/basicComp')`
- [x] Step 3 test_migration.py 新增断言（compconfig 分组）
- [x] Step 4 跑测试（19 通过）
- [x] Step 5 Commit

## Task 4: 端到端验证 + 生产构建 + 文档更新

- [x] Step 1 `npm run build`（通过）
- [x] Step 2 只读 e2e：0 iframe；标题齐全；8 模块勾选（M115 禁用、6 默认勾选）；空提交校验「企业id不能为空！」；console 0 错误。
- [x] Step 3 更新 spec 验证清单
- [x] Step 4 更新进度并汇报

> 只读验证：未真实提交。临时 e2e 账号 e2e_bccfg 已删除。

---

## 进度记录

- [x] Task 1 抽取 OperationLog + 重构
- [x] Task 2 前端组件
- [x] Task 3 菜单+路由+测试
- [x] Task 4 构建+e2e+文档
