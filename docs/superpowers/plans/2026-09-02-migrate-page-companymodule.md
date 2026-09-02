# 迁移「企业模块配置」页面 实现计划（standalone 第 1 页）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把「企业模块配置」从 Django 模板 + jQuery（companyModule.html）迁移为 Vue3 + Element Plus 组件，复用现有后端接口（零改动）。

**Architecture:** 沿用方案 B：`frontend/src/views/companyModule/index.vue` 新建组件，菜单 url 改写为 `/companyModule`（避开真实旧路由 `/sv/companyModule`），POST 复用旧视图。

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
- **不删**：`templates/companyModule.html`、`saasview.py` 的 `companyModule` 视图。
- **分支**：直接在 `main` 上继续。每步提交。
- **Python**：`/Users/imc/vllm/yes/envs/py310/bin/python3`。
- **CSRF**：`frontend/src/api/http.js` 统一加 header。
- **e2e 只读验证**：提交是真实写操作，e2e 只验证「渲染 + 校验 + 只读查询」，不真实提交。

---

## 后端契约（零改动，直接复用）

| 接口 | 请求体 | 返回 `data` |
|---|---|---|
| POST `/sv/companyModule` | `{companyId, mk, cm, env}` | 字符串（`【公司名】...`） |

**字段注意：**
- `companyId` 用 `shd` 拆分多企业。
- `mk`：勾选模块 value 逗号拼接（去重后）。
- `cm`：`addm`（增加模块，默认）/ `delm`（删除模块）。
- `env`：prod/test。
- 校验：companyId 空 → `企业id不能为空！`；mk 空 → `至少选择一个模块！`。
- **M107 互斥**：模板中 M107 出现两次（共用组「M107(表单)」id=mk107、Saleskits组「M107(推广表单)」id=sk107），均带 `mutex-checkbox`，勾选其一自动取消另一个（value 相同，提交只出一次 M107）。
- **提交成功后**：清空所有模块勾选。
- 返回 `data` 是 `str(dict)` 清理后的纯文本，直接 pre-wrap 展示。

---

## 后端契约：模块分组（6 组，复刻模板）

- 共用模块（9）：M100官网 M105动态 M107表单[M] M108视频 M109宣传册 M110案例库 M111海报 M112文章 M113文件
- 转介绍/工具版专属（5）：M103推力系统 M104小程序 M114普通版商城 M119活动分发 M120优惠券
- Saleskits专属（6）：M140 PLG企管 M107推广表单[M] M138任务中心 M139产品库 M142 toB版 M143 AI名片
- 版本（6）：M127加推云盘版 M128转介绍3.0 M136招商版 M137 Saleskits版 M146家装版 M144三一重工定制
- 不常用（10）：M115直播 M116图谱 M124企微助手 M121活码 M122奥田定制 M123课程培训 M129自动化营销 M131智能渠道码 M132客户群运营 M025商城分销[加粗]
- 已停用（4）：M102销售管理组件 M117转介绍2.0 M106推任务 M126聊天侧边栏

---

## Task 1: 前端 companyModule/index.vue 组件

**Files:** Create `frontend/src/views/companyModule/index.vue`

- [x] Step 1 写组件（企业IDs input + 6 组模块勾选(含 M107 互斥) + 环境/cm radio + 结果展示）
- [x] Step 2 语法自检（Task 3 build 验证）
- [x] Step 3 Commit

## Task 2: 菜单 url 改写 + 路由接入 + 后端测试

- [x] Step 1 `MIGRATED` 增加 `'companyModule': '/companyModule'`
- [x] Step 2 router `migrated` 增加 + 替换 `legacy('/sv/companyModule')`
- [x] Step 3 test_migration.py 新增断言（standalone）
- [x] Step 4 跑测试（21 通过）
- [x] Step 5 Commit

## Task 3: 端到端验证 + 生产构建 + 文档更新

- [x] Step 1 `npm run build`（通过）
- [x] Step 2 只读 e2e：0 iframe；标题/分组齐全；6 组模块渲染；M107 互斥正确；空提交校验「企业id不能为空！」；console 0 错误。
- [x] Step 3 更新 spec 验证清单
- [x] Step 4 更新进度并汇报

> 只读验证：未真实提交。临时 e2e 账号 e2e_cm 已删除。

---

## 进度记录

- [x] Task 1 前端组件
- [x] Task 2 菜单+路由+测试
- [x] Task 3 构建+e2e+文档
