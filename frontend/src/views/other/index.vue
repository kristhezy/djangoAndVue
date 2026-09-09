<template>
  <div class="mo-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title"><i class="fa-solid fa-clock-rotate-left"></i> 操作变更记录</h2>
      </div>
    </div>

    <!-- 筛选区 -->
    <div class="search-bar">
      <div class="search-bar__inner">
        <el-form :inline="true" :model="query" @submit.prevent class="filter-form">
          <el-form-item label="环境">
            <el-select v-model="query.env" clearable placeholder="选择环境">
              <el-option label="生产" value="prod" />
              <el-option label="测试" value="test" />
            </el-select>
          </el-form-item>
          <el-form-item label="版本">
            <el-select v-model="query.vers" clearable placeholder="选择版本">
              <el-option label="Soon" value="4" />
              <el-option label="基线版" value="3" />
              <el-option label="通威版" value="6" />
              <el-option label="SAAS" value="1" />
            </el-select>
          </el-form-item>
          <el-form-item class="cid-input" label="企业ID">
            <el-input v-model="query.compid" placeholder="输入企业ID" />
          </el-form-item>
          <el-form-item label="企业名称">
            <el-input v-model="query.compname" placeholder="输入企业名称" />
          </el-form-item>
          <el-form-item label="操作信息">
            <el-input v-model="query.minfo" placeholder="输入操作信息" />
          </el-form-item>
          <el-form-item class="opr-select" label="操作人">
            <el-select v-model="query.uname" clearable filterable placeholder="选择操作人">
              <el-option v-for="n in operators" :key="n" :label="n" :value="n" />
            </el-select>
          </el-form-item>
          <el-form-item class="filter-actions">
            <el-button type="primary" :loading="loading" @click="search">查询</el-button>
            <el-button @click="reset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <!-- 表格区 -->
    <div class="mo-body">
      <div class="m-card" style="height:100%;">
        <div class="table-wrap">
          <el-table :data="list" v-loading="loading" stripe height="100%" :style="{ '--row-height': rowHeight + 'px' }">
            <el-table-column prop="id" label="序号" width="70" />
            <el-table-column label="环境" width="120">
              <template #default="{ row }">{{ envLabel(row) }}</template>
            </el-table-column>
            <el-table-column prop="companyId" label="企业ID" width="200" show-overflow-tooltip />
            <el-table-column prop="companyName" label="企业名称" width="230" show-overflow-tooltip />
            <el-table-column prop="message" label="操作信息" class-name="wrap-cell">
              <template #default="{ row }">
                <el-tooltip :content="row.message" placement="top-start" :show-after="200">
                  <div class="msg-wrap">{{ row.message }}</div>
                </el-tooltip>
              </template>
            </el-table-column>
            <el-table-column prop="uname" label="操作人" width="100" show-overflow-tooltip />
            <el-table-column prop="createTime" label="操作时间" width="170" show-overflow-tooltip />
            <el-table-column label="操作" width="90" fixed="right">
              <template #default="{ row }">
                <el-popconfirm title="确定删除这条记录吗？" @confirm="del(row.id)">
                  <template #reference>
                    <el-button type="danger" link>删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div class="pager">
          <el-pagination v-model:current-page="page" :page-size="num" :total="total"
            layout="total, prev, pager, next, jumper" @current-change="load" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const num = 10
const loading = ref(false)
const list = ref([])
const operators = ref([])
const total = ref(0)
const page = ref(1)
const rowHeight = ref(48)

const query = reactive({ env: '', vers: '', compid: '', compname: '', minfo: '', uname: '' })

let resizeObserver = null

function setRowHeight() {
  const wrapper = document.querySelector('.table-wrap .el-table__body-wrapper')
  if (!wrapper) return
  const rows = wrapper.querySelectorAll('tbody tr')
  const count = rows.length
  if (!count) return
  const available = wrapper.clientHeight
  if (available <= 0) return
  const h = Math.floor(available / count)
  rowHeight.value = count >= num ? h : Math.min(72, h)
}

function envLabel(row) {
  const env = row.env || '', ver = String(row.version ?? ''), ss = String(row.serverSide ?? '')
  if (env === '生产' || env === '测试') {
    if (ver === '1') return env + '/SAAS'
    if (ver === '3') { if (env === '生产' && ss === '3') return '私有化/基线版'; return env + '/基线版' }
    if (ver === '4') return env + '/Soon'
    if (ver === '5') return env + '/Meet'
    if (ver === '6') return env + '/通威版'
    return env
  }
  return env
}

function payload() {
  return { page: page.value, env: query.env, vers: query.vers, num, compid: query.compid, compname: query.compname, uname: query.uname, minfo: query.minfo }
}

async function load() {
  loading.value = true
  try {
    const resp = await http.post('/pv/other', payload())
    const a = resp.data?.data?.oprationalInfo
    if (typeof a === 'string') { list.value = []; ElMessage.error(a) }
    else if (!Array.isArray(a) || a.length === 0) { list.value = [] }
    else { list.value = a }
  } catch (e) { list.value = []; ElMessage.error('查询失败：' + (e?.response?.data?.msg || e.message)) }
  finally { loading.value = false; nextTick(() => setRowHeight()) }
}

async function loadTotal() {
  try { const resp = await http.post('/pv/pagecount', payload()); total.value = Number(resp.data?.data?.total ?? 0) }
  catch (e) { total.value = 0 }
}

async function loadOperators() {
  try {
    const resp = await http.post('/pv/other/queryOpraterName', {})
    const s = resp.data?.data?.otherPartRlt || ''
    operators.value = s.split(',').filter(x => x.trim() !== '')
  } catch (e) { operators.value = [] }
}

async function del(id) {
  try {
    const resp = await http.post('/pv/other/delmsg', { id })
    ElMessage.success(resp.data?.data?.otherPartRlt || '删除成功！')
    await load(); await loadTotal()
  } catch (e) { ElMessage.error('删除失败：' + (e?.response?.data?.msg || e.message)) }
}

function search() { page.value = 1; load(); loadTotal() }
function reset() { query.env = ''; query.vers = ''; query.compid = ''; query.compname = ''; query.minfo = ''; query.uname = ''; page.value = 1; load(); loadTotal() }

onMounted(() => {
  loadOperators(); load(); loadTotal()
  nextTick(() => {
    const wrapper = document.querySelector('.table-wrap .el-table__body-wrapper')
    if (wrapper) { resizeObserver = new ResizeObserver(() => setRowHeight()); resizeObserver.observe(wrapper); setRowHeight() }
  })
})

onBeforeUnmount(() => { if (resizeObserver) resizeObserver.disconnect() })
</script>

<style scoped>
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

.search-bar {
  flex-shrink: 0;
  padding: 0 14px;
}

.search-bar__inner {
  background: #fff;
  border-radius: 12px;
  padding: 14px 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, .06), 0 1px 2px rgba(0, 0, 0, .04);
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px 16px;
}

.filter-form :deep(.el-form-item) {
  margin: 0;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.filter-form :deep(.el-form-item__label) {
  font-size: 13px;
  font-weight: 500;
  color: #475569;
  padding: 0;
  white-space: nowrap;
  flex-shrink: 0;
}

.filter-form :deep(.el-input) {
  width: 200px;
}

.filter-form :deep(.cid-input .el-input) {
  width: 172px;
}

.filter-form :deep(.el-select) {
  width: 100px;
}

.filter-form :deep(.opr-select .el-select) {
  width: 120px;
}

.filter-actions {
  margin-left: auto;
}

.mo-body {
  flex: 1;
  padding: 12px 14px 14px;
  overflow: hidden;
}

.m-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, .06), 0 1px 2px rgba(0, 0, 0, .04);
  overflow: hidden;
  transition: box-shadow .2s;
  display: flex;
  flex-direction: column;
}

.m-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, .08), 0 2px 4px rgba(0, 0, 0, .04);
}

.table-wrap {
  flex: 1;
  overflow: hidden;
}

.table-wrap :deep(.el-table) {
  height: 100%;
}

.table-wrap :deep(.el-table th.el-table__cell) {
  font-size: 14px;
  font-weight: 700;
  background-color: #f8fafc;
  color: #1e293b;
}

.table-wrap :deep(.el-table td.el-table__cell) {
  padding: 0;
  height: var(--row-height, 48px);
}

.table-wrap :deep(.el-table .cell) {
  line-height: 1.4;
}

.pager {
  display: flex;
  justify-content: flex-end;
  padding: 12px 16px;
  flex-shrink: 0;
  border-top: 1px solid #f1f5f9;
}

.msg-wrap {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-word;
  white-space: normal;
  line-height: 1.4;
}
</style>
