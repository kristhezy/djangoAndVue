<template>
  <div class="tw-page">
    <div class="tw-body">
      <!-- 卡片1: 通威版企业开户 -->
      <div class="card">
        <div class="card-title"><h1>通威版企业开户</h1></div>
        <div class="fg">
          <div class="fgr"><label><span class="rq">*</span>企业名称:</label><el-input v-model="oa.compName" placeholder="输入企业全称" /></div>
          <div class="fgr"><label>企业简称:</label><el-input v-model="oa.compShortName" placeholder="输入企业简称" /></div>
          <div class="fgr"><label><span class="rq">*</span>管理员名称:</label><el-input v-model="oa.adminName" placeholder="输入管理员名称" /></div>
          <div class="fgr"><label><span class="rq">*</span>登录手机号:</label><el-input v-model="oa.loginPhone" placeholder="输入手机号" /></div>
          <div class="fgr"><label><span class="rq">*</span>企业账号数:</label><el-input v-model="oa.maxTotalAccount" placeholder="输入账号数" /></div>
          <div class="fgr"><label><span class="rq">*</span>企业有效期:</label><el-date-picker v-model="oa.expireTime" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width:180px" /></div>
          <div class="fgr"><label>名片模板:</label>
            <el-select v-model="oa.templateNo" style="width:180px"><el-option label="默认" value="" /><el-option label="中电四公司" value="9" /></el-select>
          </div>
        </div>
        <EnvRadio v-model="oa.env" name="env" :default="'prod'" />
        <BtnGroup @reset="resetOa" @submit="submitOa" />
        <ResultBox :text="oa.result" :loading="oa.loading" />
      </div>

      <!-- 卡片2: 通威版企业绑定小程序 -->
      <div class="card">
        <div class="card-title"><h1>通威版企业绑定小程序</h1></div>
        <div class="fg">
          <div class="fgr"><label><span class="rq">*</span>企业ID:</label><el-input v-model="wx.compId" /></div>
          <div class="fgr"><label><span class="rq">*</span>APP ID:</label><el-input v-model="wx.appId" /></div>
          <div class="fgr"><label><span class="rq">*</span>Secret:</label><el-input v-model="wx.appSecret" /></div>
        </div>
        <EnvRadio v-model="wx.env" name="env2" :default="'prod'" />
        <BtnGroup @reset="resetWx" @submit="submitWx" />
        <ResultBox :text="wx.result" :loading="wx.loading" />
      </div>

      <!-- 卡片3: 通威版企业信息配置记录 -->
      <div class="card">
        <div class="card-title"><h1>通威版企业信息配置记录</h1></div>
        <div class="fg">
          <div class="fgr"><label><span class="rq">*</span>企业ID:</label><el-input v-model="uci.compId" /></div>
          <div class="fgr"><label>销售席位:</label><el-input v-model="uci.maxTotAcc" /></div>
          <div class="fgr"><label>有效日期:</label><el-date-picker v-model="uci.expireTime" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width:180px" /></div>
          <div class="fgr"><label>企业状态:</label>
            <el-select v-model="uci.compStatus" style="width:180px"><el-option label="请选择" value="" /><el-option label="正常" value="1" /><el-option label="禁用" value="0" /><el-option label="注销" value="2" /></el-select>
          </div>
        </div>
        <EnvRadio v-model="uci.env" name="env3" :default="'prod'" />
        <BtnGroup @reset="resetUci" @submit="submitUci" />
        <ResultBox :text="uci.result" :loading="uci.loading" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import http from '../../api/http.js'

// --- Inline sub-components ---
const EnvRadio = {
  props: ['modelValue','name','default'],
  emits:['update:modelValue'],
  mounted() { if (this.default && !this.modelValue) this.$emit('update:modelValue', this.default) },
  template:`<div class="env-group"><label :class="{active:modelValue==='test'}"><input type="radio" :name="name" value="test" :checked="modelValue==='test'" @change="$emit('update:modelValue','test')"/> 测试环境</label><label :class="{active:modelValue==='prod'}"><input type="radio" :name="name" value="prod" :checked="modelValue==='prod'" @change="$emit('update:modelValue','prod')"/> 生产环境</label></div>`,
}
const BtnGroup = { emits:['reset','submit'], template:`<div class="btn-group"><el-button @click="$emit('reset')">重置</el-button><el-button type="primary" @click="$emit('submit')">提交</el-button></div>` }
const ResultBox = { props:['text','loading'], template:`<div class="result"><span v-if="loading" style="color:#6366f1">加载中...</span><span v-else v-html="text||''"></span></div>` }

// ====== Card 1: 通威版企业开户 ======
const oa = reactive({ compName:'', compShortName:'', adminName:'', loginPhone:'', maxTotalAccount:'', expireTime:'', templateNo:'', env:'prod', result:'', loading:false })
function resetOa() { Object.assign(oa, { compName:'', compShortName:'', adminName:'', loginPhone:'', maxTotalAccount:'', expireTime:'', templateNo:'', env:'prod', result:'' }) }
function submitOa() {
  if (!oa.compName || !oa.adminName || !oa.loginPhone) { alert('必填项不能为空！'); return }
  oa.loading = true; oa.result = ''
  http.post('/ov/twCompSet', { cname:oa.compName, csname:oa.compShortName, aname:oa.adminName, lp:oa.loginPhone, mta:oa.maxTotalAccount, etime:oa.expireTime, templateNo:oa.templateNo, env:oa.env, version:6, type:'twopenaccount' })
    .then(r => { oa.result = r.data?.data || '' }).catch(() => { oa.result = '请求失败' }).finally(() => { oa.loading = false })
}

// ====== Card 2: 通威版企业绑定小程序 ======
const wx = reactive({ compId:'', appId:'', appSecret:'', env:'prod', result:'', loading:false })
function resetWx() { Object.assign(wx, { compId:'', appId:'', appSecret:'', env:'prod', result:'' }) }
function submitWx() {
  if (!wx.compId || !wx.appId || !wx.appSecret) { alert('必填项不能为空！'); return }
  wx.loading = true; wx.result = ''
  http.post('/ov/twCompSet', { cid:wx.compId, appid:wx.appId, secret:wx.appSecret, env:wx.env, type:'twbindapplet' })
    .then(r => { wx.result = r.data?.data || '' }).catch(() => { wx.result = '请求失败' }).finally(() => { wx.loading = false })
}

// ====== Card 3: 通威版企业信息配置记录 ======
const uci = reactive({ compId:'', maxTotAcc:'', expireTime:'', compStatus:'', env:'prod', result:'', loading:false })
function resetUci() { Object.assign(uci, { compId:'', maxTotAcc:'', expireTime:'', compStatus:'', env:'prod', result:'' }) }
function submitUci() {
  if (!uci.compId) { alert('企业ID不能为空！'); return }
  if (!uci.maxTotAcc && !uci.expireTime && !uci.compStatus) { alert('配置项至少填写一项！'); return }
  uci.loading = true; uci.result = ''
  http.post('/ov/twCompSet', { cid:uci.compId, mta:uci.maxTotAcc, etime:uci.expireTime, cs:uci.compStatus, env:uci.env, version:6, type:'twsetrecord' })
    .then(r => { uci.result = r.data?.data || '' }).catch(() => { uci.result = '请求失败' }).finally(() => { uci.loading = false })
}
</script>

<style scoped>
.tw-page { display:flex; flex-direction:column; height:100%; overflow:hidden; }
.tw-body { display:flex; gap:16px; padding:10px 16px; height:100%; overflow-y:auto; }

.card { flex:1; background:#fff; border:1px solid #f3f4f6; border-radius:16px; padding:10px 20px; display:flex; flex-direction:column; align-items:center; box-shadow:0 4px 6px -1px rgba(0,0,0,.1),0 2px 4px -2px rgba(0,0,0,.1); min-width:260px; }
.card-title { text-align:center; margin-bottom:20px; padding-bottom:10px; border-bottom:2px solid #f0f0f0; width:100%; }
.card-title h1 { margin:0; font-size:20px; font-weight:600; color:#333; }

.fg { display:grid; grid-template-columns:max-content 180px; column-gap:8px; row-gap:8px; align-items:center; }
.fgr { display:contents; }
.fgr label { text-align:right; white-space:nowrap; }
.rq { color:red; }

:deep(.env-group) { display:flex; justify-content:center; gap:20px; margin:15px 0; }
:deep(.env-group label) { cursor:pointer; display:inline-flex; align-items:center; gap:4px; padding:5px 16px; border-radius:9999px; border:1px solid #d1d5db; background:#fff; font-size:13px; transition:all .15s; user-select:none; }
:deep(.env-group label.active) { background:#6366f1; color:#fff; border-color:#6366f1; }
:deep(.env-group input[type="radio"]) { display:none; }

:deep(.btn-group) { display:flex; justify-content:center; gap:15px; margin-bottom:15px; }
.result { flex:1; margin-top:10px; padding:10px; border-radius:8px; overflow-y:auto; font-size:15px; text-align:center; width:100%; word-wrap:break-word; word-break:break-all; white-space:pre-wrap; }
</style>
