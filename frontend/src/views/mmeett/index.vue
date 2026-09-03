<template>
  <div class="mo-page">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title"><i class="fa-solid fa-layer-group"></i> Mmeett 开户 & 配置</h2>
      </div>
      <div class="toolbar-right">
        <span class="suffix-label">邮箱后缀</span>
        <el-input v-model="emailSuffix" size="small" style="width:130px" />
      </div>
    </div>

    <div class="mo-body">
      <!-- 第一列 -->
      <div class="column">
        <!-- 卡片1: Mmeett注册用户 -->
        <div :class="['m-card', {collapsed:!cards.reg}]">
          <div class="m-card-hd accent-blue" @click="cards.reg=!cards.reg">
            <div class="m-card-hd-left">
              <i class="fa-solid fa-user-plus card-icon"></i>
              <h3>Mmeett注册用户</h3>
            </div>
            <i :class="['fa-solid fa-chevron-right chevron', {open:cards.reg}]"></i>
          </div>
          <div class="m-card-bd">
            <TabGroup :tabs="[{v:'regist',l:'用户注册'},{v:'bemaspp',l:'绑定邮箱&设置支付密码'}]" v-model="reg.mset" @change="onRegTab" />
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span>用户账号</label><el-input v-model="reg.uname" placeholder="输入用户账号" /></div>
              <div v-if="reg.mset==='regist'" class="fgr"><label><span class="rq">*</span>邀请码</label><el-input v-model="reg.rcode" placeholder="输入邀请码" /></div>
              <div v-if="reg.mset==='regist'" class="fgr"><label><span class="rq">*</span>国家/地区</label><el-select v-model="reg.country" @focus="loadCountries"><el-option v-for="c in countryList" :key="c.value" :label="c.name" :value="c.value" /></el-select></div>
              <div class="fgr"><label><span class="rq">*</span>登录密码</label><el-input v-model="reg.pwd" /></div>
              <div v-if="reg.mset==='regist' && reg.env==='test'" class="fgr"><label><span class="rq">*</span>绑定邮箱</label><el-select v-model="reg.bemail"><el-option label="是" value="yes" /><el-option label="否" value="no" /></el-select></div>
              <div v-if="reg.mset==='regist' && reg.env==='test'" class="fgr"><label><span class="rq">*</span>支付密码</label><el-input v-model="reg.paypwd" /></div>
              <div class="fgr"><label><span class="rq">*</span>账号数量</label><el-input v-model="reg.unum" type="number" /></div>
            </div>
            <EnvRadio v-model="reg.env" name="reg-env" />
            <BtnGroup @reset="resetReg" @submit="submitReg" />
            <ResultBox :lines="reg.results" :loading="reg.loading" />
          </div>
        </div>

        <!-- 卡片4: 修改国家/地区 | 用户名 | 用户邮箱 -->
        <div :class="['m-card', {collapsed:!cards.cfg}]">
          <div class="m-card-hd accent-orange" @click="cards.cfg=!cards.cfg">
            <div class="m-card-hd-left">
              <i class="fa-solid fa-pen-to-square card-icon"></i>
              <h3>修改用户信息</h3>
            </div>
            <i :class="['fa-solid fa-chevron-right chevron', {open:cards.cfg}]"></i>
          </div>
          <div class="m-card-bd">
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span>用户账号</label><el-input v-model="cfg.uname" /></div>
              <div class="fgr"><label>用户名</label>
                <div class="input-with-btn"><el-input v-model="cfg.userName" /><el-button size="small" @click="queryUser('userName')" title="查询用户名"><i class="fa-solid fa-user"></i></el-button></div></div>
              <div class="fgr"><label>用户邮箱</label>
                <div class="input-with-btn"><el-input v-model="cfg.userEmail" /><el-button size="small" @click="queryUser('userEmail')" title="查询用户邮箱"><i class="fa-solid fa-envelope"></i></el-button></div></div>
              <div class="fgr"><label>国家/地区</label>
                <div class="input-with-btn"><el-select v-model="cfg.country" @focus="loadCountries"><el-option label="--请选择--" value="" /><el-option v-for="c in countryList" :key="c.value" :label="c.name" :value="c.value" /></el-select><el-button size="small" @click="queryUser('country')" title="查询注册国家"><i class="fa-solid fa-earth-americas"></i></el-button></div></div>
            </div>
            <EnvRadio v-model="cfg.env" name="cfg-env" />
            <BtnGroup @reset="resetCfg" @submit="submitCfg" />
            <ResultBox :text="cfg.result" :loading="cfg.loading" />
          </div>
        </div>

        <!-- 卡片7: 用户安置 -->
        <div :class="['m-card', {collapsed:!cards.settle}]">
          <div class="m-card-hd accent-green" @click="cards.settle=!cards.settle">
            <div class="m-card-hd-left">
              <i class="fa-solid fa-sitemap card-icon"></i>
              <h3>用户安置</h3>
            </div>
            <i :class="['fa-solid fa-chevron-right chevron', {open:cards.settle}]"></i>
          </div>
          <div class="m-card-bd">
            <TabGroup :tabs="[{v:'place',l:'安置'},{v:'cancel',l:'取消安置'}]" v-model="settle.type" @change="onSettleTab" />
            <div v-if="settle.type==='cancel'" class="pill-group">
              <span class="pill-label"><span class="rq">*</span>取消方向</span>
              <div class="pill-options">
                <label v-for="d in [{v:'all',l:'全部'},{v:'up',l:'上级'},{v:'down',l:'下级'}]" :key="d.v" :class="{active:settle.cancelDir===d.v}"><input type="radio" :value="d.v" v-model="settle.cancelDir" />{{ d.l }}</label>
              </div>
            </div>
            <div class="fgi"><label><span class="rq">*</span>用户账号</label><el-input v-model="settle.uname" style="width:140px" />
              <el-button size="small" text type="primary" @click="getTree('gettree')">查看树形结构</el-button>
              <el-button size="small" text type="primary" @click="getTree('issettle')">是否被安置</el-button>
            </div>
            <div v-if="settle.checkResult" class="check-result">{{ settle.checkResult }}</div>
            <div v-if="settle.type==='place'" class="pill-group">
              <span class="pill-label"><span class="rq">*</span>是否批量</span>
              <div class="pill-options">
                <label :class="{active:settle.isBatch==='1'}"><input type="radio" value="1" v-model="settle.isBatch" />是</label>
                <label :class="{active:settle.isBatch==='0'}"><input type="radio" value="0" v-model="settle.isBatch" />否</label>
              </div>
            </div>
            <EnvRadio v-model="settle.env" name="settle-env" />
            <BtnGroup @reset="resetSettle" @submit="submitSettle" />
            <ResultBox :lines="settle.results" :loading="settle.loading" />
          </div>
        </div>

        <!-- 卡片9: 赠送点位 -->
        <div :class="['m-card', {collapsed:!cards.gift}]">
          <div class="m-card-hd accent-purple" @click="cards.gift=!cards.gift">
            <div class="m-card-hd-left">
              <i class="fa-solid fa-gift card-icon"></i>
              <h3>赠送点位</h3>
            </div>
            <i :class="['fa-solid fa-chevron-right chevron', {open:cards.gift}]"></i>
          </div>
          <div class="m-card-bd">
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span>用户账号</label><el-input v-model="gift.uname" /></div>
              <div class="fgr"><label><span class="rq">*</span>会员等级</label>
                <el-select v-model="gift.level" placeholder="--请选择--">
                  <el-option label="尊享" value="-1" /><el-option label="银级" value="3" /><el-option label="金级" value="1" /><el-option label="白金" value="2" /><el-option label="钻石" value="4" />
                </el-select></div>
              <div class="fgr"><label><span class="rq">*</span>会员数量</label><el-input v-model="gift.amount" type="number" /></div>
              <div class="fgr"><label><span class="rq">*</span>有效天数</label><el-input v-model="gift.expire" type="number" /></div>
            </div>
            <EnvRadio v-model="gift.env" name="gift-env" />
            <BtnGroup @reset="resetGift" @submit="submitGift" />
            <ResultBox :text="gift.result" :loading="gift.loading" />
          </div>
        </div>
      </div>

      <!-- 第二列 -->
      <div class="column">
        <!-- 卡片2: Mmeett余额购买会员 -->
        <div :class="['m-card', {collapsed:!cards.buy}]">
          <div class="m-card-hd accent-blue" @click="cards.buy=!cards.buy">
            <div class="m-card-hd-left">
              <i class="fa-solid fa-crown card-icon"></i>
              <h3>余额购买会员</h3>
            </div>
            <i :class="['fa-solid fa-chevron-right chevron', {open:cards.buy}]"></i>
          </div>
          <div class="m-card-bd">
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span>用户账号</label><el-input v-model="buy.uname" @blur="getRechargeConfig" /></div>
              <div class="fgr"><label><span class="rq">*</span>会员类型</label><el-select v-model="buy.level" placeholder="--请选择--"><el-option v-for="l in buy.levels" :key="l.id" :label="l.name" :value="l.id" /></el-select></div>
              <div class="fgr"><label><span class="rq">*</span>账号数量</label><el-input v-model="buy.unum" type="number" /></div>
            </div>
            <EnvRadio v-model="buy.env" name="buy-env" />
            <div class="hint-text">注：相同会员类型可批量执行，反之仅可单个执行。</div>
            <BtnGroup @reset="resetBuy" @submit="submitBuy" />
            <ResultBox :lines="buy.results" :loading="buy.loading" />
          </div>
        </div>

        <!-- 卡片8: 会员降级 -->
        <div :class="['m-card', {collapsed:!cards.sv}]">
          <div class="m-card-hd accent-orange" @click="cards.sv=!cards.sv">
            <div class="m-card-hd-left">
              <i class="fa-solid fa-arrow-down-long card-icon"></i>
              <h3>会员降级</h3>
            </div>
            <i :class="['fa-solid fa-chevron-right chevron', {open:cards.sv}]"></i>
          </div>
          <div class="m-card-bd">
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span>用户账号</label><el-input v-model="sv.uname" /></div>
              <div class="fgr"><label><span class="rq">*</span>会员等级</label>
                <el-select v-model="sv.level"><el-option label="非会员" :value="0" /><el-option label="银级" :value="3" /><el-option label="金级" :value="1" /><el-option label="白金" :value="2" /></el-select></div>
            </div>
            <EnvRadio v-model="sv.env" name="sv-env" />
            <BtnGroup @reset="resetSv" @submit="submitSv" />
            <ResultBox :text="sv.result" :loading="sv.loading" />
          </div>
        </div>

        <!-- 卡片5: 分成奖励重跑 -->
        <div :class="['m-card', {collapsed:!cards.reward}]">
          <div class="m-card-hd accent-green" @click="cards.reward=!cards.reward">
            <div class="m-card-hd-left">
              <i class="fa-solid fa-rotate card-icon"></i>
              <h3>分成奖励重跑</h3>
            </div>
            <i :class="['fa-solid fa-chevron-right chevron', {open:cards.reward}]"></i>
          </div>
          <div class="m-card-bd">
            <div class="section-label">结算类型</div>
            <div class="checkbox-group">
              <el-checkbox v-model="reward.pre">预结算</el-checkbox>
              <el-checkbox v-model="reward.detail">明细</el-checkbox>
              <el-checkbox v-model="reward.summary">汇总</el-checkbox>
            </div>
            <div class="section-label">奖励类型 <el-checkbox v-model="reward.allTypes" @change="onRewardAllChange" class="select-all-cb">全选</el-checkbox></div>
            <div class="cb-grid">
              <el-checkbox v-for="rt in rewardTypeList" :key="rt.v" :label="rt.l" :value="rt.v" v-model="reward.types" />
            </div>
            <div v-if="reward.types.includes('43')" class="checkbox-group" style="margin-top:4px">
              <span class="section-label" style="margin:0">集团奖励模式</span>
              <el-checkbox v-model="reward.weekly">周结</el-checkbox>
              <el-checkbox v-model="reward.monthly">月结</el-checkbox>
            </div>
            <div class="fgi">
              <label><span class="rq">*</span>时间范围</label>
              <el-date-picker v-model="reward.dateRange" type="daterange" start-placeholder="开始" end-placeholder="结束" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width:240px" />
            </div>
            <EnvRadio v-model="reward.env" name="reward-env" />
            <BtnGroup @reset="resetReward" @submit="submitReward" />
            <ResultBox :lines="reward.results" :loading="reward.loading" />
          </div>
        </div>

        <!-- 用户注销 -->
        <div :class="['m-card', {collapsed:!cards.del}]">
          <div class="m-card-hd accent-red" @click="cards.del=!cards.del">
            <div class="m-card-hd-left">
              <i class="fa-solid fa-user-slash card-icon"></i>
              <h3>用户注销</h3>
            </div>
            <i :class="['fa-solid fa-chevron-right chevron', {open:cards.del}]"></i>
          </div>
          <div class="m-card-bd">
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span>账号</label><el-input v-model="del.account" placeholder="输入账号" /></div>
              <div class="fgr"><label><span class="rq">*</span>密码</label><el-input v-model="del.pwd" /></div>
              <div class="fgr"><label><span class="rq">*</span>数量</label><el-input v-model="del.num" type="number" :min="1" :max="10000" /></div>
            </div>
            <EnvRadio v-model="del.env" name="del-env" />
            <BtnGroup @reset="resetDel" @submit="submitDel" />
            <ResultBox :text="del.result" :loading="del.loading" />
          </div>
        </div>
      </div>

      <!-- 第三列 -->
      <div class="column">
        <!-- 卡片3: Mmeett生成邀请链路 -->
        <div :class="['m-card', {collapsed:!cards.ref}]">
          <div class="m-card-hd accent-blue" @click="cards.ref=!cards.ref">
            <div class="m-card-hd-left">
              <i class="fa-solid fa-link card-icon"></i>
              <h3>生成邀请链路</h3>
            </div>
            <i :class="['fa-solid fa-chevron-right chevron', {open:cards.ref}]"></i>
          </div>
          <div class="m-card-bd">
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span>用户账号</label><el-input v-model="ref.uname" @blur="queryRCode" /></div>
              <div class="fgr"><label><span class="rq">*</span>邀请码</label><el-input v-model="ref.rcode" /></div>
              <div class="fgr"><label><span class="rq">*</span>国家/地区</label><el-select v-model="ref.country" @focus="loadCountries"><el-option v-for="c in countryList" :key="c.value" :label="c.name" :value="c.value" /></el-select></div>
              <div class="fgr"><label><span class="rq">*</span>会员类型</label>
                <el-select v-model="ref.level"><el-option label="银级" value="3" /><el-option label="金级" value="1" /><el-option label="白金" value="2" /><el-option label="钻石" value="4" /></el-select></div>
              <div class="fgr"><label><span class="rq">*</span>账号数量</label><el-input v-model="ref.unum" type="number" /></div>
            </div>
            <EnvRadio v-model="ref.env" name="ref-env" />
            <BtnGroup @reset="resetRef" @submit="submitRef" />
            <ResultBox :lines="ref.results" :loading="ref.loading" />
          </div>
        </div>

        <!-- 卡片6: 算力充值/扣减 -->
        <div :class="['m-card', {collapsed:!cards.power}]">
          <div class="m-card-hd accent-purple" @click="cards.power=!cards.power">
            <div class="m-card-hd-left">
              <i class="fa-solid fa-bolt card-icon"></i>
              <h3>算力充值 / 扣减</h3>
            </div>
            <i :class="['fa-solid fa-chevron-right chevron', {open:cards.power}]"></i>
          </div>
          <div class="m-card-bd">
            <TabGroup :tabs="[{v:'recharge',l:'充值'},{v:'deduct',l:'扣减'}]" v-model="power.op" />
            <template v-if="power.op==='recharge'">
              <div class="fg">
                <div class="fgr"><label><span class="rq">*</span>用户账号</label><el-input v-model="power.uname" /></div>
                <div class="fgr"><label><span class="rq">*</span>充值类型</label><el-select v-model="power.computingType" placeholder="--请选择--" @focus="loadComputing"><el-option v-for="c in computingList" :key="c.value" :label="c.name" :value="c.value" /></el-select></div>
                <div v-if="power.computingType==='0'" class="fgr"><label><span class="rq">*</span>算力数值</label><el-input v-model="power.computingNum" type="number" placeholder="请输入算力数值" /></div>
                <div class="fgr"><label><span class="rq">*</span>是否分佣</label><el-select v-model="power.sendAward"><el-option label="是" value="1" /><el-option label="否" value="0" /></el-select></div>
              </div>
              <EnvRadio v-model="power.env" name="power-env" />
            </template>
            <template v-else>
              <div class="fg">
                <div class="fgr"><label><span class="rq">*</span>用户账号</label><el-input v-model="power.unameD" /></div>
                <div class="fgr"><label><span class="rq">*</span>算力数值</label><el-input v-model="power.deductNum" type="number" placeholder="请输入扣减算力数值" /></div>
              </div>
              <EnvRadio v-model="power.envD" name="power-envD" />
            </template>
            <BtnGroup @reset="resetPower" @submit="submitPower" />
            <ResultBox :text="power.result" :loading="power.loading" />
          </div>
        </div>

        <!-- 卡片10: 账户充值/扣减 -->
        <div :class="['m-card', {collapsed:!cards.account}]">
          <div class="m-card-hd accent-purple" @click="cards.account=!cards.account">
            <div class="m-card-hd-left">
              <i class="fa-solid fa-wallet card-icon"></i>
              <h3>账户充值 / 扣减</h3>
            </div>
            <i :class="['fa-solid fa-chevron-right chevron', {open:cards.account}]"></i>
          </div>
          <div class="m-card-bd">
            <TabGroup :tabs="[{v:'1',l:'充值'},{v:'0',l:'扣减'}]" v-model="account.state" />
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span>用户账号</label><el-input v-model="account.uname" /></div>
              <div class="fgr"><label><span class="rq">*</span>金额</label><el-input v-model="account.amount" type="number" placeholder="请输入金额" /></div>
            </div>
            <EnvRadio v-model="account.env" name="account-env" />
            <BtnGroup @reset="resetAccount" @submit="submitAccount" />
            <ResultBox :text="account.result" :loading="account.loading" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import http from '../../api/http.js'

// --- Inline sub-components ---
const EnvRadio = {
  props: ['modelValue','name'], emits:['update:modelValue'],
  template:`<div class="env-group"><div class="env-track"><label :class="{active:modelValue==='test'}"><input type="radio" :name="name" value="test" :checked="modelValue==='test'" @change="$emit('update:modelValue','test')"/><i class="fa-solid fa-flask"></i> 测试环境</label><label :class="{active:modelValue==='prod'}"><input type="radio" :name="name" value="prod" :checked="modelValue==='prod'" @change="$emit('update:modelValue','prod')"/><i class="fa-solid fa-server"></i> 生产环境</label></div></div>`,
}
const BtnGroup = { emits:['reset','submit'], template:`<div class="btn-group"><el-button class="btn-reset" @click="$emit('reset')">重置</el-button><el-button class="btn-submit" type="primary" @click="$emit('submit')">提交</el-button></div>` }
const ResultBox = {
  props:['text','lines','loading'],
  template:`<div class="result"><span v-if="loading" class="result-loading"><i class="fa-solid fa-spinner fa-spin"></i> 处理中...</span><template v-else-if="lines&&lines.length"><div v-for="(l,i) in lines" :key="i" class="result-line" v-html="l"></div></template><span v-else v-html="text||''"></span></div>`,
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
    reg.results.unshift(`<span class="rl-pending">第${i+1}条 [${unames[i]}] 请求中...</span>`)
    try {
      const r = await http.post('/ov/pmmeett/mmeettRegist', { mset:reg.mset, uname:unames[i], rcode:reg.rcode, pwd:reg.pwd, repwd:reg.pwd, country:reg.country, bemail:reg.bemail, paypwd:reg.paypwd, unum:1, env:reg.env, version:7, emailSuffix, type:'mmeettRegist' })
      if (r.data?.code >= 500) { reg.results[0] = `<span class="rl-error">第${i+1}条 [${unames[i]}] 服务端异常 (code=${r.data.code})</span>`; break }
      reg.results[0] = r.data?.data || '完成'
    } catch(e) { reg.results[0] = `<span class="rl-error">第${i+1}条 [${unames[i]}] 失败: ${e.message||e}</span>`; break }
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
    buy.results.unshift(`<span class="rl-pending">第${i+1}条 [${unames[i]}] 请求中...</span>`)
    try {
      const r = await http.post('/ov/pmmeett/buyVip', { rcinfo:buy.rcinfo, uname:unames[i], level:buy.level, unum:1, env:buy.env, version:7, emailSuffix, type:'buyVip' })
      buy.results[0] = r.data?.data || '完成'
    } catch(e) { buy.results[0] = `<span class="rl-error">第${i+1}条 失败: ${e.message||e}</span>` }
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
    ref.results.unshift(`<span class="rl-pending">第${i+1}条 [${unames[i]}] 请求中...</span>`)
    try {
      const r = await http.post('/ov/pmmeett/mmeettAddReferralLinks', { uname:unames[i], rcode:ref.rcode, country:ref.country, level:ref.level, unum:1, env:ref.env, version:7, emailSuffix, type:'mmeettAddReferralLinks' })
      ref.results[0] = r.data?.data || '完成'
    } catch(e) { ref.results[0] = `<span class="rl-error">第${i+1}条 失败: ${e.message||e}</span>` }
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
    reward.results.unshift(`<span class="rl-pending">第${i+1}条 [${typeNames[rt]}] 请求中...</span>`)
    try {
      const r = await http.post('/ov/pmmeett/runReward', { uname:'', rewardType:rt, startTime, endTime, env:reward.env, types:sendTypes(rt), rerunMode, version:7, emailSuffix, type:'runReward' })
      reward.results[0] = r.data?.data || '完成'
    } catch(e) { reward.results[0] = `<span class="rl-error">第${i+1}条 失败: ${e.message||e}</span>` }
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
    settle.results.push(`<span class="rl-pending">[${settle.uname}] 请求中...</span>`)
    try {
      const r = await http.post('/ov/pmmeett/userCancelSettle', { uname:settle.uname, env:settle.env, version:7, settleType:settle.type, cancelDirs:settle.cancelDir, emailSuffix, type:'userCancelSettle' })
      settle.results[0] = r.data?.data || '完成'
    } catch(e) { settle.results[0] = `<span class="rl-error">失败: ${e.message||e}</span>` }
  } else if (settle.isBatch === '1') {
    const unames = genUnames(settle.uname, 1000)
    let notFound = 0
    for (let i = 0; i < unames.length; i++) {
      settle.results.unshift(`<span class="rl-pending">第${i+1}条 [${unames[i]}] 请求中...</span>`)
      try {
        const r = await http.post('/ov/pmmeett/userSettle', { uname:unames[i], isBatch:settle.isBatch, idx:i+1, env:settle.env, version:7, emailSuffix, type:'userSettle' })
        const res = r.data?.data || {}
        settle.results[0] = res.usrlt || '完成'
        if (res.usrlt?.includes('不存在')) { notFound++; if (notFound >= 3) { settle.results.unshift('<span class="rl-info">连续3次用户不存在，已停止</span>'); break } } else { notFound = 0 }
        if (res.stop == 1) { settle.results.unshift('<span class="rl-info">已停止</span>'); break }
      } catch(e) { settle.results[0] = `<span class="rl-error">第${i+1}条 失败: ${e.message||e}</span>` }
    }
  } else {
    settle.results.push(`<span class="rl-pending">[${settle.uname}] 请求中...</span>`)
    try {
      const r = await http.post('/ov/pmmeett/userSettle', { uname:settle.uname, isBatch:settle.isBatch, env:settle.env, version:7, emailSuffix, type:'userSettle' })
      settle.results[0] = r.data?.data?.usrlt || '完成'
    } catch(e) { settle.results[0] = `<span class="rl-error">失败: ${e.message||e}</span>` }
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
const account = reactive({ uname:'', amount:'', state:'1', env:'test', result:'', loading:false })
function resetAccount() { Object.assign(account, { uname:'', amount:'', state:'1', env:'test', result:'' }) }
function submitAccount() {
  if (!account.uname) { alert('请输入用户账号！'); return }
  if (!account.amount) { alert('请输入金额！'); return }
  const typeLabel = account.state === '1' ? '充值' : '扣减'
  if (!confirm(`确认对用户「${account.uname}」进行「${typeLabel}」操作，金额：${account.amount}？`)) return
  account.loading = true; account.result = ''
  http.post('/ov/pmmeett/assetChange', { uname:account.uname, state:account.state, camount:account.amount, env:account.env, version:7, emailSuffix, type:'assetChange' })
    .then(r => { account.result = r.data?.data || '' }).catch(() => { account.result='请求失败' }).finally(() => { account.loading=false })
}

// ====== Card: 用户注销 ======
const del = reactive({ account:'', pwd:'qq123456', num:1, env:'test', result:'', loading:false })
function resetDel() { Object.assign(del, { account:'', pwd:'qq123456', num:1, env:'test', result:'' }) }
function submitDel() {
  if (!del.account) { del.result = '<span class="rl-error">请输入账号</span>'; return }
  const accounts = genUnames(del.account, parseInt(del.num))
  if (!confirm(`确定要注销 ${accounts.length} 个账号吗？（${del.env==='prod'?'生产':'测试'}环境）此操作不可逆！`)) return
  del.loading = true; del.result = ''
  http.post('/ov/pmmeett/delAccount', { account:accounts[0], accounts, pwd:del.pwd, env:del.env, version:7, type:'delAccount' })
    .then(r => {
      if (r.data?.code == '0') del.result = `<span class="rl-ok">✅ ${r.data?.data || '注销成功'}</span>`
      else del.result = `<span class="rl-error">❌ 注销失败: ${r.data?.msg||'未知错误'}</span>`
    }).catch(e => { del.result = `<span class="rl-error">❌ 请求异常: ${e.message||e}</span>` }).finally(() => { del.loading=false })
}

onMounted(() => { setDefaultDates() })
</script>

<style scoped>
/* ===================== 页面骨架 ===================== */
.mo-page { display:flex; flex-direction:column; height:100%; overflow:hidden; background:#f5f6fa; }

.toolbar {
  display:flex; justify-content:space-between; align-items:center;
  padding:12px 20px 8px; flex-shrink:0;
}
.toolbar-left { display:flex; align-items:center; gap:8px; }
.page-title { margin:0; font-size:16px; font-weight:700; color:#1e293b; letter-spacing:.3px; }
.page-title i { color:#6366f1; margin-right:4px; }
.toolbar-right { display:flex; align-items:center; gap:8px; }
.suffix-label { font-size:12px; color:#94a3b8; white-space:nowrap; }

.mo-body { display:flex; gap:14px; padding:0 14px 14px; height:calc(100% - 48px); overflow:hidden; }
.column { display:flex; flex-direction:column; gap:12px; flex:1; min-width:300px; overflow-y:auto; height:100%; padding:2px; }
.column::-webkit-scrollbar { width:4px; }
.column::-webkit-scrollbar-track { background:transparent; }
.column::-webkit-scrollbar-thumb { background:#cbd5e1; border-radius:4px; }
.column::-webkit-scrollbar-thumb:hover { background:#94a3b8; }

/* ===================== 卡片 ===================== */
.m-card {
  background:#fff; border-radius:12px; flex-shrink:0;
  box-shadow:0 1px 3px rgba(0,0,0,.06), 0 1px 2px rgba(0,0,0,.04);
  overflow:hidden; transition:box-shadow .2s;
}
.m-card:hover { box-shadow:0 4px 12px rgba(0,0,0,.08), 0 2px 4px rgba(0,0,0,.04); }

/* 卡片头 */
.m-card-hd {
  display:flex; justify-content:space-between; align-items:center;
  padding:14px 18px; cursor:pointer; user-select:none;
  border-left:4px solid transparent; transition:background .15s;
}
.m-card-hd:hover { background:#fafbfc; }
.m-card-hd-left { display:flex; align-items:center; gap:10px; }
.card-icon { font-size:15px; width:18px; text-align:center; }
.m-card-hd h3 { margin:0; font-size:14px; font-weight:600; color:#1e293b; letter-spacing:.2px; }

/* 折叠箭头 */
.chevron { font-size:11px; color:#94a3b8; transition:transform .25s ease; }
.chevron.open { transform:rotate(90deg); }

/* 折叠状态 */
.m-card.collapsed .m-card-bd { max-height:0; padding-top:0; padding-bottom:0; opacity:0; overflow:hidden; }
.m-card-bd {
  padding:16px 18px; display:flex; flex-direction:column; align-items:center;
  max-height:800px; transition:max-height .3s ease, padding .3s ease, opacity .25s; opacity:1;
  border-top:1px solid #f1f5f9;
}

/* 色彩主题：左侧竖条 */
.accent-blue  { border-left-color:#3b82f6; }  .accent-blue  .card-icon { color:#3b82f6; }
.accent-green { border-left-color:#22c55e; }  .accent-green .card-icon { color:#22c55e; }
.accent-orange{ border-left-color:#f59e0b; }  .accent-orange .card-icon { color:#f59e0b; }
.accent-purple{ border-left-color:#8b5cf6; }  .accent-purple .card-icon { color:#8b5cf6; }
.accent-red   { border-left-color:#ef4444; }  .accent-red   .card-icon { color:#ef4444; }

/* ===================== 表单 Grid ===================== */
.fg { display:grid; grid-template-columns:auto 1fr; column-gap:10px; row-gap:10px; align-items:center; width:100%; }
.fgr { display:contents; }
.fgr label { text-align:right; white-space:nowrap; font-size:13px; color:#475569; }
.fgr :deep(.el-input), .fgr :deep(.el-select) { width:100% !important; }
.rq { color:#ef4444; margin-right:2px; }

.fgi { display:flex; justify-content:center; align-items:center; gap:8px; margin-bottom:8px; width:100%; }

.input-with-btn { display:flex; gap:4px; width:100%; }
.input-with-btn :deep(.el-input), .input-with-btn :deep(.el-select) { flex:1; }

/* ===================== 环境切换 ===================== */
:deep(.env-group) { display:flex; justify-content:center; margin:14px 0 10px; width:100%; }
:deep(.env-track) { display:inline-flex; gap:0; background:#f1f5f9; border-radius:8px; padding:3px; }
:deep(.env-track label) {
  cursor:pointer; display:inline-flex; align-items:center; gap:5px;
  padding:6px 16px; border-radius:6px; border:none; background:transparent;
  font-size:12px; font-weight:500; color:#64748b; transition:all .2s; user-select:none;
}
:deep(.env-track label.active) { background:#fff; color:#6366f1; box-shadow:0 1px 3px rgba(0,0,0,.1); font-weight:600; }
:deep(.env-track label i) { font-size:11px; }
:deep(.env-track input[type="radio"]) { display:none; }

/* ===================== 按钮 ===================== */
:deep(.btn-group) { display:flex; justify-content:center; gap:12px; margin:10px 0 12px; width:100%; }
:deep(.btn-reset) { min-width:72px; }
:deep(.btn-submit) { min-width:72px; }

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
:deep(.result-line) { padding:4px 0; border-bottom:1px solid #e2e8f0; }
:deep(.result-line:last-child) { border-bottom:none; }
:deep(.rl-pending) { color:#94a3b8; }
:deep(.rl-error)   { color:#ef4444; }
:deep(.rl-ok)      { color:#22c55e; font-weight:500; }
:deep(.rl-info)    { color:#3b82f6; }

/* ===================== Tab 切换 ===================== */
:deep(.tab-group) { display:flex; justify-content:center; gap:0; margin-bottom:14px; background:#f1f5f9; border-radius:8px; padding:3px; width:100%; }
:deep(.tab-group label) { cursor:pointer; margin:0; display:flex; flex:1; justify-content:center; }
:deep(.tab-group .tab-item) { padding:7px 20px; background:transparent; color:#64748b; border:none; border-radius:6px; font-size:13px; font-weight:500; transition:all .2s; }
:deep(.tab-group label.active .tab-item) { background:#fff; color:#6366f1; box-shadow:0 1px 3px rgba(0,0,0,.08); font-weight:600; }
:deep(.tab-group input[type="radio"]) { display:none; }

/* ===================== Pill 选项组 ===================== */
.pill-group { display:flex; align-items:center; gap:8px; margin-bottom:12px; width:100%; justify-content:center; flex-wrap:wrap; }
.pill-label { font-size:13px; color:#475569; white-space:nowrap; }
.pill-options { display:inline-flex; gap:0; background:#f1f5f9; border-radius:6px; padding:2px; }
.pill-options label {
  cursor:pointer; display:inline-flex; align-items:center; gap:4px;
  padding:5px 12px; border-radius:5px; font-size:12px; color:#64748b;
  transition:all .15s; user-select:none;
}
.pill-options label.active { background:#fff; color:#6366f1; box-shadow:0 1px 2px rgba(0,0,0,.06); font-weight:500; }
.pill-options input[type="radio"] { display:none; }

.check-result { color:#3b82f6; font-size:12px; margin:4px 0 8px; text-align:center; }

/* ===================== Checkbox 区 ===================== */
.checkbox-group { margin-bottom:10px; display:flex; gap:10px; justify-content:center; flex-wrap:wrap; }
.section-label { font-size:12px; font-weight:600; color:#64748b; text-transform:uppercase; letter-spacing:.5px; margin-bottom:8px; text-align:center; width:100%; display:flex; align-items:center; justify-content:center; gap:8px; }
.select-all-cb { font-size:12px !important; font-weight:400 !important; text-transform:none !important; letter-spacing:0 !important; }
.cb-grid { display:grid; grid-template-columns:repeat(3,auto); gap:6px 16px; justify-content:center; padding:10px 16px; border:1px solid #e2e8f0; border-radius:8px; margin-bottom:10px; width:100%; box-sizing:border-box; background:#fafbfc; }

/* ===================== 提示文字 ===================== */
.hint-text { color:#f59e0b; font-size:12px; text-align:center; margin:4px 0 8px; }
</style>
