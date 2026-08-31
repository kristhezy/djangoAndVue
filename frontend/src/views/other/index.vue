<template>
  <div class="other-page">
    <!-- 筛选区 -->
    <el-card class="filter-card" shadow="never">
      <template #header><span class="filter-title">操作变更记录</span></template>
      <el-form :inline="true" :model="query" @submit.prevent>
        <el-form-item label="环境">
          <el-select v-model="query.env" clearable placeholder="选择环境" style="width:120px">
            <el-option label="生产" value="prod" />
            <el-option label="测试" value="test" />
          </el-select>
        </el-form-item>
        <el-form-item label="版本">
          <el-select v-model="query.vers" clearable placeholder="选择版本" style="width:120px">
            <el-option label="Soon" value="4" />
            <el-option label="基线版" value="3" />
            <el-option label="通威版" value="6" />
            <el-option label="SAAS" value="1" />
          </el-select>
        </el-form-item>
        <el-form-item label="企业ID">
          <el-input v-model="query.compid" placeholder="输入企业ID" style="width:140px" />
        </el-form-item>
        <el-form-item label="企业名称">
          <el-input v-model="query.compname" placeholder="输入企业名称" style="width:140px" />
        </el-form-item>
        <el-form-item label="操作信息">
          <el-input v-model="query.minfo" placeholder="输入操作信息" style="width:140px" />
        </el-form-item>
        <el-form-item label="操作人">
          <el-select v-model="query.uname" clearable filterable placeholder="选择操作人" style="width:140px">
            <el-option v-for="n in operators" :key="n" :label="n" :value="n" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="search">查询</el-button>
          <el-button @click="reset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 表格区 -->
    <el-card class="table-card" shadow="never">
      <el-table :data="list" v-loading="loading" stripe height="100%">
        <el-table-column prop="id" label="序号" width="70" />
        <el-table-column label="环境" width="150">
          <template #default="{ row }">{{ envLabel(row) }}</template>
        </el-table-column>
        <el-table-column prop="companyId" label="企业ID" width="120" show-overflow-tooltip />
        <el-table-column prop="companyName" label="企业名称" show-overflow-tooltip />
        <el-table-column prop="message" label="操作信息" show-overflow-tooltip />
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

      <!-- 分页 -->
      <div class="pager">
        <el-pagination
          v-model:current-page="page"
          :page-size="num"
          :total="total"
          layout="total, prev, pager, next, jumper"
          @current-change="load"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../api/http'

const num = 10
const loading = ref(false)
const list = ref([])
const operators = ref([])
const total = ref(0)
const page = ref(1)

const query = reactive({ env: '', vers: '', compid: '', compname: '', minfo: '', uname: '' })

function envLabel(row) {
  const env = row.env || ''
  const ver = String(row.version ?? '')
  const ss = String(row.serverSide ?? '')
  if (env === '生产' || env === '测试') {
    if (ver === '1') return env + '/SAAS'
    if (ver === '3') {
      if (env === '生产' && ss === '3') return '私有化/基线版'
      return env + '/基线版'
    }
    if (ver === '4') return env + '/Soon'
    if (ver === '5') return env + '/Meet'
    if (ver === '6') return env + '/通威版'
    return env
  }
  return env
}

function payload() {
  return {
    page: page.value,
    env: query.env,
    vers: query.vers,
    num,
    compid: query.compid,
    compname: query.compname,
    uname: query.uname,
    minfo: query.minfo,
  }
}

async function load() {
  loading.value = true
  try {
    const resp = await http.post('/pv/other', payload())
    const a = resp.data?.data?.oprationalInfo
    if (typeof a === 'string') {
      list.value = []
      ElMessage.error(a)
    } else if (!Array.isArray(a) || a.length === 0) {
      list.value = []
    } else {
      list.value = a
    }
  } catch (e) {
    list.value = []
    ElMessage.error('查询失败：' + (e?.response?.data?.msg || e.message))
  } finally {
    loading.value = false
  }
}

async function loadTotal() {
  try {
    const resp = await http.post('/pv/pagecount', payload())
    total.value = Number(resp.data?.data?.total ?? 0)
  } catch (e) {
    total.value = 0
  }
}

async function loadOperators() {
  try {
    const resp = await http.post('/pv/other/queryOpraterName', {})
    const s = resp.data?.data?.otherPartRlt || ''
    operators.value = s.split(',').filter(x => x.trim() !== '')
  } catch (e) {
    operators.value = []
  }
}

async function del(id) {
  try {
    const resp = await http.post('/pv/other/delmsg', { id })
    ElMessage.success(resp.data?.data?.otherPartRlt || '删除成功！')
    await load()
    await loadTotal()
  } catch (e) {
    ElMessage.error('删除失败：' + (e?.response?.data?.msg || e.message))
  }
}

function search() {
  page.value = 1
  load()
  loadTotal()
}

function reset() {
  query.env = ''
  query.vers = ''
  query.compid = ''
  query.compname = ''
  query.minfo = ''
  query.uname = ''
  page.value = 1
  load()
  loadTotal()
}

onMounted(() => {
  loadOperators()
  load()
  loadTotal()
})
</script>

<style scoped>
.other-page { height: 100%; display: flex; flex-direction: column; gap: 16px; padding: 16px; box-sizing: border-box; background: #f0f2f5; overflow: hidden; }
.filter-card { flex-shrink: 0; }
.filter-title { font-weight: 600; font-size: 16px; }
.table-card { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.table-card :deep(.el-card__body) { flex: 1; display: flex; flex-direction: column; overflow: hidden; padding: 0; }
.table-card :deep(.el-table) { flex: 1; }
.pager { display: flex; justify-content: flex-end; padding: 12px 16px; }
</style>
