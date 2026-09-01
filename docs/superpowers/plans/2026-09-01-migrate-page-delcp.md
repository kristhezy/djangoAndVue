# 迁移「删除线索[合]」页面 实现计划（第二阶段第 4 页）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把「删除线索[合]」从 Django 模板 + jQuery（AT_delCP.html + 内联 JS）迁移为 Vue3 + Element Plus 组件，复用现有 3 个后端接口（零改动）。

**Architecture:** 沿用方案 B：`frontend/src/views/delCP/index.vue` 新建组件，菜单 url 由 `/api/menu` 改写为独立前端路径 `/delCP`（避开真实旧路由 `/sv/delCP`），POST 接口仍复用旧视图。

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
- **不删**：`templates/AT_delCP.html`、`saasview.py` 的 `delCP`/`delclueinfo`/`queryuibycp`/`saci` 视图，全部原样保留。
- **分支**：直接在 `main` 上继续。每步提交到 main。
- **测试策略**：后端唯一新增逻辑（`/api/menu` 对 delCP 的 url 改写）用 Django test client 写测试；前端 Vue 组件用 browser-automation + 手动清单验证。
- **Python 解释器**：`/Users/imc/vllm/yes/envs/py310/bin/python3`。
- **CSRF**：POST 请求由 `frontend/src/api/http.js` 统一加 `X-CSRFToken` header，组件直接 `import http from '../../api/http'`。
- **企业下拉框硬编码**：旧版在模板里写死 prod/test 两组企业（后端无企业列表接口），迁移后继续硬编码。
- **e2e 只读验证**：删除/添加线索是真实业务写操作，e2e 只验证「页面渲染 + 表单校验 + 只读接口 queryuibycp」，不真实调用 delclueinfo / saci。

---

## 后端契约（零改动，直接复用）

| 接口 | method | 请求体 | 返回 `data` |
|---|---|---|---|
| `/sv/delclueinfo` | POST | `{companyId, userId, ppc, delcheck, env, check:"del"}` | 字符串（如 `"删除成功..."`） |
| `/sv/queryuibycp` | POST | `{cid, tel, env}` | `{userId, partnerId}`（partnerId 可能为空串） |
| `/sv/saci` | POST | `{cid, cardid, uname, utel, bn, pId, env}` | 字符串（`"添加成功=>..."`） |

**字段注意：**
- `delcheck`：`delclue`（删除线索）或 `delpartner`（删除合伙人）。
- `saci` 的 `bn`：批量时为 2~1000 的整数，非批量固定传 `1`。
- `queryuibycp` 查询成功后回填卡片1的 `userId` 和 `ppidcontent`（联动）。

### 企业下拉硬编码列表（复刻旧模板 AT_delCP.html 第 78-100 行）

prod 组（11 家）、test 组（8 家），见 Task 1 组件代码中的 `companies` 常量。

### 联动逻辑（复刻旧版 changeInput）

1. 卡片1「企业名称」下拉选择：
   - 选「输入企业ID」（空值）→ 卡片1「企业ID」输入框清空可编辑，卡片1 env 设为 test 且**启用**，卡片2 env 设为 test。
   - 选具体企业 → 卡片1「企业ID」自动填该企业ID，卡片2「企业ID」同步填，卡片1 env 设为对应 prod/test 且**禁用**（锁定），卡片2 env 同步设为对应环境。
2. 卡片2 查询成功 → 卡片1「用户ID」「合伙人ID」自动回填。
3. 卡片1「删除类型」切换 → `delclue` 时合伙人ID禁用清空，`delpartner` 时启用。

---

## Task 1: 前端 delCP/index.vue 组件（三卡片 + 联动 + 校验）

**Files:**
- Create: `frontend/src/views/delCP/index.vue`

**Interfaces:**
- Consumes: `frontend/src/api/http.js`
- Produces: `DelCPPage` 组件（default export），供 Task 2 路由引用

- [ ] **Step 1: 写组件**

新建 `frontend/src/views/delCP/index.vue`，完整代码如下（照抄，不要改动逻辑）：

```vue
<template>
  <div class="delcp-page">
    <div class="delcp-cols">
      <!-- 卡片1: 删除线索/合伙人 -->
      <el-card class="delcp-card" shadow="never">
        <template #header><div class="delcp-title">删除线索/合伙人</div></template>
        <el-form label-width="90px">
          <el-form-item label="企业 ID" required>
            <el-input v-model="form1.companyName" placeholder="请输入企业ID" />
          </el-form-item>
          <el-form-item label="企业名称" required>
            <el-select v-model="form1.companyId" placeholder="输入企业ID" style="width:100%" @change="onCompanyChange">
              <el-option label="输入企业ID" value="" />
              <el-option-group label="🔽【prod】">
                <el-option v-for="c in companies.prod" :key="c.id" :label="c.name" :value="c.id" />
              </el-option-group>
              <el-option-group label="🔽【test】">
                <el-option v-for="c in companies.test" :key="c.id" :label="c.name" :value="c.id" />
              </el-option-group>
            </el-select>
          </el-form-item>
          <el-form-item label="用户 ID" required>
            <el-input v-model="form1.userId" />
          </el-form-item>
          <el-form-item label="合伙人 ID">
            <el-input v-model="form1.ppidcontent" :disabled="form1.delcheck !== 'delpartner'" />
          </el-form-item>
          <el-form-item label="删除类型">
            <el-radio-group v-model="form1.delcheck">
              <el-radio value="delclue">删除线索</el-radio>
              <el-radio value="delpartner">删除合伙人</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="环境">
            <el-radio-group v-model="form1.env" :disabled="envLocked">
              <el-radio value="prod">生产环境</el-radio>
              <el-radio value="test">测试环境</el-radio>
            </el-radio-group>
          </el-form-item>
          <div class="delcp-actions">
            <el-button type="primary" :loading="loading1" @click="cleanClue">提交</el-button>
            <el-button @click="resetForm1">重置</el-button>
          </div>
          <div class="delcp-note">※ 删除合伙人时:【先删除合伙人，再删除线索数据】</div>
          <div class="result" v-html="result1"></div>
        </el-form>
      </el-card>

      <!-- 卡片2: 根据手机号查询用户ID -->
      <el-card class="delcp-card" shadow="never">
        <template #header><div class="delcp-title">根据手机号查询用户ID</div></template>
        <el-form label-width="90px">
          <el-form-item label="企业 ID" required>
            <el-input v-model="form2.cid" />
          </el-form-item>
          <el-form-item label="手机号" required>
            <el-input v-model="form2.tel" maxlength="11" />
          </el-form-item>
          <el-form-item label="环境">
            <el-radio-group v-model="form2.env">
              <el-radio value="prod">生产环境</el-radio>
              <el-radio value="test">测试环境</el-radio>
            </el-radio-group>
          </el-form-item>
          <div class="delcp-actions">
            <el-button type="primary" :loading="loading2" @click="queryByCp">提交</el-button>
            <el-button @click="resetForm2">重置</el-button>
          </div>
          <div class="result" v-html="result2"></div>
        </el-form>
      </el-card>

      <!-- 卡片3: 销售添加线索 -->
      <el-card class="delcp-card" shadow="never">
        <template #header><div class="delcp-title">销售添加线索</div></template>
        <el-form label-width="90px">
          <el-form-item label="企业 ID" required>
            <el-input v-model="form3.companyId" />
          </el-form-item>
          <el-form-item label="员工 ID" required>
            <el-input v-model="form3.cardId" />
          </el-form-item>
          <el-form-item label="用户姓名" required>
            <el-input v-model="form3.userName" />
          </el-form-item>
          <el-form-item label="用户手机" required>
            <el-input v-model="form3.userTel" maxlength="11" />
          </el-form-item>
          <el-form-item label="合伙人 ID">
            <el-input v-model="form3.pId" />
          </el-form-item>
          <el-form-item label="是否批量">
            <el-checkbox v-model="form3.batch" />
            <el-input v-model="form3.batchNum" :disabled="!form3.batch" placeholder="输入2~1000的整数" class="batch-input" />
          </el-form-item>
          <el-form-item label="环境">
            <el-radio-group v-model="form3.env">
              <el-radio value="prod">生产环境</el-radio>
              <el-radio value="test">测试环境</el-radio>
            </el-radio-group>
          </el-form-item>
          <div class="delcp-actions">
            <el-button type="primary" :loading="loading3" @click="addClue">提交</el-button>
            <el-button @click="resetForm3">重置</el-button>
          </div>
          <div class="result" v-html="result3"></div>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

// 硬编码企业列表（复刻旧模板 AT_delCP.html 第 78-100 行）
const companies = {
  prod: [
    { id: '1021060956165488640', name: '招商版小程序测试企业1' },
    { id: '839508475783573504', name: '加推（测试）' },
    { id: '1040268843043500032', name: '超级推广部' },
    { id: '1012037449188364288', name: '深圳灰度测试企业5' },
    { id: '532972735412850688', name: '铁岭县供销合作社联合社' },
    { id: '1069929980139683840', name: '深圳市加推科技有限公司' },
    { id: '1189258248478707712', name: '红蚂蚁测试企业1' },
    { id: '1189258337557340160', name: '点石测试企业1' },
    { id: '1192136192859492352', name: '红蚂蚁装饰股份有限公司' },
    { id: '693225071459762176', name: '石家庄七度文化传播有限公司' },
    { id: '844635664262787073', name: '石家庄七度文化传播有限公司转介绍' },
  ],
  test: [
    { id: '1017368198385172480', name: '招商版测试企业7' },
    { id: '755550234976985088', name: '百度（中国）有限公司' },
    { id: '1035144123776442368', name: '招商版小程序测试企业8' },
    { id: '846400679986987008', name: '云盘版转介绍3' },
    { id: '870366245806292992', name: '北京积木世纪教育科技' },
    { id: '874593368431542272', name: '深圳市兴光电子有限公司' },
    { id: '1181172541784809472', name: '红蚂蚁家装' },
    { id: '1185152155297222656', name: '点石家装' },
  ],
}

const envLocked = ref(false)

const form1 = reactive({
  companyName: '',
  companyId: '',
  userId: '',
  ppidcontent: '',
  delcheck: 'delclue',
  env: 'prod',
})
const form2 = reactive({ cid: '', tel: '', env: 'prod' })
const form3 = reactive({
  companyId: '', cardId: '', userName: '', userTel: '', pId: '',
  batch: false, batchNum: '', env: 'prod',
})

const result1 = ref('')
const result2 = ref('')
const result3 = ref('')
const loading1 = ref(false)
const loading2 = ref(false)
const loading3 = ref(false)

function onCompanyChange(val) {
  if (val === '') {
    form1.companyName = ''
    form1.env = 'test'
    form2.env = 'test'
    envLocked.value = false
  } else {
    form1.companyName = val
    form2.cid = val
    const isProd = companies.prod.some(c => c.id === val)
    form1.env = isProd ? 'prod' : 'test'
    form2.env = isProd ? 'prod' : 'test'
    envLocked.value = true
  }
}

async function cleanClue() {
  const compid = form1.companyName || form1.companyId
  if (!compid) { ElMessage.warning('请先选择企业！'); return }
  if (!form1.userId) { ElMessage.warning('用户ID不能为空！'); return }
  if (form1.delcheck === 'delpartner' && !form1.ppidcontent) {
    ElMessage.warning('合伙人ID不能为空！'); return
  }
  loading1.value = true
  try {
    const resp = await http.post('/sv/delclueinfo', {
      companyId: compid, userId: form1.userId, ppc: form1.ppidcontent,
      delcheck: form1.delcheck, env: form1.env, check: 'del',
    })
    result1.value = resp.data?.data || ''
  } catch (e) {
    result1.value = ''
    ElMessage.error('删除失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    loading1.value = false
  }
}

async function queryByCp() {
  const cid = form2.cid
  const tel = form2.tel
  if (cid.length < 18 || isNaN(cid)) { ElMessage.warning('企业ID只能是大于等于18位的纯数字！'); return }
  if (tel.length !== 11 || isNaN(tel)) { ElMessage.warning('手机号只能为11位纯数字！'); return }
  loading2.value = true
  try {
    const resp = await http.post('/sv/queryuibycp', { cid, tel, env: form2.env })
    const d = resp.data?.data
    if (d) {
      result2.value = d.partnerId ? `userId: ${d.userId}, partnerId: ${d.partnerId}` : `userId: ${d.userId}`
      form1.userId = d.userId || ''
      form1.ppidcontent = d.partnerId || ''
    }
  } catch (e) {
    result2.value = ''
    ElMessage.error('查询失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    loading2.value = false
  }
}

async function addClue() {
  const { companyId, cardId, userName, userTel, pId, batch, batchNum, env } = form3
  let bn = 1
  if (batch) {
    if (!batchNum || isNaN(batchNum) || batchNum <= 1 || batchNum > 1000) {
      ElMessage.warning('批量数为[2~1000]之间的整数！'); return
    }
    bn = batchNum
  }
  if (!companyId || !cardId || !userName || !userTel) { ElMessage.warning('必填项不能为空！'); return }
  if (companyId.length < 18 || companyId.length > 19 || isNaN(companyId)) { ElMessage.warning('企业ID只能是18或19位的纯数字！'); return }
  if (userTel.length !== 11 || isNaN(userTel)) { ElMessage.warning('手机号只能是11位的纯数字！'); return }
  loading3.value = true
  try {
    const resp = await http.post('/sv/saci', { cid: companyId, cardid: cardId, uname: userName, utel: userTel, bn, pId, env })
    result3.value = resp.data?.data || ''
  } catch (e) {
    result3.value = ''
    ElMessage.error('添加失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    loading3.value = false
  }
}

function resetForm1() {
  form1.companyName = ''; form1.companyId = ''; form1.userId = ''
  form1.ppidcontent = ''; form1.delcheck = 'delclue'; form1.env = 'prod'
  envLocked.value = false
  result1.value = ''
}
function resetForm2() {
  form2.cid = ''; form2.tel = ''; form2.env = 'prod'
  result2.value = ''
}
function resetForm3() {
  form3.companyId = ''; form3.cardId = ''; form3.userName = ''; form3.userTel = ''
  form3.pId = ''; form3.batch = false; form3.batchNum = ''; form3.env = 'prod'
  result3.value = ''
}
</script>

<style scoped>
.delcp-page {
  height: 100%;
  overflow: hidden;
  background: #f0f2f5;
  padding: 16px;
  box-sizing: border-box;
}
.delcp-cols {
  height: 100%;
  display: flex;
  gap: 16px;
}
.delcp-card {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.delcp-card :deep(.el-card__body) { overflow-y: auto; }
.delcp-title { text-align: center; font-weight: 600; font-size: 18px; }
.delcp-actions { display: flex; justify-content: center; gap: 12px; margin: 12px 0; }
.delcp-note { font-size: 12px; color: #f56c6c; text-align: center; margin: 6px 0; }
.result { margin-top: 12px; font-size: 14px; color: #303133; white-space: pre-wrap; word-break: break-all; }
.batch-input { width: 140px; margin-left: 8px; }
</style>
```

- [ ] **Step 2: 语法自检**

```bash
cd /Users/imc/djangoAndVue/frontend
node --check src/views/delCP/index.vue 2>/dev/null; echo "（.vue 需 SFC 编译，改用 build 验证）"
```

> 语法正确性由 Task 3 的 `npm run build` 统一验证。

- [ ] **Step 3: Commit**

```bash
cd /Users/imc/djangoAndVue
git add frontend/src/views/delCP/index.vue
git commit -m "feat(frontend): 迁移「删除线索[合]」为 Vue 三卡片组件（删除/查询/添加线索）"
```

---

## Task 2: 菜单 url 改写 + 路由接入 + 后端测试

**Files:**
- Modify: `djangoPlant/api_menu.py`（`MIGRATED` 增加 `delCP`）
- Modify: `frontend/src/router/index.js`（`migrated` 增加 `delCP`，`legacy('/sv/delCP')` 换成 Vue 组件路由）
- Modify: `djangoPlant/test_migration.py`（新增一条 delCP url 改写测试）

- [ ] **Step 1: api_menu.py 的 MIGRATED 增加 delCP**

```python
MIGRATED = {
    'mergeUser': '/mergeUser',
    'other': '/other',
    'mynote': '/mynote',
    'delCP': '/delCP',
}
```

- [ ] **Step 2: router 接入 delCP**

`migrated` 增加 `delCP: () => import('../views/delCP/index.vue')`；children 里 `legacy('/sv/delCP')` 改为 `{ path: 'delCP', component: migrated.delCP || LegacyIframe }`。

- [ ] **Step 3: 后端测试新增 delCP url 改写断言**

仿照 mynote 测试，新增 `test_delcp_menu_url_rewritten_to_frontend_path`（delCP 在 GROUPS 的 tools 组，用 `data['groups']` 查找 key=='delCP'，断言 url=='/delCP'）。

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
git commit -m "feat(menu): 「删除线索[合]」菜单 url 改写 /delCP 并接入 Vue 路由"
```

---

## Task 3: 端到端验证 + 生产构建 + 文档更新

- [x] **Step 1: 生产构建**：`npm run build`（通过，产物在 static/vue/）

- [x] **Step 2: 端到端只读验证（browser-automation）**
  - [x] 直达 url `/delCP`，渲染 Vue 三卡片（0 iframe）
  - [x] 三卡片标题齐全（删除线索/合伙人、根据手机号查询用户ID、销售添加线索）
  - [x] 企业下拉含 prod/test 两组企业（展开后可见「🔽【prod】」「🔽【test】」及企业名）
  - [x] 选企业 → 卡片1「企业ID」自动填 `1021060956165488640`、env 锁定（disabled）
  - [x] 删除类型切换 → 合伙人ID禁用（delclue）/启用（delpartner）
  - [x] 卡片2 校验（企业ID <18位 → 提示「企业ID只能是大于等于18位的纯数字！」）
  - [x] 卡片2 只读查询（queryuibycp 真调，返回「查询结果为None」即接口已通；回填逻辑在数据缺失时正常为空）
  - [x] 刷新 `/delCP` 仍 Vue 版（0 iframe，console 0 错误，请求 0 失败）

> 只读验证：未真实调用 delclueinfo / saci 写接口。临时 e2e 账号 e2e_delcp 已删除。

- [x] **Step 3: 更新 spec 验证清单**

- [x] **Step 4: 更新本计划进度标记并汇报**

---

## 进度记录

- [x] Task 1 前端 delCP/index.vue 组件
- [x] Task 2 菜单 url 改写 + 路由接入 + 后端测试
- [x] Task 3 端到端验证 + 生产构建 + 文档更新
