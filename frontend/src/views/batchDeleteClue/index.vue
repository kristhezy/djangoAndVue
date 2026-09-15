<template>
  <div class="mo-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title"><i class="fa-solid fa-trash-can"></i> 批量删除线索</h2>
      </div>
    </div>

    <div class="mo-body">
      <div class="m-card">
        <div class="m-card-hd accent-red">
          <div class="m-card-hd-left"><i class="fa-solid fa-eraser card-icon"></i><h3>批量删除线索</h3></div>
        </div>
        <div class="m-card-bd">
          <div class="fg fg-wide">
            <div class="fgr"><label><span class="rq">*</span>选择企业ID</label>
              <el-select v-model="form.cid" placeholder="选择企业ID" style="width:100%">
                <el-option v-for="c in companies" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
            </div>
            <div class="fgr"><label><span class="rq">*</span>手机号</label>
              <el-input v-model="form.phones" type="textarea" :rows="8" placeholder="输入手机号（支持逗号/换行/空格分隔多个）" />
            </div>
          </div>
          <EnvRadio v-model="form.env" name="env1" />
          <BtnGroup @reset="reset" @submit="submit" :loading="loading" />
          <div class="result">{{ result }}</div>
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
/* ===================== 页面骨架 ===================== */
.mo-page { display:flex; flex-direction:column; height:100%; overflow:hidden; background:var(--bg-page); }
.toolbar { display:flex; justify-content:space-between; align-items:center; padding:12px 20px 8px; flex-shrink:0; }
.toolbar-left { display:flex; align-items:center; gap:8px; }
.page-title { margin:0; font-size:16px; font-weight:700; color:var(--text-primary); letter-spacing:.3px; }
.page-title i { color:var(--color-primary-light); margin-right:4px; }

.mo-body { flex:1; padding:0 14px 14px; overflow-y:auto; display:flex; justify-content:center; align-items:flex-start; }
.mo-body::-webkit-scrollbar { width:4px; }
.mo-body::-webkit-scrollbar-track { background:transparent; }
.mo-body::-webkit-scrollbar-thumb { background:var(--scrollbar-thumb); border-radius:4px; }

/* ===================== 卡片 ===================== */
.m-card {
  background:var(--bg-card); border-radius:12px; width:680px; max-width:100%;
  box-shadow:var(--shadow-card);
  overflow:hidden; transition:box-shadow .2s;
}
.m-card:hover { box-shadow:var(--shadow-card-hover); }

.m-card-hd {
  display:flex; justify-content:space-between; align-items:center;
  padding:14px 18px; user-select:none;
  border-left:4px solid transparent;
}
.m-card-hd-left { display:flex; align-items:center; gap:10px; }
.card-icon { font-size:15px; width:18px; text-align:center; }
.m-card-hd h3 { margin:0; font-size:14px; font-weight:600; color:var(--text-primary); letter-spacing:.2px; }

.m-card-bd {
  padding:16px 18px; display:flex; flex-direction:column; align-items:center;
  border-top:1px solid var(--border-card);
}

.accent-red { border-left-color:#ef4444; } .accent-red .card-icon { color:#ef4444; }

/* ===================== 表单 Grid ===================== */
.fg { display:grid; grid-template-columns:auto 1fr; column-gap:12px; row-gap:12px; align-items:start; width:fit-content; margin:0 auto; }
.fg-wide { grid-template-columns:auto minmax(300px, 500px); }
.fgr { display:contents; }
.fgr label { text-align:left; white-space:nowrap; font-size:13px; color:var(--text-secondary); padding-top:6px; }
.fgr :deep(.el-input), .fgr :deep(.el-select) { width:100% !important; }
.rq { color:#ef4444; margin-right:2px; }

/* ===================== 环境切换 ===================== */
:deep(.env-group) { display:inline-flex; justify-content:center; margin:14px auto 10px; }
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
:deep(.btn-group) { display:flex; justify-content:center; gap:12px; margin:10px 0 12px; }

/* ===================== 结果区 ===================== */
.result {
  width:100%; min-height:40px; max-height:360px; overflow-y:auto;
  padding:10px 14px; border-radius:8px; background:var(--bg-subtle);
  font-size:13px; text-align:center; line-height:1.7; color:var(--color-primary-light);
  white-space:pre-wrap; word-break:break-all;
}
.result:empty { display:none; }
</style>
