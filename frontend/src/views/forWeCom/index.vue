<template>
  <div class="mo-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title"><i class="fa-solid fa-building-shield"></i> 企微工具</h2>
      </div>
    </div>

    <div class="mo-body">
      <div class="mo-col">
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
      </div>

      <div class="mo-col">
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

      <div class="mo-col">
        <!-- 占位卡片: 预留功能区域 -->
        <div class="m-card">
          <div class="m-card-hd accent-orange">
            <div class="m-card-hd-left"><i class="fa-solid fa-puzzle-piece card-icon"></i><h3>预留功能区域</h3></div>
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
/* mo-page / mo-body / mo-col / m-card 等样式由 design-system.css 统一提供 */

.fg { display:grid; grid-template-columns:auto 300px; column-gap:12px; row-gap:12px; align-items:center; width:fit-content; margin:0 auto; }
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

.result-box { width:100%; margin-top:4px; }
.placeholder { display:flex; align-items:center; justify-content:center; width:100%; padding:24px 0; }
.placeholder p { color:var(--text-placeholder); text-align:center; }
</style>
