<template>
  <div class="mo-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title"><i class="fa-solid fa-right-to-bracket"></i> 登录相关</h2>
      </div>
    </div>

    <div class="mo-body">
      <div class="column">
        <!-- 卡片1: 查询验证码 -->
        <div :class="['m-card', {collapsed:!cards.c1}]">
          <div class="m-card-hd accent-blue" @click="cards.c1=!cards.c1">
            <div class="m-card-hd-left"><i class="fa-solid fa-magnifying-glass card-icon"></i><h3>查询验证码</h3></div>
            <i :class="['fa-solid fa-chevron-right chevron', {open:cards.c1}]"></i>
          </div>
          <div class="m-card-bd">
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span>手机号码</label><el-input v-model="form1.tel" maxlength="11" placeholder="请输入手机号" /></div>
            </div>
            <EnvRadio v-model="form1.env" name="env1" />
            <BtnGroup @reset="reset1" @submit="queryCode" submit-text="查询" :loading="loading1" />
            <div class="note">注：查询10分钟以内的短信验证码。</div>
            <ResultBox :text="result1" :loading="loading1" />
          </div>
        </div>

        <!-- 卡片2: 设置销售/推荐官固定验证码 -->
        <div :class="['m-card', {collapsed:!cards.c2}]">
          <div class="m-card-hd accent-orange" @click="cards.c2=!cards.c2">
            <div class="m-card-hd-left"><i class="fa-solid fa-key card-icon"></i><h3>设置销售/推荐官固定验证码</h3></div>
            <i :class="['fa-solid fa-chevron-right chevron', {open:cards.c2}]"></i>
          </div>
          <div class="m-card-bd">
            <div class="fg">
              <div v-show="form2.role==='sale'" class="fgr"><label><span class="rq">*</span>企业ID</label><el-input v-model="form2.cid" placeholder="请输入企业ID" /></div>
              <div class="fgr"><label><span class="rq">*</span>手机号</label><el-input v-model="form2.tel" maxlength="11" placeholder="请输入手机号" /></div>
              <div class="fgr"><label><span class="rq">*</span>验证码</label><el-input v-model="form2.code" maxlength="4" placeholder="请输入4位验证码" /></div>
              <div class="fgr"><label>角色</label>
                <el-radio-group v-model="form2.role" size="small">
                  <el-radio value="sale">销售</el-radio>
                  <el-radio value="partner">推荐官</el-radio>
                </el-radio-group>
              </div>
            </div>
            <EnvRadio v-model="form2.env" name="env2" />
            <BtnGroup @reset="reset2" @submit="setCode" :loading="loading2" />
            <ResultBox :text="result2" :loading="loading2" />
          </div>
        </div>

        <!-- 卡片3: 小程序码 -->
        <div :class="['m-card', {collapsed:!cards.c3}]">
          <div class="m-card-hd accent-green" @click="cards.c3=!cards.c3">
            <div class="m-card-hd-left"><i class="fa-solid fa-qrcode card-icon"></i><h3>小程序码</h3></div>
            <i :class="['fa-solid fa-chevron-right chevron', {open:cards.c3}]"></i>
          </div>
          <div class="m-card-bd">
            <div class="thumb-grid">
              <el-image
                v-for="name in thumbNames"
                :key="name"
                :src="`/static/img/${name}.png`"
                :preview-src-list="[`/static/img/${name}.png`]"
                :preview-teleported="true"
                fit="contain"
                class="thumb-img"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const warn = (msg) => ElMessage({ message: msg, type: 'warning', duration: 2500 })

// --- Inline sub-components ---
const EnvRadio = {
  props: ['modelValue', 'name'], emits: ['update:modelValue'],
  template: `<div class="env-group"><div class="env-track"><label :class="{active:modelValue==='test'}"><i class="fa-solid fa-flask"></i><input type="radio" :name="name" value="test" :checked="modelValue==='test'" @change="$emit('update:modelValue','test')"/><span>测试环境</span></label><label :class="{active:modelValue==='prod'}"><i class="fa-solid fa-rocket"></i><input type="radio" :name="name" value="prod" :checked="modelValue==='prod'" @change="$emit('update:modelValue','prod')"/><span>生产环境</span></label></div></div>`,
}
const BtnGroup = {
  props: ['loading', 'submitText'],
  emits: ['reset', 'submit'],
  template: `<div class="btn-group"><el-button @click="$emit('reset')">重置</el-button><el-button type="primary" :loading="loading" @click="$emit('submit')">{{ submitText || '提交' }}</el-button></div>`,
}
const ResultBox = {
  props: ['text', 'loading'],
  template: `<div class="result"><span v-if="loading" class="result-loading"><i class="fa-solid fa-spinner fa-spin"></i> 加载中...</span><span v-else v-html="text||''"></span></div>`,
}

// --- 小程序码图片名 ---
const thumbNames = ['jdkf', 'jdcs', 'mdcszy', 'hxbd', 'dzhx', 'wfw666', 'jtmp', 'jtty', 'cjzsbys']

const cards = reactive({ c1: true, c2: true, c3: true })

const form1 = reactive({ tel: '', env: 'test' })
const form2 = reactive({ cid: '', tel: '', code: '', role: 'sale', env: 'prod' })
const result1 = ref('')
const result2 = ref('')
const loading1 = ref(false)
const loading2 = ref(false)

const isDigits = (s) => /^\d+$/.test(s)

async function queryCode() {
  if (!form1.tel) { result1.value = "'手机号码'不能为空! "; return }
  loading1.value = true
  try {
    const resp = await http.post('/sv/queryLoginCode', { tel: form1.tel, env: form1.env })
    result1.value = resp.data?.data || ''
  } catch (e) {
    result1.value = ''
    ElMessage.error('查询失败：' + (e?.response?.data?.msg || e.message))
  } finally { loading1.value = false }
}

async function setCode() {
  const { cid, tel, code, role, env } = form2
  let data
  if (role === 'sale') {
    if (!cid) { result2.value = '企业ID不能为空！'; return }
    if (cid.length < 18 || !isDigits(cid)) { result2.value = '企业ID为18位以上的纯数字！'; return }
    data = { cid, tel, code, role, env }
  } else {
    data = { tel, code, role, env }
  }
  if (!tel) { result2.value = '手机号不能为空！'; return }
  if (tel.length !== 11 || !isDigits(tel)) { result2.value = '手机号只能为11位纯数字！'; return }
  if (!code) { result2.value = '验证码不能为空！'; return }
  if (code.length !== 4 || !isDigits(code)) { result2.value = '验证码只能是4位纯数字！'; return }

  loading2.value = true
  try {
    const resp = await http.post('/sv/splc', data)
    result2.value = resp.data?.data || ''
  } catch (e) {
    result2.value = ''
    ElMessage.error('设置失败：' + (e?.response?.data?.msg || e.message))
  } finally { loading2.value = false }
}

function reset1() { form1.tel = ''; form1.env = 'test'; result1.value = '' }
function reset2() { form2.cid = ''; form2.tel = ''; form2.code = ''; form2.role = 'sale'; form2.env = 'prod'; result2.value = '' }

onMounted(() => {})
</script>

<style scoped>
/* ===================== 页面骨架 ===================== */
.mo-page { display:flex; flex-direction:column; height:100%; overflow:hidden; background:#f5f6fa; }
.toolbar { display:flex; justify-content:space-between; align-items:center; padding:12px 20px 8px; flex-shrink:0; }
.toolbar-left { display:flex; align-items:center; gap:8px; }
.page-title { margin:0; font-size:16px; font-weight:700; color:#1e293b; letter-spacing:.3px; }
.page-title i { color:#6366f1; margin-right:4px; }

.mo-body { flex:1; padding:0 14px 14px; overflow-y:auto; }
.mo-body::-webkit-scrollbar { width:4px; }
.mo-body::-webkit-scrollbar-track { background:transparent; }
.mo-body::-webkit-scrollbar-thumb { background:#cbd5e1; border-radius:4px; }
.mo-body::-webkit-scrollbar-thumb:hover { background:#94a3b8; }
.column { columns:2; column-gap:12px; }

/* ===================== 卡片 ===================== */
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
.accent-orange{ border-left-color:#f59e0b; }  .accent-orange .card-icon { color:#f59e0b; }

/* ===================== 表单 Grid ===================== */
.fg { display:grid; grid-template-columns:auto 150px; column-gap:12px; row-gap:12px; align-items:center; width:fit-content; margin:0 auto; }
.fgr { display:contents; }
.fgr label { text-align:left; white-space:nowrap; font-size:13px; color:#475569; }
.fgr :deep(.el-input), .fgr :deep(.el-select) { width:100% !important; }
.rq { color:#ef4444; margin-right:2px; }

/* ===================== 环境切换 ===================== */
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

/* ===================== 按钮 ===================== */
:deep(.btn-group) { display:flex; justify-content:center; gap:12px; margin:10px 0 12px; }

/* ===================== 结果区 ===================== */
.result {
  width:100%; min-height:32px; max-height:160px; overflow-y:auto;
  padding:10px 14px; border-radius:8px; background:#f8fafc;
  font-size:13px; text-align:center; line-height:1.7; color:#475569;
  word-wrap:break-word; word-break:break-all; white-space:pre-wrap;
}
.result:empty { display:none; }
.result-loading { color:#6366f1; font-weight:500; }
.result-loading i { margin-right:4px; }

/* ===================== 杂项 ===================== */
.note { color:#94a3b8; font-size:12px; margin-bottom:8px; text-align:center; }
.thumb-grid { display:flex; flex-wrap:wrap; gap:10px; justify-content:center; }
.thumb-img { width:120px; height:120px; border-radius:8px; cursor:pointer; }
</style>
