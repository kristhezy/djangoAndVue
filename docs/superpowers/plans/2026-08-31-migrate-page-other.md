# 迁移「操作变更记录」页面 实现计划（第二阶段第 2 页）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把列表页「操作变更记录」从 Django 模板 + jQuery（other.html + other.js）迁移为 Vue3 + Element Plus 组件，复用现有 4 个后端接口（零改动）。

**Architecture:** 沿用第一阶段方案 B：`frontend/src/views/other/index.vue` 新建组件，菜单 url 由 `/api/menu` 改写为独立前端路径 `/other`（避开真实旧路由 `/pv/other`，使刷新也走 Vue 版），POST 接口仍复用旧视图 `/pv/other*`、`/pv/pagecount` 的 POST 分支。

**Tech Stack:** Vue3 + Element Plus + Pinia + axios（已有）；Django 5.2（零改动）。

**设计文档:** `docs/superpowers/specs/2026-08-28-django-vue3-migration-design.md`（第 10 节「单页迁移流程」是本页的迁移规范）
**上一阶段 plan（参考）:** `docs/superpowers/plans/2026-08-28-django-vue3-migration-plan.md`

---

## 断点续作约定（硬约束）

1. 本文件是**进度的单一真相**。每完成一步、遇到阻塞、跳过某步，**立即**更新对应 checkbox 状态（`[ ] 未开始 / [~] 进行中 / [x] 已完成 / [!] 阻塞`）并在行尾或下方加备注。
2. 恢复时：读上一阶段 spec 恢复「为什么」，读本文件 checkbox 恢复「做到哪」，直接接下一步。
3. 禁止依赖对话记忆判断进度。

---

## Global Constraints

- **端口**：Django 统一用 **8001**；Vite dev 用 5173。
- **前端语言**：JavaScript（不用 TypeScript）。
- **UI 组件库**：Element Plus。
- **后端接口**：复用现有视图，**零改动**。接口返回结构统一为 `{code, msg, data}`（code '0'=成功）。
- **不删**：`templates/other.html`、`static/js/other.js`、`publicview.py` 的 `other`/`other_part`/`pagecount` 视图，全部原样保留。
- **分支**：直接在 `main` 上继续（第一阶段已合并回 main）。每步提交到 main。
- **测试策略**：后端唯一新增逻辑（`/api/menu` 对 other 的 url 改写）用 Django test client 写测试；前端 Vue 组件无测试基础设施，用 browser-automation + 手动清单验证，不引入 vitest。
- **Python 解释器**：`/Users/imc/vllm/yes/envs/py310/bin/python3`。
- **CSRF**：POST 请求由 `frontend/src/api/http.js` 统一加 `X-CSRFToken` header，组件直接 `import http from '../../api/http'` 使用，不要自己手写 axios。

---

## 后端契约（零改动，直接复用）

| 接口 | method | 请求体 | 返回 `data` |
|---|---|---|---|
| `/pv/other` | POST | `{page, env, vers, num, compid, compname, uname, minfo}` | `data.oprationalInfo`：数组（每项 `{id, env, companyName, companyId, message, uname, createTime, serverSide, version}`），或字符串 `"数据库连接异常！..."`（异常时） |
| `/pv/other/queryOpraterName` | POST | `{}` | `data.otherPartRlt`：逗号分隔的操作人名字符串（如 `"张三,李四,"`） |
| `/pv/other/delmsg` | POST | `{id}` | `data.otherPartRlt`：删除成功后为 `"删除成功！"` |
| `/pv/pagecount` | POST | `{env, vers, compid, compname, uname, minfo}` | `data.total`：总记录数字符串 |

**字段注意：**
- `oprationalInfo` 里的 `env` 已被后端转成中文（`生产`/`测试`/`宁夏联通`）。
- `version` 和 `serverSide` 是 **IntegerField**，可能为 `null`。前端统一用 `String(x ?? '')` 转字符串比较。
- `num` 每页条数固定传 `10`，`page` 从 `1` 开始（后端 `page==1 → p=0`，`else → 10*(page-1)`）。
- `total` 是字符串，前端 `Number(total)` 后传给 `el-pagination`。

### env 标签展示逻辑（复刻旧 other.js 第 82-107 行）

前端拿到 `env`（中文）+ `version` + `serverSide` 后，`envLabel(row)` 返回：

```js
function envLabel(row) {
  const env = row.env || ''
  const ver = String(row.version ?? '')
  const ss = String(row.serverSide ?? '')
  if (env === '生产' || env === '测试') {
    if (ver === '1') return env + '/SAAS'
    if (ver === '3') {
      if (env === '生产' && ss === '3') return '私有化/基线版'
      return env + '/基线版'
    }
    if (ver === '4') return env + '/Soon'
    if (ver === '5') return env + '/Meet'
    if (ver === '6') return env + '/通威版'
    return env
  }
  return env
}
```

---

## Task 1: 前端 other/index.vue 组件（列表 + 查询 + 分页 + 删除）

**Files:**
- Create: `frontend/src/views/other/index.vue`

**Interfaces:**
- Consumes: `frontend/src/api/http.js`（axios 实例，已封装 CSRF + 401/403 跳登录）
- Produces: `OtherPage` 组件（default export），供 Task 2 路由引用

- [ ] **Step 1: 写组件**

新建 `frontend/src/views/other/index.vue`，完整代码如下（照抄，不要改动逻辑）：

```vue
<template>
  <div class="other-page">
    <!-- 筛选区 -->
    <el-card class="filter-card" shadow="never">
      <template #header><span class="filter-title">操作变更记录</span></template>
      <el-form :inline="true" :model="query" @submit.prevent>
        <el-form-item label="环境">
          <el-select v-model="query.env" clearable placeholder="选择环境" style="width:120px">
            <el-option label="生产" value="prod" />
            <el-option label="测试" value="test" />
          </el-select>
        </el-form-item>
        <el-form-item label="版本">
          <el-select v-model="query.vers" clearable placeholder="选择版本" style="width:120px">
            <el-option label="Soon" value="4" />
            <el-option label="基线版" value="3" />
            <el-option label="通威版" value="6" />
            <el-option label="SAAS" value="1" />
          </el-select>
        </el-form-item>
        <el-form-item label="企业ID">
          <el-input v-model="query.compid" placeholder="输入企业ID" style="width:140px" />
        </el-form-item>
        <el-form-item label="企业名称">
          <el-input v-model="query.compname" placeholder="输入企业名称" style="width:140px" />
        </el-form-item>
        <el-form-item label="操作信息">
          <el-input v-model="query.minfo" placeholder="输入操作信息" style="width:140px" />
        </el-form-item>
        <el-form-item label="操作人">
          <el-select v-model="query.uname" clearable filterable placeholder="选择操作人" style="width:140px">
            <el-option v-for="n in operators" :key="n" :label="n" :value="n" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="search">查询</el-button>
          <el-button @click="reset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 表格区 -->
    <el-card class="table-card" shadow="never">
      <el-table :data="list" v-loading="loading" stripe height="100%">
        <el-table-column prop="id" label="序号" width="70" />
        <el-table-column label="环境" width="150">
          <template #default="{ row }">{{ envLabel(row) }}</template>
        </el-table-column>
        <el-table-column prop="companyId" label="企业ID" width="120" show-overflow-tooltip />
        <el-table-column prop="companyName" label="企业名称" show-overflow-tooltip />
        <el-table-column prop="message" label="操作信息" show-overflow-tooltip />
        <el-table-column prop="uname" label="操作人" width="100" show-overflow-tooltip />
        <el-table-column prop="createTime" label="操作时间" width="170" show-overflow-tooltip />
        <el-table-column label="操作" width="90" fixed="right">
          <template #default="{ row }">
            <el-popconfirm title="确定删除这条记录吗？" @confirm="del(row.id)">
              <template #reference>
                <el-button type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pager">
        <el-pagination
          v-model:current-page="page"
          :page-size="num"
          :total="total"
          layout="total, prev, pager, next, jumper"
          @current-change="load"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const num = 10
const loading = ref(false)
const list = ref([])
const operators = ref([])
const total = ref(0)
const page = ref(1)

const query = reactive({ env: '', vers: '', compid: '', compname: '', minfo: '', uname: '' })

function envLabel(row) {
  const env = row.env || ''
  const ver = String(row.version ?? '')
  const ss = String(row.serverSide ?? '')
  if (env === '生产' || env === '测试') {
    if (ver === '1') return env + '/SAAS'
    if (ver === '3') {
      if (env === '生产' && ss === '3') return '私有化/基线版'
      return env + '/基线版'
    }
    if (ver === '4') return env + '/Soon'
    if (ver === '5') return env + '/Meet'
    if (ver === '6') return env + '/通威版'
    return env
  }
  return env
}

function payload() {
  return {
    page: page.value,
    env: query.env,
    vers: query.vers,
    num,
    compid: query.compid,
    compname: query.compname,
    uname: query.uname,
    minfo: query.minfo,
  }
}

async function load() {
  loading.value = true
  try {
    const resp = await http.post('/pv/other', payload())
    const a = resp.data?.data?.oprationalInfo
    if (typeof a === 'string') {
      list.value = []
      ElMessage.error(a)
    } else if (!Array.isArray(a) || a.length === 0) {
      list.value = []
    } else {
      list.value = a
    }
  } catch (e) {
    list.value = []
    ElMessage.error('查询失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    loading.value = false
  }
}

async function loadTotal() {
  try {
    const resp = await http.post('/pv/pagecount', payload())
    total.value = Number(resp.data?.data?.total ?? 0)
  } catch (e) {
    total.value = 0
  }
}

async function loadOperators() {
  try {
    const resp = await http.post('/pv/other/queryOpraterName', {})
    const s = resp.data?.data?.otherPartRlt || ''
    operators.value = s.split(',').filter(x => x.trim() !== '')
  } catch (e) {
    operators.value = []
  }
}

async function del(id) {
  try {
    const resp = await http.post('/pv/other/delmsg', { id })
    ElMessage.success(resp.data?.data?.otherPartRlt || '删除成功！')
    await load()
    await loadTotal()
  } catch (e) {
    ElMessage.error('删除失败：' + (e?.response?.data?.msg || e.message))
  }
}

function search() {
  page.value = 1
  load()
  loadTotal()
}

function reset() {
  query.env = ''
  query.vers = ''
  query.compid = ''
  query.compname = ''
  query.minfo = ''
  query.uname = ''
  page.value = 1
  load()
  loadTotal()
}

onMounted(() => {
  loadOperators()
  load()
  loadTotal()
})
</script>

<style scoped>
.other-page { height: 100%; display: flex; flex-direction: column; gap: 16px; padding: 16px; box-sizing: border-box; background: #f0f2f5; overflow: hidden; }
.filter-card { flex-shrink: 0; }
.filter-title { font-weight: 600; font-size: 16px; }
.table-card { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.table-card :deep(.el-card__body) { flex: 1; display: flex; flex-direction: column; overflow: hidden; padding: 0; }
.table-card :deep(.el-table) { flex: 1; }
.pager { display: flex; justify-content: flex-end; padding: 12px 16px; }
</style>
```

- [ ] **Step 2: 语法自检**

```bash
cd /Users/imc/djangoAndVue/frontend
node --check src/views/other/index.vue 2>/dev/null; echo "（.vue 需 SFC 编译，node --check 跳过，改用 build 验证）"
```

> 说明：`.vue` 文件不能直接 `node --check`（含 template）。语法正确性由 Task 3 的 `npm run build` 统一验证；本步只确认文件已创建、内容与上方一致。

- [ ] **Step 3: Commit**

```bash
cd /Users/imc/djangoAndVue
git add frontend/src/views/other/index.vue
git commit -m "feat(frontend): 迁移「操作变更记录」为 Vue 列表组件（查询+分页+删除）"
```

---

## Task 2: 菜单 url 改写 + 路由接入 + 后端测试

**Files:**
- Modify: `djangoPlant/api_menu.py`（`MIGRATED` 增加 `other`）
- Modify: `frontend/src/router/index.js`（`migrated` 增加 `other`，`legacy('/pv/other')` 换成 Vue 组件路由）
- Modify: `djangoPlant/test_migration.py`（新增一条 other url 改写测试）

**Interfaces:**
- Consumes: Task 1 的 `OtherPage` 组件（`../views/other/index.vue`）
- Produces: 菜单「操作变更记录」返回 url `/other`；路由 `/other` 渲染 Vue 组件

- [ ] **Step 1: api_menu.py 的 MIGRATED 增加 other**

将：
```python
MIGRATED = {
    'mergeUser': '/mergeUser',
}
```
改为：
```python
MIGRATED = {
    'mergeUser': '/mergeUser',
    'other': '/other',
}
```

- [ ] **Step 2: router 接入 other**

`frontend/src/router/index.js` 中，将：
```js
const migrated = {
  mergeUser: () => import('../views/mergeUser/index.vue'),
}
```
改为：
```js
const migrated = {
  mergeUser: () => import('../views/mergeUser/index.vue'),
  other: () => import('../views/other/index.vue'),
}
```

并将 children 里的：
```js
      legacy('/pv/other'),
```
改为：
```js
      { path: 'other', component: migrated.other || LegacyIframe },
```

> 注意：`legacy('/pv/other')` 这一行必须删除，否则 `/pv/other` 会残留一个 legacy 路由（虽然菜单已指向 `/other`，但残留路由易混淆）。删除后 `/pv/other` 仍由 Django 真实路由兜底（刷新时返回旧模板），符合「旧版保留作回退」原则。

- [ ] **Step 3: 后端测试新增 other url 改写断言**

在 `djangoPlant/test_migration.py` 的 `MenuApiTests` 类中，仿照 `test_migrated_menu_url_rewritten_to_frontend_path`，新增：

```python
    def test_other_menu_url_rewritten_to_frontend_path(self):
        s = self.c.session
        s['menus'] = ['other']
        s.save()
        resp = self.c.get('/api/menu')
        data = resp.json()['data']
        # other 是 standalone 菜单
        item = next(x for x in data['standalone'] if x['key'] == 'other')
        self.assertEqual(item['url'], '/other')
```

- [ ] **Step 4: 跑后端测试**

```bash
cd /Users/imc/djangoAndVue
/Users/imc/vllm/yes/envs/py310/bin/python3 manage.py test djangoPlant.test_migration -v 2
```
预期：全部 PASS（含新增的 other 测试）。

- [ ] **Step 5: Commit**

```bash
cd /Users/imc/djangoAndVue
git add djangoPlant/api_menu.py frontend/src/router/index.js djangoPlant/test_migration.py
git commit -m "feat(menu): 「操作变更记录」菜单 url 改写 /other 并接入 Vue 路由"
```

---

## Task 3: 端到端验证 + 生产构建 + 文档更新

**Files:**
- Modify: 无代码改动（验证 + 文档）
- Modify: `docs/superpowers/specs/2026-08-28-django-vue3-migration-design.md`（第 11 节验证清单勾选）

**Interfaces:**
- Consumes: Task 1 + Task 2 全部产物

- [x] **Step 1: 生产构建**

```bash
cd /Users/imc/djangoAndVue/frontend
npm run build
```
预期：无编译错误，产物在 `static/vue/`，index.html 引用 `/static/vue/assets/...`。
结果：通过，新增 lazy chunk `index-dY01b-uJ.js`（5.29KB，即 other 组件，懒加载生效）。

- [x] **Step 2: 端到端验证（browser-automation）**

启动 Django（`bash run.sh`，端口 8001），用无头浏览器验证：
- [x] 登录 → 进入 Vue 壳
- [x] 点击「操作变更记录」→ url 变为 `/other`，渲染 Vue 列表组件（非 iframe，无 `iframe` 元素）
- [x] 表格有数据（10 行，真实库有数据）
- [x] 点击「查询」→ 触发 `/pv/other` 请求，列表刷新
- [x] 点某行「删除」→ 弹出 el-popconfirm 二次确认（deleteBtnCount=1）
- [x] 操作人下拉 → `/pv/other/queryOpraterName` 返回 2 个选项
- [x] 直接刷新 `/other` → 仍是 Vue 组件（非旧模板，0 iframe）
- [x] console 错误 0，请求失败 0

> 验证脚本用 browser-automation 技能的 `--script` 驱动，真实登录用临时 e2e 账号（绑 role 1，验证后删除）。

- [x] **Step 3: 更新 spec 验证清单**

在 `docs/superpowers/specs/2026-08-28-django-vue3-migration-design.md` 第 11 节，把「操作变更记录」相关项勾选并补注已迁移。

- [x] **Step 4: 更新本计划进度标记并汇报**

在下方「进度记录」勾选完成，向用户汇报。

---

## 进度记录

- [x] Task 1 前端 other/index.vue 组件
- [x] Task 2 菜单 url 改写 + 路由接入 + 后端测试
- [x] Task 3 端到端验证 + 生产构建 + 文档更新

> 恢复执行时：从上到下找到第一个未勾选的 Task，从它的第一个未勾选 Step 继续。
