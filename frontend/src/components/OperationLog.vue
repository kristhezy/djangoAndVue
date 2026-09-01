<template>
  <el-card class="oplog-panel" shadow="never">
    <template #header>
      <div class="oplog-title">执行结果</div>
    </template>
    <div v-loading="loading" class="oplog-log">
      <div v-if="!records.length" class="oplog-empty">暂无数据</div>
      <div v-for="(r, i) in records" :key="i" class="oplog-item">
        <div class="oplog-item__head">
          <span class="oplog-item__title">{{ r.env }} ┆ {{ r.companyName }}（{{ r.companyId }}）</span>
          <span class="oplog-item__time">{{ r.t }}</span>
        </div>
        <div class="oplog-item__msg" v-html="sanitize(r.message)"></div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '../api/http'

// ds: 操作记录来源 ds 数组（如 [1]/[2]/[3]/[15]）；initNum: 进入页面时查询条数
const props = defineProps({
  ds: { type: Array, required: true },
  initNum: { type: Number, default: 10 },
})

const loading = ref(false)
const records = ref([])

// 先转义全部 HTML，再只还原 <b> 与 <br/>，既保留加粗/换行又防 XSS
function sanitize(str) {
  return (str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/&lt;b&gt;/gi, '<b>')
    .replace(/&lt;\/b&gt;/gi, '</b>')
    .replace(/&lt;br\s*\/?&gt;/gi, '<br/>')
}

async function qbdan(num) {
  const resp = await http.post('/sv/qmbydsan', { dss: props.ds, num })
  const res = resp.data?.data?.qmbydsan
  if (!Array.isArray(res)) {
    records.value = []
    return
  }
  records.value = res
}

async function querymsgbyds(num) {
  loading.value = true
  try {
    await qbdan(num)
    const resp = await http.post('/sv/aftergetqmbydsan', { dss: props.ds, num })
    if (resp.data?.data === '更新数据成功！') {
      await qbdan(num)
    }
  } catch (e) {
    console.log('查询操作信息err:', e.message)
  } finally {
    loading.value = false
  }
}

function refresh(num) {
  return querymsgbyds(num)
}

onMounted(() => querymsgbyds(props.initNum))

defineExpose({ refresh })
</script>

<style scoped>
.oplog-panel {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.oplog-panel :deep(.el-card__body) { overflow-y: auto; }
.oplog-title { text-align: center; font-weight: 600; font-size: 16px; }
.oplog-log { min-height: 200px; }
.oplog-empty {
  color: #c0c4cc;
  text-align: center;
  padding: 48px 20px;
}
.oplog-item {
  padding: 10px 12px;
  border-bottom: 1px solid #ebeef5;
}
.oplog-item__head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}
.oplog-item__title { font-weight: 600; font-size: 14px; color: #303133; }
.oplog-item__time { font-size: 12px; color: #909399; white-space: nowrap; }
.oplog-item__msg {
  margin-top: 4px;
  font-size: 13px;
  color: #606266;
  word-break: break-all;
}
.oplog-item__msg :deep(b) { font-weight: 700; color: #303133; }
</style>
