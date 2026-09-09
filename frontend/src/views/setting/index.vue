<template>
  <div class="mo-page">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title"><i class="fa-solid fa-gear"></i> Setting 基线版配置</h2>
      </div>
    </div>

    <div class="mo-body">
      <!-- 第一列 -->
      <div class="column">
        <!-- 卡片1: 基线版企业开户 -->
        <div :class="['m-card', { collapsed: !cards.oa }]">
          <div class="m-card-hd accent-blue" @click="cards.oa = !cards.oa">
            <div class="m-card-hd-left">
              <i class="fa-solid fa-building card-icon"></i>
              <h3>基线版企业开户</h3>
            </div>
            <i :class="['fa-solid fa-chevron-right chevron', { open: cards.oa }]"></i>
          </div>
          <div class="m-card-bd">
            <div class="fg">
              <div class="fgr">
                <label>私有域名</label>
                <el-select v-model="oa.privaddr" :disabled="oa.env === 'test'">
                  <el-option label="请选择" value="" />
                  <el-option label="中交四航院" value="https://47.92.151.128:443" />
                </el-select>
              </div>
              <div class="fgr"><label><span class="rq">*</span>企业名称</label><el-input v-model="oa.compName"
                  placeholder="输入企业全称" /></div>
              <div class="fgr"><label><span class="rq">*</span>登录账号</label><el-input v-model="oa.loginName"
                  placeholder="输入手机号" /></div>
              <div class="fgr"><label>销售席位</label><el-input v-model="oa.maxTotAcc" type="number"
                  placeholder="输入销售席位数" /></div>
              <div class="fgr"><label><span class="rq">*</span>语言类型</label>
                <el-select v-model="oa.langType">
                  <el-option label="中文（简体）" value="zh-CN" /><el-option label="English" value="en" />
                </el-select>
              </div>
              <div class="fgr"><label>有效日期</label><el-date-picker v-model="oa.expireTime" type="date"
                  format="YYYY-MM-DD" value-format="YYYY-MM-DD" /></div>
            </div>
            <EnvRadio v-model="oa.env" name="env1" />
            <BtnGroup @reset="resetOa" @submit="submitOa" />
            <ResultBox :text="oa.result" :loading="oa.loading" />
          </div>
        </div>

        <!-- 卡片4: 修改企管角色密码 -->
        <div :class="['m-card', { collapsed: !cards.pwd }]">
          <div class="m-card-hd accent-red" @click="cards.pwd = !cards.pwd">
            <div class="m-card-hd-left">
              <i class="fa-solid fa-key card-icon"></i>
              <h3>修改企管角色密码</h3>
            </div>
            <i :class="['fa-solid fa-chevron-right chevron', { open: cards.pwd }]"></i>
          </div>
          <div class="m-card-bd">
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span>用户ID</label><el-input v-model="pwd.userid" /></div>
              <div class="fgr"><label><span class="rq">*</span>密码</label><el-input v-model="pwd.passwd" /></div>
            </div>
            <EnvRadio v-model="pwd.env" name="env4" />
            <BtnGroup @reset="resetPwd" @submit="submitPwd" />
            <ResultBox :text="pwd.result" :loading="pwd.loading" />
          </div>
        </div>
      </div>

      <!-- 第二列 -->
      <div class="column">
        <!-- 卡片2: 基线版企业信息配置 -->
        <div :class="['m-card', { collapsed: !cards.uci }]">
          <div class="m-card-hd accent-green" @click="cards.uci = !cards.uci">
            <div class="m-card-hd-left">
              <i class="fa-solid fa-sliders card-icon"></i>
              <h3>基线版企业信息配置</h3>
            </div>
            <i :class="['fa-solid fa-chevron-right chevron', { open: cards.uci }]"></i>
          </div>
          <div class="m-card-bd">
            <div class="fg">
              <div class="fgr">
                <label>私有域名</label>
                <el-select v-model="uci.privaddr" :disabled="uci.env === 'test'">
                  <el-option label="请选择" value="" />
                  <el-option label="中交四航院" value="https://47.92.151.128:443" />
                </el-select>
              </div>
              <div class="fgr"><label><span class="rq">*</span>企业ID</label><el-input v-model="uci.compId"
                  placeholder="输入后回车可查有效日期" @keydown.enter="getExpireDate" /></div>
              <div class="fgr"><label>销售席位</label><el-input v-model="uci.maxTotAcc" type="number"
                  placeholder="0为无限席位" /></div>
              <div class="fgr"><label>有效日期</label>
                <div style="display:flex;align-items:center;width:250px">
                  <el-date-picker v-model="uci.expireTime" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD"
                    :disabled="!uci.islong" style="width:225px" />
                  <el-checkbox v-model="uci.islong" style="margin-left:8px" />
                </div>
              </div>
              <div class="fgr"><label>企业状态</label>
                <el-select v-model="uci.compStatus"><el-option label="请选择" value="" /><el-option label="正常"
                    value="1" /><el-option label="禁用" value="0" /><el-option label="注销" value="2" /></el-select>
              </div>
              <div class="fgr"><label>AI名片</label>
                <el-select v-model="uci.aiCard"><el-option label="请选择" value="" /><el-option label="开启"
                    value="1" /><el-option label="关闭" value="0" /></el-select>
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
        <!-- 卡片3: 基线版企业绑定小程序 -->
        <div :class="['m-card', { collapsed: !cards.wx }]">
          <div class="m-card-hd accent-orange" @click="cards.wx = !cards.wx">
            <div class="m-card-hd-left">
              <i class="fa-solid fa-link card-icon"></i>
              <h3>基线版企业绑定小程序</h3>
            </div>
            <i :class="['fa-solid fa-chevron-right chevron', { open: cards.wx }]"></i>
          </div>
          <div class="m-card-bd">
            <div class="fg">
              <div class="fgr">
                <label>私有域名</label>
                <el-select v-model="wx.privaddr" :disabled="wx.env === 'test'">
                  <el-option label="请选择" value="" />
                  <el-option label="中交四航院" value="https://47.92.151.128:443" />
                </el-select>
              </div>
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
  props: ['modelValue', 'name'], emits: ['update:modelValue'],
  template: `<div class="env-group"><div class="env-track"><label :class="{active:modelValue==='test'}"><i class="fa-solid fa-flask"></i><input type="radio" :name="name" value="test" :checked="modelValue==='test'" @change="$emit('update:modelValue','test')"/><span>测试环境</span></label><label :class="{active:modelValue==='prod'}"><i class="fa-solid fa-rocket"></i><input type="radio" :name="name" value="prod" :checked="modelValue==='prod'" @change="$emit('update:modelValue','prod')"/><span>生产环境</span></label></div></div>`,
}
const BtnGroup = { emits: ['reset', 'submit'], template: `<div class="btn-group"><el-button @click="$emit('reset')">重置</el-button><el-button type="primary" @click="$emit('submit')">提交</el-button></div>` }
const ResultBox = { props: ['text', 'loading'], template: `<div class="result"><span v-if="loading" class="result-loading"><i class="fa-solid fa-spinner fa-spin"></i> 加载中...</span><span v-else v-html="text||''"></span></div>` }

function defaultDate() {
  const d = new Date()
  d.setFullYear(d.getFullYear() + 1)
  d.setDate(d.getDate())
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

const cards = reactive({ oa: true, uci: true, wx: true, pwd: true })

// ====== Card 1: 基线版企业开户 ======
const oa = reactive({ privaddr: '', compName: '', loginName: '', maxTotAcc: '', langType: 'zh-CN', expireTime: defaultDate(), env: 'test', result: '', loading: false })
function resetOa() { Object.assign(oa, { privaddr: '', compName: '', loginName: '', maxTotAcc: '', langType: 'zh-CN', expireTime: defaultDate(), env: 'test', result: '' }) }
function submitOa() {
  if (oa.privaddr && oa.env === 'test') { warn('私有化域名不可以调测试环境！'); return }
  if (!oa.compName || !oa.loginName) { warn('必填项不能为空！'); return }
  if (!oa.langType) { warn('选择语言种类！'); return }
  oa.loading = true; oa.result = ''
  http.post('/ov/setting/openaccount', { privaddr: oa.privaddr, cname: oa.compName, csname: '', mta: oa.maxTotAcc, phone: ';', lname: oa.loginName, pwd: 'Aa@123456', langType: oa.langType, etime: oa.expireTime, env: oa.env, version: 3, type: 'openaccount' })
    .then(r => { oa.result = r.data?.data || '' }).catch(() => { oa.result = '请求失败' }).finally(() => { oa.loading = false })
}

// ====== Card 2: 基线版企业信息配置 ======
const uci = reactive({ privaddr: '', compId: '', maxTotAcc: '', expireTime: defaultDate(), islong: false, compStatus: '', aiCard: '', env: 'test', result: '', loading: false })
function resetUci() { Object.assign(uci, { privaddr: '', compId: '', maxTotAcc: '', expireTime: defaultDate(), islong: false, compStatus: '', aiCard: '', env: 'test', result: '' }) }
function getExpireDate() {
  if (!uci.compId) { warn('输入"企业ID"查询!'); return }
  http.post('/ov/setting/getEDByCID', { compId: uci.compId, env: uci.env, type: 'getEDByCID' })
    .then(r => { if (r.data?.data) uci.expireTime = r.data.data }).catch(() => { })
}
function submitUci() {
  if (!uci.compId) { warn('"企业ID"不能为空！'); return }
  if (!uci.maxTotAcc && !uci.compStatus && !uci.aiCard && !uci.islong) { warn('输入需要修改的内容！'); return }
  uci.loading = true; uci.result = ''
  http.post('/ov/setting/updcompinfo', { privaddr: uci.privaddr, compid: uci.compId, mta: uci.maxTotAcc, cs: uci.compStatus, aics: uci.aiCard, isl: uci.islong, expireTime: uci.islong ? uci.expireTime : '', env: uci.env, version: 3, type: 'updcompinfo' })
    .then(r => { uci.result = r.data?.data || '' }).catch(() => { uci.result = '请求失败' }).finally(() => { uci.loading = false })
}

// ====== Card 3: 基线版企业绑定小程序 ======
const wx = reactive({ privaddr: '', compId: '', appId: '', appSecret: '', env: 'test', result: '', loading: false })
function resetWx() { Object.assign(wx, { privaddr: '', compId: '', appId: '', appSecret: '', env: 'test', result: '' }) }
function submitWx() {
  if (!wx.compId || !wx.appId || !wx.appSecret) { warn('必填项不能为空！'); return }
  wx.loading = true; wx.result = ''
  http.post('/ov/setting/savewxappinfo', { privaddr: wx.privaddr, cid: wx.compId, appid: wx.appId, secret: wx.appSecret, env: wx.env, type: 'savewxappinfo' })
    .then(r => { wx.result = r.data?.data || '' }).catch(() => { wx.result = '请求失败' }).finally(() => { wx.loading = false })
}

// ====== Card 4: 修改企管角色密码 ======
const pwd = reactive({ userid: '', passwd: '', env: 'test', result: '', loading: false })
function resetPwd() { Object.assign(pwd, { userid: '', passwd: '', env: 'test', result: '' }) }
function submitPwd() {
  if (!pwd.userid || !pwd.passwd) { warn('必填项不能为空！'); return }
  pwd.loading = true; pwd.result = ''
  http.post('/ov/setting/initpwd', { userid: pwd.userid, passwd: pwd.passwd, env: pwd.env, type: 'initpwd' })
    .then(r => { pwd.result = r.data?.data || '' }).catch(() => { pwd.result = '请求失败' }).finally(() => { pwd.loading = false })
}

onMounted(() => { })
</script>

<style scoped>
/* ===================== 页面骨架 ===================== */
.mo-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background: #f5f6fa;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px 8px;
  flex-shrink: 0;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-title {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
  letter-spacing: .3px;
}

.page-title i {
  color: #6366f1;
  margin-right: 4px;
}

.mo-body {
  display: flex;
  gap: 12px;
  padding: 0 12px 12px;
  flex: 1;
  overflow: hidden;
}

.column {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
  min-width: 260px;
  overflow-y: auto;
  height: 100%;
  padding: 2px;
}

.column::-webkit-scrollbar {
  width: 4px;
}

.column::-webkit-scrollbar-track {
  background: transparent;
}

.column::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.column::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* ===================== 卡片 ===================== */
.m-card {
  background: #fff;
  border-radius: 12px;
  flex-shrink: 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, .06), 0 1px 2px rgba(0, 0, 0, .04);
  overflow: hidden;
  transition: box-shadow .2s;
}

.m-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, .08), 0 2px 4px rgba(0, 0, 0, .04);
}

/* 卡片头 */
.m-card-hd {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  cursor: pointer;
  user-select: none;
  border-left: 4px solid transparent;
  transition: background .15s;
}

.m-card-hd:hover {
  background: #fafbfc;
}

.m-card-hd-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-icon {
  font-size: 15px;
  width: 18px;
  text-align: center;
}

.m-card-hd h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  letter-spacing: .2px;
}

/* 折叠箭头 */
.chevron {
  font-size: 11px;
  color: #94a3b8;
  transition: transform .25s ease;
}

.chevron.open {
  transform: rotate(90deg);
}

/* 折叠状态 */
.m-card.collapsed .m-card-bd {
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
  opacity: 0;
  overflow: hidden;
}

.m-card-bd {
  padding: 16px 18px;
  display: flex;
  flex-direction: column;
  align-items: center;
  max-height: 800px;
  transition: max-height .3s ease, padding .3s ease, opacity .25s;
  opacity: 1;
  border-top: 1px solid #f1f5f9;
}

/* 色彩主题：左侧竖条 */
.accent-blue {
  border-left-color: #3b82f6;
}

.accent-blue .card-icon {
  color: #3b82f6;
}

.accent-green {
  border-left-color: #22c55e;
}

.accent-green .card-icon {
  color: #22c55e;
}

.accent-orange {
  border-left-color: #f59e0b;
}

.accent-orange .card-icon {
  color: #f59e0b;
}

.accent-red {
  border-left-color: #ef4444;
}

.accent-red .card-icon {
  color: #ef4444;
}

/* ===================== 表单 Grid ===================== */
.fg {
  display: grid;
  grid-template-columns: auto 250px;
  column-gap: 12px;
  row-gap: 12px;
  align-items: center;
  width: fit-content;
  margin: 0 auto;
}

.fgr {
  display: contents;
}

.fgr label {
  text-align: left;
  white-space: nowrap;
  font-size: 13px;
  color: #475569;
}

.fgr :deep(.el-input),
.fgr :deep(.el-select) {
  width: 100% !important;
}

.rq {
  color: #ef4444;
  margin-right: 2px;
}

/* ===================== 环境切换 ===================== */
:deep(.env-group) {
  display: inline-flex;
  justify-content: center;
  margin: 14px auto 10px;
}

:deep(.env-track) {
  display: inline-flex;
  gap: 0;
  background: #f1f5f9;
  border-radius: 6px;
  padding: 2px;
  flex-wrap: nowrap;
}

:deep(.env-track label) {
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 5px 14px;
  border-radius: 5px;
  border: none;
  background: transparent;
  font-size: 12px;
  font-weight: 500;
  color: #64748b;
  transition: all .2s;
  user-select: none;
  white-space: nowrap;
}

:deep(.env-track label.active) {
  background: #fff;
  color: #6366f1;
  box-shadow: 0 1px 3px rgba(0, 0, 0, .1);
  font-weight: 600;
}

:deep(.env-track label i) {
  font-size: 11px;
}

:deep(.env-track input[type="radio"]) {
  display: none;
}

/* ===================== 按钮 ===================== */
:deep(.btn-group) {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin: 10px 0 12px;
}

/* ===================== 结果区 ===================== */
.result {
  width: 100%;
  min-height: 32px;
  max-height: 160px;
  overflow-y: auto;
  padding: 10px 14px;
  border-radius: 8px;
  background: #f8fafc;
  font-size: 13px;
  text-align: center;
  line-height: 1.7;
  color: #475569;
  word-wrap: break-word;
  word-break: break-all;
  white-space: pre-wrap;
}

.result:empty {
  display: none;
}

.result-loading {
  color: #6366f1;
  font-weight: 500;
}

.result-loading i {
  margin-right: 4px;
}
</style>
