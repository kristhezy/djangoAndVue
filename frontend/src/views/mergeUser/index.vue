<template>
  <div class="mo-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title"><i class="fa-solid fa-people-arrows"></i> 手工合并用户</h2>
      </div>
    </div>

    <div class="mo-body">
      <div class="column">
        <div class="m-card" style="max-width:680px;margin:0 auto;">
          <div class="m-card-hd accent-blue">
            <div class="m-card-hd-left"><i class="fa-solid fa-people-arrows card-icon"></i><h3>手工合并用户</h3></div>
          </div>
          <div class="m-card-bd">
            <div class="fg fg-wide">
              <div class="fgr"><label><span class="rq">*</span>企业ID</label><el-input v-model="form.companyId" placeholder="请输入企业 ID" /></div>
              <div class="fgr"><label><span class="rq">*</span>openID</label>
                <el-input v-model="form.opids" type="textarea" :rows="6" placeholder="多个 openID 换行分隔" />
              </div>
            </div>
            <EnvRadio v-model="form.env" name="env1" />
            <BtnGroup @reset="reset" @submit="submit" :loading="loading" />
            <div v-if="result" :class="['result', alertType==='error'?'result--error':'']">{{ result }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import http from '../../api/http'

const EnvRadio = {
  props: ['modelValue', 'name'], emits: ['update:modelValue'],
  template: `<div class="env-group"><div class="env-track"><label :class="{active:modelValue==='test'}"><i class="fa-solid fa-flask"></i><input type="radio" :name="name" value="test" :checked="modelValue==='test'" @change="$emit('update:modelValue','test')"/><span>测试环境</span></label><label :class="{active:modelValue==='prod'}"><i class="fa-solid fa-rocket"></i><input type="radio" :name="name" value="prod" :checked="modelValue==='prod'" @change="$emit('update:modelValue','prod')"/><span>生产环境</span></label></div></div>`,
}
const BtnGroup = {
  props: ['loading'],
  emits: ['reset', 'submit'],
  template: `<div class="btn-group"><el-button @click="$emit('reset')">重置</el-button><el-button type="primary" :loading="loading" @click="$emit('submit')">提交</el-button></div>`,
}

const loading = ref(false)
const result = ref('')
const alertType = ref('success')
const form = reactive({ companyId: '', opids: '', env: 'prod' })

async function submit() {
  if (!form.companyId || !form.opids) { return }
  loading.value = true
  result.value = ''
  try {
    const resp = await http.post('/sv/mergeUser', { companyId: form.companyId, opids: form.opids, env: form.env })
    const a = resp.data?.data?.a ?? JSON.stringify(resp.data?.data ?? '')
    result.value = a
    alertType.value = String(resp.data?.code) === '0' ? 'success' : 'error'
  } catch (e) {
    alertType.value = 'error'
    result.value = '请求失败：' + (e?.response?.data?.msg || e.message)
  } finally {
    loading.value = false
  }
}

function reset() { form.companyId = ''; form.opids = ''; form.env = 'prod'; result.value = ''; alertType.value = 'success' }
</script>

<style scoped>
.mo-page { display:flex; flex-direction:column; height:100%; overflow:hidden; background:#f5f6fa; }
.toolbar { display:flex; justify-content:space-between; align-items:center; padding:12px 20px 8px; flex-shrink:0; }
.toolbar-left { display:flex; align-items:center; gap:8px; }
.page-title { margin:0; font-size:16px; font-weight:700; color:#1e293b; letter-spacing:.3px; }
.page-title i { color:#6366f1; margin-right:4px; }

.mo-body { flex:1; padding:0 14px 14px; overflow-y:auto; }
.mo-body::-webkit-scrollbar { width:4px; }
.mo-body::-webkit-scrollbar-track { background:transparent; }
.mo-body::-webkit-scrollbar-thumb { background:#cbd5e1; border-radius:4px; }
.column { columns:1; }

.m-card {
  background:#fff; border-radius:12px;
  box-shadow:0 1px 3px rgba(0,0,0,.06), 0 1px 2px rgba(0,0,0,.04);
  overflow:hidden; transition:box-shadow .2s;
  break-inside:avoid; margin-bottom:12px;
}
.m-card:hover { box-shadow:0 4px 12px rgba(0,0,0,.08), 0 2px 4px rgba(0,0,0,.04); }
.m-card-hd {
  display:flex; justify-content:space-between; align-items:center;
  padding:14px 18px; user-select:none;
  border-left:4px solid transparent;
}
.m-card-hd-left { display:flex; align-items:center; gap:10px; }
.card-icon { font-size:15px; width:18px; text-align:center; }
.m-card-hd h3 { margin:0; font-size:14px; font-weight:600; color:#1e293b; letter-spacing:.2px; }
.m-card-bd {
  padding:16px 18px; display:flex; flex-direction:column; align-items:center;
  border-top:1px solid #f1f5f9;
}

.accent-blue { border-left-color:#3b82f6; } .accent-blue .card-icon { color:#3b82f6; }

.fg { display:grid; grid-template-columns:auto 1fr; column-gap:12px; row-gap:12px; align-items:start; width:fit-content; margin:0 auto; }
.fg-wide { grid-template-columns:auto minmax(250px, 420px); }
.fgr { display:contents; }
.fgr label { text-align:left; white-space:nowrap; font-size:13px; color:#475569; padding-top:6px; }
.fgr :deep(.el-input), .fgr :deep(.el-select) { width:100% !important; }
.rq { color:#ef4444; margin-right:2px; }

:deep(.env-group) { display:inline-flex; justify-content:center; margin:14px auto 10px; }
:deep(.env-track) { display:inline-flex; gap:0; background:#f1f5f9; border-radius:6px; padding:2px; flex-wrap:nowrap; }
:deep(.env-track label) {
  cursor:pointer; display:inline-flex; align-items:center; gap:4px;
  padding:5px 14px; border-radius:5px; border:none; background:transparent;
  font-size:12px; font-weight:500; color:#64748b; transition:all .2s;
  user-select:none; white-space:nowrap;
}
:deep(.env-track label.active) { background:#fff; color:#6366f1; box-shadow:0 1px 3px rgba(0,0,0,.1); font-weight:600; }
:deep(.env-track label i) { font-size:11px; }
:deep(.env-track input[type="radio"]) { display:none; }

:deep(.btn-group) { display:flex; justify-content:center; gap:12px; margin:10px 0 12px; }

.result {
  width:100%; padding:10px 14px; border-radius:8px; background:#f0fdf4;
  font-size:13px; text-align:left; line-height:1.7; color:#15803d;
  white-space:pre-wrap; word-break:break-all;
}
.result--error { background:#fef2f2; color:#dc2626; }
</style>
