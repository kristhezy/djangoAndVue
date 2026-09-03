<template>
  <div class="st-page">
    <div class="st-body">
      <!-- 卡片1: 基线版企业开户 -->
      <div class="card">
        <div class="card-title"><h1>基线版企业开户</h1></div>
        <div class="fg">
          <div class="fgr">
            <label>私有域名:</label>
            <el-select v-model="oa.privaddr" :disabled="oa.env==='test'" style="width:180px">
              <el-option label="请选择" value="" />
              <el-option label="中交四航院" value="https://47.92.151.128:443" />
            </el-select>
          </div>
          <div class="fgr"><label><span class="rq">*</span>企业名称:</label><el-input v-model="oa.compName" placeholder="输入企业全称" /></div>
          <div class="fgr"><label><span class="rq">*</span>登录账号:</label><el-input v-model="oa.loginName" placeholder="输入手机号" /></div>
          <div class="fgr"><label>销售席位:</label><el-input v-model="oa.maxTotAcc" type="number" placeholder="输入销售席位数" /></div>
          <div class="fgr"><label><span class="rq">*</span>语言类型:</label>
            <el-select v-model="oa.langType" style="width:180px">
              <el-option label="中文（简体）" value="zh-CN" /><el-option label="English" value="en" />
            </el-select>
          </div>
          <div class="fgr"><label>有效日期:</label><el-date-picker v-model="oa.expireTime" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width:180px" /></div>
        </div>
        <EnvRadio v-model="oa.env" name="env1" />
        <BtnGroup @reset="resetOa" @submit="submitOa" />
        <ResultBox :text="oa.result" :loading="oa.loading" />
      </div>

      <!-- 卡片2: 基线版企业信息配置 -->
      <div class="card">
        <div class="card-title"><h1>基线版企业信息配置</h1></div>
        <div class="fg">
          <div class="fgr">
            <label>私有域名:</label>
            <el-select v-model="uci.privaddr" :disabled="uci.env==='test'" style="width:180px">
              <el-option label="请选择" value="" />
              <el-option label="中交四航院" value="https://47.92.151.128:443" />
            </el-select>
          </div>
          <div class="fgr"><label><span class="rq">*</span>企业ID:</label><el-input v-model="uci.compId" placeholder="输入后回车可查有效日期" @keydown.enter="getExpireDate" /></div>
          <div class="fgr"><label>销售席位:</label><el-input v-model="uci.maxTotAcc" type="number" placeholder="0为无限席位" /></div>
          <div class="fgr"><label>有效日期:</label>
            <div style="display:flex;align-items:center;width:180px">
              <el-date-picker v-model="uci.expireTime" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" :disabled="!uci.islong" style="width:155px" />
              <el-checkbox v-model="uci.islong" style="margin-left:8px" />
            </div>
          </div>
          <div class="fgr"><label>企业状态:</label>
            <el-select v-model="uci.compStatus" style="width:180px"><el-option label="请选择" value="" /><el-option label="正常" value="1" /><el-option label="禁用" value="0" /><el-option label="注销" value="2" /></el-select>
          </div>
          <div class="fgr"><label>AI名片:</label>
            <el-select v-model="uci.aiCard" style="width:180px"><el-option label="请选择" value="" /><el-option label="开启" value="1" /><el-option label="关闭" value="0" /></el-select>
          </div>
        </div>
        <EnvRadio v-model="uci.env" name="env3" />
        <BtnGroup @reset="resetUci" @submit="submitUci" />
        <ResultBox :text="uci.result" :loading="uci.loading" />
      </div>

      <!-- 卡片3: 基线版企业绑定小程序 -->
      <div class="card">
        <div class="card-title"><h1>基线版企业绑定小程序</h1></div>
        <div class="fg">
          <div class="fgr">
            <label>私有域名:</label>
            <el-select v-model="wx.privaddr" :disabled="wx.env==='test'" style="width:180px">
              <el-option label="请选择" value="" />
              <el-option label="中交四航院" value="https://47.92.151.128:443" />
            </el-select>
          </div>
          <div class="fgr"><label><span class="rq">*</span>企业ID:</label><el-input v-model="wx.compId" /></div>
          <div class="fgr"><label><span class="rq">*</span>APP ID:</label><el-input v-model="wx.appId" /></div>
          <div class="fgr"><label><span class="rq">*</span>Secret:</label><el-input v-model="wx.appSecret" /></div>
        </div>
        <EnvRadio v-model="wx.env" name="env2" />
        <BtnGroup @reset="resetWx" @submit="submitWx" />
        <ResultBox :text="wx.result" :loading="wx.loading" />
      </div>

      <!-- 卡片4: 修改企管角色密码 -->
      <div class="card">
        <div class="card-title"><h1>修改企管角色密码</h1></div>
        <div class="fg">
          <div class="fgr"><label><span class="rq">*</span>用户ID:</label><el-input v-model="pwd.userid" /></div>
          <div class="fgr"><label><span class="rq">*</span>密码:</label><el-input v-model="pwd.passwd" /></div>
        </div>
        <EnvRadio v-model="pwd.env" name="env4" />
        <BtnGroup @reset="resetPwd" @submit="submitPwd" />
        <ResultBox :text="pwd.result" :loading="pwd.loading" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import http from '../../api/http.js'

// --- Inline sub-components ---
const EnvRadio = {
  props: ['modelValue','name'], emits:['update:modelValue'],
  template:`<div class="env-group"><label :class="{active:modelValue==='test'}"><input type="radio" :name="name" value="test" :checked="modelValue==='test'" @change="$emit('update:modelValue','test')"/> 测试环境</label><label :class="{active:modelValue==='prod'}"><input type="radio" :name="name" value="prod" :checked="modelValue==='prod'" @change="$emit('update:modelValue','prod')"/> 生产环境</label></div>`,
}
const BtnGroup = { emits:['reset','submit'], template:`<div class="btn-group"><el-button @click="$emit('reset')">重置</el-button><el-button type="primary" @click="$emit('submit')">提交</el-button></div>` }
const ResultBox = { props:['text','loading'], template:`<div class="result"><span v-if="loading" style="color:#6366f1">加载中...</span><span v-else v-html="text||''"></span></div>` }

function defaultDate() {
  const d = new Date()
  d.setFullYear(d.getFullYear() + 1)
  d.setDate(d.getDate() + 1)
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
}

// ====== Card 1: 基线版企业开户 ======
const oa = reactive({ privaddr:'', compName:'', loginName:'', maxTotAcc:'', langType:'zh-CN', expireTime:defaultDate(), env:'test', result:'', loading:false })
function resetOa() { Object.assign(oa, { privaddr:'', compName:'', loginName:'', maxTotAcc:'', langType:'zh-CN', expireTime:defaultDate(), env:'test', result:'' }) }
function submitOa() {
  if (oa.privaddr && oa.env === 'test') { alert('私有化域名不可以调测试环境！'); return }
  if (!oa.compName || !oa.loginName) { alert('必填项不能为空！'); return }
  if (!oa.langType) { alert('选择语言种类！'); return }
  oa.loading = true; oa.result = ''
  http.post('/ov/setting/openaccount', { privaddr:oa.privaddr, cname:oa.compName, csname:'', mta:oa.maxTotAcc, phone:';', lname:oa.loginName, pwd:'Aa@123456', langType:oa.langType, etime:oa.expireTime, env:oa.env, version:3, type:'openaccount' })
    .then(r => { oa.result = r.data?.data || '' }).catch(() => { oa.result = '请求失败' }).finally(() => { oa.loading = false })
}

// ====== Card 2: 基线版企业信息配置 ======
const uci = reactive({ privaddr:'', compId:'', maxTotAcc:'', expireTime:defaultDate(), islong:false, compStatus:'', aiCard:'', env:'test', result:'', loading:false })
function resetUci() { Object.assign(uci, { privaddr:'', compId:'', maxTotAcc:'', expireTime:defaultDate(), islong:false, compStatus:'', aiCard:'', env:'test', result:'' }) }
function getExpireDate() {
  if (!uci.compId) { alert('输入"企业ID"查询!'); return }
  http.post('/ov/setting/getEDByCID', { compId:uci.compId, env:uci.env, type:'getEDByCID' })
    .then(r => { if (r.data?.data) uci.expireTime = r.data.data }).catch(() => {})
}
function submitUci() {
  if (!uci.compId) { alert('"企业ID"不能为空！'); return }
  if (!uci.maxTotAcc && !uci.compStatus && !uci.aiCard && !uci.islong) { alert('输入需要修改的内容！'); return }
  uci.loading = true; uci.result = ''
  http.post('/ov/setting/updcompinfo', { privaddr:uci.privaddr, compid:uci.compId, mta:uci.maxTotAcc, cs:uci.compStatus, aics:uci.aiCard, isl:uci.islong, expireTime:uci.islong ? uci.expireTime : '', env:uci.env, version:3, type:'updcompinfo' })
    .then(r => { uci.result = r.data?.data || '' }).catch(() => { uci.result = '请求失败' }).finally(() => { uci.loading = false })
}

// ====== Card 3: 基线版企业绑定小程序 ======
const wx = reactive({ privaddr:'', compId:'', appId:'', appSecret:'', env:'test', result:'', loading:false })
function resetWx() { Object.assign(wx, { privaddr:'', compId:'', appId:'', appSecret:'', env:'test', result:'' }) }
function submitWx() {
  if (!wx.compId || !wx.appId || !wx.appSecret) { alert('必填项不能为空！'); return }
  wx.loading = true; wx.result = ''
  http.post('/ov/setting/savewxappinfo', { privaddr:wx.privaddr, cid:wx.compId, appid:wx.appId, secret:wx.appSecret, env:wx.env, type:'savewxappinfo' })
    .then(r => { wx.result = r.data?.data || '' }).catch(() => { wx.result = '请求失败' }).finally(() => { wx.loading = false })
}

// ====== Card 4: 修改企管角色密码 ======
const pwd = reactive({ userid:'', passwd:'', env:'test', result:'', loading:false })
function resetPwd() { Object.assign(pwd, { userid:'', passwd:'', env:'test', result:'' }) }
function submitPwd() {
  if (!pwd.userid || !pwd.passwd) { alert('必填项不能为空！'); return }
  pwd.loading = true; pwd.result = ''
  http.post('/ov/setting/initpwd', { userid:pwd.userid, passwd:pwd.passwd, env:pwd.env, type:'initpwd' })
    .then(r => { pwd.result = r.data?.data || '' }).catch(() => { pwd.result = '请求失败' }).finally(() => { pwd.loading = false })
}
</script>

<style scoped>
.st-page { display:flex; flex-direction:column; height:100%; overflow:hidden; }
.st-body { display:flex; gap:16px; padding:10px 16px; height:100%; overflow-y:auto; }

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
