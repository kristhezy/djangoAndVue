<template>
  <div class="mp-page">
    <!-- 左侧：小程序发版管理 -->
    <div class="mp-left">
      <el-card class="mp-card" shadow="never">
        <template #header>
          <div class="mp-card-header">
            <span class="mp-card-header__title">小程序发版管理</span>
            <el-button text @click="resetLeft">重置</el-button>
          </div>
        </template>
        <div class="mp-card-body">
          <!-- 查询企业信息 -->
          <div class="mp-query">
            <el-input v-model="loginName" placeholder="输入登录手机号或企业ID" :disabled="loading" />
            <el-button type="primary" :loading="loading" :disabled="loading" @click="queryCompany">查询</el-button>
          </div>
          <div class="mp-cinfo">
            <div v-if="cid">
              <div>企业名称: {{ cn }}</div>
              <div>企业ID: {{ cid }}</div>
              <div>appID: {{ appid }}</div>
            </div>
            <div v-else-if="queryError" style="color: #ff4d4f;">{{ queryError }}</div>
            <div v-else style="color: #999;">未查询</div>
          </div>

          <!-- 提交前配置 -->
          <div class="mp-section">
            <div class="mp-section__row">
              <el-checkbox-group v-model="tsq">
                <el-checkbox value="priv">隐私权限配置</el-checkbox>
                <el-checkbox value="ulcm">上传代码模板</el-checkbox>
                <el-checkbox value="addm">添加域名</el-checkbox>
              </el-checkbox-group>
            </div>
            <el-button type="primary" :loading="loading" :disabled="loading || !cid" @click="submitBaconfig">提交</el-button>
            <div v-if="tsqrlt" class="mp-result">{{ tsqrlt }}</div>
          </div>

          <!-- 审核/发布 -->
          <div class="mp-section">
            <div class="mp-section__row">
              <el-radio-group v-model="fts">
                <el-radio value="audit">提交审核</el-radio>
                <el-radio value="ads">查看审核结果</el-radio>
                <el-radio value="rls">发布小程序</el-radio>
                <el-radio value="ucaudit">撤回审核</el-radio>
              </el-radio-group>
            </div>
            <el-button type="primary" :loading="loading" :disabled="loading || !cid" @click="submitAuditRelease">提交</el-button>
            <div v-if="tsrlt" class="mp-result">{{ tsrlt }}</div>
          </div>

          <!-- 体验者管理 -->
          <div class="mp-section" style="border-bottom: none;">
            <div class="mp-section__row">
              <el-radio-group v-model="tyb">
                <el-radio value="bindtester">绑定体验者</el-radio>
                <el-radio value="unbindtester">解绑体验者</el-radio>
                <el-radio value="getqrcode">生成体验码</el-radio>
              </el-radio-group>
            </div>
            <el-input v-if="tyb !== 'getqrcode'" v-model="wcid" placeholder="输入微信号" />
            <el-button type="primary" :loading="loading" :disabled="loading || !cid" @click="submitTester">提交</el-button>
            <div v-if="tybrlt" class="mp-result">
              <img v-if="tyb === 'getqrcode' && tybrlt.startsWith('/static/img/')" :src="tybrlt" height="180" />
              <template v-else>{{ tybrlt }}</template>
            </div>
          </div>

          <!-- 提示对话框 -->
          <el-dialog v-model="showTips" title="提示" width="360px" :close-on-click-modal="false">
            <div class="mp-tips-content">
              <div>请先配置业务域名的
                <el-button type="primary" plain size="small" :loading="loading" @click="downloadWdcFile">校验文件</el-button>
                ，并点击按钮去上传。
              </div>
              <div class="mp-tips-actions">
                <el-button type="primary" @click="window.open('https://dsa-app.aijiatui.com/upload.html', '_blank')">去上传</el-button>
              </div>
            </div>
          </el-dialog>
        </div>
      </el-card>
    </div>

    <!-- 右侧：操作记录 -->
    <div class="mp-right">
      <el-card class="mp-card" shadow="never">
        <div class="mp-card-body">
          <!-- 搜索 -->
          <div class="mp-search">
            <el-input v-model="qkey" placeholder="输入企业账号/ID/名称/appID查询" clearable
              @keydown.enter="searchRecords" />
            <el-button type="primary" @click="searchRecords">查询</el-button>
          </div>

          <!-- 表格 -->
          <el-table :data="records" stripe style="width: 100%" v-loading="loadingRecords"
            @row-click="onRowClick" row-class-name="mp-clickable-row" empty-text="暂无数据">
            <el-table-column prop="phone" label="账号" width="10%" />
            <el-table-column prop="companyName" label="企业名称" width="22%" />
            <el-table-column prop="appId" label="appID" width="18%" />
            <el-table-column prop="oContent" label="操作信息" width="32%" />
            <el-table-column prop="uname" label="操作人" width="8%" />
            <el-table-column prop="createTime" label="操作时间" width="10%" />
          </el-table>

          <!-- 分页 -->
          <div class="mp-pagination">
            <span class="mp-stats">共 {{ totalRecords }} 条，第 {{ page }}/{{ totalPages }} 页</span>
            <el-pagination v-model:current-page="page" :page-size="pageSize" :total="totalRecords"
              layout="prev, pager, next, jumper" @current-change="loadRecords" />
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

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
  loginName.value = ''
  cid.value = ''
  cn.value = ''
  phone.value = ''
  appid.value = ''
  queryError.value = ''
  tsq.value = []
  tsqrlt.value = ''
  fts.value = 'audit'
  tsrlt.value = ''
  tyb.value = 'bindtester'
  wcid.value = ''
  tybrlt.value = ''
}

async function queryCompany() {
  if (!loginName.value.trim()) {
    ElMessage.warning('请输入查询参数')
    return
  }
  loading.value = true
  queryError.value = ''
  try {
    const resp = await http.post('/sv/querycompid/saas', {
      ln: loginName.value,
      env: 'prod',
      cid: '',
      cn: '',
    })
    if (resp.data?.code === 0) {
      const d = resp.data.data
      cid.value = d.cid || ''
      cn.value = d.cn || ''
      phone.value = d.phone || ''
      const appResp = await http.post('/sv/getappid', { cid: cid.value, env: 'prod' })
      appid.value = appResp.data?.data?.appid || ''
    } else {
      queryError.value = resp.data?.data || '查询失败'
    }
  } catch (e) {
    queryError.value = '查询失败'
  } finally {
    loading.value = false
  }
}

async function submitBaconfig() {
  if (!tsq.value.length) {
    ElMessage.warning('请勾选需要提交的内容！')
    return
  }
  loading.value = true
  try {
    const resp = await http.post('/sv/miniprogramRelease/baconfig', {
      tsq: tsq.value.join(','),
      phone: phone.value,
      cid: cid.value,
      cn: cn.value,
      appid: appid.value,
      env: 'prod',
      type: 'baconfig',
    })
    tsqrlt.value = resp.data?.data?.rlt || ''
    if (resp.data?.data?.errtips) showTips.value = true
    loadRecords()
  } catch (e) {
    tsqrlt.value = '操作失败'
  } finally {
    loading.value = false
  }
}

async function submitAuditRelease() {
  if (!cid.value) {
    ElMessage.warning('企业信息不能为空！')
    return
  }
  loading.value = true
  try {
    const resp = await http.post('/sv/miniprogramRelease/auditAndRelease', {
      ts: fts.value,
      phone: phone.value,
      cid: cid.value,
      cn: cn.value,
      appid: appid.value,
      env: 'prod',
      type: 'auditAndRelease',
    })
    tsrlt.value = resp.data?.data?.rlt || ''
    if (resp.data?.data?.errtips) showTips.value = true
    loadRecords()
  } catch (e) {
    tsrlt.value = '操作失败'
  } finally {
    loading.value = false
  }
}

async function submitTester() {
  if (!cid.value) {
    ElMessage.warning('企业信息不能为空！')
    return
  }
  loading.value = true
  try {
    const resp = await http.post('/sv/miniprogramRelease/testerAndQrcode', {
      tyb: tyb.value,
      phone: phone.value,
      cid: cid.value,
      cn: cn.value,
      appid: appid.value,
      env: 'prod',
      type: 'testerAndQrcode',
      wcid: wcid.value,
    })
    if (tyb.value === 'getqrcode') {
      tybrlt.value = '/static/img/latest_img.jpg?t=' + Date.now()
    } else {
      tybrlt.value = resp.data?.data?.rlt || ''
    }
  } catch (e) {
    tybrlt.value = '操作失败'
  } finally {
    loading.value = false
  }
}

async function downloadWdcFile() {
  loading.value = true
  try {
    const resp = await http.post('/sv/miniprogramRelease/getwdcfile', {
      phone: phone.value,
      cid: cid.value,
      cn: cn.value,
      appid: appid.value,
      env: 'prod',
      type: 'getwdcfile',
    })
    if (resp.data?.code === 0) {
      const f = resp.data.data.rlt
      window.open(`/download_dynamic?type=txt&name=${f.file_name}&content=${f.file_content}`, '_blank')
    } else {
      ElMessage.error(resp.data?.data || '下载失败')
    }
  } catch (e) {
    ElMessage.error('下载失败')
  } finally {
    loading.value = false
  }
}

function searchRecords() {
  page.value = 1
  loadRecords()
}

async function loadRecords() {
  loadingRecords.value = true
  try {
    const resp = await http.post('/sv/queryMiniprogramRecord/querympoc', {
      page: page.value,
      num: pageSize.value,
      qkey: qkey.value,
      type: 'querympoc',
    })
    const data = resp.data?.data?.oprationalInfo || []
    records.value = Array.isArray(data) ? data : []
    loadPagination()
  } catch (e) {
    records.value = []
  } finally {
    loadingRecords.value = false
  }
}

async function loadPagination() {
  try {
    const resp = await http.post('/sv/queryMiniprogramRecord/querytp', {
      qkey: qkey.value,
      type: 'querytp',
    })
    totalRecords.value = parseInt(resp.data?.data?.total) || 0
    totalPages.value = Math.ceil(totalRecords.value / pageSize.value) || 1
  } catch (e) {
    totalRecords.value = 0
    totalPages.value = 1
  }
}

function onRowClick(row) {
  phone.value = row.phone || ''
  cid.value = row.companyId || ''
  cn.value = row.companyName || ''
  appid.value = row.appId || ''
  loginName.value = phone.value
  queryError.value = ''
}

onMounted(() => {
  loadRecords()
})
</script>

<style scoped>
.mp-page {
  height: 100%;
  overflow: hidden;
  background: #f0f2f5;
  padding: 16px;
  box-sizing: border-box;
  display: flex;
  gap: 12px;
}
.mp-left {
  width: 507px;
  min-width: 400px;
  padding: 15px 0;
  overflow-y: auto;
}
.mp-right {
  flex: 1;
  min-width: 0;
  padding: 15px 0;
  overflow-y: auto;
}
.mp-card {
  height: 100%;
  border-radius: 16px;
  overflow: hidden;
}
.mp-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.mp-card-header__title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}
.mp-card-body {
  padding: 12px 16px;
}
.mp-query {
  display: flex;
  gap: 10px;
  align-items: center;
  justify-content: center;
}
.mp-query .el-input {
  flex: 1;
}
.mp-cinfo {
  margin: 15px 0;
  min-height: 92px;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 4px;
  line-height: 1.6;
}
.mp-section {
  margin: 12px 0;
  padding-bottom: 12px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.mp-section__row {
  display: flex;
  gap: 12px;
  align-items: center;
}
.mp-result {
  min-height: 20px;
  font-size: 14px;
  margin-top: 8px;
  color: #606266;
}
.mp-tips-content {
  text-align: center;
}
.mp-tips-actions {
  margin-top: 16px;
}
.mp-search {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}
.mp-search .el-input {
  flex: 1;
}
.mp-clickable-row {
  cursor: pointer;
}
.mp-clickable-row:hover {
  background-color: #f5f5f5 !important;
}
.mp-pagination {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 16px;
  margin-top: 12px;
}
.mp-stats {
  color: #666;
  font-size: 14px;
}
</style>
