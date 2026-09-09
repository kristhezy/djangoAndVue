<template>
  <div class="mo-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title"><i class="fa-solid fa-building-shield"></i> 企微工具</h2>
      </div>
    </div>

    <div class="mo-body">
      <div class="column">
        <!-- 卡片1: 生成企微应用链接 -->
        <div :class="['m-card', {collapsed:!cards.c1}]">
          <div class="m-card-hd accent-blue" @click="cards.c1=!cards.c1">
            <div class="m-card-hd-left"><i class="fa-solid fa-link card-icon"></i><h3>生成企微应用链接</h3></div>
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
            </div>
            <EnvRadio v-model="form1.env" name="env1" />
            <BtnGroup @reset="reset1" @submit="genLink" :loading="loading1" />
            <el-input v-model="result1" type="textarea" :rows="4" readonly placeholder="结果" class="result-box" />
          </div>
        </div>

        <!-- 卡片2: 获取密文企微ID -->
        <div :class="['m-card', {collapsed:!cards.c2}]">
          <div class="m-card-hd accent-green" @click="cards.c2=!cards.c2">
            <div class="m-card-hd-left"><i class="fa-solid fa-lock card-icon"></i><h3>获取密文企微ID</h3></div>
            <i :class="['fa-solid fa-chevron-right chevron', {open:cards.c2}]"></i>
          </div>
          <div class="m-card-bd">
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span>企微ID(明文)</label><el-input v-model="form2.corpId" placeholder="请输入企微ID" /></div>
            </div>
            <EnvRadio v-model="form2.env" name="env2" />
            <BtnGroup @reset="reset2" @submit="getCorpId" :loading="loading2" />
            <el-input v-model="result2" type="textarea" :rows="4" readonly placeholder="结果" class="result-box" />
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
  { id: 'cpe_tong', name: '通讯录' },
  { id: 'cpe_radar', name: '雷达' },
  { id: 'cpe_file', name: '文件' },
  { id: 'cpe_article', name: '文章' },
  { id: 'cpe_video', name: '视频' },
  { id: 'cpe_poster', name: '海报' },
  { id: 'cpe_manual', name: '宣传册' },
  { id: 'cpe_case', name: '案例' },
]

const cards = reactive({ c1: true, c2: true })
const form1 = reactive({ companyId: '', appId: 'cpe_tong', env: 'prod' })
const form2 = reactive({ corpId: '', env: 'prod' })
const result1 = ref(''), result2 = ref('')
const loading1 = ref(false), loading2 = ref(false)

async function genLink() {
  const cid = form1.companyId
  if (!cid || cid.length < 18 || cid.length > 19 || isNaN(cid)) { ElMessage.warning('企业ID只能是18或19位的纯数字！'); return }
  loading1.value = true
  try {
    const resp = await http.post('/sv/forWeCom', { companyId: cid, appId: form1.appId, env: form1.env, type: 1 })
    result1.value = resp.data?.data || ''
    if (result1.value.includes('http')) window.open(result1.value)
  } catch (e) { result1.value = ''; ElMessage.error('生成失败：' + (e?.response?.data?.msg || e.message)) }
  finally { loading1.value = false }
}

async function getCorpId() {
  const corpid = form2.corpId
  if (!corpid) { ElMessage.warning('"企微ID(明文)"不能为空！'); return }
  loading2.value = true
  try {
    const resp = await http.post('/sv/forWeCom', { corpId: corpid, env: form2.env, type: 2 })
    result2.value = resp.data?.data || ''
  } catch (e) { result2.value = ''; ElMessage.error('获取失败：' + (e?.response?.data?.msg || e.message)) }
  finally { loading2.value = false }
}

function reset1() { form1.companyId = ''; form1.appId = 'cpe_tong'; form1.env = 'prod'; result1.value = '' }
function reset2() { form2.corpId = ''; form2.env = 'prod'; result2.value = '' }
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
.column { columns:2; column-gap:12px; }

.m-card {
  background:#fff; border-radius:12px;
  box-shadow:0 1px 3px rgba(0,0,0,.06), 0 1px 2px rgba(0,0,0,.04);
  overflow:hidden; transition:box-shadow .2s;
  break-inside:avoid; margin-bottom:12px;
}
.m-card:hover { box-shadow:0 4px 12px rgba(0,0,0,.08), 0 2px 4px rgba(0,0,0,.04); }
.m-card-hd {
  display:flex; justify-content:space-between; align-items:center;
  padding:14px 18px; cursor:pointer; user-select:none;
  border-left:4px solid transparent; transition:background .15s;
}
.m-card-hd:hover { background:#fafbfc; }
.m-card-hd-left { display:flex; align-items:center; gap:10px; }
.card-icon { font-size:15px; width:18px; text-align:center; }
.m-card-hd h3 { margin:0; font-size:14px; font-weight:600; color:#1e293b; letter-spacing:.2px; }
.chevron { font-size:11px; color:#94a3b8; transition:transform .25s ease; }
.chevron.open { transform:rotate(90deg); }
.m-card.collapsed .m-card-bd { display:none; }
.m-card-bd {
  padding:16px 18px; display:flex; flex-direction:column; align-items:center;
  border-top:1px solid #f1f5f9;
}

.accent-blue  { border-left-color:#3b82f6; }  .accent-blue  .card-icon { color:#3b82f6; }
.accent-green { border-left-color:#22c55e; }  .accent-green .card-icon { color:#22c55e; }

.fg { display:grid; grid-template-columns:auto 150px; column-gap:12px; row-gap:12px; align-items:center; width:fit-content; margin:0 auto; }
.fgr { display:contents; }
.fgr label { text-align:left; white-space:nowrap; font-size:13px; color:#475569; }
.fgr :deep(.el-input), .fgr :deep(.el-select) { width:100% !important; }
.rq { color:#ef4444; margin-right:2px; }

:deep(.env-group) { display:inline-flex; justify-content:center; margin:12px auto 8px; }
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

:deep(.btn-group) { display:flex; justify-content:center; gap:12px; margin:8px 0 10px; }

.result-box { width:100%; margin-top:4px; }
</style>
