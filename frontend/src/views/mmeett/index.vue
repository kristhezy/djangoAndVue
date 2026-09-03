<template>
  <div class="mo-page">
    <div style="text-align:right;padding:2px 18px 0 0;">
      <label style="font-size:12px;color:#666;">邮箱后缀:</label>
      <el-input v-model="emailSuffix" style="width:120px;display:inline-flex" size="small" />
    </div>
    <div class="mo-body">
      <!-- 第一列 -->
      <div class="column">
        <!-- 卡片1: Mmeett注册用户 -->
        <Card title="Mmeett注册用户" :open="cards.reg">
          <template #header><span class="ct" @click="cards.reg=!cards.reg">▼</span></template>
          <TabGroup :tabs="[{v:'regist',l:'用户注册'},{v:'bemaspp',l:'绑定邮箱&设置支付密码'}]" v-model="reg.mset" @change="onRegTab" />
          <div class="fg">
            <div class="fgr"><label><span class="rq">*</span>用户账号:</label><el-input v-model="reg.uname" placeholder="输入用户账号" /></div>
            <div v-if="reg.mset==='regist'" class="fgr"><label><span class="rq">*</span>邀请码:</label><el-input v-model="reg.rcode" placeholder="输入邀请码" /></div>
            <div v-if="reg.mset==='regist'" class="fgr"><label><span class="rq">*</span>国家/地区:</label><el-select v-model="reg.country" style="width:180px" @focus="loadCountries"><el-option v-for="c in countryList" :key="c.value" :label="c.name" :value="c.value" /></el-select></div>
            <div class="fgr"><label><span class="rq">*</span>登录密码:</label><el-input v-model="reg.pwd" /></div>
            <div v-if="reg.mset==='regist' && reg.env==='test'" class="fgr"><label><span class="rq">*</span>绑定邮箱:</label><el-select v-model="reg.bemail" style="width:180px"><el-option label="是" value="yes" /><el-option label="否" value="no" /></el-select></div>
            <div v-if="reg.mset==='regist' && reg.env==='test'" class="fgr"><label><span class="rq">*</span>支付密码:</label><el-input v-model="reg.paypwd" /></div>
            <div class="fgr"><label><span class="rq">*</span>账号数量:</label><el-input v-model="reg.unum" type="number" /></div>
          </div>
          <EnvRadio v-model="reg.env" name="reg-env" />
          <BtnGroup @reset="resetReg" @submit="submitReg" />
          <ResultBox :lines="reg.results" :loading="reg.loading" />
        </Card>

        <!-- 卡片4: 修改国家/地区 | 用户名 | 用户邮箱 -->
        <Card title="修改国家/地区 | 用户名 | 用户邮箱" :open="cards.cfg">
          <template #header><span class="ct" @click="cards.cfg=!cards.cfg">▼</span></template>
          <div class="fg">
            <div class="fgr"><label><span class="rq">*</span>用户账号:</label><el-input v-model="cfg.uname" /></div>
            <div class="fgr"><label>用户名:</label>
              <div style="display:flex;width:180px"><el-input v-model="cfg.userName" style="flex:1" /><el-button size="small" @click="queryUser('userName')" title="查询用户名"><i class="fa-solid fa-user"></i></el-button></div></div>
            <div class="fgr"><label>用户邮箱:</label>
              <div style="display:flex;width:180px"><el-input v-model="cfg.userEmail" style="flex:1" /><el-button size="small" @click="queryUser('userEmail')" title="查询用户邮箱"><i class="fa-solid fa-envelope"></i></el-button></div></div>
            <div class="fgr"><label>国家/地区:</label>
              <div style="display:flex;width:180px"><el-select v-model="cfg.country" style="flex:1" @focus="loadCountries"><el-option label="--请选择--" value="" /><el-option v-for="c in countryList" :key="c.value" :label="c.name" :value="c.value" /></el-select><el-button size="small" @click="queryUser('country')" title="查询注册国家"><i class="fa-solid fa-earth-americas"></i></el-button></div></div>
          </div>
          <EnvRadio v-model="cfg.env" name="cfg-env" />
          <BtnGroup @reset="resetCfg" @submit="submitCfg" />
          <ResultBox :text="cfg.result" :loading="cfg.loading" />
        </Card>

        <!-- 卡片7: 用户安置 -->
        <Card title="用户安置" :open="cards.settle">
          <template #header><span class="ct" @click="cards.settle=!cards.settle">▼</span></template>
          <TabGroup :tabs="[{v:'place',l:'安置'},{v:'cancel',l:'取消安置'}]" v-model="settle.type" @change="onSettleTab" />
          <div v-if="settle.type==='cancel'" class="radio-group">
            <label><span class="rq">*</span>取消方向:</label>
            <label v-for="d in [{v:'all',l:'全部'},{v:'up',l:'上级'},{v:'down',l:'下级'}]" :key="d.v" :class="{active:settle.cancelDir===d.v}"><input type="radio" :value="d.v" v-model="settle.cancelDir" /> {{ d.l }}</label>
          </div>
          <div class="fgi"><label><span class="rq">*</span>用户账号:</label><el-input v-model="settle.uname" style="width:140px" />
            <el-button size="small" text type="primary" @click="getTree('gettree')">查看树形结构</el-button>
            <el-button size="small" text type="primary" @click="getTree('issettle')">是否被安置</el-button>
          </div>
          <div v-if="settle.checkResult" style="color:blue;font-size:12px;margin:4px 0">{{ settle.checkResult }}</div>
          <div v-if="settle.type==='place'" class="radio-group">
            <label><span class="rq">*</span>是否批量:</label>
            <label :class="{active:settle.isBatch==='1'}"><input type="radio" value="1" v-model="settle.isBatch" /> 是</label>
            <label :class="{active:settle.isBatch==='0'}"><input type="radio" value="0" v-model="settle.isBatch" /> 否</label>
          </div>
          <EnvRadio v-model="settle.env" name="settle-env" />
          <BtnGroup @reset="resetSettle" @submit="submitSettle" />
          <ResultBox :lines="settle.results" :loading="settle.loading" />
        </Card>

        <!-- 卡片9: 赠送点位 -->
        <Card title="赠送点位" :open="cards.gift">
          <template #header><span class="ct" @click="cards.gift=!cards.gift">▼</span></template>
          <div class="fg">
            <div class="fgr"><label><span class="rq">*</span>用户账号:</label><el-input v-model="gift.uname" /></div>
            <div class="fgr"><label><span class="rq">*</span>会员等级:</label>
              <el-select v-model="gift.level" placeholder="--请选择--" style="width:180px">
                <el-option label="尊享" value="-1" /><el-option label="银级" value="3" /><el-option label="金级" value="1" /><el-option label="白金" value="2" /><el-option label="钻石" value="4" />
              </el-select></div>
            <div class="fgr"><label><span class="rq">*</span>会员数量:</label><el-input v-model="gift.amount" type="number" /></div>
            <div class="fgr"><label><span class="rq">*</span>有效天数:</label><el-input v-model="gift.expire" type="number" /></div>
          </div>
          <EnvRadio v-model="gift.env" name="gift-env" />
          <BtnGroup @reset="resetGift" @submit="submitGift" />
          <ResultBox :text="gift.result" :loading="gift.loading" />
        </Card>
      </div>

      <!-- 第二列 -->
      <div class="column">
        <!-- 卡片2: Mmeett余额购买会员 -->
        <Card title="Mmeett余额购买会员" :open="cards.buy">
          <template #header><span class="ct" @click="cards.buy=!cards.buy">▼</span></template>
          <div class="fg">
            <div class="fgr"><label><span class="rq">*</span>用户账号:</label><el-input v-model="buy.uname" @blur="getRechargeConfig" /></div>
            <div class="fgr"><label><span class="rq">*</span>会员类型:</label><el-select v-model="buy.level" placeholder="--请选择--" style="width:180px"><el-option v-for="l in buy.levels" :key="l.id" :label="l.name" :value="l.id" /></el-select></div>
            <div class="fgr"><label><span class="rq">*</span>账号数量:</label><el-input v-model="buy.unum" type="number" /></div>
          </div>
          <EnvRadio v-model="buy.env" name="buy-env" />
          <div style="color:red;font-size:13px;text-align:center;margin:4px 0">注：相同会员类型可批量执行，反之，则只可单个执行。</div>
          <BtnGroup @reset="resetBuy" @submit="submitBuy" />
          <ResultBox :lines="buy.results" :loading="buy.loading" />
        </Card>

        <!-- 卡片8: 会员降级 -->
        <Card title="会员降级" :open="cards.sv">
          <template #header><span class="ct" @click="cards.sv=!cards.sv">▼</span></template>
          <div class="fg">
            <div class="fgr"><label><span class="rq">*</span>用户账号:</label><el-input v-model="sv.uname" /></div>
            <div class="fgr"><label><span class="rq">*</span>会员等级:</label>
              <el-select v-model="sv.level" style="width:180px"><el-option label="非会员" :value="0" /><el-option label="银级" :value="3" /><el-option label="金级" :value="1" /><el-option label="白金" :value="2" /></el-select></div>
          </div>
          <EnvRadio v-model="sv.env" name="sv-env" />
          <BtnGroup @reset="resetSv" @submit="submitSv" />
          <ResultBox :text="sv.result" :loading="sv.loading" />
        </Card>

        <!-- 卡片5: 分成奖励重跑 -->
        <Card title="分成奖励重跑" :open="cards.reward">
          <template #header><span class="ct" @click="cards.reward=!cards.reward">▼</span></template>
          <div class="checkbox-group">
            <el-checkbox v-model="reward.pre">预结算</el-checkbox>
            <el-checkbox v-model="reward.detail">明细</el-checkbox>
            <el-checkbox v-model="reward.summary">汇总</el-checkbox>
          </div>
          <div class="cb-grid">
            <span class="grid-title">奖励类型 <el-checkbox v-model="reward.allTypes" @change="onRewardAllChange" style="color:#4f6ef7">全选</el-checkbox></span>
            <el-checkbox v-for="rt in rewardTypeList" :key="rt.v" :label="rt.l" :value="rt.v" v-model="reward.types" />
          </div>
          <div v-if="reward.types.includes('43')" class="checkbox-group" style="margin-top:8px">
            <span style="font-weight:500">集团奖励重跑模式:</span>
            <el-checkbox v-model="reward.weekly">周结</el-checkbox>
            <el-checkbox v-model="reward.monthly">月结</el-checkbox>
          </div>
          <div class="fgi">
            <label><span class="rq">*</span>时间范围:</label>
            <el-date-picker v-model="reward.dateRange" type="daterange" start-placeholder="开始" end-placeholder="结束" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width:220px" />
          </div>
          <EnvRadio v-model="reward.env" name="reward-env" />
          <BtnGroup @reset="resetReward" @submit="submitReward" />
          <ResultBox :lines="reward.results" :loading="reward.loading" />
        </Card>

        <!-- 用户注销 -->
        <Card title="用户注销" :open="cards.del">
          <template #header><span class="ct" @click="cards.del=!cards.del">▼</span></template>
          <div class="fg">
            <div class="fgr"><label><span class="rq">*</span>账号:</label><el-input v-model="del.account" placeholder="输入账号" /></div>
            <div class="fgr"><label><span class="rq">*</span>密码:</label><el-input v-model="del.pwd" /></div>
            <div class="fgr"><label><span class="rq">*</span>数量:</label><el-input v-model="del.num" type="number" :min="1" :max="10000" /></div>
          </div>
          <EnvRadio v-model="del.env" name="del-env" />
          <BtnGroup @reset="resetDel" @submit="submitDel" />
          <ResultBox :text="del.result" :loading="del.loading" />
        </Card>
      </div>

      <!-- 第三列 -->
      <div class="column">
        <!-- 卡片3: Mmeett生成邀请链路 -->
        <Card title="Mmeett生成邀请链路" :open="cards.ref">
          <template #header><span class="ct" @click="cards.ref=!cards.ref">▼</span></template>
          <div class="fg">
            <div class="fgr"><label><span class="rq">*</span>用户账号:</label><el-input v-model="ref.uname" @blur="queryRCode" /></div>
            <div class="fgr"><label><span class="rq">*</span>邀请码:</label><el-input v-model="ref.rcode" /></div>
            <div class="fgr"><label><span class="rq">*</span>国家/地区:</label><el-select v-model="ref.country" style="width:180px" @focus="loadCountries"><el-option v-for="c in countryList" :key="c.value" :label="c.name" :value="c.value" /></el-select></div>
            <div class="fgr"><label><span class="rq">*</span>会员类型:</label>
              <el-select v-model="ref.level" style="width:180px"><el-option label="银级" value="3" /><el-option label="金级" value="1" /><el-option label="白金" value="2" /><el-option label="钻石" value="4" /></el-select></div>
            <div class="fgr"><label><span class="rq">*</span>账号数量:</label><el-input v-model="ref.unum" type="number" /></div>
          </div>
          <EnvRadio v-model="ref.env" name="ref-env" />
          <BtnGroup @reset="resetRef" @submit="submitRef" />
          <ResultBox :lines="ref.results" :loading="ref.loading" />
        </Card>

        <!-- 卡片6: 算力充值/扣减 -->
        <Card title="算力充值/扣减" :open="cards.power">
          <template #header><span class="ct" @click="cards.power=!cards.power">▼</span></template>
          <TabGroup :tabs="[{v:'recharge',l:'充值'},{v:'deduct',l:'扣减'}]" v-model="power.op" />
          <template v-if="power.op==='recharge'">
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span>用户账号:</label><el-input v-model="power.uname" /></div>
              <div class="fgr"><label><span class="rq">*</span>充值类型:</label><el-select v-model="power.computingType" placeholder="--请选择--" style="width:180px" @focus="loadComputing"><el-option v-for="c in computingList" :key="c.value" :label="c.name" :value="c.value" /></el-select></div>
              <div v-if="power.computingType==='0'" class="fgr"><label><span class="rq">*</span>算力数值:</label><el-input v-model="power.computingNum" type="number" placeholder="请输入算力数值" /></div>
              <div class="fgr"><label><span class="rq">*</span>是否分佣:</label><el-select v-model="power.sendAward" style="width:180px"><el-option label="是" value="1" /><el-option label="否" value="0" /></el-select></div>
            </div>
            <EnvRadio v-model="power.env" name="power-env" />
          </template>
          <template v-else>
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span>用户账号:</label><el-input v-model="power.unameD" /></div>
              <div class="fgr"><label><span class="rq">*</span>算力数值:</label><el-input v-model="power.deductNum" type="number" placeholder="请输入扣减算力数值" /></div>
            </div>
            <EnvRadio v-model="power.envD" name="power-envD" />
          </template>
          <BtnGroup @reset="resetPower" @submit="submitPower" />
          <ResultBox :text="power.result" :loading="power.loading" />
        </Card>

        <!-- 卡片10: 账户充值/扣减 -->
        <Card title="账户充值/扣减" :open="cards.account">
          <template #header><span class="ct" @click="cards.account=!cards.account">▼</span></template>
          <div class="fg">
            <div class="fgr"><label><span class="rq">*</span>用户账号:</label><el-input v-model="account.uname" /></div>
            <div class="fgr"><label><span class="rq">*</span>金额:</label><el-input v-model="account.amount" type="number" placeholder="请输入金额" /></div>
          </div>
          <EnvRadio v-model="account.env" name="account-env" />
          <BtnGroup @reset="resetAccount" @submit="submitAccount" />
          <ResultBox :text="account.result" :loading="account.loading" />
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import http from '../../api/http.js'

// --- Inline sub-components ---
const Card = {
  props: ['title', 'open'],
  template: `<div :class="['card',{collapsed:!open}]"><div class="card-header"><h1>{{ title }}</h1><slot name="header" /></div><div class="card-body"><slot /></div></div>`,
}
const EnvRadio = {
  props: ['modelValue','name'], emits:['update:modelValue'],
  template:`<div class="env-group"><label :class="{active:modelValue==='test'}"><input type="radio" :name="name" value="test" :checked="modelValue==='test'" @change="$emit('update:modelValue','test')"/> 测试环境</label><label :class="{active:modelValue==='prod'}"><input type="radio" :name="name" value="prod" :checked="modelValue==='prod'" @change="$emit('update:modelValue','prod')"/> 生产环境</label></div>`,
}
const BtnGroup = { emits:['reset','submit'], template:`<div class="btn-group"><el-button @click="$emit('reset')">重置</el-button><el-button type="primary" @click="$emit('submit')">提交</el-button></div>` }
const ResultBox = {
  props:['text','lines','loading'],
  template:`<div class="result"><span v-if="loading" style="color:#6366f1">处理中...</span><template v-else-if="lines&&lines.length"><div v-for="(l,i) in lines" :key="i" v-html="l" style="border-bottom:1px solid #e0e0e0;padding:6px 0"></div></template><span v-else v-html="text||''"></span></div>`,
}
const TabGroup = {
  props:['tabs','modelValue'], emits:['update:modelValue','change'],
  template:`<div class="tab-group"><label v-for="t in tabs" :key="t.v" :class="{active:modelValue===t.v}"><input type="radio" :value="t.v" :checked="modelValue===t.v" @change="$emit('update:modelValue',t.v);$emit('change',t.v)"/><span class="tab-item">{{t.l}}</span></label></div>`,
}

const emailSuffix = reactive('@jt.com')
const cards = reactive({ reg:true, cfg:false, settle:false, gift:false, buy:true, sv:false, reward:false, del:false, ref:true, power:false, account:false })

// --- Shared: country list ---
const countryList = reactive([])
let countryLoaded = false
function loadCountries() {
  if (countryLoaded) return
  countryLoaded = true
  http.post('/ov/pmmeett/queryCountryInfo', { uname:'', env:'test', version:7, emailSuffix, type:'queryCountryInfo' })
    .then(r => { if (r.data?.data) countryList.push(...r.data.data) })
    .catch(() => { countryLoaded = false })
}

// --- Shared: computing list ---
const computingList = reactive([])
let computingLoaded = false
let computingNames = null
function loadComputing() {
  if (computingLoaded) return
  computingLoaded = true
  http.post('/ov/pmmeett/queryComputingList', { uname:'', env:'test', version:7, emailSuffix, type:'queryComputingList' })
    .then(r => {
      const d = r.data?.data
      if (d?.clist) { computingList.push(...d.clist); computingNames = d.computingNames }
    }).catch(() => { computingLoaded = false })
}

// --- Helpers ---
function parseUnameBase(raw) {
  const m = raw.match(/^(.*?)(\d+)$/)
  return m ? { base:m[1], num:parseInt(m[2]), len:m[2].length } : { base:raw, num:0, len:0 }
}
function genUnames(base, count) {
  const info = parseUnameBase(base)
  const names = []
  for (let i = 0; i < count; i++) {
    names.push(info.len > 0 ? info.base + String(info.num + i).padStart(info.len, '0') : base)
  }
  return names
}

// ====== Card 1: Mmeett注册用户 ======
const reg = reactive({ mset:'regist', uname:'', rcode:'', country:'3630979328926013', pwd:'qq123456', bemail:'yes', paypwd:'123123', unum:1, env:'test', results:[], loading:false })
function onRegTab() {}
function resetReg() { Object.assign(reg, { mset:'regist', uname:'', rcode:'', country:'3630979328926013', pwd:'qq123456', bemail:'yes', paypwd:'123123', unum:1, env:'test', results:[] }) }
async function submitReg() {
  if (reg.mset==='regist' && (!reg.uname || !reg.rcode)) { alert('必填项不能为空！'); return }
  reg.loading = true; reg.results = []
  const unames = genUnames(reg.uname, parseInt(reg.unum))
  for (let i = 0; i < unames.length; i++) {
    reg.results.unshift(`<span style="color:#999">第${i+1}条 [${unames[i]}] 请求中...</span>`)
    try {
      const r = await http.post('/ov/pmmeett/mmeettRegist', { mset:reg.mset, uname:unames[i], rcode:reg.rcode, pwd:reg.pwd, repwd:reg.pwd, country:reg.country, bemail:reg.bemail, paypwd:reg.paypwd, unum:1, env:reg.env, version:7, emailSuffix, type:'mmeettRegist' })
      if (r.data?.code >= 500) { reg.results[0] = `<span style="color:red">第${i+1}条 [${unames[i]}] 服务端异常 (code=${r.data.code})</span>`; break }
      reg.results[0] = r.data?.data || '完成'
    } catch(e) { reg.results[0] = `<span style="color:red">第${i+1}条 [${unames[i]}] 失败: ${e.message||e}</span>`; break }
  }
  reg.loading = false
}

// ====== Card 2: 余额购买会员 ======
const buy = reactive({ uname:'', level:'', unum:1, env:'test', results:[], loading:false, levels:[], rcinfo:null })
function resetBuy() { Object.assign(buy, { uname:'', level:'', unum:1, env:'test', results:[], levels:[] }); }
function getRechargeConfig() {
  if (!buy.uname) { buy.levels = []; return }
  http.post('/ov/pmmeett/getRechargeConfig', { uname:buy.uname, env:buy.env, version:7, emailSuffix, type:'getRechargeConfig' })
    .then(r => {
      const rcinfo = r.data?.data
      if (r.data?.code == 0 && rcinfo?.length) {
        buy.rcinfo = rcinfo
        const order = [30,1,3,35,39,43,47,5,45,41,33,7,9,37]
        buy.levels = order.map(id => rcinfo.find(x => x.id === id)).filter(Boolean)
      } else if (r.data?.code == -15) {
        alert((r.data?.msg||'') + '【本系统仅支持默认密码为 qq123456 的用户操作!】')
      } else {
        alert('用户已是钻石会员，请先降级再购买！')
      }
    }).catch(() => {})
}
async function submitBuy() {
  if (!buy.uname) { alert('用户账号不能为空！'); return }
  if (!buy.level) { alert('请选择会员类型！'); return }
  buy.loading = true; buy.results = []
  const unames = genUnames(buy.uname, parseInt(buy.unum))
  for (let i = 0; i < unames.length; i++) {
    buy.results.unshift(`<span style="color:#999">第${i+1}条 [${unames[i]}] 请求中...</span>`)
    try {
      const r = await http.post('/ov/pmmeett/buyVip', { rcinfo:buy.rcinfo, uname:unames[i], level:buy.level, unum:1, env:buy.env, version:7, emailSuffix, type:'buyVip' })
      buy.results[0] = r.data?.data || '完成'
    } catch(e) { buy.results[0] = `<span style="color:red">第${i+1}条 失败: ${e.message||e}</span>` }
  }
  buy.loading = false
}

// ====== Card 3: 生成邀请链路 ======
const ref = reactive({ uname:'', rcode:'', country:'3630979328926013', level:'3', unum:1, env:'test', results:[], loading:false })
function resetRef() { Object.assign(ref, { uname:'', rcode:'', country:'3630979328926013', level:'3', unum:1, env:'test', results:[] }) }
function queryRCode() {
  if (!ref.uname) return
  http.post('/ov/pmmeett/queryRCode', { uname:ref.uname, env:ref.env, version:7, emailSuffix, type:'queryRCode' })
    .then(r => {
      const d = r.data?.data
      if (d) {
        ref.rcode = d.rcode || ''
        const cm = {'TW':'3630979328926013','JP':'3630979328926009','ID':'3630979328925988','TH':'3630979328926003','SG':'3630979328925990','MY':'3630979328925992'}
        ref.country = cm[d.country] || ''
      }
    }).catch(() => {})
}
async function submitRef() {
  if (!ref.uname) { alert('用户账号不能为空！'); return }
  ref.loading = true; ref.results = []
  const unames = genUnames(ref.uname, parseInt(ref.unum))
  for (let i = 0; i < unames.length; i++) {
    ref.results.unshift(`<span style="color:#999">第${i+1}条 [${unames[i]}] 请求中...</span>`)
    try {
      const r = await http.post('/ov/pmmeett/mmeettAddReferralLinks', { uname:unames[i], rcode:ref.rcode, country:ref.country, level:ref.level, unum:1, env:ref.env, version:7, emailSuffix, type:'mmeettAddReferralLinks' })
      ref.results[0] = r.data?.data || '完成'
    } catch(e) { ref.results[0] = `<span style="color:red">第${i+1}条 失败: ${e.message||e}</span>` }
  }
  ref.loading = false
}

// ====== Card 4: 修改配置 ======
const cfg = reactive({ uname:'', userName:'', userEmail:'', country:'', env:'test', result:'', loading:false })
function resetCfg() { Object.assign(cfg, { uname:'', userName:'', userEmail:'', country:'', env:'test', result:'' }) }
function queryUser(type) {
  if (!cfg.uname) { alert('请输入用户账号！'); return }
  const actionMap = { userName:'queryUserName', userEmail:'queryUserEmail', country:'queryRCode' }
  http.post('/ov/pmmeett/' + actionMap[type], { uname:cfg.uname, env:cfg.env, version:7, emailSuffix })
    .then(r => {
      const d = r.data?.data
      if (type==='userName' && d?.userName) cfg.userName = d.userName
      else if (type==='userEmail' && d?.email) cfg.userEmail = d.email
      else if (type==='country' && d?.country) {
        const cm = {'TW':'3630979328926013','JP':'3630979328926009','ID':'3630979328925988','TH':'3630979328926003','SG':'3630979328925990','MY':'3630979328925992'}
        cfg.country = cm[d.country] || ''
        loadCountries()
      }
    }).catch(() => {})
}
function submitCfg() {
  if (!cfg.uname) { alert('用户账号不能为空！'); return }
  cfg.loading = true; cfg.result = ''
  http.post('/ov/pmmeett/updateUserInfo', { uname:cfg.uname, userName:cfg.userName, userEmail:cfg.userEmail, country:cfg.country, env:cfg.env, version:7, emailSuffix, type:'updateUserInfo' })
    .then(r => { cfg.result = r.data?.data || '' }).catch(() => { cfg.result = '请求失败' }).finally(() => { cfg.loading = false })
}

// ====== Card 5: 分成奖励重跑 ======
const rewardTypeList = [{v:'27',l:'感恩分红奖'},{v:'28',l:'推荐奖'},{v:'29',l:'分享奖'},{v:'30',l:'安置奖'},{v:'31',l:'层碰奖'},{v:'32',l:'级差奖'},{v:'33',l:'级差对等奖'},{v:'35',l:'全球分红'},{v:'43',l:'集团奖励分红'}]
const reward = reactive({ pre:false, detail:true, summary:true, types:[], allTypes:false, weekly:true, monthly:false, dateRange:null, env:'test', results:[], loading:false })
function onRewardAllChange(v) { reward.types = v ? rewardTypeList.map(r=>r.v) : [] }
function resetReward() {
  Object.assign(reward, { pre:false, detail:true, summary:true, types:[], allTypes:false, weekly:true, monthly:false, env:'test', results:[] })
  setDefaultDates()
}
function setDefaultDates() {
  const now = new Date(), y = now.getFullYear(), m = now.getMonth(), d = now.getDate()
  let s, e
  if (d<=7) { s=1; e=7 } else if (d<=14) { s=8; e=14 } else if (d<=21) { s=15; e=21 } else { s=22; e=new Date(y,m+1,0).getDate() }
  const fmt = (dt) => `${dt.getFullYear()}-${String(dt.getMonth()+1).padStart(2,'0')}-${String(dt.getDate()).padStart(2,'0')}`
  reward.dateRange = [fmt(new Date(y,m,s)), fmt(new Date(y,m,e))]
}
async function submitReward() {
  if (!reward.types.length) { alert('请选择奖励类型！'); return }
  const [startTime, endTime] = reward.dateRange || []
  if (!startTime || !endTime) { alert('请选择时间范围！'); return }
  reward.loading = true; reward.results = []
  const typeNames = Object.fromEntries(rewardTypeList.map(r=>[r.v,r.l]))
  const sendTypes = (rt) => rt==='43' ? ['summary'] : [reward.pre&&'pre', reward.detail&&'detail', reward.summary&&'summary'].filter(Boolean)
  const rerunMode = reward.types.includes('43') ? [reward.weekly&&'1', reward.monthly&&'2'].filter(Boolean) : []
  for (let i = 0; i < reward.types.length; i++) {
    const rt = reward.types[i]
    reward.results.unshift(`<span style="color:#999">第${i+1}条 [${typeNames[rt]}] 请求中...</span>`)
    try {
      const r = await http.post('/ov/pmmeett/runReward', { uname:'', rewardType:rt, startTime, endTime, env:reward.env, types:sendTypes(rt), rerunMode, version:7, emailSuffix, type:'runReward' })
      reward.results[0] = r.data?.data || '完成'
    } catch(e) { reward.results[0] = `<span style="color:red">第${i+1}条 失败: ${e.message||e}</span>` }
  }
  reward.loading = false
}

// ====== Card 6: 算力充值/扣减 ======
const power = reactive({ op:'recharge', uname:'', computingType:'', computingNum:'', sendAward:'0', env:'test', unameD:'', deductNum:'', envD:'test', result:'', loading:false })
function resetPower() { Object.assign(power, { op:'recharge', uname:'', computingType:'', computingNum:'', sendAward:'0', env:'test', unameD:'', deductNum:'', envD:'test', result:'' }) }
function submitPower() {
  power.loading = true; power.result = ''
  if (power.op === 'recharge') {
    if (!power.uname) { alert('请输入用户账号！'); power.loading=false; return }
    if (!power.computingType) { alert('请选择充值类型！'); power.loading=false; return }
    http.post('/ov/pmmeett/sendComputing', { computingNames, ccntlist:computingList, uname:power.uname, computingType:power.computingType, computingNum:power.computingNum, sendAward:power.sendAward, env:power.env, version:7, emailSuffix, type:'sendComputing' })
      .then(r => { power.result = r.data?.data || '' }).catch(() => { power.result='请求失败' }).finally(() => { power.loading=false })
  } else {
    if (!power.unameD) { alert('请输入用户账号！'); power.loading=false; return }
    if (!power.deductNum) { alert('请输入算力数值！'); power.loading=false; return }
    http.post('/ov/pmmeett/computingConsumption', { uname:power.unameD, amount:power.deductNum, env:power.envD, version:7, emailSuffix, type:'computingConsumption' })
      .then(r => { power.result = r.data?.data || '' }).catch(() => { power.result='请求失败' }).finally(() => { power.loading=false })
  }
}

// ====== Card 7: 用户安置 ======
const settle = reactive({ type:'place', uname:'', cancelDir:'all', isBatch:'1', env:'test', results:[], loading:false, checkResult:'' })
function onSettleTab() { settle.checkResult = '' }
function resetSettle() { Object.assign(settle, { type:'place', uname:'', cancelDir:'all', isBatch:'1', env:'test', results:[], checkResult:'' }) }
function getTree(gtype) {
  if (!settle.uname) { alert('请先输入用户账号！'); return }
  if (gtype === 'issettle') {
    http.post('/ov/pmmeett/issettle', { uname:settle.uname, emailSuffix, env:settle.env, version:7, type:gtype })
      .then(r => { settle.checkResult = r.data?.data || '' }).catch(() => {})
  } else {
    window.open(`/ov/mmeettTreeView?uname=${encodeURIComponent(settle.uname)}&env=${settle.env}&version=7&emailSuffix=${encodeURIComponent(emailSuffix)}&_plain=1`, '_blank')
  }
}
async function submitSettle() {
  if (!settle.uname) { alert('用户账号不能为空！'); return }
  settle.loading = true; settle.results = []
  if (settle.type === 'cancel') {
    settle.results.push(`<span style="color:#999">[${settle.uname}] 请求中...</span>`)
    try {
      const r = await http.post('/ov/pmmeett/userCancelSettle', { uname:settle.uname, env:settle.env, version:7, settleType:settle.type, cancelDirs:settle.cancelDir, emailSuffix, type:'userCancelSettle' })
      settle.results[0] = r.data?.data || '完成'
    } catch(e) { settle.results[0] = `<span style="color:red">失败: ${e.message||e}</span>` }
  } else if (settle.isBatch === '1') {
    const unames = genUnames(settle.uname, 1000)
    let notFound = 0
    for (let i = 0; i < unames.length; i++) {
      settle.results.unshift(`<span style="color:#999">第${i+1}条 [${unames[i]}] 请求中...</span>`)
      try {
        const r = await http.post('/ov/pmmeett/userSettle', { uname:unames[i], isBatch:settle.isBatch, idx:i+1, env:settle.env, version:7, emailSuffix, type:'userSettle' })
        const res = r.data?.data || {}
        settle.results[0] = res.usrlt || '完成'
        if (res.usrlt?.includes('不存在')) { notFound++; if (notFound >= 3) { settle.results.unshift('<span style="color:#999">连续3次用户不存在，已停止</span>'); break } } else { notFound = 0 }
        if (res.stop == 1) { settle.results.unshift('<span style="color:#999">已停止</span>'); break }
      } catch(e) { settle.results[0] = `<span style="color:red">第${i+1}条 失败: ${e.message||e}</span>` }
    }
  } else {
    settle.results.push(`<span style="color:#999">[${settle.uname}] 请求中...</span>`)
    try {
      const r = await http.post('/ov/pmmeett/userSettle', { uname:settle.uname, isBatch:settle.isBatch, env:settle.env, version:7, emailSuffix, type:'userSettle' })
      settle.results[0] = r.data?.data?.usrlt || '完成'
    } catch(e) { settle.results[0] = `<span style="color:red">失败: ${e.message||e}</span>` }
  }
  settle.loading = false
}

// ====== Card 8: 会员降级 ======
const sv = reactive({ uname:'', level:0, env:'test', result:'', loading:false })
function resetSv() { Object.assign(sv, { uname:'', level:0, env:'test', result:'' }) }
function submitSv() {
  if (!sv.uname) { alert('用户账号不能为空！'); return }
  sv.loading = true; sv.result = ''
  http.post('/ov/pmmeett/demotionVip', { uname:sv.uname, level:sv.level, env:sv.env, version:7, emailSuffix, type:'demotionVip' })
    .then(r => { sv.result = r.data?.data || '' }).catch(() => { sv.result='请求失败' }).finally(() => { sv.loading=false })
}

// ====== Card 9: 赠送点位 ======
const gift = reactive({ uname:'', level:'', amount:1, expire:'', env:'test', result:'', loading:false })
function resetGift() { Object.assign(gift, { uname:'', level:'', amount:1, expire:'', env:'test', result:'' }) }
function submitGift() {
  if (!gift.uname) { alert('用户账号不能为空！'); return }
  if (!gift.level) { alert('等级不能为空！'); return }
  gift.loading = true; gift.result = ''
  http.post('/ov/pmmeett/assetChange', { uname:gift.uname, level:gift.level, amount:gift.amount, expire:gift.expire, env:gift.env, version:7, emailSuffix, type:'giftPoints' })
    .then(r => { gift.result = r.data?.data || '' }).catch(() => { gift.result='请求失败' }).finally(() => { gift.loading=false })
}

// ====== Card 10: 账户充值/扣减 ======
const account = reactive({ uname:'', amount:'', env:'test', result:'', loading:false })
function resetAccount() { Object.assign(account, { uname:'', amount:'', env:'test', result:'' }) }
function submitAccount() {
  if (!account.uname) { alert('请输入用户账号！'); return }
  if (!account.amount) { alert('请输入金额！'); return }
  account.loading = true; account.result = ''
  http.post('/ov/pmmeett/assetChange', { uname:account.uname, state:'1', camount:account.amount, env:account.env, version:7, emailSuffix, type:'assetChange' })
    .then(r => { account.result = r.data?.data || '' }).catch(() => { account.result='请求失败' }).finally(() => { account.loading=false })
}

// ====== Card: 用户注销 ======
const del = reactive({ account:'', pwd:'qq123456', num:1, env:'test', result:'', loading:false })
function resetDel() { Object.assign(del, { account:'', pwd:'qq123456', num:1, env:'test', result:'' }) }
function submitDel() {
  if (!del.account) { del.result = '<span style="color:red">请输入账号</span>'; return }
  const accounts = genUnames(del.account, parseInt(del.num))
  if (!confirm(`确定要注销 ${accounts.length} 个账号吗？（${del.env==='prod'?'生产':'测试'}环境）此操作不可逆！`)) return
  del.loading = true; del.result = ''
  http.post('/ov/pmmeett/delAccount', { account:accounts[0], accounts, pwd:del.pwd, env:del.env, version:7, type:'delAccount' })
    .then(r => {
      if (r.data?.code == '0') del.result = `✅ ${r.data?.data || '注销成功'}`
      else del.result = `<span style="color:red">❌ 注销失败: ${r.data?.msg||'未知错误'}</span>`
    }).catch(e => { del.result = `<span style="color:red">❌ 请求异常: ${e.message||e}</span>` }).finally(() => { del.loading=false })
}

onMounted(() => { setDefaultDates() })
</script>

<style scoped>
.mo-page { display:flex; flex-direction:column; height:100%; overflow:hidden; }
.mo-body { display:flex; flex-direction:row; gap:12px; padding:0 10px; height:calc(100% - 30px); overflow:hidden; }
.column { display:flex; flex-direction:column; gap:12px; flex:1; min-width:280px; overflow-y:auto; height:100%; padding-top:4px; }
.column::-webkit-scrollbar { width:5px; }
.column::-webkit-scrollbar-thumb { background:#c0c0c0; border-radius:10px; }

:deep(.card) { background:#fff; border-radius:14px; box-shadow:0 2px 12px rgba(0,0,0,.08); overflow:hidden; flex-shrink:0; border:1px solid #e9e9e9; }
:deep(.card-header) { display:flex; justify-content:space-between; align-items:center; padding:12px 20px; cursor:pointer; background:#f0f2f5; border-bottom:1px solid #f0f0f0; user-select:none; }
:deep(.card-header:hover) { background:#fafafa; }
:deep(.card-header h1) { margin:0; font-size:15px; font-weight:600; color:#1a1a1a; }
:deep(.card.collapsed .card-body) { max-height:0; padding:0 16px; opacity:0; overflow:hidden; }
:deep(.card-body) { padding:12px 16px; display:flex; flex-direction:column; align-items:center; max-height:800px; transition:max-height .3s,padding .3s,opacity .3s; opacity:1; }
.ct { font-size:12px; color:#666; transition:transform .3s; }
.card.collapsed .ct { transform:rotate(-90deg); }

.fg { display:grid; grid-template-columns:max-content 180px; column-gap:8px; row-gap:8px; align-items:center; }
.fgr { display:contents; }
.fgr label { text-align:right; white-space:nowrap; }
.rq { color:red; }
.fgi { display:flex; justify-content:center; align-items:center; gap:8px; margin-bottom:8px; }

:deep(.env-group) { display:flex; justify-content:center; gap:20px; margin:10px 0; }
:deep(.env-group label) { cursor:pointer; display:inline-flex; align-items:center; gap:4px; padding:5px 16px; border-radius:9999px; border:1px solid #d1d5db; background:#fff; font-size:13px; transition:all .15s; user-select:none; }
:deep(.env-group label.active) { background:#6366f1; color:#fff; border-color:#6366f1; }
:deep(.env-group input[type="radio"]) { display:none; }

:deep(.btn-group) { display:flex; justify-content:center; gap:15px; margin-bottom:15px; }
.result { flex:1; padding:10px; border-radius:8px; overflow-y:auto; font-size:14px; text-align:center; width:100%; word-wrap:break-word; word-break:break-all; white-space:pre-wrap; color:#444; line-height:1.8; }

:deep(.tab-group) { display:flex; justify-content:center; gap:6px; margin-bottom:15px; padding:4px; background:#f0f2f5; border-radius:10px; }
:deep(.tab-group label) { cursor:pointer; margin:0; display:flex; }
:deep(.tab-group .tab-item) { padding:7px 20px; background:transparent; color:#555; border:none; border-radius:8px; font-size:14px; font-weight:500; transition:all .25s; }
:deep(.tab-group label.active .tab-item) { background:#fff; color:#6366f1; box-shadow:0 1px 4px rgba(0,0,0,.1); font-weight:600; }
:deep(.tab-group input[type="radio"]) { display:none; }

.radio-group { margin-bottom:15px; display:flex; gap:6px; justify-content:center; flex-wrap:wrap; align-items:center; }
.radio-group label { display:inline-flex; align-items:center; gap:5px; padding:5px 14px; border:1px solid #d9d9d9; border-radius:14px; font-size:13px; cursor:pointer; user-select:none; background:#fff; }
.radio-group label.active { background:#6366f1; color:#fff; border-color:#6366f1; }
.radio-group input[type="radio"] { accent-color:#6366f1; }

.checkbox-group { margin-bottom:15px; display:flex; gap:8px; justify-content:center; flex-wrap:wrap; }
.cb-grid { display:grid; grid-template-columns:repeat(3,auto); gap:4px 12px; justify-content:center; padding:10px 16px; border:1px solid #d9d9d9; border-radius:6px; position:relative; margin-bottom:12px; }
.grid-title { position:absolute; top:-10px; left:12px; background:#fff; padding:0 6px; font-size:13px; font-weight:500; white-space:nowrap; }
</style>
