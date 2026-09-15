<template>
  <div class="mo-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title"><i class="fa-solid fa-wrench"></i> 定制功能</h2>
      </div>
    </div>

    <div class="mo-body">
      <div class="column">
        <!-- 卡片1: 红蚂蚁企业修改客户阶段 -->
        <div :class="['m-card', {collapsed:!cards.c1}]">
          <div class="m-card-hd accent-red" @click="cards.c1=!cards.c1">
            <div class="m-card-hd-left"><i class="fa-solid fa-chart-line card-icon"></i><h3>红蚂蚁修改客户阶段</h3></div>
            <i :class="['fa-solid fa-chevron-right chevron', {open:cards.c1}]"></i>
          </div>
          <div class="m-card-bd">
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span>客户 ID</label><el-input v-model="form1.cfid" placeholder="输入CustomerFormID" /></div>
              <div class="fgr"><label><span class="rq">*</span>跟进状态</label><el-input v-model="form1.fs" placeholder="生命周期顺序，从0起" /></div>
            </div>
            <EnvRadio v-model="form1.env" name="env1" />
            <BtnGroup @reset="reset1" @submit="updateStage" :loading="loading1" />
            <div class="result">{{ result1 }}</div>
          </div>
        </div>

        <!-- 卡片2: 华为云license激活 -->
        <div :class="['m-card', {collapsed:!cards.c2}]">
          <div class="m-card-hd accent-blue" @click="cards.c2=!cards.c2">
            <div class="m-card-hd-left"><i class="fa-solid fa-key card-icon"></i><h3>华为云license激活</h3></div>
            <i :class="['fa-solid fa-chevron-right chevron', {open:cards.c2}]"></i>
          </div>
          <div class="m-card-bd">
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span>企业 ID</label><el-input v-model="form2.compid" placeholder="输入加推的企业ID" /></div>
              <div class="fgr"><label><span class="rq">*</span>授权码</label><el-input v-model="form2.lisence" placeholder="华为云lisence授权码" /></div>
              <div class="fgr"><label><span class="rq">*</span>备注</label><el-input v-model="form2.remark" placeholder="lisence的备注信息" /></div>
            </div>
            <EnvRadio v-model="form2.env" name="env2" />
            <BtnGroup @reset="reset2" @submit="activateLicense" :loading="loading2" />
            <div class="result">{{ result2 }}</div>
          </div>
        </div>

        <!-- 卡片3: 预留 -->
        <div :class="['m-card', {collapsed:!cards.c3}]">
          <div class="m-card-hd accent-green" @click="cards.c3=!cards.c3">
            <div class="m-card-hd-left"><i class="fa-solid fa-puzzle-piece card-icon"></i><h3>预留功能区域</h3></div>
            <i :class="['fa-solid fa-chevron-right chevron', {open:cards.c3}]"></i>
          </div>
          <div class="m-card-bd">
            <div class="placeholder"><p>此区域预留用于未来功能扩展</p></div>
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

const cards = reactive({ c1: true, c2: true, c3: true })
const form1 = reactive({ cfid: '', fs: '', env: 'prod' })
const form2 = reactive({ compid: '', lisence: '', remark: '', env: 'prod' })
const result1 = ref(''), result2 = ref('')
const loading1 = ref(false), loading2 = ref(false)

async function updateStage() {
  if (!form1.cfid || !form1.fs) { ElMessage.warning('必填项不能为空！'); return }
  loading1.value = true
  try {
    const resp = await http.post('/sv/dzFunction', { cfid: form1.cfid, fs: form1.fs, env: form1.env, type: 'hmyupdcs' })
    result1.value = resp.data?.data || ''
  } catch (e) { result1.value = ''; ElMessage.error('操作失败：' + (e?.response?.data?.msg || e.message)) }
  finally { loading1.value = false }
}

async function activateLicense() {
  if (!form2.lisence) { ElMessage.warning('"lisence"不能为空！'); return }
  loading2.value = true
  try {
    const resp = await http.post('/sv/dzFunction', { compid: form2.compid, lisence: form2.lisence, remark: form2.remark, env: form2.env, type: 'hwylicensejh' })
    result2.value = resp.data?.data || ''
  } catch (e) { result2.value = ''; ElMessage.error('操作失败：' + (e?.response?.data?.msg || e.message)) }
  finally { loading2.value = false }
}

function reset1() { form1.cfid = ''; form1.fs = ''; form1.env = 'prod'; result1.value = '' }
function reset2() { form2.compid = ''; form2.lisence = ''; form2.remark = ''; form2.env = 'prod'; result2.value = '' }
</script>

<style scoped>
.mo-page { display:flex; flex-direction:column; height:100%; overflow:hidden; background:var(--bg-page); }
.toolbar { display:flex; justify-content:space-between; align-items:center; padding:12px 20px 8px; flex-shrink:0; }
.toolbar-left { display:flex; align-items:center; gap:8px; }
.page-title { margin:0; font-size:16px; font-weight:700; color:var(--text-primary); letter-spacing:.3px; }
.page-title i { color:var(--color-primary-light); margin-right:4px; }

.mo-body { flex:1; padding:0 14px 14px; overflow-y:auto; }
.mo-body::-webkit-scrollbar { width:4px; }
.mo-body::-webkit-scrollbar-track { background:transparent; }
.mo-body::-webkit-scrollbar-thumb { background:var(--scrollbar-thumb); border-radius:4px; }
.column { columns:3; column-gap:12px; }

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
.accent-red   { border-left-color:#ef4444; }  .accent-red   .card-icon { color:#ef4444; }

.fg { display:grid; grid-template-columns:auto 300px; column-gap:10px; row-gap:10px; align-items:center; width:fit-content; margin:0 auto; }
.fgr { display:contents; }
.fgr label { text-align:left; white-space:nowrap; font-size:13px; color:var(--text-secondary); }
.fgr :deep(.el-input), .fgr :deep(.el-select) { width:100% !important; }
.rq { color:#ef4444; margin-right:2px; }

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

:deep(.btn-group) { display:flex; justify-content:center; gap:12px; margin:8px 0 10px; }

.result {
  width:100%; min-height:24px; max-height:140px; overflow-y:auto;
  padding:8px 12px; border-radius:8px; background:var(--bg-subtle);
  font-size:13px; text-align:center; line-height:1.7; color:var(--text-secondary);
  white-space:pre-wrap; word-break:break-all;
}
.result:empty { display:none; }

.placeholder { display:flex; align-items:center; justify-content:center; width:100%; padding:24px 0; }
.placeholder p { color:var(--text-placeholder); text-align:center; }
</style>
