# 迁移「批量删除线索」页面 实现计划（第二阶段第 5 页）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把「批量删除线索」从 Django 模板 + jQuery（AT_batchDeleteClue.html + 内联 JS）迁移为 Vue3 + Element Plus 组件，复用现有后端接口（零改动）。

**Architecture:** 沿用方案 B：`frontend/src/views/batchDeleteClue/index.vue` 新建组件，菜单 url 由 `/api/menu` 改写为独立前端路径 `/batchDeleteClue`（避开真实旧路由 `/sv/batchDeleteClue`，刷新仍走 Vue 版），POST 接口仍复用旧视图 `/sv/batchDeleteClue` 的 POST 分支。

**Tech Stack:** Vue3 + Element Plus 2.8.4 + axios（已有）；Django 5.2（零改动）。

**设计文档:** `docs/superpowers/specs/2026-08-28-django-vue3-migration-design.md`（第 10 节「单页迁移流程」）

---

## 断点续作约定（硬约束）

1. 本文件是**进度的单一真相**。每完成一步、遇到阻塞、跳过某步，**立即**更新对应 checkbox 状态。
2. 恢复时：读上一阶段 spec 恢复「为什么」，读本文件 checkbox 恢复「做到哪」，直接接下一步。
3. 禁止依赖对话记忆判断进度。

---

## Global Constraints

- **端口**：Django 统一用 **8001**；Vite dev 用 5173。
- **前端语言**：JavaScript（不用 TypeScript）。
- **UI 组件库**：Element Plus 2.8.4（el-radio 用 `value` 属性）。
- **后端接口**：复用现有视图，**零改动**。返回结构 `{code, msg, data}`（code '0'=成功）。
- **不删**：`templates/AT_batchDeleteClue.html`、`saasview.py` 的 `batchDeleteClue` 视图，原样保留。
- **分支**：直接在 `main` 上继续。每步提交。
- **测试策略**：后端唯一新增逻辑（`/api/menu` 对 batchDeleteClue 的 url 改写）用 Django test client 写测试；前端用 browser-automation + 手动清单验证。
- **Python 解释器**：`/Users/imc/vllm/yes/envs/py310/bin/python3`。
- **CSRF**：POST 由 `frontend/src/api/http.js` 统一加 `X-CSRFToken`，组件直接 `import http from '../../api/http'`。
- **企业下拉框硬编码**：旧版只写死 2 家企业，迁移后继续硬编码这 2 家。
- **e2e 只读验证**：批量删除是真实写操作，e2e 只验证「页面渲染 + 表单校验」，不真实提交。

---

## 后端契约（零改动，直接复用）

| 接口 | method | 请求体 | 返回 `data` |
|---|---|---|---|
| `/sv/batchDeleteClue` | POST | `{cid, phones, env}` | 字符串，形如 `【{cid}】总执行的手机号数为: N ; 执行失败的手机号数为: M , 手机号为: [...] .` |

**字段注意：**
- `phones` 后端用 `split_hh_dh` 按 **逗号 / 换行 / 空格** 分隔成手机号列表（见 `publicDef.py:75`）。
- 校验（旧前端）：`cid` 非空、`phones` 非空，否则 alert。

### 企业下拉硬编码列表（复刻旧模板 AT_batchDeleteClue.html 第 77-81 行）

| value | label |
|---|---|
| `693225071459762176` | 石家庄七度文化传播有限公司(693225071459762176)【18630183501】 |
| `844635664262787073` | 石家庄七度文化传播有限公司转介绍(844635664262787073)【13303043501】 |

---

## Task 1: 前端 batchDeleteClue/index.vue 组件（单卡片 + 校验）

**Files:**
- Create: `frontend/src/views/batchDeleteClue/index.vue`

**Interfaces:**
- Consumes: `frontend/src/api/http.js`
- Produces: `BatchDeleteCluePage` 组件（default export），供 Task 2 路由引用

- [ ] **Step 1: 写组件**

```vue
<template>
  <div class="batch-page">
    <el-card class="batch-card" shadow="never">
      <template #header>
        <div class="batch-title">批量删除线索</div>
      </template>
      <el-form label-position="top">
        <el-form-item label="选择企业ID" required>
          <el-select v-model="form.cid" placeholder="选择企业ID" style="width:100%">
            <el-option
              v-for="c in companies"
              :key="c.id"
              :label="c.name"
              :value="c.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="手机号" required>
          <el-input
            v-model="form.phones"
            type="textarea"
            :rows="8"
            placeholder="输入手机号（支持逗号/换行/空格分隔多个）"
          />
        </el-form-item>
        <el-form-item label="环境">
          <el-radio-group v-model="form.env">
            <el-radio value="prod">生产环境</el-radio>
            <el-radio value="test">测试环境</el-radio>
          </el-radio-group>
        </el-form-item>
        <div class="batch-actions">
          <el-button type="primary" :loading="loading" @click="submit">提交</el-button>
          <el-button @click="reset">重置</el-button>
        </div>
        <div class="batch-result">{{ result }}</div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

// 硬编码企业列表（复刻旧模板 AT_batchDeleteClue.html 第 77-81 行）
const companies = [
  { id: '693225071459762176', name: '石家庄七度文化传播有限公司(693225071459762176)【18630183501】' },
  { id: '844635664262787073', name: '石家庄七度文化传播有限公司转介绍(844635664262787073)【13303043501】' },
]

const form = reactive({ cid: '', phones: '', env: 'prod' })
const result = ref('')
const loading = ref(false)

async function submit() {
  if (!form.cid) { ElMessage.warning('企业ID不能为空！'); return }
  if (!form.phones.trim()) { ElMessage.warning('手机号码不能为空！'); return }
  loading.value = true
  try {
    const resp = await http.post('/sv/batchDeleteClue', {
      cid: form.cid, phones: form.phones, env: form.env,
    })
    result.value = resp.data?.data || ''
  } catch (e) {
    result.value = ''
    ElMessage.error('删除失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    loading.value = false
  }
}

function reset() {
  form.cid = ''
  form.phones = ''
  form.env = 'prod'
  result.value = ''
}
</script>

<style scoped>
.batch-page {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  box-sizing: border-box;
  background: #f0f2f5;
  overflow: hidden;
}
.batch-card {
  width: 680px;
  max-width: 100%;
  max-height: 100%;
  overflow-y: auto;
}
.batch-title { text-align: center; font-weight: 600; font-size: 20px; }
.batch-actions { display: flex; justify-content: center; gap: 12px; margin-top: 8px; }
.batch-result {
  margin-top: 16px;
  min-height: 40px;
  max-height: 360px;
  overflow-y: auto;
  padding: 10px;
  border-radius: 8px;
  font-size: 15px;
  text-align: center;
  word-break: break-all;
  white-space: pre-wrap;
  color: #409eff;
}
</style>
```

- [ ] **Step 2: 语法自检**：`.vue` 需 SFC 编译，由 Task 3 的 `npm run build` 统一验证。

- [ ] **Step 3: Commit**

```bash
cd /Users/imc/djangoAndVue
git add frontend/src/views/batchDeleteClue/index.vue
git commit -m "feat(frontend): 迁移「批量删除线索」为 Vue 单卡片组件"
```

---

## Task 2: 菜单 url 改写 + 路由接入 + 后端测试

**Files:**
- Modify: `djangoPlant/api_menu.py`（`MIGRATED` 增加 `batchDeleteClue`）
- Modify: `frontend/src/router/index.js`（`migrated` 增加 `batchDeleteClue`，`legacy('/sv/batchDeleteClue')` 换成 Vue 组件路由）
- Modify: `djangoPlant/test_migration.py`（新增一条 url 改写测试）

- [ ] **Step 1: api_menu.py 的 MIGRATED 增加 batchDeleteClue**

```python
MIGRATED = {
    'mergeUser': '/mergeUser',
    'other': '/other',
    'mynote': '/mynote',
    'delCP': '/delCP',
    'batchDeleteClue': '/batchDeleteClue',
}
```

- [ ] **Step 2: router 接入**

`migrated` 增加 `batchDeleteClue: () => import('../views/batchDeleteClue/index.vue')`；children 里 `legacy('/sv/batchDeleteClue')` 改为 `{ path: 'batchDeleteClue', component: migrated.batchDeleteClue || LegacyIframe }`。

- [ ] **Step 3: 后端测试新增 url 改写断言**

在 `djangoPlant/test_migration.py` 的 `MenuApiTests` 类新增（batchDeleteClue 在 tools 分组）：

```python
    def test_batchdeleteclue_menu_url_rewritten_to_frontend_path(self):
        s = self.c.session
        s['menus'] = ['batchDeleteClue']
        s.save()
        resp = self.c.get('/api/menu')
        data = resp.json()['data']
        item = next(x for x in data['groups'][0]['items'] if x['key'] == 'batchDeleteClue')
        self.assertEqual(item['url'], '/batchDeleteClue')
```

- [ ] **Step 4: 跑后端测试**

```bash
cd /Users/imc/djangoAndVue
/Users/imc/vllm/yes/envs/py310/bin/python3 manage.py test djangoPlant.test_migration -v 2
```
预期：全部 PASS。

- [ ] **Step 5: Commit**

```bash
cd /Users/imc/djangoAndVue
git add djangoPlant/api_menu.py frontend/src/router/index.js djangoPlant/test_migration.py
git commit -m "feat(menu): 「批量删除线索」菜单 url 改写 /batchDeleteClue 并接入 Vue 路由"
```

---

## Task 3: 端到端验证 + 生产构建 + 文档更新

- [x] **Step 1: 生产构建**：`npm run build`（通过）

- [x] **Step 2: 端到端只读验证（browser-automation）**
  - [x] 直达 url `/batchDeleteClue`，渲染 Vue 单卡片（0 iframe）
  - [x] 标题「批量删除线索」齐全
  - [x] 企业下拉含 2 家企业
  - [x] 校验（cid 空 → 提示「企业ID不能为空！」）
  - [x] 刷新 `/batchDeleteClue` 仍 Vue 版（0 iframe，console 0 错误）

> 只读验证：不真实提交写操作。临时 e2e 账号 e2e_batchdc 已删除。

- [x] **Step 3: 更新 spec 验证清单**

- [x] **Step 4: 更新本计划进度标记并汇报**

---

## 进度记录

- [x] Task 1 前端 batchDeleteClue/index.vue 组件
- [x] Task 2 菜单 url 改写 + 路由接入 + 后端测试
- [x] Task 3 端到端验证 + 生产构建 + 文档更新
