<template>
  <div class="mo-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title"><i class="fa-solid fa-mobile-screen"></i> 小程序发版管理</h2>
      </div>
    </div>

    <div class="mo-body">
      <!-- 左栏：操作卡片 -->
      <div class="left-col">
        <!-- 查询企业信息 -->
        <div class="m-card">
          <div class="m-card-hd accent-blue">
            <div class="m-card-hd-left"><i class="fa-solid fa-magnifying-glass card-icon"></i>
              <h3>查询企业信息</h3>
            </div>
            <el-button text size="small" @click="resetLeft">重置</el-button>
          </div>
          <div class="m-card-bd">
            <div class="mp-query">
              <el-input v-model="loginName" placeholder="输入登录手机号或企业ID" :disabled="loading"
                @keyup.enter="queryCompany" />
              <el-button type="primary" :loading="loading" :disabled="loading" @click="queryCompany">查询</el-button>
            </div>
            <div class="mp-cinfo">
              <div v-if="cid">
                <div>企业名称: {{ cn }}</div>
                <div>企业ID: {{ cid }}</div>
                <div>appID: {{ appid }}</div>
              </div>
              <div v-else-if="queryError" style="color:#dc2626;">{{ queryError }}</div>
              <div v-else style="color:var(--text-placeholder);">未查询</div>
            </div>
          </div>
        </div>

        <!-- 提交前配置 -->
        <div class="m-card">
          <div class="m-card-hd accent-green">
            <div class="m-card-hd-left"><i class="fa-solid fa-sliders card-icon"></i>
              <h3>提交前配置</h3>
            </div>
          </div>
          <div class="m-card-bd">
            <el-checkbox-group v-model="tsq">
              <el-checkbox value="priv">隐私权限配置</el-checkbox>
              <el-checkbox value="ulcm">上传代码模板</el-checkbox>
              <el-checkbox value="addm">添加域名</el-checkbox>
            </el-checkbox-group>
            <div v-if="tsq.includes('ulcm')" class="mp-tpl">
              <label>代码模板：</label>
              <el-select v-model="templateId" placeholder="选择模板" style="flex:1;">
                <el-option v-for="t in templateList" :key="t.id" :label="t.label" :value="t.id" />
              </el-select>
            </div>
            <div v-if="tsq.includes('addm')" class="mp-domain">
              <label>业务域名：</label>
              <div class="mp-domain-tags">
                <el-tag v-for="(d, i) in customDomains" :key="i" closable @close="customDomains.splice(i, 1)"
                  type="info" class="mp-tag">{{ d }}</el-tag>
                <el-input v-if="domainInputVisible" ref="domainInputRef" v-model="domainInput" size="small"
                  style="width:200px;" placeholder="输入域名后回车" @keyup.enter="addDomain" @blur="addDomain" />
                <el-button v-else size="small" @click="showDomainInput">+ 添加域名</el-button>
              </div>
            </div>
            <BtnOnly text="提交" :loading="loading" :disabled="!cid" @submit="submitBaconfig" />
            <div v-if="tsqrlt" class="result">{{ tsqrlt }}</div>
          </div>
        </div>

        <!-- 审核/发布 -->
        <div class="m-card">
          <div class="m-card-hd accent-orange">
            <div class="m-card-hd-left"><i class="fa-solid fa-paper-plane card-icon"></i>
              <h3>审核/发布</h3>
            </div>
          </div>
          <div class="m-card-bd">
            <el-radio-group v-model="fts">
              <el-radio value="audit">提交审核</el-radio>
              <el-radio value="ads">查看审核结果</el-radio>
              <el-radio value="rls">发布小程序</el-radio>
              <el-radio value="ucaudit">撤回审核</el-radio>
            </el-radio-group>
            <BtnOnly text="提交" :loading="loading" :disabled="!cid" @submit="submitAuditRelease" />
            <div v-if="tsrlt" class="result">{{ tsrlt }}</div>
          </div>
        </div>

        <!-- 体验者管理 -->
        <div class="m-card">
          <div class="m-card-hd accent-purple">
            <div class="m-card-hd-left"><i class="fa-solid fa-user-plus card-icon"></i>
              <h3>体验者管理</h3>
            </div>
          </div>
          <div class="m-card-bd">
            <el-radio-group v-model="tyb">
              <el-radio value="bindtester">绑定体验者</el-radio>
              <el-radio value="unbindtester">解绑体验者</el-radio>
              <el-radio value="getqrcode">生成体验码</el-radio>
            </el-radio-group>
            <el-input v-if="tyb !== 'getqrcode'" v-model="wcid" placeholder="输入微信号" />
            <BtnOnly text="提交" :loading="loading" :disabled="!cid" @submit="submitTester" />
            <div v-if="tybrlt" class="result">
              <img v-if="tyb === 'getqrcode' && tybrlt.startsWith('/static/img/')" :src="tybrlt" height="180" />
              <template v-else>{{ tybrlt }}</template>
            </div>
          </div>
        </div>
      </div>

      <!-- 右栏：操作记录 -->
      <div class="right-col">
        <div class="m-card" style="height:100%;">
          <div class="m-card-hd accent-blue">
            <div class="m-card-hd-left"><i class="fa-solid fa-clock-rotate-left card-icon"></i>
              <h3>操作记录</h3>
            </div>
          </div>
          <div class="m-card-bd" style="align-items:stretch;">
            <div class="mp-search">
              <el-input v-model="qkey" placeholder="输入企业账号/ID/名称/appID查询" clearable @keydown.enter="searchRecords" />
              <el-button type="primary" @click="searchRecords">查询</el-button>
            </div>

            <el-table :data="records" stripe class="mp-table" v-loading="loadingRecords" @row-click="onRowClick"
              row-class-name="mp-clickable-row" empty-text="暂无数据">
              <el-table-column prop="phone" label="账号" min-width="110" />
              <el-table-column prop="companyName" label="企业名称" min-width="220" show-overflow-tooltip />
              <el-table-column prop="appId" label="appID" min-width="160" />
              <el-table-column prop="oContent" label="操作信息" min-width="220" show-overflow-tooltip />
              <el-table-column prop="uname" label="操作人" min-width="80" />
              <el-table-column prop="createTime" label="操作时间" min-width="160" />
            </el-table>

            <div class="mp-pagination">
              <span class="mp-stats">共 {{ totalRecords }} 条，第 {{ page }}/{{ totalPages }} 页</span>
              <el-pagination v-model:current-page="page" :page-size="pageSize" :total="totalRecords"
                layout="prev, pager, next, jumper" @current-change="loadRecords" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 提示对话框 -->
    <el-dialog v-model="showTips" title="提示" width="360px" :close-on-click-modal="false">
      <div style="text-align:center;">
        <div>请先配置业务域名的
          <el-button type="primary" plain size="small" :loading="loading" @click="downloadWdcFile">校验文件</el-button>
          ，并点击按钮去上传。
        </div>
        <div style="margin-top:16px;">
          <el-button type="primary" @click="openUploadPage">去上传</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const BtnOnly = {
  props: ['text', 'loading', 'disabled'],
  emits: ['submit'],
  template: `<div class="btn-only"><el-button type="primary" :loading="loading" :disabled="disabled" @click="$emit('submit')">{{ text || '提交' }}</el-button></div>`,
}

// 共享企业信息
const loginName = ref('')
const cid = ref('')
const cn = ref('')
const phone = ref('')
const appid = ref('')
const queryError = ref('')
const loading = ref(false)

// 提交前配置
const tsq = ref([])
const tsqrlt = ref('')

// 代码模板选择
const templateList = [
  { id: '510', label: 'v3.10.36 - 安卓兼容', version: 'v3.10.36', desc: '安卓兼容' },
  { id: '535', label: 'v4.3.0 - vr配置', version: 'v4.3.0', desc: 'vr配置' },
]
const templateId = ref('510')

// 自定义业务域名（Tag 输入）
const customDomains = ref([])
const domainInput = ref('')
const domainInputVisible = ref(false)
const domainInputRef = ref(null)
function showDomainInput() {
  domainInputVisible.value = true
  nextTick(() => { domainInputRef.value?.focus() })
}
function addDomain() {
  const d = domainInput.value.trim()
  if (d && !customDomains.value.includes(d)) {
    customDomains.value.push(d)
  }
  domainInput.value = ''
  domainInputVisible.value = false
}

// 审核/发布
const fts = ref('audit')
const tsrlt = ref('')

// 体验者管理
const tyb = ref('bindtester')
const wcid = ref('')
const tybrlt = ref('')

// 提示对话框
const showTips = ref(false)

// 操作记录
const qkey = ref('')
const records = ref([])
const loadingRecords = ref(false)
const page = ref(1)
const pageSize = ref(10)
const totalRecords = ref(0)
const totalPages = ref(1)

function resetLeft() {
  loginName.value = ''; cid.value = ''; cn.value = ''; phone.value = ''; appid.value = ''
  queryError.value = ''; tsq.value = []; tsqrlt.value = ''
  templateId.value = '535'; customDomains.value = []; domainInput.value = ''; domainInputVisible.value = false
  fts.value = 'audit'; tsrlt.value = ''
  tyb.value = 'bindtester'; wcid.value = ''; tybrlt.value = ''
}

async function queryCompany() {
  if (!loginName.value.trim()) { ElMessage.warning('请输入查询参数'); return }
  loading.value = true; queryError.value = ''
  try {
    const resp = await http.post('/sv/querycompid/saas', { ln: loginName.value, env: 'prod', cid: '', cn: '' })
    if (resp.data?.code == 0) {
      const d = resp.data.data
      cid.value = d.cid || ''; cn.value = d.cn || ''; phone.value = d.phone || ''
      try {
        const appResp = await http.post('/sv/getappid', { cid: cid.value, env: 'prod' })
        appid.value = appResp.data?.data?.appid || ''
      } catch (e) { console.error('getappid failed:', e) }
    } else { queryError.value = resp.data?.data || '查询失败' }
  } catch (e) { queryError.value = '查询失败' }
  finally { loading.value = false }
}

async function submitBaconfig() {
  if (!tsq.value.length) { ElMessage.warning('请勾选需要提交的内容！'); return }
  loading.value = true
  try {
    const tpl = templateList.find(t => t.id === templateId.value) || templateList[0]
    const resp = await http.post('/sv/miniprogramRelease/baconfig', {
      tsq: tsq.value.join(','), phone: phone.value, cid: cid.value, cn: cn.value, appid: appid.value, env: 'prod', type: 'baconfig',
      template_id: tpl.id, template_version: tpl.version, template_desc: tpl.desc,
      domains: customDomains.value,
    })
    tsqrlt.value = resp.data?.data?.rlt || ''
    if (resp.data?.data?.errtips) showTips.value = true
    loadRecords()
  } catch (e) { tsqrlt.value = '操作失败' }
  finally { loading.value = false }
}

async function submitAuditRelease() {
  if (!cid.value) { ElMessage.warning('企业信息不能为空！'); return }
  loading.value = true
  try {
    const resp = await http.post('/sv/miniprogramRelease/auditAndRelease', {
      ts: fts.value, phone: phone.value, cid: cid.value, cn: cn.value, appid: appid.value, env: 'prod', type: 'auditAndRelease',
    })
    tsrlt.value = resp.data?.data?.rlt || ''
    if (resp.data?.data?.errtips) showTips.value = true
    loadRecords()
  } catch (e) { tsrlt.value = '操作失败' }
  finally { loading.value = false }
}

async function submitTester() {
  if (!cid.value) { ElMessage.warning('企业信息不能为空！'); return }
  loading.value = true
  try {
    const resp = await http.post('/sv/miniprogramRelease/testerAndQrcode', {
      tyb: tyb.value, phone: phone.value, cid: cid.value, cn: cn.value, appid: appid.value, env: 'prod', type: 'testerAndQrcode', wcid: wcid.value,
    })
    if (tyb.value === 'getqrcode') { tybrlt.value = '/static/img/latest_img.jpg?t=' + Date.now() }
    else { tybrlt.value = resp.data?.data?.rlt || '' }
  } catch (e) { tybrlt.value = '操作失败' }
  finally { loading.value = false }
}

function openUploadPage() {
  window.open('https://dsa-app.aijiatui.com/upload.html', '_blank')
}

async function downloadWdcFile() {
  loading.value = true
  try {
    const resp = await http.post('/sv/miniprogramRelease/getwdcfile', {
      phone: phone.value, cid: cid.value, cn: cn.value, appid: appid.value, env: 'prod', type: 'getwdcfile',
    })
    if (resp.data?.code == 0) {
      const f = resp.data.data.rlt
      window.open(`/download/dynamic/?type=txt&name=${f.file_name}&content=${f.file_content}`, '_blank')
    } else { ElMessage.error(resp.data?.data || '下载失败') }
  } catch (e) { ElMessage.error('下载失败') }
  finally { loading.value = false }
}

function searchRecords() { page.value = 1; loadRecords() }

async function loadRecords() {
  loadingRecords.value = true
  try {
    const resp = await http.post('/sv/queryMiniprogramRecord/querympoc', { page: page.value, num: pageSize.value, qkey: qkey.value, type: 'querympoc' })
    const data = resp.data?.data?.oprationalInfo || []
    records.value = Array.isArray(data) ? data : []
    loadPagination()
  } catch (e) { records.value = [] }
  finally { loadingRecords.value = false }
}

async function loadPagination() {
  try {
    const resp = await http.post('/sv/queryMiniprogramRecord/querytp', { qkey: qkey.value, type: 'querytp' })
    totalRecords.value = parseInt(resp.data?.data?.total) || 0
    totalPages.value = Math.ceil(totalRecords.value / pageSize.value) || 1
  } catch (e) { totalRecords.value = 0; totalPages.value = 1 }
}

function onRowClick(row) {
  phone.value = row.phone || ''; cid.value = row.companyId || ''; cn.value = row.companyName || ''
  appid.value = row.appId || ''; loginName.value = phone.value; queryError.value = ''
}

onMounted(() => { loadRecords() })
</script>

<style scoped>
.mo-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background: var(--bg-page);
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
  color: var(--text-primary);
  letter-spacing: .3px;
}

.page-title i {
  color: var(--color-primary-light);
  margin-right: 4px;
}

.mo-body {
  flex: 1;
  padding: 0 14px 14px;
  overflow: hidden;
  display: flex;
  gap: 12px;
}

.left-col {
  width: 520px;
  min-width: 400px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.left-col::-webkit-scrollbar {
  width: 4px;
}

.left-col::-webkit-scrollbar-track {
  background: transparent;
}

.left-col::-webkit-scrollbar-thumb {
  background: var(--scrollbar-thumb);
  border-radius: 4px;
}

.right-col {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  display: flex;
}

.m-card {
  background: var(--bg-card);
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, .06), 0 1px 2px rgba(0, 0, 0, .04);
  overflow: hidden;
  transition: box-shadow .2s;
  width: 100%;
}

.m-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, .08), 0 2px 4px rgba(0, 0, 0, .04);
}

.m-card-hd {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  user-select: none;
  border-left: 4px solid transparent;
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
  color: var(--text-primary);
  letter-spacing: .2px;
}

.m-card-bd {
  padding: 16px 18px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  border-top: 1px solid var(--border-card);
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

.mp-query {
  display: flex;
  gap: 10px;
  align-items: center;
  width: 100%;
}

.mp-query .el-input {
  flex: 1;
}

.mp-tpl,
.mp-domain {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  width: 100%;
  font-size: 13px;
  color: var(--text-secondary);
}

.mp-tpl label,
.mp-domain label {
  white-space: nowrap;
  line-height: 32px;
}

.mp-domain-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
  flex: 1;
}

.mp-tag {
  font-size: 12px;
}

.mp-cinfo {
  width: 100%;
  min-height: 72px;
  padding: 10px 14px;
  background: var(--bg-subtle);
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-secondary);
}

:deep(.btn-only) {
  display: flex;
  justify-content: center;
}

.result {
  width: 100%;
  min-height: 20px;
  padding: 10px 14px;
  border-radius: 8px;
  background: var(--bg-subtle);
  font-size: 13px;
  text-align: left;
  line-height: 1.7;
  color: var(--text-secondary);
  white-space: pre-wrap;
  word-break: break-all;
}

.mp-search {
  display: flex;
  gap: 8px;
  width: 100%;
}

.mp-search .el-input {
  flex: 1;
}

.mp-table {
  width: 100%;
}

.mp-table :deep(.mp-clickable-row) {
  cursor: pointer;
  height: 60px;
}

.mp-table :deep(.mp-clickable-row:hover > .el-table__cell) {
  background-color: #f0f5ff !important;
}

.mp-pagination {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
  width: 100%;
}

.mp-stats {
  color: var(--text-muted);
  font-size: 13px;
  white-space: nowrap;
}
</style>
