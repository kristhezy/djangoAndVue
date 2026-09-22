<template>
  <div class="mo-page">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title"><i class="fa-solid fa-fish"></i> 通威版配置</h2>
      </div>
    </div>

    <div class="mo-body">
      <!-- 第一列 -->
      <div class="column">
        <!-- 卡片1: 通威版企业开户 -->
        <div :class="['m-card', {collapsed:!cards.oa}]">
          <div class="m-card-hd accent-blue" @click="cards.oa=!cards.oa">
            <div class="m-card-hd-left">
              <i class="fa-solid fa-building card-icon"></i>
              <h3>通威版企业开户</h3>
            </div>
            <i :class="['fa-solid fa-chevron-right chevron', {open:cards.oa}]"></i>
          </div>
          <div class="m-card-bd">
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span>企业名称</label><el-input v-model="oa.compName" placeholder="输入企业全称" /></div>
              <div class="fgr"><label>企业简称</label><el-input v-model="oa.compShortName" placeholder="输入企业简称" /></div>
              <div class="fgr"><label><span class="rq">*</span>管理员名称</label><el-input v-model="oa.adminName" placeholder="输入管理员名称" /></div>
              <div class="fgr"><label><span class="rq">*</span>登录手机号</label><el-input v-model="oa.loginPhone" placeholder="输入手机号" /></div>
              <div class="fgr"><label><span class="rq">*</span>企业账号数</label><el-input v-model="oa.maxTotalAccount" placeholder="输入账号数" /></div>
              <div class="fgr"><label><span class="rq">*</span>企业有效期</label><el-date-picker v-model="oa.expireTime" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" /></div>
              <div class="fgr"><label>名片模板</label>
                <el-select v-model="oa.templateNo"><el-option label="默认" value="" /><el-option label="中电四公司" value="9" /></el-select>
              </div>
            </div>
            <EnvRadio v-model="oa.env" name="env" />
            <BtnGroup @reset="resetOa" @submit="submitOa" />
            <ResultBox :text="oa.result" :loading="oa.loading" />
          </div>
        </div>
      </div>

      <!-- 第二列 -->
      <div class="column">
        <!-- 卡片3: 通威版企业信息配置记录 -->
        <div :class="['m-card', {collapsed:!cards.uci}]">
          <div class="m-card-hd accent-green" @click="cards.uci=!cards.uci">
            <div class="m-card-hd-left">
              <i class="fa-solid fa-sliders card-icon"></i>
              <h3>通威版企业信息配置记录</h3>
            </div>
            <i :class="['fa-solid fa-chevron-right chevron', {open:cards.uci}]"></i>
          </div>
          <div class="m-card-bd">
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span>企业ID</label><el-input v-model="uci.compId" /></div>
              <div class="fgr"><label>销售席位</label><el-input v-model="uci.maxTotAcc" /></div>
              <div class="fgr"><label>有效日期</label><el-date-picker v-model="uci.expireTime" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" /></div>
              <div class="fgr"><label>企业状态</label>
                <el-select v-model="uci.compStatus"><el-option label="请选择" value="" /><el-option label="正常" value="1" /><el-option label="禁用" value="0" /><el-option label="注销" value="2" /></el-select>
              </div>
            </div>
            <EnvRadio v-model="uci.env" name="env3" />
            <BtnGroup @reset="resetUci" @submit="submitUci" />
            <ResultBox :text="uci.result" :loading="uci.loading" />
          </div>
        </div>
      </div>

      <!-- 第三列 -->
      <div class="column">
        <!-- 卡片2: 通威版企业绑定小程序 -->
        <div :class="['m-card', {collapsed:!cards.wx}]">
          <div class="m-card-hd accent-orange" @click="cards.wx=!cards.wx">
            <div class="m-card-hd-left">
              <i class="fa-solid fa-link card-icon"></i>
              <h3>通威版企业绑定小程序</h3>
            </div>
            <i :class="['fa-solid fa-chevron-right chevron', {open:cards.wx}]"></i>
          </div>
          <div class="m-card-bd">
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span>企业ID</label><el-input v-model="wx.compId" /></div>
              <div class="fgr"><label><span class="rq">*</span>APP ID</label><el-input v-model="wx.appId" /></div>
              <div class="fgr"><label><span class="rq">*</span>Secret</label><el-input v-model="wx.appSecret" /></div>
            </div>
            <EnvRadio v-model="wx.env" name="env2" />
            <BtnGroup @reset="resetWx" @submit="submitWx" />
            <ResultBox :text="wx.result" :loading="wx.loading" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http.js'

const warn = (msg) => ElMessage({ message: msg, type: 'warning', duration: 2500 })

// --- Inline sub-components ---
const EnvRadio = {
  props: ['modelValue','name','default'],
  emits:['update:modelValue'],
  mounted() { if (this.default && !this.modelValue) this.$emit('update:modelValue', this.default) },
  template:`<div class="env-group"><div class="env-track"><label :class="{active:modelValue==='test'}"><i class="fa-solid fa-flask"></i><input type="radio" :name="name" value="test" :checked="modelValue==='test'" @change="$emit('update:modelValue','test')"/><span>测试环境</span></label><label :class="{active:modelValue==='prod'}"><i class="fa-solid fa-rocket"></i><input type="radio" :name="name" value="prod" :checked="modelValue==='prod'" @change="$emit('update:modelValue','prod')"/><span>生产环境</span></label></div></div>`,
}
const BtnGroup = { emits:['reset','submit'], template:`<div class="btn-group"><el-button @click="$emit('reset')">重置</el-button><el-button type="primary" @click="$emit('submit')">提交</el-button></div>` }
const ResultBox = { props:['text','loading'], template:`<div class="result"><span v-if="loading" class="result-loading"><i class="fa-solid fa-spinner fa-spin"></i> 加载中...</span><span v-else v-html="text||''"></span></div>` }

const cards = reactive({ oa:true, wx:true, uci:true })

// ====== Card 1: 通威版企业开户 ======
const oa = reactive({ compName:'', compShortName:'', adminName:'', loginPhone:'', maxTotalAccount:'', expireTime:'', templateNo:'', env:'prod', result:'', loading:false })
function resetOa() { Object.assign(oa, { compName:'', compShortName:'', adminName:'', loginPhone:'', maxTotalAccount:'', expireTime:'', templateNo:'', env:'prod', result:'' }) }
function submitOa() {
  if (!oa.compName || !oa.adminName || !oa.loginPhone) { warn('必填项不能为空！'); return }
  oa.loading = true; oa.result = ''
  http.post('/ov/twCompSet', { cname:oa.compName, csname:oa.compShortName, aname:oa.adminName, lp:oa.loginPhone, mta:oa.maxTotalAccount, etime:oa.expireTime, templateNo:oa.templateNo, env:oa.env, version:6, type:'twopenaccount' })
    .then(r => { oa.result = r.data?.data || '' }).catch(() => { oa.result = '请求失败' }).finally(() => { oa.loading = false })
}

// ====== Card 2: 通威版企业绑定小程序 ======
const wx = reactive({ compId:'', appId:'', appSecret:'', env:'prod', result:'', loading:false })
function resetWx() { Object.assign(wx, { compId:'', appId:'', appSecret:'', env:'prod', result:'' }) }
function submitWx() {
  if (!wx.compId || !wx.appId || !wx.appSecret) { warn('必填项不能为空！'); return }
  wx.loading = true; wx.result = ''
  http.post('/ov/twCompSet', { cid:wx.compId, appid:wx.appId, secret:wx.appSecret, env:wx.env, type:'twbindapplet' })
    .then(r => { wx.result = r.data?.data || '' }).catch(() => { wx.result = '请求失败' }).finally(() => { wx.loading = false })
}

// ====== Card 3: 通威版企业信息配置记录 ======
const uci = reactive({ compId:'', maxTotAcc:'', expireTime:'', compStatus:'', env:'prod', result:'', loading:false })
function resetUci() { Object.assign(uci, { compId:'', maxTotAcc:'', expireTime:'', compStatus:'', env:'prod', result:'' }) }
function submitUci() {
  if (!uci.compId) { warn('企业ID不能为空！'); return }
  if (!uci.maxTotAcc && !uci.expireTime && !uci.compStatus) { warn('配置项至少填写一项！'); return }
  uci.loading = true; uci.result = ''
  http.post('/ov/twCompSet', { cid:uci.compId, mta:uci.maxTotAcc, etime:uci.expireTime, cs:uci.compStatus, env:uci.env, version:6, type:'twsetrecord' })
    .then(r => { uci.result = r.data?.data || '' }).catch(() => { uci.result = '请求失败' }).finally(() => { uci.loading = false })
}

onMounted(() => {})
</script>

<style scoped>
/* ===================== 页面骨架 ===================== */
.mo-page { display:flex; flex-direction:column; height:100%; overflow:hidden; background:var(--bg-page); }

.toolbar {
  display:flex; justify-content:space-between; align-items:center;
  padding:12px 20px 8px; flex-shrink:0;
}
.toolbar-left { display:flex; align-items:center; gap:8px; }
.page-title { margin:0; font-size:16px; font-weight:700; color:var(--text-primary); letter-spacing:.3px; }
.page-title i { color:var(--color-primary-light); margin-right:4px; }

.mo-body { display:flex; gap:12px; padding:0 12px 12px; flex:1; overflow:hidden;
  min-height: 0;; }
.mo-body::-webkit-scrollbar { width:4px; }
.mo-body::-webkit-scrollbar-track { background:transparent; }
.mo-body::-webkit-scrollbar-thumb { background:var(--scrollbar-thumb); border-radius:4px; }
.mo-body::-webkit-scrollbar-thumb:hover { background:var(--scrollbar-thumb-hover); }
.column { display:flex; flex-direction:column; gap:12px; flex:1; min-width:260px; overflow-y:auto; height:100%; padding:2px; }
.column::-webkit-scrollbar { width:4px; }
.column::-webkit-scrollbar-track { background:transparent; }
.column::-webkit-scrollbar-thumb { background:var(--scrollbar-thumb); border-radius:4px; }
.column::-webkit-scrollbar-thumb:hover { background:var(--scrollbar-thumb-hover); }

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
.fg { display:grid; grid-template-columns: auto minmax(120px, 300px); column-gap:12px; row-gap:12px; align-items:center; width:fit-content; margin:0 auto; }
.fgr { display:contents; }
.fgr label { text-align:left; white-space:nowrap; font-size:13px; color:var(--text-secondary); }
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
  width:100%; min-height:32px; max-height:160px; overflow-y:auto;
  padding:10px 14px; border-radius:8px; background:var(--bg-subtle);
  font-size:13px; text-align:center; line-height:1.7; color:var(--text-secondary);
  word-wrap:break-word; word-break:break-all; white-space:pre-wrap;
}
.result:empty { display:none; }
.result-loading { color:var(--color-primary-light); font-weight:500; }
.result-loading i { margin-right:4px; }
</style>
