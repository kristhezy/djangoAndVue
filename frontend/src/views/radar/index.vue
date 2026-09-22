<template>
  <div class="mo-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title"><i class="fa-solid fa-satellite-dish"></i> SAAS企业雷达数据</h2>
      </div>
    </div>

    <!-- 筛选区 -->
    <div class="search-bar">
      <div class="search-bar__inner">
        <el-form :inline="true" :model="query" @submit.prevent class="filter-form">
          <el-form-item label="企业名称">
            <el-input v-model="query.company_name" placeholder="输入企业名称" @keyup.enter="searchCompany" />
          </el-form-item>
          <el-form-item class="no-label">
            <el-button type="primary" :loading="companyLoading" @click="searchCompany">搜索</el-button>
            <el-button @click="showCompanyDetail">企业详情</el-button>
          </el-form-item>
          <el-form-item label="企业ID">
            <el-input v-model="query.company_id" placeholder="输入企业ID" />
          </el-form-item>
          <el-form-item label="起始时间">
            <el-date-picker v-model="query.start_time" type="date" placeholder="选择起始日期" value-format="YYYY-MM-DD"
              :clearable="false" />
          </el-form-item>
          <el-form-item label="结束时间">
            <el-date-picker v-model="query.end_time" type="date" placeholder="选择结束日期" value-format="YYYY-MM-DD"
              :clearable="false" />
          </el-form-item>
          <el-form-item class="filter-actions">
            <el-button type="primary" :loading="loading" @click="search">查询</el-button>
            <el-button @click="reset">重置</el-button>
            <el-button type="info" @click="exportCsv">导出</el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <!-- 表格区 -->
    <div class="mo-body">
      <div class="m-card">
        <div class="table-wrap">
          <el-table :data="pagedList" v-loading="loading" stripe height="100%">
            <el-table-column prop="card_name" label="员工姓名" min-width="150" />
            <el-table-column prop="card_position" label="职务" min-width="180" />
            <el-table-column prop="department" label="部门" min-width="120" />
            <el-table-column prop="radar_status" label="ai雷达" min-width="120" />
            <el-table-column prop="boss_status" label="boss雷达" min-width="120" />
            <el-table-column prop="action_type" label="内容类型" min-width="120" />
            <el-table-column prop="share_count" label="分享次数" min-width="90" align="center" />
            <el-table-column prop="uv_count" label="浏览人数" min-width="90" align="center" />
            <el-table-column prop="pv_count" label="浏览次数" min-width="90" align="center" />
            <el-table-column prop="customer_count" label="新增用户" min-width="90" align="center" />
          </el-table>
        </div>
        <div class="pager">
          <el-pagination v-model:current-page="page" :page-size="pageSize" :total="allData.length"
            :page-sizes="[100, 200, 300]" layout="total, sizes, prev, pager, next, jumper"
            @current-change="onPageChange" @size-change="onSizeChange" />
        </div>
      </div>
    </div>

    <!-- 企业详情弹窗 -->
    <el-dialog v-model="detailVisible" title="企业详情" width="70%" top="5vh">
      <pre class="detail-json">{{ companyDetailJson }}</pre>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../../api/http'

const loading = ref(false)
const companyLoading = ref(false)
const allData = ref([])
const companyInfo = ref([])
const detailVisible = ref(false)
const companyDetailJson = ref('')
const page = ref(1)
const pageSize = ref(100)

const today = new Date()
const y = today.getFullYear()
const m = String(today.getMonth() + 1).padStart(2, '0')
const defaultStart = `${y}-${m}-01`
const defaultEnd = `${y}-${m}-${String(today.getDate()).padStart(2, '0')}`

const query = reactive({
  company_name: '',
  company_id: '',
  start_time: defaultStart,
  end_time: defaultEnd,
})

const pagedList = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return allData.value.slice(start, start + pageSize.value)
})

async function loadData() {
  if (!query.company_id) {
    ElMessage.warning('请输入企业ID')
    return
  }
  loading.value = true
  try {
    const params = {
      company_id: query.company_id,
      start_time: query.start_time,
      end_time: query.end_time,
    }
    const resp = await http.get('/pv/radar/data', { params })
    const d = resp.data
    if (d?.code === 0 || d?.code === '0') {
      allData.value = Array.isArray(d.data) ? d.data : []
      if (!allData.value.length) ElMessage.info('无数据')
    } else {
      allData.value = []
      ElMessage.error(d?.msg || '查询失败')
    }
  } catch (e) {
    allData.value = []
    ElMessage.error('查询失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    loading.value = false
  }
}

async function searchCompany() {
  if (!query.company_name) {
    ElMessage.warning('请输入企业名称')
    return
  }
  companyLoading.value = true
  try {
    const resp = await http.get('/pv/radar/company', { params: { company_name: query.company_name } })
    const d = resp.data
    if (d?.code === 0 || d?.code === '0') {
      const arr = Array.isArray(d.data) ? d.data : []
      companyInfo.value = arr
      const match = arr.find(v => v.company_name === query.company_name)
      if (match) {
        query.company_id = match.company_id
        ElMessage.success(`找到企业ID: ${match.company_id}`)
      } else if (arr.length > 0) {
        query.company_id = arr[arr.length - 1]?.company_id || ''
        ElMessage.info(`未精确匹配，使用最近结果: ${arr[arr.length - 1]?.company_name}`)
      } else {
        ElMessage.warning('未找到该企业')
      }
    } else {
      ElMessage.error(d?.msg || '搜索失败')
    }
  } catch (e) {
    ElMessage.error('搜索失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    companyLoading.value = false
  }
}

function showCompanyDetail() {
  if (!companyInfo.value || !companyInfo.value.length) {
    ElMessage.warning('请先搜索企业')
    return
  }
  companyDetailJson.value = JSON.stringify(companyInfo.value, null, '\t')
  detailVisible.value = true
}

function search() {
  page.value = 1
  loadData()
}

function reset() {
  query.company_name = ''
  query.company_id = ''
  query.start_time = defaultStart
  query.end_time = defaultEnd
  allData.value = []
  page.value = 1
}

function onPageChange() { /* computed handles it */ }
function onSizeChange(size) { pageSize.value = size; page.value = 1 }

function exportCsv() {
  if (!allData.value.length) {
    ElMessage.warning('无数据可导出')
    return
  }
  const headers = ['员工姓名', '职务', '部门', 'ai雷达', 'boss雷达', '内容类型', '分享次数', '浏览人数', '浏览次数', '新增用户']
  const fields = ['card_name', 'card_position', 'department', 'radar_status', 'boss_status', 'action_type', 'share_count', 'uv_count', 'pv_count', 'customer_count']
  const rows = allData.value.map(row => fields.map(f => row[f] ?? '').join(','))
  const csv = '﻿' + headers.join(',') + '\n' + rows.join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `企业${query.company_id}雷达数据.csv`
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(() => { /* 不自动加载，需用户输入企业ID后查询 */ })
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

.search-bar {
  flex-shrink: 0;
  padding: 0 14px;
}

.search-bar__inner {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 14px 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, .06), 0 1px 2px rgba(0, 0, 0, .04);
  box-sizing: border-box;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px 12px;
}

.filter-form :deep(.el-form-item) {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 0 1 auto;
  min-width: 130px;
}

.filter-form :deep(.el-form-item__label) {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  padding: 0;
  white-space: nowrap;
  flex-shrink: 0;
}

.filter-form :deep(.el-input),
.filter-form :deep(.el-select),
.filter-form :deep(.el-date-editor) {
  flex: 1;
  min-width: 0;
  width: 100%;
}

.filter-form :deep(.no-label) {
  flex: none;
  gap: 4px;
}

.filter-actions {
  flex: none;
  margin-left: auto;
}

.mo-body {
  flex: 1;
  padding: 12px 14px 14px;
  overflow: hidden;
  min-height: 0;
}

.m-card {
  background: var(--bg-card);
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, .06), 0 1px 2px rgba(0, 0, 0, .04);
  overflow: hidden;
  transition: box-shadow .2s;
  display: flex;
  flex-direction: column;
  flex: 1;
  width: 100%;
}

.m-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, .08), 0 2px 4px rgba(0, 0, 0, .04);
}

.table-wrap {
  flex: 1;
  overflow: hidden;
  width: 100%;
  min-height: 0;
}

.table-wrap :deep(.el-table) {
  height: 100%;
}

.table-wrap :deep(.el-table th.el-table__cell) {
  font-size: 14px;
  font-weight: 700;
  background-color: var(--bg-subtle);
  color: var(--text-primary);
}

.pager {
  display: flex;
  justify-content: flex-end;
  padding: 12px 16px;
  flex-shrink: 0;
  border-top: 1px solid var(--border-card);
}

.detail-json {
  font-size: 14px;
  line-height: 1.6;
  max-height: 70vh;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-all;
  background: var(--bg-subtle);
  color: var(--text-primary);
  padding: 16px;
  border-radius: 8px;
  margin: 0;
}
</style>
