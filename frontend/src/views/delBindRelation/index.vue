<template>
  <div class="mo-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title"><i class="fa-solid fa-link-slash"></i> 清除绑定关系</h2>
      </div>
    </div>

    <div class="mo-body">
      <div class="mo-col">
        <!-- 卡片1: 清除公众号/小程序绑定数据 -->
        <div :class="['m-card', {collapsed:!cards.c1}]">
          <div class="m-card-hd accent-blue" @click="cards.c1=!cards.c1">
            <div class="m-card-hd-left"><i class="fa-solid fa-unlink card-icon"></i><h3>清除公众号/小程序绑定</h3></div>
            <i :class="['fa-solid fa-chevron-right chevron', {open:cards.c1}]"></i>
          </div>
          <div class="m-card-bd">
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span>企业 ID</label><el-input v-model="form1.companyId" placeholder="请输入企业ID" /></div>
              <div class="fgr"><label><span class="rq">*</span>应用 ID</label>
                <el-select v-model="form1.appId" style="width:100%">
                  <el-option v-for="a in appList" :key="a.id" :label="a.name" :value="a.id" />
                </el-select>
              </div>
              <div class="fgr"><label><span class="rq">*</span>Status</label>
                <el-select v-model="form1.status" style="width:100%">
                  <el-option v-for="s in ['0', '1', '2']" :key="s" :label="s" :value="s" />
                </el-select>
              </div>
            </div>
            <EnvRadio v-model="form1.env" name="env1" />
            <BtnGroup @reset="reset1" @submit="clearBind" :loading="loading1" />
            <div class="result">{{ formatResult(result1) }}</div>
          </div>
        </div>
      </div>

      <div class="mo-col">
        <!-- 卡片2: 清除过期企业信息数据 -->
        <div :class="['m-card', {collapsed:!cards.c2}]">
          <div class="m-card-hd accent-orange" @click="cards.c2=!cards.c2">
            <div class="m-card-hd-left"><i class="fa-solid fa-building-circle-xmark card-icon"></i><h3>清除过期企业信息</h3></div>
            <i :class="['fa-solid fa-chevron-right chevron', {open:cards.c2}]"></i>
          </div>
          <div class="m-card-bd">
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span>企业 ID</label><el-input v-model="form2.companyIds" placeholder="支持逗号/换行/空格分隔多个" /></div>
            </div>
            <EnvRadio v-model="form2.env" name="env2" />
            <BtnGroup @reset="reset2" @submit="clearExpired" :loading="loading2" />
            <div class="notice">
              <ol>
                <b>清除过期企业，功能包含以下3点：</b>
                <li>企业设置为注销状态</li>
                <li>关闭员工雷达，清除员工和推荐官app登录token</li>
                <li>解除企业第三方绑定关系(公众号、小程序、企微)</li>
              </ol>
            </div>
            <div class="result">{{ formatResult(result2) }}</div>
          </div>
        </div>
      </div>

      <div class="mo-col">
        <!-- 卡片3: 清除app登录token -->
        <div :class="['m-card', {collapsed:!cards.c3}]">
          <div class="m-card-hd accent-green" @click="cards.c3=!cards.c3">
            <div class="m-card-hd-left"><i class="fa-solid fa-key card-icon"></i><h3>清除app登录token</h3></div>
            <i :class="['fa-solid fa-chevron-right chevron', {open:cards.c3}]"></i>
          </div>
          <div class="m-card-bd">
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span>企业 ID</label><el-input v-model="form3.companyId" placeholder="请输入企业ID" /></div>
            </div>
            <EnvRadio v-model="form3.env" name="env3" />
            <BtnGroup @reset="reset3" @submit="clearToken" :loading="loading3" />
            <div class="result">{{ formatResult(result3) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

// --- Inline sub-components ---
const EnvRadio = {
  props: ['modelValue', 'name'], emits: ['update:modelValue'],
  template: `<div class="env-group"><div class="env-track"><label :class="{active:modelValue==='test'}"><i class="fa-solid fa-flask"></i><input type="radio" :name="name" value="test" :checked="modelValue==='test'" @change="$emit('update:modelValue','test')"/><span>测试环境</span></label><label :class="{active:modelValue==='prod'}"><i class="fa-solid fa-rocket"></i><input type="radio" :name="name" value="prod" :checked="modelValue==='prod'" @change="$emit('update:modelValue','prod')"/><span>生产环境</span></label></div></div>`,
}
const BtnGroup = {
  props: ['loading'],
  emits: ['reset', 'submit'],
  template: `<div class="btn-group"><el-button @click="$emit('reset')">重置</el-button><el-button type="primary" :loading="loading" @click="$emit('submit')">提交</el-button></div>`,
}

const appList = [
  { id: 'wx_oa', name: '公众号' },
  { id: 'card', name: '小程序' },
  { id: 'cpe_backlog', name: '自建应用' },
  { id: 'cpe_investment_applet', name: '招商/推广版小程序' },
  { id: 'cpe_partner_applet', name: '合伙人小程序' },
]

const cards = reactive({ c1: true, c2: true, c3: true })

const form1 = reactive({ companyId: '', appId: 'wx_oa', status: '0', env: 'prod' })
const form2 = reactive({ companyIds: '', env: 'prod' })
const form3 = reactive({ companyId: '', env: 'prod' })
const result1 = ref(''), result2 = ref(''), result3 = ref('')
const loading1 = ref(false), loading2 = ref(false), loading3 = ref(false)

function formatResult(str) { return (str || '').replace(/<br\s*\/?>/gi, '\n') }

async function clearBind() {
  if (!form1.companyId) { ElMessage.warning('"企业ID"不能为空！'); return }
  loading1.value = true
  try {
    const resp = await http.post('/sv/forWeCom', { companyId: form1.companyId, appId: form1.appId, status: form1.status, env: form1.env, type: 3 })
    result1.value = resp.data?.data || ''
  } catch (e) { result1.value = ''; ElMessage.error('操作失败：' + (e?.response?.data?.msg || e.message)) }
  finally { loading1.value = false }
}

async function clearExpired() {
  if (!form2.companyIds) { ElMessage.warning('"企业ID"不能为空！'); return }
  loading2.value = true
  try {
    const resp = await http.post('/sv/delBindRelation', { companyIds: form2.companyIds, env: form2.env })
    result2.value = resp.data?.data || ''
  } catch (e) { result2.value = ''; ElMessage.error('操作失败：' + (e?.response?.data?.msg || e.message)) }
  finally { loading2.value = false }
}

async function clearToken() {
  if (!form3.companyId) { ElMessage.warning('"企业ID"不能为空！'); return }
  loading3.value = true
  try {
    const resp = await http.post('/sv/cleanAppToken', { companyId: form3.companyId, env: form3.env })
    result3.value = resp.data?.data || resp.data?.msg || '操作完成'
  } catch (e) { result3.value = ''; ElMessage.error('操作失败：' + (e?.response?.data?.msg || e.message)) }
  finally { loading3.value = false }
}

function reset1() { form1.companyId = ''; form1.appId = 'wx_oa'; form1.status = '0'; form1.env = 'prod'; result1.value = '' }
function reset2() { form2.companyIds = ''; form2.env = 'prod'; result2.value = '' }
function reset3() { form3.companyId = ''; form3.env = 'prod'; result3.value = '' }
</script>

<style scoped>
/* ===================== 页面骨架 ===================== */
/* mo-page / mo-body / mo-col / m-card 等样式由 design-system.css 统一提供 */

/* ===================== 卡片 ===================== */
.m-card {
  background:var(--bg-card); border-radius:12px;
  box-shadow:var(--shadow-card);
  overflow:hidden; transition:box-shadow .2s;
  break-inside:avoid; margin-bottom:12px;
}
.m-card:hover { box-shadow:var(--shadow-card-hover); }

.m-card-hd {
  display:flex; justify-content:space-between; align-items:center;
  padding:14px 18px; cursor:pointer; user-select:none;
  border-left:4px solid transparent; transition:background .15s;
}
.m-card-hd:hover { background:var(--bg-hover); }
.m-card-hd-left { display:flex; align-items:center; gap:10px; }
.card-icon { font-size:15px; width:18px; text-align:center; }
.m-card-hd h3 { margin:0; font-size:14px; font-weight:600; color:var(--text-primary); letter-spacing:.2px; }

.chevron { font-size:11px; color:var(--text-placeholder); transition:transform .25s ease; }
.chevron.open { transform:rotate(90deg); }

.m-card.collapsed .m-card-bd { display:none; }
.m-card-bd {
  padding:16px 18px; display:flex; flex-direction:column; align-items:center;
  border-top:1px solid var(--border-card);
}

.accent-blue  { border-left-color:#3b82f6; }  .accent-blue  .card-icon { color:#3b82f6; }
.accent-green { border-left-color:#22c55e; }  .accent-green .card-icon { color:#22c55e; }
.accent-orange{ border-left-color:#f59e0b; }  .accent-orange .card-icon { color:#f59e0b; }

/* ===================== 表单 Grid ===================== */
.fg { display:grid; grid-template-columns:auto 300px; column-gap:10px; row-gap:10px; align-items:center; width:fit-content; margin:0 auto; }
.fgr { display:contents; }
.fgr label { text-align:left; white-space:nowrap; font-size:13px; color:var(--text-secondary); }
.fgr :deep(.el-input), .fgr :deep(.el-select) { width:100% !important; }
.rq { color:#ef4444; margin-right:2px; }

/* ===================== 环境切换 ===================== */
:deep(.env-group) { display:inline-flex; justify-content:center; margin:12px auto 8px; }
:deep(.env-track) { display:inline-flex; gap:0; background:var(--bg-hover); border-radius:6px; padding:2px; flex-wrap:nowrap; }
:deep(.env-track label) {
  cursor:pointer; display:inline-flex; align-items:center; gap:4px;
  padding:5px 14px; border-radius:5px; border:none; background:transparent;
  font-size:12px; font-weight:500; color:var(--text-muted); transition:all .2s;
  user-select:none; white-space:nowrap;
}
:deep(.env-track label.active) { background:var(--bg-card); color:var(--color-primary-light); box-shadow:0 1px 3px rgba(0,0,0,.1); font-weight:600; }
:deep(.env-track label i) { font-size:11px; }
:deep(.env-track input[type="radio"]) { display:none; }

/* ===================== 按钮 ===================== */
:deep(.btn-group) { display:flex; justify-content:center; gap:12px; margin:8px 0 10px; }

/* ===================== 结果区 ===================== */
.result {
  width:100%; min-height:24px; max-height:140px; overflow-y:auto;
  padding:8px 12px; border-radius:8px; background:var(--bg-subtle);
  font-size:13px; text-align:center; line-height:1.7; color:var(--text-secondary);
  white-space:pre-wrap; word-break:break-all;
}
.result:empty { display:none; }

/* ===================== 提示 ===================== */
.notice {
  font-size:12px; color:#92400e; border-radius:8px;
  margin:8px 0; text-align:left; line-height:1.625;
  background:#fffbeb; padding:12px; width:100%;
}
.notice ol { padding-left:20px; margin:0; }
</style>
