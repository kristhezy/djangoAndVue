<template>
  <div class="mo-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title"><i class="fa-solid fa-user-minus"></i> 删除线索/合伙人</h2>
      </div>
    </div>

    <div class="mo-body">
      <div class="column">
        <!-- 卡片1: 删除线索/合伙人 -->
        <div :class="['m-card', {collapsed:!cards.c1}]">
          <div class="m-card-hd accent-red" @click="cards.c1=!cards.c1">
            <div class="m-card-hd-left"><i class="fa-solid fa-user-minus card-icon"></i><h3>删除线索/合伙人</h3></div>
            <i :class="['fa-solid fa-chevron-right chevron', {open:cards.c1}]"></i>
          </div>
          <div class="m-card-bd">
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span>企业 ID</label><el-input v-model="form1.companyName" placeholder="请输入企业ID" /></div>
              <div class="fgr"><label><span class="rq">*</span>企业名称</label>
                <el-select v-model="form1.companyId" placeholder="输入企业ID" style="width:100%" @change="onCompanyChange">
                  <el-option label="输入企业ID" value="" />
                  <el-option-group label="🔽【prod】">
                    <el-option v-for="c in companies.prod" :key="c.id" :label="c.name" :value="c.id" />
                  </el-option-group>
                  <el-option-group label="🔽【test】">
                    <el-option v-for="c in companies.test" :key="c.id" :label="c.name" :value="c.id" />
                  </el-option-group>
                </el-select>
              </div>
              <div class="fgr"><label><span class="rq">*</span>用户 ID</label><el-input v-model="form1.userId" /></div>
              <div class="fgr"><label>合伙人 ID</label><el-input v-model="form1.ppidcontent" :disabled="form1.delcheck !== 'delpartner'" /></div>
            </div>
            <div class="radio-row">
              <div class="tab-group">
                <label :class="{active:form1.delcheck==='delclue'}"><input type="radio" name="dc1" value="delclue" :checked="form1.delcheck==='delclue'" @change="form1.delcheck='delclue'"/><span>删除线索</span></label>
                <label :class="{active:form1.delcheck==='delpartner'}"><input type="radio" name="dc1" value="delpartner" :checked="form1.delcheck==='delpartner'" @change="form1.delcheck='delpartner'"/><span>删除合伙人</span></label>
              </div>
            </div>
            <EnvRadio v-model="form1.env" name="env1" :disabled="envLocked" />
            <BtnGroup @reset="resetForm1" @submit="cleanClue" :loading="loading1" />
            <div class="warn-note">※ 删除合伙人时:【先删除合伙人，再删除线索数据】</div>
            <div class="result">{{ result1 }}</div>
          </div>
        </div>

        <!-- 卡片2: 根据手机号查询用户ID -->
        <div :class="['m-card', {collapsed:!cards.c2}]">
          <div class="m-card-hd accent-blue" @click="cards.c2=!cards.c2">
            <div class="m-card-hd-left"><i class="fa-solid fa-magnifying-glass card-icon"></i><h3>手机号查询用户ID</h3></div>
            <i :class="['fa-solid fa-chevron-right chevron', {open:cards.c2}]"></i>
          </div>
          <div class="m-card-bd">
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span>企业 ID</label><el-input v-model="form2.cid" /></div>
              <div class="fgr"><label><span class="rq">*</span>手机号</label><el-input v-model="form2.tel" maxlength="11" /></div>
            </div>
            <EnvRadio v-model="form2.env" name="env2" />
            <BtnGroup @reset="resetForm2" @submit="queryByCp" submit-text="查询" :loading="loading2" />
            <div class="result">{{ result2 }}</div>
          </div>
        </div>

        <!-- 卡片3: 销售添加线索 -->
        <div :class="['m-card', {collapsed:!cards.c3}]">
          <div class="m-card-hd accent-green" @click="cards.c3=!cards.c3">
            <div class="m-card-hd-left"><i class="fa-solid fa-user-plus card-icon"></i><h3>销售添加线索</h3></div>
            <i :class="['fa-solid fa-chevron-right chevron', {open:cards.c3}]"></i>
          </div>
          <div class="m-card-bd">
            <div class="fg">
              <div class="fgr"><label><span class="rq">*</span>企业 ID</label><el-input v-model="form3.companyId" /></div>
              <div class="fgr"><label><span class="rq">*</span>员工 ID</label><el-input v-model="form3.cardId" /></div>
              <div class="fgr"><label><span class="rq">*</span>用户姓名</label><el-input v-model="form3.userName" /></div>
              <div class="fgr"><label><span class="rq">*</span>用户手机</label><el-input v-model="form3.userTel" maxlength="11" /></div>
              <div class="fgr"><label>合伙人 ID</label><el-input v-model="form3.pId" /></div>
              <div class="fgr"><label>是否批量</label>
                <div style="display:flex;align-items:center;gap:8px;">
                  <el-checkbox v-model="form3.batch" />
                  <el-input v-model="form3.batchNum" :disabled="!form3.batch" placeholder="2~1000" style="width:100px" />
                </div>
              </div>
            </div>
            <EnvRadio v-model="form3.env" name="env3" />
            <BtnGroup @reset="resetForm3" @submit="addClue" :loading="loading3" />
            <div class="result">{{ result3 }}</div>
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

// --- Inline sub-components ---
const EnvRadio = {
  props: ['modelValue', 'name', 'disabled'], emits: ['update:modelValue'],
  template: `<div class="env-group"><div class="env-track"><label :class="{active:modelValue==='test'}"><i class="fa-solid fa-flask"></i><input type="radio" :name="name" value="test" :checked="modelValue==='test'" :disabled="disabled" @change="$emit('update:modelValue','test')"/><span>测试环境</span></label><label :class="{active:modelValue==='prod'}"><i class="fa-solid fa-rocket"></i><input type="radio" :name="name" value="prod" :checked="modelValue==='prod'" :disabled="disabled" @change="$emit('update:modelValue','prod')"/><span>生产环境</span></label></div></div>`,
}
const BtnGroup = {
  props: ['loading', 'submitText'],
  emits: ['reset', 'submit'],
  template: `<div class="btn-group"><el-button @click="$emit('reset')">重置</el-button><el-button type="primary" :loading="loading" @click="$emit('submit')">{{ submitText || '提交' }}</el-button></div>`,
}

const companies = {
  prod: [
    { id: '1021060956165488640', name: '招商版小程序测试企业1' },
    { id: '839508475783573504', name: '加推（测试）' },
    { id: '1040268843043500032', name: '超级推广部' },
    { id: '1012037449188364288', name: '深圳灰度测试企业5' },
    { id: '532972735412850688', name: '铁岭县供销合作社联合社' },
    { id: '1069929980139683840', name: '深圳市加推科技有限公司' },
    { id: '1189258248478707712', name: '红蚂蚁测试企业1' },
    { id: '1189258337557340160', name: '点石测试企业1' },
    { id: '1192136192859492352', name: '红蚂蚁装饰股份有限公司' },
    { id: '693225071459762176', name: '石家庄七度文化传播有限公司' },
    { id: '844635664262787073', name: '石家庄七度文化传播有限公司转介绍' },
  ],
  test: [
    { id: '1017368198385172480', name: '招商版测试企业7' },
    { id: '755550234976985088', name: '百度（中国）有限公司' },
    { id: '1035144123776442368', name: '招商版小程序测试企业8' },
    { id: '846400679986987008', name: '云盘版转介绍3' },
    { id: '870366245806292992', name: '北京积木世纪教育科技' },
    { id: '874593368431542272', name: '深圳市兴光电子有限公司' },
    { id: '1181172541784809472', name: '红蚂蚁家装' },
    { id: '1185152155297222656', name: '点石家装' },
  ],
}

const cards = reactive({ c1: true, c2: true, c3: true })
const envLocked = ref(false)

const form1 = reactive({ companyName: '', companyId: '', userId: '', ppidcontent: '', delcheck: 'delclue', env: 'prod' })
const form2 = reactive({ cid: '', tel: '', env: 'prod' })
const form3 = reactive({ companyId: '', cardId: '', userName: '', userTel: '', pId: '', batch: false, batchNum: '', env: 'prod' })
const result1 = ref(''), result2 = ref(''), result3 = ref('')
const loading1 = ref(false), loading2 = ref(false), loading3 = ref(false)

function onCompanyChange(val) {
  if (val === '') {
    form1.companyName = ''; form1.env = 'test'; form2.env = 'test'; envLocked.value = false
  } else {
    form1.companyName = val; form2.cid = val
    const isProd = companies.prod.some(c => c.id === val)
    form1.env = isProd ? 'prod' : 'test'; form2.env = isProd ? 'prod' : 'test'; envLocked.value = true
  }
}

async function cleanClue() {
  const compid = form1.companyName || form1.companyId
  if (!compid) { ElMessage.warning('请先选择企业！'); return }
  if (!form1.userId) { ElMessage.warning('用户ID不能为空！'); return }
  if (form1.delcheck === 'delpartner' && !form1.ppidcontent) { ElMessage.warning('合伙人ID不能为空！'); return }
  loading1.value = true
  try {
    const resp = await http.post('/sv/delclueinfo', { companyId: compid, userId: form1.userId, ppc: form1.ppidcontent, delcheck: form1.delcheck, env: form1.env, check: 'del' })
    result1.value = resp.data?.data || ''
  } catch (e) { result1.value = ''; ElMessage.error('删除失败：' + (e?.response?.data?.msg || e.message)) }
  finally { loading1.value = false }
}

async function queryByCp() {
  const { cid, tel } = form2
  if (cid.length < 18 || isNaN(cid)) { ElMessage.warning('企业ID只能是大于等于18位的纯数字！'); return }
  if (tel.length !== 11 || isNaN(tel)) { ElMessage.warning('手机号只能为11位纯数字！'); return }
  loading2.value = true
  try {
    const resp = await http.post('/sv/queryuibycp', { cid, tel, env: form2.env })
    const d = resp.data?.data
    if (d) {
      result2.value = d.partnerId ? `userId: ${d.userId}, partnerId: ${d.partnerId}` : `userId: ${d.userId}`
      form1.userId = d.userId || ''; form1.ppidcontent = d.partnerId || ''
    }
  } catch (e) { result2.value = ''; ElMessage.error('查询失败：' + (e?.response?.data?.msg || e.message)) }
  finally { loading2.value = false }
}

async function addClue() {
  const { companyId, cardId, userName, userTel, pId, batch, batchNum, env } = form3
  let bn = 1
  if (batch) {
    if (!batchNum || isNaN(batchNum) || batchNum <= 1 || batchNum > 1000) { ElMessage.warning('批量数为[2~1000]之间的整数！'); return }
    bn = batchNum
  }
  if (!companyId || !cardId || !userName || !userTel) { ElMessage.warning('必填项不能为空！'); return }
  if (companyId.length < 18 || companyId.length > 19 || isNaN(companyId)) { ElMessage.warning('企业ID只能是18或19位的纯数字！'); return }
  if (userTel.length !== 11 || isNaN(userTel)) { ElMessage.warning('手机号只能是11位的纯数字！'); return }
  loading3.value = true
  try {
    const resp = await http.post('/sv/saci', { cid: companyId, cardid: cardId, uname: userName, utel: userTel, bn, pId, env })
    result3.value = resp.data?.data || ''
  } catch (e) { result3.value = ''; ElMessage.error('添加失败：' + (e?.response?.data?.msg || e.message)) }
  finally { loading3.value = false }
}

function resetForm1() { form1.companyName = ''; form1.companyId = ''; form1.userId = ''; form1.ppidcontent = ''; form1.delcheck = 'delclue'; form1.env = 'prod'; envLocked.value = false; result1.value = '' }
function resetForm2() { form2.cid = ''; form2.tel = ''; form2.env = 'prod'; result2.value = '' }
function resetForm3() { form3.companyId = ''; form3.cardId = ''; form3.userName = ''; form3.userTel = ''; form3.pId = ''; form3.batch = false; form3.batchNum = ''; form3.env = 'prod'; result3.value = '' }
</script>

<style scoped>
/* ===================== 页面骨架 ===================== */
.mo-page { display:flex; flex-direction:column; height:100%; overflow:hidden; background:var(--bg-page); }
.toolbar { display:flex; justify-content:space-between; align-items:center; padding:12px 20px 8px; flex-shrink:0; }
.toolbar-left { display:flex; align-items:center; gap:8px; }
.page-title { margin:0; font-size:16px; font-weight:700; color:var(--text-primary); letter-spacing:.3px; }
.page-title i { color:var(--color-primary-light); margin-right:4px; }

.mo-body { flex:1; padding:0 14px 14px; overflow-y:auto; }
.mo-body::-webkit-scrollbar { width:4px; }
.mo-body::-webkit-scrollbar-track { background:transparent; }
.mo-body::-webkit-scrollbar-thumb { background:var(--scrollbar-thumb); border-radius:4px; }
.column { columns:3; column-gap:12px; }

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
.accent-red   { border-left-color:#ef4444; }  .accent-red   .card-icon { color:#ef4444; }

/* ===================== 表单 Grid ===================== */
.fg { display:grid; grid-template-columns:auto 300px; column-gap:10px; row-gap:10px; align-items:center; width:fit-content; margin:0 auto; }
.fgr { display:contents; }
.fgr label { text-align:left; white-space:nowrap; font-size:13px; color:var(--text-secondary); }
.fgr :deep(.el-input), .fgr :deep(.el-select) { width:100% !important; }
.rq { color:#ef4444; margin-right:2px; }

/* ===================== 单选行 ===================== */
.radio-row { display:flex; justify-content:center; margin:10px 0 6px; }
:deep(.tab-group) { display:inline-flex; gap:0; background:var(--bg-hover); border-radius:6px; padding:2px; flex-wrap:nowrap; }
:deep(.tab-group label) {
  cursor:pointer; display:inline-flex; align-items:center; gap:4px;
  padding:5px 14px; border-radius:5px; border:none; background:transparent;
  font-size:12px; font-weight:500; color:var(--text-muted); transition:all .2s;
  user-select:none; white-space:nowrap;
}
:deep(.tab-group label.active) { background:var(--bg-card); color:var(--color-primary-light); box-shadow:0 1px 3px rgba(0,0,0,.1); font-weight:600; }
:deep(.tab-group input[type="radio"]) { display:none; }

/* ===================== 环境切换 ===================== */
:deep(.env-group) { display:inline-flex; justify-content:center; margin:10px auto 6px; }
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
:deep(.env-track input[type="radio"]:disabled + span) { opacity:.5; }

/* ===================== 按钮 ===================== */
:deep(.btn-group) { display:flex; justify-content:center; gap:12px; margin:8px 0 10px; }

/* ===================== 结果区 ===================== */
.result {
  width:100%; min-height:24px; max-height:140px; overflow-y:auto;
  padding:8px 12px; border-radius:8px; background:var(--bg-subtle);
  font-size:13px; text-align:center; line-height:1.7; color:var(--text-secondary);
  white-space:pre-wrap; word-break:break-all;
}
.result:empty { display:none; }

/* ===================== 警告提示 ===================== */
.warn-note { font-size:12px; color:#ef4444; text-align:center; margin:4px 0 6px; }
</style>
