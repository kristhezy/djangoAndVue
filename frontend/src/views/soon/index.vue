<template>
  <div class="mo-page">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title"><i class="fa-solid fa-clock"></i> SOON 配置管理</h2>
      </div>
    </div>

    <div class="mo-body">
      <!-- 第一列 -->
      <div class="column">
        <!-- 卡片1: SOON版企业开户 -->
        <div :class="['m-card', { collapsed: !cards.soa }]">
          <div class="m-card-hd accent-blue" @click="cards.soa = !cards.soa">
            <div class="m-card-hd-left"><i class="fa-solid fa-building card-icon"></i>
              <h3>SOON版企业开户</h3>
            </div>
            <i :class="['fa-solid fa-chevron-right chevron', { open: cards.soa }]"></i>
          </div>
          <div class="m-card-bd">
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span>企业名称</label><el-input v-model="soa.compName"
                  placeholder="输入企业名称" /></div>
              <div class="fgr"><label>手机号码</label><el-input v-model="soa.phone" placeholder="输入带区号的手机号，如+86-" /></div>
              <div class="fgr"><label><span class="rq">*</span>登录邮箱</label><el-input v-model="soa.lemail"
                  placeholder="输入邮箱号" /></div>
              <div class="fgr"><label>有效日期</label><el-input v-model="soa.expireTime" type="date" /></div>
            </div>
            <EnvRadio v-model="soa.env" name="soa-env" />
            <BtnGroup @reset="resetSoa" @submit="submitSoa" />
            <ResultBox :text="soa.result" :loading="soa.loading" />
          </div>
        </div>

        <!-- 卡片2: 企业信息配置 -->
        <div :class="['m-card', { collapsed: !cards.uci }]">
          <div class="m-card-hd accent-green" @click="cards.uci = !cards.uci">
            <div class="m-card-hd-left"><i class="fa-solid fa-sliders card-icon"></i>
              <h3>企业信息配置</h3>
            </div>
            <i :class="['fa-solid fa-chevron-right chevron', { open: cards.uci }]"></i>
          </div>
          <div class="m-card-bd">
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span>企业ID</label><el-input v-model="uci.compId"
                  placeholder="输入后回车可查有效日期" @keydown.enter="queryCompInfo" /></div>
              <div class="fgr"><label>销售席位</label><el-input v-model="uci.maxTotAcc" type="number"
                  placeholder="0为无限席位" /></div>
              <div class="fgr"><label>有效日期</label>
                <div class="date-wrapper">
                  <el-input v-model="uci.expireTime" type="date" :disabled="!uci.islong" style="width:160px" />
                  <el-checkbox v-model="uci.islong" style="margin-left:8px" />
                </div>
              </div>
              <div class="fgr"><label>企业状态</label>
                <el-select v-model="uci.compStatus" placeholder="请选择" clearable>
                  <el-option label="正常" value="1" /><el-option label="禁用" value="0" /><el-option label="注销" value="2" />
                </el-select>
              </div>
            </div>
            <EnvRadio v-model="uci.env" name="uci-env" />
            <BtnGroup @reset="resetUci" @submit="submitUci" />
            <ResultBox :text="uci.result" :loading="uci.loading" />
          </div>
        </div>

        <!-- 卡片3: SOON版手工发放时长 -->
        <div :class="['m-card', { collapsed: !cards.dad }]">
          <div class="m-card-hd accent-orange" @click="cards.dad = !cards.dad">
            <div class="m-card-hd-left"><i class="fa-solid fa-clock card-icon"></i>
              <h3>SOON版手工发放时长</h3>
            </div>
            <i :class="['fa-solid fa-chevron-right chevron', { open: cards.dad }]"></i>
          </div>
          <div class="m-card-bd">
            <TabGroup :tabs="[{ value: 'personal', label: '个人版' }, { value: 'company', label: '企业版' }]"
              v-model="dad.bpoc" @change="onDadTabChange" />
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span><span v-html="dad.labelName"></span></label><el-input
                  v-model="dad.ccid" :placeholder="dad.placeholder" /></div>
              <div class="fgr"><label><span class="rq">*</span>发放时长</label><el-input v-model="dad.duration"
                  placeholder="输入发放时长(分)" /></div>
              <div class="fgr"><label>发放类型</label>
                <el-select v-model="dad.dtype">
                  <el-option label="所有类型" value="" /><el-option label="会议转录" value="0" /><el-option label="AI翻译"
                    value="1" />
                </el-select>
              </div>
            </div>
            <EnvRadio v-model="dad.env" name="dad-env" />
            <BtnGroup @reset="resetDad" @submit="submitDad" />
            <ResultBox :text="dad.result" :loading="dad.loading" />
          </div>
        </div>
      </div>

      <!-- 第二列 -->
      <div class="column">
        <!-- 卡片4: 生成物料链接 -->
        <div :class="['m-card', { collapsed: !cards.gfl }]">
          <div class="m-card-hd accent-purple" @click="cards.gfl = !cards.gfl">
            <div class="m-card-hd-left"><i class="fa-solid fa-link card-icon"></i>
              <h3>生成物料链接</h3>
            </div>
            <i :class="['fa-solid fa-chevron-right chevron', { open: cards.gfl }]"></i>
          </div>
          <div class="m-card-bd">
            <TabGroup :tabs="gflTabs" v-model="gfl.ftype" @change="onGflTabChange" />
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span>物料ID</label><el-input v-model="gfl.fileId"
                  :placeholder="gfl.filePlaceholder" /></div>
              <div class="fgr"><label><span class="rq">*</span>员工ID</label><el-input v-model="gfl.cardId"
                  placeholder="输入cardId" /></div>
              <div class="fgr"><label><span class="rq">*</span>名片ID</label><el-input v-model="gfl.holderId"
                  placeholder="输入holderId" /></div>
            </div>
            <EnvRadio v-model="gfl.env" name="gfl-env" />
            <BtnGroup @reset="resetGfl" @submit="submitGfl" />
            <ResultBox :text="gfl.result" :loading="gfl.loading" />
          </div>
        </div>

        <!-- 卡片5: 解绑翻译器卡片 -->
        <div :class="['m-card', { collapsed: !cards.ubd }]">
          <div class="m-card-hd accent-red" @click="cards.ubd = !cards.ubd">
            <div class="m-card-hd-left"><i class="fa-solid fa-unlink card-icon"></i>
              <h3>解绑翻译器卡片</h3>
            </div>
            <i :class="['fa-solid fa-chevron-right chevron', { open: cards.ubd }]"></i>
          </div>
          <div class="m-card-bd">
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span>卡片编码</label><el-input v-model="ubd.deviceNo"
                  placeholder="输入翻译卡编码" /></div>
              <div class="fgr"><label>员工ID</label><el-input v-model="ubd.cardId" placeholder="仅解绑该员工数据" /></div>
            </div>
            <div class="note">注:不传员工ID时,则解绑设备所有关系</div>
            <EnvRadio v-model="ubd.env" name="ubd-env" />
            <BtnGroup @reset="resetUbd" @submit="submitUbd" />
            <ResultBox :text="ubd.result" :loading="ubd.loading" />
          </div>
        </div>

        <!-- 卡片6: SOON名片和NFC卡片 -->
        <div :class="['m-card', { collapsed: !cards.nfc }]">
          <div class="m-card-hd accent-blue" @click="cards.nfc = !cards.nfc">
            <div class="m-card-hd-left"><i class="fa-solid fa-address-card card-icon"></i>
              <h3>SOON名片和NFC卡片</h3>
            </div>
            <i :class="['fa-solid fa-chevron-right chevron', { open: cards.nfc }]"></i>
          </div>
          <div class="m-card-bd">
            <TabGroup :tabs="[{ value: 'setnfc', label: '绑定' }, { value: 'remove', label: '解绑' }]" v-model="nfc.mode"
              @change="onNfcTabChange" />
            <div class="fg">
              <div v-if="nfc.mode === 'setnfc'" class="fgr"><label><span class="rq">*</span>名片ID</label><el-input
                  v-model="nfc.cardId" /></div>
              <div class="fgr"><label><span class="rq">*</span>CODE</label><el-input v-model="nfc.code" /></div>
            </div>
            <EnvRadio v-model="nfc.env" name="nfc-env" />
            <BtnGroup @reset="resetNfc" @submit="submitNfc" />
            <ResultBox :text="nfc.result" :loading="nfc.loading" />
          </div>
        </div>
      </div>

      <!-- 第三列 -->
      <div class="column">
        <!-- 卡片7: 修改SOON版会员 -->
        <div :class="['m-card', { collapsed: !cards.rpv }]">
          <div class="m-card-hd accent-green" @click="cards.rpv = !cards.rpv">
            <div class="m-card-hd-left"><i class="fa-solid fa-user-pen card-icon"></i>
              <h3>修改SOON版会员</h3>
            </div>
            <i :class="['fa-solid fa-chevron-right chevron', { open: cards.rpv }]"></i>
          </div>
          <div class="m-card-bd">
            <TabGroup :tabs="[{ value: 'personal', label: '个人版' }, { value: 'company', label: '企业版' }]"
              v-model="rpv.bpoc" @change="onRpvTabChange" />
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span>企业ID</label><el-input v-model="rpv.compId" /></div>
              <div v-if="rpv.bpoc === 'personal'" class="fgr"><label><span class="rq">*</span>名片ID</label><el-input
                  v-model="rpv.cardId" placeholder="第一张名片的cardID" /></div>
              <div class="fgr"><label><span class="rq">*</span>版本</label>
                <el-select v-model="rpv.pversion" placeholder="请选择" clearable>
                  <el-option v-if="rpv.bpoc === 'personal'" label="个人版Pro" value="1" />
                  <el-option v-if="rpv.bpoc === 'company'" label="企业版Pro" value="3" />
                </el-select>
              </div>
              <div class="fgr"><label><span class="rq">*</span>有效日期</label><el-input v-model="rpv.expireTime"
                  type="date" /></div>
            </div>
            <EnvRadio v-model="rpv.env" name="rpv-env" />
            <BtnGroup @reset="resetRpv" @submit="submitRpv" />
            <ResultBox :text="rpv.result" :loading="rpv.loading" />
          </div>
        </div>

        <!-- 卡片8: 修改SOON用户工作台 -->
        <div :class="['m-card', { collapsed: !cards.ush }]">
          <div class="m-card-hd accent-orange" @click="cards.ush = !cards.ush">
            <div class="m-card-hd-left"><i class="fa-solid fa-desktop card-icon"></i>
              <h3>修改SOON用户工作台</h3>
            </div>
            <i :class="['fa-solid fa-chevron-right chevron', { open: cards.ush }]"></i>
          </div>
          <div class="m-card-bd">
            <div class="fg">
              <div class="fgr"><label>邮箱/手机</label><el-input v-model="ush.emorp" @blur="onEmorpBlur"
                  @keydown.enter.prevent="getUidByEmail" /></div>
              <div v-if="ush.queryError" class="sub-result"><span style="color:#ef4444;font-weight:500">{{
                ush.queryError }}</span></div>
              <div class="fgr"><label><span class="rq">*</span>用户ID</label><el-input v-model="ush.userId" /></div>
              <div class="fgr"><label><span class="rq">*</span>用户版本</label>
                <el-select v-model="ush.status" placeholder="请选择" clearable>
                  <el-option label="大众版" value="0" /><el-option label="Tommy版" value="1" />
                </el-select>
              </div>
            </div>
            <EnvRadio v-model="ush.env" name="ush-env" />
            <BtnGroup @reset="resetUsh" @submit="submitUsh" />
            <ResultBox :text="ush.result" :loading="ush.loading" />
          </div>
        </div>

        <!-- 卡片9: 加密/解密 -->
        <div :class="['m-card', { collapsed: !cards.crypto }]">
          <div class="m-card-hd accent-purple" @click="cards.crypto = !cards.crypto">
            <div class="m-card-hd-left"><i class="fa-solid fa-lock card-icon"></i>
              <h3>加密/解密</h3>
            </div>
            <i :class="['fa-solid fa-chevron-right chevron', { open: cards.crypto }]"></i>
          </div>
          <div class="m-card-bd">
            <TabGroup :tabs="[{ value: 'decrypt', label: '解密' }, { value: 'encrypt', label: '加密' }]"
              v-model="crypto.mode" />
            <div style="width:100%;margin-bottom:8px">
              <el-input v-model="crypto.value" type="textarea" :rows="3" placeholder="请输入待加密/解密的内容" />
            </div>
            <EnvRadio v-model="crypto.env" name="crypto-env" />
            <BtnGroup @reset="resetCrypto" @submit="submitCrypto" />
            <ResultBox :text="crypto.result" :loading="crypto.loading" />
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

// --- Reusable sub-components (inline) ---
const EnvRadio = {
  props: ['modelValue', 'name'], emits: ['update:modelValue'],
  template: `<div class="env-group"><div class="env-track"><label :class="{active:modelValue==='test'}"><i class="fa-solid fa-flask"></i><input type="radio" :name="name" value="test" :checked="modelValue==='test'" @change="$emit('update:modelValue','test')"/><span>测试环境</span></label><label :class="{active:modelValue==='prod'}"><i class="fa-solid fa-rocket"></i><input type="radio" :name="name" value="prod" :checked="modelValue==='prod'" @change="$emit('update:modelValue','prod')"/><span>生产环境</span></label></div></div>`,
}
const BtnGroup = { emits: ['reset', 'submit'], template: `<div class="btn-group"><el-button @click="$emit('reset')">重置</el-button><el-button type="primary" @click="$emit('submit')">提交</el-button></div>` }
const ResultBox = { props: ['text', 'loading'], template: `<div class="result"><span v-if="loading" class="result-loading"><i class="fa-solid fa-spinner fa-spin"></i> 加载中...</span><span v-else v-html="text"></span></div>` }
const TabGroup = {
  props: ['tabs', 'modelValue'], emits: ['update:modelValue', 'change'],
  template: `<div class="tab-group"><label v-for="t in tabs" :key="t.value" :class="{active:modelValue===t.value}"><input type="radio" :value="t.value" :checked="modelValue===t.value" @change="$emit('update:modelValue',t.value);$emit('change',t.value)"/><span class="tab-item">{{ t.label }}</span></label></div>`,
}

// --- Card collapse state ---
const cards = reactive({ soa: true, uci: false, dad: false, gfl: true, ubd: false, nfc: false, rpv: true, ush: false, crypto: false })

// --- Card 1: SOON版企业开户 ---
const soa = reactive({ compName: '', phone: '', lemail: '', expireTime: '', env: 'test', result: '', loading: false })
function resetSoa() { Object.assign(soa, { compName: '', phone: '', lemail: '', expireTime: '', env: 'test', result: '' }) }
function submitSoa() {
  if (!soa.compName || !soa.lemail) { warn('"企业名称"和"登录邮箱"不能为空！'); return }
  soa.loading = true; soa.result = ''
  http.post('/ov/setting/openaccount', { privaddr: '', cname: soa.compName, csname: '', phone: soa.phone, lname: soa.lemail, pwd: '', langType: 'zh-CN', etime: soa.expireTime, env: soa.env, version: 4, type: 'openaccount' })
    .then(r => { soa.result = r.data?.data || '' }).catch(() => { soa.result = '请求失败' }).finally(() => { soa.loading = false })
}

// --- Card 2: 企业信息配置 ---
const uci = reactive({ compId: '', maxTotAcc: '', expireTime: '', islong: false, compStatus: '', env: 'test', result: '', loading: false })
function resetUci() { Object.assign(uci, { compId: '', maxTotAcc: '', expireTime: '', islong: false, compStatus: '', env: 'test', result: '' }) }
function queryCompInfo() { /* placeholder: original had no actual handler */ }
function submitUci() {
  if (!uci.compId) { warn('"企业ID"不能为空！'); return }
  if (!uci.maxTotAcc && !uci.compStatus && !uci.expireTime && !uci.islong) { warn('输入需要修改的内容！'); return }
  uci.loading = true; uci.result = ''
  http.post('/ov/setting/updcompinfo', { privaddr: '', compId: uci.compId, mta: uci.maxTotAcc, cs: uci.compStatus, aics: '', isl: uci.islong, expt: uci.expireTime, env: uci.env, version: 4, type: 'updcompinfo' })
    .then(r => { uci.result = r.data?.data || '' }).catch(() => { uci.result = '请求失败' }).finally(() => { uci.loading = false })
}

// --- Card 3: SOON版手工发放时长 ---
const dad = reactive({ bpoc: 'personal', ccid: '', duration: '', dtype: '1', env: 'test', result: '', loading: false, labelName: '员&nbsp;工&nbsp;I&nbsp;D', placeholder: '输入员工ID' })
function onDadTabChange(v) {
  if (v === 'personal') { dad.labelName = '员&nbsp;工&nbsp;I&nbsp;D'; dad.placeholder = '输入员工ID' }
  else { dad.labelName = '企&nbsp;业&nbsp;I&nbsp;D'; dad.placeholder = '输入企业ID' }
}
function resetDad() { Object.assign(dad, { bpoc: 'personal', ccid: '', duration: '', dtype: '1', env: 'test', result: '', labelName: '员&nbsp;工&nbsp;I&nbsp;D', placeholder: '输入员工ID' }) }
function submitDad() {
  if (!dad.ccid) { warn(dad.bpoc === 'personal' ? '"员工ID"不能为空！' : '"企业ID"不能为空！'); return }
  if (!dad.duration) { warn('"发放时长"不能为空！'); return }
  dad.loading = true; dad.result = ''
  http.post('/ov/setting/addduration', { bpoc: dad.bpoc, ccid: dad.ccid, duration: dad.duration, dtype: dad.dtype, etime: '', env: dad.env, version: 4, type: 'addduration' })
    .then(r => { dad.result = r.data?.data || '' }).catch(() => { dad.result = '请求失败' }).finally(() => { dad.loading = false })
}

// --- Card 4: 生成物料链接 ---
const gflTabs = [{ value: 'dcard', label: '名片' }, { value: 'file', label: '文件' }, { value: 'video', label: '视频' }, { value: 'product', label: '产品' }, { value: 'case', label: '案例' }]
const gfl = reactive({ ftype: 'dcard', fileId: '0', cardId: '', holderId: '', env: 'test', result: '', loading: false, filePlaceholder: '' })
function onGflTabChange(v) {
  if (v === 'dcard') { gfl.fileId = '0'; gfl.filePlaceholder = '' }
  else { gfl.fileId = ''; gfl.filePlaceholder = '输入materialId' }
}
function resetGfl() { Object.assign(gfl, { ftype: 'dcard', fileId: '0', cardId: '', holderId: '', env: 'test', result: '', filePlaceholder: '' }) }
function submitGfl() {
  if (!gfl.fileId || !gfl.cardId || !gfl.holderId) { warn('必填项不能为空！'); return }
  gfl.loading = true; gfl.result = ''
  http.post('/ov/setting/getflink', { ftype: gfl.ftype, fileId: gfl.fileId, cardId: gfl.cardId, holderId: gfl.holderId, env: gfl.env, version: 4, type: 'getflink' })
    .then(r => { gfl.result = r.data?.data || '' }).catch(() => { gfl.result = '请求失败' }).finally(() => { gfl.loading = false })
}

// --- Card 5: 解绑翻译器 ---
const ubd = reactive({ deviceNo: '', cardId: '', env: 'test', result: '', loading: false })
function resetUbd() { Object.assign(ubd, { deviceNo: '', cardId: '', env: 'test', result: '' }) }
function submitUbd() {
  ubd.loading = true; ubd.result = ''
  http.post('/ov/setting/removedevice', { deviceNo: ubd.deviceNo, cardId: ubd.cardId, env: ubd.env, version: 4, type: 'removedevice' })
    .then(r => { ubd.result = r.data?.data || '' }).catch(() => { ubd.result = '请求失败' }).finally(() => { ubd.loading = false })
}

// --- Card 6: SOON名片和NFC卡片 ---
const nfc = reactive({ mode: 'setnfc', cardId: '', code: '', env: 'test', result: '', loading: false })
function onNfcTabChange() { nfc.cardId = '' }
function resetNfc() { Object.assign(nfc, { mode: 'setnfc', cardId: '', code: '', env: 'test', result: '' }) }
function submitNfc() {
  if (!nfc.code) { warn('"CODE"不能为空！'); return }
  if (nfc.mode === 'setnfc' && !nfc.cardId) { warn('"名片ID"不能为空！'); return }
  nfc.loading = true; nfc.result = ''
  const url = nfc.mode === 'setnfc' ? '/ov/setting/setnfcservice' : '/ov/setting/rmvnfcservice'
  const body = nfc.mode === 'setnfc'
    ? { code: nfc.code, cardid: nfc.cardId, env: nfc.env, version: 4, type: 'setnfcservice' }
    : { code: nfc.code, env: nfc.env, version: 4, type: 'rmvnfcservice' }
  http.post(url, body).then(r => { nfc.result = r.data?.data || '' }).catch(() => { nfc.result = '请求失败' }).finally(() => { nfc.loading = false })
}

// --- Card 7: 修改SOON版会员 ---
const rpv = reactive({ bpoc: 'personal', compId: '0', cardId: '', pversion: '', expireTime: '', env: 'test', result: '', loading: false })
function onRpvTabChange(v) {
  if (v === 'personal') { rpv.compId = '0'; rpv.pversion = '' }
  else { rpv.compId = ''; rpv.pversion = '' }
}
function resetRpv() { Object.assign(rpv, { bpoc: 'personal', compId: '0', cardId: '', pversion: '', expireTime: '', env: 'test', result: '' }) }
function submitRpv() {
  if (rpv.bpoc === 'personal' && !rpv.cardId) { warn('个人版"名片ID"不能为空！'); return }
  if (!rpv.compId || !rpv.pversion) { warn('必填项不能为空！'); return }
  rpv.loading = true; rpv.result = ''
  http.post('/ov/setting/resetpv', { bpoc: rpv.bpoc, compid: rpv.compId, cardid: rpv.cardId, pv: rpv.pversion, expt: rpv.expireTime, env: rpv.env, version: 4, type: 'resetpv' })
    .then(r => { rpv.result = r.data?.data || '' }).catch(() => { rpv.result = '请求失败' }).finally(() => { rpv.loading = false })
}

// --- Card 8: 修改SOON用户工作台 ---
const ush = reactive({ emorp: '', userId: '', status: '', env: 'test', result: '', loading: false, queryError: '' })
function resetUsh() { Object.assign(ush, { emorp: '', userId: '', status: '', env: 'test', result: '', queryError: '' }) }
function onEmorpBlur() { if (ush.emorp) getUidByEmail() }
function getUidByEmail() {
  if (!ush.emorp) { warn('输入"邮箱/手机"查询!'); return }
  ush.queryError = ''; ush.userId = ''
  http.post('/ov/setting/getuidbyemail', { email: ush.emorp, env: ush.env, version: 4, type: 'getuidbyemail' })
    .then(r => {
      if (r.data?.code === '0') { ush.userId = r.data.data }
      else { ush.queryError = r.data?.msg || '查询失败' }
    }).catch(() => { ush.queryError = '请求失败' })
}
function submitUsh() {
  if (!ush.userId) { warn('"用户ID"不能为空！'); return }
  if (!ush.status) { warn('"用户版本"不能为空！'); return }
  ush.loading = true; ush.result = ''
  http.post('/ov/setting/setnewhome', { userId: ush.userId, status: ush.status, env: ush.env, version: 4, type: 'setnewhome' })
    .then(r => { ush.result = r.data?.data || '' }).catch(() => { ush.result = '请求失败' }).finally(() => { ush.loading = false })
}

// --- Card 9: 加密/解密 ---
const crypto = reactive({ mode: 'decrypt', value: '', env: 'test', result: '', loading: false })
function resetCrypto() { Object.assign(crypto, { mode: 'decrypt', value: '', env: 'test', result: '' }) }
function submitCrypto() {
  if (!crypto.value) { warn('请输入内容！'); return }
  crypto.loading = true; crypto.result = ''
  const url = crypto.mode === 'encrypt' ? '/ov/setting/cryptoEncrypt' : '/ov/setting/cryptoDecrypt'
  http.post(url, { value: crypto.value, env: crypto.env, version: 4, uname: '', emailSuffix: '' })
    .then(r => { crypto.result = r.data?.data || r.data?.msg || '操作完成' }).catch(e => { crypto.result = '请求失败: ' + (e.message || e) }).finally(() => { crypto.loading = false })
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

.chevron {
  font-size: 11px;
  color: #94a3b8;
  transition: transform .25s ease;
}

.chevron.open {
  transform: rotate(90deg);
}

.m-card.collapsed .m-card-bd {
  display: none;
}

.m-card-bd {
  padding: 16px 18px;
  display: flex;
  flex-direction: column;
  align-items: center;
  border-top: 1px solid #f1f5f9;
}

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

.accent-purple {
  border-left-color: #8b5cf6;
}

.accent-purple .card-icon {
  color: #8b5cf6;
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
  grid-template-columns: auto 300px;
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

.date-wrapper {
  display: flex;
  align-items: center;
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

/* ===================== Tab 切换 ===================== */
:deep(.tab-group) {
  display: inline-flex;
  justify-content: center;
  gap: 0;
  margin: 0 auto 14px;
  background: #f1f5f9;
  border-radius: 6px;
  padding: 2px;
  flex-wrap: nowrap;
}

:deep(.tab-group label) {
  cursor: pointer;
  margin: 0;
  display: flex;
  flex: 1;
  justify-content: center;
  white-space: nowrap;
}

:deep(.tab-group .tab-item) {
  padding: 6px 16px;
  background: transparent;
  color: #64748b;
  border: none;
  border-radius: 5px;
  font-size: 12px;
  font-weight: 500;
  transition: all .2s;
  white-space: nowrap;
}

:deep(.tab-group label.active .tab-item) {
  background: #fff;
  color: #6366f1;
  box-shadow: 0 1px 3px rgba(0, 0, 0, .08);
  font-weight: 600;
}

:deep(.tab-group input[type="radio"]) {
  display: none;
}

/* ===================== 杂项 ===================== */
.note {
  color: #94a3b8;
  font-size: 12px;
  margin-bottom: 8px;
  text-align: center;
}

.sub-result {
  grid-column: 1 / -1;
  min-height: 20px;
  text-align: center;
  font-size: 12px;
  padding: 2px 0;
}
</style>
